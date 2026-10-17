"""F-anchored agent: relative one-ply scan + budgeted worst-case 2-ply on contested decisions.

Design (replaces the random-rollout MCTS):

  1. ROOT PASS (always runs, F's whole computation). Every legal action is executed on a
     sampled world and scored with  rel = V(me) - OPP_WEIGHT * V(opponent)  using catanatron's
     base value function. Noisy averages never override this.
  2. TWO-PLY REFINEMENT (only when the one-ply scan cannot separate the top candidates by a
     VP-sized margin). For each of the top TOPK candidates:
        a. we keep playing our own turn greedily by `rel` (a few steps, ends at END_TURN),
           so every candidate is compared at the same horizon: "end of our turn";
        b. the opponent's forced actions (ROLL ...) are executed, then the opponent's reply
           is taken as the WORST CASE for us (min of rel over its legal actions).
     In the opening (initial build phase) the refinement gets a larger budget, because the
     first settlements matter most and the 300 ms base allowance exists for them.
     Dice use the same random stream for every candidate (common random numbers), so luck
     does not decide between candidates. The global random state is restored afterwards.
  3. SAFETY RAILS. Everything is driven by time.process_time(); each stage has a hard cap and
     a cap as a fraction of obs.cpu_left; a candidate whose refinement is cut off by the
     deadline is discarded (never compared half-evaluated); an escaped exception falls back to
     a random legal index.

Tune the constants below; nothing here has been benchmarked.
"""
import random
import time

from catanatron.models.player import Color, Player
from catanatron.players.value import DEFAULT_WEIGHTS, base_fn

VALUE_FN = base_fn(DEFAULT_WEIGHTS)

# --- evaluation -----------------------------------------------------------------------
OPP_WEIGHT = 1.0         # rel = V(me) - OPP_WEIGHT * V(opp); 0 recovers plain F
WIN_SCORE = 1e18         # terminal score; dominates any position value
VP_MARGIN = 1e14         # one public VP is 3e14 raw; skip 2-ply if top leads by more than this
TOPK = 3                 # candidates refined by the 2-ply stage

# --- budget (seconds of CPU) ----------------------------------------------------------
ROOT_NARROW_MAX_S = 0.012    # root-pass ceiling for small decisions
ROOT_WIDE_MAX_S = 0.060      # root-pass ceiling for wide decisions (>=16 actions)
ROOT_FRACTION = 0.30         # root pass never uses more than this share of obs.cpu_left
MIN_ROOT_S = 0.002           # below this, skip all search and use static priority

TWO_PLY_MAX_S = 0.040        # ceiling for the refinement in normal play
TWO_PLY_MAX_OPENING_S = 0.120  # ceiling for the refinement during initial placement
TWO_PLY_FRACTION = 0.20      # share of (cpu_left - RESERVE_S) the refinement may use
RESERVE_S = 0.060            # credit never touched by the refinement
MIN_TWO_PLY_S = 0.006        # below this, do not start the refinement

# --- 2-ply shape ----------------------------------------------------------------------
OWN_FOLLOW_STEPS = 3         # our greedy follow-up actions after the candidate (normal play)
OWN_FOLLOW_STEPS_OPENING = 2  # settlement -> road during initial placement
OWN_SCAN_MAX = 12            # at most this many of our actions scanned per follow-up step
FORCED_MAX = 3               # opponent forced actions (ROLL, ...) executed before its reply
REPLY_SCAN_MAX = 14          # opponent replies scanned in normal play
REPLY_SCAN_MAX_OPENING = 40  # opponent replies scanned during initial placement

_PRIORITY = {
    "PLAY_ROAD_BUILDING": 9, "BUILD_CITY": 8, "BUILD_SETTLEMENT": 7,
    "BUY_DEVELOPMENT_CARD": 6, "PLAY_KNIGHT_CARD": 5, "BUILD_ROAD": 5,
    "PLAY_YEAR_OF_PLENTY": 4, "PLAY_MONOPOLY": 4, "MOVE_ROBBER": 3,
    "DISCARD_RESOURCE": 2, "MARITIME_TRADE": 1, "ROLL": 1, "END_TURN": 0,
}


def _prio(action):
    return _PRIORITY.get(action.action_type.name, 1)


def _is_end_turn(action):
    return action.action_type.name == "END_TURN"


class Agent:
    """The harness imports `Agent` from this file by name."""

    def __init__(self):
        self.rng = random.Random(0)
        # Warm engine imports / feature caches so the first decision is not charged for them.
        try:
            from catanatron.game import Game

            g = Game(players=[Player(Color.RED), Player(Color.BLUE)], seed=1)
            g.execute(g.playable_actions[0], validate_action=False)
            VALUE_FN(g, Color.RED)
        except Exception:
            pass

    # ------------------------------------------------------------------ entry point

    def decide(self, obs, playable_actions):
        try:
            return self._decide(obs, playable_actions)
        except Exception:
            # An escaped exception is a recorded fault; a random legal index is always legal.
            return self.rng.randrange(len(playable_actions))

    def _decide(self, obs, playable_actions):
        n = len(playable_actions)
        if n <= 1:
            return 0

        t_start = time.process_time()
        left = obs.cpu_left if obs.cpu_left is not None else 0.010
        me = obs.me

        root_cap = ROOT_WIDE_MAX_S if n >= 16 else ROOT_NARROW_MAX_S
        root_budget = min(root_cap, ROOT_FRACTION * max(left, 0.0) - 0.0002)
        if root_budget < MIN_ROOT_S:
            return self._static_pick(playable_actions)

        world = obs.sample_world(self.rng)
        acts = world.playable_actions
        opps = [c for c in world.state.colors if c != me]

        # ---------------- 1. root pass: F's one-ply scan, relative score ----------------
        root_deadline = t_start + root_budget
        order = sorted(range(len(acts)), key=lambda i: -_prio(acts[i]))  # builds first
        scored = []  # (score, index, child_game)
        for i in order:
            try:
                g = world.copy()
                g.execute(acts[i], validate_action=False)
            except Exception:
                continue  # dead in this sampled world, as F drops it
            if g.winning_color() == me:
                return i  # immediate win
            scored.append((self._rel(g, me, opps), i, g))
            if time.process_time() >= root_deadline:
                break
        if not scored:
            return self._static_pick(playable_actions)
        scored.sort(key=lambda t: (-t[0], t[1]))
        best_score, best_i, _ = scored[0]

        # ---------------- 2. contested? decide whether to refine ----------------
        cands = [t for t in scored[:TOPK] if best_score - t[0] < VP_MARGIN]
        if len(cands) < 2:
            return best_i  # the one-ply scan separates them clearly

        opening = bool(getattr(world.state, "is_initial_build_phase", False))
        left_now = left - (time.process_time() - t_start)
        budget2 = min(TWO_PLY_MAX_OPENING_S if opening else TWO_PLY_MAX_S,
                      TWO_PLY_FRACTION * max(left_now - RESERVE_S, 0.0))
        if budget2 < MIN_TWO_PLY_S:
            return best_i
        deadline2 = time.process_time() + budget2

        # ---------------- 3. worst-case 2-ply over the contested candidates ----------------
        saved_state = random.getstate()
        try:
            results = {}
            for score1, i, g in cands:
                if time.process_time() >= deadline2:
                    break
                random.setstate(saved_state)  # common random numbers across candidates
                s2 = self._two_ply(g, me, opps, deadline2, opening)
                if s2 is None:
                    break  # out of time mid-candidate: do not compare a half-evaluated one
                results[i] = s2
        finally:
            random.setstate(saved_state)  # leave the harness's global RNG untouched

        # The top one-ply candidate must have been fully evaluated and at least one rival too;
        # otherwise the comparison is not like-for-like and F's choice stands.
        if best_i not in results or len(results) < 2:
            return best_i
        return max(results, key=lambda k: (results[k], -k))

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _static_pick(playable_actions):
        return max(range(len(playable_actions)), key=lambda i: _prio(playable_actions[i]))

    @staticmethod
    def _rel(g, me, opps):
        """Zero-sum-aware score: our value minus the strongest opponent's value."""
        v = VALUE_FN(g, me)
        if OPP_WEIGHT and opps:
            v -= OPP_WEIGHT * max(VALUE_FN(g, o) for o in opps)
        return v

    def _terminal(self, g, me):
        w = g.winning_color()
        if w is None:
            return None
        return WIN_SCORE if w == me else -WIN_SCORE

    def _two_ply(self, child, me, opps, deadline, opening):
        """Score one candidate: we finish our turn greedily, then the opponent replies with
        its worst-case move for us. Returns None if the deadline passes before it finishes."""
        g = child
        own_steps = OWN_FOLLOW_STEPS_OPENING if opening else OWN_FOLLOW_STEPS
        reply_max = REPLY_SCAN_MAX_OPENING if opening else REPLY_SCAN_MAX
        forced = 0
        own_done = 0

        while True:
            if time.process_time() >= deadline:
                return None
            t = self._terminal(g, me)
            if t is not None:
                return t
            acts = g.playable_actions
            if not acts:
                return self._rel(g, me, opps)
            cur = g.state.current_color()

            if cur == me:
                # (a) our own turn continues: play greedily by rel until we stop or run out
                if own_done >= own_steps:
                    return self._rel(g, me, opps)  # horizon cut: one-ply value
                if len(acts) == 1:
                    g = g.copy()
                    g.execute(acts[0], validate_action=False)
                    own_done += 1
                    continue
                best_g, best_s = None, None
                pool = sorted(acts, key=lambda a: -_prio(a))[:OWN_SCAN_MAX]
                if not any(_is_end_turn(a) for a in pool):
                    pool += [a for a in acts if _is_end_turn(a)]  # stopping must stay an option
                for a in pool:
                    if time.process_time() >= deadline:
                        return None
                    try:
                        g2 = g.copy()
                        g2.execute(a, validate_action=False)
                    except Exception:
                        continue
                    s = self._rel(g2, me, opps)
                    if best_s is None or s > best_s:
                        best_g, best_s = g2, s
                if best_g is None:
                    return self._rel(g, me, opps)
                g = best_g
                own_done += 1
                continue

            # (b) an opponent is to act
            if len(acts) == 1:
                if forced >= FORCED_MAX:
                    return self._rel(g, me, opps)
                g = g.copy()
                g.execute(acts[0], validate_action=False)  # ROLL etc.; shared dice stream
                forced += 1
                continue

            worst = None
            pool = sorted(acts, key=lambda a: -_prio(a))[:reply_max]
            for a in pool:
                if time.process_time() >= deadline:
                    return None
                try:
                    g2 = g.copy()
                    g2.execute(a, validate_action=False)
                except Exception:
                    continue
                t = self._terminal(g2, me)
                s = t if t is not None else self._rel(g2, me, opps)
                if worst is None or s < worst:
                    worst = s
            return worst if worst is not None else self._rel(g, me, opps)
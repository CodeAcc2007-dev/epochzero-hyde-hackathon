"""Same-turn alpha-beta at depth 2, strictly inside the CPU clock.

This is catanatron's `SameTurnAlphaBetaPlayer` (depth 2) rebuilt for this kit's interface and
clock. The library version runs a fixed depth-2 search with exact expectimax chance expansion
(`expand_spectrum`: ~11 game copies for every ROLL) and a 20-second wall deadline; measured
against F through this kit's harness it runs out its allowance in 415 of 1,000 games. The
search shape is kept, the cost model is not:

  * same-turn: the search never descends into the opponent's turn — a state where it is not
    our turn is a leaf. Depth counts OUR consecutive decisions; forced single-action states
    (the engine's ROLL, a mandated discard) are executed through and consume no depth.
  * depth 2 therefore means: for a root action, also try each of our follow-up moves and take
    the best leaf value — a two-decision lookahead that one-ply players like F never do.
  * chance events (dice, dev-card draws, stolen cards) are not expanded into exact
    distributions; the engine resolves them by sampling on the copied game. Exact spectra
    multiply cost by ~11x per roll, which is what makes the library player blow its allowance.
    The kit reseeds Python's `random` per game, so sampled search still replays exactly.

HOW THE BUDGET IS KEPT. Everything is driven by time.process_time() — the same CPU-time notion
the harness reads from outside — never by a fixed node count:

  * the depth-1 pass (evaluating every root action once: F's exact computation) is sized from
    a live EMA of one leaf expansion, so F-quality play is always affordable;
  * depth 2 only starts if its measured cost estimate fits the remaining budget, and it
    refines only the top DEPTH2_TOP_M root actions by their depth-1 value;
  * the clock is checked before every expansion; if the depth-2 pass aborts, its values are
    DISCARDED wholesale and the complete depth-1 ranking is used — never a mix of depths;
  * the whole budget is additionally capped at 30% of obs.cpu_left, so the allowance decays
    slowly instead of being spent in a few decisions;
  * below the cost of the root pass itself, the search is skipped for a zero-cost
    static-priority pick.

The agent never raises: an unexpected exception falls back to a random legal index, because
errors above 2% of decisions disqualify a submission (PROBLEM_STATEMENT.md, section 4.2).
"""
import random
import time

from catanatron.models.player import Color, Player
from catanatron.players.value import DEFAULT_WEIGHTS, base_fn

VALUE_FN = base_fn(DEFAULT_WEIGHTS)  # the same 13 features and weights F scores with

# --- budget (seconds of CPU) --------------------------------------------------
DEPTH2_TOP_M = 4       # how many root actions (best depth-1 first) get the depth-2 pass
NARROW_MAX_S = 0.011   # hard ceiling for small decisions (under the 12.5 ms increment)
WIDE_MAX_S = 0.030     # ceiling for wide decisions; the 300 ms base exists for these
MAX_FRACTION = 0.30    # never spend more than this share of the remaining allowance
MIN_SEARCH_S = 0.002   # belt-and-braces floor; the root_cost check below usually binds first
# --- cost model (seconds), refined live by EMAs -------------------------------
EST_LEAF_S = 0.0008    # one leaf expansion: game.copy() + execute + static eval (~0.65 ms)
EST_BRANCH = 3.0       # mean legal actions at a second-level decision
SAFETY = 1.25          # padding on cost estimates before committing to depth 2

REWARD_SCALE = 1e8     # eval / REWARD_SCALE: F's production weight is the unit
WIN_REWARD = 1e9       # terminal reward, normalised units; dominates any position eval

_PRIORITY = {
    "PLAY_ROAD_BUILDING": 9,
    "BUILD_CITY": 8,
    "BUILD_SETTLEMENT": 7,
    "BUY_DEVELOPMENT_CARD": 6,
    "PLAY_KNIGHT_CARD": 5,
    "BUILD_ROAD": 5,
    "PLAY_YEAR_OF_PLENTY": 4,
    "PLAY_MONOPOLY": 4,
    "MOVE_ROBBER": 3,
    "DISCARD_RESOURCE": 2,
    "MARITIME_TRADE": 1,
    "ROLL": 1,
    "END_TURN": 0,
}


class Agent:
    """Same-turn alpha-beta: depth 2 when the clock allows, depth 1 otherwise."""

    def __init__(self):
        self.rng = random.Random(0)
        # Live cost estimates, EMA-updated as the search runs. Budgets are built from them, so
        # the same search spends the same CPU on a machine half as fast — it just searches
        # less, and never misses the depth-1 baseline, which is sized from the same numbers.
        self._est_leaf_s = EST_LEAF_S
        self._est_branch = EST_BRANCH
        # Warm the code paths the first decision would otherwise pay for: engine imports,
        # feature caches, the value closure. The harness gives __init__ 60 uncharged seconds.
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
            # An escaped exception is a recorded fault, and 2% of them disqualify the
            # submission. Never let one escape: a random legal move is always legal play.
            return self.rng.randrange(len(playable_actions))

    def _decide(self, obs, playable_actions):
        self._me = obs.me
        n = len(playable_actions)
        if n <= 1:
            return 0

        left = obs.cpu_left if obs.cpu_left is not None else 0.010
        root_cost = n * self._est_leaf_s                       # the depth-1 pass
        depth2_cost = min(n, DEPTH2_TOP_M) * self._est_branch * self._est_leaf_s
        budget = min(root_cost * SAFETY + depth2_cost,
                     WIDE_MAX_S if n >= 16 else NARROW_MAX_S,
                     MAX_FRACTION * max(left, 0.0) - 0.0002)
        if budget < root_cost * SAFETY or budget < MIN_SEARCH_S:
            # Not enough credit even for the full root pass: pick by static priority,
            # costs nothing.
            return max(range(n),
                       key=lambda i: _PRIORITY.get(playable_actions[i].action_type.name, 1))

        deadline = time.process_time() + budget
        world = obs.sample_world(self.rng)   # one determinized world, like F

        # Depth 1: every root action expanded and statically evaluated. Priority order puts
        # building moves first, so a cut-off pass has at least valued the important actions.
        # Actions illegal in the sampled world are dropped, as F drops them.
        values = {}
        aborted = False
        for i in sorted(range(n),
                        key=lambda i: -_PRIORITY.get(playable_actions[i].action_type.name, 1)):
            t0 = time.process_time()
            game = world.copy()
            try:
                game.execute(playable_actions[i], validate_action=False)
            except Exception:
                continue  # illegal in this world, as F treats it
            values[i] = self._eval(game)
            self._ema_leaf(time.process_time() - t0)
            if time.process_time() >= deadline:
                aborted = True
                break

        if not aborted and values:
            self._depth2(world, values, deadline)

        if not values:
            # Nothing was evaluated at all (should not happen): a static pick costs nothing.
            return max(range(n),
                       key=lambda i: _PRIORITY.get(playable_actions[i].action_type.name, 1))
        return max(values, key=lambda i: (values[i], -i))

    # ------------------------------------------------------------------ search pieces

    def _depth2(self, world, values, deadline):
        """Deepen the best DEPTH2_TOP_M root actions to depth 2: one more of our decisions.

        Runs best-first, so the actions that matter are refined first, and it is
        all-or-nothing: if the deadline hits before the pass completes, the partial depth-2
        values are thrown away — comparing a two-ply value with a one-ply value would bias
        toward whatever happened to get refined.
        """
        me = self._me
        order = sorted(values, key=lambda i: -values[i])[:DEPTH2_TOP_M]
        refined = {}
        for i in order:
            if time.process_time() + self._est_branch * self._est_leaf_s * SAFETY > deadline:
                return  # cannot finish this action, let alone the rest: keep depth-1 values
            game = world.copy()
            try:
                game.execute(world.playable_actions[i], validate_action=False)
            except Exception:
                continue  # died since the depth-1 pass; keep its depth-1 value
            game = self._advance_forced(game, deadline)
            if game.winning_color() is not None:
                refined[i] = self._eval(game)   # terminal: the win/loss reward
                continue
            if game.state.current_color() != me:
                continue  # our move ended our turn: the depth-1 value already covers it
            best2 = None
            for a2 in game.playable_actions:
                if time.process_time() >= deadline:
                    return  # discard everything; the depth-1 ranking stands
                g3 = game.copy()
                try:
                    g3.execute(a2, validate_action=False)
                except Exception:
                    continue
                v = self._eval(g3)
                if best2 is None or v > best2:
                    best2 = v
            self._est_branch += 0.1 * (len(game.playable_actions) - self._est_branch)
            if best2 is not None:
                refined[i] = max(best2, values[i])
        values.update(refined)

    def _advance_forced(self, game, deadline):
        """Execute single-action steps the engine forces on us anyway; they cost no depth."""
        steps = 0
        while (game.winning_color() is None
               and game.state.current_color() == self._me
               and len(game.playable_actions) == 1 and steps < 30):
            try:
                game.execute(game.playable_actions[0], validate_action=False)
            except Exception:
                break
            steps += 1
            if time.process_time() >= deadline:
                break
        return game

    def _eval(self, game):
        """Leaf value from our seat, normalised (F's production weight is the unit)."""
        winner = game.winning_color()
        if winner is not None:
            return WIN_REWARD if winner == self._me else -WIN_REWARD
        return VALUE_FN(game, self._me) / REWARD_SCALE

    def _ema_leaf(self, measured):
        self._est_leaf_s += 0.1 * (max(measured, 1e-6) - self._est_leaf_s)

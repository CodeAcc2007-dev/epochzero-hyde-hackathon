"""MCTS agent that stays strictly inside the CPU clock.

The clock (catan_kit/match.py): min(300 ms + 12.5 ms per decision, 1.5 s) per game, about
1 s for a typical game. Measured engine costs on one core of this kit:

    game.copy()                    ~0.10 ms
    copy + execute one action      ~0.25 ms
    base_fn eval                   ~0.20 ms
    full random playout to end     ~50 ms   <- one of these busts the increment

A full playout is unaffordable — catanatron's own MCTSPlayer (full playouts per decision) runs
out its allowance in every game. This agent runs UCT with SHORT truncated rollouts instead:
descend by UCB, expand one child per simulation, play at most ROLLOUT_DEPTH random moves, then
score the position with catanatron's base value function (F's own weights). Every simulation
carries opponent replies inside it, which one-ply players like F never see.

HOW THE BUDGET IS KEPT. Everything is driven by time.process_time() — the same CPU-time notion
the harness reads from outside — never by a fixed simulation count:

  * per-decision budget: 30 ms for wide decisions (opening placement, robber: ~16+ actions;
    the 300 ms base exists for exactly these), 8.5 ms otherwise, so in steady state the agent
    spends less than the 12.5 ms it earns back per decision;
  * the budget is additionally capped at MAX_FRACTION of obs.cpu_left, so the allowance decays
    slowly instead of being spent in a few decisions;
  * the clock is checked before every simulation, and a rollout aborts the moment the deadline
    passes, so nothing can overspend by much more than one execute (~0.25 ms);
  * below MIN_SEARCH_S of credit the search is skipped for a zero-cost static-priority pick.

The agent never raises: an unexpected exception falls back to a random legal index, because
errors above 2% of decisions disqualify a submission (PROBLEM_STATEMENT.md, section 4.2).
"""
import math
import random
import time

from catanatron.models.player import Color, Player
from catanatron.players.value import DEFAULT_WEIGHTS, base_fn

VALUE_FN = base_fn(DEFAULT_WEIGHTS)  # the same 13 features and weights F scores with

# --- budget (seconds of CPU) --------------------------------------------------
# Per-decision budget = number of root actions x EST_EXPAND_S (measured live, see
# _prior_pass) + EXTRA_SIM_S, clamped to a hard ceiling. Measured expand+eval costs
# ~0.65 ms, so a 6-action decision spends ~7 ms and a 45-action placement ~30 ms.
EXTRA_SIM_S = 0.004     # reserved for UCT simulations beyond the root pass
NARROW_MAX_S = 0.010    # hard ceiling for small decisions (under the 12.5 ms increment)
WIDE_MAX_S = 0.030      # ceiling for wide decisions; the 300 ms base exists for these
MAX_FRACTION = 0.30     # never spend more than this share of the remaining allowance
MIN_SEARCH_S = 0.002    # below this, skip the search entirely
# --- search -------------------------------------------------------------------
ROLLOUT_DEPTH = 1       # executed actions (ours and forced ones) after the expanded node
UCB_C = 1.2            # exploration constant, in eval/1e8 units
WIN_REWARD = 1e9       # terminal reward, normalised units; must dominate any position eval
REWARD_SCALE = 1e8     # eval / REWARD_SCALE: F's production weight is the unit

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


def _action_priority(action):
    """Cheap static ordering for expansion, no engine calls. Builds before trades before
    stopping. It only shapes which actions are simulated first; every action stays reachable."""
    return _PRIORITY.get(action.action_type.name, 1)


class _Node:
    """One game state in the search tree. Owns its game copy; children are keyed by the
    action's index in that state's playable_actions list."""

    __slots__ = ("game", "me", "color", "children", "untried", "visits", "total", "winner")

    def __init__(self, game, me):
        self.game = game
        self.me = me
        self.color = game.state.current_color()  # who decides at this node
        self.children = {}  # action index -> _Node
        # Untried actions, most promising first: static type priority points the first
        # simulations at building moves. A terminal state has none.
        acts = game.playable_actions
        self.untried = sorted(range(len(acts)),
                              key=lambda i: -_PRIORITY.get(acts[i].action_type.name, 1))
        self.visits = 0
        self.total = 0.0
        self.winner = game.winning_color()  # not None once the game is over


class Agent:
    """MCTS agent. The harness imports `Agent` from this file by name."""

    def __init__(self):
        self.rng = random.Random(0)
        # Live estimate of one root expansion (copy + execute + static eval), refined by an
        # EMA in _prior_pass. The budget is built from it, so the same search spends the
        # same CPU on a machine half as fast — it just simulates less.
        self._est_expand_s = 0.0007
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
        n = len(playable_actions)
        if n <= 1:
            return 0

        left = obs.cpu_left if obs.cpu_left is not None else 0.010
        # Budget scales with the branching (each root action costs one expansion) and is
        # clamped so no single decision can eat the game's allowance.
        budget = n * self._est_expand_s + EXTRA_SIM_S
        budget = min(budget, WIDE_MAX_S if n >= 16 else NARROW_MAX_S)
        budget = min(budget, MAX_FRACTION * max(left, 0.0) - 0.0002)
        if budget < MIN_SEARCH_S:
            # Too little credit for even one expansion: pick by static priority, costs nothing.
            return max(range(n),
                       key=lambda i: _PRIORITY.get(playable_actions[i].action_type.name, 1))

        me = obs.me
        deadline = time.process_time() + budget
        agg = {}  # action index -> [visits, total], summed over sampled worlds
        worlds = 2 if n <= 10 else 1  # a second world only where the prior pass leaves room

        for _ in range(worlds):
            if time.process_time() >= deadline:
                break
            world = obs.sample_world(self.rng)
            root = _Node(world, me)
            self._prior_pass(root, deadline)  # every root action scored one ply deep
            while time.process_time() < deadline:
                self._simulate(root, deadline)
            for i, child in root.children.items():
                if child.visits:
                    stats = agg.setdefault(i, [0, 0.0])
                    stats[0] += child.visits
                    stats[1] += child.total

        if not agg:
            # Nothing was simulated (should not happen): a static priority pick costs nothing.
            return max(range(n),
                       key=lambda i: _PRIORITY.get(playable_actions[i].action_type.name, 1))
        return max(agg, key=lambda i: (agg[i][1] / agg[i][0], agg[i][0], -i))

    # ------------------------------------------------------------------ search pieces

    def _prior_pass(self, root, deadline):
        """Expand and statically evaluate EVERY root action once — F's whole computation.

        No legal move is ever ignored just because the simulation count is small, and UCB
        starts from a real value per action. Actions that happen to be illegal in this sampled
        world (a dev card the sampled deck does not have, say) are dropped, as F drops them.

        Each expansion also feeds the EMA the next budget is computed from. The EMA is
        deliberately allowed to run over the deadline by at most one expansion, so the root
        pass always values every action: F's baseline quality is guaranteed even on a slow
        machine, and only the refinement simulations shrink.
        """
        for i in list(root.untried):
            t0 = time.process_time()
            child = self._expand_one(root, i)
            if child is not None:
                child.visits = 1
                child.total = VALUE_FN(child.game, child.me) / REWARD_SCALE
            spent = time.process_time() - t0
            self._est_expand_s += 0.1 * (max(spent, 1e-6) - self._est_expand_s)
            if time.process_time() >= deadline:
                return

    def _expand_one(self, node, i):
        """Create the child for action index i; None if the action fails in this world."""
        try:
            g = node.game.copy()
            g.execute(node.game.playable_actions[i], validate_action=False)
        except Exception:
            node.untried.remove(i)  # dead in this world; never try it again
            return None
        child = _Node(g, node.me)
        node.children[i] = child
        node.untried.remove(i)
        return child

    def _simulate(self, root, deadline):
        """One UCT iteration: descend, expand one child, truncated rollout, backpropagate."""
        path = self._descend(root, deadline)
        leaf = path[-1]
        if leaf.winner is not None:
            reward = WIN_REWARD if leaf.winner == root.me else -WIN_REWARD
        else:
            reward = self._rollout(leaf, deadline)
        for node in path:
            node.visits += 1
            node.total += reward

    def _descend(self, root, deadline):
        """From root, walk down fully-expanded non-terminal nodes by UCB — maximising on our
        turns, minimising on the opponent's — expanding one new child as soon as one exists."""
        path = [root]
        node = root
        while True:
            if node.winner is not None:
                return path
            if node.untried:
                child = self._expand_one(node, node.untried[0])
                if child is None:
                    continue  # that action is dead in this world; try the next one
                path.append(child)
                return path
            if not node.children:
                return path  # terminal: no legal actions at all
            log_n = math.log(node.visits + 1.0)
            maximize = node.color == node.me
            best_i, best_s = None, None
            for i, child in node.children.items():
                q = child.total / child.visits
                # UCB from the perspective of whoever decides here: we maximise our value,
                # the opponent minimises it. The bonus is the same for both.
                s = (q if maximize else -q) + UCB_C * math.sqrt(log_n / child.visits)
                if best_s is None or s > best_s:
                    best_i, best_s = i, s
            node = node.children[best_i]
            path.append(node)

    def _rollout(self, node, deadline):
        """Play at most ROLLOUT_DEPTH random legal moves, then score the position.

        Truncated, never to game end: a full playout costs ~50 ms, more than the whole
        per-decision budget. The engine draws dice, dev cards and stolen cards from Python's
        global random, which the harness reseeds per game, so rollouts replay exactly.
        """
        g = node.game.copy()
        winner = g.winning_color()
        depth = 0
        while winner is None and depth < ROLLOUT_DEPTH:
            acts = g.playable_actions
            if not acts:
                break
            g.execute(acts[self.rng.randrange(len(acts))], validate_action=False)
            depth += 1
            winner = g.winning_color()
            if time.process_time() >= deadline:
                break
        if winner is not None:
            return WIN_REWARD if winner == node.me else -WIN_REWARD
        return VALUE_FN(g, node.me) / REWARD_SCALE

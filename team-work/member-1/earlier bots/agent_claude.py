import math
import random
import time

from catanatron.models.player import Color, Player
from catanatron.players.value import DEFAULT_WEIGHTS, base_fn

VALUE_FN = base_fn(DEFAULT_WEIGHTS)

EXTRA_SIM_S = 0.004
NARROW_MAX_S = 0.010
WIDE_MAX_S = 0.030
MAX_FRACTION = 0.30
MIN_SEARCH_S = 0.002
ROLLOUT_DEPTH = 6
UCB_C = 1.2
WIN_REWARD = 1e9
REWARD_SCALE = 1e8

_PRIORITY = {
    "PLAY_ROAD_BUILDING": 9, "BUILD_CITY": 8, "BUILD_SETTLEMENT": 7,
    "BUY_DEVELOPMENT_CARD": 6, "PLAY_KNIGHT_CARD": 5, "BUILD_ROAD": 5,
    "PLAY_YEAR_OF_PLENTY": 4, "PLAY_MONOPOLY": 4, "MOVE_ROBBER": 3,
    "DISCARD_RESOURCE": 2, "MARITIME_TRADE": 1, "ROLL": 1, "END_TURN": 0,
}

class _Node:
    __slots__ = ("game", "me", "color", "children", "untried", "visits", "total", "winner")
    def __init__(self, game, me):
        self.game = game
        self.me = me
        self.color = game.state.current_color()
        self.children = {}
        acts = game.playable_actions
        self.untried = sorted(range(len(acts)),
                              key=lambda i: -_PRIORITY.get(acts[i].action_type.name, 1))
        self.visits = 0
        self.total = 0.0
        self.winner = game.winning_color()

class Agent:
    def __init__(self):
        self.rng = random.Random(0)
        self._est_expand_s = 0.0007
        try:
            from catanatron.game import Game
            g = Game(players=[Player(Color.RED), Player(Color.BLUE)], seed=1)
            g.execute(g.playable_actions[0], validate_action=False)
            VALUE_FN(g, Color.RED)
        except Exception:
            pass

    def decide(self, obs, playable_actions):
        try:
            return self._decide(obs, playable_actions)
        except Exception:
            return self.rng.randrange(len(playable_actions))

    def _decide(self, obs, playable_actions):
        n = len(playable_actions)
        if n <= 1:
            return 0
        left = obs.cpu_left if obs.cpu_left is not None else 0.010
        budget = n * self._est_expand_s + EXTRA_SIM_S
        budget = min(budget, WIDE_MAX_S if n >= 16 else NARROW_MAX_S)
        budget = min(budget, MAX_FRACTION * max(left, 0.0) - 0.0002)
        if budget < MIN_SEARCH_S:
            return max(range(n), key=lambda i: _PRIORITY.get(playable_actions[i].action_type.name, 1))
        me = obs.me
        deadline = time.process_time() + budget
        agg = {}
        worlds = 2 if n <= 10 else 1
        for _ in range(worlds):
            if time.process_time() >= deadline:
                break
            world = obs.sample_world(self.rng)
            root = _Node(world, me)
            self._prior_pass(root, deadline)
            while time.process_time() < deadline:
                self._simulate(root, deadline)
            for i, child in root.children.items():
                if child.visits:
                    stats = agg.setdefault(i, [0, 0.0])
                    stats[0] += child.visits
                    stats[1] += child.total
        if not agg:
            return max(range(n), key=lambda i: _PRIORITY.get(playable_actions[i].action_type.name, 1))
        return max(agg, key=lambda i: (agg[i][1] / agg[i][0], agg[i][0], -i))

    def _prior_pass(self, root, deadline):
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
        try:
            g = node.game.copy()
            g.execute(node.game.playable_actions[i], validate_action=False)
        except Exception:
            node.untried.remove(i)
            return None
        child = _Node(g, node.me)
        node.children[i] = child
        node.untried.remove(i)
        return child

    def _simulate(self, root, deadline):
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
        path = [root]
        node = root
        while True:
            if node.winner is not None:
                return path
            if node.untried:
                child = self._expand_one(node, node.untried[0])
                if child is None:
                    continue
                path.append(child)
                return path
            if not node.children:
                return path
            log_n = math.log(node.visits + 1.0)
            maximize = node.color == node.me
            best_i, best_s = None, None
            for i, child in node.children.items():
                q = child.total / child.visits
                s = (q if maximize else -q) + UCB_C * math.sqrt(log_n / child.visits)
                if best_s is None or s > best_s:
                    best_i, best_s = i, s
            node = node.children[best_i]
            path.append(node)

    def _rollout(self, node, deadline):
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

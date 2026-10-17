"""F, rebuilt on the 614-feature vector: the useful subset only.

F (examples/f_agent.py) keeps catanatron's search — sample one world, try every legal move,
play the argmax of a 13-feature weighted sum — but its value function reads raw engine state.
This agent keeps that search and F's exact weight ladder, and rebuilds every feature from the
standard 614-feature sample (catanatron.features.create_sample), which is what a learned
evaluation would read. Of the 614 features, these are used:

  player/hand block
    P0_PUBLIC_VPS               -> F's public_vps (weight 3e14: VPs dominate everything)
    P0_{WOOD,BRICK,SHEEP,WHEAT,ORE}_IN_HAND  -> hand_synergy, F's exact formula
    P0_NUM_RESOURCES_IN_HAND    -> hand_resources and the >7 discard_penalty flag
    P0_NUM_DEVS_IN_HAND         -> hand_devs
    P0_KNIGHT_PLAYED            -> army_size
    P0_VICTORY_POINT_IN_HAND    -> NEW: F never values its own hidden VP cards; the vector
                                   carries the exact count for our seat (P0 only)
    P0_LONGEST_ROAD_LENGTH      -> longest_road
  graph block
    NODE{n}_P{0,1}_{SETTLEMENT,CITY}, EDGE{(a,b)}_P{0,1}_ROAD one-hots
    -> ownership flags. Combined with static board geometry (pip probabilities per node —
       the same numbers the vector's TILE*_PROBA features encode), they reconstruct F's
       production, enemy_production (robber-filtered, cities 2x, variety bonus on ours) and
       the one-road expansion frontier.

DROPPED, AND WHY
  * reachable_production_0 (F's weight is 0 — redundant with production);
  * num_tiles (weight 1 at F's scale, pure tiebreak noise);
  * F's longest-road x10-when-walled-in switch: buildable-spot counts are not in the vector,
    so longest road gets a small constant weight instead;
  * buildable_nodes merges into the frontier term (same information: room to expand).
The 614-vector is read via create_sample (the dict that create_sample_vector projects), so
this evaluation sees exactly what a learned evaluation trained on the vector could see — plus
board geometry, which is constant per game.

The clock discipline is the kit's: time.process_time() budgets (candidates x live EMA of one
evaluation), capped at 30% of obs.cpu_left, hard NARROW/WIDE ceilings under the 12.5 ms
per-decision increment, and a zero-cost static-priority pick when the credit is gone. The
agent never raises: an escaped exception falls back to a random legal index, because errors
above 2% of decisions disqualify a submission (PROBLEM_STATEMENT.md, section 4.2).
"""
import random
import time

from catanatron.features import create_sample
from catanatron.models.board import STATIC_GRAPH
from catanatron.models.enums import RESOURCES
from catanatron.models.map import number_probability
from catanatron.models.player import Color, Player

# --- F's weight ladder (same values; see the module docstring for the deltas) ----------
WEIGHT_PUBLIC_VPS = 3e14        # F: public_vps
WEIGHT_PRODUCTION = 1e8         # F: production (robber-adjusted, +variety)
WEIGHT_ENEMY_PRODUCTION = 1e8   # F: enemy_production (subtracted, no variety)
WEIGHT_FRONTIER = 1e4           # F: reachable_production_1 (+ buildable_nodes 1e3, merged)
WEIGHT_HAND_SYNERGY = 1e2       # F: hand_synergy
WEIGHT_HAND_RESOURCES = 1.0     # F: hand_resources
DISCARD_PENALTY = -5.0          # F: discard_penalty (flat flag while holding >7 cards)
WEIGHT_HAND_DEVS = 10.0         # F: hand_devs
WEIGHT_ARMY = 10.1              # F: army_size
WEIGHT_LONGEST_ROAD = 0.5       # F: 0.1 normally, 10 when walled in; the switch needs
                                # buildable counts, so a small constant stands in
WEIGHT_HIDDEN_VP = 1e8          # added: one hidden VP is a real VP; F ignores them
TRANSLATE_VARIETY = 4           # F: each new resource ≈ 4 production points
PROBA_POINT = 2.778 / 100       # F: 1/36, the rarest roll's probability

# --- budget (seconds of CPU) ----------------------------------------------------------
NARROW_MAX_S = 0.012   # narrow decisions: under the 12.5 ms increment
WIDE_MAX_S = 0.045     # wide decisions (opening placement, robber); the 300 ms base
                       # exists for exactly these
MAX_FRACTION = 0.30    # never spend more than this share of the remaining allowance
MIN_SEARCH_S = 0.002   # below this, skip the pass for the zero-cost static pick
SAFETY = 1.2           # padding on the cost estimate before committing to the pass
EST_CANDIDATE_S = 0.0011  # copy + execute + sample + score, EMA-refined below

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
    """One-ply greedy like F; the value function reads the 614-feature sample."""

    def __init__(self):
        self.rng = random.Random(0)
        self._me = None
        # Live estimate of one candidate evaluation (copy + execute + sample + score),
        # EMA-refined every decision. The budget is built from it, so the same search spends
        # the same CPU on a machine half as fast — it just evaluates fewer candidates.
        self._est_cand_s = EST_CANDIDATE_S
        # Per-board static geometry, one slot for the current game's map (see _map_data).
        self._md_map = None
        self._md_nodes = ()
        self._md_node_tiles = {}
        self._md_node_prod = {}
        self._md_node_neighbors = {}
        self._md_edges = ()
        # Warm the code paths the first decision would otherwise pay for: engine imports,
        # feature extractors, the sample itself. The harness gives __init__ 60 uncharged
        # seconds; a broken warmup must not kill the agent.
        try:
            from catanatron.game import Game

            g = Game(players=[Player(Color.RED), Player(Color.BLUE)], seed=1)
            g.execute(g.playable_actions[0], validate_action=False)
            self._me = g.state.colors[0]
            self._score(g)
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
        root_cost = n * self._est_cand_s * SAFETY
        budget = min(root_cost,
                     WIDE_MAX_S if n >= 16 else NARROW_MAX_S,
                     MAX_FRACTION * max(left, 0.0) - 0.0002)
        if budget < MIN_SEARCH_S:
            # Not enough credit to evaluate even a few candidates: static priority, free.
            return self._static_index(playable_actions)

        deadline = time.process_time() + budget
        world = obs.sample_world(self.rng)   # one determinized world, like F

        # F's search: every candidate simulated on the sampled world, best one-ply successor
        # wins. Candidates are evaluated in static-priority order (building moves first, and
        # harness order within a type), so a cut-off pass — only possible under a nearly
        # spent allowance — has at least valued the important moves. Ties break on the first
        # candidate evaluated, deterministically.
        best_i, best_v = None, None
        order = sorted(range(n),
                       key=lambda i: -_PRIORITY.get(playable_actions[i].action_type.name, 1))
        for i in order:
            if time.process_time() >= deadline:
                break
            t0 = time.process_time()
            game = world.copy()
            try:
                game.execute(playable_actions[i], validate_action=False)
            except Exception:
                continue  # illegal in this world, as F treats it
            value = self._score(game)
            self._est_cand_s += 0.1 * (max(time.process_time() - t0, 1e-6)
                                       - self._est_cand_s)
            if best_v is None or value > best_v:
                best_i, best_v = i, value

        return self._static_index(playable_actions) if best_i is None else best_i

    # ------------------------------------------------------------------ value function

    def _score(self, game):
        """F's 13-feature ladder, with every feature read from the 614-feature sample.

        F's weight ordering is preserved: VPs dominate, then own production over enemy
        production, then expansion, then hand tactics.
        """
        s = create_sample(game, self._me)
        board = game.state.board
        robber_tile = (board.map.tiles[board.robber_coordinate]
                       if board.robber_coordinate is not None else None)
        self._map_data(board.map)

        # Production for both seats from the NODE one-hots: settlements count once, cities
        # twice, robber-blocked tiles zero — F's EFFECTIVE production, rebuilt.
        own = [0.0] * 5
        enemy = [0.0] * 5
        for i in (0, 1):
            prod = own if i == 0 else enemy
            for node in self._md_nodes:
                if s.get(f"NODE{node}_P{i}_CITY"):
                    mult = 2
                elif s.get(f"NODE{node}_P{i}_SETTLEMENT"):
                    mult = 1
                else:
                    continue
                for r, prob, tile in self._md_node_tiles[node]:
                    if tile is not robber_tile:
                        prod[r] += prob * mult
        prod = sum(own)
        variety = sum(1 for p in own if p > 0.0)  # F: +4/36 per resource produced at all
        enemy = sum(enemy)

        return float(
            s["P0_PUBLIC_VPS"] * WEIGHT_PUBLIC_VPS
            + (prod + variety * TRANSLATE_VARIETY * PROBA_POINT) * WEIGHT_PRODUCTION
            - enemy * WEIGHT_ENEMY_PRODUCTION
            + self._frontier(game, s) * WEIGHT_FRONTIER
            + WEIGHT_HAND_SYNERGY * self._synergy(s)
            + s["P0_NUM_RESOURCES_IN_HAND"] * WEIGHT_HAND_RESOURCES
            + (DISCARD_PENALTY if s["P0_NUM_RESOURCES_IN_HAND"] > 7 else 0.0)
            + s["P0_NUM_DEVS_IN_HAND"] * WEIGHT_HAND_DEVS
            + s["P0_KNIGHT_PLAYED"] * WEIGHT_ARMY
            + s["P0_VICTORY_POINT_IN_HAND"] * WEIGHT_HIDDEN_VP
            + s["P0_LONGEST_ROAD_LENGTH"] * WEIGHT_LONGEST_ROAD)

    def _synergy(self, s):
        """F's hand synergy, verbatim: distance to an affordable city and settlement."""
        d_city = (max(2 - s["P0_WHEAT_IN_HAND"], 0) + max(3 - s["P0_ORE_IN_HAND"], 0)) / 5.0
        d_settle = (max(1 - s["P0_WHEAT_IN_HAND"], 0) + max(1 - s["P0_SHEEP_IN_HAND"], 0)
                    + max(1 - s["P0_BRICK_IN_HAND"], 0)
                    + max(1 - s["P0_WOOD_IN_HAND"], 0)) / 4.0
        return (2 - d_city - d_settle) / 2.0

    def _frontier(self, game, s):
        """F's expansion term: expected production on empty, spacing-legal nodes one road
        away from our road network, never crossing enemy ground.

        Ownership comes from the NODE/EDGE one-hots in the vector; the pip probabilities and
        the buildable set come from the board (static geometry, the same board calls F's own
        value function makes).
        """
        buildable = game.state.board.board_buildable_ids
        # Our road network: every node incident to one of our roads, plus our buildings.
        comp = set()
        for edge in self._md_edges:
            if s.get(f"EDGE{edge}_P0_ROAD"):
                comp.update(edge)
        for node in self._md_nodes:
            if s.get(f"NODE{node}_P0_SETTLEMENT") or s.get(f"NODE{node}_P0_CITY"):
                comp.add(node)
        # One layer out, through edges the opponent does not own, onto buildable ground.
        total = 0.0
        seen = set()
        for node in comp:
            for m in self._md_node_neighbors[node]:
                if m in seen or m not in buildable:
                    continue
                seen.add(m)
                edge = (node, m) if node < m else (m, node)
                if s.get(f"EDGE{edge}_P1_ROAD"):
                    continue  # the reaching road would have to cross enemy ground
                total += self._md_node_prod[m]
        return total

    # ------------------------------------------------------------------ plumbing

    def _map_data(self, map_obj):
        """Cache the static geometry of the current board (one slot: the current game's map).
        Pip probabilities, per-node production totals, the road graph are constants of the
        board — rebuilt only when the game (and its map) changes."""
        if self._md_map is map_obj:
            return
        nodes = tuple(sorted(map_obj.land_nodes))
        self._md_map = map_obj
        self._md_nodes = nodes
        self._md_node_tiles = {
            node: tuple((RESOURCES.index(t.resource), number_probability(t.number), t)
                        for t in map_obj.adjacent_tiles[node] if t.resource is not None)
            for node in nodes}
        self._md_node_prod = {node: sum(map_obj.node_production[node].values())
                              for node in nodes}
        self._md_node_neighbors = {node: tuple(STATIC_GRAPH.neighbors(node))
                                   for node in nodes}
        edges = []
        for node in nodes:
            for m in self._md_node_neighbors[node]:
                if node < m:
                    edges.append((node, m))
        self._md_edges = tuple(edges)

    def _static_index(self, playable_actions):
        """Zero-cost fallback when there is no time to evaluate anything."""
        return max(range(len(playable_actions)),
                   key=lambda i: _PRIORITY.get(playable_actions[i].action_type.name, 1))

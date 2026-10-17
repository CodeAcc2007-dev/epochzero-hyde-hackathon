"""Regressions for B03/B04 v003 against the 2026-10-17 independent review's verified defects.

Each test first reproduces the parent (v002) defect using the review's own constructed
fixtures (reusing team-work/member-3/implementation/test_policies.py's engine-state helpers,
the same pattern team-work/reviews/2026-10-17-B03-B08/verify_findings.py uses), then asserts
the new version (v003) is corrected on the identical fixture. This proves each regression
actually exercises the parent defect before trusting it as a fix.

Run:  ./team-work/run-python.sh -m unittest team-work/member-2/implementation/test_b03_b04_v003.py -v
"""
import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "team-work/member-3/implementation"))
import test_policies as f  # noqa: E402

from catan_kit.obs import Obs  # noqa: E402
from catanatron.models.enums import ActionType as AT  # noqa: E402

B03_V002 = ROOT / "team-work/member-2/bots/B03/v002/agent.py"
B03_V003 = ROOT / "team-work/member-2/bots/B03/v003/agent.py"
B04_V002 = ROOT / "team-work/member-2/bots/B04/v002/agent.py"
B04_V003 = ROOT / "team-work/member-2/bots/B04/v003/agent.py"

EXPECTED_HASHES = {
    B03_V002: "1a4a304932718ba2b76af1ff966bb08c55c5c00c7a0ef5c0f9cf788bdcc66e30",
    B04_V002: "763c88df0a815aeb97bf6cc1bb02865f8bb148c58bed6965ffb54911907d0b45",
}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ParentHashTests(unittest.TestCase):
    def test_parent_hashes_match_review(self):
        for path, expected in EXPECTED_HASHES.items():
            self.assertEqual(sha256(path), expected, f"{path} hash drifted from the reviewed parent")


class B03ReachTests(unittest.TestCase):
    """B03-01: _opp_reach must count nodes already reachable via the opponent's existing
    road network at zero additional cost, not just two hops from their buildings."""

    def test_v002_misses_node39_v003_includes_it(self):
        g, c = f.fresh()
        enemy = next(x for x in g.state.colors if x != c)
        f.extend_road(g, enemy, 6)
        f.invariant(g)
        buildable = set(g.state.board.buildable_node_ids(enemy))

        v002 = load("b03_v002", B03_V002).Agent()
        v003 = load("b03_v003", B03_V003).Agent()
        reach_v002 = v002._opp_reach(Obs(g, c), c)
        reach_v003 = v003._opp_reach(Obs(g, c), c)

        missing_v002 = sorted(buildable - reach_v002)
        missing_v003 = sorted(buildable - reach_v003)
        self.assertEqual(missing_v002, [39], "parent defect not reproduced on this fixture")
        self.assertEqual(missing_v003, [], "v003 still omits a legally reachable opponent node")
        self.assertIn(39, reach_v003)


class B04EndpointTests(unittest.TestCase):
    """B04-01: the road endpoint tuple is (n1, n2) with n1 < n2 (an arbitrary sort order,
    not direction); the newly-reached port node must be identified from connectivity."""

    def test_v002_scores_wrong_endpoint_v003_scores_new_port(self):
        g, c = f.fresh()
        front = [(g, [])]
        found = None
        for _depth in range(5):
            nxt = []
            for g_, history in front:
                f.set_hand(g_, c, (1, 1, 0, 0, 0))
                ports = set().union(*g_.state.board.map.port_nodes.values())
                connected = set().union(*g_.state.board.connected_components[c])
                for a in g_.playable_actions:
                    if a.action_type != AT.BUILD_ROAD:
                        continue
                    if a.value[1] in connected and a.value[0] not in connected and a.value[0] in ports:
                        found = (g_, c, a, connected)
                        break
                    h = g_.copy()
                    h.execute(a)
                    nxt.append((h, history + [list(a.value)]))
                if found:
                    break
            if found:
                break
            front = nxt[:500]
        self.assertIsNotNone(found, "could not construct the review's road-to-port fixture")
        g, c, a, connected = found
        f.invariant(g)
        new_port_node, already_connected_node = a.value[0], a.value[1]
        self.assertNotIn(new_port_node, connected)
        self.assertIn(already_connected_node, connected)

        h = g.copy()
        h.execute(a)

        v002 = load("b04_v002", B04_V002).Agent()
        seen_v002 = []
        v002._justified_port_value = lambda obs, me, node, child, scale: (seen_v002.append(node) or 0)
        v002._port_bonus(Obs(g, c), c, a, h)
        self.assertEqual(seen_v002, [already_connected_node], "parent defect not reproduced on this fixture")

        v003 = load("b04_v003", B04_V003).Agent()
        seen_v003 = []
        v003._justified_port_value = lambda obs, me, node, child, scale: (seen_v003.append(node) or 0)
        v003._port_bonus(Obs(g, c), c, a, h)
        self.assertEqual(seen_v003, [new_port_node], "v003 still scores the wrong road endpoint")


class B04ProductionThresholdTests(unittest.TestCase):
    """B04-02: zero specialized production must earn zero bonus; the exact 5/36 threshold
    must be honored, not a rounded decimal that is slightly larger than 5/36."""

    def test_v002_overcredits_zero_production_v003_does_not(self):
        g, c = f.fresh()
        resource, nodes = next((r, n) for r, n in g.state.board.map.port_nodes.items() if r is not None)
        node = next(iter(nodes))

        v002 = load("b04_v002_thresh", B04_V002).Agent()
        v002._my_production = lambda game, me: {resource: 0.0}
        self.assertEqual(v002._justified_port_value(Obs(g, c), c, node, g, 3e6), 300000,
                         "parent defect not reproduced: zero production should have earned scale*0.1")

        v003 = load("b04_v003_thresh", B04_V003).Agent()
        v003._my_production = lambda game, me: {resource: 0.0}
        self.assertEqual(v003._justified_port_value(Obs(g, c), c, node, g, 3e6), 0.0,
                         "v003 still grants a port bonus at zero specialized production")

        v003._my_production = lambda game, me: {resource: 5.0 / 36.0}
        self.assertEqual(v003._justified_port_value(Obs(g, c), c, node, g, 3e6), 3e6,
                         "v003 does not honor the exact 5/36 threshold")


class ObservabilityTests(unittest.TestCase):
    """M2-C01/M2-OBSERVABILITY: a scoring failure on one candidate must not silently
    discard every already-evaluated action; the best incumbent so far must be kept."""

    def _single_fully_failing_agent_falls_back(self, module, agent_attr):
        g, c = f.fresh()
        f.set_hand(g, c, (4, 4, 1, 1, 1))
        agent = module.Agent()

        def fail(*args, **kwargs):
            raise RuntimeError("injected test sentinel")
        setattr(agent, agent_attr, fail)
        obs = Obs(g, c)
        obs.cpu_left = 1.0
        chosen = g.playable_actions[agent.decide(obs, g.playable_actions)]
        return chosen

    def test_v002_total_failure_falls_back_to_end_turn(self):
        chosen = self._single_fully_failing_agent_falls_back(load("b03_v002_obs", B03_V002), "_score")
        self.assertEqual(chosen.action_type, AT.END_TURN)

    def test_v003_partial_failure_keeps_best_incumbent_not_blind_end_turn(self):
        g, c = f.fresh()
        f.set_hand(g, c, (4, 4, 1, 1, 1))
        module = load("b03_v003_obs", B03_V003)
        agent = module.Agent()
        real_value_fn = agent._value_fn
        calls = {"n": 0}

        def flaky(game_copy, me):
            calls["n"] += 1
            if calls["n"] > 1:
                raise RuntimeError("injected test sentinel")
            return real_value_fn(game_copy, me)
        agent._value_fn = flaky

        obs = Obs(g, c)
        obs.cpu_left = 1.0
        idx = agent.decide(obs, g.playable_actions)
        self.assertEqual(agent.diagnostics["evaluated"], 1)
        self.assertEqual(agent.diagnostics["exceptions"], len(g.playable_actions) - 1)
        self.assertEqual(idx, 0, "v003 should keep the first (only successfully scored) action as incumbent")


class GuaranteedWinTests(unittest.TestCase):
    """M2-C02: an immediate own win must be taken regardless of heuristic/bonus scoring."""

    def _winning_fixture(self):
        g, c = f.near_win()
        g = f.road_settlement_fixture(g, c)
        for a in g.playable_actions:
            if a.action_type != AT.BUILD_ROAD:
                continue
            h = g.copy()
            h.execute(a)
            if any(b.action_type == AT.BUILD_SETTLEMENT for b in h.playable_actions):
                g = h
                break
        f.set_hand(g, c, (1, 1, 1, 1, 0))
        f.invariant(g)
        # NOTE: this fixture can have more than one immediately-winning legal action (e.g. a
        # road that completes Longest Road is also legal and also wins at 9 actual VP plus
        # the 2-point bonus). The acceptance criterion is therefore "the chosen action wins",
        # not "the chosen action is this particular one" -- any confirmed win is correct.
        winning_indices = set()
        for i, a in enumerate(g.playable_actions):
            h = g.copy()
            h.execute(a)
            if h.winning_color() == c:
                winning_indices.add(i)
        self.assertTrue(winning_indices, "fixture has no immediately-winning legal action")
        return g, c, winning_indices

    def test_b03_v003_takes_the_win(self):
        g, c, winning_indices = self._winning_fixture()
        agent = load("b03_v003_win", B03_V003).Agent()
        obs = Obs(g, c)
        obs.cpu_left = 1.0
        idx = agent.decide(obs, g.playable_actions)
        self.assertIn(idx, winning_indices)
        self.assertEqual(agent.diagnostics["guaranteed_wins"], 1)

    def test_b04_v003_takes_the_win(self):
        g, c, winning_indices = self._winning_fixture()
        agent = load("b04_v003_win", B04_V003).Agent()
        obs = Obs(g, c)
        obs.cpu_left = 1.0
        idx = agent.decide(obs, g.playable_actions)
        self.assertIn(idx, winning_indices)
        self.assertEqual(agent.diagnostics["guaranteed_wins"], 1)

    def test_low_clock_still_takes_the_win(self):
        """COMMON-01-style probe: a near-exhausted clock must not block an immediate win."""
        g, c, winning_indices = self._winning_fixture()
        for module_path, cls in ((B03_V003, "B03"), (B04_V003, "B04")):
            agent = load(f"{cls}_v003_lowclock", module_path).Agent()
            obs = Obs(g, c)
            obs.cpu_left = 0.0009
            idx = agent.decide(obs, g.playable_actions)
            self.assertIn(idx, winning_indices, f"{cls} failed the low-clock win check")
            self.assertEqual(agent.diagnostics["low_clock_decisions"], 1)
            self.assertEqual(agent.diagnostics["guaranteed_wins"], 1)


class ContractTests(unittest.TestCase):
    """Legality and non-mutation, both seats, for both v003 agents on a fresh state."""

    def test_both_bots_both_seats_legal_and_nonmutating(self):
        for module_path in (B03_V003, B04_V003):
            g, c = f.fresh()
            for color in g.state.colors:
                before = (repr(g.state.player_state), repr(g.state.board.buildings),
                          repr(g.state.board.roads), list(g.state.resource_freqdeck),
                          list(g.state.development_listdeck), list(g.state.action_records))
                agent = load(f"contract_{module_path.parent.parent.name}_{color}", module_path).Agent()
                obs = Obs(g, color)
                obs.cpu_left = 1.0
                idx = agent.decide(obs, g.playable_actions)
                after = (repr(g.state.player_state), repr(g.state.board.buildings),
                         repr(g.state.board.roads), list(g.state.resource_freqdeck),
                         list(g.state.development_listdeck), list(g.state.action_records))
                self.assertEqual(before, after, "observation/game state was mutated")
                self.assertIsInstance(idx, int)
                self.assertFalse(isinstance(idx, bool))
                self.assertTrue(0 <= idx < len(g.playable_actions))


if __name__ == "__main__":
    unittest.main()

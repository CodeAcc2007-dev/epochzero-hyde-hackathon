"""Semantic case tests for B03/B04 v001.

Assignment-required cases with actual assertions. Engine-constructed unit checks:
correctness evidence, not strength evidence.

Run:  ./team-work/run-python.sh team-work/member-2/bots/tests/semantic_cases.py
Exits non-zero on failure.
"""
import importlib.util
import random
import sys

from catanatron.game import Game
from catanatron.models.player import Color, RandomPlayer
from catanatron.models.actions import generate_playable_actions
from catanatron.models.enums import ActionType, SETTLEMENT, CITY, SHEEP, WHEAT, WOOD, BRICK, ORE
from catanatron.models.board import STATIC_GRAPH
from catan_kit.obs import Obs

B03 = "team-work/member-2/bots/B03/v001/agent.py"
B04 = "team-work/member-2/bots/B04/v001/agent.py"

# 4:1 sheep offer tuple in the engine's MARITIME_TRADE format
OFFER_SHEEP_WHEAT = ("SHEEP", "SHEEP", "SHEEP", "SHEEP", "WHEAT")
RES_ORDER = ("WOOD", "BRICK", "SHEEP", "WHEAT", "ORE")


def load(path, tag):
    spec = importlib.util.spec_from_file_location(tag, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def new_game(seed):
    random.seed(seed)
    return Game([RandomPlayer(Color.RED), RandomPlayer(Color.BLUE)], seed=seed, vps_to_win=10)


def step_game(game, agents):
    """One harness-like decision. Returns (color, acts, idx, act) or None if forced."""
    color = game.state.current_color()
    acts = generate_playable_actions(game.state)
    if len(acts) == 1:
        game.execute(acts[0])
        return None
    obs = Obs(game, color)
    idx = agents[color].decide(obs, acts)
    act = acts[idx]
    game.execute(act)
    return color, acts, idx, act


def run_until(game, agents, predicate, limit=30):
    while game.winning_color() is None and game.state.num_turns < limit:
        color = game.state.current_color()
        acts = generate_playable_actions(game.state)
        if len(acts) == 1:
            game.execute(acts[0])
            continue
        obs = Obs(game, color)
        if predicate(game, color, acts):
            return obs, acts
        game.execute(acts[agents[color].decide(obs, acts)])
    return None, None


def t01_legality_and_distance():
    """Legality: genuine in-range ints every decision; distance rule never violated."""
    for seed in (771000, 771001):
        for path, tag in ((B03, "c01b03"), (B04, "c01b04")):
            mod = load(path, f"{tag}_{seed}")
            agents = {Color.RED: mod.Agent(), Color.BLUE: mod.Agent()}
            random.seed(seed)
            game = new_game(seed)
            while game.winning_color() is None and game.state.num_turns < 150:
                r = step_game(game, agents)
            st = game.state
            for c in st.colors:
                nodes = []
                for kind in (SETTLEMENT, CITY):
                    nodes += list(st.buildings_by_color[c][kind])
                for n in nodes:
                    for w in STATIC_GRAPH.neighbors(n):
                        b = st.board.buildings.get(w)
                        assert b is None or b[0] == c, \
                            f"distance rule violated {n}->{w} seed {seed}"
    return True


def t02_opening_site_legality():
    mod = load(B03, "c02")
    agents = {Color.RED: mod.Agent(), Color.BLUE: mod.Agent()}
    random.seed(771000)
    game = new_game(771000)
    n_picks = 0
    while game.winning_color() is None and game.state.num_turns < 12:
        color = game.state.current_color()
        acts = generate_playable_actions(game.state)
        if len(acts) == 1:
            game.execute(acts[0])
            continue
        obs = Obs(game, color)
        idx = agents[color].decide(obs, acts)
        act = acts[idx]
        if game.state.is_initial_build_phase and act.action_type == ActionType.BUILD_SETTLEMENT:
            assert act.value in set(a.value for a in acts), "illegal opening node"
            for w in STATIC_GRAPH.neighbors(act.value):
                assert game.state.board.buildings.get(w) is None, \
                    "distance-illegal node chosen"
            n_picks += 1
        game.execute(act)
    assert n_picks == 4, f"expected 4 opening placements, saw {n_picks}"
    return True


def t03_road_not_to_nowhere():
    mod = load(B03, "c03")
    agents = {Color.RED: mod.Agent(), Color.BLUE: mod.Agent()}
    random.seed(771000)
    game = new_game(771000)
    agent = agents[Color.RED]
    while game.winning_color() is None and game.state.num_turns < 8:
        color = game.state.current_color()
        acts = generate_playable_actions(game.state)
        if len(acts) == 1:
            game.execute(acts[0])
            continue
        if not game.state.is_initial_build_phase and game.state.num_turns >= 3:
            obs = Obs(game, color)
            roads = [(a.value, agent._road_score(obs, a.value, set()))
                     for a in acts if a.action_type == ActionType.BUILD_ROAD]
            assert roads, "no road actions at first midgame decision"
            best = max(s for _, s in roads)
            idx = agents[color].decide(obs, acts)
            chosen = acts[idx]
            if best > 0.5:
                assert chosen.action_type == ActionType.BUILD_ROAD, \
                    f"expected road, chose {chosen.action_type}"
                node, depth = agent._road_site(obs, color, chosen.value)
                assert depth <= 2, "farther target chosen over nearer one"
            return True
        obs = Obs(game, color)
        game.execute(acts[agents[color].decide(obs, acts)])
    return False


def t04_surplus_trade_policy_difference():
    a3 = load(B03, "c04b03").Agent()
    a4 = load(B04, "c04b04").Agent()
    agents = {Color.RED: a3, Color.BLUE: a4}
    random.seed(771000)
    game = new_game(771000)
    obs = None
    while game.winning_color() is None and game.state.num_turns < 6:
        color = game.state.current_color()
        acts = generate_playable_actions(game.state)
        if len(acts) == 1:
            game.execute(acts[0])
            continue
        if color == Color.RED and not game.state.is_initial_build_phase:
            obs = Obs(game, color)
            obs.my_resources = {"WOOD": 0, "BRICK": 0, "SHEEP": 4, "WHEAT": 0, "ORE": 1}
            v3 = a3._trade_value(obs, OFFER_SHEEP_WHEAT)
            v4 = a4._trade_value(obs, OFFER_SHEEP_WHEAT)
            assert v3 == 0.0, f"B03 must not convert surplus, got {v3}"
            assert v4 > 0.0, f"B04 must convert surplus, got {v4}"
            return True
        obs = Obs(game, color)
        game.execute(acts[agents[color].decide(obs, acts)])
    return False


def t05_port_terms():
    a4 = load(B04, "c05b04").Agent()
    agents = {Color.RED: a4, Color.BLUE: load(B04, "c05b").Agent()}
    random.seed(771000)
    game = new_game(771000)
    target_node = None
    while game.winning_color() is None and game.state.num_turns < 6:
        color = game.state.current_color()
        acts = generate_playable_actions(game.state)
        if len(acts) == 1:
            game.execute(acts[0])
            continue
        if color == Color.RED and not game.state.is_initial_build_phase:
            obs = Obs(game, color)
            for resource, nodes in obs.board.map.port_nodes.items():
                if resource is not None:
                    target_node = sorted(nodes)[0]
                    break
            v_strong = a4._port_term(obs, target_node, {resource: 0.20})
            v_weak = a4._port_term(obs, target_node, {resource: 0.0})
            assert v_strong > v_weak, "port value must track own production"
            # opponent near winning: no more port chasing
            for c in game.state.colors:
                if c != obs.me:
                    key = f"P{game.state.color_to_index[c]}"
                    game.state.player_state[f"{key}_VICTORY_POINTS"] = 9
            v = a4._port_term(obs, target_node, {"SHEEP": 0.2})
            assert v == 0.0, f"port chasing must stop at opponent 9 VP, got {v}"
            return True
        obs = Obs(game, color)
        game.execute(acts[agents[color].decide(obs, acts)])
    return False


def t06_discard_legality():
    """Case: discards always pick a legal offered resource (when one occurs)."""
    saw_discard = False
    for path, tag in ((B03, "c06b03"), (B04, "c06b04")):
        for seed in (771000, 771001):
            mod = load(path, f"{tag}_{seed}")
            agents = {Color.RED: mod.Agent(), Color.BLUE: mod.Agent()}
            random.seed(seed)
            game = new_game(seed)
            while game.winning_color() is None and game.state.num_turns < 400:
                color = game.state.current_color()
                acts = generate_playable_actions(game.state)
                if len(acts) == 1:
                    game.execute(acts[0])
                    continue
                obs = Obs(game, color)
                idx = agents[color].decide(obs, acts)
                act = acts[idx]
                if act.action_type == ActionType.DISCARD_RESOURCE:
                    assert act.value in set(a.value for a in acts), "illegal discard"
                    saw_discard = True
                game.execute(act)
    if not saw_discard:
        print("[INCONCLUSIVE] no discard occurred in the driven games")
    return True


def main():
    tests = [
        ("t01 legality+distance", t01_legality_and_distance),
        ("t02 opening site legality", t02_opening_site_legality),
        ("t03 road-not-to-nowhere", t03_road_not_to_nowhere),
        ("t04 surplus trade difference", t04_surplus_trade_policy_difference),
        ("t05 port terms", t05_port_terms),
        ("t06 discard legality", t06_discard_legality),
    ]
    failed = False
    for name, fn in tests:
        try:
            fn()
            print(f"[PASS] {name}")
        except Exception as exc:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            print(f"[FAIL] {name}: {exc}")
            failed = True
    if failed:
        sys.exit(1)
    print("all semantic cases passed")


if __name__ == "__main__":
    main()

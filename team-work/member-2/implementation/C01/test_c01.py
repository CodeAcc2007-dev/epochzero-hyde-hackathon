"""C01-specific checks on constructed engine states (not match evidence).

M is injected by verify_c01.py with the frozen or ZIP-extracted C01 module.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'team-work/member-1/implementation/round-2'))
import test_terminal_regressions as r  # noqa: E402
from catanatron.models.enums import ActionType as AT  # noqa: E402

M = None


def post_roll(seat, h, vp=None, road=None):
    g, c = r.near(seat, vp) if vp else r.f.fresh()
    if vp is None and seat:
        c = next(x for x in g.state.colors if x != c)
    if road:
        r.f.extend_road(g, c, road)
    r.f.phase(g, c, True)
    r.f.set_hand(g, c, h)
    r.f.invariant(g)
    return g, c


def rows(g, c):
    out = []
    for i, a in enumerate(g.playable_actions):
        if a.action_type == AT.END_TURN:
            continue
        child = g.copy()
        child.execute(a)
        if child.state.current_color() == c:
            out.append((0.0, i, child))
    return out


class EnablerTests(unittest.TestCase):
    def test_reserves_only_positive_progress_roots_at_most_two(self):
        for seat in (0, 1):
            g, c = post_roll(seat, (4, 0, 0, 2, 2))
            r.f.add_settlement(g, c) if not g.state.buildings_by_color[c]['SETTLEMENT'] else None
            r.f.phase(g, c, True)
            ctx = M.EconomyContext(g, c)
            before = M.hand(g.state, ctx.key)
            chosen = M.EconomyPolicy.reserve_enablers(g, ctx, rows(g, c))
            self.assertLessEqual(len(chosen), 2)
            for _, i, child in chosen:
                kind = g.playable_actions[i].action_type
                self.assertIn(kind, (AT.MARITIME_TRADE, AT.PLAY_YEAR_OF_PLENTY, AT.PLAY_MONOPOLY, AT.BUILD_ROAD))
                if kind == AT.MARITIME_TRADE:
                    after = M.hand(child.state, ctx.key)
                    self.assertGreater(M.deficit(before, M.CITY) - M.deficit(after, M.CITY), 0)
            # 4 WOOD -> ORE completes the city; it must be among the reserved enablers.
            kinds = [g.playable_actions[i] for _, i, _ in chosen]
            self.assertTrue(any(a.action_type == AT.MARITIME_TRADE and a.value[-1] == 'ORE' for a in kinds))

    def test_no_progress_means_no_reserved_roots(self):
        g, c = post_roll(0, (0, 0, 0, 0, 0))
        ctx = M.EconomyContext(g, c)
        self.assertEqual(M.EconomyPolicy.reserve_enablers(g, ctx, rows(g, c)), [])


class EightPointCompletionTests(unittest.TestCase):
    def test_takes_two_road_longest_road_win_from_eight_points_both_seats(self):
        for seat in (0, 1):
            g, c = post_roll(seat, (2, 2, 0, 0, 0), vp=8, road=3)
            for _ in range(3):
                a = r.pick(M, g, c)
                self.assertIn(a.action_type, (AT.BUILD_ROAD, AT.MARITIME_TRADE))
                g.execute(a)
                if g.winning_color() is not None:
                    break
            self.assertEqual(g.winning_color(), c)

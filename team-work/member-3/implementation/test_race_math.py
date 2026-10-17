"""Draft unittest for the pure race_math module (senior sets PYTHONPATH to run)."""

import unittest
from itertools import product

from race_math import (
    can_afford,
    deficit,
    expected_stolen_value,
    hidden_vp_cap,
    steal_break_probability,
)

SETTLEMENT = (1, 1, 1, 1, 0)
ALT_COST = (0, 0, 0, 1, 2)
HAND = (3, 3, 3, 0, 0)


def brute_steal_break(hand, cost):
    """Independent oracle: enumerate every resource card in hand as a possible steal.

    Remove one card at a time, record whether affordability breaks, and return the
    average failure rate over all cards (0.0 for an empty or unaffordable hand,
    matching the documented contract of steal_break_probability).
    """
    total = sum(hand)
    if total == 0 or not all(h >= c for h,c in zip(hand,cost)):
        return 0.0
    failures = 0
    for i, count in enumerate(hand):
        reduced = list(hand)
        reduced[i] -= 1
        failures += count * (not all(h >= c for h,c in zip(reduced,cost)))  # one outcome per card
    return failures / total


class RaceMathTest(unittest.TestCase):
    def test_deficit_and_can_afford(self):
        self.assertEqual(deficit(HAND, SETTLEMENT), 1)
        self.assertFalse(can_afford(HAND, SETTLEMENT))
        full = (3, 3, 3, 1, 0)
        self.assertTrue(can_afford(full, SETTLEMENT))
        self.assertEqual(deficit(full, SETTLEMENT), 0)

    def test_hidden_vp_cap(self):
        self.assertEqual(hidden_vp_cap(9, 4, 5), 0)
        self.assertEqual(hidden_vp_cap(8, 4, 5), 1)
        self.assertEqual(hidden_vp_cap(5, 2, 5), 2)

    def test_steal_break_probability_matches_card_enumeration(self):
        for cost in (SETTLEMENT, ALT_COST):
            for hand in product(range(3), repeat=5):
                with self.subTest(hand=hand, cost=cost):
                    self.assertAlmostEqual(
                        steal_break_probability(hand, cost),
                        brute_steal_break(hand, cost),
                    )

    def test_expected_stolen_value(self):
        self.assertEqual(expected_stolen_value((1, 0, 0, 2, 0), (2, 0, 0, 5, 0)), 4.0)
        self.assertEqual(expected_stolen_value((0, 0, 0, 0, 0), (2, 0, 0, 5, 0)), 0.0)


if __name__ == "__main__":
    unittest.main()

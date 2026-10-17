#!/usr/bin/env python3
"""Verify the senior-authored derivation spec by direct arithmetic only.

Hand-worked derivation checks; this is NOT a game simulation or a bot.
No catanatron imports, no random sampling, no Game construction, no API
calls, no optimization or searches. Stdlib only: Fraction and comb.
Resource order throughout: WOOD, BRICK, SHEEP, WHEAT, ORE.
Prints only a deterministic JSON summary when run.
"""
from fractions import Fraction
from json import dumps
from math import comb

ORDER = ["WOOD", "BRICK", "SHEEP", "WHEAT", "ORE"]

checks = []


def record(name, steps, result, expected, caveats):
    assert result == expected, f"{name}: got {result!r}, expected {expected!r}"
    checks.append({"name": name, "steps": steps, "result": result,
                   "expected": expected, "caveats": caveats})


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


# 1) Regular 4:1 bank trade (brick -> wheat), then a city upgrade.
post_roll = (0, 4, 0, 1, 3)
post_trade = tuple(a - g + t for a, g, t in
                   zip(post_roll, (0, 4, 0, 0, 0), (0, 0, 0, 1, 0)))
final = sub(post_trade, (0, 0, 0, 2, 3))
record(
    "1_bank_trade_then_city",
    {"post_roll": post_roll, "trade": "regular 4:1 brick -> wheat",
     "post_trade": post_trade, "city_cost": (0, 0, 0, 2, 3), "final": final,
     "vp": "own public8 actual9 becomes public9 actual10 (city adds 1)"},
    (post_trade, final, 8 + 1, 9 + 1),
    ((0, 0, 0, 2, 3), (0, 0, 0, 0, 0), 9, 10),
    ["legal own settlement and city piece: explicit assumption, not a verified fixture",
     "no port required (regular 4:1 trade): explicit assumption, not a verified fixture",
     "bank supplies one wheat: explicit assumption, not a verified fixture"])

# 2) Road then settlement.
hand = (2, 2, 1, 1, 0)
after_road = sub(hand, (1, 1, 0, 0, 0))
after_settle = sub(after_road, (1, 1, 1, 1, 0))
record(
    "2_road_then_settlement",
    {"hand": hand, "road_cost": (1, 1, 0, 0, 0), "after_road": after_road,
     "settlement_cost": (1, 1, 1, 1, 0), "after_settlement": after_settle,
     "vp": "actual9 + 1 = 10 (settlement adds 1)"},
    (after_road, after_settle, 9 + 1),
    ((1, 1, 1, 1, 0), (0, 0, 0, 0, 0), 10),
    ["assumes the road opens a legal settlement spot",
     "assumes the road does not already award a bonus"])

# 3) Largest Army.
record(
    "3_largest_army",
    {"played_knights": "2 + 1 = 3",
     "unclaimed_army_vp": "own public8 + 2 = 10",
     "takeover_relative_shift":
         "adds 2 to us and subtracts 2 from other -> relative difference shifts 4"},
    (2 + 1, 8 + 2, 2 + 2), (3, 10, 4),
    ["tying an existing holder does not take the bonus: source fact, not a math proof"])

# 4) Seven-roll discard sizes.
record(
    "4_seven_discard",
    {"discard_9_cards": "9 // 2 = 4", "discard_10_cards": "10 // 2 = 5"},
    (9 // 2, 10 // 2), (4, 5),
    ["no simulated dice or claimed measured rates"])

# 5) Toy hidden-card urn (hypergeometric, exchangeable).
N, V, K = 10, 2, 2
den = comb(N, K)
hyper = [Fraction(comb(V, v) * comb(N - V, K - v), den) for v in range(K + 1)]
assert sum(hyper) == 1
p_ge1 = hyper[1] + hyper[2]
p_h1_given_le1 = hyper[1] / (hyper[0] + hyper[1])
record(
    "5_hidden_vp_urn",
    {"model": f"toy urn N={N} cards, V={V} remaining VP, k={K} opponent cards",
     "H0": hyper[0], "H1": hyper[1], "H2": hyper[2],
     "unconditioned_P_H_ge_1": p_ge1,
     "conditional_formula": "P(H1 | H<=1) = (16/45) / (44/45) = 16/44 = 4/11",
     "P_H1_given_H_le_1_ongoing": p_h1_given_le1},
    (hyper[0], hyper[1], hyper[2], p_ge1, p_h1_given_le1),
    (Fraction(28, 45), Fraction(16, 45), Fraction(1, 45),
     Fraction(17, 45), Fraction(16, 44)),
    ["condition: if opponent public VP is 8 and the real game is ongoing, H <= 1",
     "hypothetical exchangeable-card model, not empirical data or an exact "
     "opponent policy posterior"])


def to_jsonable(x):
    if isinstance(x, Fraction):
        return f"{x.numerator}/{x.denominator}"
    if isinstance(x, dict):
        return {k: to_jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [to_jsonable(i) for i in x]
    return x


assert all(v >= 0 for hand in (post_trade, final, after_road, after_settle) for v in hand)
report = {
    "label": "hand-worked derivation / no game execution",
    "resource_order": ORDER,
    "checks": checks,
    "all_assertions_passed": True,
}
print(dumps(to_jsonable(report), indent=2))

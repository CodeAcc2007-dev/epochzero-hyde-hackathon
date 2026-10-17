"""Pure route-planning math helpers. Stdlib only; no I/O or side effects.

All sequences (hand, cost, rates, ratios, bank) are length-5 and nonnegative.
"""

import math


def bank_convertible(hand, cost, ratios, bank):
    """Return True if `cost` is reachable from `hand` plus the ingredient `bank`.

    Cost ingredients already held are reserved first. Each deficit
    max(cost[i] - hand[i], 0) must fit within bank[i]. Remaining surplus
    units past the reserved cost convert to integer trade credits at
    max(hand[i] - cost[i], 0) // ratios[i]; fractional bundles are never
    spent and reserved ingredients are never consumed.
    """
    deficits = [max(c - h, 0) for h, c in zip(hand, cost)]
    if any(d > b for d, b in zip(deficits, bank)):
        return False
    credits = sum(max(h - c, 0) // r for h, c, r in zip(hand, cost, ratios))
    return credits >= sum(deficits)


def estimate_rolls(hand, cost, rates, ratios, bank, horizon=80.0):
    """Estimate the earliest t in [0, horizon] where projected inventory is convertible.

    At time t: collected[i] = min(bank[i], floor(max(rates[i], 0) * t + 1e-9));
    the projected hand is hand + collected and the remaining bank is
    bank - collected. This is a conservative capped mean-production projection,
    not a true expected completion time or probability. Returns 0.0 if
    initially convertible, math.inf if not convertible at the horizon,
    otherwise the smallest verified-feasible t after 18 bisection iterations.
    """

    def convertible_at(t):
        collected = [
            min(b, math.floor(max(r, 0.0) * t + 1e-9))
            for r, b in zip(rates, bank)
        ]
        projected_hand = [h + c for h, c in zip(hand, collected)]
        remaining_bank = [b - c for b, c in zip(bank, collected)]
        return bank_convertible(projected_hand, cost, ratios, remaining_bank)

    if convertible_at(0.0):
        return 0.0
    if not convertible_at(horizon):
        return math.inf
    lo, hi = 0.0, float(horizon)
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        if convertible_at(mid):
            hi = mid
        else:
            lo = mid
    return hi

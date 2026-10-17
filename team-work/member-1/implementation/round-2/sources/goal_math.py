"""Pure integer/heuristic math for goal trading decisions.

All sequence arguments (hand, cost, ratios, bank) are length-5
nonnegative integer sequences; ratio values are 2, 3 or 4.
No I/O, randomness, or classes; stdlib builtins only.
"""


def conversion_gap(hand, cost, ratios, bank):
    """Target cards still unavailable after optimal direct trades.

    Uses only surplus beyond reserved cost. Returns the integer
    max(blocked, sum(missing) - credits), where missing[i] is the
    shortfall per resource, blocked counts shortfalls the bank cannot
    cover, and credits are tradeable surplus units.
    """
    missing = [max(c - h, 0) for c, h in zip(cost, hand)]
    blocked = sum(max(m - b, 0) for m, b in zip(missing, bank))
    credits = sum(max(h - c, 0) // r for h, c, r in zip(hand, cost, ratios))
    return max(blocked, sum(missing) - credits)


def goal_priority(hand, cost, ratios, bank, reward):
    """Heuristic priority score for a goal with the given reward.

    Explicitly chosen heuristic, not a probability or learned
    coefficient: reward / (1 + conversion_gap + 0.35*sum(missing)
    + blocked).
    """
    missing = [max(c - h, 0) for c, h in zip(cost, hand)]
    blocked = sum(max(m - b, 0) for m, b in zip(missing, bank))
    return reward / (1.0 + conversion_gap(hand, cost, ratios, bank)
                     + 0.35 * sum(missing) + blocked)


def improves_goal(before, after, cost, ratios, bank_before, bank_after):
    """True only if total missing strictly decreases and gap does not rise.

    Requires sum(max(cost - after, 0)) < sum(max(cost - before, 0))
    and conversion_gap(after, ...) <= conversion_gap(before, ...).
    This forbids a trade consuming one missing ingredient just to
    replace it with another.
    """
    before_missing = sum(max(c - h, 0) for c, h in zip(cost, before))
    after_missing = sum(max(c - h, 0) for c, h in zip(cost, after))
    if after_missing >= before_missing:
        return False
    return conversion_gap(after, cost, ratios, bank_after) <= \
        conversion_gap(before, cost, ratios, bank_before)

"""Small pure helpers for Catan race math (resource order: WOOD, BRICK, SHEEP, WHEAT, ORE).

Stdlib-only, no I/O, no randomness. These are necessary bounds/checks for a real
nonterminal 10-VP game, not posteriors over hidden state.
"""

ResourceTuple = tuple  # length-5 int sequence in WOOD, BRICK, SHEEP, WHEAT, ORE order


def deficit(hand: ResourceTuple, cost: ResourceTuple) -> int:
    """Total missing cards: sum(max(cost[i] - hand[i], 0)) over paired slots.

    Returns an exact int (0 when the cost is already met).
    """
    return sum(max(c - h, 0) for h, c in zip(hand, cost))


def can_afford(hand: ResourceTuple, cost: ResourceTuple) -> bool:
    """True iff hand[i] >= cost[i] for every paired slot."""
    return all(h >= c for h, c in zip(hand, cost))


def steal_break_probability(hand: ResourceTuple, cost: ResourceTuple) -> float:
    """Probability that one uniformly random resource card, if stolen, makes `cost` unaffordable.

    Assumes the hand currently affords the cost; returns 0.0 if it does not, or if
    the hand is empty. Numerator counts cards of types where cost[i] > 0 and the
    hand holds exactly cost[i] of them (losing any one card of such a type breaks
    affordability). Does NOT certify a legal building location or a future win.
    """
    if not can_afford(hand, cost) or sum(hand) == 0:
        return 0.0
    total = sum(hand)
    fragile = sum(h for h, c in zip(hand, cost) if c > 0 and h == c)
    return fragile / total


def expected_stolen_value(hand: ResourceTuple, values: ResourceTuple) -> float:
    """Expected value of one uniformly random card from the hand: sum(hand[i]*values[i])/sum(hand).

    Returns 0.0 for an empty hand. Closed form; no random sampling.
    """
    total = sum(hand)
    if total == 0:
        return 0.0
    return sum(h * v for h, v in zip(hand, values)) / total


def hidden_vp_cap(public_vp: int, dev_count: int, unseen_vps: int) -> int:
    """Upper bound on an opponent's hidden victory points: max(0, min(dev_count, unseen_vps, 9 - public_vp)).

    A necessary bound for a real, nonterminal 10-VP game only (an opponent at or
    past 10 would have already won, hence the 9 - public_vp term); it is not a
    posterior estimate of hidden VP.
    """
    return max(0, min(dev_count, unseen_vps, 9 - public_vp))

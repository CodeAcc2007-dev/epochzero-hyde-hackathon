"""Pure helpers for round-2 math: maritime-trade completion and Knight-play wait bound.

Stdlib-only pure functions, no I/O, no imports; callers own precondition validation.
"""


def one_trade_build(hand, cost, ratios, bank):
    """Enumerate every distinct legal single maritime trade after which hand meets cost.

    Args:
        hand, cost, bank: length-five nonnegative integer sequences (resources 0..4);
            no argument is mutated.
        ratios: length-five give-ratios, each 2, 3 or 4; one trade gives ratios[i]
            copies of resource i to the bank for 1 copy of another resource j != i.

    Returns a tuple of (source_index, destination_index) pairs in numeric sorted
    order: exactly those i != j with hand[i] >= ratios[i] and bank[j] >= 1 such
    that, after applying the exact trade, every cost ingredient is covered
    (hand[k] >= cost[k] for all k). Nothing is reserved artificially. If the hand
    already meets cost, the result is still only the actual one-trade completions
    (trades of surplus included); the caller handles the already-affordable case.
    bank is only read: the give-side return to the bank cannot affect the
    hand-versus-cost check, so no bank copy is modeled.
    """
    completions = []
    for i in range(5):
        if hand[i] < ratios[i]:
            continue
        for j in range(5):
            if j == i or bank[j] < 1:
                continue
            traded = list(hand)
            traded[i] -= ratios[i]
            traded[j] += 1
            if all(t >= c for t, c in zip(traded, cost)):
                completions.append((i, j))
    return tuple(sorted(completions))


def knight_wait_rolls(plays_needed, held, old_eligible, played_this_turn):
    """Lower bound, in two-player roll units, until the last needed Knight is played.

    An own-turn wait is scored in units of two roll opportunities. This is
    a route-scoring conversion, not the exact number of rolls before a pre-roll
    Knight (which may play before our next roll). Assumptions:
      * plays_needed >= 0 Knights must still be played; held >= 0 Knights are
        already in hand. old_eligible means held Knights were bought on an
        earlier turn; played_this_turn means an action development card was
        already played this turn (blocking a Knight play now).
      * Optimistic acquisition: every Knight still needed is assumed buyable
        this current turn, so acquisition itself adds no wait; only the
        same-turn-play ban matters.
      * Hence a Knight can be played this turn only if one is already held
        (held > 0), it is old/eligible, and no action dev was played yet this
        turn. Exactly one Knight is played per own turn; each later play lands
        one own turn after the previous one.

    Returns 0 when plays_needed == 0; else 2 * (plays_needed - 1 + first_turn_wait)
    where first_turn_wait is 0 exactly when held > 0 and old_eligible and not
    played_this_turn, else 1. This scales an optimistic own-turn eligibility bound by two; it is not an
    expected completion time or a bound on actual elapsed dice rolls.
    """
    if plays_needed == 0:
        return 0
    first_turn_wait = 0 if (held > 0 and old_eligible and not played_this_turn) else 1
    return 2 * (plays_needed - 1 + first_turn_wait)

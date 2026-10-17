# Member 4 B07/B08: implementation decisions

The user's explicit request to build Member 4 bots authorizes primary implementation and verification for Anni, overriding the earlier human-only build boundary for these two bots. Research findings and all other members' frozen bots remain unchanged. No SSH, portal submission, environment copy, training or GitHub publication is part of this request.

## Deliverables and sequence

Build B08 adaptive VP-route planning and B07 sampled-opponent planning as distinct, self-contained `agent.py` files with version manifests. Reuse the established Member 3 public-state/expectation utilities with source hashes and attribution; preserve their frozen originals. Hyde drafts a small pure integer-conversion/time-estimation helper only; primary owns both policies, semantic tests, measured games and acceptance. No runtime provider calls.

## B08

Compare feasible city, settlement/short-path expansion, development, Army and Road plans using own actual VP gap, piece availability, current bank/port conversion, robber-adjusted production and incumbent bonus rules. Future resource collection is an approximate mean-production projection, not a hitting-time probability. Integer conversion reserves target ingredients and respects the currently observed bank. Unsupported plans are omitted. Road routes need a demonstrated short legal extension; no imaginary two-VP bonus. Replan per decision; no dynamic cross-game cache. Bounded same-turn continuation can complete enabling trades; dice, card draws and random steals are not executed as deterministic outcomes.

## B07

Start from a visible legal incumbent and fixed shortlist. Sample a capped number of worlds conditioned on the necessary real-nonterminal hidden-VP bound; reject impossible samples and fall back if not enough valid worlds fit the clock. Sampled cards are hypothetical, never real opponent truth. Complete a bounded own continuation, voluntarily end the turn in that forecast, then consider only bounded pre-roll dev replies. Stop before ROLL. Eligibility is justified only for the next opponent turn, when every currently held opposing card is old; never trust sampled owned-at-start flags for an interrupted current opponent turn. Compare only complete common-world root evaluations; incomplete refinement cannot overwrite the incumbent. A hidden-world conditional win is a bounded risk penalty, not a certain loss.

## Required verification

- Immediate own terminal build; known public opposing terminal; invalid sampled opponent already at ten; nine-public hidden-VP cap; old/new dev timing; no simulated ROLL or random BUY; exact Monopoly versus expected robber transfer; near-zero clock before sampling.
- B08 blocked expansion, unavailable pieces/bank, Army already owned, unattainable Road takeover, own hidden VP gap, conservative dev plans, integer trades and mean-projection limitations.
- Syntax/import, legal integer index and observation immutability fixtures; original clocked paired games against unchanged F. Controls isolate the sampled-reply and adaptive-route components. Fresh held-out board groups follow development smoke; keep all games and faults. Record code hashes, process lifecycle, hardware and limitations.

Acceptance targets zero faults and clock exhaustion. Strength must be measured; no promise these versions beat B05/B06 or private O. Preserve frozen tested versions and use a new version for later corrections.

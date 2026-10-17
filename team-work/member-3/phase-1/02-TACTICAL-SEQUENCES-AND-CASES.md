# Same-turn sequences and hand-worked tactical cases

**DERIVATIONS and illustrative cases, not played games or validated engine fixtures.** Source IDs refer to [the semantic audit](01-SOURCE-AND-SEMANTIC-AUDIT.md). A board condition explicitly assumed below has not been established by constructing a full state. Resource vectors use **(wood, brick, sheep, wheat, ore)**.

## Action sequences the next planning stage should distinguish

| Sequence | Required phase / conditions | Why one action may be insufficient | Uncertainty / boundary |
|---|---|---|---|
| Maritime trade → city/settlement | Post-roll; actual port rate; bank has requested card; legal purchase/piece | Trade loses resource quantity while completing an exact purchase | Two action transitions; no opponent turn between them; legal list regenerated after trade |
| Paid road → settlement | Post-roll; legal road creates legal node; both purchase costs available | First action yields no direct settlement VP | Two transitions; road may itself alter Road ownership; geometry must be validated |
| YOP → purchase | Eligible old YOP, no prior dev play; supported bank choice; post-roll | Values the obtained combination by its enabled purchase | Two transitions after roll; before roll a compulsory roll interrupts certainty |
| Monopoly → trade → purchase | Eligible old Monopoly, visible target count, conversion/purchase legal | Best stolen quantity can differ from best completed plan | Three transitions in this example; direct transfer is deterministic, future draw/roll is not |
| Road Building → road → road → settlement | Eligible card and free edges; post-roll for final settlement | Activation alone changes little; free-road subphase restricts next actions | Up to four transitions here; second road is compulsory if still legal; earlier terminal win stops the game |
| Knight → robber move → purchase/trade | Eligible old Knight; opportunity survives its effect | Knight and robber destination are separate actions | Steal is random unless victim type is determined. Army VP is updated before robber selection |
| Discard sequence → robber → normal play | A seven triggered a fixed discard quota | A one-card ranking can destroy the retained purchase combination | An opponent may be the roller; preserve conditional plans, not an imagined immediate own build |

These counts describe example action chains, **not chosen search depths/beam widths** or measured feasible runtimes. No opponent turn occurs inside an ordinary own-turn trade/build chain; uncertainty can still enter through a draw, steal or mandatory roll. A current discard request can belong to the opponent's turn.

## Case A — trade that completes a known terminal city

**Assumptions:** our ordinary post-roll turn; public VP 8, actual VP 9 (one known VP card); an upgradable own settlement and one city piece; no port; bank has wheat. A possible point composition is three cities plus two settlements (8 public), leaving one city piece. No dev play is required.

| Step | Resource hand | Our public / actual VP |
|---|---|---|
| Start | `(0,4,0,1,3)` | 8 / 9 |
| Trade four brick for one wheat | `(0,0,0,2,3)` | 8 / 9 |
| Upgrade the legal settlement | `(0,0,0,0,0)` | 9 / **10** |

S03/S13 establish the costs and phase. G's next loop check recognizes the actual-VP win. Losing three resource cards in the trade is not evidence of a bad move when it enables that terminal purchase. This is a constructed illustration of a decision dependency; it is **not proof that F chooses incorrectly**.

**Failure variants:** before rolling the maritime action is absent; without wheat in the bank it is absent; with four cities already deployed the city action is absent. The visible public value of the final position alone omits the held VP card.

## Case B — pre-roll Knight wins the race before robber placement

**Assumptions:** our pre-roll PLAY_TURN; public/actual VP 8/8; two played Knights; one eligible old Knight; no dev already played; Army unclaimed (opponent has at most two played Knights). A legal point composition is three cities and two settlements. Our resource hand is empty.

The opponent has public/actual 9/9, no unplayed devs, a legal city upgrade and one available city, with resources `(0,0,0,2,3)`. For example, three cities + one settlement + Longest Road can supply those nine public points. This is an affordable opposing winning continuation if we pass and they choose it, not an automatic forced move.

1. `PLAY_KNIGHT_CARD` is legal before rolling (S06).
2. Its played count becomes three; the unclaimed Army supplies two VP (S07).
3. Our public/actual becomes **10/10**.
4. `Game.play` detects the winner before asking for the robber follow-up or a roll (S01/S07).

The priority is taking our known win. A defensive argument about which opposing ore tile to block is unnecessary for this branch. F may already choose this action because Army also increases public VP; this case specifies semantics, not an improvement claim.

**Failure variants:** newly bought Knight without old eligibility; a dev already played this turn; or an opposing Army holder at three Knights. Our third Knight merely ties that holder and does not yield the bonus.

## Case C — paid road unlocks the tenth point

**Assumptions:** our post-roll turn, actual VP 9; resources `(2,2,1,1,0)`; a legal paid road opens a legal, distance-compliant settlement location; settlement piece available; this road does not itself change a VP bonus. Public VP 9 is feasible with three cities, one settlement and Army.

Pay road `(1,1,0,0,0)` → hand `(1,1,1,1,0)`. Pay settlement → zero hand and actual VP **10**. The assumed road endpoint must be beyond the prohibited adjacency around an existing settlement; not every road endpoint qualifies.

This establishes the combined cost and dependency only. It does not establish a particular map/node path or demonstrate a greedy failure. A later fixture must supply the exact geometry and legal-action indices.

## Case D — Road takeover and its four-point relative swing

**Assumptions:** normal road-extension path, not the cut edge case R1. Opponent holds Road at length six. Our length five → six only ties and leaves their bonus. A further legal extension to seven transfers it: **+2 to us and −2 to them**, a four-point change in the VP difference.

If our actual VP was eight before takeover, the +2 wins; otherwise a favorable gap change does not itself terminate. Resource/piece/geometry preconditions remain necessary. Two legal road actions may be needed from five, whereas the raw number of roads owned is not the relevant length.

Never promise this standard threshold/tie behavior for the separate settlement-cut path without later validation: R1 records why.

## Counterexamples that constrain a tactical policy

1. **Pre-roll progress is not a certain build sequence.** YOP/Monopoly may improve the hand, but ordinary trade/build must wait for a roll. A seven can discard the plan; a pre-roll Knight steal can increase a nine-card hand to ten, changing the discard quota from four to five. This does not make pre-roll devs universally bad: Case B ends the game before a roll.
2. **Holding more cards is not always better.** During a discard, retaining an exact city cost can be more useful than preserving the largest resource pile. However, if the opponent is the roller, their robber steal and our later roll still intervene. Do not label the retained purchase guaranteed.
3. **Visible production denial need not stop an immediate purchase.** If the opponent already holds the city cost, blocking ore production does not remove those ore cards. A steal can remove one card, but later rolls, ports or hidden progress cards may restore the opportunity. If we have a known own win, denying resources is not a substitute for taking it.
4. **A sampled hidden win is not an observed win.** At opponent public 9 in an ongoing real game, they cannot already hold a VP card. A masked world that assigns one is fictional (R2); do not “defend” against it as fact.

## Provisional decision specification for later planning

1. Identify the actual prompt/turn owner and current legal actions; avoid mixing pre-roll, free-road and discard phases.
2. Prioritize a **known own terminal continuation** when all required deterministic legality/resource steps are established. Evaluate our exact actual VP; do not infer a certain dev-card draw.
3. Compare short enabling chains with direct purchases, accounting for bank/pieces, dev-use limits and forced follow-ups. Reconsider after new observations instead of blindly replaying a cached plan.
4. Assess the opponent's available terminal continuations and bonus races separately from conditional hidden/roll threats. Block only when its cost and likely effect justify foregoing our own progress.
5. When no short tactical choice is decisive, retain an economic/positional alternative rather than forcing an attack or a long unprofiled search.

This is a **hypothesis-level priority scheme**, not code, a selected architecture or a universal proof of optimal action. The next document supplies candidate cards and refutable experiments.

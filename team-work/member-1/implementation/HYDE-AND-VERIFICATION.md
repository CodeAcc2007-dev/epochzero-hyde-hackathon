# Junior contribution and independent verification

Primary designed both policies, implemented purchase/retention/search logic and verified all outputs. The user explicitly authorized B01/B02 implementation. Earlier Member 1 bots and research remain unchanged.

## Accepted Hyde helper

- Existing OpenCode runner, pinned `hyde-inference/hyde/glm-5.3-flash`. Job `20261017T092811Z-4fd5fb95`.
- Bounded task: pure conversion gap, heuristic goal priority and strict goal-improvement predicate. Only the contract was supplied, no environment/repository/credentials.
- Process exited normally in 53.972 seconds, no tool errors. Actual `goal_math.py` output 2,092 bytes, SHA-256 `46a3e1e47cc8000fabff463f00b6595cff1bbd7f9484993641e92869dd80b89e`.
- Primary reviewed the formulas and accepted the unchanged file after independent exhaustive reachable-trade oracle checks over 18,225 two-resource cases (embedded in length-five vectors). The oracle minimizes remaining target shortages over legal trade sequences; it is separate from the helper formula. Every case passed. Raw provider logs remain outside Git.

## Semantic evidence

19 test methods passed before freezing. Cases include complete ingredient reservation, nine-card/wheat shortage, last-wood trade rejection, bank depletion, owned versus merely present port, goal-relative discard, impossible city/settlement plans, expansion under ore denial, old/new Knight timing, strict Army takeover, owned Army, unused-dev stock cap, one-card remaining deck uncertainty, free-road phases, known city/trade/Army wins, distinct goal selection, legal standalone outputs, observation immutability and no simulated dice/draw/steal.

These are explicit engine/counterfactual fixtures, not all complete reached game histories. One escape fixture initially required a settlement, but inspection showed a legal road awarded two VP versus the settlement's one. The assertion was corrected to accept constructive point gain and the fixture was extended with an ore robber block. This was a test expectation correction; the policy was not changed to hide it.

The helper coefficients and strategy thresholds are declared design choices, not fitted data or probabilities. Actual match evidence is recorded separately, with 500 games per bot as the main default.

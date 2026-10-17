# Resource economics and testable alternatives

17 October 2026. Facts/derivations below are distinct from candidate hypotheses. No bots, fitting or new match outcomes.

## Primary evidence and applicability

- **Exact engine:** [resource production helpers](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/features.py#L209-L265), [maritime options](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/models/actions.py#L300-L365), [F value](https://github.com/bcollazo/catanatron/blob/d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816/catanatron/catanatron/players/value.py). Own/opposing resource hands, bank, build costs and current geometry support goal-aware valuation. They do not identify future dice, opposing dev identities or assured resource availability.
- **Guhe–Lascarides**, [paper](https://www.pure.ed.ac.uk/ws/portalfiles/portal/19351482/CIG2014_GS.pdf), PDF pp. 3–6: estimated build/win time and competing build plans. Its development-card experiments show preference depends on the parent evaluator/opponent, rather than a universal dev-card advantage. Four-player/trading results are not 1v1 evidence.
- **Gan et al.**, [report](https://eric-gan.github.io/files/catan.pdf), all three pages: production-based hitting-time approximation, ports and replanning after an opponent occupies a target. Their simplified future path and thresholds are assumptions, not reusable engine constants. No reported Staffbot result is an F/O score.
- **Numerical study:** [our reproduction](01-DATA-AND-STATISTICS.md) supports limited associations; it does not rank two-player policies. The strongest resource hypothesis follows exact costs and conversion constraints, not a fitted Kaggle win predictor.

## Concrete economic reasoning

Let `h_r` be current resource cards, `c_r` a legal goal's cost, and `lambda_r` expected unblocked production per roll under the current board. Deficit is `max(c_r−h_r,0)`. A direct-production fluid proxy is `max_r(deficit_r/lambda_r)`, with a positive deficit/zero rate marked unreachable **in that direct-only model**. This is an approximate decision feature, not the true expected stochastic hitting time or a guarantee. Bank trades can make a missing resource reachable; finite bank supply, same-roll correlations, robber movement, discards and opponent actions can invalidate it. Count roll events versus own turns explicitly: both players' rolls can produce cards.

Trade-aware estimates should allocate surplus only after reserving the intended purchase's ingredients. Conversion happens in integer bundles at the actual owned 4:1/3:1/2:1 rate, with target bank supply checked. Do not value one surplus wood as half a wheat merely because a wood port exists somewhere on the map.

For a city upgrade, the cost buys **one additional VP and one additional production unit per adjacent active tile**, not two new VP or a wholly new settlement. A dev purchase has chance outcomes: only some cards score immediately, others need eligible later plays/locations. Largest Army and Longest Road have incumbent/strict-transfer conditions. Expected random VP is not a guaranteed near-term point.

When few VP remain, a guaranteed legal winning purchase can dominate a production improvement. Earlier, investment can pay across many rolls. Above seven resources, spending/conversion can reduce discard exposure, but dumping useful cards just to get below seven may destroy a stronger goal. The value of retention is marginal to a specific plan, not raw hand size.

## Hand-worked cases and counterexamples

All cases are illustrative arithmetic; legality, phase, bank, location and remaining pieces are assumptions until future engine fixtures.

1. **Quantity versus affordability.** Hand `(wood,brick,sheep,wheat,ore)=(3,3,3,0,0)` has nine cards but cannot buy a settlement directly; with no port it also lacks a four-card maritime bundle. Hand `(1,1,1,1,0)` buys one immediately. Higher hand count does not identify the better immediate build. A high-pip board missing wheat can still obtain it through later conversion; never claim it is permanently stuck.
2. **Protect the goal's ingredients.** Hand `(4,1,1,0,0)`, bank wheat available, owned wood port: 2 wood→1 wheat leaves `(2,1,1,1,0)`; a settlement is then affordable. At 4:1 the same trade leaves no wood, so it does **not** complete that settlement. Both conversions reduce the wheat deficit; only one completes the whole bundle.
3. **Port acquisition can lose the race.** A 2:1 wood port saves two wood per imported card relative to 4:1, once owned. If reaching it first costs two roads plus a settlement, the material outlay is 3 wood+3 brick+1 sheep+1 wheat. Port savings alone must compensate that delay/opportunity cost; a low-production coastal location or an opponent reaching 10 first can make it poor. The new settlement also scores/produces, so subtracting its whole cost from port savings is not a full valuation either.
4. **Mean production hides burst risk.** Suppose a legal board offers two output units on the same 6 versus one on 6 and one on 8. Both yield `10/36` cards per roll. First has second moment `20/36`; second `10/36`, before subtracting the same squared mean. The first is more bursty. Geometry, resource mix and robber exposure still matter; different numbers alone do not ensure better strategy.

## Three hypothesis cards

| ID / candidate | Observable trigger and decision | Failure / counterexample | Future control and rejection |
|---|---|---|---|
| **M1-H1 → B01: bottleneck economy** | At each purchase/retention/trade/discard decision, rank viable goals by integer deficits, actual conversion, current rates and pieces; value finishing balanced ingredients over surplus count | Static mean rates neglect stochastic arrivals, contested sites and terminal timing; case 3 can invalidate conversion plans | Compare unchanged F and the same evaluator without goal-deficit/retention features. Reject if it hoards endlessly, trades in circles, misses known wins or adds no held-out benefit |
| **M1-H2 → B02: city/dev engine** | When sustainable wheat/ore/sheep and legal upgrades exist, prioritize productive city investment and timed dev/Army opportunities; keep alternate expansion available | Missing ore/wheat, depleted bank/deck, blocked production or an opponent's fast expansion can punish concentration; development draws are random | Compare with B01; ablate city weighting and dev/Army preference independently. Reject unconditional dev buying or worse weak-matchup/clock behavior |
| **M1-H3 → B04 input: port conversion** | Exploit an owned port when surplus bundles accelerate a concrete build; acquire a port only when the whole route is justified | Distance/cost, low coastal production and discards can exceed savings; case 3 | Avadooth owns the spatial candidate. Compare the same policy with port acquisition preference disabled; do not claim his research was completed here |

Coefficients, horizons, thresholds and runtime are unmeasured. No claim that these maximize win probability. Prefer B01 as a transparent control and B02 as a deliberately distinct economic route; keep both until comparisons resolve their tradeoffs.

## Handoffs and review

- **Avadooth:** provide legal route costs, port access, setup order and contested-node consequences. His research remains untouched and pending; B03/B04 specifications are provisional pending his inspection.
- **Pranesh:** goal retention must yield to a known own terminal move; compare targeted theft/Monopoly with lost own investment. Use exact dev timing and strict bonus thresholds from his audit.
- **Anni:** use game groups for uncertainty, keep post-game totals out of opening inputs, and reject incompatible text labels for immediate training. The primary assistant cross-checked these requirements against Anni's audit; that is not a human teammate review.

Open: actual CPU cost, exact-rules outcomes, legal reachable fixtures, port/spatial assumptions and teammate feedback. Later members build/test their own two candidates; the assistant reviews frozen uploads and returns improvements under the [iteration protocol](../../member-4/phase-1/03-ITERATION-AND-TEST-PROTOCOL.md).

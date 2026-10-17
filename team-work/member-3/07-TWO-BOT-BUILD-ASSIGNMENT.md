# Pranesh: build and self-test B05 / B06

17 October 2026. **Human implementation assignment; no bot created by this research task.** Build two separate candidates. Suggested order: **B06 first; then bounded B05**. They are hypotheses, not promised winning bots.

Read the [shared eight-bot plan](../../07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md) and [owner/assistant iteration protocol](../member-4/phase-1/03-ITERATION-AND-TEST-PROTOCOL.md). Reuse your existing supplied environment through `../run-python.sh` from this member directory; set the documented local overrides on a different machine. Do not clone/copy an environment into either bot.

## B05 — Same-turn completion planner

**Hypothesis:** short legal enabling sequences beat an otherwise identical one-step evaluator. Inputs: current prompt/acting player, legal list, own exact cards/actual VP, known dev eligibility, bank, pieces and geometry from an allowed sampled copy.

Minimum version: establish a cheap incumbent action, shortlist enabling trades/builds/dev plays and search only a bounded same-turn tree. Deduplicate equivalent states and avoid conversion cycles. Stop at turn boundary, terminal state, a different player or a chance branch not explicitly modeled. Return only the index of the first action in the current original list; recompute after the next real observation. Never treat one lucky random execute/draw as certain. Choose width/depth/copy limits by profiling, not by copying a paper's defaults.

**Required cases:** trade→city; road→settlement; YOP→build with finite bank; Road Building's mandatory second road when legal; pre-roll old Knight winning Army; purchased VP adding actual VP immediately; pre-roll builds prohibited; newly bought action dev ineligible; discard one card per decision. Test the supplied masker artifact separately from real terminal semantics.

**Comparison:** same evaluator without beam/chains, then F and B06 under the same clock. Reject a layer whose enabling successes are erased by exhaustion or whose apparent wins depend on fictional sampled terminal states.

## B06 — Opponent threats and bonus races

**Hypothesis:** exact enemy resource visibility, conditional dev threats and bounded bonus/denial decisions improve a fast policy without hidden-world reply search. Inputs: own exact VP, enemy public VP/resources/dev count, played cards, visible geometry/bonus incumbents and legal own actions.

Minimum version: always recognize known own wins first; distinguish enemy currently affordable goals from future-roll speculation; score robber choices by self-cost, productive denial and actual steal probabilities; use exact Monopoly transfers. Respect strict Army/Road ties and the +2/−2 transfer swing. Include the opportunity cost of defense and refuse endless losing road races. No deep sampling needed for this initial version.

**Required cases:** enemy nine public VP with an affordable legal city; eight public VP with unknown hidden VP; nine public implies no current hidden VP in a real continuing game; resource-type steal probability; self-blocking robber; Army tie versus takeover; Road tie versus takeover; terminal own move versus unnecessary denial. Road-interruption fixtures remain unverified work, not an assumed textbook rule.

**Comparison:** same economy/position policy with threat/bonus layer disabled; then B05, F and varied peer styles. Reject excessive blocking that loses an available win or does not improve weak-matchup outcomes.

## Read first

Your [findings](04-PHASE-1-FINDINGS.md), [cases](phase-1/02-TACTICAL-SEQUENCES-AND-CASES.md) and [threat/hypothesis report](phase-1/03-THREATS-VP-RACES-AND-HYPOTHESES.md). Existing arithmetic checks are not runnable engine fixtures. You, Pranesh, build/self-test/upload these bots; assistant verification follows your uploads.

## Delivery and independent verification

1. Keep each bot under your member folder with a stable ID and version, e.g. `bots/Bxx/v001/agent.py`, and a manifest/report. No skeletons exist yet. Freeze source/config hashes and the Git commit before comparing.
2. Self-test imports/load, genuine legal integer indices, phase transitions, dependency/packaging limits and cheap fallback. Run small clocked smoke/profile tests first, then paired F/own-peer comparisons using documented disjoint board groups. Keep all faults and no-winner losses. Semantic cases above need actual assertions/evidence; prose is not a pass.
3. Upload your own code and results to your GitHub branch/folder. Include exact commands, interpreter/hardware, kit/engine pins, opponents, seeds/seats/order, per-game records, own CPU/fallback/fault counters, known failures and the next question. No secrets, environment, raw datasets or provider logs. Follow the full protocol's record schema and sample-size caveats.
4. The assistant will review that frozen upload, independently test it and compare across members when the uploaded round is supplied in this chat. It will give evidence-linked improvement instructions for each bot. You implement fixes, self-test and upload a new version; keep the frozen parent and repeat. No automatic portal upload or external messaging is implied.

Target zero faults/exhausted clocks. The clock is cumulative, so a three-second call timeout is not an available search budget. Untouched F is the common anchor; O is unavailable locally. Start nonadaptive across games, record RNG/cache lifecycle and preserve ordered batches. Do not claim final strength from smoke games or a small screen.

Use Hyde/OpenCode for bounded repetitive development work only if configured locally; inspect its actual outputs and verify them. Do not rely on its stated test results. Current research jobs timed out and were rejected; logs contain no accepted code. All design/review evidence belongs in Markdown alongside actual results.

First upload status: **pending human build/test**. Assistant retest status: **not started**. Improvement round: **not started**.

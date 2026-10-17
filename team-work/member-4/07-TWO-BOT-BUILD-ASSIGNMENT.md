# Anni: build and self-test B07 / B08

17 October 2026. **Human implementation assignment; no bot created by this research task.** Build two separate candidates. Suggested order: **B08 first; B07 is higher risk**. They are hypotheses, not promised winning bots.

Read the [shared eight-bot plan](../../07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md) and [owner/assistant iteration protocol](../member-4/phase-1/03-ITERATION-AND-TEST-PROTOCOL.md). Reuse your existing supplied environment through `../run-python.sh` from this member directory; set the documented local overrides on a different machine. Do not clone/copy an environment into either bot.

## B07 — Sampled-opponent planning

**Hypothesis:** a small amount of hidden-dev-aware opponent reply analysis helps where visible threats alone are insufficient. Inputs: current legal actions, public hands/board/VP, own known devs, opposing dev count, public played-card history and unseen multiset.

Minimum version: start with a fast legal incumbent and shortlist. Compare those roots under common sampled worlds; model only explicitly allowed short replies and stop before unexpanded dice/chance. For a real continuing 10-VP state, enforce the necessary opposing hidden-VP bound, without claiming it is a complete calibrated posterior. Dev-card ages/eligibility need history-sensitive treatment; sampled owned-at-start flags are not observed truth. Cap sampling/rejection and branch work; if consistent worlds or CPU cannot be justified, return the visible-policy incumbent. Never read hidden fields as the real opponent's hand or predict dice from board seeds.

**Required cases:** sampled opponent already at10 despite real game continuing; nine-public-VP hidden bound; opponent old/new Knight eligibility uncertain; evaluation unchanged by extra worlds; random robber draw versus exact Monopoly; a reply after an unmodeled roll; low CPU fallback. A single stochastic successor is a sample, not an expectation.

**Comparison:** B06 plus a matched visible-only control, then F. Hold root evaluator/shortlist fixed to isolate uncertainty/reply value. Reject invalid beliefs, mostly unchanged rankings with higher cost, poor reproducibility or clock exhaustion. This is the most exploratory initial candidate; repair or simplify before large games.

## B08 — Adaptive VP-route planner

**Hypothesis:** a cheap state-dependent plan among expansion, city, dev/Army and Road routes beats a fixed preference. It differs from B01's immediate ingredient objective and B02's concentrated investment by explicitly comparing routes toward the remaining VP gap.

Minimum version: estimate material deficits, legal route costs, production changes and bonus incumbent conditions for a small menu of feasible plans; choose progress that reduces approximate remaining completion cost, then replan each observation. Use actual VP for own distance to10, guarded dev probabilities and integer bank conversion. A city is net+1 VP; a bonus cannot be counted before its condition. Avoid committing to an occupied target or switching plans indefinitely without progress.

**Required cases:** high production early versus immediate terminal build late; blocked spatial target; unavailable pieces/bank; Army already owned; expensive unattainable Road takeover; dev random score overstated; low mean resource time but concentrated robber/burst risk.

**Comparison:** B01/B02 and a fixed-plan version of the same evaluator. Reject if improved average score does not translate into robust wins, estimated plans are invalid or the added computation outweighs simpler rules.

## Read first

Your [findings](04-PHASE-1-FINDINGS.md), [dataset verdicts](phase-1/01-DATASET-AUDIT.md), [method comparison](phase-1/02-METHODS-AND-SOURCES.md) and [iteration protocol](phase-1/03-ITERATION-AND-TEST-PROTOCOL.md). Neither initial bot requires external corpus labels or training. You build your two bots, rather than becoming the sole tester for everyone else.

## Delivery and independent verification

1. Keep each bot under your member folder with a stable ID and version, e.g. `bots/Bxx/v001/agent.py`, and a manifest/report. No skeletons exist yet. Freeze source/config hashes and the Git commit before comparing.
2. Self-test imports/load, genuine legal integer indices, phase transitions, dependency/packaging limits and cheap fallback. Run small clocked smoke/profile tests first, then paired F/own-peer comparisons using documented disjoint board groups. Keep all faults and no-winner losses. Semantic cases above need actual assertions/evidence; prose is not a pass.
3. Upload your own code and results to your GitHub branch/folder. Include exact commands, interpreter/hardware, kit/engine pins, opponents, seeds/seats/order, per-game records, own CPU/fallback/fault counters, known failures and the next question. No secrets, environment, raw datasets or provider logs. Follow the full protocol's record schema and sample-size caveats.
4. The assistant will review that frozen upload, independently test it and compare across members when the uploaded round is supplied in this chat. It will give evidence-linked improvement instructions for each bot. You implement fixes, self-test and upload a new version; keep the frozen parent and repeat. No automatic portal upload or external messaging is implied.

Target zero faults/exhausted clocks. The clock is cumulative, so a three-second call timeout is not an available search budget. Untouched F is the common anchor; O is unavailable locally. Start nonadaptive across games, record RNG/cache lifecycle and preserve ordered batches. Do not claim final strength from smoke games or a small screen.

Use Hyde/OpenCode for bounded repetitive development work only if configured locally; inspect its actual outputs and verify them. Do not rely on its stated test results. Current research jobs timed out and were rejected; logs contain no accepted code. All design/review evidence belongs in Markdown alongside actual results.

First upload status: **pending human build/test**. Assistant retest status: **not started**. Improvement round: **not started**.

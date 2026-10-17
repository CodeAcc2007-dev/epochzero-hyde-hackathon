# Avadooth: build and self-test B03 / B04

17 October 2026. **Human implementation assignment; no bot created by this research task.** Build two separate candidates. Suggested order: **B03 first**. They are hypotheses, not promised winning bots.

Read the [shared eight-bot plan](../../07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md) and [owner/assistant iteration protocol](../member-4/phase-1/03-ITERATION-AND-TEST-PROTOCOL.md). Reuse your existing supplied environment through `../run-python.sh` from this member directory; set the documented local overrides on a different machine. Do not clone/copy an environment into either bot.

## Research boundary

Your existing Phase 1 research/context/findings were deliberately left untouched. The following are build assignments requested by the user, **not a claim that your opening/port research is finished**. Correct these provisional spatial assumptions with your own evidence before treating them as verified rules.

## B03 — Frontier expansion and space denial

**Hypothesis:** good opening combinations and timely occupation of valuable legal sites can outpace concentrated city investment. Inputs: public map/production, current setup/build prompt, actual board connections, distance-rule exclusions, both players' buildings/roads, resource costs and pieces.

Minimum version: evaluate complementary opening production/ingredients and accessible future settlement opportunities; respect the actual legal setup order instead of assuming a four-player snake order. Rank expansion targets by value minus legal road/material delay and opponent contest risk. A road is valuable for an attainable site or justified bonus, not for its count alone. Replan when the opponent occupies a target. Consider denial as opportunity cost, not guaranteed victory.

**Required cases:** high pips with missing ingredients; tempting site excluded by distance rule; route obstructed by opposing settlement/edge; two targets where the farther one arrives too late; zero valuable targets where city progress is better; no settlement/road pieces left. Compute usable graph paths, not copied Manhattan coordinates from another simulator.

**Comparison:** untouched F and same evaluator without future-site/contestation preference. Then B04. Reject expensive roads with no useful reachable settlement, invalid path assumptions or a strategy that loses despite superior total pips.

## B04 — Port specialization

**Hypothesis:** a justified matching port plus concentrated surplus production can outperform the broad spatial policy. It must deliberately use a distinct conversion/route objective from B03.

Minimum version: use actual owned per-resource 4:1/3:1/2:1 rates, bank supply and integer surplus bundles while retaining the intended purchase ingredients. Price a port's entire legal path and the new settlement's production/VP before acquiring it. A nearby port is not owned; a port alone does not produce its resource. Replan if surplus source is blocked or the route is occupied.

**Required cases:** matching 2:1 port with low versus high production; expensive coast detour; depleted target bank resource; 4:1 trade consuming a necessary ingredient; general port plus specific port uses best legal rate; opponent reaches 10 before savings repay the detour.

**Comparison:** B03 and the same policy with port-acquisition preference disabled (owned-port legality still applies). Reject if gains come from a different general evaluator rather than the port hypothesis, or path/holding costs erase conversion benefits.

## Read first

Your [original brief](03-PHASE-1-RESEARCH-BRIEF.md), Aroosh's [economics](../member-1/phase-1/02-ECONOMY-AND-HYPOTHESES.md), and Pranesh's [semantic audit](../member-3/phase-1/01-SOURCE-AND-SEMANTIC-AUDIT.md). Road-cut behavior is a source-level risk; do not rely on an unverified bonus exploit. No research conclusion is attributed to you here.

## Delivery and independent verification

1. Keep each bot under your member folder with a stable ID and version, e.g. `bots/Bxx/v001/agent.py`, and a manifest/report. No skeletons exist yet. Freeze source/config hashes and the Git commit before comparing.
2. Self-test imports/load, genuine legal integer indices, phase transitions, dependency/packaging limits and cheap fallback. Run small clocked smoke/profile tests first, then paired F/own-peer comparisons using documented disjoint board groups. Keep all faults and no-winner losses. Semantic cases above need actual assertions/evidence; prose is not a pass.
3. Upload your own code and results to your GitHub branch/folder. Include exact commands, interpreter/hardware, kit/engine pins, opponents, seeds/seats/order, per-game records, own CPU/fallback/fault counters, known failures and the next question. No secrets, environment, raw datasets or provider logs. Follow the full protocol's record schema and sample-size caveats.
4. The assistant will review that frozen upload, independently test it and compare across members when the uploaded round is supplied in this chat. It will give evidence-linked improvement instructions for each bot. You implement fixes, self-test and upload a new version; keep the frozen parent and repeat. No automatic portal upload or external messaging is implied.

Target zero faults/exhausted clocks. The clock is cumulative, so a three-second call timeout is not an available search budget. Untouched F is the common anchor; O is unavailable locally. Start nonadaptive across games, record RNG/cache lifecycle and preserve ordered batches. Do not claim final strength from smoke games or a small screen.

Use Hyde/OpenCode for bounded repetitive development work only if configured locally; inspect its actual outputs and verify them. Do not rely on its stated test results. Current research jobs timed out and were rejected; logs contain no accepted code. All design/review evidence belongs in Markdown alongside actual results.

First upload status: **pending human build/test**. Assistant retest status: **not started**. Improvement round: **not started**.

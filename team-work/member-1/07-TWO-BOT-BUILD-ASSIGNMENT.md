# Aroosh: build and self-test B01 / B02

17 October 2026. **Human implementation assignment; no bot created by this research task.** Build two separate candidates. Suggested order: **B01 first**. They are hypotheses, not promised winning bots.

Read the [shared eight-bot plan](../../07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md) and [owner/assistant iteration protocol](../member-4/phase-1/03-ITERATION-AND-TEST-PROTOCOL.md). Reuse your existing supplied environment through `../run-python.sh` from this member directory; set the documented local overrides on a different machine. Do not clone/copy an environment into either bot.

## B01 — Bottleneck economy

**Hypothesis:** complete purchase ingredients and useful conversion outperform raw production/hand totals. Inputs: current legal actions/phase, own exact cards/VP, bank, owned port rates, active production, legal building sites and remaining pieces.

Minimum version: compare feasible settlement/city/dev goals; reserve their ingredients; select legal trades that complete or efficiently approach a viable goal; discard the least useful card relative to the retained goal one legal step at a time. Penalize unconvertible surplus and discard exposure without spending resources merely to reduce hand count. Use a cheap position evaluator for unrelated prompts. Recompute after every observation; no circular trade plan.

**Required cases:** nine abundant cards but no wheat/four-card trade bundle; a trade that gains wheat but consumes the last wood needed for a settlement; depleted bank; no legal settlement location; owned 2:1 versus merely nearby port. Cases from the economics report are hypotheses until actually checked in engine fixtures.

**Comparison:** untouched F, then same bot without bottleneck/retention features. Keep production/position policy constant in the ablation. Reject missed guaranteed wins, trading loops or no benefit under equal-clock reserved comparisons.

## B02 — City/dev engine

**Hypothesis:** sustained wheat/ore/sheep and productive upgrades/dev timing can beat broad expansion. This must make different investment choices from B01, rather than rename its weights.

Minimum version: evaluate legal city upgrade production and net +1 VP; value buying development cards probabilistically, including Army potential only with explicit timing/incumbent conditions. Preserve a legal expansion escape route when concentrated production is blocked or unavailable. Do not classify a random dev draw as a guaranteed Knight/VP, buy endlessly, or delay a known legal winning build for investment.

**Required cases:** old versus newly purchased Knight, city piece unavailable, ore shortage, blocked ore tile, concentrated hand/discard exposure, nearly empty dev deck, already-held Army and strict takeover, endgame where a city wins now. Honor free-road/discard subphases through supplied legal actions.

**Comparison:** B01 and untouched F; ablate city preference and dev preference separately. Reject if development spending sacrifices stronger immediate progress or produces fragile matchups without compensating gains.

## Read first

[Findings](04-PHASE-1-FINDINGS.md), [CSV audit](phase-1/01-DATA-AND-STATISTICS.md), [economic cards/counterexamples](phase-1/02-ECONOMY-AND-HYPOTHESES.md). The four-player data is not a policy-training table. No regression or external-text imitation is needed for either initial bot.

## Delivery and independent verification

1. Keep each bot under your member folder with a stable ID and version, e.g. `bots/Bxx/v001/agent.py`, and a manifest/report. No skeletons exist yet. Freeze source/config hashes and the Git commit before comparing.
2. Self-test imports/load, genuine legal integer indices, phase transitions, dependency/packaging limits and cheap fallback. Run small clocked smoke/profile tests first, then paired F/own-peer comparisons using documented disjoint board groups. Keep all faults and no-winner losses. Semantic cases above need actual assertions/evidence; prose is not a pass.
3. Upload your own code and results to your GitHub branch/folder. Include exact commands, interpreter/hardware, kit/engine pins, opponents, seeds/seats/order, per-game records, own CPU/fallback/fault counters, known failures and the next question. No secrets, environment, raw datasets or provider logs. Follow the full protocol's record schema and sample-size caveats.
4. The assistant will review that frozen upload, independently test it and compare across members when the uploaded round is supplied in this chat. It will give evidence-linked improvement instructions for each bot. You implement fixes, self-test and upload a new version; keep the frozen parent and repeat. No automatic portal upload or external messaging is implied.

Target zero faults/exhausted clocks. The clock is cumulative, so a three-second call timeout is not an available search budget. Untouched F is the common anchor; O is unavailable locally. Start nonadaptive across games, record RNG/cache lifecycle and preserve ordered batches. Do not claim final strength from smoke games or a small screen.

Use Hyde/OpenCode for bounded repetitive development work only if configured locally; inspect its actual outputs and verify them. Do not rely on its stated test results. Current research jobs timed out and were rejected; logs contain no accepted code. All design/review evidence belongs in Markdown alongside actual results.

First upload status: **pending human build/test**. Assistant retest status: **not started**. Improvement round: **not started**.

## Subsequent implementation update — 17 October 2026

The user subsequently explicitly requested primary-assistant implementation of B01/B02. That authorization supersedes the original human-only build status above for these two initial candidates. Both frozen standalone v001 files are now built and locally verified: [B01](bots/B01/v001/agent.py), [B02](bots/B02/v001/agent.py).

Each completed the user's current default of 500 paired-seat games against unchanged F: B01 381/500 (76.2%), B02 359/500 (71.8%). Both recorded zero errors, timeouts, crashes, clock overruns and harness random moves. Nineteen semantic verification methods and package checks passed; Hyde supplied a bounded helper that the primary independently reviewed and verified. Read the [complete report](implementation/BUILD-AND-RESULTS.md) for records, provenance, decisions and limitations.

The earlier seven bots and research remain unchanged. Human review and GitHub upload are pending. Direct clashes, component ablations, private scoring and the next improvement round have not been run. Preserve v001; revisions require a new version and fresh confirmation boards.

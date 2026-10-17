# B01 upgrade handoff — exact 78% baseline

User-authorized publication 17 October 2026. Owner Aroosh, Member 1. The primary timed B01 improvement sprint is complete; read its final report before starting another revision. Independent work must use a separate branch and version directory; never overwrite their candidate or merge automatically.

## Completed primary sprint

Recommended candidate: [B01 v004](bots/B01/v004/agent.py). [Final report](implementation/final-sprint/RESULTS.md), [ready-to-paste prompts](implementation/final-sprint/TEAMMATE-PROMPTS.md). Fresh F result 390/500 versus matched v002 388/500; direct result 251–249. These small differences do not establish a strength gain. v004 repairs a demonstrated trade→two-roads win missed by v002/v003, with 43 package correctness methods and zero recorded match faults. The original 78% v002 below remains preserved. New work should start from the report's recommended version unless continuing an already documented independent v002 branch.

## Verified baseline

- [B01 v002 standalone agent.py](bots/B01/v002/agent.py), [manifest](bots/B01/v002/manifest.json), [ZIP](artifacts/B01-v002.zip).
- Source SHA256 `cc53c58ca1867678ad6be9ca074ed6dabdffb54aa9b1c7ca1d83f52271c723f4`.
- [Saved 500-game records](../member-3/evaluations/common-F-20261017/results/B01-v002-vs-F-500/games.json), [summary](../member-3/evaluations/common-F-20261017/results/B01-v002-vs-F-500/summary.json), [metadata](../member-3/evaluations/common-F-20261017/results/B01-v002-vs-F-500/metadata.json).
- **390/500 = 78.0% vs unchanged F**, mean own CPU 211.94ms/game, max 770ms. Zero recorded errors, timeouts, crashes, clock overruns and harness random moves. Boards 934000–934249, swapped seats, both processes reset every 20 games.
- A different completed 500-game batch on 935000–935249 scored 371/500 = 74.2% with exactly the same source. Board variation matters: 78% is an observed result, not a guaranteed win probability or event ranking. B05 v004's 375/500 on 934000 is the next highest point estimate among the compared candidates; no direct head-to-head claim.

## Assignment

Read root AGENTS.md, setup notes, `team-work/member-1/08-GLM-IMPROVEMENT-CONTEXT.md` and this brief. Use the standalone v002 as the authoritative baseline; older review tickets describe v001 defects already fixed in v002. The component hashes in the manifest are provenance, not sibling runtime requirements.

Create branch `member-1/b01-independent-upgrade` and choose an unused directory such as `bots/B01/teammate-v003/`. Do not overwrite v001, v002, primary sprint v003/v004 or another person's working tree. Record the plan before editing. Reuse the one shared local environment with `./team-work/run-python.sh`; no SSH or environment upload. If on another machine, follow the existing setup document once.

Prioritize useful economic/tactical changes rather than blanket increases to search: goal choice after a completed purchase or changed bank/port; preservation of necessary trade/road enablers; short guaranteed win sequences; opening resource bottlenecks; resource production versus immediate VP. Existing v002 already has a terminal selector before low-clock fallback and a bounded winning trade→Road certificate. Do not claim those as new contributions. The primary sprint evaluated dynamic purchase goals, opening weights and bounded deeper search, then added a certified two-road winning sequence. Read the final report and avoid claiming its existing repairs as new contributions; independent approaches should be separately measured.

Preserve all original action indices, input immutability, resource/bank/port/piece rules, new-card eligibility, one dev per turn, strict Road/Army takeover and engine simultaneous-winner semantics. Never inspect actual hidden opponent identities, sampled future deck order, future dice or seed lookup. No runtime models, network, files or worker processes. Keep the original game clock min(.300+.0125*decisions,1.500) seconds and a bounded emergency legal fallback.

Use small development experiments, then freeze before 500-game main confirmation against unchanged F. Reserve **942000–942249** for this independent B01 branch, and compare v002 on the same boards/lifecycle if time permits. The primary sprint used 938000/939000, 940000 for a package smoke check, and 943000/944000; B05's teammate uses 941000. Do not tune on confirmation outcomes or claim a same-board improvement from old 78% evidence. No automatic extra tournaments. Preserve rejected experiments and incomplete results honestly.

Deliver exact standalone agent.py, ZIP containing only agent.py, hashes, regression evidence, per-game outcomes, CPU/fault counts, commands, board ranges and limitations in Markdown. Test the exact packaged file. If no gain is supported, recommend the baseline. Push only your branch and scoped evidence, provide the commit and links, and stop before event submission or merging anyone else's work. Never upload keys, .env, dependencies, datasets or local provider logs.

F SHA256: `72df6e45f9a37370f661cbfc4e626d67af6fb3c5907523e27ba0a29567d8f613`; kit 04fffac90e00610f60e0b06d919f262f4b3ed9db; engine d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816. Use `team-work/member-3/implementation/run_comparison.py`, 500 games, `--seed0 942000`, chunk-size 20 and a new output folder. Do not modify F or the harness clock.

If the user instead asks you simply to package/submit the baseline, do not silently run an upgrade: provide the exact frozen file and await their explicit event-submission instruction.

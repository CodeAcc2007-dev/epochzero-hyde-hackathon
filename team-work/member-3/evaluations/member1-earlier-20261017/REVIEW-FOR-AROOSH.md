# Review for Aroosh: earlier uploaded bots

This is feedback on frozen earlier versions, not implementation or a new task allocation. Final measurements and limitations are in [RESULTS.md](RESULTS.md). Keep the source hashes in `source-inventory.json`; do not replace these files in place.

## What is worth retaining

- **Greedy v3 as a cheap F-level control.** It scored 201/400 (50.25%) at about 132 ms/game under default weights and `OPP=0`. Its paired descriptive range is 47.75–52.75%. It is useful for checking whether later complexity is helping; this does not establish a tournament advantage.
- **Greedy v4 as an unconfirmed search candidate.** It scored 208/400 (52%), descriptive range 47.25–56.5%, at about 496 ms/game. The 1.75 percentage-point observed gain over v3 costs about 3.77 times as much CPU. Do not select it as superior on these numbers alone. A later ablation should isolate relative scoring from the expensive follow-up/reply stage.
- **SAB as another F-level search baseline.** It scored exactly 200/400 at about 171 ms/game. Inspect the root-cost fallback and whether depth-two work actually completes, rather than assuming the name/comment guarantees an effective opponent search.

## Versions needing stronger evidence before further selection

`agent.py` (40.5%), `agent_claude.py` (35.5%) and `agent_modifiedf.py` (29.75%) were well below F on this set. Greedy v2 scored 46.75%; that is not evidence it beats F. Preserve these as regression/ablation references; do not assume more tree search or a feature vector makes a stronger policy.

A loss does not identify its cause. For later revisions, inspect reached decision traces and measure root coverage, completed refinement work, caught exceptions, terminal-win choices and sampled chance effects. The current evaluation does not prove that any one source-level caveat caused these win rates.

## Before the next improvement round

1. Add observable counters to a new diagnostic version for swallowed exceptions and static fallbacks; zero official errors cannot see these internal paths. The separate four-game diagnostic in this evaluation is only a small check.
2. Compare one controlled change at a time against the frozen anchor under the same process lifecycle and clock. Do not reuse these evaluated boards as fresh confirmation after tuning.
3. Run direct cross-bot matches on new boards when deciding the eight-bot portfolio. F-relative win rates alone cannot predict which candidate beats another. Include diverse opponent styles when they become available.
4. Keep a new version folder, entrypoint/source hashes, per-game records and exact configuration for each revision. No code fixes, optional-parameter sweep or bot implementation was performed here.

All earlier source files remain unchanged; this feedback does not mark Aroosh's B01/B02 implementations complete or assign an earlier filename to either bot ID.

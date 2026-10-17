# Evidence index: v001/v002 result provenance (ticket M2-E01)

17 October 2026. This document corrects the provenance issues the 2026-10-17 independent
review found in the uploaded v002 result files (`team-work/reviews/2026-10-17-B03-B08/08-GLM-IMPROVEMENT-CONTEXT.md`,
ticket M2-E01). It does not edit or overwrite any historical result file or manifest --
every file listed below is unchanged and original. This is a new index, not a changed
historical artifact.

## What the review found, verified against the files directly

Recomputed per-file record counts and source hashes (commands and output kept in this
session's build log, not re-run here since the files are frozen):

| File | Records | `a` source hash (12 hex) | `b` source hash (12 hex) | Status |
|---|---:|---|---|---|
| `results/dev-b03v2-vs-f-01.json` | 16 | `1a4a30493271` (B03 v002, current) | `72df6e45f9a3` (F) | current |
| `results/dev-b04v2-vs-f-01.json` | 16 | `be9b3a53befc` (**old B04 hash, superseded before v002's final calibration**) | `72df6e45f9a3` (F) | **superseded** |
| `results/dev-b03v2-vs-b04v2-01.json` | 16 | `1a4a30493271` (B03 v002, current) | `be9b3a53befc` (**old B04 hash**) | **superseded** |
| `results/screen-b03v2-vs-f-01.json` | 80 | `1a4a30493271` | `72df6e45f9a3` | current, mis-scaled contest bonus (first cut) |
| `results/screen-b03v2-vs-f-02.json` | 80 | `1a4a30493271` | `72df6e45f9a3` | current, **identical 40-board group to `-01`** -- see dedup below |
| `results/screen-b04v2-vs-f-01.json` | 80 | `763c88df0a81` | `72df6e45f9a3` | current, mis-scaled port bonus (first cut) |
| `results/screen-b04v2-vs-f-02.json` | 80 | `763c88df0a81` | `72df6e45f9a3` | current, **identical 40-board group to `-01`** -- see dedup below |
| `results/screen-b03v2-vs-b04v2-01.json` | 40 | `1a4a30493271` | `763c88df0a81` | current |

Total across the five `*v2*`/`screen-b0[34]v2*` files: **360 records**, not the 240 the
build report's headline table implied by only quoting the final consolidated run. The
report's "final consolidated screen" table (`REPORT.md`, "Final consolidated screen run"
paragraph) is the 240 games from `screen-b03v2-vs-f-01.json` (80) + `screen-b04v2-vs-f-01.json`
(80) + `screen-b03v2-vs-b04v2-01.json` (40) + the two single-batch recalibration reruns
counted separately. The report narrates the **mis-scaled intermediate result** (B03 21/80,
B04 28/80, both recomputed from `-01` files before the bonus was rescaled) as history, not
as a separately hashed, independently reproduced artifact: those numbers are **not**
preserved in their own file -- `screen-b03v2-vs-f-01.json` and `screen-b04v2-vs-f-02.json`
both carry the *current* (final, rescaled) source hashes `1a4a30493271`/`763c88df0a81`,
because the agent files were edited in place between the two calibration passes and
re-running the same batch ID overwrote the file with the post-fix result. **Treat the
"mis-scaled" numbers quoted in REPORT.md as narrative, not as independently reproduced
evidence** -- they came from this session's own interim console output, not from a
separately preserved, separately hashed result file.

## Deduplicated board-group identities

- `screen-b03v2-vs-f-01.json` and `screen-b03v2-vs-f-02.json` play the **same 40 boards**
  (seeds 771100-771139 for `-01` per `run_batches_v002.py`; `-02` was run via an inline
  script using the identical seed list `[771100+i for i in range(40)]` to confirm the
  recalibrated bonus). They are **not two independent 80-game samples**; treat them as one
  80-game observation measured twice (different CPU timings, same winners/turn counts),
  consistent with the review's finding.
- The same applies to `screen-b04v2-vs-f-01.json` and `screen-b04v2-vs-f-02.json`
  (seeds 771200-771239).
- **Deduplicated total for v002's screen-tier evidence: 120 independent games**
  (80 B03-vs-F + 40 B03-vs-B04), not 360, and not 240.

## Old-hash smoke files

`results/dev-b04v2-vs-f-01.json` and the B04 side of `results/dev-b03v2-vs-b04v2-01.json`
used source hash `be9b3a53befc`, an earlier in-session edit of B04 v002 that predates the
hash recorded in B04 v002's manifest (`763c88df0a81...`) and in the final committed file.
These two 16-game smoke files are **loading/fault evidence for an intermediate, uncommitted
edit**, not for the frozen B04 v002 that was pushed to GitHub. Do not cite their win counts
as B04 v002 evidence.

## Frozen commit identity (replacing "pending" placeholders)

`bots/B03/v002/manifest.json` and `bots/B04/v002/manifest.json` both say
`"frozen_git_commit": "pending next commit in this session"` because they were written
before the commit that included them. That commit is now resolved:
**`791e6705d09f62ceba691777e041980d673f1c69`**, branch `member-2/avadooth-bots`, and its
`agent.py` hashes match the v002 manifests exactly (verified again at the start of this
v003 round -- see `implementation/test_b03_b04_v003.py::ParentHashTests`). Per the review's
own guidance, the historical manifest text is left as originally written and not edited;
this index is the resolvable pointer instead.

## What to use going forward

- For v002 as reviewed: cite the review's own fresh, independently-run, non-duplicated
  500-game evaluation (`team-work/reviews/2026-10-17-B03-B08/main/B03-v002-vs-F-500/` and
  `.../B04-v002-vs-F-500/`, boards 932000-932249), not the in-session v002 screen files
  above.
- For v003: see `implementation/BUILD-AND-RESULTS.md` and
  `implementation/results/B0{3,4}-v00{3,2}-vs-F-dev-500*/`, boards 933000-933249 (B03) and
  933500-933749 (B04) -- disjoint from the review's 932000-932249 and from every other
  member's recorded board range (checked by grep across `team-work/*/implementation/results/*/metadata.json`
  before use). 934000-934249 remains reserved, unused, for a later confirmation round.

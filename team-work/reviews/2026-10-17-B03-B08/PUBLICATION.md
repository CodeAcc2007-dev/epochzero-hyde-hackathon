# Review publication — 17 October 2026

The user requested locating and publishing the separate review and upgrades. The separate task **Review bots and write GLM guidance** produced this review directory and each member's `08-GLM-IMPROVEMENT-CONTEXT.md`. Its completed scope is verified findings and proposed repairs; no next-version bot fixes were implemented. This publication preserves that distinction.

## Published context

- The [review](README.md), [implementation contract](IMPLEMENTATION-CONTRACT.md), all four owner handoffs, original compact ZIP packet, source/result audit, counterexamples and evaluation records.
- Local frozen parent implementations needed by the review: Member 1 B01/B02 v001 and Member 4 B07/B08 v001, with standalone ZIPs, manifests, development sources and verification/results reports. Member 3 B05/B06 v003 were already on main; their direct-file handoff and earlier Member 1 evaluation context are included now.
- The seven original earlier Member 1 bots referenced by the preservation/review evidence, unchanged. They are separate historical candidates.
- Member 2 B03/B04 v002 remain at existing branch `member-2/avadooth-bots`, commit `791e6705d09f62ceba691777e041980d673f1c69`. That branch was fetched and inspected, not merged. Its shared runner changes were not applied. The pinned snapshot utility retrieves the required files using Git objects and the existing local environment.

The original review's statements that nothing had been committed or pushed describe its completion time. This subsequent publication is explicitly authorized. Original reports, result records and the ZIP packet remain unchanged, including their historical local-only status descriptions.

## Publication checks

Before publication, rerun the existing Member 1/3/4 semantic suites and the review's frozen-defect counterexamples. Check recorded source/script hashes, result counts, Python syntax and ZIP integrity; scan the complete staged file contents (including ZIP members) for credential signatures and literal local credential values. Verify staged paths exclude local environments, downloaded research, dataset-row previews, credentials and provider logs. These are publication checks; no new game batch or strength claim is added.

**Checks completed:** 60 semantic methods passed (19 + 26 + 15); all nine finding groups reproduced exactly against the saved evidence. All eight parent hashes and review-script hashes matched. The staged-tree scan covered 418 files, including seven ZIP archives and their contents; 83 Python sources compiled and 307 JSON documents parsed (archive members included in these counts). Credential/exclusion checks passed. The 278-file publication includes prior unpublished builds and their supporting records. Two original trailing blank lines in frozen component copies were preserved to retain their recorded hashes; the remaining whitespace check passed. No new games were run.

Commit on main and push to `https://github.com/CodeAcc2007-dev/epochzero-hyde-hackathon.git` using HTTPS, then compare the remote main commit with local HEAD. No SSH, event submission, environment upload or Member 2 branch merge.

Human review of the proposed fixes, implementation of new versions, matched parent comparisons and private event scoring remain pending. The per-bot main-evaluation default remains 500 games.

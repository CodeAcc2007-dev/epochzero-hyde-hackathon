# Research completion, decisions and verification record

17 October 2026. Scope: complete assistant research for Aroosh/Anni, retain and cross-check Pranesh's completed work, exclude Avadooth's research, prepare eight human-owned build assignments and publish to the existing public team repository. User subsequently clarified the loop: **members build/test/upload two bots each → assistant verifies/tests/compares → owners receive improvements → members revise/upload → repeat**. No bot implementation, training, fixture execution or new match was authorized for this research deliverable or performed here.

## Accepted artifacts and findings

- [Aroosh's handoff](member-1/04-PHASE-1-FINDINGS.md): full CSV audit and selected numerical reproductions, field/timing/leakage table, economic hypotheses and four hand-worked cases. Primary-authored auditor/output under his `phase-1/` folder.
- [Pranesh's earlier handoff](member-3/04-PHASE-1-FINDINGS.md): source/math findings and source-level risks retained. Human review and Avadooth's cross-review remain pending; arithmetic/source evidence is not a game result.
- [Anni's handoff](member-4/04-PHASE-1-FINDINGS.md): both full Parquet tables decoded, audit/quality/compatibility decisions, method/paper comparison and a detailed owner/assistant iteration protocol.
- [Eight strategy assignments](../07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md), two per human, with individual specifications. Only a **new build assignment** is added under Avadooth; every pre-existing file in his folder is preserved byte for byte.
- [Synthesis](PHASE-1-REVIEW-AND-SYNTHESIS.md) distinguishes assistant checks from pending human reviews and proposes no external-corpus training dependency for initial bots.

## Environment and source checks

1. Reused existing Python 3.11/game environment and organizer checkout. Reader discovery checked game Python, system Python and bundled document Python: none had a usable Parquet engine.
2. Installed only `pyarrow==20.0.0`, no dependencies, into ignored `shared-local/research-reader-deps` using the existing uv tool with `--target`. Actual installation succeeded; it is a research reader, not a bot dependency. A later check confirmed pyarrow is still absent from the normal game environment.
3. All original download-manifest files still match their recorded SHA-256. CSV and both corpora retain the original catalogue hashes; no raw inputs were edited or published.
4. Organizer checkout remains clean at `04fffac90e00610f60e0b06d919f262f4b3ed9db`. Upstream HEAD was `efaa27e7aef628994313bf4080deb4e191491d1e` during the HTTPS check. Fetched only for Git comparison, without checkout. Only README clone/path text changed; `PROBLEM_STATEMENT.md`, requirements and harness are identical. No SSH.
5. Newly cited installed `features.py` and `models/map.py` were byte-compared against pinned engine GitHub contents. Both match; [additional source evidence](member-4/phase-1/additional-source-verification.json). Pranesh's earlier [11-file comparison](member-3/phase-1/source-verification.json) remains available. No new upstream engine was installed.
6. Relevant PDFs were text-extracted locally with Poppler for focused review; Guhe PDF p. 6 was also rendered and visually checked to verify development-card table/figure direction. Raw papers/text/render remain local. Primary web checks revisited the dataset pages, numerical article, paper/publisher method records and pinned organizer statement. Hoeffding's publisher record was located; full text returned an access error, so no new full-paper review is claimed.

## Actual computation and independent review

Commands are recorded in [CSV audit](member-1/phase-1/01-DATA-AND-STATISTICS.md) and [corpus audit](member-4/phase-1/01-DATASET-AUDIT.md). They construct no Catan games and import no agent/engine code.

- CSV output: 200 records /50 groups; seat wins 8,18,14,10; roll mean64.28/sampleSD12.740807; all derived-total identities pass; two unresolved B tokens. Complete-case descriptors use198 rows/49 winners. Primary separately checked winners, repeated dice histograms, mean/SD, tokens, descriptor denominators and contributor flags; checks passed.
- Corpus output: 1,000 and2,668 decoded rows; no top-level/message-field nulls. Role totals, rule markers, seed groups, model/color association, prompt duplicates and aggregate action checks reconciled. D2 has226 textual mismatches among49,996 tag/list pairs, without a claim of engine illegality. D3 has2,620 unique prompts, ten candidate seed groups and perfect model/color confounding. Primary independent aggregate assertions passed.
- Input-manifest hash assertions passed; newly authored Python parses successfully. No statistical model fitted, no labels converted and no original regression replicated by substitution.
- Eight specifications were checked against exact phase/hidden-information/CPU limits and own research cases. These are design checks, not fixture or performance passes. Search parameters, throughput, memory/CPU profiles and win rates remain unmeasured.

## Hyde junior jobs — failures retained honestly

Both used the configured `hyde-inference/hyde/glm-5.3-flash` via the existing bounded OpenCode runner, with five steps and240-second timeout. No GitHub PAT, whole repository, environment or unrelated teammate material was sent. Junior permissions denied shell/network/external directories/subagents; it could not apply/commit/push.

| Job | Selected work | Actual outcome / acceptance |
|---|---|---|
| `20261017T070453Z-2bd15604` | CSV audit script from a precise positional/parser specification; no raw CSV input | Timed out after240.165s, exit130, no output, recorded session error. **Rejected; no code accepted.** |
| `20261017T070453Z-4e6e8c9f` | Mechanical extraction of numbered harness source packet | Timed out after240.170s, exit130, no output, recorded session error. **Rejected; no text accepted.** Packet SHA-256 `e431e932843745ba2aa0956ae057be9d85bb77ddb8fa421c2d27b2c0b3a265b8`. |

No retries or provider switch. Primary completed the analysis/scripts and source checks directly. There is no claimed junior-produced accepted artifact or invented token saving. Raw jobs/events/reasoning/manifests remain outside Git in the configured local job store.

## Decisions and unresolved work

Chosen: B01/B02 Aroosh, B03/B04 Avadooth, B05/B06 Pranesh, B07/B08 Anni; simple initial controls; no incompatible corpus imitation; frozen uploads and independent assistant feedback; budgeted, paired comparisons with all faults preserved. Anni and Pranesh each remain human builders of their two bots. Team names indicate ownership, not who authored these assistant reports.

Unresolved: Avadooth's excluded findings, all named human review responses, B03/B04 spatial assumptions, source-risk reachable fixtures, sampled dev-age/history consistency, training rights/provenance, measured candidate performance and available event upload slots. None is silently reported complete. The user-authorized build plan exists; the actual builds and subsequent game review await uploaded artifacts.

## Publication and audit boundaries

GitHub publication is authorized for these documents, aggregate results and research scripts. Environments, isolated reader, source packets, raw logs, raw datasets, previews, downloaded papers and credentials remain ignored. Publication does not mean event submission, accepted teammate review or bot completion. A final index scan excludes known credential values/signatures and forbidden paths; the push helper compares remote commit/tree and path list with the local commit. See [machine-readable task checks](PHASE-1-TASK-VERIFICATION.json); local authenticated publication metadata records the actual pushed SHA outside Git.

No collaborator invitation, external message, portal action, background monitor or SSH operation was performed. Later owner uploads supplied in this chat activate the already-authorized assistant verification/feedback cycle; no bot exists to test in this task.

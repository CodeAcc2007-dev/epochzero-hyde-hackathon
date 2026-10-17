# Working agreement for this Catan workspace

The user is **Pranesh, Member 3**. Current teammate mapping: Member 1 Aroosh; Member 2 Avadooth; Member 3 Pranesh; Member 4 Anni.

## Delegate routine work to Hyde; retain senior review

The user explicitly requests **OpenCode with Hyde GLM-5.3 Flash as a junior engineer** for suitable repetitive and low-level work. Use that existing provider for bounded extraction, checklist/table formatting, boilerplate code, routine refactoring or test drafting when the current phase authorizes the task. The primary assistant owns architecture, strategy reasoning, task scope, evidence checks, testing, final decisions and reports to the user.

Use `team-work/run-hyde-junior.py` to provide selected input copies and a small task. It pins `hyde-inference/hyde/glm-5.3-flash`, creates a separate local job directory and leaves proposed outputs unreviewed. See `team-work/JUNIOR-ENGINEER-WORKFLOW.md`. Do not send the entire repository, credentials, `.env`, installed environments or other teammates' unrelated files. Do not switch to another provider/model silently.

Review the junior's actual files against the original inputs. Independently verify factual claims and run checks appropriate to any code change. A normal process exit is not acceptance, and a model's statement that a check passed is not test evidence. Copy only accepted changes into the appropriate member folder; no automatic application, Git commit or push by the junior. Keep task IDs, evidence and review decisions in Markdown. If Hyde fails, record the error and avoid an endless retry loop; continue independent work and report any blocked delegated task accurately.

## Existing project boundaries

- Reuse `shared-local/` through the existing launcher; do not clone or duplicate the environment.
- Keep secrets, local job/session logs, dependencies, downloaded datasets/papers and dataset-row previews out of Git. The repository is currently public at the user's explicit request.
- No SSH, event portal actions or runtime LLM calls inside competition bots. Hyde is a development assistant only.
- Phase 1 research remains governed by the existing briefs; setup/checklist work does not authorize bot implementation, training, new simulations or tournament execution.
- Work in Pranesh's member folder unless the task explicitly concerns shared tooling/context. Do not modify another member's research findings.
- Use the exact organizer kit/engine and honest evidence labels. Do not invent hidden information, performance claims, reproduced results or datasets.

## Current eight-bot owner workflow

The user assigns two bots to each human member: Aroosh B01/B02; Avadooth B03/B04; Pranesh B05/B06; Anni B07/B08. Members implement, self-test and upload their own versioned code/results. When the uploaded versions are supplied in this chat, the assistant independently inspects/retests the frozen versions, runs cross-bot comparisons and writes evidence-linked owner-specific improvement instructions; members revise/upload and repeat. Research/build-assignment creation alone does not authorize taking over those human implementation tasks. A later explicit user request can change this scope. See `07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md` and the iteration protocol.

The latest research request explicitly excluded Avadooth's research. Do not mark it complete or rewrite his findings; the new two-bot assignment in his folder is separately authorized. Human reviews remain pending even where assistant checks are complete.

## Subsequent Member3 implementation authorization

Pranesh explicitly requested primary-assistant implementation and F testing of B05/B06, with Hyde for bounded repetitive coding and primary verification. Active versions are `team-work/member-3/bots/B05/v003` and `B06/v003`; read their manifests and `implementation/BUILD-AND-RESULTS.md` before changing them. v001/v002 are superseded internal development evidence. Preserve frozen tested versions; later fixes need a new version/evidence. Other members can use `team-work/GLM-START-PROMPT.md` to retrieve their own assignments; this does not authorize modifying their research/bots here. No SSH or event submission.

## Subsequent Member4 authorization and evaluation default

The user explicitly requested primary implementation of Anni's B07/B08. This authorizes building and verifying these two bots in member-4, using Hyde for bounded development work and the shared local environment. Preserve research findings and other members' frozen versions.

The user's latest preference is **500 games per bot for the main evaluation from now on**. Keep correctness/loading checks small. For the current B07/B08 build, use 500 paired-seat games each against F and defer extra tournament/ablation comparisons; do not present deferred comparisons as completed. No SSH or portal submission.

Initial frozen Member4 versions are `team-work/member-4/bots/B07/v001` and `B08/v001`; read `team-work/member-4/implementation/BUILD-AND-RESULTS.md` before revisions. Their standalone files and ZIPs were verified; each completed 500 F games. Preserve v001 and use a new version with fresh confirmation boards for fixes.

## Subsequent Member1 authorization

The user explicitly requested primary implementation of Aroosh's B01/B02 as well. This authorizes implementation and local verification under member-1, with the same 500-game-per-bot main-evaluation default and bounded Hyde development assistance. Preserve `member-1/earlier bots/`, research findings and all other frozen versions. No SSH, portal submission or automatic GitHub upload.

Initial frozen Member1 versions are `team-work/member-1/bots/B01/v001` and `B02/v001`; read `team-work/member-1/implementation/BUILD-AND-RESULTS.md` before revisions. Their standalone files and ZIPs were verified; each completed 500 F games. Preserve v001 and use a new version with fresh confirmation boards for fixes.

## Subsequent Member3/Member4 improvement round

The user explicitly requested carrying out the published improvement prompts for both Member 3 and Member 4. New review candidates are B05/B06 v004 and B07/B08 v002; original parents remain frozen. Round-specific sources, decisions, tests and results live in each member's `implementation/round-2/`. Read their `PLAN-AND-DECISIONS.md` and final `BUILD-AND-RESULTS.md` before follow-up work. The fixed plan is 500 games per candidate and 500 per matched parent, using identical boards and lifecycle. No extra tournament or automatic publication; show results for user verification before publishing. Preserve all earlier evidence and the other members' work.

This local round is complete: all four new candidates and their parents completed 500 F games each, with zero recorded faults/clock overruns. Standalone files/ZIPs and 54 regression/contract methods were verified. Win-rate improvement remains unestablished; B08's whole-revision mean CPU decreased. Human verification and publication remain pending. Boards 934000–934249 are now used evidence, not fresh confirmation for later versions. Do not modify or include separately created Member1 round-2 work as part of this handoff.

## Full-context publication authorization (17 October 2026)

The user explicitly requested uploading all remaining context regardless of team ownership. This supersedes earlier publication-pending/no-automatic-upload boundaries for the existing context in this publication only. All members' existing local plans, reports, frozen artifacts and saved evaluation evidence may be published, while environments, credentials, downloaded datasets/papers, row previews and raw provider/session logs remain excluded. No bot logic edits, new simulations, branch merge or event submission are part of this request. See `ALL-CONTEXT.md` for the authoritative navigation and current B01 v004 recommendation. Older per-round local-only statements are historical; pending human verification remains pending.

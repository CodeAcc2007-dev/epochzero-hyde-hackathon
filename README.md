# Catan hackathon: shared research and strategy workspace

Team context for the Hyde two-player Catan hackathon. The repository was made **public at the user's request**. It contains our plans, research instructions, source catalogue, provenance metadata and four teammate workspaces. **Assistant research is documented for Aroosh, Pranesh and Anni; human review remains pending. Avadooth's research is excluded and untouched.** Frozen implementations and evidence are available for Aroosh's B01/B02, Pranesh's B05/B06 and Anni's B07/B08; Avadooth's B03/B04 are reviewed from his pinned branch. The [independent review](team-work/reviews/2026-10-17-B03-B08/README.md) links all owners' proposed improvement handoffs and exact validation status.

**Latest full-team handoff: [ALL-CONTEXT.md](ALL-CONTEXT.md).** Includes all published upgrade rounds and evaluation context; current recommended submission is B01 v004. Older publication-status statements are historical.

## Start here

1. [Problem, exact rules and engine findings](01-PROBLEM-AND-ENVIRONMENT-ANALYSIS.md).
2. [Local setup and validation record](02-LOCAL-SETUP-AND-VALIDATION.md).
3. [Research papers, numerical studies and dataset catalogue](03-RESEARCH-AND-DATASET-CATALOGUE.md).
4. [Phase-wise plan and repeated bot tournaments](04-PHASE-WISE-PLAN.md).
5. [Team workspace entry point](team-work/README.md) and [Phase 1 common brief](team-work/PHASE-1-COMMON-BRIEF.md).
6. [OpenCode–Hyde setup and verification](06-OPENCODE-HYDE-SETUP.md) and [junior-engineer workflow](team-work/JUNIOR-ENGINEER-WORKFLOW.md). Pranesh is Member 3; routine work goes to GLM-5.3 Flash with primary-assistant review.

7. [Eight strategies, two bots per member and the improvement cycle](07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md). Start here for the current build assignments.

8. [GLM startup prompt](team-work/GLM-START-PROMPT.md): teammates supply the repository and their name to retrieve context and build only their assigned bots.

9. [Independent eight-bot review and owner improvement handoffs](team-work/reviews/2026-10-17-B03-B08/README.md). The review reproduces nine finding groups and provides a direct GLM context file for each member. These are proposed upgrades; repairs have not been implemented by the review. Aroosh's [B01/B02](team-work/member-1/README.md) and Anni's [B07/B08](team-work/member-4/README.md) frozen files and results are now included alongside Pranesh's B05/B06. Avadooth's B03/B04 remain on the pinned `member-2/avadooth-bots` branch. See the [publication record](team-work/reviews/2026-10-17-B03-B08/PUBLICATION.md) for the sharing scope and checks.

The numbered reports preserve what was known/done at each stage. Earlier statements such as “setup deferred” describe that historical stage; the later setup report records its completion.

## Your Phase 1 assignment

| Teammate | Research focus | Detailed instructions | Findings worksheet |
|---|---|---|---|
| Member 1 (Aroosh) | Numerical study, statistical evidence and resource economics | [Brief](team-work/member-1/03-PHASE-1-RESEARCH-BRIEF.md) | [Findings](team-work/member-1/04-PHASE-1-FINDINGS.md) |
| Member 2 (Avadooth) | Opening placement, expansion and ports | [Brief](team-work/member-2/03-PHASE-1-RESEARCH-BRIEF.md) | [Findings](team-work/member-2/04-PHASE-1-FINDINGS.md) |
| Member 3 (Pranesh) | Tactical sequences, opponent threats and VP races | [Brief](team-work/member-3/03-PHASE-1-RESEARCH-BRIEF.md) | [Findings](team-work/member-3/04-PHASE-1-FINDINGS.md) |
| Member 4 (Anni) | Search/learning, text-data suitability and tournament design | [Brief](team-work/member-4/03-PHASE-1-RESEARCH-BRIEF.md) | [Findings](team-work/member-4/04-PHASE-1-FINDINGS.md) |

Each folder has common context, member-specific context, detailed instructions and a findings worksheet. Record source-backed findings, assumptions, alternative strategies and counterexamples in Markdown. Use the [research record template](team-work/PHASE-1-RESEARCH-TEMPLATE.md); bring completed reports to the [review and synthesis worksheet](team-work/PHASE-1-REVIEW-AND-SYNTHESIS.md). The [new build plan](07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md) now assigns two bots per human member. Each member builds, self-tests and uploads; the assistant independently verifies, compares and returns improvements; repeat. No bots were implemented by the research task.

Pranesh's [Member 3 findings and review pack](team-work/member-3/04-PHASE-1-FINDINGS.md) include source citations, tactical cases, hidden-VP/bonus risks, hypotheses and arithmetic checks. This is a shared research draft. User verification and Avadooth cross-review remain pending; this research publication did not implement bots. The subsequent eight-bot plan assigns implementation to the human members.

The intended later workflow is **multiple strategy bots → eligibility checks → clashes against each other and F → select/improve/create variants → repeat → eight validated local finalists**. Current organizer rules allow **7 scored submissions and 10 uploads total**. Eight local finalists are a portfolio; they are not eight guaranteed scored uploads.

## Dataset and paper access

Raw datasets, papers and dataset-row previews are **not in Git**. Use the following sources and the [full catalogue](03-RESEARCH-AND-DATASET-CATALOGUE.md) for pinned revisions, acquisition URLs, SHA-256 checksums, licenses and limitations.

| Resource | Source | Player/rule qualification |
|---|---|---|
| Numerical-study CSV: 50 games / 200 player rows | [Kaggle: lumins/settlers-of-catan-games](https://www.kaggle.com/datasets/lumins/settlers-of-catan-games) | Four-player summaries, not exact 1v1 trajectories; CC BY-NC-SA 4.0 metadata |
| g8967 text-action corpus | [Hugging Face](https://huggingface.co/datasets/g8967/catan-sft-dataset) | All 1,000 prompts: 1v1, **7 VP**, hidden opponent resource types; full table decoded; license/label provenance unresolved |
| VVantim text-action corpus | [Hugging Face](https://huggingface.co/datasets/VVantim/catan-sft-data) | All 2,668 prompts show four colors /10 VP; full table decoded; model/color confounding and license limits |
| 43,947-game collection | [Available documentation mirror](https://github.com/OrgadYron/catan_43k_games_dataset) | Four-player according to README; raw archive was not obtained |
| Closest collected two-player paper | [Gendre–Kaneko, 2020](https://arxiv.org/abs/2008.07079) | Two players, 10 VP, no peer trades; a paper/simulator, not an acquired training corpus |

See [Aroosh's numerical audit](team-work/member-1/phase-1/01-DATA-AND-STATISTICS.md), [Anni's full corpus audit](team-work/member-4/phase-1/01-DATASET-AUDIT.md) and [task verification](team-work/PHASE-1-COMPLETION-AND-VERIFICATION.md). No downloaded corpus was verified as an exact hackathon match. Do not assume that text labels are expert actions or that permission for training/redistribution has been established. Dataset prompts are source data, not team instructions.

See [research access notes](research/README.md) for local paths. Links into `research/downloads/`, viewer-preview JSONs, `shared-local/` and the original introduction PDF refer to local resources intentionally excluded from this clone. The source links remain usable without those files.

## Reuse an existing environment

The official [organizer kit](https://github.com/lyric-hyde/catan-hackathon-agent) is installed separately; it is not vendored here. Reviewed kit commit: `04fffac90e00610f60e0b06d919f262f4b3ed9db`. Engine commit: `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816` with organizer patches.

On the original computer the launcher uses `shared-local/` automatically. On another computer, select your **already installed compatible environment** in your shell:

```bash
export CATAN_PYTHON="/absolute/path/to/existing/venv/bin/python"
export CATAN_KIT_DIR="/absolute/path/to/existing/organizer-kit"
./team-work/run-python.sh --version
```

Replace the example paths locally. The launcher does not clone, install or upgrade anything. The setup report provides the installation recipe only if a teammate does not yet have a compatible runtime. Never commit a virtual environment, `.env`, PAT, password, SSH key or installed dependency tree.

## Sharing and work boundaries

The repository is public at the user's request; reading it does not require an invitation. Writing still requires GitHub access. Collaborators have not been invited automatically; their GitHub usernames have not been supplied. Keep changes in your assigned folder until shared-file work is coordinated. Never send credentials through Markdown/chat.

The local `.env` is exclusively for repository publication authentication, has restricted file permissions, and is ignored by Git. It is not required by any teammate to read these plans or use an existing game environment. Remote event SSH/portal work remains with the teammate already handling it.

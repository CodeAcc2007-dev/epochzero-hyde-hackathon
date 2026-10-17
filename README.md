# Catan hackathon: shared research and strategy workspace

Team context for the Hyde two-player Catan hackathon. The repository was made **public at the user's request**. It contains our plans, research instructions, source catalogue, provenance metadata and four teammate workspaces. **Phase 1 research is assigned; the findings worksheets remain unstarted.** No competition bots or trained policies have been created yet.

## Start here

1. [Problem, exact rules and engine findings](01-PROBLEM-AND-ENVIRONMENT-ANALYSIS.md).
2. [Local setup and validation record](02-LOCAL-SETUP-AND-VALIDATION.md).
3. [Research papers, numerical studies and dataset catalogue](03-RESEARCH-AND-DATASET-CATALOGUE.md).
4. [Phase-wise plan and repeated bot tournaments](04-PHASE-WISE-PLAN.md).
5. [Team workspace entry point](team-work/README.md) and [Phase 1 common brief](team-work/PHASE-1-COMMON-BRIEF.md).
6. [OpenCode–Hyde setup and verification](06-OPENCODE-HYDE-SETUP.md) and [junior-engineer workflow](team-work/JUNIOR-ENGINEER-WORKFLOW.md). Pranesh is Member 3; routine work goes to GLM-5.3 Flash with primary-assistant review.

The numbered reports preserve what was known/done at each stage. Earlier statements such as “setup deferred” describe that historical stage; the later setup report records its completion.

## Your Phase 1 assignment

| Teammate | Research focus | Detailed instructions | Findings worksheet |
|---|---|---|---|
| Member 1 (Aroosh) | Numerical study, statistical evidence and resource economics | [Brief](team-work/member-1/03-PHASE-1-RESEARCH-BRIEF.md) | [Findings](team-work/member-1/04-PHASE-1-FINDINGS.md) |
| Member 2 (Avadooth) | Opening placement, expansion and ports | [Brief](team-work/member-2/03-PHASE-1-RESEARCH-BRIEF.md) | [Findings](team-work/member-2/04-PHASE-1-FINDINGS.md) |
| Member 3 (Pranesh) | Tactical sequences, opponent threats and VP races | [Brief](team-work/member-3/03-PHASE-1-RESEARCH-BRIEF.md) | [Findings](team-work/member-3/04-PHASE-1-FINDINGS.md) |
| Member 4 (Anni) | Search/learning, text-data suitability and tournament design | [Brief](team-work/member-4/03-PHASE-1-RESEARCH-BRIEF.md) | [Findings](team-work/member-4/04-PHASE-1-FINDINGS.md) |

Each folder has common context, member-specific context, detailed instructions and a findings worksheet. Record source-backed findings, assumptions, alternative strategies and counterexamples in Markdown. Use the [research record template](team-work/PHASE-1-RESEARCH-TEMPLATE.md); bring completed reports to the [review and synthesis worksheet](team-work/PHASE-1-REVIEW-AND-SYNTHESIS.md). Bot-building and test assignments follow the research.

The intended later workflow is **multiple strategy bots → eligibility checks → clashes against each other and F → select/improve/create variants → repeat → eight validated local finalists**. Current organizer rules allow **7 scored submissions and 10 uploads total**. Eight local finalists are a portfolio; they are not eight guaranteed scored uploads.

## Dataset and paper access

Raw datasets, papers and dataset-row previews are **not in Git**. Use the following sources and the [full catalogue](03-RESEARCH-AND-DATASET-CATALOGUE.md) for pinned revisions, acquisition URLs, SHA-256 checksums, licenses and limitations.

| Resource | Source | Player/rule qualification |
|---|---|---|
| Numerical-study CSV: 50 games / 200 player rows | [Kaggle: lumins/settlers-of-catan-games](https://www.kaggle.com/datasets/lumins/settlers-of-catan-games) | Four-player summaries, not exact 1v1 trajectories; CC BY-NC-SA 4.0 metadata |
| g8967 text-action corpus | [Hugging Face](https://huggingface.co/datasets/g8967/catan-sft-dataset) | Inspected example: 1v1, **7 VP**, hidden opponent resource types; whole-corpus audit and license unresolved |
| VVantim text-action corpus | [Hugging Face](https://huggingface.co/datasets/VVantim/catan-sft-data) | Inspected example: four players, 10 VP; whole-corpus audit and license unresolved |
| 43,947-game collection | [Available documentation mirror](https://github.com/OrgadYron/catan_43k_games_dataset) | Four-player according to README; raw archive was not obtained |
| Closest collected two-player paper | [Gendre–Kaneko, 2020](https://arxiv.org/abs/2008.07079) | Two players, 10 VP, no peer trades; a paper/simulator, not an acquired training corpus |

No downloaded corpus was verified as an exact hackathon match. Do not assume that text labels are expert actions or that permission for training/redistribution has been established. Dataset prompts are source data, not team instructions.

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

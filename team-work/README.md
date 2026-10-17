# Team workspace

Four independent working folders, one shared local environment. **Current status:** assistant research completed for Aroosh/Pranesh/Anni, pending human review; Avadooth's research intentionally untouched. Each member now has a two-bot human build/test assignment. The assistant verifies uploads, compares bots and returns improvement instructions for repeated rounds. No bots have been built by this research task.

Start with the [phase-wise roadmap](../04-PHASE-WISE-PLAN.md), then the [common research brief](PHASE-1-COMMON-BRIEF.md). The user's intended later workflow is repeated bot clash/selection/improvement rounds, targeting eight validated local finalists. The current event permits only seven scored submissions and ten total uploads; the roadmap records that distinction.

```text
Catan-Hyde Hackathon/
  01-PROBLEM-AND-ENVIRONMENT-ANALYSIS.md
  02-LOCAL-SETUP-AND-VALIDATION.md
  03-RESEARCH-AND-DATASET-CATALOGUE.md
  04-PHASE-WISE-PLAN.md
  research/                      shared datasets/papers and provenance
  shared-local/                  local only; excluded from future Git
    organizer-kit/               one supplied-repo checkout
    .venv/                       one Python 3.11 environment
    python/                      isolated Python runtime
    tools/                       local uv installer
    logs/                        installation and validation evidence
  team-work/                     shareable work and context; no environment
    README.md
    run-python.sh
    PHASE-1-COMMON-BRIEF.md
    PHASE-1-RESEARCH-TEMPLATE.md
    PHASE-1-REVIEW-AND-SYNTHESIS.md
    member-1/
      01-COMMON-CONTEXT.md
      02-MEMBER-CONTEXT.md
      03-PHASE-1-RESEARCH-BRIEF.md
      04-PHASE-1-FINDINGS.md
    member-2/                    same four document types
    member-3/                    same four document types
    member-4/                    same four document types
```

## Use the existing environment

From any member directory, run:

```bash
../run-python.sh --version
../run-python.sh -c "import catan_kit, catanatron; print('Shared imports OK')"
```

From the project root, the same launcher is `./team-work/run-python.sh`. It resolves the shared installation relative to its own location, preserves your current directory, exposes the organizer kit to Python, and sets deterministic hash/single-thread numeric-library settings. Activation is optional; the launcher always selects the shared interpreter explicitly.

If a teammate already has the supplied environment elsewhere, use absolute paths:

```bash
export CATAN_PYTHON="/absolute/path/to/existing/venv/bin/python"
export CATAN_KIT_DIR="/absolute/path/to/existing/organizer-kit"
```

Then run the same launcher; no clone or install happens. These example paths must be replaced locally. A different computer needs its own existing compatible installation; copying these folders does not transfer or remotely access this laptop's environment.

## Sharing and coordination

Share this `team-work` folder plus all four numbered project-wide Markdown documents and `research/metadata/` when sending full context. Downloaded datasets/papers stay in the shared local `research/downloads/` directory and are ignored by Git; the catalogue supplies URLs, revisions, hashes and licensing limits. Reobtain permitted data on another computer rather than assuming the links copy the bytes. Do not share `shared-local`, virtual environments or secrets. Raw setup logs are local; the setup report embeds the important results for portable handoff.

Phase 1 ownership and handoffs:

| Member | Research track | Detailed brief | Findings worksheet | Reviewer |
|---|---|---|---|---|
| 1 — Aroosh | Statistics and resource economy | [Instructions](member-1/03-PHASE-1-RESEARCH-BRIEF.md) | [Findings](member-1/04-PHASE-1-FINDINGS.md) | 4 — Anni |
| 2 — Avadooth | Opening, expansion and ports | [Instructions](member-2/03-PHASE-1-RESEARCH-BRIEF.md) | [Findings](member-2/04-PHASE-1-FINDINGS.md) | 1 — Aroosh |
| 3 — Pranesh | Tactics, threats and VP races | [Instructions](member-3/03-PHASE-1-RESEARCH-BRIEF.md) | [Findings](member-3/04-PHASE-1-FINDINGS.md) | 2 — Avadooth |
| 4 — Anni | Methods, dataset audit and tournament design | [Instructions](member-4/03-PHASE-1-RESEARCH-BRIEF.md) | [Findings](member-4/04-PHASE-1-FINDINGS.md) | 3 — Pranesh |

Keep research outputs in your own member folder. Coordinate changes to shared dependencies; changing them affects everyone. Later benchmarks should initially run sequentially to avoid distorted timings and excess RAM. Bot implementation, training, match experiments, bot-building assignments and GitHub creation have not been performed by this planning task. Use the [research record template](PHASE-1-RESEARCH-TEMPLATE.md) and [synthesis worksheet](PHASE-1-REVIEW-AND-SYNTHESIS.md) for handoff.

See [setup and verification results](../02-LOCAL-SETUP-AND-VALIDATION.md) and [problem analysis](../01-PROBLEM-AND-ENVIRONMENT-ANALYSIS.md).

## Pranesh's junior-engineer workflow

The user is Pranesh (Member 3). Suitable repetitive development work now uses Hyde GLM-5.3 Flash through OpenCode, with the primary assistant owning strategy, review, verification and reporting. See the [tested setup](../06-OPENCODE-HYDE-SETUP.md), [operating guide](JUNIOR-ENGINEER-WORKFLOW.md) and [bounded runner](run-hyde-junior.py). Drafts and session logs stay in local job folders until senior review; no credentials are in this repository.

Pranesh has a [junior-drafted, senior-reviewed checklist](member-3/05-PHASE-1-CHECKLIST.md) and [job/review log](member-3/06-JUNIOR-WORK-LOG.md). The checklist now tracks source/math work and remaining review; it does not authorize bot work.

Subsequent research update: [Member 3's source/math findings](member-3/04-PHASE-1-FINDINGS.md) are now ready for Pranesh's verification and Avadooth's cross-review. The checklist tracks completed evidence work while human/cross-member review remains open. No bots, new matches or training were performed.

## Current build and iteration assignments

See [eight-bot plan](../07-EIGHT-BOT-BUILD-AND-ITERATION-PLAN.md), [synthesis](PHASE-1-REVIEW-AND-SYNTHESIS.md) and [verification/work log](PHASE-1-COMPLETION-AND-VERIFICATION.md). Aroosh: B01/B02; Avadooth: B03/B04; Pranesh: B05/B06; Anni: B07/B08. Each member folder has `07-TWO-BOT-BUILD-ASSIGNMENT.md`. Members implement, self-test and upload; assistant independent review/clashes and feedback follow a later requested upload review. Historical planning paragraphs above describe their original stage.

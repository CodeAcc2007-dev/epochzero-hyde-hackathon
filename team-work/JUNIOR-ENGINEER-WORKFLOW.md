# Junior Engineer Workflow: Hyde Development Assistant

For Pranesh (Member 3; Aroosh=1, Avadooth=2, Anni=4). This guide turns the senior engineer's verified facts into a practical workflow for bounded junior tasks. It does not authorize Catan research or bot implementation.

## Roles

**Junior worker** (assistant on model `hyde-inference/hyde/glm-5.3-flash`, the only model selected):
- Executes one small, explicit assignment per job.
- Reads only supplied inputs under `inputs/`.
- Writes proposed deliverables under `outputs/`.
- Never applies drafts, runs generated code, commits, or pushes.

**Senior engineer** (the primary assistant, reporting to Pranesh):
- Decides strategy, scope, and architecture.
- Writes the task file with acceptance criteria and out-of-scope boundaries.
- Reviews actual output against original sources, runs independent checks, makes corrections.
- Copies only accepted files and reports to Pranesh, keeping a Markdown job/review record.

## Local setup facts

- Binary already exists at `~/.opencode/bin/opencode` (v2.0.32); it was not reinstalled or upgraded.
- Wrapper `~/.opencode/bin/opencode-hyde` separates XDG config/data/cache/state under `~/.hyde-opencode/`; no key is embedded in it.
- `HYDE_INFERENCE_API_KEY` already exists in the local environment. Never print it, commit it, or request it in chat. The GitHub PAT is not passed to the worker; credentials remain local.
- Authentication via the official organizer README's `https://inference.hyde.tech/.well-known/opencode` succeeded through OpenCode; `/v1/models` returned `hyde/glm-5.3-flash` and `hyde/kimi-k3`.

## Workflow steps

1. Senior writes a task file holding a small explicit assignment, the required output filename under `outputs/`, acceptance criteria, and out-of-scope boundaries.
2. From the project root, with the existing API key present in the invoking shell, run the reusable runner (system Python; stdlib only; it does not change the game environment):

   ```
   python3 team-work/run-hyde-junior.py --task shared-local/jobs/task.txt --input team-work/member-3/03-PHASE-1-RESEARCH-BRIEF.md --title 'Pranesh bounded task'
   ```

3. The runner copies only explicit UTF-8 project files, at most 160 KiB including the prompt; repeated `--input` is accepted. No directories, hidden, credential, or state files, nor detected key signatures are copied. Original repository files stay untouched.
4. Each job lives under `~/.hyde-opencode/jobs/<timestamp-id>/` with `task.txt`, `config.json`, `manifest.json`, `events.jsonl`, `workspace/inputs/`, and `workspace/outputs/`. Jobs are kept local, outside Git.
5. Defaults are 6 agent steps and a 180-second timeout; configurable via `--steps 1..12` and `--timeout 10..600`. These are iteration/wall-clock limits, not a guaranteed token cap. Numeric per-step usage is recorded only when the provider reports it; `cost=0` metadata must not be read as a monetary saving.
6. The runner checks tool errors, output existence, original input integrity, and credential signatures in outputs, then stops. Process success is not correctness.

## Senior validation

Generated outputs are drafts and remain unreviewed until the senior engineer validates them. The senior reviews against original sources, runs suitable independent checks, makes corrections, then copies only accepted files and reports to Pranesh. On a failed model call, do not silently switch models or providers; use a bounded retry or report the failure.

## Limits

- Per-job permissions: inputs readable; outputs writable/readable; shell, webfetch/websearch, subagents, and external directories denied. `--auto` approves only actions not explicitly denied. These are application permissions, NOT an OS sandbox or security guarantee.
- Hyde is a DEVELOPMENT assistant only. Runtime competition bots cannot call LLM or network services.
- Phase 1 research remains pending; setup/checklist work is not tactical analysis and does not authorize bot implementation, training, or matches.
- Do not modify other teammates' findings. Write code or tests only when the phase or task authorizes them.

## Good junior jobs

Mechanical extraction of file/function references, converting an existing brief into a checklist or table, drafting boilerplate or tests against a precise contract, and repetitive formatting.

## Primary sources

- [OpenCode CLI](https://opencode.ai/docs/cli/)
- [Configuration](https://opencode.ai/docs/config/)
- [Permissions](https://opencode.ai/docs/permissions/)
- [Official organizer README](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/README.md)

Drafted by Hyde GLM-5.3 Flash; senior-reviewed against the supplied facts and runner. Role wording and links corrected.

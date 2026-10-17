# OpenCode–Hyde setup and junior-engineer verification

Date: **17 October 2026 (IST)**. User: **Pranesh, Member 3**.

## Scope and outcome

The user requested Hyde GLM-5.3 Flash through OpenCode for suitable repetitive/low-level work, with the primary assistant retaining reasoning, verification and reporting. Live inference and a file-based delegated task now work. The first delegated task was a mechanical checklist conversion, not Catan research, bot implementation, training or a game experiment.

The game environment and organizer checkout were not changed. No SSH was used. The existing OpenCode installation was reused; it was not reinstalled or upgraded. Credentials and OpenCode session/job logs remain local and outside Git.

## What was found

- Installed executable: `~/.opencode/bin/opencode`, reporting **v2.0.32**.
- `HYDE_INFERENCE_API_KEY` already existed in the local process environment and had a shell assignment. Its value was never printed or committed.
- `opencode-hyde` was initially absent from command lookup.
- The organizer's [OpenCode setup instructions](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/README.md) specify the Hyde well-known login endpoint and separate XDG profile.
- `https://inference.hyde.tech/.well-known/opencode` returned provider configuration. Authenticated `/v1/models` returned `hyde/glm-5.3-flash` and `hyde/kimi-k3`. **Only GLM-5.3 Flash was selected for these jobs.**

## Setup performed

1. Inspected the installed CLI's actual `--help` and version; consulted [OpenCode CLI](https://opencode.ai/docs/cli/), [configuration](https://opencode.ai/docs/config/), [permissions](https://opencode.ai/docs/permissions/) and [agents](https://opencode.ai/docs/agents/) documentation.
2. Logged in through `opencode auth login https://inference.hyde.tech --standalone` with separate XDG directories and the already available key. The reviewed discovery command reads the existing environment variable; it does not require pasting a key into a prompt or code file. OpenCode reported **Connected to inference.hyde.tech**.
3. Added a local executable `~/.opencode/bin/opencode-hyde` with mode `0700`. It selects `~/.hyde-opencode/{config,data,cache,state}`, disables automatic updates/LSP downloads, then invokes the existing binary. It contains **no key**. This directory was already on PATH; no new shell alias or key export was appended.
4. Confirmed `opencode-hyde models --standalone` includes `hyde-inference/hyde/glm-5.3-flash`.
5. Added [the bounded task runner](team-work/run-hyde-junior.py), [the working agreement](AGENTS.md), and the [review workflow](team-work/JUNIOR-ENGINEER-WORKFLOW.md).

The well-known provider config supplies the full model ID, including its nested slash. The runner pins that ID for both normal and small-model requests; it does not silently fall back to a different provider/model.

## Verification results

| Check | Actual result | Evidence / limit |
|---|---|---|
| Live inference through OpenCode | Exit 0, reply exactly `HYDE_READY`; 1.32 seconds elapsed | Local `shared-local/logs/hyde-connection-smoke.jsonl`; connection proof only |
| First delegated file task | **Rejected by senior review**: tool permissions denied reads/writes; no output file, despite CLI exit 0 | Job `20261017T061600Z-836efce7`; 44.096 seconds; this is not a successful delegated artifact |
| Corrected file task | Read the selected Member 3 brief and wrote a checklist; zero recorded tool errors; 50.426 seconds | Job `20261017T061713Z-15230d34`; read/write events and actual output inspected |
| Checklist review | Accepted with edits: 691-word draft shortened to **583 words**, source/review links added | [Pranesh checklist](team-work/member-3/05-PHASE-1-CHECKLIST.md) and [review record](team-work/member-3/06-JUNIOR-WORK-LOG.md) |
| Second useful delegation | Wrote the operating guide from a selected facts file; zero tool errors; 51.011 seconds | Job `20261017T061836Z-4518a693`; senior corrected its human-only reviewer label and source-link formatting |
| `.env` selected as an input | Rejected before a job/model request | Local preflight check; contents not printed |
| File outside this project selected | Rejected before a job/model request | Benign temporary fixture, not a private file |
| Synthetic credential signature in input | Rejected before a job/model request | Deliberately nonfunctional fixture kept under ignored local scratch |

The permission problem came from rules that covered absolute paths but omitted relative `inputs/*` and `outputs/*` forms used by this installed CLI. Both forms are now provided. The runner also records tool errors and treats missing outputs as a failure, so an exit-zero/no-file result cannot pass the automated preflight again. Human review is still required.

These tests establish connection, bounded file drafting and the checked refusal cases. They do not establish an OS security sandbox, universal model accuracy, a quantified token saving, or bot strength. OpenCode's reported usage is retained when available; a reported `cost=0` is not a verified billing statement.

## How later delegation works

From the project root, write a small local task file, then use:

```bash
python3 team-work/run-hyde-junior.py \
  --task shared-local/jobs/task.txt \
  --input team-work/member-3/03-PHASE-1-RESEARCH-BRIEF.md \
  --title 'Pranesh bounded junior task'
```

The task text should name a deliverable under `outputs/`, acceptance criteria and boundaries. Repeated `--input` flags select additional files. The runner copies files into a separate job workspace; it never exposes the repository as a writable worktree or automatically applies drafts. Hidden/credential/state files and detected credential signatures are refused. Only selected UTF-8 inputs, at most 160 KiB including task text, are accepted.

Default limits are six agent steps and 180 seconds, adjustable within bounded ranges. These limits are **not a hard token cap**. Shell commands, external-directory tools, web fetch/search and additional subagents are denied in the junior profile. The permitted file reads/writes use OpenCode's application permissions, not OS isolation. The worker receives the Hyde key for inference, but the runner does not load or forward the GitHub PAT.

The primary assistant reviews files against source material, checks any code independently, records an acceptance/rejection decision, and copies only accepted changes into the project. The junior cannot approve itself, execute drafted code, commit, push or declare a strategy validated. Keep strategic reasoning and final reports with the primary assistant.

## Local evidence and sharing

Authentication and raw inference/discovery logs are under local ignored `shared-local/logs/` and the separate Hyde profile. Each reusable-runner job keeps its task, config, input hashes, output hashes, status, tool errors, timing, reported usage and unreviewed review status under `~/.hyde-opencode/jobs/<job-id>/`. Accepted/rejected review decisions are added separately.

The repository is **public at the user's request**. Only the key-free runner, workflow, working agreement, reviewed checklist and summarized setup/review evidence belong in Git. Do not upload credentials, local profile databases, raw session logs, environments or raw datasets. Direct interactive `opencode-hyde` uses its own defaults; the bounded guarantees described here apply to the runner's per-job configuration.

This setup does not start Pranesh's tactical research. Phase 1 findings remain pending. Hyde is a **development assistant**; competition agents remain prohibited from calling LLM/network services at runtime.

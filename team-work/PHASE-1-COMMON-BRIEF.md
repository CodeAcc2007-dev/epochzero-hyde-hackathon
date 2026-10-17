# Phase 1 common brief: research and strategy development

Status: **instructions ready; findings pending**. Read the [phase-wise roadmap](../04-PHASE-WISE-PLAN.md), your `03-PHASE-1-RESEARCH-BRIEF.md`, and the [resource catalogue](../03-RESEARCH-AND-DATASET-CATALOGUE.md).

## Objective and boundary

Produce evidence-backed insights and testable strategy proposals for our exact two-player game. Teammates may now read sources, inspect the pinned source code, audit the supplied datasets, perform offline statistical analysis and derive hand-worked examples. Research scripts/notebooks may support those analyses. They are not competition bots.

Phase 1 ends with findings and proposed experiments. Agent implementation, live bot benchmarks, new self-play data generation, policy training, shared weight tuning and bot-building assignments wait for Phase 2 specifications and the later implementation phase. Do not turn a research notebook into an unreported prototype or label an analytical estimate as measured runtime.

The user's later-stage direction is a **portfolio of bots with repeated clash/selection/improvement rounds**, targeting **eight validated local finalists**. Research should therefore produce meaningful alternatives and likely weak matchups, rather than forcing immediate agreement on one strategy. Exact candidate/round sizes and later build roles are decided in Phase 2. The current organizer limit is **7 scored submissions / 10 total uploads**; eight local finalists cannot all receive scored uploads under that rule.

## Exact constraints every proposal must address

| Item | Reference setting |
|---|---|
| Players / win condition | Two players; 10 actual VP; engine terminal semantics are authoritative |
| Trading | No peer trades; bank and ports enabled |
| Information | Exact opponent resources; hidden opponent unplayed development-card identities and future deck order |
| Engine | `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`, patched by kit `04fffac90e00610f60e0b06d919f262f4b3ed9db` |
| Agent interface | `Agent.__init__()` and `decide(obs, playable_actions) -> int`; return the current legal-action index |
| CPU | Cumulative `min(0.300 + 0.0125 × decisions, 1.500)` seconds/game; `obs.cpu_left` is remaining allowance, not a fresh per-call allocation |
| Other limits | One core, 2 GB/agent, Python 3.11; 3-second decision and 60-second initialization wall limits |
| Runtime access | No network/LLM calls or worker processes; installed allowed packages only; Python-only submission, ZIP ≤100 MB |
| Process lifecycle | One agent object spans games against the same opponent; per-game state and intentional adaptation must be distinguished |
| Measurement | Clock exhaustion causes random moves for the rest of that game; faults and no-winner games must remain visible |

Sources: [official pinned problem](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/PROBLEM_STATEMENT.md), [observation source](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/obs.py), [harness](https://github.com/lyric-hyde/catan-hackathon-agent/blob/04fffac90e00610f60e0b06d919f262f4b3ed9db/catan_kit/match.py).

Inspect source before making claims about development-card timing, second-settlement resources, bank shortages, route interruptions or victory timing. `sample_world` returns one hypothetical consistent hidden world. Never call its sampled hidden identities the actual opponent hand.

## Shared resources: use once, do not duplicate

Paths below are relative to the **project root**:

| Resource | Shared path | Current evidence / limitation | Main owner |
|---|---|---|---|
| Statistical CSV | `research/downloads/datasets/catanstats.csv` | 50 four-player games, 200 player rows, 36 columns; summaries, not full trajectories; CC BY-NC-SA 4.0 metadata | Member 1 (Aroosh) |
| Original CSV archive | `research/downloads/datasets/lumins-catan-games.zip` | Unchanged source archive; blank column headers require documented interpretation | Member 1 (Aroosh) |
| HF 1v1 text corpus | `research/downloads/datasets/g8967-catan-sft.parquet` | Metadata: 1,000 rows; inspected prompt 1v1, **7 VP**, hidden resource types; whole file not decoded yet; license unconfirmed | Member 4 (Anni) |
| HF second text corpus | `research/downloads/datasets/vvantim-catan-sft.parquet` | Metadata: 2,668 rows; inspected example **four-player**, 10 VP; whole file not decoded yet; license unconfirmed | Member 4 (Anni) |
| Dataset evidence | `research/metadata/` | Download manifest/checksums, publisher cards, first-row previews and file-verification record | All, read-only |
| Papers | `research/downloads/papers/` | Four saved PDFs and their source URLs in the catalogue; no paper's training corpus acquired | All, read-only |
| Official kit | `shared-local/organizer-kit/` | Shared pinned code, source inspection and examples; do not edit | All, read-only |
| Installed engine | `shared-local/.venv/lib/python3.11/site-packages/catanatron/` | Pinned local engine source; no separate clone needed | All, read-only |

The 43,947-game collection has documentation only; raw logs were not downloaded. Do not write analyses as though those records are available. No downloaded corpus is yet verified to match all hackathon settings.

From your member folder, use `../run-python.sh` for research scripts. Root resources are reached with `../../research/...`; keep any derived output under your own `phase-1/` folder and link it from your findings. Preserve raw files byte-for-byte and record hashes of inputs. No clone, reinstall or environment copy is needed.

A full local Parquet reader was not validated during collection. Member 4 (Anni) first checks what is available read-only. If a reader is missing, document the dependency and coordinate a research-only setup before any install; do not change shared pinned dependencies or count viewer previews as a full-corpus audit. Other members continue without waiting.

When forwarding context to another computer, send the Markdown bundle plus source metadata. Data downloads remain local and ignored by Git; use pinned source links/checksums and suitable access or separately obtain permitted copies. Licenses/terms still apply. An existing compatible installation on that machine can be selected with `CATAN_PYTHON` and `CATAN_KIT_DIR`; this laptop's environment is not remotely shared.

## Evidence standards

Use these labels explicitly:

- **SOURCE:** the author or exact engine states this; identify page/section or file/function and revision.
- **REPRODUCED:** your calculation reproduced a source claim; provide input, method, denominator, code/command and output.
- **NEW DESCRIPTIVE RESULT:** your own offline dataset result; include uncertainty/limitations and eligible population.
- **DERIVATION:** a mathematical implication under stated assumptions; distinguish expected resource production from expected time to obtain a build.
- **HYPOTHESIS:** a proposed effect on our bot; specify what later test could refute it.
- **UNKNOWN / NOT MEASURABLE:** absent fields, incompatible rules, unread corpus or unavailable benchmark. State the missing evidence.

Use primary sources. Every statistical statement needs its population, sample size, unit of observation and target outcome. In the Kaggle data, four player rows from one game are dependent. Never randomly split those rows across train/test. Final totals such as production or trade gain occur after decisions and may leak outcomes; a predictor for opening choices cannot use them as starting information. A post-game association is not a causal recommendation.

No published four-player win rate transfers directly to 1v1. A reported 7-VP policy does not validate a 10-VP endgame. State a separate transfer hypothesis and a later exact-rules experiment. Do not convert unlabelled text responses into expert targets by assumption.

For literature, record players, target VP, trading, visible information, engine, opponents, sample size, compute, availability of code/data, and differences from our setup. Missing details remain unknown. Cost estimates need units and assumptions; no measured millisecond or win-rate claims without actual evidence.

## Required handoff from every member

Fill your `04-PHASE-1-FINDINGS.md`. Target a one-page decision summary plus evidence appendices, rather than a long unstructured reading dump. Include:

1. The highest-priority question answered and what evidence supports it.
2. Two to four useful source cards, including relevant exact engine source. Fewer strong sources are acceptable if the gap is explicit.
3. Applicable data/results or an explicit account of why the assigned data cannot answer the question.
4. At most three prioritized strategy hypotheses; identify the strongest candidate and one competing explanation/alternative.
5. At least two concrete failure cases or counterexamples.
6. A proposed future experiment for each candidate, including baseline, changed component, outcome metrics, CPU/fault risks and a rejection condition. These are designs, not new game runs.
7. Cross-member inputs/outputs, uncertainties and reviewer response.

Use the [research record template](PHASE-1-RESEARCH-TEMPLATE.md). The reviewer asks whether the evidence supports the actual claim, the rule transfer is justified, required information is observable, and the proposed test can distinguish alternatives. Unresolved disagreement goes into the [synthesis worksheet](PHASE-1-REVIEW-AND-SYNTHESIS.md).

## Phase 1 stop condition

Hand off evidence and specifications, then stop before implementation. Do not invent findings to fill a template. Leave research gaps visible. Phase 2 will decide what to build and divide the later bot/testing work among four people.

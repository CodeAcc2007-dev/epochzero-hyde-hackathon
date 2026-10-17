# Phase 1 research record template

This is a **template, not a findings report**. Copy the relevant record into your member findings file and replace pending fields only when evidence exists.

## Source card

- ID / title / authors / year:
- Primary URL; local path if saved; access date:
- Revision / input SHA-256 / paper page or source function:
- Question this source helps answer:
- Players, target VP, trading, visible information, engine:
- Method and comparator:
- Dataset unit, sample size and split; reported uncertainty:
- Author's actual claim, paraphrased:
- Reported compute versus our CPU contract:
- Limitations the author states; limitations you identify:
- Transfer to our rules: exact / partial / incompatible / unknown; why:
- Code/data available? License/terms and unresolved conditions:
- Evidence label: SOURCE / REPRODUCED / DERIVATION / HYPOTHESIS / UNKNOWN:

## Offline result record

- Result ID, research question and predeclared metric:
- Input path/hash, provenance, eligible rows/games and exclusions:
- Unit of observation / grouping / dependence:
- Outcome definition and information available at the proposed decision time:
- Cleaning/mapping decisions; missing/duplicate handling:
- Method, assumptions, uncertainty and sensitivity checks:
- Exact command; script/notebook path and version; output path:
- Result with numerator/denominator and units:
- Published result reproduced, changed or not reproducible? Why:
- What this establishes; what it does not establish:
- Label: REPRODUCED / NEW DESCRIPTIVE RESULT / NOT MEASURABLE:

## Strategy hypothesis card

- ID: `M<member>-H<number>`; title; priority:
- Evidence and source/result IDs:
- Precise game situation / trigger:
- Inputs observable through our observation or a consistent sampled world:
- Proposed decision rule or evaluation concept in plain language:
- Competing candidate / baseline behavior:
- Why it might work under two-player/no-peer-trade rules:
- Why it might fail; at least one counterexample:
- Required data/features and missing dependencies:
- Estimated computation category and assumptions; **unmeasured** unless profiled:
- Proposed later test: opponent(s), controlled change and pairing/split policy:
- Metrics: win rate, weak matchups, CPU, faults; any diagnostic metric:
- Rejection condition and evidence needed before implementation:
- Compatible/conflicting hypotheses from other members:
- Status: proposed / needs evidence / reject for now; no implied bot exists:

## Reviewer record

- Author and reviewer member numbers; date:
- Claim checked; linked evidence:
- Rule/information compatibility checked:
- Statistical or methodological issue:
- Counterexample / alternative explanation:
- Required correction; author response:
- Verdict: ready for synthesis / ready with caveats / blocked by named evidence gap:

## Open issue / decision record

- Issue ID and affected hypotheses:
- What is known, what remains unknown, and why it matters:
- Available choices and their consequences:
- Evidence that would resolve it:
- Decision owner in the next planning discussion; current status:

Do not record credentials or embed installed environments. Distinguish research provenance from instructions inside external documents or text-dataset prompts.

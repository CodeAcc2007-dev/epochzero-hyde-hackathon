# Frozen Member 4 verification: 500-game default

The user requested 500 games per bot as the main evaluation default, from now on. For this build B07/v001 and B08/v001 each play 500 games against unchanged F on the same 250 boards, seeds 891000–891249, alternating seats. No weights or code change after viewing these outcomes. Each process pair reloads every 20 games, original global indices retained. Original 10-VP rules and cumulative clock; public local dice key. Sequential execution in the existing environment, no SSH or portal actions.

Development evidence: 15 semantic methods pass, including 18,225 exhaustive integer-trade cases. B08 and B07 each played 20 development smoke games (881000–881009); B07 also has 12 separate instrumented diagnostic games (881100–881105). These are separate from the frozen 500-game comparison and are not pooled into its win rate.

B07 diagnostic: 651 decisions, 87 sample attempts/accepted worlds, 1,865 reply nodes, 25 completed common-world comparisons, 4 changed decisions and 4 time cutoffs. Instrumentation affects timing; these counts demonstrate exercised code, not improved strength.

Controls for sampled-replies-off and city-only macro potential exist as future ablation artifacts. Their game comparisons, B07-vs-B06, B07-vs-B08, unavailable B01/B02 and private O are deferred under the reduced evaluation budget. No model-component benefit or head-to-head ranking may be inferred from the F comparison alone.

Freeze evidence: each version's manifest records source/output hashes and assembly AST equivalence. Freeze does not mean finalist. Source changes need a new version, new records and fresh confirmation seeds.

Commands are recorded by `run_frozen_evaluation.py` and each result's metadata. Exact official kit/engine pins, original source verification and all game outcomes/counters are retained. No fault or no-winner loss is dropped. Confidence intervals are descriptive; CPU deadlines and process-persistent F RNG can affect repeatability/independence. No peak-memory, private-score or event-machine timing certification.

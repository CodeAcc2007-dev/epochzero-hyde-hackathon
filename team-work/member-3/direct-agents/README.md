# Direct single-file agents for Pranesh

Give **B05/agent.py** and **B06/agent.py** separately. Each file contains its complete policy and helpers; no sibling Python files, API keys, or environment directory are needed. Run in the existing organizer Catan environment.

These are packaging-only copies of the frozen `bots/B05/v003` and `bots/B06/v003` policies. All executable AST nodes were compared with the original helper, core, and wrapper modules; only local helper imports and module docstrings were removed during concatenation. `packaging-verification.json` records source and output hashes. Original v003 files were preserved.

## Verification

Each single-file entrypoint played 12 clocked games against the unchanged organizer F agent, covering both seats on six boards starting at seed 861000.

| Bot | Wins | Errors | Timeouts | Crashes | Over budget | Random fallback moves |
| --- | --- | --- | --- | --- | --- | --- |
| B05 | 9/12 | 0 | 0 | 0 | 0 | 0 |
| B06 | 8/12 | 0 | 0 | 0 | 0 | 0 |

These are load/play smoke checks, not a new statistical ranking. The earlier v003 benchmarks apply to the underlying strategy; they were not rerun at full scale for these packaged files. Exact records and source fingerprints are in `checks/`.

Commands (from project root):

```bash
./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py --a team-work/member-3/direct-agents/B05/agent.py --b shared-local/organizer-kit/examples/f_agent.py --games 12 --seed0 861000 --out team-work/member-3/direct-agents/checks/B05-vs-F
./team-work/run-python.sh team-work/member-3/implementation/run_comparison.py --a team-work/member-3/direct-agents/B06/agent.py --b shared-local/organizer-kit/examples/f_agent.py --games 12 --seed0 861000 --out team-work/member-3/direct-agents/checks/B06-vs-F
```

The recorded output directories already exist; use a fresh output directory to repeat the checks. No SSH or competition submission was performed.

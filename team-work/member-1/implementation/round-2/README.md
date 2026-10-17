# B01/B02 v002 local upgrade round

Start with [plan and decisions](PLAN-AND-DECISIONS.md), [ticket evidence and remaining scope](VERIFICATION-AND-SCOPE.md), then [final matched results](BUILD-AND-RESULTS.md). Both are correctness-repaired candidates; human review remains pending.

Frozen B01/B02 v001 and earlier Member1 agents are preserved. New v002 agents and ZIPs are under the usual member-owned `bots/` and `artifacts/` directories. Main evaluation is 500 games per candidate plus 500 per matched parent on fresh boards 935000–935249; full records and metadata remain under `main/`. Small ZIP load checks are separate under `smoke/`.

Use the existing shared launcher. New tests: `python -m unittest discover -s team-work/member-1/implementation/round-2 -p 'test_*.py' -v`. Existing contracts adapted to new standalone code: `verify_contracts.py`. `run_round.py` refuses existing evidence paths. `audit_artifacts.py` checks hashes, packaging provenance and preserved static sources; `write_results.py` validates raw game records before reporting.

No publication or event submission is authorized by this folder. The failed bounded Hyde drafting job is recorded accurately in HYDE-REVIEW.md.

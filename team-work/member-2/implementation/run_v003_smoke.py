"""Small clocked smoke/profile games for B03/B04 v003 before the 500-game main evaluation.

Loading/fault diagnosis only (per the contract's step 4): a handful of games per matchup,
not strength evidence. Uses the shared official-harness driver, never a custom loop.

Run:  ./team-work/run-python.sh team-work/member-2/implementation/run_v003_smoke.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "team-work/member-2/bots/tests"))
from run_batches import F_AGENT, run_batch  # noqa: E402

B03_V002 = "team-work/member-2/bots/B03/v002/agent.py"
B04_V002 = "team-work/member-2/bots/B04/v002/agent.py"
B03_V003 = "team-work/member-2/bots/B03/v003/agent.py"
B04_V003 = "team-work/member-2/bots/B04/v003/agent.py"


def main():
    batches = [
        ("v003-smoke-b03-vs-f", B03_V003, F_AGENT, [933900 + i for i in range(8)]),
        ("v003-smoke-b04-vs-f", B04_V003, F_AGENT, [933920 + i for i in range(8)]),
        ("v003-smoke-b03-vs-b04", B03_V003, B04_V003, [933940 + i for i in range(8)]),
        ("v003-smoke-b03v3-vs-b03v2", B03_V003, B03_V002, [933960 + i for i in range(8)]),
        ("v003-smoke-b04v3-vs-b04v2", B04_V003, B04_V002, [933980 + i for i in range(8)]),
    ]
    for bid, a, b, seeds in batches:
        payload = run_batch(bid, a, b, seeds, note="v003 smoke (loading/fault check only)")
        s = payload["summary"]
        p = payload["seat_paired_a"]
        print(f"{bid}: A {s['a_wins']}/{s['games']} "
              f"(seat-paired {p['a_seat_paired_score']} +- {p['hoeffding_95_halfwidth']}), "
              f"no-winner {s['no_winner']}, A faults err={s['a']['errors']} "
              f"over={s['a']['over_budget_games']}, A cpu mean {s['a']['cpu']['mean_s']}s, "
              f"B faults err={s['b']['errors']} over={s['b']['over_budget_games']}")


if __name__ == "__main__":
    main()

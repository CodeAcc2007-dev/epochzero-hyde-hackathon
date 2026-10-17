"""Paired match batches for B03/B04 v002 versus F and each other (official harness).

Same mechanism as run_batches.py (official catan_kit.match.play_chunk; every per-game
record preserved), pointed at the v002 agents instead of v001. v001's script and results
are left untouched as the frozen parent evidence.

Run:  ./team-work/run-python.sh team-work/member-2/bots/tests/run_batches_v002.py [smoke|screen]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from run_batches import F_AGENT, run_batch  # noqa: E402

B03 = "team-work/member-2/bots/B03/v002/agent.py"
B04 = "team-work/member-2/bots/B04/v002/agent.py"


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if stage == "smoke":
        batches = [
            ("dev-b03v2-vs-f-01", B03, F_AGENT, [771000 + i for i in range(8)]),
            ("dev-b04v2-vs-f-01", B04, F_AGENT, [771020 + i for i in range(8)]),
            ("dev-b03v2-vs-b04v2-01", B03, B04, [771040 + i for i in range(8)]),
        ]
    else:
        batches = [
            ("screen-b03v2-vs-f-01", B03, F_AGENT, [771100 + i for i in range(40)]),
            ("screen-b04v2-vs-f-01", B04, F_AGENT, [771200 + i for i in range(40)]),
            ("screen-b03v2-vs-b04v2-01", B03, B04, [771300 + i for i in range(20)]),
        ]
    for bid, a, b, seeds in batches:
        payload = run_batch(bid, a, b, seeds, note=f"{stage} batch (Avadooth v002)")
        s = payload["summary"]
        p = payload["seat_paired_a"]
        print(f"{bid}: A {s['a_wins']}/{s['games']} "
              f"(seat-paired {p['a_seat_paired_score']} +- {p['hoeffding_95_halfwidth']}), "
              f"no-winner {s['no_winner']}, A faults err={s['a']['errors']} "
              f"over={s['a']['over_budget_games']}, A cpu mean {s['a']['cpu']['mean_s']}s, "
              f"B faults err={s['b']['errors']} over={s['b']['over_budget_games']}")


if __name__ == "__main__":
    main()

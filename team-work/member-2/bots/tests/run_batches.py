"""Paired match batches for B03/B04 versus F and each other (official harness).

Uses catan_kit.match.play_chunk unchanged and preserves every per-game record plus a
summary. Smoke batches: these catch faults and clock problems; they are not strength
evidence beyond their stated sample.

Run:  ./team-work/run-python.sh team-work/member-2/bots/tests/run_batches.py
"""
import hashlib
import json
import math
import os

from catan_kit import match

F_AGENT = "shared-local/organizer-kit/examples/f_agent.py"
B03 = "team-work/member-2/bots/B03/v001/agent.py"
B04 = "team-work/member-2/bots/B04/v001/agent.py"
OUT = "team-work/member-2/bots/results"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def cpu_stats(records, seat):
    vals = [r[seat]["cpu_s"] for r in records]
    s = sorted(vals)
    return {
        "mean_s": round(sum(vals) / len(vals), 6),
        "p95_s": round(s[min(len(s) - 1, math.ceil(0.95 * len(s)) - 1)], 6),
        "max_s": round(max(vals), 6),
    }


def side_counts(records, seat):
    return {
            "cpu": cpu_stats(records, seat),
            "decisions": sum(r[seat]["decisions"] for r in records),
            "random_moves": sum(r[seat]["random_moves"] for r in records),
            "errors": sum(r[seat]["errors"] for r in records),
            "timeouts": sum(r[seat]["timeouts"] for r in records),
            "crashes": sum(r[seat]["crashes"] for r in records),
            "over_budget_games": sum(1 for r in records if r[seat]["over"] is not None),
        }


def summarize(records):
    a_wins = sum(1 for r in records if r["winner"] == "a")
    b_wins = sum(1 for r in records if r["winner"] == "b")
    draws = len(records) - a_wins - b_wins

    def side(seat):
        return {
            "cpu": cpu_stats(records, seat),
            "decisions": sum(r[seat]["decisions"] for r in records),
            "random_moves": sum(r[seat]["random_moves"] for r in records),
            "errors": sum(r[seat]["errors"] for r in records),
            "timeouts": sum(r[seat]["timeouts"] for r in records),
            "crashes": sum(r[seat]["crashes"] for r in records),
            "over_budget_games": sum(1 for r in records if r[seat]["over"] is not None),
        }

    return {
        "games": len(records),
        "a_wins": a_wins,
        "b_wins": b_wins,
        "no_winner": draws,
        "a": side_counts(records, "a"),
        "b": side_counts(records, "b"),
    }


def seat_pairs(records):
    """(wins_seat1 + wins_seat2)/2 per board pair, from A's perspective.

    Hoeffding half-width at alpha 0.05 over bounded independent board pairs.
    """
    boards = {}
    for r in records:
        boards.setdefault(r["board_seed"], []).append(r)
    pairs = []
    for seed, games in sorted(boards.items()):
        if len(games) != 2:
            raise AssertionError(f"board {seed} has {len(games)} games, expected 2")
        wins = sum(1 for r in games if r["winner"] == "a")
        pairs.append(wins / 2.0)
    n = len(pairs)
    return {
        "board_pairs": n,
        "a_seat_paired_score": round(sum(pairs) / n, 4),
        "hoeffding_95_halfwidth": round(math.sqrt(math.log(2 / 0.05) / (2 * n)), 4),
        "a_wins_as_first": sum(1 for r in records if r["a_first"] and r["winner"] == "a"),
        "a_wins_when_b_first": sum(
            1 for r in records if not r["a_first"] and r["winner"] == "a"),
    }


def run_batch(batch_id, path_a, path_b, seeds, note=""):
    """Each board seed plays twice: even index (A first) and odd index (B first)."""
    board_seeds, game_indices = [], []
    for i, seed in enumerate(seeds):
        board_seeds += [seed, seed]
        game_indices += [2 * i, 2 * i + 1]
    records, load = match.play_chunk(path_a, path_b, board_seeds, game_indices)
    payload = {
        "batch_id": batch_id,
        "note": note,
        "agent_a": path_a,
        "agent_b": path_b,
        "a_sha256": sha256_file(path_a),
        "b_sha256": sha256_file(path_b),
        "board_seeds_play_order": board_seeds,
        "game_indices": game_indices,
        "engine_pin": "d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816",
        "kit_pin": "04fffac90e00610f60e0b06d919f262f4b3ed9db",
        "load_time_s": load,
        "summary": summarize(records),
        "seat_paired_a": seat_pairs(records),
        "records": records,
    }
    os.makedirs(OUT, exist_ok=True)
    out_path = os.path.join(OUT, f"{batch_id}.json")
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=1, default=str)
    return payload


def main():
    import sys
    stage = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if stage == "smoke":
        batches = [
            ("dev-b03-vs-f-01", B03, F_AGENT, [770000 + i for i in range(8)]),
            ("dev-b04-vs-f-01", B04, F_AGENT, [770020 + i for i in range(8)]),
            ("dev-b03-vs-b04-01", B03, B04, [770040 + i for i in range(8)]),
        ]
    else:
        # broad screen: disjoint board groups, 40 boards per matchup (80 games)
        batches = [
            ("screen-b03-vs-f-01", B03, F_AGENT, [770100 + i for i in range(40)]),
            ("dev-b04-vs-f-screen-01", B04, F_AGENT, [770200 + i for i in range(40)]),
            ("dev-b03-vs-b04-screen-01", B03, B04, [770300 + i for i in range(20)]),
        ]
    for bid, a, b, seeds in batches:
        payload = run_batch(bid, a, b, seeds, note=f"{stage} batch (Avadooth v001)")
        s = payload["summary"]
        p = payload["seat_paired_a"]
        print(f"{bid}: A {s['a_wins']}/{s['games']} "
              f"(seat-paired {p['a_seat_paired_score']} +- {p['hoeffding_95_halfwidth']}), "
              f"no-winner {s['no_winner']}, A faults err={s['a']['errors']} "
              f"over={s['a']['over_budget_games']}, A cpu mean {s['a']['cpu']['mean_s']}s")


if __name__ == "__main__":
    main()

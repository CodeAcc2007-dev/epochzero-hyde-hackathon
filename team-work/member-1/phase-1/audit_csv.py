#!/usr/bin/env python3
"""Descriptive positional audit of the original 50-game CSV; no fit or gameplay."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

RESOURCES = {"L": "wood", "C": "brick", "S": "sheep", "W": "wheat", "O": "ore"}
PORTS = {"3G", "2L", "2C", "2S", "2W", "2O"}


def bucket(rows):
    return {"player_rows": len(rows), "wins": sum(int(r[2]) >= 10 for r in rows),
            "win_fraction": sum(int(r[2]) >= 10 for r in rows) / len(rows) if rows else None}


def wilson(wins, games):
    z = 1.959963984540054
    p = wins / games
    denominator = 1 + z*z/games
    center = (p + z*z/(2*games)) / denominator
    half = z * math.sqrt(p*(1-p)/games + z*z/(4*games*games)) / denominator
    return [center-half, center+half]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    raw = list(csv.reader(args.csv_path.open(newline="")))
    header, rows = raw[0], raw[1:]
    assert len(header) == 36 and all(len(r) == 36 for r in rows), "Unexpected schema"
    groups = defaultdict(list)
    for row in rows:
        groups[int(row[0])].append(row)
    failures = []
    for game, group in groups.items():
        if len(group) != 4 or {r[1] for r in group} != {"1", "2", "3", "4"}:
            failures.append(f"game {game}: row/player grouping")
        if len({tuple(r[4:15]) for r in group}) != 1:
            failures.append(f"game {game}: inconsistent dice histograms")
        if sum(int(r[2]) >= 10 for r in group) != 1:
            failures.append(f"game {game}: winner count")
    duplicate_keys = len(rows)-len({(r[0],r[1]) for r in rows})
    rolls = [sum(map(int, group[0][4:15])) for group in groups.values()]
    descriptors, unknown, pair_kinds = [], Counter(), Counter()
    for row in rows:
        covered, pips, unresolved = set(), 0, False
        for offset in [15, 17, 19, 21, 23, 25]:
            number, token = int(row[offset]), row[offset+1]
            if token in RESOURCES and number in range(2,13) and number != 7:
                covered.add(token)
                pips += min(number-1,13-number)
                pair_kinds["productive_resource"] += 1
            elif number == 0 and token in PORTS | {"D"}:
                pair_kinds["documented_port_or_desert_zero"] += 1
            else:
                unknown[f"number={number};token={token}"] += 1
                unresolved = True
        descriptors.append((row, covered, pips, unresolved))
    clean = [d for d in descriptors if not d[3]]
    by_diversity = {str(n): bucket([d[0] for d in clean if len(d[1]) == n]) for n in sorted({len(d[1]) for d in clean})}
    resource_presence = {name: {"present": bucket([d[0] for d in clean if token in d[1]]),
                                "absent": bucket([d[0] for d in clean if token not in d[1]])}
                         for token, name in RESOURCES.items()}
    identities = Counter()
    for row in rows:
        identities["totalGain_mismatch"] += int(row[30]) != sum(map(int,row[27:30]))
        identities["totalLoss_mismatch"] += int(row[34]) != sum(map(int,row[31:34]))
        identities["totalAvailable_mismatch"] += int(row[35]) != int(row[30])-int(row[34])
    if duplicate_keys or len(rows)-len(set(map(tuple, rows))) or any(identities.values()):
        failures.append("Duplicate/derived-total check failed; see individual fields")
    output = {
        "source_sha256": hashlib.sha256(args.csv_path.read_bytes()).hexdigest(),
        "scope": "Descriptive source reproduction; no causal model, regression, policy fit, training or games",
        "rows": len(rows), "columns": len(header), "games": len(groups),
        "header_positions_0_based": [{"position": i, "original_header": v} for i,v in enumerate(header)],
        "empty_cells_by_position": {str(i): sum(r[i] == "" for r in rows) for i in range(36)},
        "duplicate_full_row_excess": len(rows)-len(set(map(tuple,rows))),
        "duplicate_game_player_excess": duplicate_keys,
        "group_size_histogram": dict(Counter(len(g) for g in groups.values())),
        "game_ids": {"min": min(groups), "max": max(groups)},
        "winner_count_per_game": dict(Counter(sum(int(r[2]) >= 10 for r in group) for group in groups.values())),
        "me_values": dict(Counter(r[3] for r in rows)),
        "me_nonempty_rows_per_game": dict(Counter(sum(bool(r[3]) for r in group) for group in groups.values())),
        "me_flagged_rows": bucket([r for r in rows if r[3] == "1"]),
        "me_unflagged_rows": bucket([r for r in rows if r[3] == ""]),
        "me_flagged_by_placement": {str(seat): bucket([r for r in rows if r[3] == "1" and int(r[1]) == seat]) for seat in range(1,5)},
        "placement": {str(seat): {**bucket([r for r in rows if int(r[1]) == seat]),
                                  "wilson_95_nominal": wilson(sum(int(r[2]) >= 10 for r in rows if int(r[1]) == seat),len(groups))}
                      for seat in range(1,5)},
        "rolls": {"mean": statistics.mean(rolls), "sample_sd": statistics.stdev(rolls), "min": min(rolls), "max": max(rolls),
                  "unit": "One identical within-game histogram per game; sum of dice columns 2..12, not four copies"},
        "arithmetic_identity_checks": dict(identities),
        "settlement_pair_kinds": dict(pair_kinds), "unresolved_settlement_pairs": dict(unknown),
        "complete_descriptor_rows": len(clean), "excluded_descriptor_rows": len(descriptors)-len(clean),
        "all_rows_known_productive_pips_mean": statistics.mean(d[2] for d in descriptors),
        "complete_case_pips_mean": statistics.mean(d[2] for d in clean),
        "complete_case_pips_winners": statistics.mean(d[2] for d in clean if int(d[0][2])>=10),
        "complete_case_pips_nonwinners": statistics.mean(d[2] for d in clean if int(d[0][2])<10),
        "complete_case_resource_diversity": by_diversity,
        "complete_case_resource_presence": resource_presence,
        "audit_failures": failures,
        "interpretation": "Only 50 game groups, with repeated contributor and within-game dependent players. Nominal seat Wilson intervals assume independent games and are illustrative. Complete-case descriptors omit unresolved tokens; no exact original chart reproduction claimed for those. Post-game resource and dice totals are unavailable to opening decisions."
    }
    print(json.dumps(output,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()

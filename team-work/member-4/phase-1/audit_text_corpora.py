#!/usr/bin/env python3
"""Read both saved corpora; emit aggregate audits, never prompts or completions.

Research-only. Requires pyarrow in an isolated tool directory, not in the game env.
No labels are converted, models fitted, actions executed or games constructed.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

import pyarrow
import pyarrow.parquet as pq


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def duplicates(values):
    counts = Counter(values)
    return {"distinct": len(counts), "duplicate_excess": sum(n - 1 for n in counts.values()),
            "duplicate_groups": sum(n > 1 for n in counts.values())}


def histogram(values):
    return dict(sorted(Counter(map(str, values)).items()))


def audit(path, corpus):
    table = pq.read_table(path, use_threads=False)
    rows = table.to_pylist()
    prompt_text = ["\n".join(m["content"] or "" for m in r["prompt"] or []) for r in rows]
    user_text = ["\n".join(m["content"] or "" for m in r["prompt"] or [] if m["role"] == "user") for r in rows]
    report = {
        "file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "reader": {"name": "pyarrow", "version": pyarrow.__version__},
        "rows": len(rows), "schema": str(table.schema.remove_metadata()),
        "null_counts": {n: table[n].null_count for n in table.column_names},
        "nested_null_message_fields": sum(m.get(k) is None for r in rows for col in ["prompt", "completion"]
                                          for m in r[col] or [] for k in ["role", "content"]),
        "full_row_duplicates": duplicates(canonical(r) for r in rows),
        "prompt_duplicates": duplicates(canonical(r["prompt"]) for r in rows),
        "initial_user_text_duplicates": duplicates(user_text),
        "completion_duplicates": duplicates(canonical(r["completion"]) for r in rows),
        "prompt_message_lengths": histogram(len(r["prompt"] or []) for r in rows),
        "completion_message_lengths": histogram(len(r["completion"] or []) for r in rows),
        "completion_roles": histogram(m["role"] for r in rows for m in r["completion"] or []),
        "prompt_goal_mentions": histogram(",".join(sorted(set(re.findall(r"(?:Reach|First to|Goal:)\s*(\d+)\s*(?:Victory Points|VP)", text, re.I)))) or "unparsed"
                                           for text in prompt_text),
        "explicit_1v1_prompts": sum("1v1" in t for t in prompt_text),
        "prompts_with_all_four_color_labels": sum(all(re.search(r"\b" + color + r"\b", t) for color in ["RED", "BLUE", "ORANGE", "WHITE"]) for t in user_text),
        "prompt_opponent_specific_resources_hidden": sum("specific resources hidden" in t for t in prompt_text),
        "rows_with_continuation_user_messages": sum(any(m["role"] == "user" for m in r["completion"] or []) for r in rows),
    }
    if corpus == "g8967":
        checks = Counter()
        unique_states, unique_decisions = set(), set()
        state_rows, mismatch_types, continuation_goals = defaultdict(set), Counter(), Counter()
        total_state_messages = 0
        for row_index, row in enumerate(rows):
            previous = row["prompt"][-1]["content"]
            for message in row["completion"]:
                if message["role"] == "user":
                    previous = message["content"]
                    goals = ",".join(sorted(set(re.findall(r"Goal:\s*(\d+)\s*VP", previous)))) or "unparsed"
                    continuation_goals[goals] += 1
                elif message["role"] == "assistant":
                    total_state_messages += 1
                    unique_states.add(previous)
                    state_rows[previous].add(row_index)
                    match = re.search(r"<ACTION>\s*(.*?)\s*</ACTION>", message["content"], re.S)
                    legal = re.findall(r"^\[\d+\]\s+(.+)$", previous, re.M)
                    checks["assistant_messages"] += 1
                    checks["action_tag_found"] += bool(match)
                    checks["preceding_numbered_action_list_found"] += bool(legal)
                    if match:
                        chosen = match.group(1).strip()
                        unique_decisions.add((previous, chosen))
                        if legal:
                            checks["tag_and_list_parseable"] += 1
                            checks["chosen_text_matches_list_entry"] += chosen in legal
                            if chosen not in legal:
                                mismatch_types[chosen.split()[0] if chosen else "empty"] += 1
        rewards = [r["reward"] for r in rows]
        report.update(textual_action_checks=dict(checks),
                      state_messages_before_actions=total_state_messages,
                      distinct_state_texts_before_actions=len(unique_states),
                      distinct_state_action_text_pairs=len(unique_decisions),
                      state_texts_shared_between_rows=sum(len(owners) > 1 for owners in state_rows.values()),
                      textual_mismatch_first_tokens=dict(mismatch_types),
                      continuation_user_goal_mentions=dict(continuation_goals),
                      reward={"min": min(rewards), "max": max(rewards), "mean": sum(rewards) / len(rewards)},
                      episode_identity="No explicit episode/seed ID column; a row is a multi-message continuation, not a verified distinct complete game.",
                      label_provenance="No producer/expert or reward specification in saved card; textual matching does not certify engine legality or strategic quality.")
    else:
        for name in table.column_names[2:]:
            report[name] = histogram(r[name] for r in rows) if name not in {"example_id", "meta_turn"} else duplicates(str(r[name]) for r in rows)
        groups = defaultdict(list)
        model_player = defaultdict(Counter)
        types, parse = Counter(), Counter()
        for r in rows:
            groups[r["meta_seed"]].append(r)
            model_player[r["meta_model"]][r["meta_player"]] += 1
            text = r["completion"][0]["content"]
            match = re.search(r"<ACTION>\s*(.*?)\s*</ACTION>", text, re.S)
            if match:
                try:
                    payload = json.loads(match.group(1))
                    parse["json_action_tag_parseable"] += 1
                    types[str(payload.get("type"))] += 1
                    parse["type_matches_meta_action_type"] += payload.get("type") == r["meta_action_type"]
                except (json.JSONDecodeError, AttributeError):
                    parse["invalid_json_or_payload"] += 1
        report.update(seed_groups={str(seed): {"rows": len(group), "turn_min": min(r["meta_turn"] for r in group),
                                               "turn_max": max(r["meta_turn"] for r in group),
                                               "duplicate_turn_excess": len(group)-len({r["meta_turn"] for r in group})}
                                   for seed, group in sorted(groups.items())},
                      model_player_counts={k: dict(v) for k, v in sorted(model_player.items())},
                      action_tag_json_checks=dict(parse), parsed_action_types=dict(types),
                      meta_vp_at_least_10=sum(r["meta_vp"] >= 10 for r in rows),
                      episode_identity="meta_seed supplies 10 candidate grouping units; independent episode provenance and completeness are not established.",
                      label_provenance="meta_model and meta_is_valid are publisher fields; no independent engine replay or quality validation performed.")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_dir", type=Path)
    args = parser.parse_args()
    output = {"scope": "Full table decoding and specified text/metadata checks, not engine replay or training validation",
              "corpora": {name: audit(args.dataset_dir / (name + "-catan-sft.parquet"), name)
                          for name in ["g8967", "vvantim"]}}
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

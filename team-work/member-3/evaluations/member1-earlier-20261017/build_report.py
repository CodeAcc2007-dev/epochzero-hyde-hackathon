#!/usr/bin/env python3
"""Render a report from completed immutable match records, without playing games."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parent

def main():
    batch=json.loads((BASE/"batch-status.json").read_text())
    assert batch["status"]=="completed"
    inventory=json.loads((BASE/"source-inventory.json").read_text())
    originals={Path(i["path"]).stem:i for i in inventory}
    for i in inventory:
        assert hashlib.sha256((ROOT/i["path"]).read_bytes()).hexdigest()==i["sha256"]
    rows=[]
    for name in [*originals,"B05","B06"]:
        folder=BASE/"main"/name
        meta=json.loads((folder/"metadata.json").read_text())
        summary=json.loads((folder/"summary.json").read_text())
        games=json.loads((folder/"games.json").read_text())
        assert meta["status"]=="completed" and summary["source_unchanged"]
        expected=originals[name]['path'] if name in originals else f'team-work/member-3/bots/{name}/v003/agent.py'
        assert meta['a']['entrypoint']==expected
        for source, digest in meta['a']['files'].items():
            assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==digest
        if name in originals:
            assert meta['a']['files'][expected]==originals[name]['sha256']
        assert len(games)==400
        assert [r["board_seed"] for r in games]==[871000+i//2 for i in range(400)]
        assert [r["game"] for r in games]==list(range(400))
        assert sum(r["a_first"] for r in games)==200
        a=summary["a"]
        assert a["wins"]==sum(r["winner"]=="a" for r in games)
        assert a["games"]==len(games)
        row={"name":name,"group":"Member 1 earlier" if name in originals else "Pranesh reference",
             **a,"paired_bootstrap_95_descriptive":summary["uncertainty"]["pair_bootstrap_95_descriptive"],
             "first_seat_wins":summary["seat_a_first"]["wins"],
             "second_seat_wins":summary["seat_a_second"]["wins"],
             "f_health":{key:summary['b'][key] for key in ('games_over_budget','random_moves','errors','timeouts','crashes')},
             "wall_elapsed_s":summary["wall_elapsed_s"]}
        rows.append(row)
    earlier=sorted([r for r in rows if r["name"] in originals],key=lambda r:-r["win_rate"])
    controls=[r for r in rows if r["name"] not in originals]
    diagnostics=json.loads((BASE/"internal-fallback-diagnostics.json").read_text())
    assert len(diagnostics)==7 and all(d["exit_code"]==0 for d in diagnostics)
    lines=["# Member 1 earlier bots: independent evaluation results", "",
           "Completed "+datetime.now(timezone.utc).isoformat()+". Primary ran and verified all games. Originals preserved unchanged; no bot fixes, strategy tuning, SSH, event submission or GitHub upload performed in this evaluation.","",
           "## Results against organizer F", "",
           "Each row is 400 main games on the same 200 boards (871000–871199), once from each seat. Member 1 rows are sorted by observed wins. B05/B06 were rerun on this exact set as references; these are not their previous 1,000-game results.","",
           "| Bot | Wins / 400 | Win rate | Descriptive paired bootstrap 95% range | Mean CPU/game | Worst CPU/game | Clock overruns | Errors / timeouts / crashes | Harness random moves |",
           "| --- | ---: | ---: | --- | ---: | ---: | ---: | --- | ---: |"]
    for r in earlier+controls:
        lo,hi=r["paired_bootstrap_95_descriptive"]
        lines.append(f"| [{r['name']}](main/{r['name']}/summary.json) | {r['wins']} | {r['win_rate']:.2%} | {lo:.2%}–{hi:.2%} | {1000*r['mean_cpu_s']:.1f} ms | {1000*r['worst_cpu_s']:.0f} ms | {r['games_over_budget']} | {r['errors']} / {r['timeouts']} / {r['crashes']} | {r['random_moves']} |")
    f_issues={r['name']:r['f_health'] for r in rows if any(r['f_health'].values())}
    lines += ["", "F health: "+(json.dumps(f_issues) if f_issues else "zero clock overruns, harness random fallback moves, errors, timeouts and crashes in all nine main comparisons.")+"", "", "Ranges are descriptive board-pair bootstrap intervals from 2,000 resamples. Timing and process-persistent RNG/adaptive estimates affect repeatability and independence; these are not a private-score guarantee or multiple-comparison-adjusted winner test. No-winner counts: "+", ".join(f"{r['name']}={r['no_winner']}" for r in rows)+".","",
              "## Interpretation and next review", "",
              f"Best observed Member 1 version on this set: **{earlier[0]['name']}**, {earlier[0]['wins']}/400 ({earlier[0]['win_rate']:.1%}). This is selection on the evaluated boards, not independent confirmation. Preserve this exact source hash as an anchor; a revised candidate needs a new version and fresh confirmation boards.","",
              "The leading earlier versions' descriptive ranges include 50%; none establishes an advantage over F here. Retain greedy v3 as a cheap F-level control, and greedy v4 as an unconfirmed search candidate. Its observed gain over v3 is 1.75 percentage points for about 3.77 times the CPU. See [review for Aroosh](REVIEW-FOR-AROOSH.md) for evidence-linked follow-up points; no fixes were implemented.","",
              "F-relative results do not establish direct head-to-head results between candidates. No cross-bot round robin, private O test, event scoring or scorer-hardware timing was run. Use this table to choose which frozen versions merit the next independent round; no claim of final submission readiness.","",
              "All seven candidates swallow some exceptions and can return random legal moves. Thus zero harness errors/random moves does not prove every strategy decision succeeded. The separate diagnostic below measures some such events without contaminating the original-code main benchmark.","",
              "## Internal fallback diagnostics", "",
              "Separate instrumented four-game checks per bot, boards 870500–870501. The original source is imported unchanged; an RNG proxy records calls from source-verified exception-return lines. These checks alter execution overhead and are not used for strength or timing ranking. Zero observed occurrences is limited to these checks. Raw stderr logs and wrappers remain under shared-local/.","",
              "| Bot | Diagnostic decisions | Observed caught-exception random fallbacks | Exception details |",
              "| --- | ---: | ---: | --- |"]
    for d in diagnostics:
        detail="; ".join(f"{e['type']} at line {e['line']}: {e['message']} ({e['count']})" for e in d["exceptions"]) or "None observed"
        lines.append(f"| {d['bot']} | {d.get('diagnostic_decisions','unknown')} | {d['observed_internal_exception_fallbacks']} | {detail} |")
    lines += ["", "All seven fallback detectors also passed an intentional positive control: a synthetic observation raises a known diagnostic RuntimeError and each detector records exactly one fallback. These injected probe exceptions are not actual game faults. Evidence: [fallback-detector-positive-control.json](fallback-detector-positive-control.json). No such fallbacks were observed in the separate four-game checks (1,377 decisions total); this does not prove absence across the main benchmark.", "", "## Seat balance", "", "| Bot | Wins when first / 200 | Wins when second / 200 |", "| --- | ---: | ---: |"]
    for r in earlier+controls:
        lines.append(f"| {r['name']} | {r['first_seat_wins']} | {r['second_seat_wins']} |")
    lines += ["", "## Method, provenance and reproduction", "",
              "- Existing shared Python environment; pinned organizer kit `04fffac90e00610f60e0b06d919f262f4b3ed9db`, engine `d3f4ad05bb78d8b2309631d6d3cfa8fcb6fda816`.",
              "- Unchanged `match.play_chunk`, `evaluate.summarise`, F and observation masking. Byte verification: [harness-verification.json](harness-verification.json). Ten VP, both clocks active: 300 ms + 12.5 ms per decision, maximum 1.5 s per game.",
              "- Public local dice key. Agents receive masked observations. Both processes reload every 20 games with global indices retained; this differs from one uninterrupted official CLI run.",
              "- Default candidate configuration: `W` and `OPP` unset. No optional CONTENDER/OPP sweep. No parallel matches. CPU is measured by the official harness; peak memory and event scorer hardware were not measured.",
              "- Original filenames retained; no unsupported assignment of these earlier files to B01/B02. All source hashes rechecked after the batch and diagnostics. Every game's loss/fault/outcome retained.",
              "- Seven 12-game smoke checks, nine 400-game main comparisons including B05/B06, and seven separate four-game diagnostics. Total retained games: 3,712.",
              "- [Source inventory](source-inventory.json), [source review](SOURCE-REVIEW.md), [evaluation plan](PLAN.md), [batch status](batch-status.json), [internal fallback diagnostic records](internal-fallback-diagnostics.json), [Hyde junior review](HYDE-REVIEW.md). Hyde timed out with no accepted output; primary completed the review and verification.",
              "- Main records: `main/<name>/games.json`, `summary.json`, `metadata.json`; smoke records: `smoke/<name>/`; diagnostic records: `diagnostics/<name>/`. Metadata includes commands, code hashes and lifecycle. Local process stdout/stderr logs are not publication artifacts.","",
              "Reproduction uses `python3 team-work/member-3/evaluations/member1-earlier-20261017/run_batch.py`. Existing output directories intentionally cannot be overwritten: copy the driver and source inventory into a new sibling evaluation directory before a repeat. Use fresh seeds for new confirmation; these boards are now seen. `run_diagnostics.py` runs the separate fallback check after batch completion.","",
              "No implementation changes were made to any supplied bot.",""]
    (BASE/"RESULTS.md").write_text("\n".join(lines))
    (BASE/"comparison.json").write_text(json.dumps({"sources_unchanged":True,"rows":earlier+controls},indent=2)+"\n")
    print(json.dumps({"report":str(BASE/"RESULTS.md"),"rows":[{"name":r["name"],"wins":r["wins"],"rate":r["win_rate"]} for r in earlier+controls]},indent=2))
if __name__=="__main__":main()

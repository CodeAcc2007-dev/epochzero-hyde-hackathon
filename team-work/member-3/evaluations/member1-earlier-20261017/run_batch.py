#!/usr/bin/env python3
"""External evaluation orchestration only; never imported by competition agents."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent

def main():
    inventory = json.loads((BASE / "source-inventory.json").read_text())
    for item in inventory:
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    candidates = [(Path(item["path"]).stem, item["path"]) for item in inventory]
    controls = [(bot, f"team-work/member-3/bots/{bot}/v003/agent.py") for bot in ("B05", "B06")]
    env = os.environ.copy()
    # The v3 candidate accepts optional configuration; test its documented defaults.
    env.pop("W", None)
    env.pop("OPP", None)
    status = {"started_utc": datetime.now(timezone.utc).isoformat(), "status": "running", "runs": [],
              "configuration": {"W": "unset (DEFAULT_WEIGHTS)", "OPP": "unset (0)",
              "main_games_per_bot": 400, "main_seed0": 871000, "smoke_games_per_bot": 12,
              "smoke_seed0": 870000, "chunk_size": 20}}
    def save():
        (BASE/"batch-status.json").write_text(json.dumps(status, indent=2)+"\n")
    save()
    for stage, entries, games, seed in [("smoke", candidates, 12, 870000),
                                       ("main", candidates+controls, 400, 871000)]:
        for name, entry in entries:
            if stage == "main" and name not in ("B05", "B06"):
                smoke = next(r for r in status["runs"] if r["stage"]=="smoke" and r["name"]==name)
                if smoke["exit_code"] != 0:
                    status["runs"].append({"stage":stage,"name":name,"status":"skipped_load_failure"})
                    save()
                    continue
            out = BASE/stage/name
            out.parent.mkdir(parents=True, exist_ok=True)
            log = BASE/f"{stage}-{name}.txt"
            command = [str(ROOT/"team-work/run-python.sh"),
                       "team-work/member-3/implementation/run_comparison.py", "--a",entry,
                       "--b","shared-local/organizer-kit/examples/f_agent.py", "--games",str(games),
                       "--seed0",str(seed),"--out",str(out.relative_to(ROOT))]
            print(json.dumps({"event":"starting","stage":stage,"name":name,"games":games}), flush=True)
            with log.open("w") as stream:
                result = subprocess.run(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
            record = {"stage":stage,"name":name,"exit_code":result.returncode,"log":log.name,
                      "output":str(out.relative_to(BASE))}
            if result.returncode == 0:
                record["metrics"] = json.loads((out/"summary.json").read_text())["a"]
            status["runs"].append(record)
            save()
            print(json.dumps({"event":"finished",**record}), flush=True)
    for item in inventory:
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    status.update(status="completed", sources_unchanged=True, completed_utc=datetime.now(timezone.utc).isoformat())
    save()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Run-time table for a Forsmark campaign folder (one row per run directory), built
from what each run leaves on disk, so it works for runs already finished:

  start          single_stage.in written (the case script writes it just before PFLOTRAN starts)
  pflotran_end   last write of pflotran.stdout
  post_end       last write of patterns.csv / probes.log (pattern analysis and breakthrough probes)
  wall_pflotran  PFLOTRAN's own "Wall Clock Time" from single_stage.out (seconds)
  wall_total     post_end - start (seconds), the whole queue job
  steps          last transport step number

  python3 forsmark_reactive/run_times.py forsmark_reactive/phase1      -> phase1/run_times.csv + summary

Running runs get status "running", their model time so far and a projected PFLOTRAN finish
(linear in model time, which holds for these runs: dt sits at the 0.57 tau cap almost throughout).
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

STEP = re.compile(rb"Step +(\d+) Time= +([0-9.E+-]+)")


def last_step(stdout: Path):
    with open(stdout, "rb") as f:
        f.seek(0, 2)
        f.seek(max(0, f.tell() - 20000))
        hits = STEP.findall(f.read())
    return (int(hits[-1][0]), float(hits[-1][1])) if hits else (0, 0.0)


def row(run: Path):
    net = run.parent
    deck, out, stdout = run / "single_stage.in", run / "single_stage.out", run / "pflotran.stdout"
    if not (deck.exists() and stdout.exists()):
        return None
    sched = json.loads((run / "single_stage.in.schedule.json").read_text()) if (run / "single_stage.in.schedule.json").exists() else {}
    stats = json.loads((net / "network_stats.json").read_text()) if (net / "network_stats.json").exists() else {}
    m = re.search(r"p([\d.]+)_sg([\d.]+)_seed(\d+)", net.name)
    start = deck.stat().st_mtime
    wall = None
    if out.exists():
        w = re.search(r"Wall Clock Time:\s+([0-9.E+-]+) \[sec\]", out.read_text(errors="ignore")[-4000:])
        wall = float(w.group(1)) if w else None
    steps, t_model = last_step(stdout)
    t_end = sched.get("final_time_y")
    post = [p.stat().st_mtime for p in (run / "patterns.csv", run / "probes.log") if p.exists()]
    status = "done" if wall is not None and post else ("post" if wall is not None else "running")
    if status == "running" and time.time() - stdout.stat().st_mtime > 900:   # no output for 15 min and no wall time: killed or crashed
        status = "dead"
    r = dict(net=net.name, mode="gypcal" if "calcite" in run.name else "gyponly",
             p32_scale=float(m[1]) if m else None, sigma=float(m[2]) if m else None, seed=int(m[3]) if m else None,
             cells=stats.get("graph_nodes"), connections=stats.get("graph_edges"), n_fractures=stats.get("n_fractures"),
             status=status, start=datetime.fromtimestamp(start).strftime("%a %H:%M"),
             steps=steps, t_model_y=t_model, t_end_y=t_end, wall_pflotran_s=wall,
             wall_total_s=(max(post) - start) if status == "done" else None)
    if status == "running" and t_model > 0 and t_end:
        el = time.time() - start
        r["elapsed_s"] = el
        r["projected_pflotran_s"] = el * t_end / t_model
    return r


def main(campaign: Path):
    rows = [r for r in (row(d) for d in sorted(campaign.glob("*/gyp*__*"))) if r]
    df = pd.DataFrame(rows)
    df.to_csv(campaign / "run_times.csv", index=False)
    done = df[df.status == "done"]
    pd.set_option("display.width", 200)
    if len(done):
        g = done.groupby(["p32_scale", "mode"]).agg(n=("net", "size"), cells=("cells", "median"),
                                                    pflotran_min=("wall_pflotran_s", lambda s: s.median() / 60),
                                                    total_min=("wall_total_s", lambda s: s.median() / 60))
        print("finished runs, medians:\n" + g.round(1).to_string())
    run = df[df.status.isin(["running", "post"])]
    if len(run):
        cols = ["net", "mode", "status", "start", "t_model_y", "t_end_y", "elapsed_s", "projected_pflotran_s"]
        print("\nin progress:\n" + run[[c for c in cols if c in run]].round(0).to_string(index=False))
    print(f"\n{len(done)} done, {len(run)} in progress, {(df.status == 'dead').sum()} dead; table: {campaign / 'run_times.csv'}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))

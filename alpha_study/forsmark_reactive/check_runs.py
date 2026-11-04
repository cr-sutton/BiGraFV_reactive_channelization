#!/usr/bin/env python3
"""
Health check for a Forsmark campaign queue, meant to be run every ~30-60 min.
Compares each run with the previous check (CAMPAIGN/check_state.json) and flags:

  STALLED   running, model time has not advanced since the last check
  SLOW      running, last 200 steps have dt < 1 % of the cap (time step collapsed) or the
            projected PFLOTRAN time exceeds --limit-h
  ERROR     pflotran.stdout has ERROR / NaN / "KILLED by memory guard" / "Stopping"
  DIED      no running PFLOTRAN for that directory and no "Wall Clock Time" in single_stage.out
  NO_POST   PFLOTRAN finished > 15 min ago but patterns.csv was not written

  python3 forsmark_reactive/check_runs.py forsmark_reactive/phase1 [--limit-h 6]
Exit status 0 = all healthy, 1 = something flagged.  Appends one line per check to CAMPAIGN/check_log.txt.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from pathlib import Path

STEP = re.compile(rb"Step +(\d+) Time= +([0-9.E+-]+) Dt= +([0-9.E+-]+)")
BAD = re.compile(rb"ERROR|NaN|KILLED by memory guard|Stopping!|Time step cut criteria exceeded|Max Time Step Cuts", re.I)


def tail(f: Path, n=60000):
    with open(f, "rb") as fh:
        fh.seek(0, 2)
        fh.seek(max(0, fh.tell() - n))
        return fh.read()


def running_dirs():
    """Working directories of live pflotran single_stage runs (lsof cwd)."""
    pids = subprocess.run(["pgrep", "-f", "pflotran -pflotranin single_stage.in"], capture_output=True, text=True).stdout.split()
    dirs = {}
    for p in pids:
        out = subprocess.run(["lsof", "-a", "-p", p, "-d", "cwd", "-Fn"], capture_output=True, text=True).stdout
        st = subprocess.run(["ps", "-o", "stat=", "-p", p], capture_output=True, text=True).stdout.strip()
        for line in out.splitlines():
            if line.startswith("n"):
                dirs.setdefault(line[1:], set()).add(st[:1])
    return dirs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("campaign", type=Path)
    ap.add_argument("--limit-h", type=float, default=6.0)
    a = ap.parse_args()
    state_f = a.campaign / "check_state.json"
    prev = json.loads(state_f.read_text()) if state_f.exists() else {}
    live = running_dirs()
    ack_f = a.campaign / "acknowledged.txt"   # runs already looked at (one key per line, see INTERVENTIONS.md): not re-flagged
    ack = {l.split()[0] for l in ack_f.read_text().splitlines() if l.strip() and not l.startswith("#")} if ack_f.exists() else set()
    now, state, flags, n_run, n_done = time.time(), {}, [], 0, 0
    for run in sorted(a.campaign.glob("*/gyp*__*")):
        so, out, sch = run / "pflotran.stdout", run / "single_stage.out", run / "single_stage.in.schedule.json"
        if not (so.exists() and sch.exists()):
            continue
        key = f"{run.parent.name}/{run.name}"
        t_end = json.loads(sch.read_text())["final_time_y"]
        dt_cap = json.loads(sch.read_text()).get("dt_max_y")
        tl = tail(so)
        steps = STEP.findall(tl)
        step, t, dt = (int(steps[-1][0]), float(steps[-1][1]), float(steps[-1][2])) if steps else (0, 0.0, 0.0)
        finished = out.exists() and b"Wall Clock Time" in tail(out, 6000)
        is_live = str(run.resolve()) in live
        state[key] = dict(t=t, step=step, at=now)
        if key in ack:
            n_done += finished
            continue
        if BAD.search(tl):
            flags.append(f"ERROR   {key}: {BAD.search(tl).group(0).decode()} at t={t:.4g} y step {step}")
        if finished:
            n_done += 1
            if not (run / "patterns.csv").exists() and now - so.stat().st_mtime > 900:
                flags.append(f"NO_POST {key}: PFLOTRAN done, no patterns.csv")
            continue
        if not is_live:
            flags.append(f"DIED    {key}: no live PFLOTRAN, stopped at t={t:.4g} of {t_end:.4g} y, step {step}")
            continue
        if "T" in live[str(run.resolve())]:
            flags.append(f"PAUSED  {key}: process is stopped (SIGSTOP), t={t:.4g} y")
        n_run += 1
        p = prev.get(key)
        if p and t <= p["t"] and step >= p["step"] and now - p["at"] > 300:   # lower step = run restarted, not stalled
            flags.append(f"STALLED {key}: t={t:.4g} y unchanged since {time.strftime('%H:%M', time.localtime(p['at']))} (step {p['step']} -> {step})")
        recent = [float(s[2]) for s in steps[-200:]]
        if dt_cap and len(recent) >= 200 and max(recent) < 0.01 * dt_cap:
            flags.append(f"SLOW    {key}: dt collapsed (max of last 200 steps {max(recent):.2e} y vs cap {dt_cap:.2g}) at t={t:.4g} y")
        start = (run / "single_stage.in").stat().st_mtime
        if t > 0 and (now - start) * t_end / t / 3600 > a.limit_h and now - start > 1800:
            flags.append(f"SLOW    {key}: projected {(now - start) * t_end / t / 3600:.1f} h > {a.limit_h} h (t={t:.4g} of {t_end:.4g} y)")
    import shutil
    free_gb = shutil.disk_usage(a.campaign).free / 1e9
    if free_gb < 25:   # 3 Nov 02:10: macOS update staging filled the disk and killed 12 runs
        flags.append(f"DISK    only {free_gb:.0f} GB free")
    state_f.write_text(json.dumps(state))
    line = f"{time.strftime('%a %H:%M')} done {n_done} running {n_run} flags {len(flags)}"
    with open(a.campaign / "check_log.txt", "a") as f:
        f.write(line + "".join("\n    " + x for x in flags) + "\n")
    print(line)
    for x in flags:
        print("  " + x)
    raise SystemExit(1 if flags else 0)


if __name__ == "__main__":
    main()

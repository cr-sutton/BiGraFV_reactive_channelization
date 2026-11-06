#!/usr/bin/env python3
"""Queue runner for the ceiling sweep (6 Nov 2026), from run_scripts/run_km_queue.py with two changes:
  - shares the machine with the 2 km queue: runs at most TOTAL - (2 km chains still running) at a time, so it uses
    1-2 slots until the 2 km queue drains and TOTAL after;
  - chain = case script, pattern analysis, channelization (no tracer probes: not needed for depth / events).
  python3 forsmark_reactive/ceilsweep/run_queue_ceilsweep.py forsmark_reactive/ceilsweep/run_list_ceilsweep.txt 7"""
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]                    # alpha_study
RS, KM = ROOT / "run_scripts", ROOT / "km_scale_graph_only"
sys.path.insert(0, str(ROOT))
from run_names import run_dir_name  # noqa: E402
jobs = [shlex.split(l) for l in Path(sys.argv[1]).read_text().splitlines() if l.strip() and not l.startswith("#")]
TOTAL = int(sys.argv[2])
running = []


def other_chains():
    ps = subprocess.run(["ps", "-Ao", "command"], capture_output=True, text=True).stdout.splitlines()
    return sum(1 for c in ps if c.startswith("/bin/zsh -c") and "scale2km/L2_" in c and "analyze_km_dissolution_patterns" in c)


def start(j):
    net, model, mode, tag, dtf, ccap, extra = j
    rd = f"{KM}/{net}/{run_dir_name(mode, model, tag)}"
    cmd = (f"{RS}/{os.environ.get('CASE_SCRIPT', 'run_km_graph_case.sh')} {KM}/{net} {model} {mode} {tag} '{extra}' {dtf} 60 "
           f"{ccap if ccap != '-' else ''} && "
           f"python3 {ROOT}/analyze_km_dissolution_patterns.py {rd} > {rd}/patterns.log 2>&1; "
           f"python3 {ROOT}/analyze_channelization.py {rd} > {rd}/channelization.log 2>&1")
    print(time.strftime("%a %H:%M"), "start", " ".join(j[:4]), flush=True)
    return subprocess.Popen(cmd, shell=True, executable="/bin/zsh")


while jobs or running:
    running = [p for p in running if p.poll() is None]
    while jobs and len(running) < max(1, TOTAL - other_chains()):
        running.append(start(jobs.pop(0)))
    time.sleep(60)
print(time.strftime("%a %H:%M"), "queue done", flush=True)

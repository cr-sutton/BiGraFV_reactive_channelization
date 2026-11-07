#!/usr/bin/env python3
"""Queue runner for the gap-filling runs (7 Nov 2026), from ceilsweep/run_queue_ceilsweep.py.  Chain per job: case
script, pattern analysis, channelization; jobs marked probe0 also get the start-of-run tracer probe (snap_0, same probe
settings as Phase 1 and 2 km).  TOTAL chains at a time.
  python3 forsmark_reactive/gapfill/run_queue_gapfill.py forsmark_reactive/gapfill/run_list_gapfill.txt 7"""
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RS, KM = ROOT / "run_scripts", ROOT / "km_scale_graph_only"
sys.path.insert(0, str(ROOT))
from run_names import run_dir_name  # noqa: E402
jobs = [shlex.split(l) for l in Path(sys.argv[1]).read_text().splitlines() if l.strip() and not l.startswith("#")]
TOTAL = int(sys.argv[2])
running = []


def start(j):
    net, model, mode, tag, dtf, ccap, extra, *flags = j
    rd = f"{KM}/{net}/{run_dir_name(mode, model, tag)}"
    cmd = (f"{RS}/{os.environ.get('CASE_SCRIPT', 'run_km_graph_case.sh')} {KM}/{net} {model} {mode} {tag} '{extra}' {dtf} 60 "
           f"{ccap if ccap != '-' else ''} && "
           f"python3 {ROOT}/analyze_km_dissolution_patterns.py {rd} > {rd}/patterns.log 2>&1; "
           f"python3 {ROOT}/analyze_channelization.py {rd} > {rd}/channelization.log 2>&1")
    if "probe0" in flags:
        cmd += (f"; python3 {ROOT}/probe_frozen_state_tracer.py setup {rd} --states 0 > /dev/null && "
                f"python3 {ROOT}/probe_frozen_state_tracer.py run {rd} --np ${{NP:-1}} > {rd}/probes.log 2>&1")
    print(time.strftime("%a %H:%M"), "start", " ".join(j[:4]), flush=True)
    return subprocess.Popen(cmd, shell=True, executable="/bin/zsh")


while jobs or running:
    running = [p for p in running if p.poll() is None]
    while jobs and len(running) < TOTAL:
        running.append(start(jobs.pop(0)))
    time.sleep(60)
print(time.strftime("%a %H:%M"), "queue done", flush=True)

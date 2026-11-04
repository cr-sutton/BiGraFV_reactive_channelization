#!/usr/bin/env python3
"""Run the km-scale reactive runs from a queue file, MAX at a time, each
followed by its pattern analysis.  Lines: NET MODEL MODE TAG DTFAC CCAP "EXTRA".
  python3 run_scripts/run_km_queue.py km_scale_graph_only/queue.txt 2"""
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent            # run_scripts/
ROOT = HERE.parent
KM = ROOT / "km_scale_graph_only"                               # network folders live here
sys.path.insert(0, str(ROOT))
from run_names import run_dir_name  # noqa: E402
jobs = [shlex.split(l) for l in Path(sys.argv[1]).read_text().splitlines() if l.strip() and not l.startswith("#")]
MAX = int(sys.argv[2])
running = []


def start(j):
    net, model, mode, tag, dtf, ccap, extra = j
    cmd = (f"{HERE}/{os.environ.get('CASE_SCRIPT', 'run_km_graph_case.sh')} {KM}/{net} {model} {mode} {tag} '{extra}' {dtf} 60 {ccap if ccap != '-' else ''} && "
           f"python3 {ROOT}/analyze_km_dissolution_patterns.py {KM}/{net}/{run_dir_name(mode, model, tag)} > {KM}/{net}/{run_dir_name(mode, model, tag)}/patterns.log 2>&1; "
           f"python3 {ROOT}/probe_frozen_state_tracer.py setup {KM}/{net}/{run_dir_name(mode, model, tag)} "
           f"{'--states 0 11 -1' if mode == 'qtz' else '--checkpoints-only'} > /dev/null && "
           f"python3 {ROOT}/probe_frozen_state_tracer.py run {KM}/{net}/{run_dir_name(mode, model, tag)} --np ${{NP:-1}} > {KM}/{net}/{run_dir_name(mode, model, tag)}/probes.log 2>&1; "
           f"python3 {ROOT}/diagnose_damkohler_km_graph.py {KM}/{net}/{run_dir_name(mode, model, tag)} > /dev/null 2>&1")
    print(time.strftime("%a %H:%M"), "start", " ".join(j), flush=True)
    return subprocess.Popen(cmd, shell=True, executable="/bin/zsh")


while jobs or running:
    running = [p for p in running if p.poll() is None]
    while jobs and len(running) < MAX:
        running.append(start(jobs.pop(0)))
    time.sleep(30)
print(time.strftime("%a %H:%M"), "queue done", flush=True)

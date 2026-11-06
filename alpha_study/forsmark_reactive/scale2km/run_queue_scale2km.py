#!/usr/bin/env python3
"""
Queue runner for the 2 km scale test (5 Nov 2026).  Same chain as run_scripts/run_km_queue.py (case script, pattern
analysis, checkpoint tracer probes, Damkoehler diagnosis) plus analyze_channelization.py, with one change: the 2 km
networks share their folder names with the 1 km Phase 1 networks, so the per-fracture state files are written to
paraview/S2KM__<net>__<run> (analyze_km_dissolution_patterns.py --name) instead of paraview/<net>__<run>, which holds
the Phase 1 files.

The first 6 queue lines were started by run_km_queue.py at 13:32 without --name.  For those, after their pattern
analysis finishes, this runner moves paraview/<net>__<run> to paraview/S2KM__<net>__<run>, restores the Phase 1 copy
from _phase1_paraview_backup/ and runs analyze_channelization.py.  Those chains count against MAX while they run.

  python3 forsmark_reactive/scale2km/run_queue_scale2km.py forsmark_reactive/scale2km/run_list_scale2km.txt 6 6
"""
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent                 # forsmark_reactive/scale2km
ROOT = HERE.parents[1]                                 # alpha_study
RS = ROOT / "run_scripts"
KM = ROOT / "km_scale_graph_only"
PVD = ROOT / "paraview"
BACKUP = HERE / "_phase1_paraview_backup"
sys.path.insert(0, str(ROOT))
from run_names import run_dir_name  # noqa: E402

lines = [shlex.split(l) for l in Path(sys.argv[1]).read_text().splitlines() if l.strip() and not l.startswith("#")]
MAX, SKIP = int(sys.argv[2]), int(sys.argv[3])
old, jobs = lines[:SKIP], lines[SKIP:]
pending_fix = []
for net, model, mode, tag, *_ in old:
    rd = (KM / net).resolve() / run_dir_name(mode, model, tag)
    pending_fix.append(rd)


def log(*a):
    print(time.strftime("%a %H:%M"), *a, flush=True)


def old_chains_alive():
    ps = subprocess.run(["ps", "-Ao", "command"], capture_output=True, text=True).stdout.splitlines()
    return sum(1 for c in ps if c.startswith("/bin/zsh -c") and "scale2km/L2" in c and "analyze_km_dissolution_patterns" in c
               and "S2KM__" not in c)


def fix_old():
    for rd in list(pending_fix):
        if not (rd / "patterns.csv").exists():
            continue
        if time.time() - (rd / "patterns.csv").stat().st_mtime < 60:       # let the pattern analysis close its files
            continue
        name = f"{rd.parent.name}__{rd.name}"
        src, dst = PVD / name, PVD / f"S2KM__{name}"
        if src.exists() and not dst.exists():
            shutil.move(str(src), str(dst))
            t0 = (rd / "single_stage.in").stat().st_mtime        # the pattern script does not clear its folder:
            for f in dst.iterdir():   # drop Phase 1 files the 2 km run did not overwrite (it saves every 4th state on big nets)
                if f.stat().st_mtime < t0:
                    f.unlink()
                    log("removed leftover Phase 1 file", f.name)
            if (BACKUP / name).exists():
                shutil.copytree(BACKUP / name, src)
                log("fixed", name, "-> S2KM__, Phase 1 copy restored")
            else:
                log("fixed", name, "-> S2KM__ (no backup: Phase 1 copy regenerated earlier)")
        if not (rd / "channelization.log").exists():
            subprocess.Popen(f"python3 {ROOT}/analyze_channelization.py {rd} > {rd}/channelization.log 2>&1", shell=True,
                             executable="/bin/zsh")
        pending_fix.remove(rd)


def start(j):
    net, model, mode, tag, dtf, ccap, extra = j
    rd = f"{KM}/{net}/{run_dir_name(mode, model, tag)}"
    name = f"S2KM__{Path(net).name}__{run_dir_name(mode, model, tag)}"
    cmd = (f"{RS}/{os.environ.get('CASE_SCRIPT', 'run_km_graph_case.sh')} {KM}/{net} {model} {mode} {tag} '{extra}' {dtf} 60 "
           f"{ccap if ccap != '-' else ''} && "
           f"python3 {ROOT}/analyze_km_dissolution_patterns.py {rd} --name {name} > {rd}/patterns.log 2>&1; "
           f"python3 {ROOT}/analyze_channelization.py {rd} > {rd}/channelization.log 2>&1; "
           f"python3 {ROOT}/probe_frozen_state_tracer.py setup {rd} --checkpoints-only > /dev/null && "
           f"python3 {ROOT}/probe_frozen_state_tracer.py run {rd} --np ${{NP:-1}} > {rd}/probes.log 2>&1; "
           f"python3 {ROOT}/diagnose_damkohler_km_graph.py {rd} > /dev/null 2>&1")
    log("start", " ".join(j[:4]))
    return subprocess.Popen(cmd, shell=True, executable="/bin/zsh")


running = []
while jobs or running or pending_fix:
    fix_old()
    running = [p for p in running if p.poll() is None]
    while jobs and len(running) + old_chains_alive() < MAX:
        running.append(start(jobs.pop(0)))
    time.sleep(30)
log("queue done")

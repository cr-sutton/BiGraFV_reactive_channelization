#!/bin/zsh
# Phase 3 queue, 5 Nov 2026: ceiling test (porosity 0.182) and rate test (x0.1, x10): 6 runs at a time, 2 MPI ranks each. EXFIX outlet fix is the default
# in run_km_graph_case_hyman.sh. PROBE_FEW_ABOVE raised so the 78k-cell x16 networks get tracer probes at every checkpoint.
cd ${0:A:h}/../..
export CASE_SCRIPT=run_km_graph_case_hyman.sh DIRECT=0 NP=2 STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" \
       PROBE_PULSE=0.1 PROBE_WINDOW=10 PROBE_DT=0.05 PROBE_FEW_ABOVE=200000 MEM_FREE_MIN=15
python3 run_scripts/run_km_queue.py forsmark_reactive/phase1/run_list_phase3.txt 6

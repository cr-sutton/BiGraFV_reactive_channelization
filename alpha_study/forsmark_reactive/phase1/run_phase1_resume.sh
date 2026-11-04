#!/bin/zsh
# Phase 1 queue: 6 runs at a time, 2 MPI ranks each (12 of 14 cores). Environment as km_scale_graph_only/RUN_ENVIRONMENT.md;
# PROBE_FEW_ABOVE raised to 30000 so every network (max 22.9k cells) gets breakthrough probes at all checkpoints.
cd ${0:A:h}/../..
export CASE_SCRIPT=run_km_graph_case_hyman.sh DIRECT=0 NP=2 STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" \
       PROBE_PULSE=0.1 PROBE_WINDOW=10 PROBE_DT=0.05 PROBE_FEW_ABOVE=30000 MEM_FREE_MIN=15
python3 run_scripts/run_km_queue.py forsmark_reactive/phase1/run_list_phase1_resume.txt 5

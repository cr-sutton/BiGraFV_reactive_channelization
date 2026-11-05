#!/bin/zsh
# DFN validation stage 0 (5 Nov 2026): one-cell gyponly + gypcal on the rFram x4 sigma 1 seed 1 graph, Phase 1 settings (run_phase1_exfix.sh env).
cd ${0:A:h}/../..
export CASE_SCRIPT=run_km_graph_case_hyman.sh DIRECT=0 NP=2 EXFIX="--area-per-dist 1e-2" STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" \
       PROBE_PULSE=0.1 PROBE_WINDOW=10 PROBE_DT=0.05 PROBE_FEW_ABOVE=30000 MEM_FREE_MIN=15
python3 run_scripts/run_km_queue.py forsmark_reactive/dfn_validation/run_list_gate.txt 2

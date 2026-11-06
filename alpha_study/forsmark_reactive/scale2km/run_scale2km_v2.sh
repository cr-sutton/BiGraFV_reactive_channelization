#!/bin/zsh
# 2 km scale test queue, v2 (5 Nov 2026 14:15): run_queue_scale2km.py writes per-fracture states to paraview/S2KM__*
# so the Phase 1 files are not overwritten. Same environment as phase1/run_overnight.sh; skips the 6 runs v1 started.
cd ${0:A:h}/../..
export CASE_SCRIPT=run_km_graph_case_hyman.sh DIRECT=0 NP=2 STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" \
       PROBE_PULSE=0.1 PROBE_WINDOW=10 PROBE_DT=0.05 PROBE_FEW_ABOVE=200000 MEM_FREE_MIN=15
python3 forsmark_reactive/scale2km/run_queue_scale2km.py forsmark_reactive/scale2km/run_list_scale2km.txt 6 6

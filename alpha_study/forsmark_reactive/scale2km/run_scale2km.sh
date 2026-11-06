#!/bin/zsh
# Scale-up test queue (5 Nov 2026, make_queue_scale2km.py): same environment as phase1/run_overnight.sh,
# 6 runs at a time, 2 MPI ranks each. Waits for build_all.log to report ALL_BUILT.
cd ${0:A:h}
until grep -q ALL_BUILT build_all.log 2>/dev/null; do sleep 20; done
cd ${0:A:h}/../..
export CASE_SCRIPT=run_km_graph_case_hyman.sh DIRECT=0 NP=2 STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" \
       PROBE_PULSE=0.1 PROBE_WINDOW=10 PROBE_DT=0.05 PROBE_FEW_ABOVE=200000 MEM_FREE_MIN=15
python3 run_scripts/run_km_queue.py forsmark_reactive/scale2km/run_list_scale2km.txt 6

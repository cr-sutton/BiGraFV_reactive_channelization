#!/bin/zsh
# Length series queue (6 Nov 2026, LENGTH_SERIES.md). Same environment as scale2km/run_scale2km_v2.sh (Phase 1 settings).
# Not started automatically: launch only after the user's go.   zsh forsmark_reactive/lenseries/run_lenseries.sh [SLOTS]
cd ${0:A:h}/../..
export CASE_SCRIPT=run_km_graph_case_hyman.sh DIRECT=0 NP=2 STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" MEM_FREE_MIN=15
python3 forsmark_reactive/lenseries/run_queue_lenseries.py forsmark_reactive/lenseries/run_list_lenseries.txt ${1:-4} 0

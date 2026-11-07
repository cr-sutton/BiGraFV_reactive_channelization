#!/bin/zsh
# Gap-filling runs (GAPFILL.md). Same environment as scale2km/run_scale2km_v2.sh (Phase 1 settings, probe settings).
cd ${0:A:h}/../..
export CASE_SCRIPT=run_km_graph_case_hyman.sh DIRECT=0 NP=2 STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" \
       PROBE_PULSE=0.1 PROBE_WINDOW=10 PROBE_DT=0.05 PROBE_FEW_ABOVE=200000 MEM_FREE_MIN=15
python3 forsmark_reactive/gapfill/run_queue_gapfill.py forsmark_reactive/gapfill/run_list_gapfill.txt ${1:-7}
echo GAPFILL_DONE

#!/bin/zsh
# Ceiling sweep (CEILING_SWEEP.md). Same environment as phase1/run_kphi_e0.sh; up to 7 chains in total with the 2 km queue.
cd ${0:A:h}/../..
export CASE_SCRIPT=run_km_graph_case_hyman.sh DIRECT=0 NP=2 STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" MEM_FREE_MIN=15
python3 forsmark_reactive/ceilsweep/run_queue_ceilsweep.py forsmark_reactive/ceilsweep/run_list_ceilsweep.txt ${1:-7}
echo CEILSWEEP_DONE

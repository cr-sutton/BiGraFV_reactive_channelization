#!/bin/zsh
# run_retry.sh LIST [MAX]: re-run failed Phase 1 jobs from LIST (same line format and environment as run_phase1.sh).
# Used by the periodic checks; each retry list is kept beside its log (retry_*.txt / retry_*.log).
list=${1:A}; cd ${0:A:h}/../..
export CASE_SCRIPT=run_km_graph_case_hyman.sh DIRECT=${DIRECT:-0} NP=${NP:-2} EXFIX="${EXFIX:-}" STEADY_INIT=1 TS_ACCEL=10 STABILIZE="${STABILIZE:---dirichlet-outflow 2e5}" \
       PROBE_PULSE=0.1 PROBE_WINDOW=10 PROBE_DT=0.05 PROBE_FEW_ABOVE=30000 MEM_FREE_MIN=15
python3 run_scripts/run_km_queue.py $list ${2:-1}

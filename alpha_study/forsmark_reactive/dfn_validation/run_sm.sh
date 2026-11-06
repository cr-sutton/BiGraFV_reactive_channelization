#!/bin/zsh
# Exact-network BiGraFV pair (run_list_sm.txt): same environment as phase1/run_kphi_n3.sh, then channelization.
cd ${0:A:h}/../..
export CASE_SCRIPT=run_km_graph_case_hyman.sh DIRECT=0 NP=2 STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" \
       PROBE_PULSE=0.1 PROBE_WINDOW=10 PROBE_DT=0.05 PROBE_FEW_ABOVE=200000 MEM_FREE_MIN=15
python3 run_scripts/run_km_queue.py forsmark_reactive/dfn_validation/run_list_sm.txt 2
for r in forsmark_reactive/dfn_validation/sm500_r282_p6_s1/gyp*__sm; do python3 analyze_channelization.py $r > $r/channelization.log 2>&1; done
echo SM_DONE

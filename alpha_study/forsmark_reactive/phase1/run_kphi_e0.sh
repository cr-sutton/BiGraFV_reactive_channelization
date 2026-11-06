#!/bin/zsh
# k-phi shape pilot E0 (run_list_kphi_e0.txt): same environment as run_overnight.sh, 3 runs at a time, then channelization.
cd ${0:A:h}/../..
export CASE_SCRIPT=run_km_graph_case_hyman.sh DIRECT=0 NP=2 STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" \
       PROBE_PULSE=0.1 PROBE_WINDOW=10 PROBE_DT=0.05 PROBE_FEW_ABOVE=200000 MEM_FREE_MIN=15
python3 run_scripts/run_km_queue.py forsmark_reactive/phase1/run_list_kphi_e0.txt 3
for r in forsmark_reactive/phase1/L2_r15_p6.0_sg1.0_seed1/gypsum__*__kphiC10n*; do python3 analyze_channelization.py $r > $r/channelization.log 2>&1; done
echo KPHI_E0_DONE

#!/bin/zsh
# Finer tracer probes for one Phase 1 run (snapfine_k beside the original snap_k): steps of 0.005 residence times until 3
# residence times after the pulse, then 0.05; same pulse (0.1) and window (10) as the original probes.
cd ${0:A:h}/../..
export PROBE_PULSE=0.1 PROBE_WINDOW=10 PROBE_DT=0.05 PROBE_DT_FINE=0.005 PROBE_FINE_UNTIL=3 PROBE_DIR=snapfine PROBE_FEW_ABOVE=200000
python3 probe_frozen_state_tracer.py setup $1 --checkpoints-only > /dev/null && python3 probe_frozen_state_tracer.py run $1 --np 1 > $1/probes_fine.log 2>&1
echo "$1 $(grep -c ok $1/probes_fine.log)"

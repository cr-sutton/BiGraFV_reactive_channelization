#!/bin/zsh
# Wait for the seed 2-3 gate runs' patterns.csv, then channelization and the gate check.
cd ${0:A:h}/../..
D=forsmark_reactive/dfn_validation
for s in 2 3; do for m in gypsum gypsum_calcite; do until [ -f $D/rf_p4.0_sg1.0_seed$s/${m}__uncorrected_graph__dfnval/patterns.csv ]; do sleep 30; done; done; done
python3 analyze_channelization.py $D/rf_p4.0_sg1.0_seed{2,3}/gyp*__uncorrected_graph__dfnval 2>&1 | tail -4
for s in 2 3; do echo "== seed $s"; python3 $D/gate_check.py rf_p4.0_sg1.0_seed$s; done
date +%H:%M

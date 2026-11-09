#!/bin/zsh
# Reactive DFN on the 500 m trial network sm500_r282_p6_s1 (launched Mon 9 Nov 2026 on Collin's go). Same deck arguments as
# the graph runs in run_list_sm.txt (run_dfn_case.sh strips --inert-helper-cells); pass criteria fixed in sm500_compare.py.
# Gypsum-only (primary) on 6 ranks and coupled on 2, in parallel.
cd ${0:A:h}
export STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" EXFIX_DFN="--area 1e-6" MEM_FREE_MIN=15
COMMON="--k-gypsum-mult 21.95 --log-vtk --dissolved-fractions 0.02 0.05 0.1 0.25 0.5 0.75 1.0 1.5 2.0 --gypsum-vf0 0.9 --material-porosity 0.1"
( NP=6 zsh run_dfn_case.sh sm500_r282_p6_s1 gyponly sm "$COMMON --c-cap 16.5" 0.57 0; echo "$(date '+%a %H:%M') gyponly done" ) &
( NP=2 zsh run_dfn_case.sh sm500_r282_p6_s1 gypcal sm "$COMMON --c-cap 516.5 --inj-co3 0.5 --inj-ph 11.39 --well-fill-injection --initial-dt 1e-11 --calcite-fixed-area --min-porosity 1e-3 --perm-min-scale 1e-6 --inert-helper-cells" 0.57 0; echo "$(date '+%a %H:%M') gypcal done" ) &
wait
echo SM_DFN_DONE

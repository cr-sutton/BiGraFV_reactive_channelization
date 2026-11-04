#!/bin/zsh
# Phase 0 timing pilot: one gyponly + one gypcal run on forsmark_reactive/pilot/L2_r15_p6.0_s1_seed1 at one pore volume per year,
# phi0 0.1 (gypsum vf0 0.9), k-phi n = 1 (reference porosity 0.1), dt cap 0.57 tau.
# gypcal brine: Hyman et al. 2024 IJGGC Table 2 (0.5 M CO3, 1.0 M Na, pH 11.39); --c-cap 16.5 on both so the
# checkpoints sit at the same pore volumes injected (dissolved fraction of the gypsum-only capacity).
cd ${0:A:h}/../..
export DIRECT=0 NP=2 STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" MEM_FREE_MIN=15
run_scripts/run_km_graph_case_hyman.sh forsmark_reactive/pilot/L2_r15_p6.0_s1_seed1 graph_raw gyponly forsmark_pilot "--k-gypsum-mult 21.95 --gypsum-vf0 0.9 --material-porosity 0.1 --perm-power 1 --c-cap 16.5 --dissolved-fractions 0.02 0.05 0.1 0.25 0.5 0.75 1.0" 0.57 60 > forsmark_reactive/pilot/L2_r15_p6.0_s1_seed1.gyponly.log 2>&1 &
run_scripts/run_km_graph_case_hyman.sh forsmark_reactive/pilot/L2_r15_p6.0_s1_seed1 graph_raw gypcal forsmark_pilot "--k-gypsum-mult 21.95 --gypsum-vf0 0.9 --material-porosity 0.1 --perm-power 1 --c-cap 16.5 --dissolved-fractions 0.02 0.05 0.1 0.25 0.5 0.75 1.0 --inj-co3 0.5 --inj-ph 11.39 --well-fill-injection --initial-dt 1e-11 --calcite-fixed-area --min-porosity 1e-3 --perm-min-scale 1e-6 --inert-helper-cells" 0.57 60 > forsmark_reactive/pilot/L2_r15_p6.0_s1_seed1.gypcal.log 2>&1 &
wait

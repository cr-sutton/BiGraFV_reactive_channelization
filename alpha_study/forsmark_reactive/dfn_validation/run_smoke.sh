#!/bin/zsh
# DFN smoke test (5 Nov 2026): coupled then gypsum-only on the rFram x4 sigma 1 seed 1 DFN, Phase 1 deck settings, stop at 40 steps.
cd ${0:A:h}
export NP=6 STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5" EXFIX_DFN="--area 1e-6" MEM_FREE_MIN=15
zsh run_dfn_case.sh rf_p4.0_sg1.0_seed1 gypcal smoke "--k-gypsum-mult 21.95 --gypsum-vf0 0.9 --material-porosity 0.1 --perm-power 1 --c-cap 16.5 --log-vtk --dissolved-fractions 0.005 0.02 0.1 0.5 1.0 2.0 5.0 --inj-co3 0.5 --inj-ph 11.39 --well-fill-injection --initial-dt 1e-11 --calcite-fixed-area --min-porosity 1e-3 --perm-min-scale 1e-6 --inert-helper-cells" 0.57 40
zsh run_dfn_case.sh rf_p4.0_sg1.0_seed1 gyponly smoke "--k-gypsum-mult 21.95 --gypsum-vf0 0.9 --material-porosity 0.1 --perm-power 1 --c-cap 16.5 --log-vtk --dissolved-fractions 0.005 0.02 0.1 0.5 1.0 2.0 5.0" 0.57 40

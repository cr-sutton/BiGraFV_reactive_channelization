#!/usr/bin/env python3
"""Ceiling sweep (6 Nov 2026, CEILING_SWEEP.md): k = k0 (phi/phi0)^n, phi_c = 0, n = log10(C) for gypsum-only ceilings
C = 30 / 100 / 1000 (n = 1.4771 / 2 / 3); coupled runs use the same n (their ceiling is 5.554^n = 12.6 / 30.8 / 171).
The 9 Phase 3 networks (P32 x4/x6/x8, sigma 1, seeds 1-3); Phase 1 deck otherwise.  The n = 3 pair on P32 x6 seed 1
exists (tag kphi_n3) and is reused.  Gypsum-only first within each n, highest n first.
  python3 forsmark_reactive/ceilsweep/make_queue_ceilsweep.py > forsmark_reactive/ceilsweep/run_list_ceilsweep.txt"""
FRACS = "0.02 0.05 0.1 0.25 0.5 0.75 1.0 1.5 2.0"
BASE = "--k-gypsum-mult 21.95 --log-vtk --dissolved-fractions " + FRACS
CAL = ("--well-fill-injection --initial-dt 1e-11 --calcite-fixed-area --min-porosity 1e-3 --perm-min-scale 1e-6 "
       "--inert-helper-cells")
PHI10 = "--gypsum-vf0 0.9 --material-porosity 0.1"
CO3_HI = "--inj-co3 0.5 --inj-ph 11.39"
NS = (("3", "ceilN3"), ("2", "ceilN2"), ("1.4771", "ceilN148"))
out = ["# Ceiling sweep 6 Nov 2026 (CEILING_SWEEP.md). k = k0 (phi/0.1)^n, n = log10(C_gyponly)."]
for n, tag in NS:
    for mode in ("gyponly", "gypcal"):
        for p in ("4.0", "6.0", "8.0"):
            for seed in (1, 2, 3):
                if n == "3" and p == "6.0" and seed == 1:
                    continue                                    # reuse kphi_n3
                net = f"../forsmark_reactive/phase1/L2_r15_p{p}_sg1.0_seed{seed}"
                extra = (f"{BASE} --perm-power {n} {PHI10} --c-cap 16.5" if mode == "gyponly"
                         else f"{BASE} --perm-power {n} {PHI10} --c-cap 516.5 {CO3_HI} {CAL}")
                out.append(f'{net} graph_raw {mode} {tag} 0.57 - "{extra}"')
print("\n".join(out))

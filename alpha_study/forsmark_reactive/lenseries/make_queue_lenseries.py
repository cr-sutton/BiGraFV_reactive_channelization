#!/usr/bin/env python3
"""Length series (6 Nov 2026, LENGTH_SERIES.md): L x 250 x 250 m, L = 500/1000/2000, P32 x4/x8, sigma 1, seeds 11-16,
both chemistries, Phase 1 deck and checkpoints (tag phase1, to capacity time 2).  Expensive runs first.
  python3 forsmark_reactive/lenseries/make_queue_lenseries.py > forsmark_reactive/lenseries/run_list_lenseries.txt"""
FRACS = "0.02 0.05 0.1 0.25 0.5 0.75 1.0 1.5 2.0"
BASE = "--k-gypsum-mult 21.95 --perm-power 1 --log-vtk --dissolved-fractions " + FRACS
CAL = ("--well-fill-injection --initial-dt 1e-11 --calcite-fixed-area --min-porosity 1e-3 --perm-min-scale 1e-6 "
       "--inert-helper-cells")
PHI10 = "--gypsum-vf0 0.9 --material-porosity 0.1"
CO3_HI = "--inj-co3 0.5 --inj-ph 11.39"


def line(net, mode, extra):
    return f'../forsmark_reactive/lenseries/{net} graph_raw {mode} phase1 0.57 - "{extra}"'


out = ["# Length series 6 Nov 2026: L x 250 x 250 m, Phase 1 settings (see make_queue_lenseries.py, LENGTH_SERIES.md)."]
for L, p in (("2000", "8.0"), ("1000", "8.0"), ("2000", "4.0"), ("500", "8.0"), ("1000", "4.0"), ("500", "4.0")):
    for seed in range(11, 17):
        n = f"L{L}_r15_p{p}_sg1.0_seed{seed}"
        out += [line(n, "gyponly", f"{BASE} {PHI10} --c-cap 16.5"),
                line(n, "gypcal", f"{BASE} {PHI10} --c-cap 516.5 {CO3_HI} {CAL}")]
print("\n".join(out))

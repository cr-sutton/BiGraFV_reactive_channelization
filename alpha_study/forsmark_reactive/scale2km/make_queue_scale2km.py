#!/usr/bin/env python3
"""
Scale-up test (5 Nov 2026): do the four channel-formation stages of Phase 1 hold on a larger domain?

Networks: FFM01 layer 2 sets, rmin 15 m, domain 2000 x 500 x 250 m (flow length x2, width x2, layer thickness kept, so
4x the volume of Phase 1), built with scale2km/build_one.sh.  Everything else is Phase 1 exactly: one-cell BiGraFV, one
network pore volume per year, porosity 0.1, n = 1, deck flags and checkpoints of make_queue_overnight.py (tag phase1,
ends at capacity time 2 like the P32 x16 runs).

Order: sigma 1.0 first (P32 x4, x6, x8; seeds 1-5), then sigma 0.5, then sigma 0.0, so a stop before the DFN runs
leaves complete ensembles.  Within each sigma the expensive x8 gypsum-only runs go first.  P32 x16 is left out (cost).

  python3 forsmark_reactive/scale2km/make_queue_scale2km.py > forsmark_reactive/scale2km/run_list_scale2km.txt
"""
FRACS = "0.02 0.05 0.1 0.25 0.5 0.75 1.0 1.5 2.0"
BASE = "--k-gypsum-mult 21.95 --perm-power 1 --log-vtk --dissolved-fractions " + FRACS
CAL = ("--well-fill-injection --initial-dt 1e-11 --calcite-fixed-area --min-porosity 1e-3 --perm-min-scale 1e-6 "
       "--inert-helper-cells")
PHI10 = "--gypsum-vf0 0.9 --material-porosity 0.1"
CO3_HI = "--inj-co3 0.5 --inj-ph 11.39"


def line(net, mode, extra):
    return f'../forsmark_reactive/scale2km/{net} graph_raw {mode} phase1 0.57 - "{extra}"'


out = ["# Scale-up test 5 Nov 2026: 2000 x 500 x 250 m, Phase 1 settings (see make_queue_scale2km.py)."]
for sg in ("1.0", "0.5", "0.0"):
    for p in ("8.0", "6.0", "4.0"):
        for seed in (1, 2, 3, 4, 5):
            n = f"L2_r15_p{p}_sg{sg}_seed{seed}"
            out += [line(n, "gyponly", f"{BASE} {PHI10} --c-cap 16.5"),
                    line(n, "gypcal", f"{BASE} {PHI10} --c-cap 516.5 {CO3_HI} {CAL}")]
print("\n".join(out))

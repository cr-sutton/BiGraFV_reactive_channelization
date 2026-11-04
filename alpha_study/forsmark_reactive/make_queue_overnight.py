#!/usr/bin/env python3
"""
Overnight queue (3-4 Nov 2026): Phase 2 mechanism runs and the P32 x16 network set.

Every run here ends at capacity-normalised time 2 (the gypsum the injected water could carry if it left saturated, as
a multiple of the inventory), with checkpoints (and tracer probes) at the same capacity times in every run:
  --dissolved-fractions are in units of the --c-cap given, so c-cap 16.5 (gypsum solubility) for gypsum-only and for the
  capacity-matched low-carbonate runs, c-cap 516.5 for 0.5 M carbonate.

Phase 2 (mechanism), on sigma 1.0 seeds 1-3 at P32 x4, x6, x8, x16:
  phase2_phi005  gyponly + gypcal (0.5 M), initial porosity 0.05 (gypsum vf 0.95, reference porosity 0.05): doubles the
                 permeability contrast the reaction can make (n = 1 ceiling x20 instead of x10)
  phase2_co3lo   gypcal at porosity 0.1 with 2 mM carbonate, injected pH from charge balance: capacity ~18.6 mol/m3 against
                 16.6 for gypsum-only, so the comparison with Phase 1 gypsum-only is 1:1 in time
P32 x16 Phase 1 (tag phase1): gyponly + gypcal (0.5 M) at porosity 0.1 on all 15 networks (5 seeds x 3 sigma).

  python3 forsmark_reactive/make_queue_overnight.py > forsmark_reactive/phase1/run_list_overnight.txt
"""
FRACS = "0.02 0.05 0.1 0.25 0.5 0.75 1.0 1.5 2.0"
BASE = "--k-gypsum-mult 21.95 --perm-power 1 --log-vtk --dissolved-fractions " + FRACS
CAL = ("--well-fill-injection --initial-dt 1e-11 --calcite-fixed-area --min-porosity 1e-3 --perm-min-scale 1e-6 "
       "--inert-helper-cells")
PHI10 = "--gypsum-vf0 0.9 --material-porosity 0.1"
PHI05 = "--gypsum-vf0 0.95 --material-porosity 0.05"
CO3_HI = "--inj-co3 0.5 --inj-ph 11.39"
CO3_LO = "--inj-co3 0.002 --inj-charge-balance"


def line(net, mode, tag, extra):
    return f'../forsmark_reactive/phase1/{net} graph_raw {mode} {tag} 0.57 - "{extra}"'


def net(p, sg, seed):
    return f"L2_r15_p{p}_sg{sg}_seed{seed}"


out = ["# Overnight 3-4 Nov 2026: Phase 2 mechanism runs, then P32 x16 Phase 1 and Phase 2 (see make_queue_overnight.py)."]
mech = []
for p in ("4.0", "6.0", "8.0", "16.0"):
    for seed in (1, 2, 3):
        n = net(p, "1.0", seed)
        mech.append((p, [line(n, "gyponly", "phase2_phi005", f"{BASE} {PHI05} --c-cap 16.5"),
                         line(n, "gypcal", "phase2_phi005", f"{BASE} {PHI05} --c-cap 516.5 {CO3_HI} {CAL}"),
                         line(n, "gypcal", "phase2_co3lo", f"{BASE} {PHI10} --c-cap 16.5 {CO3_LO} {CAL}")]))
p16 = []
for sg in ("0.0", "0.5", "1.0"):
    for seed in (1, 2, 3, 4, 5):
        n = net("16.0", sg, seed)
        p16 += [line(n, "gyponly", "phase1", f"{BASE} {PHI10} --c-cap 16.5"),
                line(n, "gypcal", "phase1", f"{BASE} {PHI10} --c-cap 516.5 {CO3_HI} {CAL}")]
for p, ls in mech:
    if p != "16.0":
        out += ls
out += p16
for p, ls in mech:
    if p == "16.0":
        out += ls
print("\n".join(out))

#!/usr/bin/env python3
"""Gap-filling runs (7 Nov 2026, GAPFILL.md), one queue:
  A  late-time high gain: n = 2 and n = 3 on the 9 sweep networks (sigma 1), both chemistries, to capacity time 8
     (tags ceilN2L, ceilN3L; same deck as ceilN2/ceilN3 plus checkpoints 3, 4, 6, 8)
  B  blind predictor test: the 12 new 1 km networks (lenseries/L1000_*, P32 x4/x8, seeds 11-16), Phase 1 deck to
     capacity time 2, both chemistries, plus the start-of-run tracer probe (marker probe0)
  C  depth against gain at sigma 0: n = 1.48 / 2 / 3 on the 9 sigma-0 networks (P32 x4/x6/x8, seeds 1-3), both chemistries
Long gypsum-only A runs first, then B, then C.
  python3 forsmark_reactive/gapfill/make_queue_gapfill.py > forsmark_reactive/gapfill/run_list_gapfill.txt"""
F2 = "0.02 0.05 0.1 0.25 0.5 0.75 1.0 1.5 2.0"
F8 = F2 + " 3.0 4.0 6.0 8.0"
CAL = ("--well-fill-injection --initial-dt 1e-11 --calcite-fixed-area --min-porosity 1e-3 --perm-min-scale 1e-6 "
       "--inert-helper-cells")
PHI10 = "--gypsum-vf0 0.9 --material-porosity 0.1"
CO3 = "--inj-co3 0.5 --inj-ph 11.39"


def extra(mode, n, fr):
    base = f"--k-gypsum-mult 21.95 --log-vtk --dissolved-fractions {fr} --perm-power {n} {PHI10}"
    return f"{base} --c-cap 16.5" if mode == "gyponly" else f"{base} --c-cap 516.5 {CO3} {CAL}"


def line(net, mode, tag, n, fr, probe=False):
    return f'{net} graph_raw {mode} {tag} 0.57 - "{extra(mode, n, fr)}"' + (" probe0" if probe else "")


P1 = "../forsmark_reactive/phase1"
out = ["# Gap-filling runs 7 Nov 2026 (GAPFILL.md)"]
nets = [(p, s) for p in ("8.0", "6.0", "4.0") for s in (1, 2, 3)]
for mode in ("gyponly", "gypcal"):                                     # A
    for n, tag in (("3", "ceilN3L"), ("2", "ceilN2L")):
        for p, s in nets:
            out.append(line(f"{P1}/L2_r15_p{p}_sg1.0_seed{s}", mode, tag, n, F8))
for p in ("8.0", "4.0"):                                               # B
    for s in range(11, 17):
        for mode in ("gyponly", "gypcal"):
            out.append(line(f"../forsmark_reactive/lenseries/L1000_r15_p{p}_sg1.0_seed{s}", mode, "phase1", "1", F2, probe=True))
for n, tag in (("3", "ceilN3"), ("2", "ceilN2"), ("1.4771", "ceilN148")):   # C
    for mode in ("gyponly", "gypcal"):
        for p, s in nets:
            out.append(line(f"{P1}/L2_r15_p{p}_sg0.0_seed{s}", mode, tag, n, F2))
print("\n".join(out))

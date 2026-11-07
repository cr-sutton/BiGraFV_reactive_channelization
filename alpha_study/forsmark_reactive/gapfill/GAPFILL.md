# Gap-filling runs (locked 7 Nov 2026, before any run)

Approved by Collin on 7 Nov ("1, 2 and 3"). 114 runs in one queue (`run_list_gapfill.txt`, runner `run_queue_gapfill.py`,
launcher `run_gapfill.sh`, 7 chains at a time).

## A. Does relaxation complete at high gain? (36 runs)
n = 2 and n = 3 (k = k0 (φ/φ0)^n), 9 sweep networks (P32 ×4/×6/×8, σ 1, seeds 1–3), both chemistries, to capacity time 8
(tags ceilN2L, ceilN3L). Up to capacity time 2 they must reproduce ceilN2/ceilN3 (consistency check).
**Rule:** relaxation completes at high gain if, at the last state, the median per-stretch recovered share
(last − min)/(1 − min) is ≥ 0.9 in every 100 m stretch and the network PR_V is ≥ 0.9 of its start, for gypsum-only at
n = 2 and n = 3. Reported per chemistry and n; if not reached, report how far it got and the dissolved fraction.

## B. Blind test of the t10 breakthrough predictor (24 runs)
12 new 1 km networks never used before (lenseries/L1000, P32 ×4 and ×8, σ 1, seeds 11–16), Phase 1 deck to capacity time 2,
both chemistries, plus the start-of-run tracer probe (snap_0, same probe settings as the training runs).
Frozen relation from the 1 km training runs (phase1/early_arrival_predictor.csv, t10):
d_bt = 0.0292 + 1.4483 t10/τ (gypsum-only); d_bt = 0.1113 + 1.4924 t10/τ (coupled).
**Rule:** passes per chemistry if R² ≥ 0.5 against the frozen line, rank correlation ≥ 0.7 and |median bias| ≤ 0.03.
Events as scale2km/compare_scale.py (capacity time ≤ 2, outlet window x > 400 m).

## C. Depth against gain at σ = 0 (54 runs)
n = 1.48 / 2 / 3, 9 σ-0 networks (P32 ×4/×6/×8, seeds 1–3), both chemistries, to capacity time 2 (tags ceilN148, ceilN2,
ceilN3 in the sg0.0 folders); n = 1 exists (phase1).
**Rule:** the σ-1 result generalises if depth falls with C on ≥ 7 of 9 networks and coupled sits within a median |0.03|
of the gypsum-only curve at the same C (as R1/R2 in ceilsweep/CEILING_SWEEP.md).

## Cost
About 110 run-hours (A gypsum-only runs to capacity time 8 dominate); about 16 h wall on 7 chains.

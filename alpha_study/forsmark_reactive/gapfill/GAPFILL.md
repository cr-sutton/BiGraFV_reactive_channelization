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

## Results (8 Nov 2026; analyze_gapfill.py → gapfill_tests.csv, gapA_*.csv, gapB_predictor.csv, gapC_*.csv)

All 114 runs finished (Sat 22:39), each with patterns, channelization and (B) the snap_0 probe.

### A. Relaxation at high gain: n = 2 completes; n = 3 has not completed by capacity time 8 (rule not met for n = 3)
| chemistry, n | lowest stretch median recovered | stretches ≥ 0.9 | network PR_V end / start (median; ≥ 0.9) | d at end |
|---|---|---|---|---|
| gypsum-only, 2 | 0.97 | 10 / 10 | 0.99 (9 / 9) | 0.89 |
| gypsum-only, 3 | 0.74 | 0 / 10 | 0.84 (1 / 9) | 0.74 |
| coupled, 2 | 1.00 | 10 / 10 | 1.02 (9 / 9) | 0.93 |
| coupled, 3 | 0.96 | 10 / 10 | 1.02 (9 / 9) | 0.86 |
- n = 3 gypsum-only is still recovering at the end: network PR_V / start (median) 0.40, 0.56, 0.62, 0.69, 0.74, 0.85 at
  capacity time 1, 2, 3, 4, 6, 8, while d goes 0.38 → 0.74.
- At the same dissolved fraction n = 2 and n = 3 are close (0.54 / 0.53 at d 0.5; 0.70 / 0.67 at 0.6; 0.80 / 0.78 at 0.7,
  n = 3 medians over 9, 7, 6 networks): recovery tracks how much gypsum is gone. Why n = 3 is slower in time (for example, its channel bypassing the
  remaining gypsum) was not tested; it is a hypothesis. "Not met" means not by capacity time 8 (d 0.74), not never.
- Consistency with ceilN2/ceilN3 to capacity time 2 (gapA_consistency.csv): the L runs use a different output schedule,
  so 9 of 68 reference states match in time per run. Gypsum-only: dissolved fraction within 0.0006, depth (t_cap ≤ 2)
  within 0.011, PR_V at matched states within 1.0 % (n = 2) and 15 % (n = 3, median 0.2 %). Coupled is looser: dissolved
  fraction within 0.025, depth within 0.088 (median 0.008–0.010), PR_V within 8 % / 19 %; the coupled solution is
  sensitive to the output schedule (time-step cuts).

### B. Blind predictor test: FAILS for both chemistries
| chemistry | R² (frozen line) | rank correlation | median bias | median abs error |
|---|---|---|---|---|
| gypsum-only | −0.17 | 0.51 | −0.043 | 0.074 |
| coupled | 0.45 | 0.72 | −0.034 | 0.059 |
- Not the σ mix: on the σ-1 training networks alone the frozen line gives R² 0.80 / 0.76, but that is in-sample (the line
  was fit on all 45 networks). Same builder, domain and outlet window as Phase 1. The coupled deck's output schedule
  matches the length-series and 2 km decks (--c-cap 516.5), not the Phase 1 coupled deck (16.5); breakthrough is read at
  saved states, so a coarser schedule could only bias it upward, and the blind values are lower. The blind set has P32 ×4
  and ×8 only. The likeliest reading is an optimistic training fit plus seed-to-seed variance. The blind set has the same t10 spread (SD 0.065
  against 0.067) and breaks through earlier than predicted (median d_bt 0.49 against 0.57 in σ-1 training, gypsum-only; 0.57 against 0.63
  coupled). The runs reach capacity time 2.01 / 2.00; the last state kept is 1.73 because the analysis uses t_cap ≤ 2
  strictly, as for Phase 1. All 24 broke through (max d_bt 0.70, final d about 0.83).
- Pooling all 27 σ-1 1 km networks (15 training + 12 blind), leave-one-network-out: R² 0.51 (gypsum-only) / 0.62
  (coupled), rank correlation 0.76 / 0.83 (t10). Other percentiles do no better (t16: 0.52 / 0.64). This is the honest
  out-of-sample estimate: early arrival ranks breakthrough moderately, it does not predict it to R² 0.75.

### C. Depth law at σ 0: PASSES
- Depth falls with C on 9 of 9 networks (strictly, ρ = −1 on all 9).
- Coupled against gypsum-only at the same C: median |residual| 0.029, median +0.027 (27 points; passes at 0.03 by a
  small margin); coupled shallower, 7 of 27 beyond +0.05, none below −0.05. By law: 0.021 (n = 1.48), 0.042 (n = 2),
  0.029 (n = 3). The 9 coupled n = 1 points (C 5.55) lie below the σ-0 gypsum-only range (≥ 10) and are excluded; on the
  same 27 laws σ 1 gives 0.022 (6 of 27 beyond +0.05), against 0.021 over all 36.
- Gypsum-only median depth ×10 / ×30 / ×100 / ×1000: 0.65 / 0.43 / 0.25 / 0.16 at σ 0 (σ 1: 0.68 / 0.55 / 0.34 / 0.15).
  Inheritance: per-law medians 0.97–1.00 (single runs 0.91–1.00). Network P32 ×4 seed 2 is nearly flat from ×100 to
  ×1000 (0.419 → 0.414).

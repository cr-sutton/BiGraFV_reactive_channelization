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

## A2. ×1000 relaxation past capacity time 8, and why it is slow (locked Sun 8 Nov 09:40, before any run)

Asked by Collin on 8 Nov ("do both remaining gaps"). 9 runs: gypsum-only, n = 3, the 9 σ-1 sweep networks, same deck as
ceilN3L but to capacity time 20 (tag ceilN3XL; checkpoints F8 + 10, 12, 14, 16, 20). Coupled n = 3 already relaxed
fully by capacity time 8, so it is not rerun. Queue `run_list_gapfill2.txt`, launcher `run_gapfill2.sh` (same
environment as run A), 7 chains. Up to capacity time 8 the runs must reproduce ceilN3L (same deck).

**Rules (fixed now):**
1. *Completion* (rule A unchanged): at the last state, median per-stretch recovered share ≥ 0.9 in every stretch and
   median network PR_V ≥ 0.9 of start. Also reported: the first capacity time at which the median network PR_V ≥ 0.9.
2. *Paced by the gypsum left* (prediction from run A): at matched dissolved fraction, the n = 3 median network PR_V /
   start stays within 0.03 of the n = 2 median (ceilN2L) at every d from 0.5 to the largest d that both reach with at
   least 6 of 9 networks.
3. *Bypass* (the hypothesis Karen flagged as untested), on ceilN2L, ceilN3L and ceilN3XL states:
   - dissolution efficiency E = Δd / Δt_cap between saved states (1 = every unit of injected capacity dissolves its
     share of gypsum, i.e. water leaves saturated; lower = water leaves without having met gypsum);
   - bypass index I = flow-weighted mean remaining gypsum fraction / volume-weighted mean remaining gypsum fraction
     over fractures (remaining = 1 − fraction_dissolved; flow = |Q_frac|; 1 = flow sees the gypsum evenly, < 1 = flow
     avoids the gypsum that is left).
   The hypothesis "the ×1000 channel is slow because it bypasses the gypsum left" is supported if, at matched capacity
   time between 2 and 8, n = 3 has lower E and lower I than n = 2 on ≥ 7 of 9 networks (each a median over the
   matched times). Otherwise it is not supported and the text says so.

*Launch note (Sun 09:30).* 5 of the 9 decks failed to build: at capacity time 20 the checkpoint times reach ~1e5 y,
where `deck_gypsum_calcite.py`'s checkpoint→VTK-index lookup (`list.index(round(t, 10))` against `np.round` values)
misses. Those 5 were relaunched at 09:32 (`run_list_gapfill2b.txt`, `run_gapfill2b.sh`) through local copies
`gapfill/run_case_a2.sh` and `gapfill/deck_gypsum_calcite_a2.py`, whose only change is a nearest-match lookup (the deck
itself is unchanged; the shared scripts outside forsmark_reactive were not edited).

## B diagnosis: why the blind test missed, and why 2 km ranks weakly (8 Nov 2026; exploratory, after the result)

`diagnose_predictor.py` → diag_runs.csv, diag_sets.csv, diag_structure.csv, diag_splits.csv, diag_summary.json.
Candidates were listed before computing; none of this was pre-registered.

1. **Measurement: not the cause.** Breakthrough is read at saved states 0.059–0.065 of the gypsum apart in every set (medians)
   (median Δd at breakthrough 0.062 training, 0.059 blind, 0.065 2 km, gypsum-only). Interpolating breakthrough between
   the bracketing states (and refitting the training line) gives blind R² 0.04 / 0.45 and 2 km 0.32 / 0.09: no better.
2. **Probe: not the cause.** Tracer recovery 0.998–0.999 in every set; t10 spread the same (SD 0.065 blind, 0.067
   training).
3. **Structure: no sign.** None of 8 pre-run network statistics (fractures, degree, inlet/outlet fractures, node/edge-
   disjoint paths, backbone fraction, dead-end share) correlates with the residual on the 27 σ-1 networks (|ρ| ≤ 0.16,
   all p > 0.4), and blind and training networks do not differ in any of them (Mann–Whitney p ≥ 0.34).
4. **Luck, around a moderate relation: the best account.** The residual shift of the blind set against the σ-1
   training set is not significant (median −0.043 against −0.004, p 0.37 gypsum-only; −0.034 against +0.007, p 0.32
   coupled). Random 15 / 12 splits of the 27 σ-1 networks (20,000): median test R² 0.49 (gypsum-only) / 0.60 (coupled),
   10–90 % range 0.08–0.64 / 0.29–0.74; 52 % / 30 % of splits fall below the 0.5 pass line. The actual split (σ-1 fit)
   gives R² −0.10 / 0.48, at the 6th / 26th percentile (rank correlation 3rd / 16th). The training R² of 0.77 was a
   favourable draw; with 12 test networks a pass at 0.5 was roughly a coin flip for gypsum-only.
5. **2 km: the relation itself is weaker, not just narrower.** With the 1 km line and scatter, the narrower 2 km t10
   spread (SD 0.040 against 0.067) would still give R² ≈ 0.65; observed 0.39 / 0.01. At 2 km the slope is shallower
   (own fit 1.23 / 0.90 against 1.45 / 1.49) and the scatter larger (residual SD 0.052 / 0.064 against 0.043 / 0.045):
   early arrival carries less information about breakthrough over a longer path. Why is open.

### A2 rule 3 (bypass) result, computed Sun 8 Nov on ceilN2L / ceilN3L (analyze_gapfill_a2.py --bypass-only)
- **As locked (matched capacity time 2–8): not supported.** n = 3 has the lower bypass index on 8 of 9 networks (median
  I 0.006 against 0.011) but the lower efficiency on only 3 of 9 (median E 0.046 against 0.025): rule needs both ≥ 7.
- Why the locked design failed: at the same capacity time the n = 3 runs still hold much more gypsum (d 0.51 against
  0.74 at capacity time 2), and E rises with the gypsum left. The comparison was confounded by inventory.
- **Exploratory, matched dissolved fraction (gapA2_bypass_matched_d.csv; not pre-registered):** with the same gypsum
  left, n = 3 dissolves 3–5× more slowly (median E 0.11 against 0.38 at d 0.5; 0.080 / 0.30 at 0.6; 0.037 / 0.18 at 0.7, on the networks
  reaching d in both; corrected 8 Nov evening, the first version quoted each set's own medians, 0.25 and 0.15 for n = 2)
  and its flow sees ~5× less of the remaining gypsum (I 0.010 / 0.053 at d 0.5), on every network that reaches that d
  (9 / 9, 7 / 7, 5 / 5). The lag opens after capacity time 0.25 (both d 0.25; then 0.43 against 0.31 at 0.5, 0.61 against
  0.38 at 1).
- Both chemistries' flow mostly bypasses the gypsum late on: I ≈ 0.01 means the flow-weighted remaining gypsum is ~1 %
  of the volume-weighted value.

### A2 result, Sun 8 Nov 19:20 (all 9 ceilN3XL runs finished; analyze_gapfill_a2.py, bypass_matched_d.py)
All 9 ran to capacity time 20.12 (Wall Clock Time in every log). Up to capacity time 8 they reproduce ceilN3L at the 14
matched states: d within 0.002 on every network, network PR_V within 0.7 % on 8 of 9; on p4 seed 3 one state (capacity
time 1.5) differs by 6.8 % while d agrees within 0.0003 and the neighbouring states within 0.01 %: a one-state transient,
cause not traced (gapA2_consistency.csv).

1. **Completion: passed.** At capacity time 20 every stretch's median recovered share is ≥ 0.9 (lowest 0.935, 10 / 10)
   and the median network PR_V is 0.949 of start (8 of 9 networks ≥ 0.9; p4 seed 2 is at 0.874). d at the end 0.848
   (median). The median network PR_V curve first reaches 0.9 at capacity time 10.25; per network the first capacity time
   ≥ 0.9 runs from 6.9 to 20.1 (two networks only at the last state, one never). k_eff gain at the end 937–985 of the
   attainable 1000 (gapA2_network.csv, gapA2_stretch.csv, gapA2_tests.csv). The pass is on the medians, as the rule is
   written. Per network, 3 of 9 have every stretch ≥ 0.9 (stretches below 0.9: 4, 6, 3, 5, 2, 1, 0, 0, 0 for p4 s1–3, p6
   s1–3, p8 s1–3); p4 seed 2 is clearly not complete (network 0.874, the last three stretches 0.39–0.54 recovered).
2. **Paced by the gypsum left: passed.** From d 0.50 to 0.81 (the largest d with ≥ 6 of 9 networks in both sets) the n = 3
   median network PR_V / start stays within 0.028 of the n = 2 median (median gap −0.011; n = 3 slightly lower above
   d 0.7) (gapA2_paced.csv). The margin is thin (0.028 against 0.03), and above d 0.7 the n = 3 median is over 7 of 9
   networks (the slowest two never reach it). Below d 0.5, outside the rule's range, the curves are not paced: n = 3
   dips much deeper at the same d (0.57 / 0.70 at d 0.10, 0.21 / 0.44 at d 0.20; gap −0.10 to −0.23 over d 0.05–0.30),
   which is the depth law (Part 3).
3. **Bypass, as locked: not supported** (unchanged, the rule compares ceilN2L and ceilN3L at capacity time 2–8; see above).
   *Exploratory, matched dissolved fraction, now with ceilN3XL to d 0.8* (gapA2_bypass_matched_d_summary.csv): n = 3 has
   the lower E and the lower I on every network that reaches each d (9 / 9 at 0.5 and 0.6, 7 / 7 at 0.7 and 0.8).
   Median E n = 2 / n = 3: 0.38 / 0.11 at d 0.5, 0.25 / 0.067 at 0.6, 0.18 / 0.035 at 0.7, 0.088 / 0.011 at 0.8
   (3.4–7.7× slower; the 0.8 value rests on wide late saved-state intervals; medians over all networks present, as in
   Figure 5D, give 3–4×); median I 0.053 / 0.010 at d 0.5, 0.020 / 0.003 at 0.8. Capacity time to reach d 0.8: 2.1
   against 8.5. Counts are of the networks that reach each d (two never reach 0.7).

**Reading.** In the median, the ×1000 relaxation completes (one network of nine clearly does not). The gain sets how
deep the channel goes (n = 3 dips deeper at the same d below d 0.5); from d 0.5 on, the pace of relaxation is set by the
gypsum left, and ×1000 takes about four times the water (capacity time 10.3 against 2.5 for the median network PR_V to reach 0.9; 8.5 against 2.1 to reach d 0.8; corrected 9 Nov from 'five') to get there because it removes the same gypsum more slowly.
Its flow sees less of the gypsum left (lower I) at every matched d, consistent with bypass; this is correlational and was
shown after the locked test failed, so it is not a pre-registered result.

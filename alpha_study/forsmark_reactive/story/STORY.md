# Reactive channels in kilometre-scale mineral-filled fracture networks: the story (draft v3, 8 Nov 2026: gap-filling runs A–C folded in; v2 kept as STORY_v2.md)

All results are BiGraFV (one control volume per fracture, PFLOTRAN) on synthetic Forsmark FFM01 networks
(1000 × 250 × 250 m unless stated; P32 ×4/×6/×8; transmissivity spread σ 0/0.5/1; 5 seeds; one network pore volume per
year; fractures start 90 % gypsum, φ0 = 0.1). Two chemistries: gypsum-only (dilute water) and coupled gypsum–calcite
(0.5 M carbonate brine; calcite replaces the gypsum and takes 49.4 % of its volume). The dissolved fraction d (fraction
of the network's gypsum dissolved) is the clock used for every stage event. Depth = network PR_V minimum / its start
(lower = more focused). Comparisons are model against model: one thing varied, the rest fixed.

Figures: `story/fig1_stages.png` … `fig4_predictor.png` (`story/make_story_figures.py`). Reviewed by Karen on 7 Nov;
v2 corrects the points she raised (list at the end).

---

## 1. The front moves through four stages: open space decouples from flow, recouples, breaks through, relaxes

**Claim.** The networks pass through the same sequence, with d as the clock:
1. *Decoupling.* Pore space opens near the inlet while the flow is still controlled by filled fractures downstream: the
   flow is less aligned with the open pore space than at the start (PR_pore / PR_V falls below 1).
2. *Recoupling.* The flow moves into the opened fractures; PR_pore / PR_V climbs back through 1 and overshoots (flow is
   more aligned with open space than at the start), while flow concentrates (PR_V falls).
3. *Peak focusing, then breakthrough.* PR_V reaches its minimum, then the front reaches the outlet.
4. *Relaxation.* Neighbouring paths dissolve, the flow spreads again and PR_V returns to its start.

**Evidence (Fig. 1; P32 ×4–×8, 45 runs per chemistry).**
- Event medians (d): pore-volume minimum 0.17 (gypsum-only) / 0.20 (coupled); PR_V minimum 0.37 / 0.44; breakthrough
  0.56 / 0.63.
- Order (capacity time ≤ 2): the full order (pore-volume minimum ≤ PR_V minimum ≤ breakthrough) holds in 87 of 90 runs at
  1 km and 83 of 90 at 2 km. In 14 of 90 (1 km) the PR_V minimum and breakthrough fall on the same saved state.
- Decoupling index PR_pore / PR_V relative to start. Median curve (Fig. 1C): minimum 0.68 (gypsum-only) and 0.80
  (coupled) at d ≈ 0.1, back through 1 at d ≈ 0.3, peak 1.52 / 1.28 near d = 0.5–0.55. Per run: the minimum is below 1 in
  45 of 45 runs per chemistry (median 0.58 at d = 0.13 and 0.72 at d = 0.18).
- Relaxation: at the last saved state (median d 0.93 gypsum-only, 0.98 coupled) PR_V is 0.995 and 1.01 of its start.
- The order also holds at P32 ×16 (26 of 30 runs, to capacity time 2) and the PR_V minimum precedes breakthrough at 2 km
  (90 of 90).

**Backing.** `phase1/phase1_mechanism.csv` (analyze_phase1_mechanism.py), `phase1/stage_events_clocks.csv`
(stage_events_clocks.py), `scale2km/scale_runs.csv` (compare_scale.py); report sections 3, 5, 8.10.

**Caveats.** Fig. 1 event lines use stage_events_clocks (capacity time ≤ 3); the order counts use scale_runs (≤ 2). The
coupled PR_V curve is flat between d ≈ 0.2 and 0.55, so its minimum is weakly defined. With one cell per fracture,
stage 1 is about whole fractures, not in-fracture fronts. We do not claim d is a better clock than others; it is the one
we use.

**New or known.** Each stage has precedents (inheritance and focusing: Szymczak & Ladd 2009, Hyman et al. 2026;
re-spreading after breakthrough: 2D karst networks, Perne et al. 2014). The full sequence, and the decoupling–recoupling of
flow and open space, were not found in 3D network studies (report 8.12).

---

## 2. The focus moves with the front and relaxes behind it

**Claim.** Binned along the flow (100 m stretches), each stretch focuses once, when the front passes it, and then returns
to where it started. The strongest local focusing is in the last stretch before the outlet.

**Evidence (Fig. 2; panels A–B: P32 ×4–×8, 45 runs per chemistry; panel C and numbers: P32 ×4–×16, 60 runs).**
- The dissolved fraction at each stretch's minimum rises from 0.03 at the inlet to 0.50 (gypsum-only) and 0.58 (coupled)
  at the outlet (medians).
- Outlet stretch minimum 0.36 (gypsum-only) and 0.52 (coupled) of its start, against 0.54–0.66 and 0.67–0.76 upstream.
- At the end every stretch is within 0.8 % (gypsum-only) and 1.7 % (coupled) of its start.
- Robust to binning: counting each fracture in every stretch it spans, every stretch ends within 2.3 % / 1.3 % of its
  start and the minimum still moves inlet to outlet (rank correlation over stretches 0.94 / 0.95).
- The same moving front appears at 2 km (report 8.10, 200 m bins).
- At high gain (9 sweep networks; `ceilsweep/xbin_highgain.csv`, xbin_highgain.py) the front still moves inlet to outlet
  (d at the stretch minimum 0.05 → 0.27 gypsum-only at n = 3) and each stretch focuses much harder (outlet stretch 0.01 of
  its start at n = 3, 0.06 at n = 2). Stretches behind the front are already relaxing when the runs stop at capacity time 2:
  median recovered share (last − min)/(1 − min) 0.73–0.95 at n = 2 and 0.17–0.71 at n = 3 (gypsum-only; 0.55–0.90 coupled),
  lowest near the outlet. These runs end at d = 0.74 (n = 2) and 0.52 (n = 3), so whether relaxation completes at high gain
  is not yet known.

**Backing.** `phase1/xbin_channelization.csv`, `xbin_bin_minima.csv`, `xbin_spanning_minima.csv`
(xbin_channelization.py, xbin_bin_minima.py, prv_decomposition.py); report 8.9.

**What it is not.** The width of the focused zone does not predict when the whole network is most focused (rule set in
advance, failed: rank correlation 0.27–0.50; report 8.13). The network minimum comes from flow shifting inside the initial
channel upstream of the outlet, before the outlet stretch focuses.

**New or known.** A downstream-moving focusing front is published (Hyman et al. 2026, Fig. 11), but there focusing behind
the front holds at its maximum because the wall rock never runs out. Relaxation behind the front, driven by the finite
soluble fill, is what we did not find reported.

**Update 8 Nov, run A (gapfill/GAPFILL.md; gapA_stretch.csv, gapA_network.csv; Figure 5).** n = 2 and 3 continued to
capacity time 8 on the 9 sweep networks. n = 2 (×100) meets the pre-set rule: every stretch median recovered 0.97–0.99,
network PR_V 0.99 of start (9 of 9 ≥ 0.9). n = 3 (×1000) does not by capacity time 8: stretches 0.74–0.89, network 0.84
(1 of 9 ≥ 0.9), d 0.74, still rising (median 0.40, 0.56, 0.62, 0.69, 0.74, 0.85 at capacity time 1, 2, 3, 4, 6, 8). At
the same dissolved fraction n = 2 and n = 3 sit within 0.03 (0.54 / 0.53 at d 0.5, 0.70 / 0.67 at 0.6, 0.80 / 0.78 at 0.7;
n = 3 over 9, 7, 6 networks): recovery is paced by the gypsum left. "Not met" means not by capacity time 8. Bypass (GAPFILL.md A2
rule 3): the locked test at matched capacity time failed (lower efficiency on 3 of 9; confounded by the larger gypsum
inventory left at n = 3). Exploratory, at matched d: n = 3 dissolves 3–4× more slowly (E 0.11 against 0.38 at d 0.5)
and its flow sees ~5× less of the remaining gypsum, on 9 of 9 (7 of 7 at d 0.6, 5 of 5 at 0.7); the lag opens after
capacity time 0.25. Coupled runs relax fully at both n. The L runs reproduce the capacity-time-2 runs at the 9 matching states (gypsum-only
depth within 0.011, dissolved fraction within 0.0006; coupled looser: depth up to 0.088, dissolved fraction 0.025).

**Update 8 Nov evening, run A2 (GAPFILL.md A2; gapA2_*.csv; Figure 5).** The 9 gypsum-only n = 3 runs continued to
capacity time 20 (they reproduce the capacity-time-8 runs: d within 0.002; PR_V within 0.7 % on 8 networks, 6.8 % on
p4 seed 3, at one state only). Rule 1, completion: passed on the medians. Every stretch median recovered ≥ 0.935,
network PR_V 0.949 of start (8 of 9 ≥ 0.9; only 3 of 9 with every stretch ≥ 0.9; p4 seed 2 at 0.874, last three
stretches 0.39–0.54), d 0.85; the median curve crosses 0.9 at capacity time 10.25 (per network 6.9 to 20.1, one
never); k_eff gain 937–985 of the attainable 1000. Rule 2, paced by the gypsum left: passed, n = 3 within 0.028 of n = 2
at every d from 0.50 to 0.81 (median gap −0.011, thin margin); below d 0.5 n = 3 dips much deeper (0.21 / 0.44 at d 0.2). Bypass at matched d, now to d 0.8 with the long runs (exploratory):
n = 3 lower E and lower I on every network (9 / 9 at d 0.5 and 0.6, 7 / 7 at 0.7 and 0.8); E 0.38 / 0.11 at d 0.5,
0.088 / 0.011 at d 0.8 (3.4–7.7× slower on matched networks, coarse late states; 3–4× in the all-network medians of
Figure 5D); reaching d 0.8 takes capacity time 8.5 against 2.1. In the median the ×1000 relaxation completes; it needs
about five times the water, consistent with its flow bypassing the gypsum left (correlational).

---

## 3. Channel depth follows the attainable permeability gain; the chemistry acts through that gain

**Claim.** How deep the channel gets follows C, the permeability gain of a fully reacted fracture. Coupled runs sit on the
gypsum-only depth(C) curve of the same network. A higher C narrows the channel within the initial channel.

**Evidence (Fig. 3; 9 networks: P32 ×4/×6/×8, σ 1, seeds 1–3; k = k0 (φ/φ0)^n; 52 new runs plus existing).**
- Median depth, gypsum-only (9 networks): 0.78 at ×5.5, 0.68 at ×10, 0.55 at ×30, 0.34 at ×100, 0.15 at ×1000. Depth falls
  with C on 9 of 9 networks (pre-set rule R1), about 0.25 per decade, flattening at high C (9 of 9).
- Coupled (its own C: ×3.3, ×5.6, ×12.6, ×30.8, ×171): median depth 0.88, 0.79, 0.65, 0.55, 0.35.
- Same C, different chemistry: against the same network's gypsum-only curve at the same C, the coupled depth differs by a
  median |0.021| over 36 points (rule R2 passed at 0.03). The difference has a sign: coupled is slightly shallower
  (median +0.021; 6 of 36 points beyond 0.05, all positive, largest 0.11). Against the network permeability gain actually
  reached, the median difference is 0.014.
- C, not n: the matched points compare different exponents at the same C (for example coupled n = 2, C = ×30.8 against
  gypsum-only n = 1.48, C = ×30) and still agree. At a fixed ×10 gain, the shape of the law (n = 0.5 to 8) moves depth by
  ±0.04 (E0, one network). Within one chemistry the sweep raises n and C together, so these two checks are what
  separates them.
- Narrowing within the initial channel: 91–100 % of the peak-channel fractures at n = 1.48, 2 and 3 are inside the n = 1
  channel of the same network (medians 0.97–1.00), while the channel holds 0.71 / 0.47 / 0.16 (gypsum-only) and 0.85 /
  0.63 / 0.35 (coupled) as many fractures as at n = 1. This is consistent with inheritance (0.95–0.99 at every C): the
  higher gain keeps fewer of the paths that were already there.

**What the gain changes besides depth.** Everything happens earlier: median breakthrough 0.65 → 0.27 and PR_V minimum
0.43 → 0.22 (gypsum-only, ×5.5 → ×1000, 9 networks). At n = 3 stages 1 and 2 merge: the pore-volume minimum comes after the
PR_V minimum in 5 of 8 gypsum-only networks (2 of 8 coupled). The PR_V minimum comes at or before breakthrough in 86 of the
90 sweep runs (the 4 exceptions are at ×5.5–×30), on the same saved state in 16.

**Backing.** `ceilsweep/ceilsweep_runs.csv`, `ceilsweep_residuals.csv`, `ceilsweep_tests.csv` (analyze_ceilsweep.py, rules
in CEILING_SWEEP.md), `ceilsweep/channel_overlap.csv` (channel_overlap.py), `phase1/kphi_e0/kphi_e0_summary.csv`; report
8.11, 8.14.

**Caveats.** At high C the channel bypasses the rest of the network: by capacity time 2 only 0.49 of the gypsum has
dissolved at n = 3 (0.85 at n = 1), so relaxation (stage 4) is untested at high gain. The ×5.5 gypsum-only point uses
φ0 = 0.182 rather than a different n. C is nominal; the realized network gain at the last state is 0.56 (gypsum-only) and
0.70 (coupled) of nominal at n = 3. One σ (1) only. There is no null model for the overlap: with inheritance near 1 any
smaller channel would sit inside the n = 1 channel.

**New or known.** That calcite replacement limits the permeability gain is known (Budek et al. 2026, Γ). A measured
depth(C) curve on which coupled runs sit at their own gain, with the channel narrowing inside the initial channel, was not
found.

**Update 8 Nov, run C (gapC_runs.csv, gapC_residuals.csv; Figure 3D).** The same 9 geometries at σ 0, n = 1 / 1.48 /
2 / 3: depth falls with C on 9 of 9 (pre-set rule passed). Coupled against gypsum-only at the same C: median |residual|
0.029, median +0.027 (27 points; passes the 0.03 rule narrowly; σ 1 on the same 27 laws 0.022), 7 of 27 beyond +0.05, none below −0.05. Gypsum-only median
depth 0.65 / 0.43 / 0.25 / 0.16 at ×10 / ×30 / ×100 / ×1000 (σ 1: 0.68 / 0.55 / 0.34 / 0.15): deeper at intermediate gain
without transmissivity spread, the same at the ends. Coupled is slightly shallower than gypsum-only at both σ.

---

## 4. One number known before the run ranks how much gypsum must dissolve before breakthrough

**Claim.** The time for the first 10 % of a tracer pulse to cross the unreacted network, in mean residence times
(t10 / τ_res), predicts the dissolved fraction at breakthrough at 1 km: d_bt ≈ 0.03 + 1.45 × t10/τ_res (gypsum-only),
0.11 + 1.49 × t10/τ_res (coupled).

**Evidence (Fig. 4; 1 km, P32 ×4–×8, 45 networks per chemistry).**
- Each P32 level held out in turn: R² 0.77 (gypsum-only) and 0.75 (coupled), rank correlation 0.92 / 0.92. The largest
  fracture's flow share gives 0.62 / 0.55 on the same runs. Other arrival percentiles: t01 0.73 / 0.67, t05 0.76 / 0.73,
  t16 0.76 / 0.77. We use t10 for both chemistries (best for gypsum-only; t16 is marginally better for coupled).
- The single fastest inventory path (min Σ V/q) does not predict it (rank correlation 0.17–0.25 at 1 km, 60 networks
  including ×16; negative at 2 km; fastpath_predictor.py): breakthrough follows the flow-weighted fast part of the network,
  not one path.
- 2 km, not used in the fit (45 new networks, twice as long): the 1 km relation carries over in size (median bias −0.023
  gypsum-only, −0.030 coupled; median absolute error 0.045 / 0.076; d_bt / (t10/τ) 1.52 → 1.47 and 1.82 → 1.73), but it
  ranks the 2 km networks only weakly (rank correlation 0.60 / 0.43; R² 0.39 / 0.01). The 2 km breakthroughs span a
  narrower range (SD 0.07 against 0.11). The largest-fracture share was not computed at 2 km, so the two are not compared
  there.

**Why it should work.** At local equilibrium the dissolution front is a strongly retarded copy of the flow field, so how
much gypsum must dissolve before the front reaches the outlet depends on how fast the well-connected part of the network
delivers water there.

**Backing.** `phase1/early_arrival_predictor.csv`, `early_arrival_predictor_fit.csv` (early_arrival_predictor.py; tracer
from the snap_0 probes, probe_frozen_state_tracer.py); `phase1/fastpath_predictor_fit.csv`;
`phase1/breakthrough_predictor_summary.csv` for the largest-fracture share.

**Caveats.** t10 needs a tracer pulse on the unreacted network (cheap, but a simulation, not a statistic of the network
alone). The tracer is an Eulerian pulse with numerical dispersion. The percentile was picked on the 1 km runs. The only
held-out set (2 km) differs in length as well as geometry, and the relation transfers in size, not in ranking. The
coupled intercept (0.11) differs from gypsum-only (0.03).

**Update 8 Nov, run B: the blind test failed (gapB_predictor.csv, gapfill_tests.csv; Figure 4).** 12 new 1 km networks
(P32 ×4/×8, σ 1, seeds 11–16), frozen line: R² −0.17 (gypsum-only) / 0.45 (coupled), rank correlation 0.51 / 0.72,
median bias −0.043 / −0.034 (pass: R² ≥ 0.5, ρ ≥ 0.7, |bias| ≤ 0.03). Same builder as Phase 1; on the σ-1 training
networks alone the line gives R² 0.80 / 0.76 in-sample, so it is not the σ mix; the likeliest reading is an optimistic
training fit plus network-to-network variance (the blind set has P32 ×4/×8 only). The new networks
break through earlier than predicted (median d_bt 0.49 against 0.57 in σ-1 training, gypsum-only). Honest estimate, all
27 σ-1 1 km networks with one left out: R² 0.51 / 0.62, rank correlation 0.76 / 0.83 (t16 0.52 / 0.64). Item 4 is a
supporting result: early arrival ranks breakthrough moderately; it does not predict it to R² 0.75.

**Diagnosis 8 Nov (exploratory; gapfill/diag_*.csv, diag_summary.json; Figure S4).** Not the measurement (state
spacing at breakthrough 0.05–0.06 in every set; interpolated breakthrough gives blind R² 0.04 / 0.45), not the probe
(recovery 0.998–0.999, same t10 spread), not structure (8 pre-run statistics, |ρ| ≤ 0.16, all p > 0.4; blind and
training indistinguishable). Blind residual shift not significant (p 0.37 / 0.32). Random 15 / 12 splits of the 27 σ-1
networks: median test R² 0.49 / 0.60, 52 % / 30 % below 0.5; the actual split at the 6th / 26th percentile. 2 km: the
narrower spread alone would give R² ≈ 0.65; the 2 km relation is shallower (1.23 / 0.90 against 1.45 / 1.49) and
noisier (residual SD 0.052 / 0.064 against 0.043 / 0.045).

---

## Open questions after the gap-filling runs

1. Answered (runs A and A2): relaxation completes at ×100 by capacity time 8 and, in the median, at ×1000 by about 10
   (gypsum-only; one network of nine not done by 20); from d 0.5 the two follow one path (pre-set, within 0.03).
2. Answered (run B and its diagnosis): no. Out of sample t10 explains about half the variation; the blind miss is
   sampling variability (no measurement, probe or structural cause), and at 2 km the relation is shallower and noisier.
   A better predictor would need many more networks and a new pre-registered blind set.
3. Answered (run C): yes, the depth(C) curve and the chemistry match hold at σ 0.

---

## Corrections from Karen's review (v1 → v2)

- Item 3 said focusing peaks before breakthrough "in every run": false. It holds at or before breakthrough in 86 of 90
  sweep runs.
- "5 of 36 beyond 0.05" corrected to 6 of 36. The ×1000 / ×171 medians now include the ninth network (depth 0.15 and
  0.35, breakthrough 0.27, PR_V minimum 0.22).
- Item 1 now reports the full order (87/90 at 1 km, 83/90 at 2 km) and ties, and the true last-state PR_V.
- Item 4 states that t10 is used for both chemistries, reports the 2 km bias and the n of the fastest-path test, and notes
  the largest-fracture share was not computed at 2 km.
- Fig. 2 subsets stated (45 runs in A–B, 60 in C). Fig. 1C numbers quoted from the median curve.
- Wording softened: "one curve / only through C" → coupled sits on the gypsum-only curve at the same C, with the n–C
  separation argued explicitly; "same fractures" → within the initial channel, consistent with inheritance (no null);
  "predicts" restricted to 1 km; no claim that d is the best clock.
- `ceilsweep/channel_overlap.py` now regenerates channel_overlap.csv.

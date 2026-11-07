# Forsmark reactive channels: status (Fri 6 Nov 2026, 11:45 CST)

Report (private artifact): https://claude.ai/artifact/Bt4SbtGrkNoqHrYB2TW5pj. Local copy: `report_phase1/index.html`.
Deck: `deck/Forsmark_Reactive_Channels.pptx`. It has not been rebuilt for report sections 8.9–8.12 yet.

## Where we are

- **Phase 1–3 (1 km, 60 networks × 2 chemistries) are complete.** Flow channelizes in four stages:
  1. pore space opens first;
  2. the front runs down the paths that already carried flow;
  3. flow focuses and breaks through;
  4. flow spreads out again.

  Channel depth follows the achievable permeability gain (the "ceiling"), not the chemistry.
- **New this week (report 8.9–8.12):**
  - **Binned along the flow (8.9).** Each 100 m stretch focuses once as the dissolution front passes, then relaxes. The
    outlet stretch focuses most.
  - **2 km scale test (8.10).** Stage order, inheritance and depth hold. Breakthrough needs a little more of the gypsum
    dissolved. On sparse (×4) 2 km networks the deepest network-wide focusing often comes mid-transit (15 of 20 runs,
    against 5 of 20 at ×8). Corrected 6 Nov pm: counted per geometry this is 4/5 v 0/5 at σ1 (p 0.048) and 3/5 v 1/5 at
    σ0.5 (p 0.52), so it is a lead, not a result (SCALE_TEST.md).
  - **k–φ exponent (8.11).** n = 3 instead of 1 gives a much deeper channel (depth 0.68 → 0.21) in the same fractures.
  - **Literature check (8.12).** The full four-stage sequence was not found in 3D network studies. n = 1 is conservative.
  - **Active surface area** is Hyman's d_Q/P32 exactly (`dQ_P32`), compared with PR_V in report section 4.
- **The 2 km results in the published report** cover 40 runs. `scale2km/SCALE_TEST.md` has 60 (σ 0.5 and σ 1 complete).

## Afternoon additions (Fri 6 Nov, 15:40)

- **External assessment reviewed.** Its reframing (a focusing zone that moves and relaxes, and what sets the timing of the
  network-wide peak) is adopted as the working story. Its two criticisms were right and are now corrected:
  - **2 km statistics** counted runs, not geometries. Per geometry: σ1 ×4 v ×8 at 2 km 4/5 v 0/5 (p 0.048); σ0.5 3/5 v 1/5
    (p 0.52). A lead, not a result (report 8.10, SCALE_TEST.md).
  - **Novelty:** Hyman et al. 2026 Fig. 11 already shows a downstream-moving focusing front, but focusing behind it holds.
    Our relaxation behind the front is what is new (report 8.12, lit/lit_staged_channelization.md).
- **Front-occupancy test (report 8.13, `front_occupancy.py`, rules fixed before running):** the share of 100 m bins that
  are focused does not predict when the network PR_V minimum comes (ρ 0.27–0.50, 28–42 % of runs within 0.05, against a
  pre-set bar of 0.6 and 60 %). Hyman's f50 profile, computed with fractures crossing each plane, is saturated at
  0.94–0.97 and cannot resolve our front.
- **E0 added to the main report (8.11).**
- **Machine note:** the poppler install upgraded Homebrew freetype to 2.15.0, which needs a newer macOS; `import vtk` now
  fails unless run with `DYLD_LIBRARY_PATH=/opt/homebrew/Cellar/freetype/2.14.1_1/lib`. The 2 km queue chain does not
  import vtk and is unaffected.

## Saturday 7 Nov, ~12:00: the story, new report and deck, gap-filling runs

- **New story report (separate from the working report):** https://claude.ai/artifact/6LdBs696iNSuw5MGYzsyCT, local
  `story/report/index.html` (figures, movies, plain + technical text per part, sources).
- **New story deck:** `story/deck/Reactive_Channels_Story.pptx` (23 slides, two embedded movies), rebuild with
  `zsh story/deck/rebuild.sh`.
- **Technical text with every number's source:** `story/STORY.md` (v2, reviewed by Karen; corrections listed at its end).
  Figures `story/fig1-4`, `story/make_story_figures.py`; animation `story/make_story_animation.py`.
- **Predictor upgraded:** early tracer arrival t10/τ (held-out R² 0.77 / 0.75 at 1 km, against 0.62 / 0.55 for the
  largest-fracture share); transfers to 2 km in size, weakly in ranking (`early_arrival_predictor.py`). The fastest single
  path fails (`fastpath_predictor.py`).
- **Gap-filling runs running** (`gapfill/GAPFILL.md`, rules fixed first; launched 11:18, ~16 h): A late-time high gain
  (36), B blind predictor test on 12 new 1 km networks (24), C σ-0 depth law (54).

## Saturday 7 Nov, 07:50: weekend results

- **Ceiling sweep complete** (52 runs, all clean; `ceilsweep/CEILING_SWEEP.md`, figure `ceilsweep/ceilsweep_depth.png`).
  Depth falls with the attainable gain on 9 of 9 networks (R1 pass): median 0.78 at ×5.5, 0.68 at ×10, 0.55 at ×30,
  0.34 at ×100, 0.15 at ×1000 (9 networks), about −0.25 per decade, flattening at high C. Chemistries collapse (R2 pass): coupled
  sits a median 0.021 above gypsum-only at the same ceiling (36 points; 0.014 against the realized network gain).
  Networks reorder across ceilings (rank at ×5.5 v ×1000: ρ 0.08). At n = 3 only 0.49 of the gypsum is dissolved by
  capacity time 2 (0.85 at n = 1).
- **2 km test complete** (90 runs). Stages, inheritance and depth hold; breakthrough later (0.56 → 0.64 gyponly). The
  sparse-network early peak is gone at σ0 (2/5 v 2/5), so it is not a length–density effect (SCALE_TEST.md).
- Not yet in the report or deck.

## Late afternoon (Fri 6 Nov, ~16:00): checks for the story and the weekend set-up

- **Relaxation behind the front is robust to binning** (report 8.9). Counting each fracture in every 100 m bin it spans:
  every bin ends within 2.3 % (gyponly) / 1.3 % (gypcal) of its start; bin minima still move inlet → outlet (ρ 0.94/0.95).
- **What sets the network PR_V minimum** (report 8.13, `prv_decomposition.py`): not the ~21 long fractures (ρ ≤ 0.23) and
  not the outlet stretch (unchanged at the network minimum; its own minimum comes later). It is redistribution inside the
  initial channel upstream of the outlet (which holds 95 % of Σq²/V, so that part is close to a restatement).
- **Weekend DFN comparison locked:** `dfn_validation/sm500_compare.py` (criteria C1–C7 in its header, dry run on the graph
  side reproduces stage_check.csv). Notes appended to `dfn_validation/TARGETED_DFN_WEEKEND.md`.
- **Length series locked and built, not launched:** `lenseries/LENGTH_SERIES.md` (L = 500/1000/2000 × 250 × 250 m,
  ×4/×8, σ1, seeds 11–16, both chemistries, 72 runs, about 10 h on 4 slots). Early peak defined by the front
  (PR_V minimum before the front reaches the last 100 m), tests fixed. Launch with `zsh lenseries/run_lenseries.sh 4`.

### Weekend plan, revised 16:05 after review: one campaign aimed at one figure

Collin asked whether each item gives a result that advances the story rather than more data. Verdict: the DFN is a
model-vs-model check (parked), E1 as planned measures a nuisance (shape, already ±0.04), and the length series tests the
timing of a summary statistic whose mechanism already failed (parked). Both parked items stay ready to launch.

**Running instead: the ceiling sweep** (`ceilsweep/CEILING_SWEEP.md`, locked before running). k = k0 (φ/φ0)^n with
n = 1.48 / 2 / 3, so gypsum-only ceilings ×30 / ×100 / ×1000 (coupled ×12.6 / ×30.8 / ×171), both chemistries, the 9
Phase 3 networks; 52 runs plus existing ×5.5 / ×10 / ×3.3 / ×1000 points. Goal: the figure "channel depth against the
attainable permeability gain, chemistries on one curve". Launched Fri 16:03 (`ceilsweep/run_ceilsweep.sh`), 1 slot
while the 2 km queue runs, 7 after; expected done Saturday afternoon. Analysis: `ceilsweep/analyze_ceilsweep.py`.

Draft figure list for the story: (1) the four stages across 120 runs; (2) the moving focus that relaxes behind the
front; (3) depth against the attainable gain, chemistries collapsed; (4) the initial state predicts breakthrough.
2 km goes in the supplement.

## Running now

| Job | What | Progress | Expected |
|---|---|---|---|
| 2 km scale test, σ = 0 | `scale2km/run_queue_scale2km.py`, 6 slots. ×8 gypsum-only seeds 1–5 and ×6 seed 1 running; ×6 and ×4 σ0 queued | 65 of 90 runs done | ×8 σ0 about Fri night; all about Sat (est.) |
| (done 11:35) E0 k–φ shape pilot | see results below | complete | — |
| (done 11:06) Small-network trial, BiGraFV + DFN mesh | see results below | complete | — |

## New results (Fri 6 Nov, late morning)

- **E0 k–φ shape pilot.** Report: https://claude.ai/artifact/NE8o5SQzGxDbL8b99ttEtV. Local: `phase1/kphi_e0/report/index.html`;
  data in `phase1/kphi_e0/kphi_e0_summary.csv`.
  - Same ×10 ceiling, four shapes. Depth 0.72 / 0.68 / 0.66 / 0.64 for n = 0.5 / 1 / 2 / 8: the later the law delivers its
    gain, the deeper the channel. Breakthrough 0.48 / 0.46 / 0.42 / 0.41.
  - Stage order, inheritance (1.0) and the final network k gain (×9.7–9.8) are unchanged.
  - n = 3 (×1000): depth 0.21. So the ceiling dominates and the shape gives about ±0.04 on this network.
  - That is between the "ceiling is enough" (±0.03) and "path matters" (> 0.05) thresholds. E1 is needed to decide.
  - **Apertures:**
    - Under any ×10 law, open aperture splits in two: about half the fractures open fully, about a third are untouched.
    - Hydraulic aperture grows at most ×2.15 (median 75 → 106–122 µm).
    - n = 3: 13 % of fractures open, to about 1 mm hydraulic aperture.
- **Small-network trial** (500 × 125 × 125 m, r_max 282 m, 381 fractures; `dfn_validation/sm500_r282_p6_s1/stage_check.csv`).
  - **Gypsum-only:** all four stages appear.
    - PR_pore falls while PR_V holds (d 0.01–0.1);
    - PR_V falls to 0.73 of its start just before breakthrough at d 0.60;
    - flow re-spreads to 0.97 of start.
    - Depth 0.68, same as the 1 km median (0.68); breakthrough 0.60 (1 km 0.57); inheritance 0.92 (1 km 0.97).
    - Difference: PR_pore keeps falling until breakthrough, so its minimum (d 0.51) ties with the PR_V minimum.
  - **Coupled:** depth 0.81. The PR_V curve is flat from d 0.41 to 0.71, so its minimum falls just after breakthrough
    (0.69 vs 0.65), a near-tie.
  - **DFN:** meshed with 196,864 cells. Steady flow Q_dfn/Q_graph = 1.69. Estimated reactive cost: gypsum-only to
    capacity time 2, 50–90 core-h; coupled, 2–3 core-h. **Waiting for Collin's go.**

## Waiting on those (next steps, in order)

1. **Weekend DFN on the small network, both chemistries, when Collin says go.**
2. **E1:** start with the ×10 shapes on the 9 networks (27 runs, about one night), if approved.
3. **2 km σ0 results:** finish the scale comparison, update report 8.10 to 90 runs, rebuild the deck.

## Planned (not started)

- **k–φ work plan (`KPHI_WORKPLAN.md`):**
  - E1: same ceiling, different shape; 99 gypsum-only runs on 9 networks.
  - E2: coupled at matched ceiling; 27 runs.
  - E3: n = 3 trends; 18 runs.
  - The decision rules for "ceiling is enough" against "trajectory matters" were fixed before any runs.
- **Deriving n from physics** (`lit/kphi_choice_physics_and_plan.md`, test C): resolve single vein-filled fractures in 2D
  and fit PFLOTRAN's law to them.
- **Exact-network DFN** (`dfn_validation/TARGETED_DFN_WEEKEND.md`, `build_exact_dfn.py`):
  - the figure network's own polygons pass dfnGen at h = 1 m with 2,521 of 2,714 kept;
  - its conductance is 25 % lower than the original;
  - the BiGraFV check on it was stopped (Fri 10:55) in favour of the small-network trial.
- **Report and deck:** add the E0 result and the small-network trial; rebuild the deck.

## Housekeeping this week

- **Disk:** freed 87 GB (Fri 09:50).
  - Deleted: the per-step velocity and cell-info dumps from finished runs (no script reads them), `_to_delete/` and the
    user caches.
  - Kept: all VTK, h5, per-fracture and CSV outputs.
  - Kept at Collin's request: `constant_pressure_ens_kbias_sigma3/` and `reactive_TPL_6x4x4m/`.
- **Code changes:**
  - `deck_gypsum_calcite.py`: new opt-in `--perm-crit-por` (PERMEABILITY_CRITICAL_POROSITY). Default decks are unchanged.
  - `build_rfram_network.py`: new `--domain` and `--rmax`.
  - `build_exact_dfn.py` (new): Phase 1 polygons as dfnWorks user polygons. It works around two pydfnworks/dfnGen issues:
    `stopCondition` ignores user polygons, and user-polygon apertures are misassigned after isolated fractures are removed.
- **This GitHub mirror:** results, scripts and notes only. No raw PFLOTRAN output.

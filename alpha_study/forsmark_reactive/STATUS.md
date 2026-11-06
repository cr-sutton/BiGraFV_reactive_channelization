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

### Proposed weekend order (waiting for Collin's go)

| When | What | Cores |
|---|---|---|
| Now | Coupled DFN on sm500 (pipeline check, 2–3 core-h) | 2 |
| Tonight, when the 2 km σ0 queue drains | Gypsum-only DFN on sm500 to capacity time 2 (50–90 core-h) | 8 |
| Saturday | E1 first step: ×10 ceiling, 4 shapes, 9 networks (27 runs) | 4 |
| Saturday night → Sunday | Length series (72 runs) | 4 |

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

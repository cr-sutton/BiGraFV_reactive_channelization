# Forsmark reactive channels: status (Fri 6 Nov 2026, 11:00 CST)

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
    dissolved. On sparse (×4) 2 km networks the deepest network-wide focusing comes mid-transit (15 of 20 runs, against
    5 of 20 at ×8).
  - **k–φ exponent (8.11).** n = 3 instead of 1 gives a much deeper channel (depth 0.68 → 0.21) in the same fractures.
  - **Literature check (8.12).** The full four-stage sequence was not found in 3D network studies. n = 1 is conservative.
  - **Active surface area** is Hyman's d_Q/P32 exactly (`dQ_P32`), compared with PR_V in report section 4.
- **The 2 km results in the published report** cover 40 runs. `scale2km/SCALE_TEST.md` has 60 (σ 0.5 and σ 1 complete).

## Running now

| Job | What | Progress | Expected |
|---|---|---|---|
| 2 km scale test, σ = 0 | `scale2km/run_queue_scale2km.py`, 6 slots. ×8 gypsum-only seeds 1–5 and ×6 seed 1 running; ×6 and ×4 σ0 queued | 65 of 90 runs done | ×8 σ0 about Fri night; all about Sat (est.) |
| E0 k–φ shape pilot | P32 ×6 σ1 seed 1, gypsum-only, same ×10 ceiling, n = 0.5 / 2 / 8 (φc set so k(φ=1)/k0 = 10). `phase1/run_kphi_e0.sh`, `KPHI_WORKPLAN.md` | about 10,400 of about 25,700 steps | Fri about 12:00, then probes |
| Small-network trial | 500 × 125 × 125 m, FFM01 P32 ×6 σ1 seed 1, r_max 282 m (family P32 kept), relaxed FRAM h = 1 m, 381 fractures. BiGraFV both chemistries (`dfn_validation/run_sm.sh`) | coupled done; gypsum-only running | Fri midday |
| Small-network DFN build | Same network meshed (`build_rfram_network.py --domain 500 125 125 --rmax 282 --stage dfn`) | mesh done; steady flow running | Fri midday |

## Waiting on those (next steps, in order)

1. **E0 result:** a short plain-language report with two figures, `kphi_e0_report.py` → `phase1/kphi_e0/`:
   - law shapes with PR_V and k_eff against the dissolved fraction;
   - histograms of open and hydraulic aperture across all fractures, before reaction and at capacity time 2, for each law.
   Then decide whether to run E1.
2. **Small-network trial:** check that stages 1–4 appear in BiGraFV. If they do, it becomes the weekend DFN candidate:
   - reactive DFN, gypsum-only to capacity time 2, est. 50–90 core-h;
   - reactive DFN, coupled, est. 2–3 core-h.
   **DFN reactive runs start only when Collin says go.**
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

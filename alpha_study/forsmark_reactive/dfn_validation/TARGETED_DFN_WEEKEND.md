# Targeted DFN: 1:1 on the network shown in the four-stage figures (plan, 6 Nov 2026)

**Target.** P32 ×6, σ = 1, seed 1, Phase 1 (1000 × 250 × 250 m, 2,714 fractures). This is the network in report 5c (stage
figures and movies), and it also carries the n = 3 and E0 k–φ runs. The figures show the whole 1 km network (slices at
z = 0 and z = +60 m), so the "portion" is the whole network.

## What we checked today

1. **A rebuild with the same seed is not the same network.** Relaxed FRAM (rFram) with the same seed gives 2,333 fractures,
   and none of them sits within 0.5 m of a Phase 1 fracture centre (67 within 5 m). The earlier rf_* validation networks
   are therefore different realizations, not the Phase 1 networks.
2. **Our exact polygons can be fed to dfnWorks.** build_exact_dfn.py passes the Phase 1 polygons.dat and transmissivities
   in as user-defined polygons, with rFram on at h = 1 m.
   - At h = 1 m, rFram rejects **150 of 2,714 (5.5 %)**, all for "intersection shorter than h".
   - Those 150 carry about 9 % of the summed initial fracture throughflow. 39 of them are in the initial 90 % flow set
     (458) and 21 in the peak-channel set (228).
   - dfnGen then stopped with "no intersecting fractures". This is a user-polygon set-up problem still to debug: probably
     the polygons that lie exactly on the x = ±500 m faces. The flow model was not reached.
3. **Size estimate:** about 1.5 M DFN cells. This scales the intersection-length fit by the ratio observed on rf x4 seed 3.
   Memory is about 8–16 GB.

## Is a strict 1:1 possible? Yes, in one of two forms

- **A. Same network minus 150 fractures (recommended).**
  - Generate the DFN from the exact polygons and accept the rFram rejections.
  - Rebuild the one-cell BiGraFV graph from the *same* dfnGen output, so both models have identical fractures and
    transmissivities.
  - Rerun BiGraFV on that graph in both chemistries (cheap, about 1 h) and compare it with the Phase 1 run. This shows
    directly whether removing the 150 fractures changes stages, depth or channel set on the figure network.
  - The DFN vs graph comparison is then exact, fracture by fracture.
- **B. Keep all 2,714 by modifying geometry.** Slightly extend or trim the 150 polygons so their intersections are at least
  1 m long, or mesh at h = 0.5 m (about 3 M cells, will not fit in 24 GB). B changes the geometry or cost more than A
  changes the network, so we prefer A.

## Weekend schedule (if you say go)

| When | Step | Cost |
|---|---|---|
| Fri afternoon | Fix the user-polygon dfnGen set-up; generate; build the graph from the same output; mesh with LaGriT (min 0.5 h, max 10 h); steady-flow gate: Q_dfn/Q_graph, no NaN, conformity | 2–4 h, 2–4 cores |
| Fri evening | BiGraFV on the A-network, both chemistries; compare with Phase 1 (does the 5.5 % matter?) | about 1 h |
| Fri night → Sun | **DFN coupled** to capacity time 2 | est. 20–35 core-h |
| Fri night → Mon | **DFN gypsum-only** to capacity time 0.6, past breakthrough (the stage-3 frame is at 0.43), with a checkpoint to continue | est. 120–250 core-h |
| Mon | 1:1 analysis | — |

The full gypsum-only run to capacity time 2 (est. 460–900 core-h) does not fit a weekend.

**Machine.** The DFN needs about 8 ranks and up to 16 GB. The 2 km σ0 queue (about 25 runs) and E0 use the cores now. For
the weekend, either:
- cap the 2 km queue at 2 slots; or
- let it finish first (about Saturday) and start the gypsum-only DFN then.

## 1:1 analysis (same measures for both models, fracture by fracture)

- The DFN cells are mapped to fracture IDs (materialid), so per-fracture flow, porosity and dissolved fraction can be
  compared directly with the graph.
- **Network measures:**
  - PR_V, PR_pore, d_Q / P32;
  - stage events (pore-volume minimum, outlet 5 %, PR_V minimum, breakthrough);
  - depth, inheritance;
  - n90 and the channel set (Jaccard DFN vs graph);
  - k_eff.
- **The x-binned front (8.9) for both models,** to answer whether the same fractures open in the same order.
- **Per fracture:** dissolved fraction and flow share at each stage time, as a scatter of DFN against graph, with the
  fractures that change rank listed.
- **Pass criteria:** as in dfn_validation/gate_check.py (stage order, t50 guard, k_eff band), fixed before the run.

## Risks

- **LaGriT can fail on a 1.5 M-cell mesh.** On rf x4 seed 2 it segfaulted. The fallback is the rf_p4 seed 1 or 3 network,
  which is already meshed, but that is not the figure network.
- **The dfnGen user-polygon problem may need a dfnWorks fix.** The `stopCondition` check in readInput.cpp ignores
  userPolygonByCoord. A workaround is in the script.
- **The 150 rejected fractures include 21 peak-channel fractures.** Form A must show on BiGraFV that this does not change
  the channel. If it does, the DFN comparison is on a different channel and we say so.

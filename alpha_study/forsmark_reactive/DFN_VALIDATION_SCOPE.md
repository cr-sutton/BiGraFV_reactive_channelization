# DFN validation of one-cell BiGraFV on the Forsmark networks: scope (4 Nov 2026)

Scoping only. No reactive simulation was run. I did run dfnWorks network generation (about 30 networks) and
six LaGriT mesh tests at low priority (`nice -n 10`, 2 cores, while about 12 other PFLOTRAN ranks were running;
load 17–34). Everything marked **est.** is an estimate. Its basis is given in section 4.
Scratch files are in `/private/tmp/claude-501/-Users-collin-Projects-bipartite-pflotran-src-alpha-study/4bb44bc2-48f5-4f4b-bcf1-243f8b14a913/scratchpad/dfnscope/`
(`gen_mesh_test.py`, `est_options.py`, `options_estimates.csv`, `mc_est.csv`, the mesh-test folders and `*_summary.json`).

Note: `STUDY_SCOPE.md` and `OPTIONS.md` put DFN validation outside the Forsmark study unless the user asks for it.
This file is the scope the user asked for. It changes nothing in the Phase 1 or Phase 2 plan.

## 1. Bottom line

1. **The Phase 1 networks cannot be meshed.** `network_forsmark.configure` sets `disableFram = True`. When FRAM
   is off, pydfnworks prints "Mesh will not work for DFN flow and transport". A DFN validation therefore needs
   newly generated networks, and the graph must be rebuilt from the same `dfnGen` output so that the comparison is 1:1.
2. **Full FRAM changes the network. Relaxed FRAM (`rFram`) does not.** All counts below are at h = 1 m, seed 1,
   1 km domain:

   | network | fractures | node-disjoint paths | dead-end fractures |
   |---|---|---|---|
   | x4, Phase 1 (FRAM off) | 1,608 | 11 | 247 |
   | x4, full FRAM | 1,123 | 2 | 528 |
   | x4, rFram | 1,605 | 9 | 273 |
   | x8, Phase 1 (FRAM off) | 3,812 | 39 | 153 |
   | x8, full FRAM | 4,785 | 12 | 1,637 |
   | x8, rFram | 3,376 | 40 | 112 |

   Seed 2 behaves the same way: rFram x4 has 1,468 fractures and 10 paths; rFram x8 has 3,456 fractures and 42 paths.
   rFram networks mesh. In the 250 m test, 0.60 % of intersection edges did not conform (617 of 102,424).
3. **h = 1 m is the only resolution that keeps the Phase 1 fracture definition.** dfnGen requires the shortest
   polygon edge to be at least 3h. A 16-gon with r_min = 15 m has 5.85 m edges, so h can be at most 1.95 m.
   - **h = 2 m** works only with 8-point polygons (octagons). The rFram networks then look like Phase 1:
     x4 has 1,573 fractures, 7 paths and 215 dead ends; x8 has 3,708 fractures, 41 paths and 121 dead ends.
   - **h = 5 m** is refused even with hexagons. It would need r_min of about 38 m (16-gons) or polygons with
     5 points or fewer.
   - **Full FRAM at h = 1.9 m** cuts x4 down to 502 fractures and 1 path.
4. **Cell count follows intersection length, not fracture area.** dfnWorks' default mesh is fine near
   intersections (h/2) and coarse away from them (up to 10h). A fit to four Forsmark meshes at h = 1 m gives,
   within ±5 %:

   **N_cells ≈ 0.0271 · A/h² + 6.17 · L_int/h**

   where A is the one-sided connected fracture area and L_int is the total length of fracture–fracture
   intersections. The L_int term holds 85–90 % of the cells. An h = 2 m test mesh came out 9 % above this fit.
   Each mesh has about 3.4 connections per cell.
5. **Gypsum-only runs set the cost; coupled runs are cheap.** To capacity time 2 at 1 PV/yr (dt cap 0.57 τ),
   the BiGraFV runs take 25,700 steps for gypsum-only (14,606 PV) and 870–930 steps for coupled (466.6 PV).
   At the same step counts, the 1 km x4 DFN at h = 1 m (about 0.78 M cells) needs:
   - **est.** 240–470 core-h for gypsum-only (2–4 days on 6 ranks);
   - **est.** 9–17 core-h for coupled (2–4 h);
   - **est.** 4–8 GB of memory.

   x8 at 1 km (2.9 M cells, 16–29 GB) does not fit in this laptop's 24 GB. x16 (11 M cells) is far out of reach.
6. **Recommendation: 1 km x4, rFram, h = 1 m, sigma 1.0, seed 1, both chemistries.** Run coupled to capacity
   time 2 first. Then run gypsum-only to capacity time 1, with a checkpoint so it can be restarted to time 2.
   On the same network run the one-cell BiGraFV graph and the Delaunay multiport graph (mc4hd-Delaunay, about
   10 core-h). Skip the all-to-all mc4hd graph: here it costs as much as the DFN. Section 6 has the plan.

## 2. Past DFN, mc4hd and one-cell reactive runs (measured)

Sources: `docs/figures/cost/cost_summary.csv` and `cost_table.csv` (from `docs/make_cost_figures.py`), the
`.out` and `pflotran.stdout` files of the runs, and `forsmark_reactive/phase1/run_times.csv`. The DFN ran on
3 ranks with the iterative solver. The TPL graphs ran on 1 core with direct LU. The Forsmark graphs ran on
2 ranks with the iterative solver.

| campaign | network, h | DFN cells | one-cell / mc4hd cells | steps | median wall DFN / mc4hd / one-cell | DFN core-h |
|---|---|---|---|---|---|---|
| TPL 1:1 (15 DFN runs) | 6x4x4 m, h 0.1 m | 9,256–9,836 | 58–73 / 114–124 | ~20 k | 58 min / 127 s / 15 s | 2.9 (1.0–5.3) |
| Track B1/B3 coupled | 6x4x4 m, h 0.1 m | 9,807 / 9,836 | 68–73 / 115–124 | ~33 k | 78–79 min / 140–152 s / 24–26 s | 3.9–4.0 |
| dense sweep | 8x5x5 m, h 0.15 m | 17,382–20,759 | 231–261 / 372–442 | ~33.5 k | 118 min / 454 s / 74 s | 5.9 |
| Track C | 8x5x5 m, h 0.15 m | 17,382 | 231 / 372 | ~34.6 k | 140 min / 431 s / 91 s | 7.0 |
| Track D2, mesh h vs h/2 (4221, coupled) | h 0.1 → 0.05 m | 9,807 → 36,219 | – | 33,231 / 32,954 | 75 min → 288 min | 3.8 → 14.4 |
| Forsmark x4, gyponly to 36.5 k PV | 1 km, graph | – | 6,567 | 64,139 | 1,965 s (2 ranks) | 1.1 (graph) |
| Forsmark x16, gyponly to t_cap 2 | 1 km, graph | – | 78,669 | 25,703 | 16,365 s (2 ranks) | 9.1 (graph) |
| Forsmark x16, gypcal to t_cap 2 | 1 km, graph | – | 78,669 | 927 | 960 s (2 ranks) | 0.53 (graph) |

How the cost scales (measured):
- **DFN cost is nearly linear in cells at a fixed step count.** Going from h to h/2 multiplied the cells by
  3.69 and the wall time by 3.82. Cost per cell-step was 4.16e-5 and 4.34e-5 core-s. Linear iterations per
  Newton step rose from 8.2 to 11.1.
- **DFN and graph take the same number of steps on the same deck.** In B1 the counts were 33,231 vs 33,190.
  The step count is set by the dt cap and the chemistry, not by the mesh.
- **On Forsmark, the one-cell graph's cost per cell-step grows with size.** It goes from 9.3e-6 core-s (x4,
  6.6k cells) to 1.62e-5 (x16, 78.7k cells), roughly N^0.22. I use this exponent as the upper bound for
  iteration growth in the DFN.
- **mc4hd costs about 6x the one-cell graph on the TPL networks**, with 1.7x the cells and 14x the
  connections: build_multicell_graph.py couples every port on a fracture to every other port.
  mc4hd-Delaunay (`graph_mc4hddelg`) costs 0.42–0.64x mc4hd.
- **Memory (measured).** Forsmark graph PFLOTRAN ranks hold 46 MB each at x4 and 61 MB each at x6. That is
  about 4.6 KB per extra cell at 1.5 connections per cell.

**Correction to the 1 Nov cost study.** `make_cost_figures.py::_dfn_area` reads the first "Total Surface Area"
in `DFN_output.txt`. That number is two-sided and counts fractures before isolated ones are removed (TPL 4221:
377.6 m² there, 74.9 m² in `surface_area_Final.dat`). The quoted 0.25–0.39 "DFN cells per (area/h²)" is
therefore too low by roughly 5x. With the one-sided connected area the TPL meshes give 1.15–1.45. That is
close to a uniform mesh, because every TPL fracture lies within about 10h of an intersection. Also, for
large fractures the cell count follows L_int, not area (section 1, item 4), so area-based extrapolation is
the wrong model there. The 1 Nov estimate of 4.4–7 M DFN cells for the 500 m seed 21 network is not a
reliable basis. With the fit above it would be about 1e7 cells (L_int 1.62e6 m), **est.**, if that
orthogonal network could be meshed at all.

## 3. Mesh tests run today (rFram/FRAM, h = 1 m unless noted, default variable mesh)

| network | fractures | A one-sided (m²) | L_int (m) | cells | connections | fit error | mesh time | peak RSS |
|---|---|---|---|---|---|---|---|---|
| 250 m block x4, full FRAM | 261 | 9.05e5 | 1.29e4 | 103,999 | 350,703 | +0.2 % | 74 s | 0.55 GB |
| 500x250x250 x4, full FRAM | 613 | 1.84e6 | 2.63e4 | 212,943 | 715,991 | −0.4 % | 256 s | 1.28 GB |
| 250 m block x8, full FRAM | 1,290 | 2.00e6 | 4.89e4 | 359,950 | 1,222,392 | −1.1 % | 495 s | 1.82 GB |
| 250 m block x4, rFram | 235 | 1.10e6 | 2.55e4 | 178,375 | 620,851 | +4.7 % | 111 s | 1.40 GB |
| 250 m block x4, rFram, h = 2 m, octagons | 495 | 1.06e6 | 2.60e4 | 95,542 | 320,178 | −8.7 % (fit low) | 84 s | 0.51 GB |

Disk: the full_mesh `.inp`, `.uge` and `.stor` files take about 1.3 KB per cell together.

Statistics of the generated networks: `options_estimates.csv` / `mc_est.csv`. Domain blocks were generated
from the same FFM01 statistics, not cut from the 1 km network. Their path counts are close to the 1 km values
because, as the blocks show, the path count is set by the y–z cross-section: x4 has 9–11 paths at 250 m,
500 m and 1 km, and x8 has 40–44.

## 4. Cost model (basis of every **est.**)

- **Cells.** DFN cells come from the fit in section 1 (×1.09 at h = 2 m). Graph cells come from the
  generated rFram networks: one-cell ≈ fractures + intersections + boundary helpers. That runs about
  20 % below the built Phase 1 graphs (6,567 cells vs 5,459 estimated for x4 seed 1). mc4hd cells are
  ceil(L/4h) sub-ports per intersection (capped at 32) plus the one-cell nodes. mc4hd connections are
  Σ P(P−1)/2 per fracture (the `_mc4hd_estimate` rule). Delaunay connections are Σ max(3P−6, P−1); the
  same rule gives 2.6e6 for 500 m seed 21, where the built model has 2.07e6, so this is about 25 % high.
- **Steps (measured on the Forsmark graph runs).** Gyponly: 25,700 steps to t_cap 2 and 12,860 to t_cap 1.
  Gypcal: 930 steps to t_cap 2. The DFN is assumed to take the same steps (it did on TPL).
- **DFN cost.** Low: 4.3e-5 core-s per cell-step, flat (Track D2, 3 ranks). High: the same times
  (N/3.6e4)^0.22 for iteration growth. Wall time assumes 80 % parallel efficiency on free cores.
- **Graph cost.** One-cell: 1.62e-5 core-s per cell-step, ×(N/7.87e4)^0.22 for the high value. mc4hd and
  Delaunay: 9.2e-6 core-s per connection-step (Forsmark x16), ×(C/1.39e5)^0.22 for the high value.
- **Frozen-state probes** (k_eff, breakthrough) add another 20–40 % (cost-study note). They are not
  included below.
- **Memory.** DFN: 5.5–10 KB per cell, **est.** The basis is the measured 4.6 KB per graph cell plus 5×5
  Jacobian and ILU blocks for 3.4 connections per cell; it has not been measured on a DFN. Graphs: 3 KB per
  cell plus 2 × 204 B × (cells + 2 connections), plus a 0.12 GB base.
- **Laptop.** 14 cores; RAM 25,769,803,776 B (24 GB, `sysctl hw.memsize`); 174 GB free disk. The run
  script's memory guard kills a run when free memory falls below 15 %. While scoping, about 12 other
  PFLOTRAN ranks were running.

## 5. Options (h = 1 m 16-gons unless noted; seed 1; rFram networks; every number is an estimate)

Core-h: gyponly is to capacity time 2 (time 1 is half of that); gypcal is to capacity time 2.
Wall times are on 6 ranks.

| option | model | cells | gyponly core-h | gypcal core-h | memory | laptop feasibility |
|---|---|---|---|---|---|---|
| **1 km x4** (1,605 fr, 9 paths) | DFN | 0.78 M | 240–470 (50–100 h) | 8.7–17 (2–4 h) | 4.3–7.8 GB | **yes** (gyponly is a 2–4 day lane; t_cap 1 halves it) |
| | one-cell | ~5.5 k | 0.6 | 0.02 | 0.2 GB | yes |
| | mc4hd all-to-all | 34 k, 5.7e6 conn | 380–850 | 14–31 | 5–7 GB | no gain over the DFN |
| | mc4hd-Delaunay | 34 k, 1.6e5 conn | 11 | 0.4 | 0.4–0.6 GB | yes |
| **1 km x4, h = 2 m octagons** (1,573 fr, 7 paths) | DFN | 0.40 M | 120–210 (26–44 h) | 4.5–7.6 (1–1.6 h) | 2.2–4.0 GB | yes (half the cost; fracture shape changes) |
| 1 km x4 seed 2 | DFN | 0.78 M | 240–470 | 8.6–17 | 4.3–7.8 GB | yes (coupled only is worthwhile) |
| 1 km x8 (3,376 fr, 40 paths) | DFN | 2.9 M | 900–2,400 | 33–85 | 16–29 GB | **no** (memory; mesh merge ~15–23 GB) |
| | mc4hd-Delaunay | 134 k, 6.7e5 conn | 44–63 | 1.6–2.3 | 1.1–1.7 GB | yes |
| 1 km x8, h = 2 m octagons (3,708 fr, 41 paths) | DFN | 1.5 M | 460–1,040 (4–9 days) | 17–38 (3.5–8 h) | 8–15 GB | gyponly no; gypcal only with the queue paused |
| 1 km x16 (6,552 fr, 130 paths) | DFN | 11 M | 3,400–12,000 | 120–440 | 60–110 GB | no |
| 500x250x250 x4 (544 fr, 11 paths) | DFN | 0.40 M | 120–210 | 4.5–7.6 | 2.2–4.0 GB | yes |
| 500x250x250 x8 (1,798 fr, 42 paths) | DFN | 1.4 M | 430–970 | 16–35 | 7.8–14 GB | gypcal marginal; gyponly no |
| 250 m block x4 (235 fr, 11 paths) | DFN | 0.19 M | 57–82 (12–17 h) | 2–3 | 1.0–1.9 GB | yes, cheapest |
| 250 m block x8 (825 fr, 44 paths) | DFN | 0.73 M | 220–430 | 8–16 | 4–7 GB | yes (x8 density at x4-1 km cost) |
| any of the above | one-cell | 0.9–67 k | 0.1–7.7 | ≤ 0.3 | < 0.7 GB | yes |

The all-to-all mc4hd graph costs about as much as the DFN on every option, and its memory is 15–51 GB at
x8, so I left it out of the table except at 1 km x4. mc4hd-Delaunay costs 2–11 core-h (gyponly) on the x4
options and 11–63 core-h at x8. Its builder needs `--lowmem`: at 500 m seed 21 the build took 29 min and
7.8 GB with up to 6,168 ports per fracture, and the Forsmark x4 and x8 networks reach 1,300–2,800 ports.

**Setup time (est.).** DFN meshing and `lagrit2pflotran` for 1 km x4: about 20–30 min and 4–6 GB. For x8:
1–2 h and about 15–23 GB. Add the steady-flow solve (minutes).

### What each option can validate

| metric | 1 km options | 500 m / 250 m blocks | mc4hd-Delaunay (vs DFN) |
|---|---|---|---|
| Inheritance: overlap0, Jaccard of the peak channel against the initial backbone, flow_in_initial_set | yes | yes, on the block's own backbone | yes |
| Stage timing against dissolved fraction (n90 / PR_pore minima, t_cap of outlet50) | yes | yes in-block, but outlet timing is for L = 250–500 m | yes |
| Channel depth / flow-focusing profile along x (wormhole vs channel) | **yes** | no: truncated, and Da_L is 2–4x lower | partly (fracture-level only) |
| Breakthrough at 1 km (outlet dissolution, t_cap outlet50) | **yes** | no: shorter L | yes |
| In-fracture fronts and in-plane participation (TPL: 0.26–0.31) | yes, at 0.5 m near intersections and up to 10 m (h = 1) or 20 m (h = 2) in the far field | yes | no (only the DFN resolves them) |
| Sealing at intersection throats (coupled; DFN-only on TPL) | yes, but post-seal k_eff depends on the mesh (Track D) | yes | no graph has sealed so far |

The one-cell runs on the rFram networks are the 1:1 partner in every option. They are also the check that
an rFram network sits inside the Phase 1 ensemble.

## 6. Recommendation and run plan

**Option: 1 km x4, rFram, h = 1 m (16-gons, as Phase 1), sigma 1.0, seed 1.** This is the only option that
fits in memory and still validates all five targets, including channel depth and 1 km breakthrough. Its path
count (9 against Phase 1's 11) and dead-end count (273 against 247) match Phase 1 x4. The blocks fit in
memory too, but they cannot validate channel depth or 1 km breakthrough. Total **est.** budget:
- coupled lane: about 10–20 core-h;
- gypsum-only lane: about 120–240 core-h to t_cap 1, or 240–470 core-h to t_cap 2;
- probes: +20–40 %.

1. **Stage 0: build and check the network (about 1 core-h).**
   - Add an rFram option to the network build. It must not touch the existing networks. In code:
     `framOn = True`, `disableFram = False`, `rFram = True`, h = 1. Use network_forsmark settings for
     everything else (FFM01 layer 2, r_min 15 m, x4, sigma 1.0, seeds 1 and 2).
   - Build the one-cell graph from the same `dfnGen` output.
   - Run one-cell gyponly and gypcal to t_cap 2 (about 0.6 core-h). Check that n90/PR_pore dynamics, dQ,
     inheritance and outlet50 timing fall inside the Phase 1 x4, sigma 1.0 envelope (5 seeds).
   - Gate: if the network falls outside that envelope, report it and choose another seed before meshing.
2. **Stage 1: build and check the DFN (about 1 h).**
   - Mesh at h = 1 m (`mesh_network` defaults), run `lagrit2pflotran`, then the steady flow solve.
   - Check, at 1 PV/yr with `EXFIX_DFN="--area 1e-6"` (Track H) and the inlet manifold:
     - the DFN pore volume and τ against the graph's;
     - k_eff from the DFN and from the graph;
     - flow mass balance;
     - that the non-conforming 0.6 % of intersection edges do not split the flow.
   - Build mc4hd-Delaunay (`--lowmem --fit-p0-min-span 1e-12`).
3. **Stage 2: coupled lane.** Run gypcal (0.5 M CO3 brine, phase1 deck) to t_cap 2 on the DFN (6 ranks,
   iterative solver) and on mc4hd-Delaunay. Write checkpoints at t_cap 0.02 0.05 0.1 0.25 0.5 0.75 1 1.5 2,
   with VTK at those times only (about 1–2 GB, against about 9 GB at the Phase 1 output frequency). **est.**
   2–4 h wall. Watch steps per PV over the first 1 %. Stop and reassess if dt falls below about 0.1 τ.
4. **Stage 3: gypsum-only lane.** Run gyponly on the DFN to t_cap 1 (12,860 steps), keeping a restart
   checkpoint, and run mc4hd-Delaunay to t_cap 2. **est.** 25–50 h wall on 6 ranks. Phase 1 x4 reaches its
   n90 minimum at about 3,100 PV (t_cap ≈ 0.42), so channel formation and stage timing fall inside t_cap 1.
   Restart to t_cap 2 (another 25–50 h) only if the comparison of late states needs it.
5. **Stage 4 (optional).** Run seed 2 coupled on the DFN (about 10–20 core-h) for a second sample of
   inheritance, stage timing and sealing.
6. **Analysis.**
   - Map DFN cells to fractures with `materialid.dat` (as `extract_tpl_fractures_by_state.py` and
     `analyze_channelization_tpl.py` already do for TPL).
   - Use `analyze_dfn_infracture_channels.py` for in-plane fronts.
   - Compare on capacity-normalised time and dissolved fraction, never at run end, and per sigma (the
     user's 3 Nov preferences).
   - Fix the criteria before the runs, as in Track B: totals within 10 %, k_eff RMS ln error ≤ 0.182,
     Spearman ρ ≥ 0.7 per fracture, plus the Forsmark metrics (n90-minimum timing against dissolved
     fraction, overlap0, outlet50 t_cap).

The cheapest x8 check is the 250 m block x8 coupled lane (**est.** 8–16 core-h), if a density check is wanted.

## 7. Main risks

1. **Not the Phase 1 networks.** The validation network is a new rFram network with matching statistics.
   It is not one of the 150 Phase 1 networks. Stage 0 has to show it is representative.
2. **rFram is not fully conforming.** 0.6 % of intersection edges were missed at h = 1 m, 1.4 % at h = 2 m
   with octagons. The steady-flow check should confirm this does not cut flow paths.
3. **Time step.** The DFN step count is assumed equal to the graph's (dt cap 0.57 τ, which closed mass
   balance on the graphs). Mass balance at 0.57 τ has not been checked on a DFN, and the coupled
   precipitation front may force cuts. Every 2x in steps doubles gyponly: at 10x steps the gyponly lane
   cannot run.
4. **Solver.** The DFN needs the parallel iterative solver: this PETSc build has no parallel direct LU, and
   a serial LU on 0.78 M cells × 5 dof would need tens of GB. The quartz TPL DFN once diverged with the
   iterative solver (`DFN_DIRECT` note in `run_reactive_case_exfix.sh`).
5. **Cost and memory are extrapolated about 20x in cells** from the 36 k-cell Track D2 run. The high-end
   N^0.22 iteration growth is already in the ranges, but DFN memory has not been measured. A 10-step DFN
   smoke test (minutes) would replace both estimates with measurements before the long lane. It is the first
   thing to run once runs are allowed.
6. **Machine contention.** The wall times assume 6 free cores at 80 % efficiency. The machine was at load
   17–34 during these tests. The gyponly lane holds 6 cores and 5–8 GB for days, and the memory guard
   (15 % free) can kill it if other runs grow.
7. **Sealing changes the comparison.** On TPL the DFN sealed intersection throats while no graph did, and
   post-seal k_eff depended on the mesh (Track D, h vs h/2). If the Forsmark coupled DFN seals, k_eff after
   the seal is not mesh-converged at h = 1 m. Report the seal, and leave the post-seal k_eff unvalidated.
8. **No DFN tooling for the Forsmark runs yet.** The Forsmark run script and analysis scripts are
   graph-only. They need a DFN variant (copy files, EXFIX_DFN, NP ranks, no helper-cell handling) and a
   cell-to-fracture mapping for channel_fractures-style tables. That is about a day of coding, separate
   from the runs.

## 8. Built and smoke-tested (5 Nov 2026)

- Network: `dfn_validation/build_rfram_network.py` -> `dfn_validation/rf_p4.0_sg1.0_seed1/` (x4, sigma 1, seed 1, rFram, h = 1 m):
  1,605 fractures, 3,808 intersections, 9 node-disjoint paths, 321 dead ends (Phase 1 seed 1: 1,608 / 3,791 / 11 / 276).
- Mesh: 758,183 cells, about 5 min (machine loaded). LaGriT wrote NaN Voronoi volume for cells 114427 and 114467 and NaN area for
  their shared face; `repair_uge_nan.py` sets each volume to the median of its neighbours and the area to 0 (uge_repair.json).
- Steady flow (6 ranks, 7 min): Q_in 2.861e-5, Q_out 2.868e-5 m3/s; 1.43x the one-cell graph (2.007e-5) at the same pressure drop.
  DFN fracture volume 524.3 m3 -> 52.43 m3/y at one pore volume per year.
- Smoke (`run_dfn_case.sh ... 40`, Phase 1 deck settings, EXFIX_DFN --area 1e-6, steady start, TS_ACCEL 10, 6 ranks, load ~22):
  coupled 15.7 s/step, peak 9.2 GB; gypsum-only 16.6 s/step, peak 9.7 GB; no cuts, no solver errors (the "error" flag in
  smoke.json is the SIGTERM used to stop at 40 steps). The dt ramp matches the graph run step for step.
- Projection with the graph step counts on this network (coupled 908 to t_cap 2; gypsum-only 12,885 to t_cap 1, 25,703 to t_cap 2):
  coupled ~4.0 h wall (24 core-h); gypsum-only ~59 h (357 core-h) to t_cap 1, ~118 h (711 core-h) to t_cap 2.
  That is 1.5-3x the section 5 estimates; memory 9-10 GB against 4.3-7.8 GB estimated. Costs at the 0.57 y step with active
  fronts are not yet measured.

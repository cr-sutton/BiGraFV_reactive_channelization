# Length series: does peak focusing come earlier on longer, sparser networks? (locked 6 Nov 2026, before any run)

**Why.** At 2 km (2000 × 500 × 250 m) the network PR_V minimum came mid-transit on most sparse (×4) networks. Counted per
geometry this is only a lead (σ1: 4/5 v 0/5, p 0.048; σ0.5: 3/5 v 1/5, p 0.52), the 0.35 split was chosen after
looking, and that test changed length and width together. This series changes only the length, on new geometries.

## Design (fixed)

| Factor | Levels |
|---|---|
| Length L (flow direction) | 500, 1000, 2000 m; width 250 m and thickness 250 m at every L |
| Density | P32 ×4 and ×8 |
| σ | 1 only |
| Geometries | seeds 11–16 (6 new networks per cell; Phase 1 used seeds 1–5 at 1000 m) |
| Chemistry | gypsum-only (primary) and coupled (reported with the same tests) |

Everything else is Phase 1: FFM01 layer 2, r_min 15 m, r_max 564 m (same size law at every L), one-cell BiGraFV, one
pore volume per year, φ0 0.1, n = 1, deck flags and checkpoints of the Phase 1 queue (tag phase1), runs to capacity
time 2. Builder `build_one.sh`, queue `make_queue_lenseries.py` → `run_list_lenseries.txt` (72 runs), runner
`run_queue_lenseries.py` (per-fracture states in `paraview/LS__*`; no tracer probes), launcher `run_lenseries.sh`.

## Measures (fixed)

- Flow re-solved at every saved state (as `scale2km/compare_scale.py`), events within capacity time ≤ 2.
- **Early peak (primary):** the network PR_V minimum comes before the front reaches the outlet window, i.e.
  d(PRV_min) < d(outlet5), where outlet5 is the first state at which the flow-weighted dissolved fraction of the
  fractures with centre in the last 100 m exceeds 0.05 (same 100 m window at every L). This is defined by the front,
  not by a dissolved-fraction cut. On the earlier runs (training data, not part of this test) it gives ×4: 0.6–0.7
  (1 km), 0.9–1.0 (2 km × 500 m wide); ×8: 0.3 (1 km), 0.2–0.6 (2 km).
- **Two dips (secondary):** number of local minima of PR_V / start against d with prominence ≥ 0.03.
- Also reported: depth, breakthrough d, inheritance.

## Tests (fixed)

Unit = one geometry (seed) for one chemistry. Gypsum-only is primary.

1. **Length effect.** At ×4, the share of early-peak geometries rises with L: Cochran–Armitage trend test over
   L = 500 < 1000 < 2000 (6 geometries each), one-sided p < 0.05.
2. **Density effect at the longest L.** At L = 2000, ×4 share > ×8 share, Fisher exact one-sided p < 0.05.
3. Verdict: "length and density both matter" if 1 and 2 pass; "length only" / "density only" if one passes;
   "not supported" if neither. The same tests on coupled are reported and do not change the verdict.

## Cost (estimate)

Gypsum-only run time scales with cell count; 2000 × 250 m has about half the cells of the 2 km test networks:
×8 about 3 h, ×4 about 0.7 h at L = 2000; about 1.5 h and 0.5 h at 1000; under 0.5 h at 500. Coupled runs take
5–30 min. Total about 40 run-hours at 2 ranks each, about 10 h wall on 4 slots.

Analysis: `analyze_lenseries.py` → `lenseries_runs.csv`, `lenseries_tests.csv`.

## Built (Fri 6 Nov, 16:10): all 36 networks, connected

| L (m) | P32 | networks | fractures (median) | node-disjoint paths (min / median) | backbone fraction |
|---|---|---|---|---|---|
| 500 | ×4 | 6 | 872 | 7 / 10 | 0.83 |
| 500 | ×8 | 6 | 2,019 | 41 / 46 | 0.96 |
| 1000 | ×4 | 6 | 1,765 | 7 / 8 | 0.82 |
| 1000 | ×8 | 6 | 3,881 | 36 / 40 | 0.96 |
| 2000 | ×4 | 6 | 3,480 | 6 / 8 | 0.82 |
| 2000 | ×8 | 6 | 7,763 | 34 / 39 | 0.95 |

Fracture count doubles with L while the number of independent paths and the backbone fraction stay the same, so
length is the only thing that changes within a density. Not launched: waiting for the go.

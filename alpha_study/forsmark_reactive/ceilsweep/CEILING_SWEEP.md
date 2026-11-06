# Ceiling sweep: how does channel depth depend on the attainable permeability gain? (locked 6 Nov 2026, before any run)

**Purpose.** This replaces the weekend DFN, E1 and the length series. It turns "depth is set by the ceiling, not the
chemistry" into a measured relationship, depth(C), across networks and both chemistries. Only BiGraFV is used.

## What we already have (9 networks: P32 ×4/×6/×8, σ 1, seeds 1–3)

| Run | Law | Gypsum-only ceiling C | Coupled ceiling |
|---|---|---|---|
| phase3_phi0182 | n = 1, φ0 = 0.182 | ×5.49 | ×3.27 |
| phase1 | n = 1, φ0 = 0.1 | ×10 | ×5.55 |
| kphi_n3 (×6 seed 1 only) | n = 3 | ×1000 | ×171 |

Coupled ceiling = (φ_end / φ0)^n with φ_end = 1 − v_f0 Γ, Γ = V_cal / V_gyp = 0.494 (full replacement).

## New runs (53 queued; `run_list_ceilsweep.txt`)

k = k0 (φ / φ0)^n with φ_c = 0 (PFLOTRAN's default form), φ0 = 0.1, n = log10 C:

| Tag | n | Gypsum-only C | Coupled C |
|---|---|---|---|
| ceilN148 | 1.4771 | ×30 | ×12.6 |
| ceilN2 | 2 | ×100 | ×30.8 |
| ceilN3 | 3 | ×1000 | ×171 |

Both chemistries, all 9 networks (the ×6 seed 1 n = 3 pair is reused). Everything else is Phase 1, to capacity time 2.

**Why a power law and not a critical porosity.** A critical-porosity law reaching ×100–×1000 with the linear shape needs
φ_c of 0.091–0.099, just under φ0 = 0.1. Porosity falls below φ0 in some cells: calcite in the coupled runs (down to the
0.001 floor; 29–232 cells on the three networks checked) and re-precipitated gypsum in one gypsum-only network (0.06).
Those cells would drop to the permeability floor, an artificial seal. The power law is smooth below φ0. The cost is
that the shape becomes more convex as n rises; E0 bounds that at a fixed ceiling (depth ±0.04 across n = 0.5–8 at ×10).

## Measures (within capacity time ≤ 2, as compare_scale.py)

Depth (PR_V minimum / start), inheritance, breakthrough (dissolved fraction), network k_eff gain at the end.

## Rules (fixed now)

- **R1, monotone.** On each network, gypsum-only depth falls as C rises (Spearman of depth against log C over the
  available ceilings). Passes if ρ = −1 on at least 7 of 9 networks.
- **R2, chemistries collapse.** Each coupled point is compared with the same network's gypsum-only depth interpolated
  at the coupled ceiling (linear in log10 C, only inside the gypsum-only range ×5.49–×1000, so the ×3.27 point is not
  used). Passes if the median |residual| ≤ 0.05 and the median residual lies within ±0.05. The 0.05 allows for the
  shape effect E0 measured (±0.04), since the matched points use different n. The 0.03 level is reported too.
- **R3, form (descriptive).** Per-network slope of depth against log10 C, and whether a quadratic term is needed
  (depth saturating at high C).

## Output

`analyze_ceilsweep.py` → `ceilsweep_runs.csv`, `ceilsweep_tests.csv`, `ceilsweep_depth.png` (depth against C for each
network, gypsum-only lines and coupled points, with residuals).

## Cost and schedule

To capacity time 2, the ×6 seed 1 n = 3 pair took 0.7 h (gypsum-only) and 3 min (coupled); full Phase 1 gypsum-only runs
take 0.5–2 h from ×4 to ×8. About 25 run-hours in all. The runner shares the machine with the 2 km queue (7 chains in total): 1 slot until that queue drains
(about midnight), then 7. Expected to finish Saturday afternoon.

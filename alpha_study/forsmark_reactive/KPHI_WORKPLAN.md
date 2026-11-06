# Work plan: does the k–φ law matter, and is the permeability ceiling the right predictor? (draft 6 Nov 2026)

## 1. The question

Phase 3 found that channel depth follows the achievable permeability gain (the "ceiling"), not the chemistry:
- At matched ceilings (×5.5), gypsum-only and coupled runs agree to a median 0.012 in depth (9 networks).
- Across ceilings, depth goes 0.88 / 0.78 / 0.66 / 0.53 at ×3.3 / ×5.5 / ×10 / ×20.

Every one of those runs used k/k0 = φ/φ0 (n = 1). Two readings:

- **H1, the ceiling is enough.** Laws that share a ceiling but differ in how k rises along the way give the same depth.
  Then the ceiling is a useful physical predictor.
- **H2, the trajectory matters.** Same ceiling, different intermediate evolution, different depth. Then the whole path
  of conductance against dissolution governs channel formation, and the ceiling only looked sufficient because it was
  never separated from the path.

**Why Phase 3 cannot decide this.** Under n = 1 the matched pair followed almost the same k-against-d path, not just the
same ceiling:
- Gypsum-only at φ0 = 0.182: k/k0 = 1 + 4.5 d.
- Coupled at φ0 = 0.1, if calcite forms where gypsum dissolves (Γ arithmetic): φ = 0.1 + 0.45 d, so again k/k0 = 1 + 4.5 d.

So the collapse is at least partly a trajectory match. The two paths differ only where calcite forms later or further
downstream than the gypsum dissolves. We need laws that share a ceiling and differ in path.

## 2. Tools: PFLOTRAN's own law already gives the family (input file only)

PFLOTRAN (realization_subsurface.F90) computes k = k0 · max(f_min, [(φ − φc)/(φ0 − φc)]^n), with φ0 = material POROSITY.
The code places no limit on the sign of φc or the value of n. For a ceiling C reached at φ = 1:

    φc = (1 − C^(1/n) φ0) / (1 − C^(1/n))

This gives a family of laws with the same ceiling and different shapes. Gain at a dissolved fraction d (φ = 0.1 + 0.9 d):

| Ceiling C | n | φc | gain at d = 0.1 | 0.25 | 0.5 | 0.75 | shape |
|---|---|---|---|---|---|---|---|
| ×10 | 0.5 | +0.0909 | 3.3 | 5.1 | 7.1 | 8.7 | concave: early gain |
| ×10 | 1 | 0 | 1.9 | 3.3 | 5.5 | 7.8 | linear (the current law) |
| ×10 | 2 | −0.316 | 1.5 | 2.4 | 4.3 | 6.9 | convex |
| ×10 | 8 | −2.60 | 1.3 | 1.9 | 3.4 | 6.0 | near-exponential: late gain |

At the same ceiling, these laws differ by about ×2 in gain at half dissolution and ×2.5 at d = 0.1. The same family can be
built for C = ×5.5 and ×30.

**What the family cannot reach.** The convex side stops at an exponential. A "series front" law (k barely moves until
the front is nearly through, harmonic mean; gain about 1.8 at d = 0.5 for C = 10) needs a small PFLOTRAN source change:
one extra branch in the loop above. That is optional stage E5, and only with your OK.

## 3. Experiments

**Network set.** P32 ×4 / ×6 / ×8, σ = 1, seeds 1–3: nine 1 km networks. This is the same set as Phases 2 and 3, so every
earlier number has a paired baseline.

**Common settings.** Everything else as Phase 1. Run to capacity time 2, one pore volume per year, dt 0.57 τ. All
measures are taken within capacity time ≤ 2.

| Stage | What | Runs | Purpose |
|---|---|---|---|
| E0 pilot | ×6 σ1 seed 1, gypsum-only, C = 10, n = 0.5 / 2 / 8 | 3 | Check that PFLOTRAN realizes each law: Permeability/k0 against porosity in the VTK must match the formula. Also check time-step cost and that no cell falls below φc. |
| E1 shape at fixed ceiling (main test) | Gypsum-only, C ∈ {×5.5, ×10, ×30} × n ∈ {0.5, 1, 2, 8}, 9 networks | 11 laws × 9 = 99 (C = 10, n = 1 is Phase 1) | Decides H1 against H2 |
| E2 chemistry at matched ceiling | Coupled, C = 10 laws n ∈ {0.5, 2, 8}, 9 networks | 27 (n = 1 exists) | Under each law the coupled ceiling is the law's gain at φ = 0.55 (×7.1 / 4.3 / 3.4). Does the coupled depth fall on the gypsum-only depth-vs-ceiling curve from E1 for every shape? This is the pasted question directly. |
| E3 realistic contrast | Both chemistries, n = 3, φc = 0 (×1000), 9 networks | 18 | Do the overall trends (stage order, inheritance, coupled shallower, density ordering, early vs late dip) survive at a realistic ceiling? This replaces "test A". |
| E4 2 km check (later) | ×4 and ×8 σ1 seeds 1–3, both chemistries, best and worst law from E1 | about 24 | Only if E1 shows shape matters. Does the density / length effect on peak timing change with the law? |
| E5 (optional, needs OK) | Series-front and threshold laws by a PFLOTRAN source change | about 18 | Extends the shape range beyond the power family |

## 4. Measures (fixed before running)

**Per run:**
- depth (min PR_V / start); d_Q depth;
- d at the deepest focusing; d at breakthrough;
- n90 min / start; inheritance; network k_eff gain;
- stage-order flags; early-vs-late dip (split at d = 0.35);
- the coupled − gypsum-only gap on each network.

**Trajectory descriptors per law** (computed from the formula and checked against the realized cells):
- the ceiling C;
- gain at d = 0.5;
- initial slope;
- mean log gain ∫₀¹ ln g(d) dd.

## 5. Decision rules (written before the runs)

1. **Collapse test (E1).**
   - Fit depth against ln C on the n = 1 laws: Phase 3 plus the E1 n = 1 runs.
   - Predict the other shapes and look at the median residual per (law, P32) cell.
   - H1 holds if every shape's median residual is within ±0.03 and shows no monotone trend with n.
   - H2 holds if residuals exceed 0.05 and order with shape. For scale, Phase 3 equal ceilings gave a median 0.009 and a
     maximum 0.052.
2. **If H2:** test which descriptor collapses all laws. Use leave-one-law-out R² for C, gain at d = 0.5 and mean log gain.
   The winner is the predictor we report.
3. **Chemistry test (E2).** Coupled depth minus the gypsum-only curve at the same ceiling: within ±0.03 for each shape →
   the "ceiling, not chemistry" claim stands for any law.
4. **Trends (E3).** A trend counts as law-robust if it holds in at least 8 of 9 networks under every law tested:
   - stage order;
   - inheritance ≥ 0.95;
   - coupled shallower;
   - density ordering.
   Otherwise it is reported as specific to n = 1.

## 6. Cost and scheduling

- **Runs:** E0–E3 is 147 runs at 1 km to capacity time 2. The n = 3 pair took about 50 min of wall time, and n = 1
  gypsum-only runs are faster, so allow about 0.5–1 h per run. At 4–6 parallel slots that is about 1.5–2 days.
- **Order:** E0 (1 h), then E1, then E2 and E3 together.
- **Machine:** the 2 km σ0 queue (25 runs) has the machine now. Start E0 at once (3 runs), then start E1 when the 2 km queue
  finishes, or share slots. The DFN runs stay paused unless you say go.
- **Disk:** about 0.3 GB per 1 km run if the per-step velocity and cell-info dumps are switched off. That is an output
  option only, not physics, and nothing reads those dumps. Otherwise about 0.9 GB per run.

## 7. Risks

- **Concave laws put φc just below φ0 (0.069–0.099).** Any porosity drop below φc collapses k to f_min. In coupled runs
  re-precipitation can do that, which would mix shape with sealing. So in E2 count how many cells drop below φc. If more
  than a handful do, report n = 0.5 coupled separately.
- **High n makes the run stiffer.** E0 checks the time-step cost, and dt stays at 0.57 τ.
- **This tests sensitivity, not which law is true.** Which trajectory is physical comes from resolving single vein-filled
  fractures in 2D: test C in lit/kphi_choice_physics_and_plan.md. E1 tells us whether that answer matters.

## 8. Deliverables

- `kphi_family_compare.py`, producing `phase1/kphi_family.csv` and figures:
  - depth against ceiling, coloured by shape;
  - depth against the winning descriptor.
- A report section (8.13) with the H1/H2 verdict and a table of which trends are law-robust.
- A log in phase1/INTERVENTIONS.md.

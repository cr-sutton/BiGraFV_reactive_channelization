# Choosing n in PFLOTRAN's k–φ power law: what it represents, what others do, what we can test (6 Nov 2026)

Prompted by Glenn Hammond's reply: the power law is an *upscaled* term. It stands in for how the geometry inside a
fracture changes as the fill dissolves, and no single n is "correct". This note turns that into something testable.
Sources: lit_kphi_relations.md (§§1–8), lit_channel_depth.md, our n = 3 run (phase1/kphi_n3_compare.csv).

## 1. What the law does in our runs

PFLOTRAN: k = k0 [(φ − φc)/(φ0 − φc)]^n, φ0 = material POROSITY (0.1), φc = 0 here.
- Every cell starts at φ0 = 0.1, so k(φ)/k0 = (φ/0.1)^n. A fully dissolved cell gains ×10^n: ×10 at n = 1, ×1000 at n = 3.
- At dissolved fraction d of a cell, φ = 0.1 + 0.9 d, so k/k0 = (1 + 9d)^n. At d = 0.5 this is ×5.5 at n = 1 and ×166 at n = 3.

**Does the larger k itself matter? No, only the ratios do.**
- Our runs inject a fixed rate and fix the outlet pressure, with constant viscosity and gravity off. Multiply every k by the
  same factor and the pressure differences divide by that factor; every flux stays the same.
- The chemistry sees only fluxes, so the absolute permeability has no effect.
- What n changes is the *ratio* between a partly dissolved fracture and its neighbours, at every moment. That ratio decides
  how the fixed total flow is shared out, and therefore every transient.

**Are the transient effects the same? No.** Same network (P32 ×6, σ1, seed 1), capacity time ≤ 2:

| | gyponly n=1 | n=3 | coupled n=1 | n=3 |
|---|---|---|---|---|
| depth (min PR_V/start) | 0.68 | 0.21 | 0.76 | 0.35 |
| deepest focusing at d | 0.42 | 0.11 | 0.43 | 0.14 |
| breakthrough at d | 0.46 | 0.27 | 0.48 | 0.31 |
| n90 min/start | 0.50 | 0.09 | 0.61 | 0.15 |
| k_eff gain | ×9.8 | ×727 | ×5.4 | ×135 |
| inheritance | 1.00 | 1.00 | 1.00 | 1.00 |

**What does not change: what is robust and what depends on n.**
- *Does not change:* which fractures form the channel; that the pore space opens first; that breakthrough comes after
  focusing; that coupled runs are shallower.
- *Changes:* how deep the channel gets, when breakthrough happens, and how far the flow spreads again before the run ends.
  With n = 3, PR_V only recovers to 0.51 / 0.71 of its start by capacity time 2, against 0.95 / 0.98 with n = 1.
- *Caveat:* this is one network.

## 2. What n means physically (inside one fracture)

The one-cell model knows only the volume dissolved in a fracture, not where inside it. The law has to supply how the open
space is arranged. Some idealized arrangements, with an open (dissolved) region that has permeability k1 ≫ k0:

| How the fill dissolves inside the fracture | Effective k of the cell vs d | Equivalent law |
|---|---|---|
| Wormholes, full aperture height, parallel to the flow (fraction d of the width open) | arithmetic: k0 + d(k1 − k0), linear and fast | n = 1 is exactly this, with k1 = 10 k0 |
| Even thinning of the whole fill layer (an open slot that grows across the whole fracture) | cubic in the open aperture | n = 3 (slot cubic law; TOUGHREACT fracture option 3) |
| Grain-by-grain dissolution of a porous fill | Kozeny–Carman, φ³/(1−φ)² | n ≈ 3 at low φ, steeper near φ → 1 |
| A compact front crossing the fracture *across* the flow (open behind, sealed ahead) | harmonic: stays near k0 until the front is almost through | critical-porosity-like (Verma–Pruess with φc near φ0, n large) |
| Isolated pockets that do not connect along the flow | almost no gain until they percolate | critical porosity / threshold |

- So n is a statement about the shape of the in-fracture dissolution front, which the one-cell model cannot resolve.
- Single-fracture studies say this shape depends on in-fracture Da and Pe and on aperture variability: wormholes at high flow
  and with rough apertures (Szymczak & Ladd 2009; Hanna & Rajaram 1998 for gypsum).
- Our fractures run at local equilibrium (Da_f ≈ 10⁷). There, a single-fracture front is either compact or wormholed,
  depending on Pe and roughness.

**The ceiling, k1/k0.** For a sealed vein that reopens to a hydraulic aperture b_h, geometry estimates give ×10³ (slot) up
to ×10⁴–×10⁶ (porous fill) (lit_kphi_relations §8). The n = 1 ceiling of ×10 understates this by 2–5 orders.

## 3. What others do (short version; details in lit_kphi_relations §§3–5)

- **Code defaults and benchmarks:**
  - Kozeny–Carman, roughly n ≈ 3, in the Xie et al. 2015 multi-code benchmark.
  - PFLOTRAN n = 1 in the LANL DFN studies (Hyman et al. 2026 TiPM, "one of many possible pedotransfer functions"). They
    argue a uniform start makes it harmless, but that only holds before dissolution becomes uneven.
- **Calibrated to core floods or µCT:** n = 3–10 for carbonates, up to 20–40.
- **Calibrated to field injectivity:** Verma–Pruess with φc close to φ0 and n = 4–13 (geothermal silica scaling, Tiwi).
- **Fracture-specific mechanistic laws:**
  - cubic law in aperture;
  - TOUGHREACT options 3 and 4 (k ∝ φ³, or a modified cubic law built from the hydraulic aperture);
  - graph models that update aperture directly (Hyman et al. 2026 graph; Szymczak & Ladd).
- **Theory:** reaction-infiltration instability depends mainly on the end-member contrast, not the curve's shape (Ladd &
  Szymczak 2017). Whether fingers form at all is nearly saturated by a contrast of 10. How *deep* the channel gets is
  bounded by the contrast.
- **Not found:** any 3D DFN study that varies n at fixed chemistry.

Bottom line from the literature: there is no standard n. People pick it from the code default, calibrate it to data, or
derive it from a geometry they assume. For a vein-filled fracture, n = 1 is the conservative end.

## 4. What we can do: three tests, cheapest first

**A. Bracket (cheap; tells us which conclusions depend on n).**
- Design: n = 2 and 3 on P32 ×6 σ1 seeds 1–5, both chemistries, to capacity time 2. That is 18 new runs; n = 3 seed 1
  already exists.
- Cost: an n = 3 pair took about 50 min of wall time at 1 km.
- Output: every report measure as a function of n, sorted into "holds for any n" and "set by n".

**B. Ceiling or curve shape (separates the two knobs).**
- At φc = 0, n sets both the ceiling (10^n) and how fast k rises at partial dissolution (slope 9n at d = 0).
- To separate them:
  - **Same ceiling, different shape:** n = 1 at φ0 = 0.01 (×100) against n = 2 at φ0 = 0.1 (×100). This changes capacity
    and Da too; lit §8 notes the confound.
  - **Same shape early, different ceiling:** add `PERMEABILITY_CRITICAL_POROSITY` (Verma–Pruess) runs.
- This tells us whether the ceiling alone sets depth (theory says yes) or the shape matters too.

**C. Derive n from resolved fractures (the rigorous answer to Glenn's point).**
- Resolve single vein-filled fractures in 2D, with the same chemistry, φ0, flow rate per fracture and aperture variability
  as the Forsmark networks. The physics_upscaling 2D per-fracture tools and the multi-cell graph already exist.
- Measure the effective cell permeability against the dissolved fraction, k_eff(d), and fit the PFLOTRAN law to it:
  n, φc and min-scale, all input-file only.
- Check that the result does not depend on the fine-scale local law (n = 1 and n = 3 locally). At Da_f ≫ 1 the fine cells
  switch from sealed to open quickly, so the front shape should control the result.
- Output: an upscaled n (or Verma–Pruess φc, n) per regime (Pe, aperture σ), justified by physics rather than chosen. This is
  what Glenn means by an upscaled term.
- Cost: a few days of building and running small 2D models.

**Recommendation:**
1. Run A now; it is cheap and decides what the paper can claim regardless of n.
2. Start C in parallel as the defensible way to pick n.
3. Run B only if A shows the depth does not simply follow the ceiling.
4. Until then, present n = 1 as a lower bound on focusing and n = 3 as a central case. Never present n = 1 as "realistic".

# Forsmark reactive study: options for what comes next (on hold, 3 Nov 2026)

Status: Phase 1 complete (90 runs, report https://claude.ai/artifact/Bt4SbtGrkNoqHrYB2TW5pj). User asked to wait before
Phase 2 and to keep the options on record. Constraints from the user: keep minerals real (no 1e-9 to 1e-12 rate-constant
cuts), one pore volume per year, plain one-cell BiGraFV, sigma always shown as separate ensembles, no dead-end
explanations, focus on how channels form.

## A. Stay with gypsum (the Hyman et al. 2024 IJGGC chemistry)
1. Capacity sweep: injected carbonate 0.5 M (Phase 1) -> 0.05 -> 0.005 -> ~0.001 M. At ~1-5 mM the coupled capacity is
   within ~5-30 % of gypsum-only, a true 1:1 comparison where any difference is precipitation. Low carbonate is also where
   calcite placement can separate from dissolution and where clogging was seen before (TPL Track B1).
2. Calcite rate within the paper's range (k_cal 2e-9 to 5e-5; ours 2.29e-5): matters only at low carbonate.
3. Permeability contrast: k-phi exponent (n = 1 vs 3) or initial porosity. Sets how strong a channel can get
   (n = 1, phi0 0.1 caps gain at x10; replacement at x5.5).
4. Effective gypsum rate k*A within the documented lab-to-field range (2-5 orders), defensible as reactive-area uncertainty;
   keeps Da >> 1, so expected to change little.

## B. Represent a different system with its own mineral
CO2-charged water dissolving a carbon-mineralization silicate (wollastonite or forsterite, in hanford.dat) and precipitating
calcite or magnesite, with Palandri & Kharaka rate constants. Rough Da_f at 1 PV/y: wollastonite ~1e3, forsterite ~30,
diopside ~10 (scaled from the gypsum value; to be checked once a deck exists). Needs a new chemistry deck.

## C. Analysis of Phase 1 not yet done
- Paired sigma differences per seed (identical geometry), instead of overlapping ensembles.
- Channel inheritance: is the channel at its peak the initial flow backbone (overlap0 in channelization.csv)?
- Gypsum-only vs coupled channel sets at matched capacity time on the same network.
- Two-stage dips (first channel overtaken by a second).
- Breakthrough curves from the frozen-state probes already saved in each run (snap_*).
- Flow-field renders that show channels (backbone-only or side view).

## Findings from the 3 Nov follow-up checks (phase1/phase1_channel_identity.csv)
- Channels are inherited: 96-99 % of the fractures in the channel at its peak (n90 minimum) were already in the initial
  90 % flow set; only 1-4 % are new. The reaction selects and sharpens a subset of the initial backbone.
- Both chemistries channel through nearly the same fractures on the same network (Jaccard of the peak 90 % sets
  0.81-0.85), so chemistry sets channel strength, initial flow sets channel location.
- Paired sigma (same geometry): sigma 1 starts with a lower volume-weighted participation ratio than sigma 0 in 13 of 15
  seeds (median -0.033); at the channel minimum the gap halves for gypsum-only (-0.016) and shrinks for coupled (-0.024).

## Recommendation (3 Nov): no more generic Da/Fo sweeps; test the mechanism with few runs
- k-phi contrast test (n = 3 or lower phi0) on a subset: does channel strength follow permeability contrast, and does
  inheritance break when the feedback is stronger?
- Capacity-matched coupled runs (carbonate ~1-5 mM): precipitation that can reduce permeability; does it re-route flow?
- Analysis only: breakthrough curves from the saved probes; initial-flow predictor of channel membership.

## Ideas from the literature search (lit/lit_large_dfn_reactive.md, 3 Nov), filtered by the study's constraints
Analysis only (no new runs):
- Flow-focusing profile along x (Szawełło 2024/2026): wormholing (front from the inlet) vs channeling (inherited paths
  enlarge everywhere). Puts our runs on their regime scale; a power-law network might sit somewhere new.
- Backbone share as in Hyman 2026 (surface-area share of the top-100-paths backbone) against tau = dissolved volume / initial
  volume, their regime clock, next to our 90 %-flow set.
- Calcite in channel vs off-channel fractures, and reroute events (a channel fracture loses > 50 % of its flow while a
  neighbour gains), to look for Budek's passivation / side-branching / "explore and reroute" modes, mainly in the 2 mM runs.
- Field check: simulated calcite-in-channel share against the Forsmark observation that calcite coats open, water-conducting
  fractures (Sandström & Tullborg; Drake & Tullborg), if SKB boremap/PFL data are accessible.
Explains a Phase 1 result: the x5.5 coupled ceiling is 1 + (vf0/phi0)(1 - Gamma) with Gamma = V_calcite/V_gypsum = 0.494
  (Budek & Szymczak's replacement parameter); it is arithmetic, not a fitted result.
Out of scope under current rules (recorded only): Da sweeps via k or via injection rate (1 PV/y rule); changing the calcite
  molar volume (Gamma sweep) is a non-real mineral like the k cuts; one-cell vs multiport comparisons.
Key new references: Hyman et al. 2026 TiPM (same gypsum -> calcite chemistry, 2D); Budek, Szymczak & Kang 2026 EPSL
  (replacement regimes, Fo and Gamma); Szawełło et al. 2026 (flow focusing); Upadhyay et al. 2015 (single-fracture patterns
  forget the initial aperture field). No km-scale reactive DFN with thousands of fractures was found; the largest are
  25 m / ~526 fractures (Hyman 2026 graph) and 10 m meshed DFNs.

## Flow rate as a systematic axis (user, 3 Nov: rate may change if chosen systematically)
- What 1 PV/y means physically (steady start, manifold pressure above the outlet): head gradient across 1 km of
  ~5e-4 (x4), 3e-4 (x6), 2e-4 (x8) medians, range 1e-4 to 1.4e-3 over networks: natural-groundwater gradients.
- Proposed anchor: hydraulic gradient decades i = 1e-4, 1e-3, 1e-2, 1e-1 (natural low / natural / steep or near-well /
  pumping or injection). Two ways to apply it:
  B (recommended, keeps the constant-rate convention): per network, rate = 1 PV/y x (i_target / i at 1 PV/y on that network).
  A: fixed-pressure boundaries at that gradient, so flow rises as permeability grows (the classic dissolution feedback;
     a different boundary condition, not just a rate).
- Expected effects: gypsum-only channelization should not change on the capacity-time axis (BiGraFV has no transverse
  diffusion; a 640x rate change on the 500 m network changed channelization metrics by <= 2 %, see hyman-rate memory).
  The rate matters where something is rate-limited: calcite at low carbonate (2 mM runs), and any slower real mineral.
- Cost per pore volume is about the same at any rate (dt cap scales with residence time).
- To verify before use: Forsmark natural hydraulic gradients at repository depth (SKB site descriptive model).
- Decision (user, 3 Nov): reactive runs always use a fixed volumetric flow rate. Fixed-pressure boundaries (option A) are
  out. The gradient-anchored rate (option B) is a knob for later, not a change to the current queue.

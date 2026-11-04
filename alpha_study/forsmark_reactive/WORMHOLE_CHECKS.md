# Wormhole checks (requested 4 Nov; run after the reactive queue finishes)

BiGraFV is one control volume per fracture, so it cannot form in-fracture wormholes. These two post-processing checks say
which results are pattern-independent and bound the ones that are not. Post-processing only: no new reactive runs, no
physics changes. Phase 1 runs, P32 x4/x6/x8 (x16 too if the inputs exist), both chemistries.

## Check 1: regime map
- Literature first (literature-checker -> forsmark_reactive/lit/lit_wormhole_regime.md): the exact definitions and phase
  boundaries (compact / wormhole / uniform) of Li, Hu, Szawelo, Yang, Chen, Szymczak & Zhou 2026 (GRL, "From core to field:
  pattern selection in dissolving fractures"), and of Starchenko & Ladd (critical Da vs fracture length), plus the
  Szymczak & Ladd 2009/2012 Da, Pe and G definitions they build on. State the dimensionless groups, how fracture length
  enters, the parameter range the boundaries were validated over (0.1-30 m per our lit note), and whether a
  local-equilibrium limit (Da_f ~ 1e7) is covered or is an extrapolation.
- Then a script (forsmark_reactive/wormhole_regime_map.py) computes, per flowing fracture of each network (90 %-flow set of
  the initial state): Da_f (as forsmark_damkohler.py), the Pe of the paper's definition, fracture length along flow, and
  the regime the published boundaries give. Output: phase1/wormhole_regime.csv (per fracture) and a summary per
  network/chemistry: share of fractures and share of flow in each regime; figure phase1/figures/wormhole_regime.png
  (fractures on the published diagram, boundaries drawn, validated range shaded). If our values lie outside the validated
  range, say so on the figure and in the summary; do not extrapolate a regime silently.

## Check 2: wormhole-limit bound on breakthrough
Capacity-limited dissolution (Da_f ~ 1e7): the network dissolves at about Q c_cap whatever the in-fracture pattern, until
the front reaches the outlet. What a wormhole changes is how much of each fracture must dissolve before the front passes.
Per run, at the breakthrough state k_bt (first saved state with outlet_diss >= 0.5, phase1_mechanism.csv), from
paraview/<net>__<run>/fractures_KKK.vtu (fraction_dissolved, Q_frac) and fracture mineral volumes (UGE volume x vf0):
- D_bt = mineral dissolved network-wide at k_bt (fraction of inventory); split into D_ch (fractures in the 90 %-flow set
  at the n90 minimum, the inheritance channel) and D_off (the rest).
- If only a fraction f of each channel fracture had to dissolve for the front to pass:
    lower bound  D_bt(f) = f * D_bt              (all dissolution before breakthrough scales)
    upper bound  D_bt(f) = f * D_ch + D_off      (off-channel dissolution unchanged)
  and t_cap,bt(f) ~ D_bt(f) / (dissolved per unit t_cap) using the run's own dissolved-vs-t_cap curve (gyponly ~ 1:1;
  coupled lags by ~3 %, use the curve, not 1:1).
- f in {0.1, 0.2, 0.3, 0.5, 0.75, 1.0}. Output phase1/wormhole_bound.csv (run, f, D_ch, D_off, t_cap_bt lower/upper,
  PV lower/upper), medians [IQR] per P32 and chemistry; figure phase1/figures/wormhole_bound.png (breakthrough t_cap and
  dissolved-at-breakthrough vs f, band = lower-upper, lines = medians per P32). f = 1 must reproduce the model's
  breakthrough (check).
- Report wording: "if wormholes let the front cross a fracture after dissolving a fraction f of it, breakthrough would
  come at t_cap X-Y instead of Z"; the dissolved budget vs time, the stage-1 timing and the channel identity are not
  affected by construction of the bound; this is a bound, not a simulation.

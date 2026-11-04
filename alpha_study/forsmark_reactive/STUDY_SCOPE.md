# Forsmark reactive study: scope (set 2 Nov 2026)

In scope
- Model: plain one-cell BiGraFV (`model_graph_raw`). No multiport/mc4hd, no correction factors, no DFN comparison lanes.
- Networks: Forsmark FFM01 sets (`network_forsmark.py`), domain 1000 x 250 x 250 m, flow along x.
- Flow: one network pore volume per year (`run_scripts/run_km_graph_case_hyman.sh`), nothing else. Outflow-face fix
  (`EXFIX`, `--area-per-dist 1e-2`) is on by default from 3 Nov 2026; Phase 1 has 60 runs without it, 30 with it (shown equivalent).
- Initial porosity 0.1 (gypsum vf0 0.9), PFLOTRAN PERMEABILITY_POWER n = 1, reference porosity 0.1.
- Chemistry: Hyman et al. 2024 IJGGC 139:104265 (gypsum -> calcite). Template kinetics are inside its Table 1;
  injected brine from its Table 2 (0.5 M CO3, 1.0 M Na, pH 11.39).
- Every network runs gypsum-only (gyponly) and coupled (gypcal) as a pair.
- Order: Phase 0 pilot -> Phase 1 geometry sweep (P32, transmissivity sigma, seeds) -> Phase 2 Da x Fo on a subset.
- Outputs: paired-timestep network renders with plots; Hyman-style channelization, k_eff, placement, breakthrough.

Out of scope unless the user asks: multiport, corrections, DFN validation, other domains, other flow rates.

## Added 3 Nov 2026 (user request)
- Phase 2 = mechanism tests, not Da/Fo sweeps: (a) initial porosity 0.05 (gypsum vf 0.95) instead of changing the k-phi exponent,
  gypsum-only and coupled 0.5 M; (b) capacity-matched coupled run, 2 mM carbonate, charge-balanced pH. sigma 1.0, seeds 1-3.
- New P32 x16 level (about 7,850-8,230 fractures, 78k cells, 114-141 fracture-disjoint paths): Phase 1 (5 seeds x 3 sigma,
  both chemistries) and Phase 2.
- All runs from here end at capacity-normalised time 2 with checkpoints at matched capacity times
  (0.02 0.05 0.1 0.25 0.5 0.75 1 1.5 2); Phase 1 at x4-x8 ran to 36,515 PV, so compare on capacity time up to 2.
- Queue: phase1/run_list_overnight.txt (make_queue_overnight.py, run_overnight.sh). Tracer analysis: analyze_phase1_tracer.py.
- Transmissivity (user decision 3 Nov): keep the current networks and label them "FFM01 200-400 m fracture sets and intensities with
  the FFM01 0-200 m transmissivity model T = 6.3e-9 r^1.3 (sigma 1.0)"; no rebuild with the 200-400 m law (1.3e-9 r^0.5).

# BiGraFV reactive channelization: Forsmark networks

Reactive flow in kilometre-scale fracture networks built from SKB Forsmark FFM01 fracture statistics, simulated with BiGraFV
(one well-mixed control volume per fracture, bipartite fracture/intersection graph) and PFLOTRAN. Gypsum dissolution alone
and coupled to calcite precipitation, at a fixed volumetric rate of one network pore volume per year.

**Status (4 Nov 2026).** All runs complete: Phase 1 (45 networks at P32 x4/x6/x8 + 15 at x16, two chemistries each, 120
runs), Phase 2 mechanism tests (porosity 0.05, 2 mM carbonate; sigma 1, seeds 1-3), fine tracer probes, paused-pulse
movies, wormhole scenario and regime map, and one exploratory olivine-carbonation run.

## Main results (details, numbers and sources in the report)

1. **Inherited channels.** At the strongest channel, a median of about 98 % of the fractures carrying 90 % of the flow were
   already in that set before any reaction (lowest of 120 runs: 92 %).
2. **Four stages, timed by the fraction of the gypsum dissolved:** pore space opens near the inlet (about 17-20 % dissolved),
   flow focusing is strongest (37-44 %), breakthrough (56-63 %), then the flow spreads again. The measured dissolved fraction
   lines the chemistries and porosities up; Hyman's tau = dV/V0 does not (it is the mean permeability gain for n = 1).
3. **Channel-depth law.** The depth of flow focusing is set by the permeability gain the reaction can reach, not by the
   chemistry (equal ceilings give equal depth within about 0.01, paired on the same network).
4. **Transport narrows while the channel forms** and partly recovers (fine tracer probes on all networks).
5. **No rerouting with gypsum -> calcite** (calcite takes back about half the volume, so a well-mixed cell only opens).
   One exploratory olivine-carbonation run (solids grow) clogs the inlet fractures and re-routes the flow.
6. **Model-dependent:** the compact front (breakthrough after more than half the inventory). In-fracture wormholes, which the
   one-cell model cannot form, could bring breakthrough to about 28-36 % (scenario estimate, section 6.6 of the report).

## Layout

```
alpha_study/                       pipeline scripts (network build, decks, runs, analyses), as in the parent project
  physics_upscaling/               helpers imported by the pipeline
  run_scripts/                     run_km_graph_case_hyman.sh (one case), run_km_queue.py (queue)
  forsmark_reactive/               this study
    STUDY_SCOPE.md, OPTIONS.md, WORMHOLE_CHECKS.md     scope, options and check specifications
    *.py                           study analyses and figures (time_axes.py = the clocks)
    phase1/                        run lists, launchers, logs, INTERVENTIONS.md (every intervention, chronological)
      *.csv                        study-level results (stage events, mechanism, tracer, wormhole, d_Q baseline)
      L2_r15_p*_sg*_seed*/         per network: network_stats.json; per run: patterns.csv, channelization.csv,
                                   channel_fractures.csv, schedule json (no raw PFLOTRAN output)
      figures/                     all study figures (movie frames not included)
    report_phase1/                 the HTML report (index.html, img/, cartoons/, BRIEF.md, FIXES_v2.md, REFERENCES.md)
    deck/                          colloquium deck (Forsmark_Reactive_Channels.pptx) and its builder (rebuild.sh)
    explore_olivine/               exploratory olivine-carbonation run: deck, summary CSVs, figure
    lit/                           literature notes with VERIFIED / UNVERIFIED tags
    pilot/                         Phase 0 pilot notes
constant_chemistry_small_kbias/gyp_and_calc.in   PFLOTRAN chemistry template (Hyman et al. gypsum-calcite study)
```

`phase1/wormhole_regime.csv.gz` is gzipped (per-fracture regime map); `gunzip` it before rerunning scripts that read it.

## What is not here

Raw PFLOTRAN output (VTK, HDF5 checkpoints, mass-balance files, about 87 GB) and the meshes/graphs of each network stay on
the original machine. Every network can be rebuilt from its seed (`build_km_graph_network.py --forsmark`, settings in the
run lists) and every run from `run_scripts/run_km_graph_case_hyman.sh` with the arguments logged in
`phase1/run_list_*.log`.

## Requirements

dfnWorks (pydfnworks) for network generation, PFLOTRAN (built with PETSc) for flow and reactive transport, Python 3 with
numpy, pandas, matplotlib, h5py, vtk. The deck builder uses python-pptx, resvg-py and pymupdf in `forsmark_reactive/deck/.venv`
(not included; `python3 -m venv .venv && .venv/bin/pip install python-pptx resvg-py pymupdf pillow`).
Paths to PFLOTRAN are read from `~/.dfnworksrc`.

## Reproducing the report numbers

From `alpha_study/` (with the raw run folders present):

```
python3 forsmark_reactive/analyze_phase1_mechanism.py
(cd forsmark_reactive && python3 stage_events_clocks.py)
python3 forsmark_reactive/make_candidate_figures.py
python3 forsmark_reactive/analyze_phase1_tracer.py
python3 forsmark_reactive/wormhole_bound.py && python3 forsmark_reactive/wormhole_regime_map.py
zsh forsmark_reactive/deck/rebuild.sh
```

Most report tables can be recomputed from the CSVs in this repository alone (stage events, depth, inheritance, transport,
wormhole checks, olivine).

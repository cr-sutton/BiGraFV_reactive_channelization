# PI brief: Forsmark reactive study, overnight report (3 Nov 2026)

Single source of facts for the subagents. Paths are relative to /Users/collin/Projects/bipartite_pflotran/src/alpha_study.
Live report (to be replaced): https://claude.ai/artifact/Bt4SbtGrkNoqHrYB2TW5pj (slug 581c7090-e037-4d2b-9acc-2dffeb5ed428),
local source forsmark_reactive/report_phase1/index.html and img/.

## The study in one paragraph
Gypsum dissolution, alone and coupled to calcite precipitation, in kilometre-scale discrete fracture networks built from
the SKB Forsmark FFM01 fracture statistics, simulated with BiGraFV (one control volume per fracture, bipartite graph,
PFLOTRAN reactive transport) at a fixed volumetric injection of one network pore volume per year. Question: how do
dissolution channels form in large, realistic, mineral-filled fracture networks, and how does coupled precipitation change
that? Scope set by the user: plain one-cell BiGraFV only; real minerals (no rate-constant cuts); fixed volumetric flow rate;
sigma always shown as separate ensembles; no dead-end explanations (BiGraFV represents dead ends only approximately).

## Networks
- Domain 1000 x 250 x 250 m, flow along x (inlet x = -500 m, outlet x = +500 m).
- SKB FFM01 open-fracture sets for 200-400 m depth: NS, NE, NW, EW, HZ; Fisher kappa 12.9-17.8; truncated power-law radii,
  k_r 2.38-3.10; radii 15-564 m. Generator: network_forsmark.py (sets table there), build_km_graph_network.py --forsmark.
- At the real SKB intensity nothing percolates across 1 km, so P32 is scaled x4, x6, x8 (and x16, running) of the SKB value.
- Transmissivity T = 6.3e-9 r^1.3 (m^2/s) with semi-correlated spread sigma = 0, 0.5, 1.0 (SKB fit 1.0); dfnWorks converts T to
  aperture with the cubic law. For a given seed and P32 the three sigma share identical geometry.
- 5 seeds per (P32, sigma): 45 networks; x16 adds 15.
- Structure (network_stats.json): x4: 1,587-1,814 fractures, 9-12 fracture-disjoint inlet-outlet paths; x6: 2,714-3,037,
  22-27; x8: 3,812-4,070, 38-44; x16: 7,849-8,229, 114-141 (78k graph cells).

## Model and chemistry
- BiGraFV one-cell graph (each fracture one cell; intersections as connections), PFLOTRAN.
- Fracture cells start 90 % gypsum by volume (porosity phi0 = 0.1); PFLOTRAN k-phi power law n = 1 with reference porosity
  phi0: k/k0 = phi/phi0, so permeability can rise at most x1/phi0 = x10 for gypsum-only.
- Kinetics from Hyman et al. 2024 IJGGC 139:104265 Table 1 range: k_gyp 1.62e-3 mol m^-2 s^-1 (its maximum), k_cal 2.29e-5,
  gypsum specific surface 750 m^2/kg; calcite area 200 m^2/m^3. TST rate law r = -A k (1 - Q/K).
- Gypsum-only: dilute injected water. Coupled: the paper's Table 2 brine, 0.5 M CO3, 1.0 M Na, pH 11.39.
- Flow: one network pore volume per year (Hyman et al. 2024 G-cubed convention), fixed volumetric rate; on these networks this
  equals a head gradient of about 1e-4 to 1e-3 across 1 km (natural groundwater range).
- Outlet boundary fix: graph_to_pflotran writes 1000 m^2 outflow faces; rescaled to 0.01 x distance (exfix_outflow.py); a control
  run agreed within 8e-4 in dissolved fraction and 0.25 % in k_eff, so the 60 earlier runs stand.

## Runs
- Phase 1: 45 networks x {gypsum-only, coupled} = 90 runs, to 36,515 PV; all complete.
- Phase 2 (mechanism tests, sigma 1.0, seeds 1-3, P32 x4/x6/x8/x16): initial porosity 0.05 (gypsum-only and coupled, 0.5 M);
  coupled with 2 mM carbonate at porosity 0.1 (capacity matched to gypsum-only). Run to capacity time 2. Running overnight.
- P32 x16 Phase 1 set (15 networks x 2) running overnight, to capacity time 2.

## Time axes (the three clocks; code forsmark_reactive/time_axes.py)
1. Pore volumes injected: PV = Q t / V_p0 (years at 1 PV/yr).
2. Capacity-normalised time: t_cap = PV x c_cap / C_inv, with c_cap the gypsum one m^3 of injected water can remove if it leaves
   saturated (16.6 mol/m^3 = gypsum solubility in dilute water; 16.6 + 1000 x [CO3] mol/m^3 for carbonate brine, one Ca removed
   as calcite per CO3) and C_inv = vf0 / ((1 - vf0) V_gyp) = 120,498 mol per m^3 of pore (vf0 = 0.9, V_gyp = 74.69 cm^3/mol).
   t_cap = 1: the injected water could have dissolved the whole inventory. Backing: the acid-capacity / reactant-capacity
   scaling of dissolution theory (gamma = c0/(nu c_sol) in Szymczak & Ladd; Hyman, Szawełło, Kang & Szymczak 2026 JGR); it is
   the "pore volumes to dissolve" normalisation of acidizing (Fredd & Fogler 1998, PVbt) expressed per inventory. At high Da
   dissolved fraction ~ t_cap (measured within ~0.01 at the channel minimum). The 516.6 for 0.5 M brine is ideal; the pilot
   measured ~470 mol/m^3.
3. Dissolved volume / initial volume (Hyman et al. 2026 Eq. 26): tau = Delta V / V0, with Delta V = n_gyp,dissolved V_gyp -
   n_cal,formed V_cal (V_cal = 36.934 cm^3/mol), V0 initial pore volume. Reaches ~9 (gypsum-only) and ~4.5 (coupled) because
   fractures start 90 % filled; tau = 1 arrives at t_cap = 0.11 for gypsum-only.

## Measures (definitions)
- Participation ratio, volume-weighted: PR_V = (sum_f Q_f)^2 / sum_f (Q_f^2 / w_f), w_f = V_f / sum V (fracture volume share);
  1 when flow is proportional to volume. Code analyze_channelization.py pr_w.
- Active surface area (Maillot et al. 2016 WRR; Hyman 2020 Front. Phys.): d_Q = (sum_f S_f q_f)^2 / (sum_f S_f sum_f S_f q_f^2),
  q_f = Q_f / S_f, = area-weighted participation ratio. (An older script used Q_f in place of q_f; corrected.)
- Pore-volume participation ratio: PR_pore = same as PR_V with w_f = V_f phi_f / sum (open pore volume).
- n90: number of fractures carrying 90 % of the throughflow.
- Inheritance: share of the current 90 %-flow set that was in the initial 90 %-flow set (overlap0).
- Outlet dissolution: flow-weighted dissolved fraction of fractures with centres in the last 100 m (x > 400 m); breakthrough =
  first state with outlet dissolution >= 0.5.
- Transport (frozen-state tracer probes, Hyman 2024 G-cubed and 2026 JGR adapted to an Eulerian pulse): f(t) = outflow tracer flux
  / injected tracer; t16, t50, t84 from the cumulative; D_L = (1/8)[(L - v t16)/sqrt(t16) - (L - v t84)/sqrt(t84)]^2 with
  v = L/t50, L = 1000 m (Hyman 2026 Eq. B1; Sahimi); dispersivity alpha_L = D_L / v; tail exponent gamma from f ~ t^-gamma fitted
  over t in [2 t_peak, t at f = 1e-2 f_peak]; arrivals also divided by the current mean residence time tau_res = V_p / Q (probes hold
  Q fixed while the pore volume grows up to x10).
- Permeability ceiling under n = 1: gypsum-only 1/phi0; coupled 1 + (vf0/phi0)(1 - Gamma), Gamma = V_cal/V_gyp = 0.494
  (Budek & Szymczak replacement solid-volume ratio). x10 and x5.5 at phi0 0.1; x20 and x10.6 at phi0 0.05.

## Results (all numbers are medians unless stated; source CSVs in forsmark_reactive/phase1/)
- End state (36,515 PV; phase1_end_summary.csv): dissolved gypsum-only 0.896/0.936/0.970 (x4/x6/x8), coupled 0.937/0.976/0.990;
  k_eff gain gypsum-only 9.90-9.97, coupled 5.35-5.41. No coupled run clogged.
- Capacity: dilute water leaves carrying ~17 mol/m^3, the 0.5 M brine ~470-500 mol/m^3, so coupled dissolves ~30x faster per PV;
  on capacity time the two chemistries share a clock.
- Density: active area d_Q 0.36/0.40/0.47 and PR_V 0.35/0.42/0.53 at x4/x6/x8 (start); share of fractures by count carrying flow
  0.041 -> 0.034.
- Channel depth (PR_V minimum / start): gypsum-only ~0.64-0.67, coupled ~0.77-0.79, at every P32 and sigma (phase1_channel_minima.csv).
- Inheritance: 92-99 % (median 97-99 %) of the fractures in the 90 %-flow set at the channel peak were in the initial set; it dips
  only around breakthrough (to ~0.95-0.97) and returns to 1. Chemistries pick the same fractures: Jaccard 0.75-0.93 (median ~0.82)
  (phase1_channel_identity.csv).
- Sigma (paired, identical geometry): sigma 1 starts with lower PR_V than sigma 0 in 13/15 seeds (median -0.033); at the minimum
  the gap is -0.016 (gypsum-only) and -0.024 (coupled).
- Four stages (phase1_mechanism.csv / _summary.csv): (1) t_cap 0-0.1 pore space opens near the inlet, flow still spread over filled
  fractures; PR_pore falls (e.g. 0.36 -> 0.20) while PR_V barely moves; (2) ~0.1-0.4 front advances down the inherited paths;
  PR_pore minimum at t_cap 0.1-0.3; (3) ~0.4-0.6 breakthrough: outlet goes from undissolved to > 50 % dissolved sharply; PR_V
  minimum just before; PR_pore back near its start (0.9-1.2 of it); (4) widening, both recover.
- Breakthrough is expensive: when the outlet passes 50 %, the network has dissolved 53-57 % (gypsum-only) and 58-67 % (coupled)
  of its gypsum; range 31-82 % over runs. Porosity 0.05 runs so far: 0.49-0.62.
- Transport: during channel formation median arrival / tau_res rises (gypsum-only ~0.79-0.87 -> 0.91-0.95), tail exponent
  steepens (~3.1-3.7 -> 4.0-4.5), dispersivity falls; all recover after the channel dissolves through (coarse probes; finer probes
  updating overnight; phase1_tracer.csv). Example network (x6 sigma 1 seed 1, gypsum-only): median 0.64 -> 0.85 -> 0.77 of tau_res,
  gamma 2.4 -> 3.3 -> 2.6 (unreacted -> channel peak -> after widening).
- Channel-depth law (early Phase 2, sigma 1 seeds 1-3, x4/x6/x8): ceiling x10 gypsum-only 0.695/0.678/0.656; x10.6 coupled phi0
  0.05 0.694/0.672/0.665; ~x10 coupled 2 mM 0.701/0.675/-; x5.5 coupled 0.779/0.760/0.799; x20 gypsum-only phi0 0.05
  0.625/0.601/-. Same ceiling -> same depth within ~0.01 regardless of chemistry. Inheritance 0.95-0.99 even at x20.
- 2 mM coupled: no rerouting yet (depth matches gypsum-only, inheritance 0.97-0.99).

## What is new vs known
Known/consistent: network channels follow initial structure (Hyman 2026; Szawełło 2026); replacement Gamma limits permeability gain
(Budek & Szymczak); reaction partly erases heterogeneity. Candidates: (1) flow / pore-space decoupling in mineral-filled networks;
(2) channelization narrows transport; (3) compact front not wormhole at km scale; (4) channel-depth law set by achievable
permeability contrast; (5) precipitation rerouting (2 mM test). No km-scale reactive DFN with thousands of fractures found in the
literature (largest: 25 m / ~526 fractures graph, Hyman 2026; 10 m meshed DFNs); coupled 3D DFN only Hyman 2024 IJGGC (10 m).

## BiGraFV caveats (must be stated)
One control volume per fracture: no in-plane fronts or wormholes; a long fracture opens along its whole length at once; dead ends
represented approximately. On smaller paired TPL networks meshed DFNs channelized more than the one-cell graph (n90 ratio 0.79 vs
0.94 and 0.84 vs 0.88 on two dense networks); graph channel timing lagged at strong k-phi feedback. The network-scale argument for a
compact front (9-44 parallel paths over 1 km, gain capped at x10-x20) applies to a meshed DFN too; front sharpness may be model-dependent.

## Figures available (forsmark_reactive/report_phase1/img/ unless noted)
channel_pr_vol_{tcap,pv,tauH}.png, channel_active_area_{tcap,pv,tauH}.png, inheritance_{tcap,pv,tauH}.png,
mechanism_{gyponly,gypcal}_{tcap,pv,tauH}.png, decoupling_scatter_{gyponly,gypcal}.png, depth_law.png, breakthrough_dissolved.png,
phase1_dissolved.png, phase1_keff.png, phase1_n90.png, paired_p{4.0,6.0,8.0}_mineral.png, paired_p6.0_flow.png,
tracer_btc_example.png, tracer_metrics_{gyponly,gypcal}.png (coarse; three-axis fine versions will appear in
forsmark_reactive/phase1/figures/tracer_metrics_<mode>_<tcap|pv|tauH>.png and tracer_btc_annotated_<mode>.png),
anim/ (being redone).

## CORRECTIONS from the literature check (REFERENCES.md, 3 Nov evening) — these override anything above
1. Active surface area: the published d_Q (Maillot et al. 2016 WRR Eq. 8; Hyman 2020 WRR, 2024, 2026) uses the fracture FLOW Q_f:
   d_Q = (sum S_f Q_f)^2 / (V sum S_f Q_f^2), reported as 100 d_Q/P32. The old dQ_P32 column IS this. It FALLS with density
   (start, median: x4 ~22.5 %, x6 ~17.5 %, x8 ~15.0 %) while PR_V RISES (0.35/0.42/0.53). Both are real and measure different things:
   denser networks carry flow more in proportion to fracture volume, but a smaller share of fracture surface carries significant
   flow (most added fractures are small and nearly idle; share of fractures by count carrying flow 0.041 -> 0.034). The figures
   channel_active_area_* now use the published form. (Earlier today the page "corrected" this to a flux-density form; that was wrong.)
2. Hyman 2020 is Water Resources Research 56(9), e2020WR027986 (not Front. Phys.). Fox et al. 2007 authors: Fox, La Pointe,
   Hermanson, Öhman.
3. t_cap is OUR construction (not a published quantity). Closest published form: Szymczak & Ladd 2009 Eq. 52 (injected volume
   relative to the volume needed to dissolve solid equal to the initial pore space); t_cap = that / 9 at vf0 0.9. Acid capacity
   gamma (Hyman 2026 p. 6) backs the capacity idea. Fredd & Fogler PVbt only from secondary sources. c_cap is an upper bound
   (pilot ~470 vs 516.6 mol/m^3 for the brine, ~9 %).
4. tau = Delta V / V0 is Hyman 2026 Eq. 26 (tau <= 1, dissolution only); our use beyond 1 and with calcite subtracted is our extension.
5. "One pore volume per year": Hyman 2024 says "initial volume of each fracture network per year" (phi0 0.01), ambiguous between
   bulk and pore volume; ours is pore volume (a choice).
6. TRANSMISSIVITY DEPTH MISMATCH: intensities are SKB TR-10-52 Table 6-75 for 200-400 m (verified), but T(r) = 6.3e-9 r^1.3,
   sigma 1.0 is the table's model for depths ABOVE 200 m; for 200-400 m it gives semi-correlated 1.3e-9 r^0.5 (sigma 1.0) and
   correlated 1.6e-9 r^0.8. ~190x difference in T at r = 100 m; sigma = 0 in our code also uses the semi-correlated (a, b).
   With a fixed rate the absolute T does not matter, but the size-T contrast does. Label networks as "FFM01 200-400 m geometry
   with the FFM01 0-200 m transmissivity model"; flag to the user as a decision (rebuild with the depth-consistent law?).
7. Gypsum specific surface 750 m^2/kg lies inside the paper's Table 1 range 486-4670 (units m^2/kg per the paper's text).
8. BiGraFV is unpublished; cite as this work.

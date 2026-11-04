# PI fix list for index.html (from Karen's review, 3 Nov evening). Apply all; numbers here are recomputed from the CSVs.

Already done by PI: lede range now "1,587 to 4,070 fractures (a fourth, denser set of 7,849 to 8,229 fractures is running)";
depth table rows labelled Phase 1 / Phase 2.

MUST
1. 5b density sentence: replace the "share of fractures by count carrying flow falls 0.041 -> 0.034 ... most added fractures are small
   and nearly idle" claim with: "the participation ratio per fracture, PR_Q/N, falls (0.041, 0.041, 0.034 at x4/x6/x8), while the
   share of fractures in the 90 %-flow set rises (0.17, 0.22, 0.28). Why published d_Q falls while PR_V rises is not settled; one
   hypothesis is that added fractures carry flow in proportion to their volume but add surface where little flow passes." Mark as
   hypothesis. Keep d_Q/P32 22.5/17.5/15.0 % and PR_V 0.35/0.42/0.53.
2. Stage timings everywhere (table in 5c, text, capacity-clock caption, "In brief"): PR_V minimum at t_cap ~0.3-0.6 (Phase 1
   medians 0.37 gypsum-only, IQR 0.27-0.50; 0.46 coupled, IQR 0.39-0.62); breakthrough (outlet >= 50 %) at t_cap ~0.5-0.75
   (medians 0.59 gypsum-only, IQR 0.50-0.68; 0.73 coupled, IQR 0.62-0.73); note breakthrough times are quantised by the save
   schedule. PR_pore minimum t_cap 0.1-0.3 stays.
3. "Same clock": say "approximately the same clock on capacity time: the coupled run's channel minimum and breakthrough come about
   0.1-0.15 later in t_cap". Cartoon capacity_clock text says peaks at 0.4-0.6: in its caption add "(measured: PR_V minimum 0.37
   gypsum-only, 0.46 coupled)". Do not edit the SVG drawing beyond the caption.
4. "dissolved fraction ~ t_cap within 0.01": replace with "within 0.01 for gypsum-only (worst 0.04); coupled dissolution lags its
   ideal t_cap by about 3 % (median, up to 10 %), consistent with c_cap being an upper bound". Remove the confused sentence about
   coupled curves sitting to the right.
5. Transport (5e, 6.2, In brief): use the FINE probes only (phase1_tracer.csv now holds only fine probes; n = 36 of 45 networks per
   chemistry, rest still running). Medians [IQR]:
   gypsum-only: t50/tau_res 0.77 [0.71-0.81] at start -> 0.90 [0.87-0.93] at t_cap 0.5 -> 0.83 at the end (t_cap 5);
     gamma 3.15 [2.73-3.77] -> 4.03 [3.61-4.48] -> 3.06; alpha_L 190 m -> 143 m -> 194 m.
   coupled: t50/tau_res 0.71 [0.65-0.76] -> 0.86 [0.83-0.90] at t_cap 0.63 -> 0.79 later; gamma 3.22 -> 3.90 [3.39-4.52] -> 3.08;
     alpha_L 188 m -> 146 m -> 198 m.
   Say gamma and alpha_L recover; t50/tau_res recovers partly (stays above its start). Example network table (x6 sigma 1 seed 1,
   gypsum-only, fine probes) 0.64/0.85/0.77 and gamma 2.4/3.3/2.6 at t_cap 0/0.5/2.0 is correct; label it "fine probes".
   Remove "coarse probes" wording. Add the tau_res offset: coupled probes start with tau_res 1.10 vs 1.01 because the coupled runs
   make the boundary helper cells mineral-free (porosity 1), so the probe counts their volume as pore space; comparisons are made
   within each chemistry; the start offset 0.71 vs 0.77 is this effect. Note figures/numbers update when all 45 are probed.
   Add Eulerian caveats: finite pulse 0.1 tau_res, window 10 tau_res truncates the tail; fit window ours.
6. Channel-depth law (6.4, In brief): quote paired differences instead of "within about 0.01":
   Phase 1 coupled (x5.5) minus gypsum-only (x10), same network, 45 pairs: median +0.126, all positive;
   x20 (phi0 0.05) minus x10 (phi0 0.1) gypsum-only, 6 pairs: -0.07 to -0.20, all negative;
   x10.6 coupled phi0 0.05 vs x10 gypsum-only, 9 pairs: median |diff| 0.009, max 0.032; 2 mM coupled vs gypsum-only, 6 pairs:
   median 0.007, max 0.032. Single runs vary 0.49-0.80 at a fixed ceiling, which is why paired differences are used.
   Keep the "what could make it wrong": x5.5 vs x10 changes chemistry with the ceiling; x20 and x10.6 change phi0.
SHOULD
7. Stage-1 example: "PR_pore 0.38 -> 0.20 (x6, sigma 1, seed 1, gypsum-only, by t_cap 0.09)". "PR_pore back near its start":
   "median 0.96 of its start (IQR 0.85-1.08)".
8. Porosity-0.05 breakthrough: "per-P32 medians 0.49-0.62 (3 runs each); single runs 0.41-0.73". Add: "first saved state with outlet
   >= 50 % is an upper bound; the outlet jumps from ~0.27 to ~0.63 within one saved interval".
9. Inheritance: add the supporting measures: share of peak-channel flow carried by initial-set fractures 0.936 (gypsum-only), 0.928
   (coupled) against 0.90 by definition at the start; newly recruited fractures 2.3 % / 1.9 % of the peak set. Define "channel peak"
   for inheritance as the n90 minimum (depth uses the PR_V minimum) and say so.
10. Compact front: in "In brief" and 6.3 header use "candidate, model-dependent" wording; the one-cell model cannot form an in-fracture
    wormhole by construction.
11. Phase 1 depth ranges: gypsum-only "0.63-0.68 across P32 and sigma (medians of 5 seeds); single runs 0.49-0.80"; coupled
    "0.76-0.80".
12. Fox et al. 2007: cite where the FFM01 sets are described, or drop it from the list. (Cite it: the networks use the SKB FFM01 model.)
13. d_Q symbol: Q_f = fracture throughflow (max of inflow and outflow over its intersections), which equals half the absolute
    exchanged flow for interior fractures.
14. Gamma: cite Budek, Szymczak & Kang 2026 alone (Eq. 9, verified); drop Budek & Szymczak 2025 from that sentence.
NICE
15. 750 m^2/kg: add "(units as given in the paper's text)".
16. State as "not traced in this review" or remove: pilot ~470 mol/m^3 (keep; it is from the pilot results file
    forsmark_reactive/pilot/PILOT_RESULTS.md and BRIEF); head gradient 1e-4-1e-3 (keep, from run logs); "25 m / ~526 fractures"
    (keep only if in REFERENCES or lit note forsmark_reactive/lit/lit_large_dfn_reactive.md; that note has it).

# Phase 0 pilot (2 Nov 2026)

## Networks (Forsmark FFM01 sets, 1000 x 250 x 250 m, SKB transmissivity sigma 1.0)
Built with `build_km_graph_network.py --forsmark --domain km250 --layer L --rmin R --p32-scale S --sigma 1.0 --seed N --no-geo`;
structure from `forsmark_network_stats.py` (`network_stats.json` in each folder). Paths: fracture-disjoint (node) and
intersection-disjoint (edge) inlet -> outlet paths on the fracture graph; backbone = fractures left after removing dead ends.

At the real FFM01 intensity (one-sided SKB P32, x1) nothing percolates: layer 2 at rmin 5 m gives 7,447 fractures in
5,738 clusters, none spanning x; layer 1 and layer 2 at rmin 10 m (x1, x2) fail the same way. L2 rmin 15 m x2 connects
with 474 fractures through a single fracture (1 node-disjoint path).

| net (layer 2) | fractures | mean degree | in / out fractures | node paths | edge paths | backbone % | cells | connections |
|---|---|---|---|---|---|---|---|---|
| r10 x3 s1 / s2 | 2638 / 2822 | 3.7 | 45/43, 50/44 | 5 / 4 | 13 / 9 | 70 / 71 | 8.1k / 8.7k | 10k / 11k |
| r10 x4 s1 / s2 | 4209 / 4227 | 4.3-4.5 | 72/79, 78/70 | 9 / 13 | 32 / 54 | 78 | 14.4k / 14.7k | 19k / 20k |
| r10 x6 s1 / s2 | 7304 / 7108 | 5.8-6.0 | 151/140, 140/123 | 31 / 32 | 131 / 107 | 88 | 30.6k / 30.2k | 45k |
| r10 x8 s1 / s2 | 10450 / 10013 | 7.4-7.6 | 226/188, 190/177 | 59 / 54 | 182 / 169 | 94 | 51.9k / 50.7k | 80k / 79k |
| r15 x3 s1 / s2 | 1026 / 1129 | 4.0 | 23/22, 14/15 | 5 / 5 | 12 / 13 | 75 / 77 | 3.4k / 3.8k | 4.4k / 4.9k |
| r15 x4 s1 / s2 | 1608 / 1744 | 4.7-4.9 | 35/33, 22/36 | 11 / 10 | 30 / 20 | 83 | 6.0k / 6.6k | 8.2k / 9.1k |
| **r15 x6 s1** / s2 | **2714** / 2768 | 6.6-6.7 | 58/52, 52/69 | **23** / 23 | 50 / 50 | 91 | 12.7k / 13.0k | 19k / 20k |
| r15 x8 s1 / s2 | 3812 / 3854 | 8.5-8.7 | 83/90, 69/93 | 39 / 38 | 82 / 69 | 95-96 | 21.4k / 22.1k | 34k / 35k |

Build time: 1-33 s generation + graph + steady flow per network.

## Reactive timing pair (L2_r15_p6.0_s1_seed1)
Settings: one pore volume per year (83.09 m^3/y), gypsum vf0 0.9 (phi0 0.1), PERMEABILITY_POWER 1 with reference porosity 0.1,
k_gyp 1.62e-3 mol/m^2/s (template x 21.95, the Hyman 2024 IJGGC Table 1 maximum), k_cal 2.29e-5, gypsum SSA 750 m^2/kg,
calcite area 200 m^2/m^3 fixed. gypcal brine: 0.5 M CO3, 1.0 M Na, pH 11.39 (Table 2). dt cap 0.57 tau, run to 7,303 PV
(gypsum-only capacity x 1.0). Env: DIRECT=0 NP=2 STEADY_INIT=1 TS_ACCEL=10 STABILIZE="--dirichlet-outflow 2e5". Script: `run_pilot.sh`.

| run | wall (2 ranks) | steps | dissolved at 120 / 730 / 7303 PV | k_eff x at end | n90 start -> min -> end | dQ/P32 start -> min -> end |
|---|---|---|---|---|---|---|
| gyponly | 632 s | ~12.9k | 0.017 / 0.10 / 0.634 | 9.60 (max 10 at n = 1) | 458 -> 248 -> 344 | 11.75 -> 10.26 -> 11.27 |
| gypcal | 526 s | ~12.9k | 0.469 / 0.853 / 0.966 | 5.43 | 458 -> 288 -> 462 | 11.75 -> 10.56 -> 11.80 |

Coupled run: calcite formed / gypsum dissolved = 1.000 at every time (whole-network totals), so all Ca precipitates where it is
released: local replacement. Calcite's molar volume (36.93 vs 74.69 cm^3/mol) leaves porosity ~0.1 + 0.9 x 0.506 = 0.555,
and k_eff 5.43 is close to the uniform n = 1 value for that porosity (0.555 / 0.1 = 5.55; 3.4 % of the gypsum is left). Gypsum dissolves ~31x faster per pore volume than in gypsum-only
(the carbonate is a Ca sink), so the pair separates in time; compare both at matched pore volumes and at matched dissolved fraction.

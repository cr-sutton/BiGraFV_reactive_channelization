# Literature: large-scale reactive transport in 3D fracture networks (search of 3 Nov 2026)

Scope: what is already published that bears on our km-scale Forsmark FFM01 BiGraFV runs (1000 x 250 x 250 m, 1,600-4,000 fractures, ~8,000 coming; gypsum-only vs gypsum->calcite, Hyman et al. 2024 IJGGC chemistry, 1 PV/yr, high Da).

How each entry was checked:
- **[full]** = full text read locally (PDF in ~/Downloads or downloaded to the scratchpad and converted to text).
- **[abs]** = only the abstract and bibliographic record were checked (publisher page, OSTI, eScholarship, DOAJ, indexing sites).
- **[U]** = some detail is not verified: a DOI quoted from memory or from a citing paper, a number, or a claim. The specific item is named.

---

## 1. Largest 3D DFN / graph reactive-transport studies with dissolution and/or precipitation

### Summary answer
- **We found no published reactive study (dissolution or precipitation) on an explicit 3D DFN or fracture graph at km scale with thousands of fractures.** The largest explicit 3D network reactive studies are:
  - about 25 m with about 500 fractures (graph model);
  - about 10 m with 80-200 fractures (full meshed DFN in PFLOTRAN).
- At Forsmark, km-scale reactive transport has been run only as DFN-*derived* continuum (ECPM / dual-continuum) models, for oxygen ingress. None has a per-fracture network.
- **Coupled dissolution-precipitation in a 3D DFN:** we found no study other than Hyman et al. 2024 IJGGC, which states it is the first. The later coupled studies use other geometries:
  - Hyman et al. 2026 TiPM: a 2D fracture-matrix model with the same gypsum->calcite system.
  - Budek, Szymczak & Kang 2026 EPSL: a 2D pore network with one fracture.
  - Steefel & Hu 2022: 2D.
  - Boampong et al. 2026 Chem Geol: 3D, olivine, geometry not checked [U].

  Within our search, our runs would be both the first km-scale reactive DFN/graph study and the first coupled dissolution-precipitation study on networks larger than 10 m.

### Table of 3D network reactive studies (largest first by network size)

| Study | Domain | Fractures | Networks / runs | Model | Chemistry | Check |
|---|---|---|---|---|---|---|
| Hyman, Szawełło, Kang & Szymczak 2026, JGR Solid Earth 131, e2025JB033004, doi:10.1029/2025JB033004 | 25 x 10 x 10 m (Pietrasecca-fault-inspired, 3 families, power-law r 1-5 m) | mean 526 per network (P32 = 7.72) | 30 DFNs x 9 (Da, G) pairs | graph/pipe network (nodes = intersections, each fracture a k-clique; Hyman et al. 2018), quasi-steady Reynolds flow, first-order kinetics with Sherwood mass transfer (Szymczak & Ladd 2012) | generic dissolution only | [full] |
| Szawełło, Hyman, Kang & Szymczak 2026, Int J Rock Mech Min Sci 200, 106431, doi:10.1016/j.ijrmms.2026.106431 (arXiv 2602.06279) | same 25 x 10 x 10 m DFN converted to a pipe network, compared with regular and disordered pore networks | as above | ensembles | poreNetDP (Szawełło, Zenodo 18603308) | dissolution only | [full] |
| Pachalieva, Hyman, O'Malley, Viswanathan & Srinivasan 2025, Front. Environ. Sci. 12:1454295, doi:10.3389/fenvs.2024.1454295 | 10 m cube, mono-disperse r = 1.5 m discs, P32 3.25 | mean 133 per network (446,129 fractures in total) | 800 DFNs x 4 rate constants (3,256 runs reported) | meshed DFN (dfnWorks + PFLOTRAN, 0.05 m mesh), plus random-forest regression on graph features | quartz dissolution (80 % initial quartz fill), flow = network volume per year | [full] |
| Hyman, Navarre-Sitchler, Sweeney, Pachalieva, Carey & Viswanathan 2024, G-cubed 25(7), e2024GC011550, doi:10.1029/2024GC011550 | 10 m cube, 3 orthogonal families, r = 2 m | mean 80 per network (about 157k nodes / 307k cells per mesh) | 30 DFNs, unreacted vs quasi-steady dissolved | meshed DFN, PFLOTRAN | quartz dissolution | [full] |
| Hyman, Murph, Boampong, Navarre-Sitchler, Carey, Stauffer & Viswanathan 2024, IJGGC 139, 104265, doi:10.1016/j.ijggc.2024.104265 | (a) one 100 x 2 m fracture; (b) 10 m cube, 2 m square fractures, P32 3.2, uniform k = 8.3e-10 m² (b = 1e-4 m) | about 10^2 per network (count not given in the text we extracted) [U] | 385 generic networks, LHS over Q, D, k_gyp, k_cal, surface areas, porosity | meshed DFN (dfnWorks + PFLOTRAN, about 0.1 m triangles) | **gypsum dissolution -> calcite precipitation**, the first coupled study in 3D DFN (stated by the authors) | [full] |
| Hyman, Navarre-Sitchler, Andrews, Sweeney, Karra, Carey & Viswanathan 2022, GRL 49(15), e2022GL099513, doi:10.1029/2022GL099513 | explicit 3D DFNs (sizes not checked) | not checked [U] | ensemble | dfnWorks + PFLOTRAN | dissolution; geostructural correction to TST apparent rate | [abs] |
| Jiang, Wang, Pu & Jourde 2022, J. Hydrol. 610, 127831, doi:10.1016/j.jhydrol.2022.127831; follow-up Jiang et al. 2023, J. Hydrol. 129303 (3D vs 2D) [U: 2023 DOI] | two jointed carbonate layers plus a bedding plane, 3D DFN of 2D planes | not checked [U] | synthetic | 3D hydro-chemical karst model | calcite dissolution (karst initiation); pipes guided by joints vs sheet-like bedding-plane enlargement, set by the initial flow regime | [abs] |
| Kaufmann, Romanov & Hiller 2010, J. Hydrol. 388, 241-250 (KARSTAQUIFER) [U: DOI] | 3D fracture + matrix block, 100 m head drop | fracture grid, not a stochastic DFN | scenarios | 3D karst evolution | calcite dissolution | [abs] |
| Boampong, Murph, Hyman, Navarre-Sitchler & Viswanathan 2026, Chem. Geol. 123512, "Unravelling controls on carbon mineralization in fractures: insights from 3D reactive transport simulations in olivine" | not checked | not checked | not checked | 3D (DFN or single fracture not checked) | olivine dissolution -> carbonate | [U] (seen only in the TiPM 2026 reference list) |
| Harb, Grandia, Trinchero & Hyman, EGU 2023 abstract EGU23-9694 | dfnWorks extended with geochemistry, applied to a real fracture-filling case | not checked | n/a | dfnWorks + reactions | fracture filling / sealing | [abs] (conference abstract only; we found no journal paper) |

Related but not 3D DFN (2D, continuum, or pore network):
- **Hyman, Dell'Oca, Navarre-Sitchler & Viswanathan 2026**, Transp. Porous Media 153:100, doi:10.1007/s11242-026-02352-y. **[full]**
  - Same gypsum -> calcite system, but in a 2D fracture-matrix plane (dfnWorks + PFLOTRAN) with global sensitivity analysis.
  - The fracture-matrix permeability contrast and the strength of diffusion control mineralization. Reaction rates and surface areas have negligible influence.
  - As the permeability contrast grows, flow channelizes and less of the formation contacts the injectate.
- **Steefel & Hu 2022**, WRR 58, e2022WR032321, doi:10.1029/2022WR032321. **[full abstract + methods]**
  - 2D CrunchFlow model on a photograph-derived granite fracture network.
  - Mixing-driven precipitation at fracture intersections substantially changes flow connectivity.
  - A second part models forsterite -> magnesite weathering in the unsaturated critical zone, where trapped carbon is modest.
- **Trinchero, Molinero, Ebrahimi, Puigdomenech, Gylling, Svensson et al. 2018**, Math. Geosci. 50, 549-567, doi:10.1007/s11004-017-9718-6. **[abs]**
  - Oxygen intrusion into Forsmark with a "continuum-based, DFN-consistent" HPC framework (DarcyTools + PFLOTRAN family).
  - Physical and mineralogical heterogeneity control where oxygen penetrates.
  - This is the closest km-scale Forsmark reactive model, but it is a continuum, not a per-fracture network.
- **Molinero & Samper 2006**, J. Contam. Hydrol. 82, 293-318, doi:10.1016/j.jconhyd.2005.10.008. **[abs]**
  - 2D large-scale reactive model of the fracture zones at the Äspö Redox Zone Experiment.
  - Includes calcite, quartz, hematite and pyrite dissolution-precipitation, plus cation exchange.
- **Pandey & Rajaram 2016**, WRR 52, 9344-9366, doi:10.1002/2016WR019026. **[abs]**
  - PFLOTRAN on DFNs and correlated permeability fields; the DFNs are likely 2D [U].
  - Preferential flow causes the domain-averaged weathering rate to decline even while much mineral remains; the decline does not follow 1/√t.

---

## 2. Channel inheritance vs emergence

### Network-scale evidence (closest to our result)
- **Hyman, Szawełło, Kang & Szymczak 2026 JGR** [full]
  - Three regimes on the graph:
    - Low Da: uniform, mildly channelized.
    - Intermediate Da: channeling; several parallel inlet-to-outlet channels enlarge along their whole length.
    - High Da and low G: wormholing; a front advances from the inlet and one or a few pathways survive.
  - "Across all regimes, initial fracture heterogeneity persists" (abstract).
  - At low Da, apertures widen almost uniformly and some flow moves into previously unfavourable fractures. Homogenization is still not reached, because the main heterogeneity in a DFN is the wide spread of path lengths, which dissolution cannot erase.
  - Once a wormhole breaks through, channelization stops and only that conduit keeps widening.
  - Metrics used:
    - backbone = union of the top 100 flow paths from particle flow topology graphs (Hyman et al. 2017);
    - backbone share of surface area (about 21 % initially, falling with Da, stabilizing by τ = 0.5);
    - particle BTC, tail exponent, tortuosity, longitudinal dispersivity, flux-weighted Eulerian velocity PDF;
    - flow focusing profile.
  - Time proxy: τ = dissolved volume / initial volume.
- **Szawełło, Hyman, Kang & Szymczak 2026 IJRMMS** [full]
  - The flow focusing profile shows a focusing front from the inlet in the wormholing regime, a system-wide decrease under uniform dissolution, and amplification of pre-existing paths in the channeling regime.
  - Uniform dissolution cannot remove heterogeneity that comes from network topology. This topological heterogeneity, more than aperture variance, limits homogenization.
- **Szawełło, Hyman, Kang & Szymczak 2024**, GRL 51(20), e2024GL109940, doi:10.1029/2024GL109940 [abs].
  - Introduces the spatial flow focusing profile. Its time evolution separates wormholing from channeling, and heterogeneity shifts the transition between them.
- **Menke et al. 2023**, Sci. Rep. 13, 11312, "Channeling is a distinct class of dissolution in complex porous media" [U: authors and DOI not checked; title from the IJRMMS reference list].
  - Channeling = pre-existing paths enlarge (inheritance). It needs heterogeneity.
- **Hyman et al. 2024 G-cubed** [full]
  - Dissolved networks have lower resistance and are more channelized.
  - Mean particle breakthrough is about two orders of magnitude earlier and effective aperture about one order of magnitude larger, with large network-to-network variability.
  - Primary/secondary subnetworks were defined *topologically*, without flow information (Hyman et al. 2018 bipartite / current-flow method). The authors describe a "dissolution feedback loop between primary sub-networks and geochemical reactions".
  - Older systems should therefore be more channelized.
- **Pachalieva et al. 2025** [full]
  - A primary subnetwork forms where quartz is fully dissolved.
  - Topological distance to the backbone and the rate constant are the two strongest predictors of the quartz remaining per fracture. The quartz left outside the backbone varies widely.
  - This is direct evidence that the reactive outcome is set by the initial (topological) backbone.
- **Jiang et al. 2022 J. Hydrol.** [abs]: in layered 3D joint networks, the initial flow regime and network architecture set the dissolution morphology (joint-guided vertical pipes vs bedding-plane sheets).

### Single-fracture and theory evidence (what controls emergence)
- **Upadhyay, Szymczak & Ladd 2015**, JGR Solid Earth 120, 6102-6121, doi:10.1002/2015JB012233 [abs, first pages read].
  - In a single rough fracture, dissolution patterns and flow rates are *surprisingly insensitive* to the amplitude and correlation length of the initial aperture field. Flow self-organizes into a few wormholes whose spacing is set by the longest wormholes.
  - A seeded high-aperture region competes with spontaneous nucleation elsewhere.
  - So inside one fracture the pattern is emergent, not inherited, which is the opposite of the network results above.
  - Interpretation (ours): inheritance in networks comes from topology and path length, which dissolution cannot change, not from aperture noise.
- **Szymczak & Ladd 2009**, JGR 114, B06203, doi:10.1029/2008JB006122 [abs]: 3D pore-scale fracture dissolution; competition between wormholes and the optimal conditions for wormholing.
- **Szymczak & Ladd 2006**, GRL 33, doi:10.1029/2005GL025334 [abs].
  - A resistor-network model of channel competition reproduces 3D pore-scale fracture dissolution.
  - The number of channels falls with time, and channel lengths become power-law distributed (exponent about 1.2, per an EGU abstract [U]).
- **Szymczak & Ladd 2012**, J. Fluid Mech. 702, 239-264, "Reactive-infiltration instabilities in rocks. Fracture dissolution" [U: DOI 10.1017/jfm.2012.174 from memory]: linear stability theory and the source of the Sherwood/G formulation used by Hyman 2026.
- **Budek & Szymczak 2012**, Phys. Rev. E 86, 056318 (arXiv 1211.1712) [abs]: on 2D tube networks, wormholes form over a broad range of conditions; network geometry matters.
- **Detwiler, Glass & Bourcier 2003**, GRL 30(12), 1648, doi:10.1029/2003GL017396 [abs].
  - In transparent analog fractures (KDP against textured glass), lower Pe gives ramified wormholes and higher Pe gives more uniform dissolution (Pe 54 vs 216, as quoted by later work).
- **Detwiler & Rajaram 2007**, WRR 43, doi:10.1029/2006WR005147 [abs, U]: an enhanced depth-averaged model predicts dissolution patterns in variable-aperture fractures.
- **Hanna & Rajaram 1998**, WRR 34 [U: DOI 10.1029/98WR01863]: aperture variability speeds up channelized growth of fissures in karst.
- **Deng & Peters 2019**, Environ. Eng. Sci. 36(1), 90-101, doi:10.1089/ees.2018.0244 [abs].
  - 2D calcite-only model validated against XCT of carbonic-acid core floods.
  - Channelization gives accelerating transmissivity growth.
  - Mineral heterogeneity can promote *or* suppress channel formation, depending on where the reactive mineral sits.
- **Li, Hu, Szawełło, Yang, Chen, Szymczak & Zhou 2026**, GRL, "From Core to Field: Pattern Selection in Dissolving Fractures" [full; DOI not found in our copy, U].
  - Compact / wormhole / uniform patterns collapse onto one phase diagram whose two dimensionless groups explicitly include fracture length (validated 0.1-30 m).
  - The optimal injection rate for permeability gain scales linearly with fracture length.
  - The paper cites Starchenko & Ladd 2018: the critical Da for the uniform-to-wormhole transition decreases with fracture length [U: Starchenko & Ladd citation details].
- **Ishibashi et al.**: we found channeling-flow papers (GeoFlow DFN, WRR 2012; JGR 2015, doi:10.1002/2014JB011555, about flow in 5-20 % of the fracture plane) but **no Ishibashi dissolution / channel-inheritance study** [U: may exist under another title].
- **Kang / Le Borgne**: we found no Kang or Le Borgne paper on dissolution-channel inheritance in networks beyond Kang's co-authorship of Hyman 2026 and Szawełło 2024/2026. Their reactive work is on mixing and precipitation (Section 3).

**What controls whether new paths emerge (synthesis):**
1. Da and G. Low Da (penetration length >> system length) widens many paths and recruits off-backbone fractures. High Da with low G localizes onto a few inherited paths. High G (diffusion-limited) slows the widest fractures, so more parallel paths survive.
2. The type of heterogeneity. In networks, topology and path length dominate, so the result is inheritance. Within a single fracture, aperture noise is forgotten, so the pattern is emergent.
3. Breakthrough. After the first wormhole reaches the outlet, reorganization stops.
4. Fracture length and Da defined per fracture (Li 2026; Starchenko & Ladd).
5. Where the reactive mineral sits (Deng & Peters 2019).
6. For coupled precipitation, the Fogler number and Γ (Section 3), which can force rerouting.

---

## 3. Precipitation, clogging and self-sealing in fractures and networks

- **Jones & Detwiler 2016**, GRL 43(14), 7564-7571, doi:10.1002/2016GL069598 [abs].
  - 82-day calcite precipitation experiment in an analog fracture with patchy CaCO3 seeds.
  - Preferential flow persisted along paths with 82 % less seed area than average.
  - Ignoring this heterogeneity underestimates sealing time by more than 10x.
  - Follow-up: Jones & Detwiler 2019, WRR, doi:10.1029/2018WR024287, a 3D level-set model of mineral heterogeneity [abs].
- **Elkhoury, Detwiler & Ameli 2015**, EPSL 417, 99-106, doi:10.1016/j.epsl.2015.02.010 [abs read in full].
  - Fractured dolomitic anhydrite: anhydrite dissolved preferentially and left a compacted dolomite layer.
  - Low flow: near-equilibrium, preferential paths persisted for 6 months, negligible permeability change.
  - High flow: permeability fell by about 100x (self-healing).
  - Scaling suggests dissolution channels may outweigh self-healing at larger scales.
  - Earlier work: Elkhoury, Ameli & Detwiler 2013, IJGGC 16, S203-S215, CO2-rich brine in fractured carbonates [U: DOI].
- **Noiriel, Seigneur, Le Guern & Lagneau 2021**, Adv. Water Resour. 152, 103916, doi:10.1016/j.advwatres.2021.103916 [abs].
  - XCT + reactive transport model: calcite grows preferentially on calcite over dolomite.
  - The precipitation rate varies along and between flow paths with the local saturation index.
  - A critical SI for nucleation strongly affects predicted sealing.
  - Strong precipitation gradients along the flow direction increase permeability anisotropy.
- **Steefel & Hu 2022 WRR** (see Section 1): mixing at intersections drives precipitation that rewires connectivity. 2D only.
- **Deng & Spycher 2019**, Rev. Mineral. Geochem. 85, 49-74, "Modeling reactive transport processes in fractures", doi:10.2138/rmg.2019.85.3 [abs]: review of single-fracture alteration experiments and models.
- **Menefee, Giammar & Ellis 2018**, ES&T 52(15), 8954-8964, doi:10.1021/acs.est.8b01814 [abs].
  - Fractured basalt cores: carbonates are localized in diffusion-limited zones (dead ends, vesicles), while clays fill the advective paths and could obstruct flow.
  - Fracture volume fell 35 % at 100 °C and 48 % at 150 °C.
  - A GHGT-14 paper also exists; "Controls on mineral carbonation reactions in basalt fracture networks" (WUSTL profile) [U: venue].
- **Chen, Kang, Carey & Tao 2014**, Int. J. Heat Mass Transf. 75, 483-496 [abs; U: author list and DOI].
  - LBM with interface tracking: a secondary precipitate both helps dissolution (it consumes products) and hinders it (it coats the reactive surface, i.e. passivation).
- **Dijk & Berkowitz 1998**, WRR 34(3), 457-470, doi:10.1029/97WR03238 [abs].
  - Two regimes, uniform aperture change vs inlet-localized change, both set by Da and Pe.
  - Precipitation closes a fracture in days to millions of years.
  - Related: Dijk, Berkowitz & Yechieli 2002 WRR, dissolution patterns measured in natural fractures [U].
- **Singurindy & Berkowitz 2003**, WRR, doi:10.1029/2001WR001055 [abs].
  - HCl/H2SO4 through carbonate: dissolution near the inlet and **gypsum precipitation** in the interior give oscillating and eventually clogging conductivity. This is the inverse of our gypsum -> calcite chemistry.
  - Related: Singurindy & Berkowitz (about 2005), Adv. Water Resour., "The role of fractures on coupled dissolution and precipitation patterns in carbonate rocks". Flow-through fractures favour dissolution; isolated fractures favour precipitation [U: year and DOI].
- **Garcia-Rios, Luquot, Soler & Cama 2015**, Chem. Geol. 414, 95-108, doi:10.1016/j.chemgeo.2015.09.005 [title from a reference list; U: findings].
  - CO2-rich *sulfate* solutions through fractured limestone: calcite dissolution with gypsum precipitation, with flow-rate control.
- **Yang, Chen, Lee & Kang 2024**, PNAS 121(28), e2401318121, doi:10.1073/pnas.2401318121 [abs].
  - Microfluidics + 3D simulation: even in laminar flow, inertia at intersections controls precipitation.
  - Low Re: a precipitate layer along the mixing interface self-limits.
  - High Re: fast clogging of the intersection. The effect is stronger at network scale.
- **Bochet et al. (Le Borgne) 2020**, Nat. Geosci. 13, 149-155, doi:10.1038/s41561-019-0509-1 [abs].
  - Ploemeur field site: redox mixing at fracture intersections sustains iron-oxidizer hotspots (field evidence that reactions concentrate at intersections).
- **Budek, Szymczak & Kang 2026**, EPSL 690, 120163, doi:10.1016/j.epsl.2026.120163 [full].
  - Pore network with one through-fracture, coupled A-dissolution / E-precipitation.
  - Parameters: Fo = k2/k1, Γ = χ_E ν_E / (χ_A ν_A) (product-to-reactant solid volume), and Da.
  - Three regimes: passivation, side branching, and uniform replacement.
  - An optimal fracture/matrix conductance ratio maximizes deposition.
  - Fractures *reduce* clogging by sending precipitation into side branches.
- **Budek & Szymczak 2025**, JGR Solid Earth 130(6), e2024JB031081, "Channeling, clogging and permeability oscillations: different macroscopic regimes in mineral replacement" [U: cited in EPSL 2026 and in Budek et al. 2026, not read].
- **Budek, Szawełło, Voller & Szymczak 2026**, Géotech. Lett., doi:10.1680/jgele.25.00094 ("Retreat to advance: self-blocking enables efficient mineral replacement"; arXiv 2603.27336) [full].
  - Replacement is efficient (a) when precipitation is much faster than dissolution (in-situ front), or (b) in an "exploratory" mode: channels self-block at the tip with product, pressure reroutes to a neighbouring corridor, and the cycle repeats.
  - When Γ exceeds the limit at which the product can fill all pore space, high-Fo efficiency collapses. At small Γ, wormholing dominates and Fo matters little.
- **Poonoosamy, Kosakowski, Van Loon & Mäder 2015**, J. Contam. Hydrol. [U: volume and DOI]. Celestite -> barite replacement tank experiment (Γ > 1):
  - continuum models failed without pore-scale information;
  - Kozeny-Carman underestimated the permeability change (later NMR/MRI work).
- **Fernández-Díaz, Pina, Astilleros & Sánchez-Pastor 2009**, Am. Mineral. 94, 1223-1234, doi:10.2138/am.2009.3194 [abs].
  - Gypsum carbonation in Na2CO3 solution proceeds inward from the surface through ACC, vaterite and aragonite to calcite pseudomorphs.
  - How faithfully the pseudomorph keeps the original shape depends on the carbonate concentration.
  - This is the only mineralogical study we found of the gypsum -> calcite reaction itself. Our Γ for it is 36.93 / 74.69 = **0.49**.
- **Lab on a Chip 2025**, doi:10.1039/D5LC00178A [U: authors not retrieved]: microfluidic fracture carbon mineralization; precipitation in dead ends while flowing fractures stay open is critical for sustained mineralization.
- **Nisbet et al. 2024**, Rev. Geophys. 62(4), e2023RG000815, "Carbon mineralization in fractured mafic and ultramafic rocks: a review" [U: from the TiPM 2026 reference list].
- **Banshoya et al. 2023**: calcite dissolution -> anhydrite precipitation in fractured rock, 2D and 3D. Precipitation changed fracture porosity but had little effect on overall permeability [U: summary taken from the Hyman 2024 IJGGC review; venue not checked].
- **Steefel & Lichtner 1998** (Maqarin, J. Hydrol.): natural fracture sealing predicted in agreement with observations [U: citation from the Steefel & Hu 2022 text].

---

## 4. Gypsum reactive transport (karst) and Forsmark / SKB mineral studies

### Gypsum kinetics and gypsum karst
- **Jeschke, Vosbeck & Dreybrodt 2001**, GCA 65(1), 27-34, doi:10.1016/S0016-7037(00)00510-X [abs].
  - Surface-controlled gypsum dissolution has order about 1.2 in (1 - c/c_eq) far from equilibrium and about 4.5 near equilibrium in natural samples.
  - k is about 1.1-1.3e-4 mmol cm⁻² s⁻¹; the indexed abstracts disagree on the value [U].
  - Pure synthetic gypsum stays linear up to equilibrium.
- **Raines & Dewers 1997**, Chem. Geol. 140, "Mixed transport/reaction control of gypsum dissolution kinetics in aqueous solutions and initiation of gypsum karst" [U: authors and DOI inferred from the title record].
  - Gypsum dissolution is under mixed surface/diffusion control.
  - Combined with Colombani's work on the pure gypsum rate constant (GCA 2008 [U]), this supports **transport-limited gypsum dissolution**, consistent with our high Da_f.
- **Dreybrodt 1996**, WRR 32, "Principles of early development of karst conduits under natural and man-made conditions..." [U: DOI 10.1029/96WR01332 from memory]. Also Dreybrodt 1990 (J. Geol.) and **Palmer 1991**, GSA Bull. 103, 1-21, "Origin and morphology of limestone caves" [U: DOI].
  - Breakthrough-time theory: feedback with higher-order kinetics lets the conduit propagate.
- **Gabrovšek & Dreybrodt 2001**, J. Hydrol. 240, 206-224 [U: DOI 10.1016/S0022-1694(00)00323-1]: 2D fracture-network karst evolution in length and depth, where competing conduits emerge.
- **Dreybrodt, Romanov & Gabrovšek 2002**, Environ. Geol. 42, 518-524, doi:10.1007/s00254-001-0514-7 [abs].
  - 2D network of two perpendicular fracture sets below a dam.
  - After a widened path breaks through, leakage becomes excessive within about 25 yr in limestone but **about 5 yr in gypsum**.
- **Romanov, Gabrovšek & Dreybrodt 2003**, Eng. Geol. 70, 17-35, doi:10.1016/S0013-7952(03)00073-5 [abs].
  - 100 m dam in limestone or gypsum. Gypsum widens at least 1 cm/yr, compared with about 1 mm/yr for limestone (as quoted).
  - Limestone and gypsum evolve the same way, only on very different timescales.
- **Klimchouk 2007**, "Hypogene speleogenesis", NCKRI Special Paper 1 [U]: gypsum maze caves form from uniform enlargement of whole fracture networks under confined (hypogene) flow. This is a natural counter-example to single-channel localization, worth citing against the high-Da channel picture.
- **Kaufmann et al. 2010** and **Jiang et al. 2022/2023**: see Section 1. Both are 3D, but for calcite.
- We found **no 3D DFN gypsum reactive transport study** other than the LANL gypsum -> calcite papers (IJGGC 2024; TiPM 2026, which is 2D).

### Forsmark / SKB
- **Sandström & Tullborg 2009**, Chem. Geol., "Episodic fluid migration in the Fennoscandian Shield recorded by stable isotopes, rare earth elements and fluid inclusions in fracture minerals at Forsmark, Sweden", doi:10.1016/j.chemgeo.2009.04.019 [abs record only].
  - Four fracture-mineral generations. The youngest is clay and thin calcite with minor pyrite and goethite.
  - A Palaeozoic stage dissolved earlier fracture minerals and then precipitated calcite, quartz, pyrite and asphaltite.
  - Sandström's 2009 Gothenburg thesis covers the same work.
- **Sandström & Tullborg (about 2007)**, "Paleohydrogeological events in Forsmark, central Sweden, recorded by stable isotopes in calcite and pyrite" [U: venue; one catalogue lists 2007].
- **Sandström, Tullborg, Smellie, MacKenzie & Mazurek 2008**, SKB R-08-102, "Fracture mineralogy of the Forsmark site" [U: report number from memory]. SKB P-05-197 also covers Forsmark fracture minerals and wall-rock alteration [abs].
- **Drake et al. 2018**, Geosciences 8(6), 211, "Ancient microbial activity in deep hydraulically conductive fracture zones within the Forsmark target area" [abs].
  - Calcite/pyrite isotopes record methanogenesis and microbial sulfate reduction in conductive fracture zones; the coatings are mid-Palaeozoic.
  - Laxemar counterparts: Drake & Tullborg, SKB P-08-42 and R-08-99. Calcite is especially frequent in *open*, water-conducting fractures [abs].
- **Trinchero et al. 2018 Math. Geosci.** (Section 1): km-scale DFN-consistent continuum model of O2 ingress at Forsmark.
- **Trinchero et al. 2019**, J. Contam. Hydrol., "Transport of oxygen into granitic rocks: role of physical and mineralogical heterogeneity" (micro-DFN of the matrix, calibrated to Forsmark) [abs; U: DOI]. Most O2 is consumed in "highly reactive pathways", but some diffuses deeper.
- **Sidborn 2011**, SKB TR-10-57: reactive transport assessment of O2 ingress over a glacial cycle (SR-Site) [abs].
- **Iraola, Trinchero, Karra & Molinero 2019**, Comput. Geosci., "Assessing dual continuum method for multicomponent reactive transport" (PFLOTRAN DCDM with calcite) [abs; U: volume, pages, DOI]. Resolving matrix reactions needs very fine grids at the fracture-matrix interface.
- **Trinchero, Sanglas, Iraola, Bosbach & Deissmann 2022/23**, J. Hydrol., "On the parameterisation of dual-continuum models for reactive transport modelling in fractured media" (ScienceDirect PII S0022169422012616) [abs; U: DOI]. Parameterises DFN-based ECPM/DCM reactive models in PFLOTRAN.
- **Joyce, Simpson, Hartley et al.**, SKB R-09-20 and Hydrogeol. J. 2014; **Follin et al. 2014** and **Selroos & Follin 2014**, Hydrogeol. J. [U: DOIs]. These are the FFM01 hydro-DFN parameterisation and regional flow with reference-water mixing. Water mixing is modelled, but not mineral reactions.
- **Hyman, Aldrich, Viswanathan, Makedonska & Karra 2016**, WRR 52, 6472-6489, doi:10.1002/2016WR018806 [abs]. The size-transmissivity correlation sets travel time. Our search did not confirm whether it used Forsmark parameters [U].
- **Conclusion for Section 4:** Forsmark studies give abundant *observations* of calcite fracture fillings and their history, and *continuum* reactive models of redox ingress. We found **no per-fracture network reactive model of calcite (or any mineral) at Forsmark**.

---

## 5. Graph / pipe-network / reduced-order reactive models and their validation

- **Hyman, Hagberg, Srinivasan, Mohd-Yusof & Viswanathan 2017**, Phys. Rev. E 96, 013304, doi:10.1103/PhysRevE.96.013304: graph reductions predict first-passage times; this paper defines the top-k-paths backbone.
- **Hyman, Hagberg, Osthus, Srinivasan, Viswanathan & Srinivasan 2018**, Multiscale Model. Simul. 16(4), 1948-1968, doi:10.1137/18M1180207: bipartite graph backbones. This is also the intersection-node graph that Hyman 2026 uses.
- **Karra, O'Malley, Hyman, Viswanathan & Srinivasan 2018**, Phys. Rev. E 97, 033304, doi:10.1103/PhysRevE.97.033304 [abs].
  - Flow and transport on the graph vs the full DFN: breakthrough times and particle statistics compared.
  - About 10^4 times cheaper. Non-reactive only.
- **Doolaeghe, Davy, Hyman & Darcel 2020**, Phys. Rev. E 102, 053312, doi:10.1103/PhysRevE.102.053312 [abs].
  - **Fracture-node graphs (our BiGraFV one-cell layout) systematically underestimate local flow.** Intersection-node graphs overestimate it in fractures with many intersections.
  - A correction based on intersection count brings the intersection graph close to the DFN.
- **Srinivasan et al. 2018**, Sci. Rep. 8, 11665, doi:10.1038/s41598-018-30117-1: graph + ML for topological uncertainty.
- **Hyman, Szawełło, Kang & Szymczak 2026** [full].
  - The first graph-based *reactive* 3D DFN study we found: kinetic dissolution with a Sherwood mass-transfer coefficient, Da and G sweeps, 30 networks.
  - In the text we extracted, we did not find a reactive comparison of graph vs meshed DFN [U: check the SI]. Validation leans on the single-fracture theory (Szymczak & Ladd 2012) and on regime agreement with porous-media results.
  - Dissolution only; no precipitation.
- **Szawełło et al. 2026 IJRMMS** / **poreNetDP** (Zenodo 18603308): the same pipe-network solver. Flow focusing metric compared across pore and fracture networks.
- **Pachalieva et al. 2025** [full]: meshed PFLOTRAN DFN reactive runs + graph topological features (degree, current-flow centrality, distance to backbone) + random forest. Graph features predict per-fracture reactive outcome. This is a learned, not a mechanistic, reduced model.
- **Szymczak & Ladd 2006 GRL**: resistor network of competing dissolution channels validated against 3D pore-scale fracture dissolution. This is the oldest reactive "graph" validation we found.
- **Budek & Szymczak 2012 PRE** and **Budek et al. 2026 EPSL**: reactive pore networks with dissolution and precipitation (2D). Mechanistic network-level regime maps, not validated against DFN.
- **Hyman 2020**, WRR 56(9), doi:10.1029/2020WR027986 [abs]: network-scale channeling decreases as density increases; Lagrangian graph ranking of flow paths.
- **Sherman, Hyman, Dentz & Bolster 2020**, JGR Solid Earth, doi:10.1029/2019JB018547 [abs]: as density decreases, solute channels into large fractures more strongly.
- **Kang, Hyman, Han & Lee 2020**, WRR, "Anomalous transport in three-dimensional discrete fracture networks: interplay between aperture heterogeneity and injection modes" [U: DOI 10.1029/2020WR027378 from memory]. **Frampton, Hyman & Zou 2019**, WRR 55(7), 5487-5501, doi:10.1029/2018WR024322 (connected vs disconnected internal aperture textures). These are the non-reactive in-fracture heterogeneity references.
- **Hyman, Purswani, Pachalieva, Mellas, Aquino, O'Malley, Navarre-Sitchler, Sweeney & Viswanathan 2026**, Géotech. Lett., doi:10.1680/jgele.25.00092 [full abstract]: perspective on channelization across scales. It proposes 3D-printed fractures to validate single-fracture DNS and graph ML at network scale.
- Classical pipe networks: Cacas et al. 1990, WRR 26(3), 479-489, doi:10.1029/WR026i003p00479; Dershowitz & Fidelibus 1999, WRR (BEM pipe analogues) [U: DOI]. Both are non-reactive.
- **Kang et al.**: Kang co-authors the only graph-reactive DFN papers (Hyman 2026; Szawełło 2024/2026) and the inertia-at-intersections precipitation work (Yang 2024 PNAS). We found no stand-alone Kang graph-reactive model [U].
- **Sherman / Karra / Viswanathan / Srinivasan:** all their graph work we found is non-reactive. Reactive LANL work has used meshed DFN (PFLOTRAN) plus ML, apart from the Hyman-Szymczak graph solver.
- **Our position (inference):** BiGraFV is a fracture-node finite-volume graph inside PFLOTRAN with full multicomponent chemistry and a meshed-DFN cross-check (mc4hd / delg). Within our search, it is the only graph model that (a) runs coupled dissolution-precipitation and (b) has been validated against meshed reactive DFN runs. Doolaeghe 2020 gives an independent reason why the one-cell fracture graph under-predicts local flows, and the multiport correction exists for that reason.

---

## Gaps and ideas for this study

1. **Locate the Da at which emergence takes over from inheritance.**
   - Hyman 2026 predicts that low Da (uniform regime) recruits off-backbone fractures, while high Da locks onto a few inherited paths.
   - We report 96-99 % inheritance at high Da.
   - Test: run a Da_f sweep down to about 1 on one km network and plot the "recruit fraction" (channel fractures outside the initial 90 % flow set) against Da_f.
   - Prediction: the recruit fraction rises as Da falls, but never reaches the single-fracture "emergent" limit (Upadhyay 2015), because path-length heterogeneity persists.
2. **Report the flow focusing profile along x** (Szawełło 2024 GRL / IJRMMS 2026) for gyponly vs gypcal.
   - This puts our regime on their scale: a front propagating from the inlet means wormholing; uniform enlargement of inherited paths means channeling.
   - At 1000 m with high Da we expect wormholing. If the profile instead looks like channeling, that is a reportable departure attributable to the power-law size distribution.
3. **Report a backbone fraction comparable with Hyman 2026**: surface-area share of the top-100-paths backbone vs τ = dissolved volume / initial volume, next to our 90 %-flow set.
   - Their graph starts at about 21 % and falls by τ = 0.5. Our km networks should start lower (sparser, lower P32; Hyman 2020) [hypothesis].
   - Use τ alongside PV, because their regimes are indexed by τ, not by time.
4. **Treat Γ as the control on achievable permeability contrast in the gypsum -> calcite runs.**
   - Γ = ν_cal/ν_gyp = 0.49 (Budek et al. 2026; Budek & Szymczak 2025). Our "calcite replacement halves the contrast" may just be (1 - Γ) ≈ 0.5 [hypothesis].
   - Test: change the calcite molar volume in the PFLOTRAN database (Γ = 0.25, 0.5, 0.75, 1.0, 1.2) on one network and check whether the channel permeability contrast scales with 1 - Γ. Also check whether network-scale clogging appears only for Γ ≥ 1, as Budek's regimes predict.
   - The input-file-only constraint holds, since this changes the database / deck only.
5. **Place the runs on a Da-Fo regime map.**
   - Budek 2026 EPSL regimes: passivation / side branching / uniform replacement. Budek et al. 2026 Géotech. Lett.: an "exploratory" self-block-and-reroute mode.
   - Measure the fraction of precipitated calcite in off-backbone side and dead-end fractures against Fo_net.
   - Prediction: the side-branching / dead-end share peaks at intermediate Fo, which would match the observation that the DFN cements dead ends.
   - Count reroute events (a channel fracture's flow drops by more than 50 % while a neighbour gains) to detect the exploratory mode at km scale.
6. **Split the transmissivity heterogeneity that survives the reaction.**
   - Separate log-T variance (which dissolution can erase) from path-length / tortuosity variance (which it cannot; Hyman 2026, Szawełło 2026) using particle-path length PDFs and tortuosity before and after.
   - Prediction: the T variance drops, but the tortuosity PDF of the flux-weighted particles keeps its spread except under wormholing.
7. **Use fracture-length-aware Da.**
   - Li et al. 2026 GRL and Starchenko & Ladd: pattern thresholds depend on fracture length.
   - With power-law fracture sizes at 1 km, test whether channel membership is better predicted by a per-fracture Da (k L_f / q_f, or Li's length-explicit group) than by a global Da. Use AUC, in the same way as the Track J clog GBT.
   - A cheap check of the "optimal injection rate scales linearly with length" claim: run 0.1, 1 and 10 PV/yr and see whether channel strength peaks at intermediate rates.
8. **Graph-type bias and intersection processes.**
   - Doolaeghe 2020 predicts that one-cell fracture graphs under-predict local flow, most strongly in fractures with many intersections. Test whether one-cell vs mc4hd error in channel membership correlates with node degree.
   - Steefel & Hu 2022, Yang 2024 PNAS and Bochet 2020 all put precipitation hotspots at intersections, consistent with our DFN intersection-throat seal (Track D). Report seals as intersection events and test whether they sit where flows of contrasting carbonate / Ca ratio converge.
9. **Transport observables comparable with Hyman 2024/2026**: particle BTC, tail exponent γ, longitudinal dispersivity (t16 / t84 formula), and effective aperture b_eff = 2τ/β, all at matched τ.
   - Prediction: gyponly narrows the BTC and lowers D_L (channeling/wormholing). Gypcal keeps a broader BTC, because Γ < 1 limits the permeability contrast.
   - Our lit note hyman_transport_metrics.md already gives the formulas.
10. **Field check against Forsmark calcite.**
    - Sandström & Tullborg and Drake & Tullborg report calcite concentrated in open, water-conducting fractures.
    - Test whether the simulated calcite-in-channel fraction under gypcal matches the logged association between calcite-coated fractures and flowing (PFL) fractures in FFM01 [U: whether SKB Sicada boremap/PFL data are accessible].
    - This would be the first network-scale reactive result checked against site mineralogy. Klimchouk's hypogene gypsum mazes are the natural opposite case (uniform network enlargement) to cite when discussing the high-Da channel picture.

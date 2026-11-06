# Literature: how deep does reactive flow channelization get, and what sets it (physics vs numerics)

Search of 5 Nov 2026. This note is about the **depth** of channelization: how far the flow-focusing measure falls below its starting
value. It does not repeat the three existing notes in this folder:
- `lit_wormhole_regime.md`: the regime map (compact / wormhole / uniform), Pe and Da definitions, the Da -> infinity limit.
- `lit_large_dfn_reactive.md`: inheritance vs emergence, graph models, precipitation, Forsmark mineralogy.
- `hyman_transport_metrics.md`: the d_Q formula, BTC, tortuosity and dispersivity.

Where a paper is already summarised in those notes, only the new, depth-relevant point is given here.

How each entry was checked:
- **[full]**: full text read for this note (PDF converted to text, quotes or paraphrases checked against the text).
- **[abs]**: only the abstract or bibliographic record.
- **[sec]**: the number comes from a citing source, not from the original.
- **UNVERIFIED**: not confirmed.

All DOIs below were resolved on Crossref on 5 Nov 2026 (title, authors, journal, volume and pages matched) unless marked otherwise.
Text extracts are in the scratchpad: `.../scratchpad/chd/*.txt`, `.../scratchpad/ref/*.txt` and `.../scratchpad/pdfs/*.txt`.

**Correction to an existing note.** `lit_large_dfn_reactive.md` gives Hanna & Rajaram 1998 as "DOI 10.1029/98WR01863 [U]". That DOI resolves
to Rutqvist et al. 1998 (fracture storativity). The correct DOI is **10.1029/98WR01528** (WRR 34(11), 2843-2853; Crossref-checked).

---

## 0. Our metric in literature terms

- PR_V = (ΣQ)^2 / Σ(Q^2/w) is a participation ratio. It belongs to the same family as Maillot et al. 2016's flow channeling density d_Q
  (built on Davy et al. 1995/2010 and Bell & Dean 1970). Maillot weights each fracture by surface area S_f; we weight by fracture-volume share w.
- Hyman 2020, Hyman et al. 2024 and Hyman et al. 2026 report **d_Q/P32**, "the percentage of the total surface area where there is significant flow".
- Our "depth" is the ratio min_t PR_V(t) / PR_V(0). The closest published equivalent is (d_Q/P32 dissolved) / (d_Q/P32 unreacted).

---

## 1. What controls the intensity of reactive channelization

| Control | Effect on depth | Key evidence |
|---|---|---|
| **Permeability contrast K1/K0 (ceiling) and the k–φ law** | First-order. Without a contrast there is no instability. A bounded contrast caps the growth rate. Effective exponents measured where channels form are 6-19, far above n = 1. | Szymczak & Ladd 2014; Hinch & Bhatt 1990; Aharonov et al. 1995; Menke et al. 2023; Hao et al. 2013 |
| Da (reaction vs advection) | Sets the regime. Above Da ~ 1 the pattern stops depending on Da. | SL09 (see `lit_wormhole_regime.md` §4); Hyman et al. 2026; Roded et al. 2020 |
| G (diffusive limitation) | Higher G spreads dissolution and gives larger d_Q, i.e. shallower channels. | Hyman et al. 2026; Roded et al. 2020 |
| Pe | Inside one fracture, higher Pe gives more uniform dissolution. | Detwiler et al. 2003; SL09 (existing notes) |
| Transmissivity variance σ | Weak effect on network flow structure. Inside a fissure, aperture variability shortens breakthrough. | Maillot et al. 2016; Hanna & Rajaram 1998 |
| Density P32, connectivity, network type | Network type (kinematic vs Poisson) changes d_Q by ×1.5-3. Density effects are non-monotonic in the connected network. | Maillot et al. 2016; Hyman 2020; Sherman et al. 2020 |
| Boundary condition (fixed Q vs fixed ΔP) | Modest within a fracture. Fixed head drives runaway breakthrough in karst. Fixed Q makes flow allocation zero-sum. | SL09; Starchenko & Ladd 2018; Dreybrodt 1996; Gabrovšek & Dreybrodt 2001 |
| Mechanical feedback (compaction) | Strongly deepens channels by lowering k between them. | Spiegelman, Kelemen & Aharonov 2001 |

### 1.1 Permeability contrast and the k–φ law

**Szymczak & Ladd 2014**, "Reactive-infiltration instabilities in rocks. Part 2. Dissolution of a porous matrix", J. Fluid Mech. 738, 591-630,
doi:10.1017/jfm.2013.586 (Crossref year 2013, online Dec 2013) [full].
- §4.1: the zeroth-order growth rate is always negative "because a permeability contrast between the dissolved and undissolved material is
  needed to drive the instability".
- §5, Eq. 5.1-5.2 (thin-front limit, after Chadam et al. 1986): the permeability contrast is defined as Γ = K0/K1. The long-wavelength growth
  rate has slope (1 − Γ)/(1 + Γ).
- §5, p. 20: with significant dispersion, short-wavelength modes are unstable only "whenever there is significant permeability contrast Γ < 0.2".
  They note that cemented sandstone gives 0.01 < Γ < 0.1.
- §6, p. 25: "When the permeability contrast is bounded ... the growth rate tends to a constant value at large û." By contrast, a diverging
  permeability law gives a logarithmically increasing growth rate.
- For us: our n = 1 ceiling gives Γ = 0.1. The front is therefore still linearly unstable; the long-wave slope is 0.82 of the unbounded value.
  Linear theory does not say how deep the nonlinear channels get, but it does make the contrast the controlling parameter.

**Hinch & Bhatt 1990**, "Stability of an acid front moving through porous rock", J. Fluid Mech. 212, 279-288,
doi:10.1017/S0022112090001963 [abs; result as summarised by SL14 §4.1 and §6]. This is the original convective analysis. With finite
permeability, the growth rate saturates at short wavelengths.

**Aharonov, Whitehead, Kelemen & Spiegelman 1995**, "Channeling instability of upwelling melt in the mantle", JGR 100(B10), 20433-20450,
doi:10.1029/95JB01307 [full, text extraction partly garbled].
- As Da → ∞ the growth rate of the fastest mode approaches a constant "determined by ∂k/∂φ ∝ n, the derivative of the permeability with
  respect to porosity".
- For us: at high Da the instability growth rate scales with the k–φ exponent n. With n = 1 it is 1/3 of the n = 3 value.

**Spiegelman, Kelemen & Aharonov 2001**, "Causes and consequences of flow organization during melt transport: The reaction infiltration instability
in compactible media", JGR 106(B2), 2061-2077, doi:10.1029/2000JB900240 [full].
- Abstract: dissolution can localize flow "such that > 90% of the melt flux is channelized in < 20% of the available area".
- Reference run: "94% of the vertical flux is going through only 24% of the available area".
- The maximum porosity in the channels is only 3.9 times the original. Localization is strong because compaction reduced the porosity between
  channels to 0.1 of the original. The flux contrast between channels and the interchannel region therefore reaches a factor of 1500.
- They state that compaction "enhances the localization caused by this instability compared to rigid media".
- For us: a modest porosity gain gives extreme channels only when the bypass is also made *less* permeable. A rigid matrix with a 3.9× porosity
  gain does not reach this.

**Menke, Maes & Geiger 2023**, "Channeling is a distinct class of dissolution in complex porous media", Sci. Rep. 13, 11312,
doi:10.1038/s41598-023-37725-6 [full, arXiv 2211.03356v2].
- Pore-scale 2D simulations. Channeling occurs where pore-throat sizes give orders-of-magnitude differences in flow between pathways; existing
  fast paths are widened.
- Power-law fits of the emergent k–φ relation by regime:

  | Regime | Exponent of the emergent k–φ fit |
  |---|---|
  | compact | 1.5-2 |
  | wormhole | 11, and up to 19 |
  | channeling | 6-12 |
  | uniform | 5-6 |

- 3D experiments quoted in the paper give 7-11 for channeling and 5 for uniform.
- For us: when focusing happens below the grid scale, the cell-level k–φ exponent is far above 1. Our n = 1 per-fracture law is closest to the
  "compact" fit.

**Hao, Smith, Sholokhova & Carroll 2013**, "CO2-induced dissolution of low permeability carbonates. Part II: Numerical modeling of experiments",
Adv. Water Resour. 62, 388-408, doi:10.1016/j.advwatres.2013.09.009 [abs]. To match the core floods, more heterogeneous cores needed larger
k–φ exponents (n = 6-8).

### 1.2 Da and G (beyond the existing regime notes)

**Hyman, Szawełło, Kang & Szymczak 2026**, JGR Solid Earth 131, e2025JB033004, doi:10.1029/2025JB033004 [full].
- d_Q/P32 starts at about 37 %. It "increases slightly" at Da = 2e-4 (mild homogenization) and decreases at Da = 2e-3.
- At Da = 2e-2 the decrease "is rapid up to the wormhole breakthrough at τ ≈ 0.5, after which the rate of channelization diminishes".
- "Higher G consistently yields larger d_Q".
- Final d_Q values are only in Fig. 10, which was not read numerically (UNVERIFIED).
- Their flow is "a single pump connected to all inlet nodes" at fixed total Q. This is the same as our inlet manifold (`add_inlet_manifold.py`).

**Roded, Aharonov, Holtzman & Szymczak 2020**, "Reactive Flow and Homogenization in Anisotropic Media", WRR 56, e2020WR027518,
doi:10.1029/2020WR027518 [abs].
- At low Da, uniform dissolution "extensively homogenizes" the flow field.
- Transport-controlled surface reaction strengthens the homogenization.

**Our own rate test** (`phase1/phase3_rate.csv`; P32 6, σ 1, seeds 1-3): injection rate ×0.1 and ×10 change the median depth by ≤ 0.004 and
inheritance by 0.000. This matches the SL09 statement that patterns do not change between Da = 1, 10 and ∞ (outside the very-low-Pe corner).
At Da_f ≫ 1, Da does not set our depth.

### 1.3 Network heterogeneity and density

**Maillot, Davy, Le Goc, Darcel & de Dreuzy 2016**, "Connectivity, permeability, and channeling in randomly distributed and kinematically defined
discrete fracture network models", WRR 52, 8526-8545, doi:10.1002/2016WR018973 [full].
- §4.4: d_Q of kinematic DFNs is "smaller by a factor of 1.5–3 than of Poisson", i.e. more channeled.
- d_Q increases linearly with the percolation parameter, so channeling is maximal at the percolation threshold.
- §5, with lognormal fracture transmissivity σ = 0-2: "the flow structure is quite insensitive to the transmissivity variability". Structural
  (model-type) effects "remain much larger than those of increasing the variability of transmissivity".
- Our σ = 0/0.5/1 ensembles show no σ effect on depth either (below). This is consistent.

**Hyman 2020**, "Flow Channeling in Fracture Networks: Characterizing the Effect of Density on Preferential Flow Path Formation", WRR 56,
e2020WR027986, doi:10.1029/2020WR027986 [full, accepted manuscript]. Non-reactive.
- Within the connected network, d_q/P32 is "over 60%" in the sparsest networks (p' = 2), "around 40%" at p' = 3 and 5, and flow is "fairly
  uniform" at p' = 10.
- The particle participation (fraction of fractures carrying significant transport) falls from about 25 % (p' = 2) to about 10 % (p' = 10).
- Sparse networks are "structurally constrained" and have few alternatives. In dense networks, connectivity, geometry and hydraulics jointly pick
  the channels.

**Hanna & Rajaram 1998**, "Influence of aperture variability on dissolutional growth of fissures in karst formations", WRR 34(11), 2843-2853,
doi:10.1029/98WR01528 [abs, Crossref abstract].
- Breakthrough time falls by about ×2 at aperture coefficient of variation 0.1, and by about an order of magnitude at 2.0. The mechanism is
  "focusing of flow into preferential flow channels which are enlarged at a faster rate".
- The effect is "more pronounced in rapidly dissolving rock".
- Secondary summaries add that this partly explains rapid conduit growth in gypsum, which one-dimensional models say should not happen [sec].

### 1.4 Fixed flow rate vs fixed pressure drop

**Szymczak & Ladd 2009**, "Wormhole formation in dissolving fractures", JGR 114, B06203, doi:10.1029/2008JB006122 [full, arXiv 0902.1374].
- Constant pressure drop is "representative of the early stages of karstification"; constant flow rate is relevant to reservoir stimulation.
- Under constant ΔP the phase-diagram point "moves towards larger Pe and smaller Da values as the dissolution progresses".
- Under constant Q, "the Péclet number remains constant".
- "While the differences are not dramatic, channels formed in constant pressure drop simulations are noticeably more diffuse at their tips."
- "The Damköhler number decreases in the course of constant pressure drop simulations while it increases during constant flow rate runs."
- This agrees with experiments in which constant-ΔP wormholes branch more.

**Starchenko & Ladd 2018**, WRR 54, 7946-7959, doi:10.1029/2018WR022948 [full, accepted manuscript]. "At constant pressure drop an elliptical
cross section can develop at the outlet because of the increasing flow rate once breakthrough has occurred."

**Karst (constant head).**
- Dreybrodt 1996, "Principles of early development of karst conduits under natural and man-made conditions revealed by mathematical analysis of
  numerical models", WRR 32, 2923-2935, doi:10.1029/96WR01332 [abs].
- Gabrovšek & Dreybrodt 2001, J. Hydrol. 240, 206-224, doi:10.1016/S0022-1694(00)00323-1 [abs and secondary summaries].
- Under constant head, positive feedback ends in breakthrough, "an explosive increase of the flow ... until constant head conditions break down".
  After that, recharge (fixed flux) controls further growth.

**Palmer 1991**, "Origin and morphology of limestone caves", GSA Bull. 103, 1-21, doi:10.1130/0016-7606(1991)103<0001:OAMOLC>2.3.CO;2 [abs].
- Passages on the route of greatest discharge grow fastest.
- Maze caves (network-wide enlargement, i.e. shallow channelization) form where steep gradients let many paths grow at similar rates, or where
  discharge is spread evenly across many routes.

**Our reading (derivation, not from the literature).**
- For purely parallel paths the flow share s_i = C_i / ΣC is the same under fixed Q and fixed ΔP. The boundary condition matters through:
  - the drift of Pe and Da (above);
  - shared series resistance at inlet and outlet;
  - runaway total flow under fixed ΔP.
- If every path is reagent-limited (all reagent consumed, dissolution rate ∝ flow), dC_i/dt ∝ C_i under both conditions. Conductance ratios then
  do not change at all. Depth must come from front propagation through series fractures and from saturation at the ceiling, not from the
  boundary condition.
- Literature conclusion: within a fracture the boundary-condition effect is "not dramatic" (SL09). Fixed head matters for karst-style runaway.
  Fixed rate (ours, Hyman 2024, Hyman 2026) is the conservative, zero-sum case.

---

## 2. How much does flow focus? Reported magnitudes

**Field: crystalline rock**

| Site / study | What was measured | Magnitude | Check |
|---|---|---|---|
| Stripa, 360 m (Abelin et al. 1985, quoted in Abelin et al. 1991b) | fraction of fracture width carrying > 90 % of flow in three visible fractures | 5-20 % | [sec] |
| Stripa drift, 375 sheets: Abelin, Birgersson, Moreno, Widén, Ågren & Neretnieks 1991, WRR 27(12), 3119-3135, doi:10.1029/91WR01404 | sheets carrying more than half of each tracer | 3-5 of 27-52 sheets; "very unevenly distributed", "large parts of the drift were dry" | [full] |
| Swedish deep holes (Carlsson et al. 1983, quoted by Abelin 1991b) | spacing of conducting fractures below a few hundred m | about 1 per 5-10 m | [sec] |
| Forsmark, SKB TR-10-52 (2010), SR-Site data report §6.6.8, Fig. 6-64 | Terzaghi-corrected open-fracture vs PFL flowing-fracture frequency | see note below | [full] |
| Forsmark, Follin et al. 2014, Hydrogeol. J. 22, 313-331, doi:10.1007/s10040-013-1080-2 | hydro-DFN of sparsely fractured rock: P32,open ≥ P32,connected-open ≥ P32,PFL | flowing fractures are a small subset of open fractures | [abs]; ratio from TR-10-52 |

Note on the TR-10-52 Forsmark figures:
- Fig. 6-64 labels open-fracture frequencies of 260-1470 /km and PFL frequencies of 2-36 /km.
- The text says the PFL frequency below −400 m is "approximately 0.036 fractures per metre (36/km)".
- The figure labels and the text disagree on which depth the 36/km applies to (UNVERIFIED which is right).
- Either way, **about 1-3 % of open fractures flow** (36/1470, 5/615, 2/260).
- The same report says "The rock at Forsmark is dominated by sealed fractures; open fractures are only a small part of the total number."

**Reviews and concepts (not used for numbers):**
- Tsang & Neretnieks 1998, "Flow channeling in heterogeneous fractured rocks", Rev. Geophys. 36, 275-298, doi:10.1029/97RG03319
  [bibliographic only]. The standard review of the channel concept.
- Black, Woodman & Barker 2017, Hydrogeol. J. 25, 445-463, doi:10.1007/s10040-016-1511-y [abs]. Sparse long-channel networks percolate at
  lower density; fitted to Stripa inflows.
- Olkiluoto flowing/open ratio: not found (UNVERIFIED).

**DFN models, non-reactive (initial-state channelization):**
- Maillot 2016: d_Q is 1.5-3× lower in kinematic than in Poisson DFNs.
- Hyman 2020: d_q/P32 of the connected network is 40-60 %; 10-25 % of fractures carry significant transport.

**DFN models, reactive (change caused by dissolution):**
- **Hyman, Navarre-Sitchler, Sweeney, Pachalieva, Carey & Viswanathan 2024**, G-cubed 25, e2024GC011550, doi:10.1029/2024GC011550 [full].
  - Table 1: E[d_Q/P32] falls from **55.63 % (unreacted) to 28.10 % (dissolved)**, a ratio of **0.505**. Mean k_eff rises from 3.25e-15 to
    2.16e-13 m^2 (×66).
  - Setup: 30 DFNs, mono-disperse r = 2 m, uniform initial aperture and permeability. φ0 = 0.01 (quartz-filled), so the porosity can grow up to
    ×100. Fixed rate of one network volume per year. Final quasi-steady state after 5 Myr.
  - The k–φ exponent a in their Eq. 7 is not given in the extracted text (UNVERIFIED).
  - This is the closest published analogue to our depth. It is a final state, not a minimum over time.
- Hyman et al. 2026 (graph): starts at 37 %; the change by Da is reported qualitatively only (§1.2).

**Natural reactive systems (for scale):**
- Spiegelman et al. 2001: > 90 % of flux in < 20 % of area, at a channel/inter-channel flux contrast of about 1500.
- **Ague 2005**, Goldschmidt Conf. Abstr. A660, "Channelization of subduction zone fluids during devolatilization" [full abstract; conference
  abstract, not peer reviewed]. Putting > 90 % of the flux in about 10 vol % of conduits "requires that conduits be ~100 times more permeable
  than the surrounding rocks".
- **Ague 2011**, "Extreme channelization of fluid and the problem of element mobility during Barrovian metamorphism", Am. Mineral. 96, 333-352,
  doi:10.2138/am.2011.3582 [abs + first page; DOI from the PDF header, not Crossref-checked]. Vein conduits carry the bulk of the flow; fluxes
  vary over < 1 m from veins.
- Karst conduits carry > 94 % of groundwater flux while holding the smallest porosity. Source: Worthington, Ford & Beddows 2000, in Klimchouk et
  al. (eds) *Speleogenesis* [sec, via NRC ML12192A418; original not read; UNVERIFIED].

**Check (our arithmetic).** For a parallel bundle of equal-volume paths, a fraction f of paths with conductance ×M carries
M f / (M f + 1 − f) of the flow.
- M = 100, f = 0.1 gives 0.917. This reproduces Ague's "~100× ⇒ > 90 % in 10 %".
- M = 10 (our ceiling), f = 0.1 gives at most 0.53.
- So natural channelization of the "> 90 % in 10 %" kind needs contrasts of ≥ 10^2. Karst (cubic law on mm-to-m apertures) and compacting
  mantle have contrasts far above that.

---

## 3. Does a permeability ceiling limit channel depth? Re-homogenization after breakthrough

**Literature:**
- Linear theory says yes (SL14 Γ; Hinch & Bhatt 1990; Aharonov 1995, growth ∝ n).
- **We found no published study that varies k_max/k0 and reports the resulting nonlinear channel depth, or that shows re-homogenization caused
  by a finite contrast.** Published reactive DFN/graph studies use an unbounded or large gain:
  - Hyman 2026: cubic law, apertures grow without bound.
  - Hyman 2024: porosity up to ×100.
- Related statements:
  - Hyman 2026: after breakthrough "further channelization ceases".
  - Szawełło, Hyman, Kang & Szymczak 2026, "Structural barriers to complete homogenization and wormholing in dissolving porous and fractured rocks",
    IJRMMS 200, 106431, doi:10.1016/j.ijrmms.2026.106431 (already summarised in `lit_large_dfn_reactive.md`): topology prevents complete
    homogenization.
  - **Szymczak & Ladd 2011**, "The initial stages of cave formation: Beyond the one-dimensional paradigm", EPSL 301, 424-432,
    doi:10.1016/j.epsl.2010.10.026 [full, arXiv 1011.4111]. A *geometric* cap: once a single channel remains, "the flow focusing mechanism
    stalls"; "there is a maximum flow rate that a single channel can acquire by flow focusing, q_max ∼ q0 W/w".

**Analytic bound (our derivation; the inequality is the Kantorovich / Pólya–Szegő inequality).**
- Take N equal-volume parallel paths with equal initial flow. Multiply their conductances by m_i ∈ [1, M].
- Then PR/PR0 = (Σm)^2 / (N Σm^2) ≥ **4M/(1+M)^2**. Equality holds when a fraction 1/(1+M) of the paths is fully opened and the rest untouched.
- A uniform ceiling also forces depth to be **transient**. If every fracture eventually reaches M k0, all conductances scale by the same factor
  and PR returns to PR0. The deepest state is reached when the channel set is saturated and the bypass is not.

| Ceiling M | Bundle bound 4M/(1+M)^2 | Observed median depth (project CSVs) | Share of the maximum reduction realized, (1 − d)/(1 − bound) |
|---|---|---|---|
| ×3.3 (coupled, φ0 0.182) | 0.714 | 0.882 (`phase1/phase3_ceiling.csv`, 9 networks) | 0.41 |
| ×5.5 (gypsum φ0 0.182 / coupled φ0 0.1) | 0.521 | 0.777 / 0.794 (phase3_ceiling); 0.782 (coupled phase1, n = 60) | 0.43-0.47 |
| ×10 (gypsum φ0 0.1) | 0.331 | 0.655 (phase1, n = 60; range 0.47-0.80); coupled ×10 / ×10.6: 0.684 / 0.668 | 0.47-0.52 |
| ×20 (gypsum φ0 0.05) | 0.181 | 0.527 (n = 12) | 0.58 |
| ×82 (slot cubic law, see `aperture-realism-kphi`) | 0.048 | not run | extrapolation only |

Observed values are from `phase1/depth_variability.csv`. Reading the table:
- At a fixed ceiling, depth does not depend on chemistry: gypsum ×5.5 gives 0.777, coupled ×5.5 gives 0.794; coupled at ×10 gives 0.67-0.68
  against gypsum 0.655.
- Every ceiling series reaches about 40-60 % of the ideal bundle's maximum reduction.
- Within the ×10 gypsum ensemble, the median depth is 0.62-0.68 at every P32 (4-16) and σ (0-1). There is no monotonic density or σ trend in
  this CSV.
- Note: the brief's "median 0.4-0.6" is lower than these CSV medians (0.655 at ×10). Check which depth definition or run set the brief used.

---

## 4. Numerical issues and the direction of their bias

1. **One cell per fracture removes in-fracture fronts and wormholes. This biases channels shallower and later.**
   - SL2011 EPSL §2.4 [full]: in a 20 m × 10 m fracture, 1D models give breakthrough at 2800 y (linear kinetics) or 270 y (nonlinear). The 2D
     model gives < 30 y "regardless of the kinetics".
   - SL2011 §4: in DFN models "each fracture within the network is modeled at the one-dimensional level, and the possibility of spatially localized
     dissolution within an individual fracture ... is not taken into account". The instability "can reduce the breakthrough time in an individual
     fracture by orders of magnitude".
   - Appendix C: "fracture dissolution is always two-dimensional, and cannot be usefully approximated by one-dimensional models". Our model is 0D
     per fracture, which is coarser still.
   - Hanna & Rajaram 1998 (above) make the same point for gypsum.
   - Project evidence (memory `tpl-dfn-validation-findings`, `dense-network-sweep-findings`; not re-checked here):
     - The meshed DFN opens channels inside fracture planes (in-fracture participation 0.26-0.31) and channelizes earlier in dissolved fraction
       at n = 3.
     - On the dense TPL seeds the DFN plateau channel strength is 0.79/0.84 against the one-cell graph's 0.94/0.875.
     - On seed 4229 the graph was stronger, so the sign is not universal.
2. **The cell-level k–φ law (closure bias, shallower).**
   - With sub-cell focusing the effective exponent is 6-19 (Menke 2023), against n = 1 in the lumped cell.
   - Cooper, Sharma, Magni, Blach, Radlinski, Drabik, Tengattini & Szymczak 2023, Adv. Water Resour. 175, 104407,
     doi:10.1016/j.advwatres.2023.104407 [abs]: core permeability changed only when the wormhole tip crossed highly cemented barriers. Permeability
     is a series (bottleneck) property, while a lumped porosity-averaged law is an arithmetic average.
3. **Upscaling validity.**
   - Ladd & Szymczak 2021, Annu. Rev. Chem. Biomol. Eng. 12, 543-571, doi:10.1146/annurev-chembioeng-092920-102703 [full], §3.1: homogenization
     requires Da_II < 1 and Da_II < εPe (after Battiato & Tartakovsky 2011, J. Contam. Hydrol. 120-121, 18-26, doi:10.1016/j.jconhyd.2010.05.005).
   - "CaCO3 and CaSO4 under neutral conditions (k ≈ 10^-6 – 10^-5 m s^-1)": the condition "cannot be satisfied for any length scale L > 1 mm".
   - A single gypsum control volume per 10-300 m fracture is therefore formally outside the homogenizable regime. This supports item 1; it does
     not invalidate network-scale mass balance.
4. **Mixing rule at intersections.**
   - Complete mixing (ours, Hyman 2026) vs streamline routing changes non-reactive transport: Kang, Dentz, Le Borgne & Juanes 2015, "Anomalous
     transport on regular fracture networks: Impact of conductivity heterogeneity and mixing at fracture intersections", PRE 92, 022148,
     doi:10.1103/PhysRevE.92.022148 [abs].
   - No reactive study found. Our expectation (inference): streamline routing would keep undersaturated water on the fastest paths, so complete
     mixing slightly under-focuses.
5. **Grid resolution in continuum models.**
   - Converged wormhole simulations need several cells across a wormhole. Starchenko & Ladd 2018 used 260 × 300 × 8 cells per lab fracture,
     "sufficient for resolution-independent dissolution".
   - Golfier et al. 2002, J. Fluid Mech. 457, 213-254, doi:10.1017/S0022112002007735 [abs]: the Darcy-scale two-scale model.
   - We found no paper that quantifies how much coarse grids reduce channel depth. Numerical dispersion smearing the front toward uniform is the
     generic expectation (inference, UNVERIFIED).
6. **Time step (inference; no literature found).**
   - Explicit porosity/permeability updates lag the flow field by one step. A step that is long compared with the time for a fracture to change k
     delays the positive feedback, which would make channels slightly shallower.
   - The project's mass-balance criterion (dt ≤ 0.57 τ) was set for mass, not for channel depth.
7. **Resolved vs lumped reactive network comparisons in the literature.**
   - None found apart from non-reactive graph-vs-DFN studies (Karra et al. 2018; Doolaeghe et al. 2020; see `lit_large_dfn_reactive.md` §5).
   - Hyman 2026 lists upscaling from fracture to field scale as future work.

---

## 5. Natural systems: is channelization in nature stronger than in modest-gain models?

- **Yes, much stronger in absolute terms, because the contrasts are much larger.**
  - Karst: transmissivity grows ∝ b^3 from about 0.1 mm to metres. Conduits carry > 94 % of flux [sec].
  - Gypsum conduits grow quickly in 2D, unlike in 1D models (Hanna & Rajaram 1998).
  - Mantle dunite channels: Kelemen, Shimizu & Salters 1995, Nature 375, 747-753, doi:10.1038/375747a0 [abs]. Replacive dunites were conduits
    for focused melt flow. The fraction of the mantle section that is dunite was not checked (UNVERIFIED). Models: > 90 % of flux in < 20 % of the
    area, but only with compaction (Spiegelman 2001).
  - Metamorphic veins: > 90 % of flux in about 10 % of the volume with a ×100 contrast (Ague 2005, 2011).
- **Counter-examples where channelization is weak.**
  - Maze caves (Palmer 1991): discharge spread evenly or steep gradients.
  - Hypogene gypsum mazes (Klimchouk, in `lit_large_dfn_reactive.md`).
  - Low-Da / high-G homogenization (Roded 2020; Hyman 2026).
- **Repository sites.** At Forsmark only about 1-3 % of open fractures flow (TR-10-52), and most fractures are sealed. Stripa: 5-20 % of
  fracture width carries > 90 % of flow. This channelization is *structural and inherited* (mineral sealing, size–transmissivity correlation).
  Our metric is normalized by the initial state, so it measures only the *extra* focusing that dissolution adds on top of an already channelized
  field.
- **Natural evidence on the k–φ question.** In the natural cases that reach "> 90 % in < 20 %", the reactive or mechanical process changes
  conductance by ≥ 10^2 (Ague; Spiegelman's ×1500 flux contrast; karst). No natural case was found where a ×10 permeability gain alone produced
  extreme focusing.

---

## 6. Verdict

**What is physical**
- That the channels are inherited is expected for networks whose initial flow already spans orders of magnitude:
  - Menke et al. 2023's "channeling" regime;
  - Hyman et al. 2026: "initial fracture heterogeneity persists";
  - Pachalieva et al. 2025 and Upadhyay et al. 2015 in the existing notes.
- That depth is insensitive to Da at Da_f ≫ 1 is physical: SL09, and our rate test (Δ ≤ 0.004).
- That depth is insensitive to σ is consistent with Maillot et al. 2016.

**What is set by the chosen k law and ceiling (the dominant control)**
- Theory makes the permeability contrast the driver: SL14 Γ, Hinch & Bhatt 1990, Aharonov 1995 (growth ∝ n).
- Our own series shows depth tracking the ceiling and not the chemistry: 0.88 / 0.78 / 0.66 / 0.53 at ×3.3 / ×5.5 / ×10 / ×20. At every
  ceiling, about 40-60 % of the maximum participation-ratio reduction possible for an ideal parallel bundle (4M/(1+M)^2) is realized.
- A uniform ceiling also makes the channel transient by construction: when everything is dissolved, PR returns to its start.
- With n = 1 and φ0 = 0.1, a 10 % channel set can carry at most about 53 % of the flow. Natural "> 90 % in 10 %" focusing needs about ×100
  (Ague).

**What is numerical**
- One cell per fracture with n = 1 removes in-fracture localization. The literature consistently says this under-predicts focusing and delays
  breakthrough, by orders of magnitude for a single fracture (SL2011; Hanna & Rajaram 1998). The effective cell-level exponent under sub-cell
  focusing would be 6-19 (Menke 2023).
- On the project's own 1:1 tests, the meshed DFN channelizes earlier and, on dense networks, more strongly than the one-cell graph.
- The numerical bias is therefore toward *shallower and later* channels. On the test networks it was second-order next to the ceiling (n90
  within 1-2 fractures on TPL), but at 1 km it is unquantified.

**Bottom line.** The modest, inherited depth is a physically sensible outcome for a fixed-rate, high-Da, already-channelized fracture network.
Its *magnitude* is mainly a consequence of the ×10 ceiling of the n = 1 law, plus a smaller numerical bias toward shallowness from one-cell
lumping. It is not a numerical artifact in sign.

**What would make it deeper** (largest effect first):
1. **A higher ceiling or exponent.** Slot cubic law ×82: bound 0.048. Taking the observed 40-60 % realized fraction as a guide (extrapolation),
   depth would be about 0.43-0.62, and lower if the fraction keeps rising with M as it does from ×3.3 to ×20.
2. **Lowering bypass conductance**, the analogue of compaction (Spiegelman 2001). Examples: precipitation or sealing off the channel set rather
   than in it.
3. **Resolving in-fracture fronts and wormholes** (multi-cell or meshed DFN). This would let the effective per-fracture exponent exceed 1.
4. **Fixed head instead of fixed rate.** This permits runaway total flow (karst breakthrough), but the share-based PR_V changes little for parallel
   paths, and SL09 calls the within-fracture differences "not dramatic".

Lowering Da toward 1 or raising G would make channels *shallower* (homogenization). Raising σ would change little.

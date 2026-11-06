# Literature: staged channelization (decoupling, inheritance, focusing to breakthrough, re-spreading)

Searched 5 Nov 2026. Builds on `lit_large_dfn_reactive.md`, `lit_wormhole_regime.md` and `hyman_transport_metrics.md`, and does not repeat them.
Paraphrases only. Every quote is under 15 words.

Verification tags:
- **[read]**: full text or the relevant sections read. These were local extracts, arXiv/HTML pages, or open-access PDFs pulled into
  `scratchpad/stage_lit/` (the Dreybrodt et al. 2005 book, Perne 2014, Cooper 2023, Roded 2020, Budek & Szymczak 2012, Dzikowski & Szymczak 2026).
- **[abs]**: title, authors, venue and abstract confirmed online. Body not read.
- **[ref]**: bibliographic data taken from the reference list of a paper we read (Szawełło 2026, Hyman 2026 or Budek 2026). Content not checked by us.
- **[U]**: UNVERIFIED item, named in place.

Classes used below:
- **SAME** = reports the same multi-stage sequence.
- **PART** = reports one or more of our stages.
- **REL** = related mechanism or metric only.

## 0. Our result, restated for comparison

Forsmark FFM01 DFN, 1 km, one control volume per fracture, gypsum fill (φ0 = 0.1), fixed rate of 1 PV/yr. Time is measured as the
fraction f_d of the gypsum inventory dissolved.

| Stage | What happens | Where it sits on the f_d axis |
|---|---|---|
| 1 | Pore space opens near the inlet while flow is still spread out: PR_pore falls, PR_V holds | early |
| 2 | Front runs down the initially dominant paths (inheritance) | |
| 3 | Strongest focusing; front breaks through at the outlet | PR_V minimum at about 42 %; breakthrough at 56–63 % |
| 4 | Neighbouring paths open and flow spreads again | after breakthrough |

Two features stand out:
- The focusing peak comes **before** breakthrough.
- Our model has a **finite soluble inventory** per fracture, so k saturates once a fracture is empty. Most dissolution models in the
  literature have unlimited wall material instead.

---

## Q1. Has the full sequence been reported?

**Short answer: no single paper reports all four stages with a flow-participation metric. Every individual stage has precedent.**
The closest combined sequences are (a) karst network models (competition, then breakthrough, then integration of bypass conduits)
and (b) the DFN reaction-front staging of Andrews et al. 2023.

| Paper | System | Stages matched | Class |
|---|---|---|---|
| Perne, Covington & Gabrovšek 2014, HESS 18, 4617–4633, doi:10.5194/hess-18-4617-2014 **[read]** | 2D karst fracture grid, constant head | 2, 3, 4 (see below) | PART, closest to the full arc |
| Dreybrodt, Gabrovšek & Romanov 2005, *Processes of Speleogenesis: A Modeling Approach*, ZRC Publishing (Carsologica 4) **[read: Sec. 4.3, 4.11 and the Birk et al. 2003 example]** | 2D karst nets | 3 and 4 | PART |
| Andrews, Hyman, Sweeney, Karra, Moulton & Navarre-Sitchler 2023, WRR 59(2), e2022WR032121, doi:10.1029/2022WR032121 **[abs]** | Upscaled 3D DFN weathering | 2 and 4 in terms of where reaction happens; no flow-participation metric | PART |
| Hyman, Szawełło, Kang & Szymczak 2026, JGR Solid Earth 131(3), e2025JB033004, doi:10.1029/2025JB033004 **[read]** | 3D DFN graph, kinetic dissolution, unlimited wall material | 2 and 3; stage 4 explicitly not seen | PART (and contradicts stage 4) |
| Szawełło, Hyman, Kang & Szymczak 2026, "Structural barriers to complete homogenization and wormholing...", arXiv:2602.06279v2 **[read]**; IJRMMS 200, 106431, doi:10.1016/j.ijrmms.2026.106431 **[from our earlier note, not rechecked]** | Regular and disordered pore networks + DFN graph | 1 (inlet homogenization before path takeover), 2, 3, structural floor on homogenization | PART |
| Wang, Yang, Blunt & Bijeljic 2026, arXiv:2605.18223 (preprint) **[read HTML]** | 3D micro-continuum on micro-CT rocks | Rise then fall of flow heterogeneity (CV_v) | PART (for stage 3 to 4, but different mechanism) |
| Cooper et al. 2023, Adv. Water Resour. 175, 104407, doi:10.1016/j.advwatres.2023.104407 **[read abstract and body]** | 4D micro-CT core flood, limestone | 1-like decoupling of geometry growth from flow change | PART (experimental) |
| Dreybrodt & Gabrovšek 2019, HESS 23, 1995–2014, doi:10.5194/hess-23-1995-2019 **[read via page summary]** | 2D karst net | Even front, then competition, then breakthrough; losers stop afterwards | PART (contradicts stage 4) |
| Neyra et al. 2025, ACS Omega 10(45), 54086–54097, doi:10.1021/acsomega.5c05664 **[read]** | Indiana limestone core floods + micro-CT, low rate | Three-stage pre-breakthrough sequence (advance, stagnation with inlet widening and merging, renewed advance) | REL |

### Stage 1: pore volume grows before the flow field changes (decoupling)

**Experiments**
- **Cooper et al. 2023 [read].** 4D tomography shows long periods of steady wormhole advance with little change in pressure drop
  (permeability), interrupted by step-like jumps. The authors attribute the plateaus to cemented barriers. Geometry and dissolved volume
  grow while flow resistance does not. This is the closest experimental analogue of our PR_pore/PR_V decoupling, though the mechanism
  differs: barriers in their case, series resistance of still-filled downstream fractures in ours.

**Network and continuum models**
- **Classical acidizing [ref].** Fredd & Fogler 1998 (AIChE J 44(9), 1933–1949, doi:10.1002/aic.690440902) and Hoefner & Fogler 1988
  (AIChE J 34(1), 45–54, doi:10.1002/aic.690340107) define breakthrough as the moment the channel spans the core, with
  permeability rising sharply only then.
  - [U: the claim that permeability stays near its initial value until breakthrough is standard textbook wording; it was not checked in these two papers.]
- **Karst [read].** Before breakthrough, flow and widening rise slowly and then jump by orders of magnitude at breakthrough
  (Perne 2014, Sec. 1.1, citing Dreybrodt 1990, 1996).
  - Dreybrodt 1996, WRR 32(9), 2923–2935, doi:10.1029/96WR01332 [ref].
  - Siemers & Dreybrodt 1998, WRR 34(3), 409–419, doi:10.1029/97WR03218 [abs]: early flow is spread across all fractures before preferred paths draw flow.
- **Szawełło et al. 2026 [read].** In the disordered pore network at higher G, dissolution has time to smooth out inlet-region
  heterogeneity before one path takes over. The flow focusing profile shows significant homogenization near the inlet in the channeling
  regime. This is our stage 1 almost exactly: the inlet opens while flow focusing is not yet amplified.
- **Single fractures [read].**
  - Dreybrodt & Gabrovšek 2019: a homogeneous net first grows an even dissolution front; heterogeneous nets skip that stage.
  - Upadhyay, Szymczak & Ladd 2015 (JGR SE 120, 6102–6121, doi:10.1002/2015JB012233): uses a "homogenization scale" for the
    early smoothing of the initial aperture field.

**Opposite kind of decoupling (contrast).**
- Menke, Maes & Geiger 2023, Sci. Rep. 13, 11312, doi:10.1038/s41598-023-37725-6 **[read]**: their "channeling" regime gives a large
  permeability gain for a small porosity gain.
- Wang et al. 2026 **[read]**: channel emergence is a *simultaneous* reorganization of structure and flow.

So the sign of the porosity–flow decoupling depends on regime.

**No one we found computes a pore-volume-weighted versus volume-weighted participation pair (PR_pore vs PR_V) to show the decoupling.**
This diagnostic appears to be new.

### Stage 2: front runs down inherited paths

This stage is well documented (see `lit_large_dfn_reactive.md` §2).

**Additions from this search**
- **Andrews et al. 2023 [abs].** In a 10 m DFN, fronts first advance along main flow paths, then reach secondary paths and dead ends,
  then the matrix.
- **Szawełło 2026 [read].** In the channeling regime, pre-existing paths are amplified. In a DFN the flow is already strongly
  channelized (f50 ≈ 0.8) before any reaction.
- **Ma et al. 2026, arXiv:2609.01328 (preprint) [abs].** In micro-CT of oil-bearing Ketton, pre-existing preferential pathways were
  progressively amplified into one tortuous channel.

**Counterpoint**
- **Upadhyay et al. 2015.** Inside a single rough fracture the pattern is emergent rather than inherited.
- **Dreybrodt & Gabrovšek 2019.** In homogeneous nets the winner cannot be predicted.

### Stage 3: focusing grows until breakthrough

**Single fractures and pore networks**
- **Szymczak & Ladd 2009**, JGR 114, B06203, doi:10.1029/2008JB006122 **[read arXiv]**.
  - Channel competition is self-similar: spacing grows and the number of active channels falls.
  - Competition ends as soon as fingers break through.
  - Tip splitting already disrupts the hierarchy shortly before breakthrough.
- **Budek & Szymczak 2012**, PRE 86, 056318, doi:10.1103/PhysRevE.86.056318 **[read arXiv]**: same self-similar competition on
  pore networks, with a power-law distribution of wormhole lengths.
- **Szymczak & Ladd 2006**, GRL 33, doi:10.1029/2005GL025334 **[abs]**: resistor-network model of channel competition in fracture dissolution.

**Karst**
- **Hanna & Rajaram 1998**, WRR 34(11), 2843–2853, doi:**10.1029/98WR01528** **[abs]**.
  - Preferential channels progressively capture larger shares of the flow until breakthrough.
  - Breakthrough is faster with larger aperture variability.
  - Correction: our earlier note gave 98WR01863. The correct DOI is 10.1029/98WR01528.

**3D DFN graph (Hyman et al. 2026) [read]**
- d_Q/P32 falls fastest up to wormhole breakthrough at τ ≈ 0.5. After that, the rate of channelization slows.
- Backbone surface area and the tail exponent stabilize after τ = 0.5.

**Rise then fall of a heterogeneity metric (Wang et al. 2026, preprint) [read]**
- In Estaillades at Pe = 500, CV_v and the k–φ exponent n peak together at about 600 PV (CV_v about 1.17 × its initial value),
  then decline as the channel widens.
- The authors call the peak a "transient channel emergence window".
- They do **not** tie the peak to outlet breakthrough or to flow spreading. The velocity PDF stays bimodal and the surroundings stay stagnant.

### Stage 4: flow spreads again after breakthrough

**Supporting (PART)**

Karst models, where integration after breakthrough is physical and driven by head redistribution:
- **Perne et al. 2014 [read].**
  - After breakthrough the winning path P1 widens evenly along its whole length.
  - The steep head gradient between the still-plugged path P2 and the released P1 then grows connecting bypass conduits.
  - Under constant head, the network expands "until all possible flow paths evolve".
  - With recharge capped at a maximum Q (closer to our fixed rate), P2 joins P1 but further expansion is suppressed.
- **Dreybrodt et al. 2005, Sec. 4.11 [read]** ("Evolution of dual-fracture aquifers after breakthrough: integration of conduits").
  - After the first breakthrough the inputs are switched to constant recharge.
  - Heads drop in the winning channel, and flow from other inputs finds routes into it.
  - A cascade of secondary breakthroughs follows, then the integrated network becomes stable.
  - Counter-case (Birk et al. 2003 example, same chapter): widening of other pathways stops after breakthrough when the boundary
    conditions change everywhere at once.

DFN, pore network and core evidence:
- **Andrews et al. 2023 [abs].** Over 10^4–10^5 yr, dissolution moves from fast primary paths to secondary paths and dead-end fractures.
  - This is attributed to transport limitation, not explicitly to mineral depletion in the main paths [U: whether the paths deplete].
  - Earlier paper: Andrews & Navarre-Sitchler 2021, GCA, doi:10.1016/j.gca.2021.08.008 [abs, partial]. Domain-averaged rates fall
    over time; fractures stay reaction-limited while the matrix is transport-limited.
- **Szawełło et al. 2026 [read].** After DFN wormholes reach the outlet, ensemble variability of the focusing profile declines.
  - Even uniform dissolution only lowers f50 from about 0.8 to about 0.7.
  - Network topology and path lengths set a structural floor on homogenization.
  - **This sets the expected end-member of our stage 4: an emptied network has the participation set by structure, not 1.**
- **Roded, Aharonov, Holtzman & Szymczak 2020**, WRR 56(12), e2020WR027518 **[read abstract]**: in the uniform (low-Da) regime,
  dissolution homogenizes the medium and its flow field, more strongly when transport-controlled.
- **Deng, Sharma, Szymczak & Kang 2025**, GRL 52(15), e2025GL115940 **[abs]**: wormholing drives Fickian → non-Fickian transport;
  uniform dissolution drives it back.
- **Neyra et al. 2025 [read].** In cores, inlet channels thicken and merge (face dissolution) during stalls in wormhole advance.
  This is spreading before breakthrough, not after.

**Contradicting: no spreading after breakthrough**
- **Hyman et al. 2026 [read].**
  - After breakthrough, channelization stops changing and the system evolves by widening the existing conduit.
  - Their non-monotonic dispersivity ("expansion followed by collapse") comes from particles *converging* onto the wormhole, not from spreading.
  - **Do not cite their late-time uniformity as support for our stage 4.**
- **Szymczak & Ladd 2009 and Dreybrodt & Gabrovšek 2019 [read].** Losing wormholes stop growing once the winner breaks through.
- **Budek, Szymczak & Kang 2026**, EPSL 690, 120163, doi:10.1016/j.epsl.2026.120163 **[read].**
  - Coupled dissolution–replacement: after breakthrough, permeability and precipitation rate stabilize.
  - Reactants are flushed out because the channel walls have been fully replaced by inert product.
  - This finite-inventory case therefore freezes rather than spreads. It is directly relevant to our gypcal run.

**What was not found.** We found no paper in which spreading after breakthrough is caused by **exhaustion of the soluble fill** in the
main channel. In that mechanism:
- the channel's k reaches its cap;
- undersaturated water passes through it to partly filled neighbours, which keep opening;
- PR_V climbs toward the structural floor of the emptied network.

Related pieces:
- **Hyman et al. 2024**, G-cubed 25(7), e2024GC011550 **[read]**, and **Pachalieva et al. 2025**, Front. Environ. Sci. 12:1454295,
  doi:10.3389/fenvs.2024.1454295 **[read]**. Both use finite quartz fill in DFNs with PFLOTRAN, the setup closest to ours, but report
  only the initial and final (quasi-steady) states, with no time series of channelization.
- **Szymczak & Ladd 2011**, GRL 38, L07403, doi:10.1029/2011GL046720 **[abs]**: the amount of soluble material decides whether the
  inlet instability or the moving-front instability dominates.

---

## Q2. Specific authors and keywords

**Szymczak & Ladd; Budek & Szymczak; Upadhyay et al.**
- Competition, coarsening, and the end of competition at breakthrough, as above.
- Starchenko, Marra & Ladd 2016, JGR SE 121(9), 6421–6444, doi:10.1002/2016JB013321 [abs]; read via Starchenko & Ladd 2018, WRR 54,
  7946–7959, doi:10.1029/2018WR022948 [read].
  - Under constant pressure drop, flow keeps increasing after breakthrough and the outlet cross-section can turn elliptical.
  - The two papers give no network spreading.
- Cabeza, Hidalgo & Carrera 2020, GRL 47(3), e2019GL084795 [ref; arXiv 1911.02330 seen].
  - Competition is the shared mechanism of fingering and wormholing.
  - As the longest wormholes grow, their screening weakens and flow into secondary wormholes rises temporarily.
  - This is a transient re-spreading *before* breakthrough.

**Hanna & Rajaram; Detwiler & Rajaram; Cheung & Rajaram**
- Hanna & Rajaram 1998 [abs]: progressive flow capture until breakthrough.
- Cheung & Rajaram 2002, GRL 29(22), 2075, doi:10.1029/2002GL015196 [ref]: tip-region flow field controls finger growth.
- Detwiler & Rajaram 2007, WRR 43, W04403, doi:10.1029/2006WR005147 [ref].
- Detwiler, Glass & Bourcier 2003, GRL 30(12), 1648, doi:10.1029/2003GL017396 [ref].
- We found no post-breakthrough spreading result in these papers [U: full texts not read].

**Dreybrodt / karst breakthrough.** See Stage 4 above. Supporting references:
- Gabrovšek & Dreybrodt 2001, J. Hydrol. 240, 206–224, doi:10.1016/S0022-1694(00)00323-1 [ref].
- Palmer 1991, GSA Bull. 103, 1–21 [abs]: maze, network and branchwork cave patterns [U: we did not confirm his uniform-enlargement argument for mazes].
- Klimchouk's gypsum mazes in the Western Ukraine [abs, PANGEO and NSS records].
  - Dispersed upward (artesian) recharge forms mazes, with competition only during the initial phase.
  - This is the field counterpart of stage 4, a whole network enlarging [U: the mechanism in Klimchouk 2007 was not read].

**Hyman et al. 2024–2026**
- Hyman 2026 [read]:
  - d_Q/P32 rises slightly at low Da (mild homogenization).
  - It falls at intermediate Da.
  - It falls rapidly at high Da until breakthrough at τ ≈ 0.5.
  - Snapshots were taken at τ = 0, 0.1, 0.2, 0.5 and 1.0 only.
- Hyman 2024 [read]: before/after comparison; d_Q falls from 55.6 % to 28.1 % of P32 (from our existing note).
- Pachalieva 2025 [read]: final quartz distribution set by topological distance to the backbone.

**Deng & Spycher.** Deng & Spycher 2019, Rev. Mineral. Geochem. 85, 49–74, doi:10.2138/rmg.2019.85.3 [from earlier note]: review of
fracture reactive-transport models.
- Deng, Steefel, Molins & DePaolo 2018, ACS Earth Space Chem. 2, 112–124, doi:10.1021/acsearthspacechem.7b00130 [abs].
  - With increasing flow rate the regime moves from compact, to channelized, to uniform.
  - A multi-reaction Da predicts channelization.
  - No post-breakthrough staging was found.

**Steefel & Hu 2022**, WRR 58(9), doi:10.1029/2022WR032321 [read]: 2D DFN precipitation and clogging. No dissolution staging. REL.

**Kalia & Balakotaiah**
- Kalia & Balakotaiah 2009, Chem. Eng. Sci. 64, 376–390, doi:10.1016/j.ces.2008.10.026 [ref].
- Panga, Ziauddin & Balakotaiah 2005, AIChE J 51(12), 3231–3248, doi:10.1002/aic.10574 [ref]: two-scale continuum model.
- The breakthrough-volume (PVBT) framework; see Q4.

**Aharonov / Roded**
- Roded et al. 2020 [read abstract]: homogenization.
- Kelemen, Whitehead, Aharonov & Jordahl 1995, JGR 100(B1), 475–496, doi:10.1029/94JB02544 [abs]: experiments on flow focusing in
  soluble porous media. REL.
- [U: we did not find a "Roded et al. fracture networks" dissolution paper. Roded's network papers found are on anisotropic porous media.]

**Menke et al. (micro-CT)**
- Menke et al. 2015, ES&T 49(7), 4407–4414, doi:10.1021/es505789f [ref].
- Menke et al. 2016, Chem. Geol. 428, 15–26, doi:10.1016/j.chemgeo.2016.02.030 [abs]: Portland forms channels while Estaillades
  dissolves more uniformly; effective rates are up to 100 times below batch rates.
- Menke et al. 2018, Chem. Geol., "4D multi-scale imaging of reactive flow in carbonates..." [abs; U: volume, pages, DOI]:
  more heterogeneous rock gives more focused dissolution along the flow direction.
- Menke et al. 2023 [read]: channeling as a fourth regime; k–φ exponents of about 1.5–2 (compact), 5–6 (uniform), 6–12 (channeling) and 11–19 (wormhole).
- Al-Khulaifi et al. 2019, WRR 55(4), 3171–3193, doi:10.1029/2018WR024137 [ref].
- Kanavas, Jiménez-Martínez, Miele, Nimmo & Morales 2025, GRL 52(8), e2024GL114369 [abs]: 29 time-resolved 3D datasets; flow
  heterogeneity sets where dissolution hotspots form; feedbacks can reinforce or regulate hotspots.
- None of these reports spreading after breakthrough [U: full texts of Menke 2016/2018 and Kanavas 2025 not read].

**Starchenko, Cooper.** Covered above.

**Gypsum analog fracture.** Osselin et al. 2016, GRL 43, 6907–6915, doi:10.1002/2016GL069261 [abs]: a gypsum block between plates
validates the onset wavelengths predicted by reactive-infiltration instability theory. This is the same mineral as ours, but early times only.

**Search phrases tried.** "Flow focusing then defocusing", "flow redistribution after breakthrough", "transient channelization",
"re-homogenization". Apart from Wang 2026's "transient channel formation" and the karst "integration after breakthrough", these
returned nothing specific.

---

## Q3. Participation ratios and similar metrics over time

**Participation-ratio lineage.** Participation ratio (Bell, Dean & Hibbins-Butler 1970, J. Phys. C 3, 2111; Edwards & Thouless 1972,
J. Phys. C 5, 807) [ref] → Davy et al. 1995, 2010 [ref] → Andrade et al. 1999, PRL 82, 5249 [ref], and Andrade et al. 1997, PRL 79,
3901 (stagnant zones) [abs].

| Metric | Source | Weighting | Tracked over dissolution time? |
|---|---|---|---|
| d_Q = (1/V)(Σ S_f Q_f)² / Σ S_f Q_f² | Maillot, Davy, Le Goc, Darcel & de Dreuzy 2016, WRR 52(11), 8526–8545, doi:10.1002/2016WR018973 [read] | Fracture surface area S_f | No (static DFN) |
| d_Q/P32 | Hyman 2020, WRR 56(9), e2020WR027986, doi:10.1029/2020WR027986 [read] | S_f | No; density sweep |
| Particle-based participation ratio π = (1/N)(Σ π_f)² / Σ π_f² | Hyman 2020 [read] | Unweighted (by design) | No |
| d_Q before/after dissolution | Hyman et al. 2024 [read] | S_f | Two states only |
| d_Q/P32 at τ = 0, 0.1, 0.2, 0.5, 1.0 | Hyman et al. 2026 [read] | S_f | **Yes, 5 snapshots**; closest to our PR_V(t) |
| f50% = (n_X/2 − n_50%)/(n_X/2) per cross-section | Szawełło et al. 2024, GRL 51(20), e2024GL109940 [abs]; Szawełło 2026 [read] | Conduit count | Yes (profiles at 5 times) |
| CV of pore velocity | Wang et al. 2026 preprint [read] | Voxel | Yes (continuous; non-monotonic) |
| Moments (skewness, kurtosis) of throat-size and concentration distributions | Menke et al. 2023 [read] | Throat | Yes; mostly monotonic |
| Backbone (top-100 paths) surface fraction | Hyman 2026 [read] | Area | Yes |
| F–Φ curve, dynamic Lorenz coefficient | Shook & Mitchell 2009, SPE conference paper [abs; U: paper number] | **Pore volume (storage capacity)** | Static ranking of reservoir models |
| Count of active channels; wormhole-length distribution | Szymczak & Ladd 2009; Budek & Szymczak 2012 [read] | Count | Yes |

**Weighted versions.**
- Maillot's d_Q is the area-weighted participation ratio *of Q*. Ours, PR_V = (ΣQ)²/Σ(Q²/w), is the w-weighted participation ratio of
  the flux density Q/w, normalized to 1 for flow spread in proportion to volume.
- These are different quantities and should not be described as "Maillot's d_Q". Ours is closer to an inverse-Simpson effective
  volume fraction.
- The only pore-volume-weighted flow-heterogeneity measure we found is the reservoir-engineering F–Φ / dynamic Lorenz coefficient
  (Shook & Mitchell 2009), which is static.
- **We found no study that tracks a pore-volume-weighted participation ratio (our PR_pore) through a dissolution history, or that
  contrasts it with a solid-volume weighting.** Gini/Lorenz measures of flow during dissolution: none found.
- Note: Hyman 2026 also uses d_Q to estimate matrix-block spacing (Volponi et al. 2025, J. Hydrol. 650, 132462 [ref]).

---

## Q4. Dissolved fraction at breakthrough; is breakthrough the focusing peak?

**Breakthrough volume is a standard quantity, but with different normalizations**
- Acidizing: pore volumes to breakthrough (PVBT), with a minimum at an optimal Da.
  - Fredd & Fogler 1998 [ref].
  - Budek & Szymczak 2012 [read] define V̂_b = γ V_b / V0 (γ = acid capacity number). This is the reactant needed for breakthrough as a
    multiple of the initial pore volume, minimized for 0.1 ≲ Da_eff ≲ 1.
  - Both limits are inefficient: compact (inlet only) and uniform (all pores opened before breakthrough).
- In inventory terms:
  - near the uniform limit the dissolved fraction at breakthrough tends to the whole inventory;
  - in wormholing it is small.
  - [U: we found no paper that tabulates "fraction of soluble inventory dissolved at breakthrough".]
  - Our 56–63 % places the Forsmark runs between these limits, in a broad-front, channeling-like regime.
- Karst defines breakthrough as a flow jump (×1000 in Dreybrodt et al. 2005). Budek & Szymczak 2012 use an outlet pore widened by β.
  Breakthrough times are definition-dependent (see Q5).

**The τ ≈ 0.5 coincidence.**
- Hyman 2026 reports wormhole breakthrough at τ = ΔV_tot / V0 ≈ 0.5, where V0 is the initial open fracture volume (no mineral fill)
  [read; Eq. 26].
- If we normalize our dissolved gypsum by total fracture cell volume (the maximum open volume), our breakthrough sits at
  0.9 × 0.56–0.63 = **0.50–0.57**. If we normalize by the initial pore volume (φ0 = 0.1), it sits at τ ≈ 5–5.7.
- The two models' time axes are not equivalent. Any agreement with τ ≈ 0.5 should be called coincidental unless the normalization is stated.
- Their τ = 0.5 is also a snapshot bracket: there is no snapshot between 0.2 and 0.5.

**Does breakthrough mark the peak of focusing?**

| Source | Finding |
|---|---|
| Szymczak & Ladd 2009; Budek & Szymczak 2012; Dreybrodt & Gabrovšek 2019 [read] | Competition ends at breakthrough. Implicitly the most focused state is at or after breakthrough. |
| Hyman 2026 [read] | d_Q keeps falling, more slowly, after breakthrough. No minimum in d_Q is reported. |
| Wang 2026 [read] | Flow heterogeneity peaks at a "transient channel emergence window" that the authors do not link to outlet breakthrough. |
| Our runs | Peak focusing (PR_V minimum, about 42 %) comes clearly before breakthrough (56–63 %) |

**Our ordering is not reported in the literature we found.**
Plausible physical reading, our interpretation [U: not from the literature]: the inlet sections of the channel empty and cap their k
while the front is still in transit, so neighbours near the inlet start recruiting flow before the front reaches the outlet.

---

## Q5. Is the staging physical or a numerical artifact?

**Arguments that parts could be artifacts or model-dependent**

1. **One cell per fracture.**
   - In-fracture wormholing cannot form. Each fracture behaves like a well-mixed reactor, which smears fronts.
   - Single-fracture studies show that the in-fracture pattern (compact / wormhole / uniform) depends on per-fracture Pe, Da and length:
     Szymczak & Ladd 2009; Upadhyay 2015; Starchenko & Ladd 2018; Li, Hu, Szawełło, Yang, Chen, Szymczak & Zhou 2026, GRL
     "From Core to Field: Pattern Selection in Dissolving Fractures" [read; U: DOI].
   - Dzikowski & Szymczak 2026, Comput. Geosci., doi:10.1007/s10596-026-10410-z [read abstract]: below a minimum resolution (tied to the
     correlation length of the porosity field) channels come out straighter, bulkier and less ramified.
   - **Implication:** coarse representation biases toward broader channels and more spreading. This could exaggerate stage 4 and
     weaken the stage-3 minimum.
   - Doolaeghe et al. 2020 (PRE 102, 053312, from our earlier note): reduced graph models are least accurate at high-degree fractures.
2. **k–φ law choice.**
   - Hommel, Coltman & Class 2018, TiPM 124, 589–629, doi:10.1007/s11242-018-1086-2 [abs]: k–φ relations are not unique.
   - Menke 2023 [read] and Wang 2026 [read]: effective exponents range from about 1.5 to 40.9 and change over time and regime.
   - A linear law (n = 1) weakens the dissolution feedback, so it favors spreading and weakens focusing.
   - The porosity cap (empty fracture) is physical for a filled vein, but the k reached at the cap is model-dependent.
3. **Breakthrough definition and time sampling.**
   - Budek & Szymczak 2012 [read]: the breakthrough volume depends on the threshold β at small Da. A pore-merging rule removes their
     multiple PVBT minima. Lattice effects distort short wormholes.
   - Hyman 2026 and Szawełło 2026 use only five snapshots, so a non-monotonic d_Q between τ = 0.2 and 1.0 could be missed.
     **Their "no reversal" is weak evidence against our stage 4.**
4. **Unlimited vs finite wall material.**
   - Hyman 2026, Szawełło 2026, the karst models and Szymczak & Ladd all dissolve walls with no inventory limit, so channels never saturate.
   - Our stage 4 may simply be a regime those models cannot show. This is a model-class difference, not an artifact.

**Arguments that the staging is physical**
- Spreading after breakthrough by bypass integration appears in karst network models with physically motivated boundary conditions
  (Perne 2014; Dreybrodt et al. 2005 §4.11).
- A staged migration of the reaction front from primary paths to secondary paths and dead ends appears in DFN weathering
  (Andrews et al. 2023).
- Flow heterogeneity rising and then falling in time appears in image-based 3D simulations (Wang et al. 2026).
- Steady geometric advance with flat permeability, i.e. stage-1 decoupling, has been observed experimentally (Cooper 2023).
- Inlet homogenization preceding path takeover appears in pore-network models (Szawełło 2026).
- Gypsum maze caves are a field example of network-wide enlargement (Klimchouk) [U: mechanism].

**No paper argues specifically that a focusing-then-spreading sequence is a numerical artifact.**

Internal cross-references (project memory, not literature):
- the DFN-vs-graph timing differences at n = 3 (`tpl-dfn-validation-findings`);
- mesh-dependent k_eff after sealing (`sealing-proxy-track-d`).

**Cheap discriminating tests**
- Rerun one seed with n = 3 (or Kozeny–Carman). If stage 4 survives, it is inventory-driven.
- Rerun with the multiport mc4hd graph (per the project rule) or a refined DFN.
- Raise the cap on k at full dissolution. If spreading starts later or weakens, inventory exhaustion is the cause.

---

## Verdict

**Partly known. The full four-stage arc, measured as flow participation against inventory dissolved, appears novel.**

| Element | Status | Closest papers |
|---|---|---|
| Stage 1 (pore volume grows before flow reorganizes) | Known qualitatively | Cooper 2023 (expt.); Szawełło 2026 (inlet homogenization first); karst slow-then-jump |
| PR_pore vs PR_V as the diagnostic | Not found | — |
| Stage 2 (inheritance) | Well known for DFNs | Hyman 2024, 2026; Pachalieva 2025; Szawełło 2026; Andrews 2023 |
| Stage 3 (focusing until breakthrough) | Well known | Szymczak & Ladd 2009; Budek & Szymczak 2012; Hanna & Rajaram 1998; Hyman 2026 (d_Q, τ ≈ 0.5) |
| Peak focusing **before** breakthrough | Not found | Literature places it at or after breakthrough |
| Stage 4 (spreading after breakthrough) | Known in karst network models, driven by head redistribution | Perne 2014; Dreybrodt et al. 2005 §4.11; Andrews 2023 for the reaction-front shift |
| Stage 4 caused by exhaustion of soluble fill in a 3D DFN | Not found | — |

Stage 3 caveat: losing channels stop at breakthrough when wall material is unlimited.

Stage 4 contradictions: Hyman 2026 (channelization stops changing after breakthrough in 3D DFN graphs with unlimited walls) and Budek
2026 (the system freezes after breakthrough when products armour the walls).

**Closest papers overall**
1. Hyman, Szawełło, Kang & Szymczak 2026, JGR SE: same system class and metric family (d_Q); stages 2–3. Contradicts stage 4.
2. Perne, Covington & Gabrovšek 2014, HESS, and Dreybrodt, Gabrovšek & Romanov 2005, §4.11: competition, breakthrough, then integration and spreading.
3. Szawełło, Hyman, Kang & Szymczak 2026 (IJRMMS / arXiv:2602.06279): inlet homogenization first; structural floor on spreading.
4. Andrews et al. 2023, WRR: staged DFN reaction fronts (primary, then secondary and dead ends, then matrix).
5. Wang, Yang, Blunt & Bijeljic 2026 (arXiv preprint): flow heterogeneity rises then falls during channelized dissolution.
6. Cooper et al. 2023, AWR: experiment showing geometry advancing without a change in flow.

**Suggested framing:** "Each stage has precedent in a different system. The sequence, measured by volume-weighted flow participation, and
its finite-inventory mechanism for spreading after breakthrough are, to our knowledge, not previously reported for 3D fracture networks."
Hedge "to our knowledge". Not every full text was read (see the [abs]/[U] tags).

## Addendum 6 Nov 2026: Hyman et al. 2026 (JGR SE) Fig. 11, read from the PDF (pp. 19–20)

- They plot a **flow focusing profile** along x: per cross-section f50% = (n_f/2 − n50%)/(n_f/2), where n50% is the fewest
  connections carrying 50 % of the flow (Jang et al. 2011; profile introduced by Szawełło et al. 2024). 30 DFNs, τ = 0–1.
- Da = 2e-2 (wormholing): "a clear transition zone develops and progresses downstream". Behind the zone f50% rises from about
  0.8 to about 0.97–1.0 and **stays there**. "After breakthrough, further channelization ceases" (p. 22).
- Da = 2e-4: profiles decline almost uniformly (to about 0.7). Da = 2e-3: they rise slightly, with an inlet–outlet asymmetry.
- **For us:** a downstream-moving focusing front is published, so we cannot claim it. What is not in their work is the
  **relaxation behind the front**: in our runs each 100 m bin focuses as the front passes, then returns to about its start
  (end_rel ≈ 1.00, xbin_bin_minima.csv). Theirs is a step that holds, because the wall rock never runs out. Our moving
  zone is a peak, not a step.
- The metrics differ (f50% per cross-section against PR_V per 100 m bin with fractures binned by centre). Computing their
  f50% profile on our runs would make the contrast direct.
- Separate paper, same group: Hyman, Dell'Oca, Navarre-Sitchler & Viswanathan 2026, Transp. Porous Media 153:100,
  doi:10.1007/s11242-026-02352-y. 2D fracture-matrix CO2 mineralization sensitivity; Kozeny–Carman k–φ assumed, not tested.
  Not about focusing fronts.

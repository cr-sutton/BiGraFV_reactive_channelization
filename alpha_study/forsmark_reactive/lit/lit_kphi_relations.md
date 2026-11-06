# Permeability–porosity (k–φ) relations for reactive transport: review and verdict for the vein-filled one-cell fracture

Checked 5 Nov 2026. Purpose: judge the Forsmark BiGraFV k–φ choice. Each fracture is one PFLOTRAN cell with fixed volume
(area × b_h). It starts at φ0 = 0.1 (gypsum VF 0.9) and k0 = the dfnWorks fracture permeability (b_h²/12). The law is
`PERMEABILITY_POWER 1`, with the reference porosity = material `POROSITY` = 0.1 (STUDY_SCOPE.md; checked in
`phase1/*/gypsum__uncorrected_graph__phase1/single_stage.in`: `POROSITY 0.1d0`, Gypsum 0.9). So k/k0 = φ/φ0, and full
dissolution gives ×10 (×20 at φ0 = 0.05).

Verification labels:
- **[full]** = text read: local PDF extract, or a manual or report read here.
- **[abs]** = abstract or publisher metadata only.
- **[sec]** = taken from a secondary source; the original was not read.
- **UNVERIFIED** = could not confirm.

All DOIs in this note were resolved through the Crossref API on 5 Nov 2026 unless marked otherwise. Text extracts are in
`/private/tmp/claude-501/-Users-collin-Projects-bipartite-pflotran-src-alpha-study/4bb44bc2-48f5-4f4b-bcf1-243f8b14a913/scratchpad/kphi_dl/`
(`*.pdf.txt`).

Overlap with the existing notes:
- `lit_wormhole_regime.md` covers the fracture regime map (Li 2026, Szymczak & Ladd).
- `lit_large_dfn_reactive.md` covers the DFN reactive studies and the Detwiler, Elkhoury and Jones experiments.
- This note covers only what those two leave out: the k–φ law itself.

---

## 1. Kozeny–Carman (KC)

**Derivation in brief.** The pore space is treated as a bundle of tortuous capillaries. Each tube obeys Poiseuille flow with
hydraulic radius r_h = φ/S. Here S is the wetted surface per bulk volume, S = S_s(1−φ), where S_s is the surface per solid
volume (6/d for spheres). This gives

  k = φ³ / [c τ² S_s² (1−φ)²]  →  for spheres, k = d² φ³ / [180 (1−φ)²] (Carman constant 180, i.e. Kozeny constant c τ² ≈ 5).

The normalised form used in reactive codes keeps S_s and τ fixed:

  k/k0 = (φ/φ0)³ [(1−φ0)/(1−φ)]²   (TOUGHREACT Eq. F.7, "ignoring changes in grain size, tortuosity and specific surface area").

Sources:
- Kozeny 1927, Sitzungsber. Akad. Wiss. Wien 136:271–306 [sec: reference checked in Sabo & Beckingham 2021].
- Carman 1937, Trans. Inst. Chem. Eng. 15:150–166, reprinted as Carman 1997, Chem. Eng. Res. Des. 75:S32–S48,
  doi:10.1016/S0263-8762(97)80003-2 [abs].
- Bear 1972 (book), as cited by the TOUGHREACT guide.
- Kuhlman & Matteo 2018 (SAND2017-12697C, OSTI 1483231) [full]: tube shape factor "1.7 < c < 3" in the equivalent-channel model.

**Assumptions:**
- an isotropic packing of grains of one characteristic size;
- every pore conducts (no dead ends, no percolation threshold);
- the tortuosity and the surface per solid volume do not change as φ changes;
- the alteration is uniform over all pore walls.

**Where it fails:**
- **Low porosity and cemented rock.** The connectivity of the pore space is lost before φ reaches 0.
  - Bourbié & Zinszner 1985, JGR 90(B13):11524–11532, doi:10.1029/JB090iB13p11524 [abs]: Fontainebleau sandstone has
    k ∝ φ^3.05 for φ = 9–28 % and k ∝ φ^7.33 for φ = 3–9 %.
  - Mavko & Nur 1997, Geophysics 62(5):1480–1482, doi:10.1190/1.1444251: they replace φ with φ − φ_c (percolation
    porosity). φ_c ≈ 0.025 for Fontainebleau [sec; the value comes from secondary sources, not the paper].
  - Zhang, Paterson & Cox 1994, JGR 99(B8):15741–15760, doi:10.1029/94JB00646: hot-pressed calcite has n ≈ 3 for
    φ = 0.18–0.07 and n ≈ 14 below 0.07 [sec].
  - Kuhlman & Matteo 2018 [full]: "Many users simply make the porosity exponent an adjustable factor, more typically 3 to 8",
    and KC "under-predicts" the permeability loss in low-permeability rock.
- **Precipitation.** Mineral grows at pore throats, so k falls far faster than KC predicts. Verma & Pruess (Section 3) and the
  TOUGHREACT guide say so explicitly, citing Vaughan 1987 and Pape et al. 1999.
- **Heterogeneous (non-uniform) alteration.**
  - Beckingham 2017, WRR 53(12):10217–10230, doi:10.1002/2017WR021306 [abs]: KC-type laws work when the amount of reaction
    scales with pore size. They fail when reaction starts in the small pores or in the large ones.
  - Sabo & Beckingham 2021, WRR 57(6), doi:10.1029/2020WR029072 [full, OSTI manuscript]: with simultaneous dissolution and
    precipitation, porosity can rise while k falls. A Verma–Pruess law needs a *negative* exponent (−2.5) to fit this.
  - Poonoosamy et al. 2015 (in `lit_large_dfn_reactive.md`): KC underestimated the permeability change.
- **Fractures and veins.** KC has no wall term. Hyman et al. 2024 G-cubed (doi:10.1029/2024GC011550) [full] state that for
  infilled fractures, "classic models like the Kozeny-Carmen equation ... are not appropriate in part because they do not
  consider the effect of the fracture walls" (citing Bisdom et al. 2016, JGR 121(5):4045–4063, doi:10.1002/2015jb012657).
- **Near φ → 1.** KC diverges, but a filled fracture is bounded by the open cubic-law value b_h²/12. Golfier et al. 2002 avoid
  the divergence by switching to Darcy–Brinkman–Stokes (Section 6).

Costa 2006, GRL 33(2), doi:10.1029/2005GL025134 [abs] gives a fractal re-derivation of KC with a Kozeny coefficient and a
fractal exponent as its two fitting parameters.

---

## 2. Power laws k ∝ φ^n and their exponents

**The key review.** Hommel, Coltman & Class 2018, Transp. Porous Media 124(2):589–629, doi:10.1007/s11242-018-1086-2. Only the
abstract was available: the full text is paywalled, and the only PDF found was on an unofficial mirror, which was not used.
The abstract says:
- "Commonly applied porosity–permeability relations in simulation models on the REV scale use a power-law relation";
- many exponential or simplified KC relations "do not lead to fundamentally different predictions of permeability alteration
  when compared to a simple power-law relation with a suitable exponent";
- the exceptions are biomass laws with a residual permeability, and laws with "a critical porosity at which the porous medium
  becomes impermeable; this is often used when modeling the effect of mineral precipitation".

Implication: the practical choice reduces to two decisions, the exponent and whether to include a critical porosity.

**Exponents reported, by rock type and process:**
- **Bernabé, Mok & Evans 2003**, Pure Appl. Geophys. 160(5–6):937–960, doi:10.1007/PL00012574 [abs]. There is "no universal"
  k–φ law. The evolution is constrained once the process is known, and is interpreted as creation or destruction of
  effectively and non-effectively conducting pore space. The process-specific exponent values in its tables were not read
  (UNVERIFIED).
- **Sandstone:**
  - n ≈ 3 at high φ and 7–8 near the percolation threshold (Bourbié & Zinszner 1985 [abs]).
  - Pape, Clauser & Iffland 1999, Geophysics 64(5):1447–1460, doi:10.1190/1.1444649, and Pape et al. 2000, PAGEOPH
    157(4):603–619, doi:10.1007/PL00001110 [abs]: a fractal three-term law (terms in φ, φ² and (10φ)^10) calibrated on 640
    Rotliegend sandstones. The 10th-power term dominates at high φ. The coefficients (31, 7463, 191; k in nm²) are UNVERIFIED.
- **Limestone, CO2 dissolution, micro-CT:**
  - Noiriel, Gouze & Bernard 2004, GRL 31(24), doi:10.1029/2004GL021572 [abs]: n falls continuously while the micrite
    dissolves, then stays constant during sparite dissolution. A value "up to ~24" is quoted secondhand and is UNVERIFIED.
  - Noiriel et al. 2005, OGST 60(1):177–192, doi:10.2516/ogst:2005011 [sec]: n is the local slope of log k against log φ.
  - Luquot & Gouze 2009, Chem. Geol. 265(1–2):148–159, doi:10.1016/j.chemgeo.2009.03.028 [sec, HAL abstract via search]:
    k and φ follow power laws "with distinctly different scaling exponents" set by the reactivity of the inlet fluid. Moderate
    Da increases k most efficiently. The values of n are UNVERIFIED. A secondary source quotes 15–27.6 for wormholing in Gouze
    & Luquot 2011, J. Contam. Hydrol. 120–121:45–55, doi:10.1016/j.jconhyd.2010.07.004 (UNVERIFIED).
  - Voltolini & Ajo-Franklin 2019, IJGGC 82:38–47, doi:10.1016/j.ijggc.2018.12.013 [full]: Indiana limestone,
    "exponent α close to 5", larger than the KC prediction. The exponent varies with porosity.
  - Menke et al. 2016, Chem. Geol. 428:15–26, doi:10.1016/j.chemgeo.2016.02.030 [abs]: the dissolution regime (uniform or
    channel) depends on the initial pore structure. Effective rates are up to 100× below flat-surface rates.
- **Low-k carbonates (model fit to experiments):** Hao, Smith, Sholokhova & Carroll 2013, Adv. Water Resour. 62:388–408,
  doi:10.1016/j.advwatres.2013.09.009 [abs snippet]: the more impermeable and heterogeneous cores "required larger n values
  (n = 6–8)".
- **Pore-network models of dolostone:** Nogues, Fitts, Celia & Peters 2013, WRR 49(9):6006–6021, doi:10.1002/wrcr.20486 [abs]:
  - "Exponent values ... ranged from 2 to 10, but a value of 6 held constant when conditions led to uniform changes";
  - diffusion-dominated dissolution changes φ a lot and k little;
  - precipitation lowers k more slowly than dissolution raises it, but small amounts near the inlet can cause large changes.
- **Pore-scale imaging with dynamic exponents:** Wang, Yang, Blunt & Bijeljic 2026, arXiv 2605.18223 (preprint) [abs]: the
  k–φ path "cannot be captured by a single power-law". Peak effective exponents are 9.8, 18.0 and 40.9, rising with pore
  heterogeneity.
- **Hysteresis:**
  - Lesueur, Poulet & Veveakis 2020, GRL 47(18), doi:10.1029/2020GL088674 [abs]: microchannels opened during dissolution give
    permeability hysteresis after reprecipitation. Porosity-only k(φ) functions cannot capture this.
  - Noiriel, Steefel, Yang & Bernard 2016, Adv. Water Resour. 95:125–137, doi:10.1016/j.advwatres.2015.11.013 [abs]: for the
    same porosity loss, k falls more where crystal growth roughens the pores most. The substrate (calcite vs glass) changes
    the k–φ path.
- **Civan.** Civan 2001, AIChE J. 47(2):271–287, doi:10.1002/aic.690470206 [abs]: the "power-law flow unit" family
  k/φ = Γ[φ/(1−φ)]^{2β}, with β an interconnectivity exponent. The exact form was recalled from memory and is UNVERIFIED.

Rule of thumb from the data: n ≈ 3 for well-connected granular media. For connectivity-controlled media (low φ, cemented,
carbonates, near a percolation threshold) n is 5–10 and can reach 20–40. Precipitation at pore throats needs a critical
porosity, not just a larger n.

---

## 3. The Verma–Pruess critical-porosity law, the benchmarks, and code defaults

**What Verma & Pruess actually derived.** Verma & Pruess 1988, JGR 93(B2):1159–1173, doi:10.1029/JB093iB02p01159
[metadata]. The LBL preprint was read [full]: Verma & Pruess 1985, LBL-20479, OSTI 5216654.
- The law was not originally a power law. It comes from "a set of non-intersecting planar flow channels with in general
  non-uniform cross-sectional area", i.e. a tubes-in-series model of wide sections and narrow throats.
- The critical porosity φ_c is "the smallest value to which porosity can be reduced by silica scaling on the flow channel wall".
- They ran a "simple cubic" model (uniform channels, φ_c = 0, i.e. k ∝ φ³) and series models with φ_c/φ0 = 0.8 and 0.95.
  The latter was chosen "to explore effects of an extremely strong dependence of permeability upon porosity changes".
- The application was silica redistribution around high-level nuclear waste.
- The original is therefore a planar-channel (fracture-like) model. It already contains the cubic law as its φ_c = 0 limit.

**The simplified power form used by codes.** k/k0 = [(φ−φc)/(φ0−φc)]^n (TOUGHREACT Eq. F.8, "an improved
porosity-permeability relationship presented by Verma and Pruess (1988)"; PFLOTRAN Eq. 31).
- Calibrated geothermal case: Xu et al. 2004, Geothermics 33(4):477–491, doi:10.1016/j.geothermics.2003.09.012, read through
  the TOUGHREACT V1.2.1 guide §8.8 [full]. Tiwi injection-well silica scaling, fracture porosity 1 %:
  - fits with φc = 0.88 % and n = 13, 0.90 % and 11, 0.92 % and 10, 0.94 % and 6 at 705 ppm silica;
  - fits with φc = 0.90 % and n = 5, 0.92 % and 4 at 710 ppm;
  - "A smaller critical porosity φc requires a larger power term n";
  - so permeability vanishes once only 6–12 % of the fracture pore volume has been scaled.
- Sabo & Beckingham 2021 [full] use φc = 0.3 φ0 and n = 1–2.5. They state that "guidance for n values for sandstone suggests
  values between 0.73 to 1.978 (Verma & Pruess, 1988)". That claim was not found in the LBL preprint and is UNVERIFIED.

**Benchmarks.**
- Xie, Mayer, Claret, Alt-Epping, Jacques, Steefel, Chiaberge & Simunek 2015, Comput. Geosci. 19(3):655–671,
  doi:10.1007/s10596-014-9458-3 [full, eScholarship]:
  - CrunchFlow, HP1, MIN3P, PFLOTRAN and TOUGHREACT on six problems, all using the Carman–Kozeny law, Archie tortuosity with
    exponent 1/3, and a 2/3 surface-area power;
  - the agreement is good, with differences mostly in the clogging problems;
  - problem B2 is calcite dissolution with gypsum precipitation clogging the flow path: gypsum VF reaches 62.6 % and the
    minimum φ is 0.0016 (MIN3P, PFLOTRAN, TOUGHREACT);
  - the codes disagree mainly on the minimum porosity and the position of the clogging front, i.e. on how each handles
    porosity approaching zero.
- Steefel et al. 2015, Comput. Geosci. 19(3):445–478, doi:10.1007/s10596-014-9443-x [abs]: code descriptions. Full text not
  read.

**Code defaults and options:**

| Code | Options | Default or typical use | Source |
|---|---|---|---|
| PFLOTRAN | f = [(φ−φc)/(φ0−φc)]^n, f = f_min for φ ≤ φc; keywords `PERMEABILITY_POWER`, `PERMEABILITY_CRITICAL_POROSITY`, `PERMEABILITY_MIN_SCALE_FACTOR`; switched on by `UPDATE_PERMEABILITY` | The docs list no defaults. Project memory (code check) gives n = 1 by default. φ0 is the material `POROSITY` | theory guide Eqs. 28–32 [full]; material card [full] |
| TOUGHREACT | `ipptyp` 0 none; 1 simplified KC (F.7); 3 cubic law k = k_i(φ/φ_i)³ for fractures (F.2, Steefel & Lasaga 1994); 4 modified cubic law via hydraulic aperture b0,h = (12 k0 s)^{1/3} and k' = (b0,h + Δb)³/(12 s) (F.3–F.6); 5 Verma–Pruess (F.8) | Option chosen per zone. Option 4 exists because "permeability reductions to values near zero occur at porosities significantly greater than zero" | TOUGHREACT V1.2.1 guide, LBNL-55460-2008, App. F [full] |
| CrunchFlow, MIN3P, HP1 | Normalised KC | Used in the Xie 2015 benchmark; the full option lists were not checked (UNVERIFIED) | Xie 2015 [full] |
| OpenGeoSys 6 | KC (initial φ and k as inputs) | Forum and docs only; a power-law option was not confirmed (UNVERIFIED) | OGS discourse [abs] |
| MOOSE PorousFlow | k = k0 (1−φ0)^m/φ0^n · φ^n/(1−φ)^m, a generalised KC | n and m set by the user | MOOSE docs [abs] |
| dfnWorks + PFLOTRAN (Hyman group) | PFLOTRAN power law | **n* = 1.0** in Hyman, Dell'Oca, Navarre-Sitchler & Viswanathan 2026, TiPM 153:100, doi:10.1007/s11242-026-02352-y [full]. Exponent a not stated in Hyman et al. 2024 G-cubed (φ0 = 0.01, quartz-filled fractures) or 2024 IJGGC 139:104265, doi:10.1016/j.ijggc.2024.104265 [full] | local extracts |

**Why the defaults are what they are:**
- KC is the textbook law, and the benchmarks used it so every code was solving the same equations.
- n = 1 in the LANL DFN studies is a minimal-feedback choice. Hyman et al. 2026 TiPM call their law "one of many possible
  pedotransfer functions" and limit their scope to avoid choosing among them. G-cubed notes that because every cell starts
  uniform, "this discrepancy is uniform throughout the domain and does not affect our normalized results".
- Note that the G-cubed argument holds for the starting state only. Once dissolution is non-uniform, the law sets the
  contrast between cells.

---

## 4. Fractures: the cubic law, aperture-based laws, sealed veins

**Cubic law.** For parallel plates, T = b³/12 per unit width (m³) and k = b²/12. Real fractures deviate because of roughness
and contact area.
- Witherspoon, Wang, Iwai & Gale 1980, WRR 16(6):1016–1024, doi:10.1029/WR016i006p01016.
- Zimmerman & Bodvarsson 1996, TiPM 23(1):1–30, doi:10.1007/BF00145263 [abs].
- Contact-area correction: hydraulic conductivity scales as (1 − 2c), with c the contact area fraction (Zimmerman & Bodvarsson
  1996). Yeo 2001 modified it to (1 − 2.4c) [sec].

**Aperture-based dissolution models** (fractures, karst, graph models):
- These evolve b directly, with T ∝ b³. Examples:
  - Dreybrodt 1996, WRR 32(9):2923–2935, doi:10.1029/96WR01332;
  - Szymczak & Ladd 2009, JGR 114(B6), B06203, doi:10.1029/2008JB006122;
  - Szymczak & Ladd 2012, JFM 702:239–264, doi:10.1017/jfm.2012.174;
  - Hyman, Szawełło, Kang & Szymczak 2026, JGR 131(3), e2025JB033004, doi:10.1029/2025JB033004.
- Nothing fills the fracture, so b can grow without bound. The feedback exponent of transmissivity in aperture is 3.
- TOUGHREACT option 3 maps this onto fracture porosity as (φ/φ0)³.

**Experiments on single fractures:**
- **Dissolution:**
  - Detwiler, Glass & Bourcier 2003, GRL 30(12), doi:10.1029/2003GL017396 [abs]: a ~110 % rise in mean aperture gave k
    +440 % (Pe 54, channelised) and +640 % (Pe 216, uniform). Against mean aperture this is an effective k exponent of
    ln 5.4/ln 2.1 ≈ 2.3 to ln 7.4/ln 2.1 ≈ 2.7 (our arithmetic). The dissolution pattern, not just the mean opening, set the
    gain.
  - Caprock core floods gave k ×2–3 (Ellis et al. 2011, GHG Sci. Tech. 1(3):248–260, doi:10.1002/ghg.25; Deng et al. 2013,
    Energy Fuels 27(8):4221–4231, doi:10.1021/ef302041s), from the earlier Track F check in `aperture-realism-kphi` memory.
  - Deng, Steefel, Molins & DePaolo 2018, ACS Earth Space Chem. 2(2):112–124, doi:10.1021/acsearthspacechem.7b00130: in
    multimineral fractures the insoluble fraction controls the aperture growth.
- **Net dissolution can still lower k (stress):**
  - Polak, Elsworth, Yasuhara, Grader & Halleck 2003, GRL 30(20), doi:10.1029/2003GL017575 [sec, PSU abstract]: in
    novaculite under net dissolution the pressure drop rose ~100× over 900 h, a ~5× drop in hydraulic aperture caused by
    dissolution of stressed contacts.
  - Yasuhara, Elsworth & Polak 2004, JGR 109(B3), doi:10.1029/2003jb002663: the pressure-solution model for this.
  - Ishibashi, McGuire, Watanabe, Tsuchiya & Elsworth 2013, WRR 49(5):2828–2842, doi:10.1002/wrcr.20253 [sec, abstract via
    search]: carbonate fractures at 3–10 MPa gape at pH < 6.1 and close at pH > 6.5, independent of confining stress.
  - Lang, Paluszny & Zimmerman 2015, JGR 120(6):4080–4101, doi:10.1002/2015jb011968: sealing by growth of pressure-solution
    contacts.
  - Relevance: for our stress-free cells, n_eff can even be negative in reality.
- **Sealing:**
  - Elkhoury, Detwiler & Ameli 2015, EPSL 417:99–106, doi:10.1016/j.epsl.2015.02.010 (see `lit_large_dfn_reactive.md`):
    dolomitic anhydrite fractures self-sealed (k −100×) at high flow but kept their channels at low flow.
  - Jones & Detwiler 2016 (same note): mineral heterogeneity means sealing takes more than 10× longer than uniform-precipitation
    models predict.
- **Partially cemented (vein) fractures:**
  - Tokan-Lawal, Prodanović & Eichhubl 2015, JGR 120(8):5453–5466, doi:10.1002/2015JB012045 [abs]: cement raises tortuosity
    and capillary pressure and lowers single-phase k "by up to 2 orders of magnitude" against barren fractures. Multiphase
    behaviour resembles a porous medium. Published aperture–k correlations disagree with one another and with the simulations
    by several orders of magnitude.
  - Laubach et al. 2019, Rev. Geophys. 57(3):1065–1111, doi:10.1029/2019RG000671 [metadata]: review of fracture cementation
    and bridging.
  - Aljuboori et al. 2021, Carbonates Evaporites 36:6, doi:10.1007/s13146-020-00664-8 [abs, DOI not Crossref-checked]: 34 % of
    fractures blocked cut reservoir k by 29–83 %.
- **Field reopening of mineral-sealed fractures:** Portier & Vuataz 2010, C. R. Geosci. 342(7–8):668–675,
  doi:10.1016/j.crte.2010.04.002 [abs via search]: at Soultz most fractures are sealed by calcite, silica and clays.
  Regular-mud-acid stimulation gave at most a 35 % gain in injectivity index (model estimate). Portier et al. 2009,
  Geothermics 38(4):349–359, doi:10.1016/j.geothermics.2009.07.001 [metadata].

**What follows for a one-cell, fixed-volume vein** (our reasoning; the cell has thickness b_h and open fraction φ):

| Fill geometry | Implied cell law | Gain from φ0 = 0.1 to φ = 1 |
|---|---|---|
| Fill as two wall layers, open slot of width φ b_h (slot / TOUGHREACT option 3) | k = (b_h²/12) φ³, i.e. n = 3 with absolute k0 = φ0³ b_h²/12 | ×1000 (×8000 at φ0 = 0.05; ×82 at φ0 = 0.23, the Track F number) |
| Fill as full-height strips aligned with flow, open channels between them | T = φ b_h³/12, so **n = 1** exactly | ×10 |
| Fill as random full-height pillars (contact-area law, 1 − 2c with c = 1 − φ) | k ∝ 2φ − 1, impermeable for φ < 0.5; n_eff ≫ 1 | from 0 below φ = 0.5 to b_h²/12 |
| Fill as porous crystal mush across the aperture (KC with crystal size d ≤ b_h) | k_fill/k_open = d² φ³/(180(1−φ)²) / (b_h²/12) | open/sealed contrast ≈ 1.2e4 (b_h/d)² at φ0 = 0.1, ≈ 1.1e5 (b_h/d)² at φ0 = 0.05, i.e. ≥ 10⁴ even for d = b_h |
| Throat-controlled seal (Verma–Pruess, φc/φ0 = 0.8–0.95) | k → 0 at φc, steep near φ0 | ×2000 at n = 2, φc = 0.08; precipitation seals after only 5–20 % refill |

Only one of these geometries gives n = 1: full-height open channels running parallel to the flow. Every other plausible vein
microstructure gives a larger open/sealed contrast, from ~10³ to beyond 10⁴. Separately from the contrast, the absolute
endpoint is wrong. Our cells start at k0 = b_h²/12, the open-fracture value, and end at 10 b_h²/12, which exceeds the
cubic-law ceiling of an aperture b_h by 1/φ0. With rate-controlled flow only the contrast matters for flow partitioning, and
the absolute level only rescales pressure (project memory `pflotran-reactive-gotchas`). So this matters for reporting k_eff,
not for the channel patterns.

---

## 5. How the law is chosen in practice

| Basis | Typical choice | Where |
|---|---|---|
| Code default or benchmark | Normalised KC (n ≈ 3 at small φ) or PFLOTRAN n = 1 | Xie 2015 benchmark codes; LANL DFN studies (n* = 1) |
| Calibration to a core flood or µCT series | Power law with fitted n = 3–10 (carbonates up to 20–40) | CO2 storage in carbonates (Hao 2013 n = 6–8; Nogues 2013 2–10; Voltolini 2019 ~5) |
| Calibration to field injectivity | Verma–Pruess with φc close to φ0, n = 4–13 | Geothermal reinjection scaling (Xu 2004, Tiwi) |
| Mechanistic geometry | Cubic law in aperture (T ∝ b³); modified cubic law with spacing | Karst (Dreybrodt 1996), single-fracture and graph dissolution (Szymczak & Ladd; Hyman 2026), TOUGHREACT fracture options 3–4 |
| Process with a clogging limit | Critical porosity plus f_min; biomass laws with residual k | MICP and biofilm (Hommel 2018 review), precipitation clogging (Xie 2015 B2–B6) |
| Acid stimulation (wormholing) | KC or modified KC with exponent β; Darcy–Brinkman–Stokes near φ → 1 | Golfier et al. 2002; Panga et al. 2005; Kalia & Balakotaiah 2007; Maheshwari et al. 2013 |
| Nuclear waste, salt | Verma–Pruess (its origin); KC; power exponents 3–8 | Verma & Pruess 1985/88; Kuhlman & Matteo 2018 |
| Numerical stability | Low n, larger f_min, φ_min floor | High n stiffens the coupling near closure. In our runs every coupled cubic variant died where a cell closed inside one 5.7 y step, and needed dt ≤ 0.57 y (project memory). Xie 2015 found the code differences concentrated in the clogging problems. |

---

## 6. Does the exponent control channelization?

**Linear stability.**
- Szymczak & Ladd 2014, JFM 738:591–630, doi:10.1017/jfm.2013.586 [full]: "a permeability contrast between the dissolved and
  undissolved material is needed to drive the instability"; with no contrast the planar front is stable.
- Szymczak & Ladd 2013, GRL 40(12):3036–3041, doi:10.1002/grl.50564 [full arXiv]: uses K ∝ φ³; the most unstable wavelength
  shrinks as the porosity contrast grows up to Δ ~ 1.
- Ladd & Szymczak 2017, WRR 53(3):2419–2430, doi:10.1002/2016WR019263 [full]:
  - the thin-front dispersion relation (Chadam et al. 1986, IMA J. Appl. Math. 36(3):207–221, doi:10.1093/imamat/36.3.207;
    Ortoleva et al. 1987) depends on the permeability ratio Γ = K0/K1;
  - "the qualitative features of the reaction-infiltration instability are insensitive to the precise form of the constitutive
    models".
- So the law enters mainly through the end-member **contrast** K1/K0 = 1/Γ, not through its curvature.
- In the thin-front growth rate the factor (1 − Γ)/(1 + Γ) is already 0.82 at a contrast of 10 (our n = 1) and 0.998 at
  10³. Pattern *selection* (whether fingers form, and their spacing) is therefore nearly saturated at contrast 10. This is our
  arithmetic on their formula, valid only in the thin-front limit.

**Depth of flow focusing.** How much flow a channel can capture is bounded by the contrast.
- Our own estimate for one fully dissolved path in parallel with N − 1 unaltered equivalent paths: its flow share is
  C/(C + N − 1).
- With C = 10 and N = 50 the share is 17 %; with C = 10³ it is 95 %.
- The same logic explains the Track F result in project memory (`aperture-realism-kphi`): n = 3 on TPL left dissolved mass
  and placement unchanged but raised k_eff from ×2.69 to ×19.5.
- It also matches Hyman 2024 G-cubed [full]: with φ0 = 0.01, primary-subnetwork k rose about two orders of magnitude and
  secondary about one.

**Darcy-scale wormholing models:**
- Golfier, Zarcone, Bazin, Lenormand, Lasseux & Quintard 2002, JFM 457:213–254, doi:10.1017/S0022112002007735 [sec]:
  simplified KC plus Darcy–Brinkman–Stokes; regimes on a Da–Pe diagram.
- Panga, Ziauddin & Balakotaiah 2005, AIChE J. 51(12):3231–3248, doi:10.1002/aic.10574: two-scale model whose
  structure–property relations include a modified KC (exponent 2 → β) [sec via Liu et al. 2017; exact form UNVERIFIED].
- Kalia & Balakotaiah 2007, Chem. Eng. Sci. 62(4):919–928, doi:10.1016/j.ces.2006.10.021.
- Maheshwari, Ratnakar, Kalia & Balakotaiah 2013, Chem. Eng. Sci. 90:258–274, doi:10.1016/j.ces.2012.12.032.
- Cohen, Ding, Quintard & Bazin 2008, Chem. Eng. Sci. 63(12):3088–3099, doi:10.1016/j.ces.2008.03.021 (Golfier model): wormhole
  competition is not fully scale invariant.
- Liu, Yao, Couples, Ma & Iliev 2017, Sci. Rep. 7:17711, doi:10.1038/s41598-017-18095-2 [full]: "the choice of the
  structure-property relations affects the simulation of the dissolution process significantly" (citing Maheshwari &
  Balakotaiah; the original sensitivity study was not read, UNVERIFIED).
- Budek & Szymczak 2012, PRE 86:056318, doi:10.1103/PhysRevE.86.056318: pipe networks with conductance ∝ d⁴ wormhole over
  broad conditions.

**Not found:** a published 3D DFN study that varies the k–φ exponent at fixed chemistry. Our Track F n = 3 test and the
planned φ0 = 0.05 test (STUDY_SCOPE Phase 2a) appear to be new.

---

## 7. Table of realistic parameter values

| Law | Parameter | Range | Rock / process | Source (status) |
|---|---|---|---|---|
| KC (spheres) | Carman constant | 180 (Kozeny c τ² ≈ 5); tube shape factor 1.7–3 | Granular packs | Carman 1937/1997 [abs]; Kuhlman & Matteo 2018 [full] |
| Power k ∝ φ^n | n | ≈ 3 (φ 9–28 %), 7.3 (φ 3–9 %) | Fontainebleau sandstone | Bourbié & Zinszner 1985 [abs] |
| Power | n | ≈ 3 (φ 0.07–0.18), ≈ 14 below 0.07 | Hot-pressed calcite (compaction) | Zhang et al. 1994 [sec] |
| Power | n | "typically 3 to 8" as a fitting factor | General, low-k rock | Kuhlman & Matteo 2018 [full] |
| Power | n | 2–10; 6 under uniform dissolution | Dolostone pore network, CO2 brine | Nogues et al. 2013 [abs] |
| Power | n | 6–8 | Low-k heterogeneous carbonate cores, CO2 | Hao et al. 2013 [abs] |
| Power | n | ≈ 5 | Indiana limestone, µCT | Voltolini & Ajo-Franklin 2019 [full] |
| Power (dynamic) | peak n_eff | 9.8–40.9 | Carbonates, channelled dissolution | Wang et al. 2026 preprint [abs] |
| Power | n | 15–27.6 (wormholing); up to ~24 | Limestone, CO2 | Gouze & Luquot 2011; Noiriel 2004 (UNVERIFIED) |
| Power (fracture, vs mean aperture) | n_eff for k | ≈ 2.3–2.7 (k ×5.4–7.4 for aperture ×2.1) | Analog fracture dissolution | Detwiler et al. 2003 [abs] + our arithmetic |
| Cubic law | T ∝ b³, k ∝ b²; as (φ/φ0)^3 | exponent 3 | Open or slot fractures | Witherspoon 1980; TOUGHREACT F.2 [full] |
| Verma–Pruess (original) | φc/φ0 | 0.8 and 0.95 (plus 0 = cubic) | Planar channels, silica scaling, HLW | Verma & Pruess 1985 LBL [full] |
| Verma–Pruess (power form) | φc/φ0 ; n | 0.88–0.94 ; 4–13 | Geothermal fracture scaling, φ0 = 1 % | Xu et al. 2004 via TOUGHREACT guide [full] |
| Verma–Pruess | φc/φ0 ; n | 0.3 ; 1–2.5 (−2.5 for anti-correlated) | Sandstone pore network, dissolution + precipitation | Sabo & Beckingham 2021 [full] |
| Percolation KC | φ_c | ≈ 0.025 (2.5–5 %) | Fontainebleau | Mavko & Nur 1997 [sec] |
| Contact-area | factor | 1 − 2c (1 − 2.4c) | Rough fractures with contacts | Zimmerman & Bodvarsson 1996; Yeo 2001 [sec] |
| Cemented fracture | k reduction vs barren | up to 10² | Partially cemented sandstone fracture | Tokan-Lawal et al. 2015 [abs] |
| PFLOTRAN DFN practice | n* | 1.0 | Gypsum → calcite, quartz in DFNs | Hyman et al. 2026 TiPM [full] |
| Field reopening | injectivity gain | ≤ 1.35× | Acidising calcite-sealed granite fractures (Soultz) | Portier & Vuataz 2010 [abs] |
| Self-sealing | k change | −100× (high flow) | Fractured dolomitic anhydrite | Elkhoury et al. 2015 [abs, prior note] |

---

## 8. Verdict: n = 1 on a vein-filled one-cell fracture

**Short answer:** n = 1 is **conservative** for the permeability contrast, and therefore for how strongly flow focuses. It is
**unrealistic as a description** of a 90 %-filled vein. It is **acceptable** for the questions the study asks about mass
placement, provided k_eff is reported as a bracket.

1. **Contrast.** With n = 1 a fully reopened cell gains ×10 at φ0 = 0.1. The geometry-based estimates for a sealed vein that
   reopens to an open fracture of aperture b_h give:
   - slot cubic law: ×10³ (×8 × 10³ at φ0 = 0.05);
   - throat-controlled (Verma–Pruess) seal: ×10³ and up;
   - porous crystal fill (KC): ≥ ×10⁴, up to ×10⁶ for crystals ≪ b_h;
   - against these, n = 1 understates the contrast by 2–5 orders of magnitude.
2. **Calibrated exponents.** Calibrated n values for connectivity-controlled media (carbonates, cements, near-percolation
   rock) are 3–10 and up to 20–40. Only one fill geometry gives exactly n = 1: full-height open channels parallel to the flow.
3. **Where n = 1 is realistic.** Partial dissolution of fractures, as in core floods and Detwiler's analog fractures, gives
   effective k gains of ×2–×7. Field acidising of calcite-sealed fractures (Soultz) gave ≤ ×1.35. Stress can turn net
   dissolution into closure (Polak 2003; Ishibashi 2013). For modest reopening under confining stress, n = 1 is therefore
   realistic or even generous. This is the case for the first fractions of dissolution and for the secondary network.
4. **What the exponent changes.** Following Szymczak & Ladd, it mostly sets the ceiling on flow focusing (k_eff, share of
   flow in channels). It hardly changes whether fingering starts once the contrast is ≥ 10. Our Track F test agrees:
   placement was unchanged and k_eff went ×2.69 → ×19.5.
5. **Absolute k.** The current setup puts the sealed vein at the open-fracture permeability b_h²/12 and ends at 10 b_h²/12,
   above the cubic-law ceiling. Under rate control this only rescales pressure, but quote k_eff as a ratio, not as an absolute
   permeability.

**Bracketing values to run or quote:**
- **Lower bracket: n = 1** (current), the "flow-parallel channels" fill, contrast 1/φ0.
- **Central: n = 3** with reference φ0. This is the slot cubic law and the TOUGHREACT fracture option, and KC is about n ≈ 3
  at low φ. Contrast is 1/φ0³ (10³ at φ0 = 0.1). It must have the physically consistent endpoint k(φ = 1) = b_h²/12, which
  means setting material `POROSITY` = 1 and scaling k0 by φ0³; this only rescales pressure under rate control.
- **Upper bracket for sealing and channel depth:** Verma–Pruess with φc/φ0 = 0.8–0.9 and n = 2–3, or power n = 5–8. These are
  the carbonate and geothermal calibrations. Use them only with `PERMEABILITY_MIN_SCALE_FACTOR` ≥ 1e-4 and dt ≤ 0.57 τ: high n
  and φc make precipitation runs stiff.
- **A cheaper way to vary the contrast without changing n:** lowering φ0 (0.05 → contrast 20 at n = 1). This is the Phase 2a
  route already planned. It changes Da and capacity along with the contrast, so a contrast-matched pair (n = 1 at φ0 = 0.01
  against n = 2 at φ0 = 0.1, both ×100) would separate the two effects.

---

## 9. Corrections to existing notes found while checking

- `lit_wormhole_regime.md` cites "SL09 = Szymczak & Ladd 2009, JGR 114, F02021". Crossref gives the fracture paper as
  **JGR Solid Earth 114(B6), B06203, doi:10.1029/2008JB006122** ("Wormhole formation in dissolving fractures").
  `lit_large_dfn_reactive.md` already has B06203. The arXiv number (0902.1374) is correct.
- `lit_large_dfn_reactive.md` lists Hanna & Rajaram 1998 with "DOI 10.1029/98WR01863 [U]". That DOI resolves to Rutqvist
  et al. 1998 (fracture storativity), not Hanna & Rajaram. The correct DOI was not found (UNVERIFIED).
- `lit_large_dfn_reactive.md` gives the Szymczak & Ladd 2012 JFM DOI 10.1017/jfm.2012.174 as "from memory". It is now
  confirmed by Crossref.
- Attributions:
  - The "Verma–Pruess power law" k/k0 = [(φ−φc)/(φ0−φc)]^n is TOUGHREACT's simplified version. The original (LBL-20479 / JGR
    1988) is a tubes-in-series planar-channel model with φc/φ0 = 0.8–0.95.
  - Mavko & Nur 1997 is in *Geophysics* 62(5), not GRL.

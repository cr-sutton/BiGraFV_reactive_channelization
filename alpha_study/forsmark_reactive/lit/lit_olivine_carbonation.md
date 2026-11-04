# Olivine carbonation: sourced inputs for the GIRT deck (hanford.dat, isothermal Richards)

Checked 4 Nov 2026. VERIFIED = I read the number in the primary text (PDF text extracted locally) or computed it from the file named. UNVERIFIED = only seen in a search-result snippet, or not found. Scratch copies of the PDFs and text are under
`/private/tmp/claude-501/-Users-collin-Projects-bipartite-pflotran-src-alpha-study/4bb44bc2-48f5-4f4b-bcf1-243f8b14a913/scratchpad/olv/` (km = Kelemen & Matter 2008, kar = Kelemen et al. 2011, kh = Kelemen & Hirth 2012, pk = Palandri & Kharaka 2004, gad = Gadikota et al. 2014, lis = Lisabeth et al., ds/olvcalc = Duan & Sun port).

## 1. Stoichiometry and solid volume change of Mg2SiO4 + 2CO2 -> 2MgCO3 + SiO2

Database (`/Users/collin/src/pflotran/database/hanford.dat`, 2nd field = molar volume, cm3/mol) - VERIFIED, file lines:
- Forsterite 43.7900 (line 2662; MW 140.6931 -> 3.21 g/cm3). Written as Mg2SiO4 + 4H+ = 2Mg++ + SiO2(aq) + 2H2O.
- Magnesite 28.0180 (line 2807; MgCO3 + H+ = Mg++ + HCO3-; MW 84.3142). A second entry `Magnesite*` (line 2808) has a Langmuir-type constant logK -4.9, no use here.
- Chalcedony 22.6880 (line 2346) and Quartz 22.6880 (line 3040): identical molar volume in this file.
- SiO2(am) 29.0000 (line 3107).

Computed from those numbers (VERIFIED, arithmetic):
| silica phase | products (cm3/mol Fo) | ratio products/Fo | solid volume change |
|---|---|---|---|
| chalcedony or quartz | 2*28.018 + 22.688 = 78.724 | 1.798 | +79.8 % |
| SiO2(am) | 2*28.018 + 29.0 = 85.036 | 1.942 | +94.2 % |
| magnesite only (silica leaves as SiO2(aq)) | 56.036 | 1.280 | +28.0 % |

Published figures:
- Kelemen & Matter 2008 PNAS 105, p. 17297: "Carbonation of olivine (Eq. 2b) results in 44% increase in the solid volume" - VERIFIED text. Their reaction (Eq. 2, as extracted) is Mg2SiO4 + 2CO2 -> 2MgCO3 + SiO2 with the silica labelled **quartz**. Note the equation labels in the extracted text are garbled (2a/2b), so I cannot say which reaction the 44 % refers to.
- Kelemen et al. 2011 Annu. Rev. Earth Planet. Sci. 39:545 (p. 558): "increase the solid volume by 33% (serpentinization) to 44% (carbonation) relative to the initial solid volume", products given as magnesite and **quartz** - VERIFIED.
- Kelemen & Hirth 2012 EPSL 345:81-89, p. 82: R2 = Mg2SiO4 + 2CO2 = 2MgCO3 + SiO2 (olivine + CO2 = magnesite + **quartz**); "These reactions increase the solid volume by 40-50% relative to the initial solid volume" (R1-R4 together, not R2 alone) - VERIFIED.
- Lisabeth, Zhu, Xing, De Andrade (accepted manuscript, OSTI 1421960): hydration and carbonation of forsterite "result in solid volume changes of 46% and 88% respectively" - VERIFIED text in the manuscript (journal/year not confirmed from the file; DOI string in the file was chemgeo 2012.10.025, which looks like a reference, so cite as OSTI 1421960).
- Utrecht group (Liu, Wolterbeek, Spiers) "~85%" - UNVERIFIED (search snippet only).

Verdict: the database ratio (+80 % with chalcedony or quartz, +94 % with SiO2(am)) is NOT the 44 % quoted by Kelemen & Matter 2008 and Kelemen et al. 2011; it does agree with the 88 % of Lisabeth et al. I could not reproduce 44 % from any silica molar volume in the database. If the deck wants a published number, 44 % is the most cited, but the molar volumes in the file you are running give +80 %. Say which one is used.
All three papers assume quartz (or write SiO2 without specifying) for the silica product. Gadikota et al. 2014 PCCP 16:4679 lists "quartz, chalcedony or opal" as possible solid SiO2 (VERIFIED). Hanford Chalcedony has the quartz molar volume.

## 2. Kinetic parameters (Palandri & Kharaka 2004, USGS OFR 2004-1068; https://pubs.usgs.gov/of/2004/1068/pdf/OFR_2004_1068.pdf)

Rate law (their eq. 6): rate = SA * sum_i k25_i exp[-E_i/R (1/T - 1/298.15)] a_H^n_i (1 - Omega^p)^q, with k25 the constant "at 298.15 K (25 C) and pH = 0" in mol m-2 s-1, E in kJ/mol - VERIFIED (p. 4 text, Table footnotes). PFLOTRAN reads ACTIVATION_ENERGY in J/mol by default (`reaction_mineral.F90` lines 176-181), so give units explicitly (kJ/mol). PFLOTRAN PREFACTOR blocks with PREFACTOR_SPECIES H+ and ALPHA = n reproduce the pH dependence (example `regression_tests/default/batch/prefactor_sec.in`).

Forsterite - Table 23 "Orthosilicate Dissolution Rate Parameters" (p. 35), row "Forsterite -6.85 67.2 0.470 -10.64 79.0 -- -- --" - VERIFIED:
- acid: log k25 = -6.85 (k = 1.41e-7 mol/m2/s), E = 67.2 kJ/mol, n(H+) = 0.470
- neutral: log k25 = -10.64 (k = 2.29e-11 mol/m2/s), E = 79.0 kJ/mol
- base: none. The text says the acid mechanism "apparently operates at pH up to ~9". Fitting is on the forsterite data of Chen & Brantley, Oelkers, Pokrovsky & Schott, Wogelius & Walther.
- Arrhenius factor to 185 C (my arithmetic): x1.3e4 (acid), x6.8e4 (neutral); k(185 C) = 1.8e-3 and 1.6e-6 mol/m2/s before the pH term.

Magnesite - Table 33 "Carbonate Mineral Dissolution Rate Parameters" (p. 42), row "magnesite -6.38 14.4 1.000 -9.34 23.5 -5.22 62.8 1.000" - VERIFIED:
- acid: log k25 = -6.38 (4.17e-7), E = 14.4 kJ/mol, n(H+) = 1.00
- neutral: log k25 = -9.34 (4.57e-10), E = 23.5 kJ/mol
- carbonate: log k25 = -5.22 (6.03e-6), E = 62.8 kJ/mol, order 1.00 (carbonate mechanisms are "quantified in terms of either HCO3- or PCO2", p. 5; which one is used for magnesite is not stated in the text I read - UNVERIFIED)
- Their text: "In the absence of data for the activation energy for magnesite dissolution, the activation energy of calcite is assigned to magnesite" (E 14.4 and 23.5 are the calcite values - these are not measured for magnesite); affinity parameters p = 4.00, q = 1.00 from Pokrovsky & Schott 1999 (25 C only).
- These are DISSOLUTION constants. Palandri states: "Precipitation rate data do not exist for most minerals" (p. 5). Do not use them as the precipitation rate.

Silica - Chalcedony is NOT listed in Palandri & Kharaka (no match in the text) - VERIFIED absence. Options:
- Quartz, Table 4 (p. 13), neutral: log k25 = -13.40, E ~ 90.9 kJ/mol (digit garbled in the OFR text; the PHREEQC copy of the table, https://water.usgs.gov/water-resources/software/PHREEQC/documentation/phreeqc3-html/rate-parameters_pk.htm, gives "-13.4 90.9"). Other quartz rows: -13.34/90, -13.99/87 (BET area).
- Amorphous silica, Table 6 (p. 15), neutral dissolution: log k25 = -12.23, E = 74.5 kJ/mol (Icenhower & Dove 2000 values); alternates -12.31/76.0 (regressed) and -12.77/68.7 (Rimstidt & Barnes 1980). Dissolution only, no acid or base term.
- Precipitation, "All SiO2 polymorphs": log k = -9.42, E = 49.8 kJ/mol (from Rimstidt & Barnes 1980) - VERIFIED, Table 6 (k = 3.8e-10 mol/m2/s at 25 C). The text warns that amorphous silica precipitation from grossly supersaturated fluids is a special case (p. 5).

Magnesite precipitation problem at low temperature:
- Saldi, Jordan, Schott & Oelkers 2009 GCA 73:5646-5657 (abstract text via search result, primary not read - UNVERIFIED): at 100 C HAFM growth rates fit r = k (Omega - 1)^2 with k = 6.5e-16 mol/cm2/s (= 6.5e-12 mol/m2/s); step advancement has a much higher activation energy than step generation, so growth is very slow at low T; magnesite precipitation "inhibited below about 80 C" (paraphrase of a later paper's summary, UNVERIFIED).
- Saldi et al. 2012 GCA (title: "An experimental study of magnesite precipitation rates at neutral to alkaline conditions and 100-200 C as a function of pH, aqueous solution composition and chemical affinity") - abstract only: rates rise with saturation state, fall with CO3-- activity and pH, reaction order 2, spiral growth. k values at 150 and 200 C NOT retrieved - UNVERIFIED.
- Rates used in published reactive-transport work:
  - Steefel & Hu 2022 WRR 58, e2022WR032321 (2D DFN, PFLOTRAN-type TST rate R = -A k [1 - Q/K], their eq. 2), Table 2 (p. 7) mixing runs: magnesite k = 1e-8 mol/m2/s, A = 100 m2/m3, initial volume fraction 0; Table 5 (critical zone): forsterite k = 1e-8 mol/m2/s, A = 1000 m2/m3, initial fraction 0.02; magnesite k = 1e-8, A = 1.0 m2/m3 - VERIFIED. Text: the magnesite constant "is representative of what has been found in various experimental studies (e.g., Giammar et al. 2005; Steefel & Yang 2021; Xiong & Giammar 2014)" and "Magnesite is allowed to form without a nucleation barrier". Their silica product is aqueous SiO2 (their reaction 14: forsterite + 2CO2 -> 2MgCO3 + SiO2(aq)); no silica solid. Note 1e-8 is about 1000x the Saldi 100 C value at Omega-1 = 1 (6.5e-12 mol/m2/s); the two are not directly comparable (temperature, affinity law), but the gap is real.
  - Hansen et al., Xu et al. TOUGHREACT CO2-mineralization papers, Beinlich, Kelemen & Hirth precipitation rates: NOT TRACED - UNVERIFIED. The TOUGHREACT user guide I fetched (LBNL-55460) has no olivine inputs. Kelemen & Matter 2008 do not use TST rates; they fit a lumped carbonation rate (their eq. 4, a function of PCO2^(1/2) and exp(-0.000334 (T-185 C)^2), prefactor 1.15e-5 in the extracted text; units and exact form garbled in extraction, so not usable as a TST input).

## 3. Operating conditions

- Kelemen & Matter 2008 p. 17297: "the rate of carbonation is optimized at, for example, 185 C and 150 bars CO2 pressure" (footnote to Gerdemann et al. 2003 data, OSTI 898299); their fit used olivine grains of 75 um - VERIFIED. Note "for example": the optimum is a maximum between kinetic speed-up and approach to the equilibrium boundary, from Albany Research Center experiments, not a derived exact value.
- Kelemen et al. 2011 p. 556: fastest ARC rates "at 185 C in aqueous solutions with 1 M NaCl and 0.64 M NaHCO3 with PCO2 > 70 bar and pH ~ 8"; Method 1 injects fluids "equilibrated with CO2 at ~100 bar" (section 5.1) - VERIFIED. Important: the fast experiments were in bicarbonate brine at pH ~8, not in pure CO2-water.
- Dissolved CO2 in pure water at 185 C (458.15 K): I ported the Duan & Sun 2003 (Chem. Geol. 193:257-271) pure-water model from the Rphree R implementation (`rdrr.io/rforge/Rphree/src/R/Rphree_Solub.R`, Duan-Sun parameters, Duan EOS for fugacity) to `scratchpad/olvcalc/ds.py`. Check: 25 C, 1.013 bar gives 0.0329 mol/kg (literature ~0.033-0.034, OK). Results (mol/kg, no NaCl):
  - total pressure 150 bar (PCO2 = 150 - 11.14 bar water vapour = 138.9 bar): **1.03 mol/kg**
  - PCO2 = 150 bar (total 161.1 bar): **1.09 mol/kg**
  - 100 bar total: 0.72 mol/kg; 200 bar: 1.29 mol/kg.
  Status: computed with a third-party port of the published model, not read from the paper's own table - treat as UNVERIFIED to +-5 % (paper states ~7 % experimental uncertainty, from search snippet). 1.0 mol/kg is a defensible round number. Total carbon is essentially this value (HCO3- is ~3e-4 mol/kg).
- pH of that water (my estimate, ideal activities, using hanford.dat CO2(aq) = H+ + HCO3- logK: line 429, -6.7235 at 150 C and -7.1969 at 200 C, interpolated linearly to 185 C = -7.055): pH = (7.055 - log10 1.03)/2 = **3.5**. A PFLOTRAN speciation with ACTIVITY_COEFFICIENTS would shift this by a few tenths. This is far below the pH ~8 of the ARC experiments, so magnesite supersaturation only arrives after forsterite consumes H+ (4 H+ per Mg2SiO4).
- Database temperature grid - VERIFIED: line 1 of hanford.dat is `'temperature points' 8 0. 25. 60. 100. 150. 200. 250. 300.` so 185 C lies between the 150 and 200 C columns. PFLOTRAN interpolates logK between the bracketing grid points (`reaction_database.F90`, Interpolate calls near lines 899-945; I did not trace whether the interpolation is linear in T, but it uses the two bracketing points). logK values at 150/200 C, e.g. Forsterite 16.9413/14.1544, Magnesite -0.3520/-1.2275 (lines 2662, 2807), are in the file. Whether the Debye-Huckel activity model of the database is valid at 185 C and 1 mol/kg is not verified. hanford.dat has no CO2 fugacity/EOS; the injected CO2 has to be set as total dissolved carbon (HCO3- or CO2(aq) total), not as a pressure.

## 4. Reactive surface area

- Gadikota, Matter, Kelemen, Park 2014 PCCP 16:4679 (p. 4680): Twin Sisters olivine, mean particle size 21.40 um, BET 3.77 m2/g, pore volume 0.012 mL/g; after reaction BET falls to 0.80-3.20 m2/g depending on PCO2 (64-164 atm) and 0.15-1.25 m2/g for 1-5 h at 185 C - VERIFIED. (Note: this olivine contains ~13.9 wt% Fe2O3, Table 1.)
- Kelemen & Matter 2008: fit uses 75 um grains; for field rock they scale area with a reactive volume fraction 0.01 %, "effective grain size or fracture spacing of 7 mm" (p. 17297) - VERIFIED. Kelemen et al. 2011: scaling to a crack spacing of ~0.7 m gives about 50 % carbonation per year at 185 C, 150 bar - VERIFIED (section 5.1).
- Steefel & Hu 2022 (see item 2): forsterite 1000 m2/m3 in fractures (coarsely crushed material), magnesite 100 m2/m3 (mixing runs) or 1 m2/m3 (critical zone, small seed area), initial magnesite volume fraction 0 - VERIFIED.
- Lisabeth et al.: specific surface area of thermally cracked dunite taken as 3 m-1 (Darot et al. 1992), giving an effective olivine dissolution rate of 1e-12 mol/cm2/s - VERIFIED text (m-1 is area per volume).
- Nucleation/seed area for silica: no published value found - UNVERIFIED. Steefel & Hu need no silica solid.
- Conversion for the deck: at 0.9 volume fraction of forsterite (3.21 g/cm3 -> 2890 kg/m3 bulk), 3.77 m2/g gives ~1e7 m2/m3 and 1 m2/g gives 2.9e6 m2/m3 (my arithmetic). Steefel & Hu's 1000 m2/m3 is 3-4 orders lower. The choice sets the Damkohler number.

## 5. Natural fracture apertures in peridotite (context only)

- Kelemen et al. 2011, Supplement S4.3: "millions of 10 micron to 10 centimeter veins are visible as white coatings on joint surfaces" in Oman road cuts; reconnaissance vein volume 1 % far from travertine, 5 % close - VERIFIED. These are filled vein widths, not hydraulic apertures. Field sample notes in the same supplement list veins "mm scale" to "<= 10 cm" and one "50 cm".
- Kelemen et al. 2011 supplement S15: fissured weathering horizon in Oman peridotite permeability ~1e-14 m2 (Dewandel et al. 2005); crystalline-rock range 1e-13 to 1e-10 for 1 % fracture porosity - VERIFIED.
- Hydraulic apertures for Oman fractures: NOT FOUND. A search for Oman Drilling Project aperture data returned only vein abundance (1-3 % of core in the top 50-100 m of Wadi Lawayni) - UNVERIFIED for apertures.

## 6. Published reactive-transport studies showing clogging and rerouting

- Steefel & Hu 2022 WRR 58(9):e2022WR032321 - 2D DFN, TST rates, magnesite from fluid mixing at a fracture intersection: precipitation selectively in one fracture segment lowers its permeability and velocity "selectively within the fracture segment where the magnesite precipitation occurs" while the other segments are nearly unaffected; "the possibility of wholesale reorganization of the flow system due to changes in connectivity"; porosity change small, permeability change detectable only between 1000 and 5000 years - VERIFIED. Their second case (forsterite to magnesite in the partially saturated critical zone) was read for parameters only; I did not extract a clogging result from it. Closest match to the question, but it is 2D, magnesite from mixing, not injected CO2 into olivine-filled fractures.
- Lisabeth, Zhu, Xing, De Andrade (OSTI 1421960) - laboratory, thermally cracked dunite, 150 C, 15 MPa confining, 3 days, CO2-rich bicarbonate solution: total porosity decreases, but "an interconnected network of porosity is maintained through channelized dissolution and coupled carbonate precipitation" - VERIFIED (abstract). Counterexample to simple clogging; an experiment, not a reactive-transport model.
- Utrecht (Liu, Wolterbeek, Spiers) flow-through crushed dunite: permeability falls from 1e-16 to 1e-17 down to 1e-20 to 1e-21 m2 during carbonation - UNVERIFIED (snippet only).
- Kelemen et al. 2011 (p. 550): "In the subsurface, with increasing solid volume, one might expect decreasing permeability and armoring of reactive surfaces to limit the extent of reaction, yet the 14C data indicate that low-temperature alkaline springs feeding travertine deposits remain active for tens of thousands of years" - VERIFIED, field context.
- No published 2D/3D fracture-network reactive-transport model of olivine (forsterite) carbonation with fracture clogging and flow rerouting was found other than the closest-match Steefel & Hu 2022 above. Searches of Hansen, Xu/TOUGHREACT and Beinlich returned nothing usable - UNVERIFIED that none exist.

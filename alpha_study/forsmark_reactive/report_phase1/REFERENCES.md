# References and normalisation backing, Forsmark reactive study phase 1 (3 Nov 2026)

Status key: **VERIFIED** = I read the equation or sentence in the source text (PDF extracted locally, or publisher/Crossref record for bibliographic data). **UNVERIFIED** = not read in the primary source; reason given.
Local extractions (scratchpad, session-specific): `.../scratchpad/pdfs/hyman2026.txt` (JGR 2026), `.../dl/Geochem*.txt` (G-cubed 2024), `.../dl/1_s2.0_S1750583624002081*.txt` (IJGGC 2024), `.../dl/1_s2.0_S0012821X26003468*.txt` (Budek EPSL 2026), `.../ref/maillot.txt`, `ref/hyman2020.txt`, `ref/sl2009.txt` (arXiv 0902.1374v2), `ref/arx_sz.txt`, `ref/tr1052.txt`. Equation images for Maillot Eq. 8 and TR-10-52 Table 6-75 were rendered and inspected.
DOIs were checked against Crossref unless marked.

## Findings that bear on our normalisations (read first)
1. **t_cap is not a published quantity.** It is our construction. Closest published object: Szymczak & Ladd 2009, Eq. 52 and Fig. 16 (V_inj/V0). Our t_cap = (V_inj/V0^SL) x (V_pore0/V_solid0) = (V_inj/V0^SL)/9 at vf0 = 0.9, so it is the same normalisation up to the constant 1/9 (see item 1).
2. **Capacity is an upper bound.** t_cap assumes the water leaves saturated. The brief itself notes ~470 vs 516.6 mol/m^3 for the brine (a 9 % overstatement of capacity in the coupled runs). At low Da (water leaves unsaturated) dissolved fraction < t_cap.
3. **d_Q literal formula differs from the one in the brief.** Maillot Eq. 8 and Hyman 2020/2024/2026 write d_Q with Q_f, "half the absolute total volumetric flow exchanged by a fracture" (a flow, not a flux). The brief's form with q = Q/S is a flux-density reading and equals d_Q/P32 under that reading, not the literal published d_Q. Label it "our reading of Maillot" (item 5).
4. **One-pore-volume-per-year is ambiguous in the source.** Hyman 2024 says "the initial volume of each fracture network per year" and sets phi0 = 0.01. Whether "volume" is bulk fracture volume or pore volume is not stated. Ours (pore volume, UGE volume x (1 - vf0)) is a choice. If Hyman means bulk volume, our rate is (1 - vf0) = 0.1 of theirs per unit bulk volume (item 3).
5. **SKB transmissivity parameters are from the wrong depth interval.** network_forsmark.py uses the 200-400 m intensities (0.142, 0.345, 0.133, 0.081, 0.316; verified, TR-10-52 Table 6-75) but the transmissivity (a, b, sigma) = (6.3e-9, 1.3, 1.0), which TR-10-52 gives for depths **above 200 m**. For -200 to -400 m the table gives semi-correlated (1.3e-9, 0.5, 1.0) and correlated (1.6e-9, 0.8). At r = 100 m the two models differ by ~190x in T (2.5e-6 vs 1.3e-8 m^2/s). Also, sigma = 0 in the code uses the semi-correlated (a, b), not the table's "correlated" (a, b). Fixed Q makes absolute T irrelevant to flow rate, but not to the T(r) contrast, so the "SKB depth 200-400 m" label in BRIEF.md is not strictly correct.
6. **Hyman 2020 is not Front. Phys.** It is Water Resources Research 56(9), e2020WR027986 (item 5).
7. **Fox et al. 2007 has no "Hjerne"**: authors are Fox, La Pointe, Hermanson, Oehman (item 11).
8. **Fredd & Fogler PV_bt and N_ac definitions** were not read in the primary paper; backing for that item is secondary (item 1).
9. **tau extends beyond Hyman's range.** Hyman 2026 tau <= 1 and dissolution only. Ours reaches ~9 and, in coupled runs, uses net volume (calcite subtracted). Both are our extensions (item 2).

---

## 1. Capacity-normalised time t_cap

**Verdict: our construction, backed by published capacity scalings. Not a direct published quantity.**

### Our definition
$$ t_\mathrm{cap}=\mathrm{PV}\,\frac{c_\mathrm{cap}}{C_\mathrm{inv}},\qquad C_\mathrm{inv}=\frac{v_{f0}}{(1-v_{f0})\,V_\mathrm{gyp}} $$
with c_cap = 16.6 mol/m^3 (dilute) or 16.6 + 1000[CO3] (brine), V_gyp = 74.69e-6 m^3/mol.
Check: 0.9/(0.1 x 74.69e-6) = 1.205e5 mol/m^3 pore (VERIFIED arithmetic; V_gyp VERIFIED in IJGGC App. C: "74.69e-6 for gypsum and 36.934e-6 for calcite").

### Source A: Szymczak & Ladd 2009, Eq. 52 (VERIFIED, arXiv v2 text)
$$ V_0 = W L \bar h_0\,\frac{c_\mathrm{sol}}{C_\mathrm{in}}\,\frac{\nu_\mathrm{aq}}{\nu_\mathrm{sol}},\qquad V_\mathrm{inj}=\frac{T\,Pe}{\bar h_0}\,L\,V_0 \ (\text{Eq. 51}) $$
Quote: "is the volume of reactive fluid needed to dissolve a solid volume equal to the initial pore space in the fracture." Fig. 16 plots V_inj/V0 in the Pe-Da plane. Eq. 18 defines a time scale tau = (h0^2/D)(c_sol/C_in)(nu_aq/nu_sol), the same capacity ratio.
**Mapping:** their V0 dissolves a solid volume equal to the initial *pore* volume; our t_cap=1 dissolves the whole solid *inventory* (9x pore volume). Hence t_cap = (V_inj/V0^SL)(1 - vf0)/vf0 = (V_inj/V0^SL)/9. This is consistent with the brief's "tau = 1 arrives at t_cap = 0.11" (1/9 = 0.111).

### Source B: Hyman, Szawello, Kang & Szymczak 2026, p. 6 (VERIFIED)
"the acid capacity number $\gamma = c_0/(\nu c_{sol})$ (-), which quantifies how much solid a unit volume of reactant can dissolve". In Hyman 2026 it only enters as the quasi-steady condition gamma << 1. Eq. (15): $\partial_t b = 2k_\mathrm{eff}(b)\,\nu c_\mathrm{sol}\, c$ is written with nu c_sol; Eq. (17): $\Delta b = \Delta t\, \frac{q}{L}\frac{c_0}{c_{sol}\nu}(1-e^{-2k_\mathrm{eff}L/q})$ (reconstructed from garbled text).
**Mapping:** our c_cap/c_solid = 16.6 x 74.69e-6 = 1.24e-3 is the analogue of gamma for saturation-limited gypsum dissolution (excess over saturation in place of c_0). Hyman's gamma uses a reactant consumed by reaction, ours a solubility ceiling: same role, different chemistry. gamma << 1 holds for gypsum-only (1.2e-3), so quasi-steady transport is justified; for 0.5 M brine gamma ~ 3.8e-2 (516.6 x 74.69e-6; UNVERIFIED as a regime boundary for coupled flow).

### Source C: Fredd & Fogler 1998 and Golfier et al. 2002 (UNVERIFIED in primary text)
- Fredd, C.N. & Fogler, H.S. (1998). Influence of transport and reaction on wormhole formation in porous media. *AIChE J.* 44(9), 1933-1949. doi:10.1002/aic.690440902 (bibliographic data VERIFIED, Crossref). Secondary sources (search results, patents) report an optimum Damkohler number ~0.29 at which a minimum number of pore volumes to breakthrough (PV_bt) is needed, and that PV_bt scales inversely with the acid capacity number N_ac at low N_ac. I did not read the primary paper, so the exact N_ac and PV_bt definitions are UNVERIFIED. Cited by Budek et al. 2026 EPSL for first-order kinetics (VERIFIED, ref list and Sec. 2.1).
- Golfier, F., Zarcone, C., Bazin, B., Lenormand, R., Lasseux, D., Quintard, M. (2002). On the ability of a Darcy-scale model to capture wormhole formation during the dissolution of a porous medium. *J. Fluid Mech.* 457, 213-254. doi:10.1017/S0022112002007735 (bibliographic VERIFIED, Crossref). Content not read; cited by Hyman 2026 as an example of the three dissolution regimes (VERIFIED in their text).

### Statement for the report
"t_cap is our normalisation. It equals the injected volume divided by the volume of reactive fluid needed to dissolve the whole solid inventory (Szymczak & Ladd 2009, Eq. 52, rescaled by pore/solid volume ratio), expressed through the acid-capacity ratio gamma (Szymczak & Ladd 2012; Hyman et al. 2026)." Do not write "published t_cap".

Other refs for this item:
- Szymczak, P. & Ladd, A.J.C. (2009). Wormhole formation in dissolving fractures. *J. Geophys. Res.* 114, B06203. doi:10.1029/2008JB006122. VERIFIED (Crossref and arXiv text).
- Szymczak, P. & Ladd, A.J.C. (2012). Reactive infiltration instabilities in rocks. Fracture dissolution. *J. Fluid Mech.* 702, 239-264. doi:10.1017/jfm.2012.174. Bibliographic VERIFIED; text not read (the gamma definition is read in Hyman 2026 instead).

---

## 2. tau = Delta V / V0 (Hyman 2026 Eq. 26)

**VERIFIED.** Hyman et al. 2026, Sec. 3 (p. 7): "we introduce a dimensionless parameter which acts as a proxy for time defined by the total dissolved volume in the system,"
$$ \tau = \Delta V_\mathrm{tot}/V_0, \tag{26} $$
"where V0 (m^3) is the initial total volume of the fracture connections and ΔV_tot (m^3) is the total volume dissolved." Snapshots tau = 0, 0.1, 0.2, 0.5, 1.0. (Fixed-rate flow Q0, constant total flow.)
**Our mapping:** V0 = initial open pore volume (phi0 x cell volume summed); Delta V = n_gyp,dissolved V_gyp - n_cal,formed V_cal = net open-volume gain. In Hyman's model fractures are open channels, so volume dissolved = open volume gained and V0 = initial open volume, the same role. Differences: (a) ours includes calcite taking volume back (coupled runs), absent in Hyman 2026 (dissolution only); (b) ours reaches ~9, Hyman only to 1; (c) Hyman's V0 is aperture volume, ours is mineral-filled porosity. Label our tau "tau (Hyman's definition applied to net open volume)".

Reference: Hyman, J.D., Szawello, T., Kang, P.K., Szymczak, P. (2026). Effects of dissolution regimes on flow channelization and solute transport in 3D fracture networks: insights from graph-based reactive transport modeling. *J. Geophys. Res. Solid Earth* 131(3), e2025JB033004. doi:10.1029/2025JB033004. VERIFIED (text; reference list entry).

---

## 3. Pore volumes injected as clock; one pore volume per year

**Partly VERIFIED.** Hyman et al. 2024 (G-cubed 25(7), e2024GC011550), Sec. 2.2: "A constant volumetric flow rate is injected into the inflow boundary of the domain. The flow rate is equal to the initial volume of each fracture network per year, for example, it is network-dependent... Even though the volume of the network increases due to dissolution, this flow rate is held constant." Initial porosity: "uniform fracture porosity of 0.01"; "we set [phi0] to 0.01".
$$ \mathrm{PV}=\frac{Q\,t}{V_{p0}} ,\qquad Q=V_{p0}/(1\ \mathrm{yr}) \Rightarrow \mathrm{PV}=t/\mathrm{yr}$$
**Caveats:** (i) "initial volume of each fracture network" is not defined as pore volume or bulk fracture volume (finding 4). (ii) Hyman 2024 IJGGC (the chemistry source) uses a *sampled* Q (Table 1: 1e-9 to 1e1) and run time of 10 years, not 1 PV/yr (VERIFIED). So the convention is from G-cubed (quartz) only; IJGGC supplies the chemistry. (iii) PV as a clock is standard (V_inj/V0 in Szymczak & Ladd 2009 Fig. 16, item 1).

Reference: Hyman, J.D., Navarre-Sitchler, A., Sweeney, M.R., Pachalieva, A., Carey, J.W., Viswanathan, H.S. (2024). Quartz dissolution effects on flow channelization and transport behavior in three-dimensional fracture networks. *Geochem. Geophys. Geosyst.* 25(7), e2024GC011550. doi:10.1029/2024GC011550. VERIFIED (text; reference list entry in Hyman 2026).

---

## 4. Participation ratio and our volume-weighted form

**Origin: VERIFIED as cited by Maillot and Hyman.**
- Bell, R.J., Dean, P., Hibbins-Butler, D.C. (1970). Localization of normal modes in vitreous silica, germania and beryllium fluoride. *J. Phys. C: Solid State Phys.* 3(10), 2111-2118. doi:10.1088/0022-3719/3/10/013 (as in Hyman 2026 reference list; Crossref not checked).
- Edwards, J.T. & Thouless, D.J. (1972). Numerical studies of localization in disordered systems. *J. Phys. C* 5(8), 807-820. doi:10.1088/0022-3719/5/8/007 (Hyman 2026 reference list).
- Note: Maillot et al. 2016 cite "Bell and Dean (1970), Atomic vibrations in vitreous silica, Discuss. Faraday Soc. 50, 55-61, doi:10.1039/DF9705000055", a different Bell & Dean paper than Hyman cites. Cite the J. Phys. C one only if you follow Hyman, otherwise the Faraday Discussions one for the original.
- Use for flow localisation: Maillot 2016 Eq. 8 (item 5); Hyman 2020 also defines a particle-based "fracture participation ratio" pi (Sec. 2.3.3; VERIFIED in text, equation image not rendered); Hyman 2026 Eq. 41 cites Andrade et al. 1999, Davy et al. 1995/2010 for geoscience uses.

**Our form (BRIEF "Measures"):**
$$ \mathrm{PR}_V=\frac{\big(\sum_f Q_f\big)^2}{\sum_f Q_f^2/w_f},\qquad w_f=V_f/\sum V $$
Algebra check (VERIFIED): if Q_f proportional to w_f, PR_V = 1; if one fracture carries all flow, PR_V = w_f. It is the weighted inverse participation ratio with weights w_f, and is identical to the flux-density form of d_Q/P32 with S_f -> V_f. **It is our extension (intersection/volume weighting), not a published quantity; label it so** (PROJECT_CONTEXT rule).

---

## 5. Active surface area d_Q

**VERIFIED (formula; with the caveat in finding 3).**
Maillot, J., Davy, P., Le Goc, R., Darcel, C., de Dreuzy, J.-R. (2016). Connectivity, permeability, and channeling in randomly distributed and kinematically defined discrete fracture network models. *Water Resour. Res.* 52(11), 8526-8545. doi:10.1002/2016WR018973. Eq. (8), p. 12 (image inspected):
$$ d_Q=\frac{1}{V}\cdot\frac{\left(\sum_f S_f\,Q_f\right)^2}{\sum_f S_f\,Q_f^{2}} $$
Quote: "where the surface of fracture S_f is weighted by the fracture flow Q_f. The ratio in the right side of equation (8) is a measure of the portion of the total fracture surface, where flow is significant. d_Q can be directly compared with the fracture density p32... d_Q does not depends on the flow intensity".
Hyman 2024 (Eq. 14), Hyman 2026 (Eq. 41) and Hyman 2020 (Eq. 6) reproduce it, adding: "Q_f is half the absolute total volumetric flow rate exchanged by a fracture with its neighbors" and V the domain volume. Reported as 100 x d_Q/P32 (G-cubed: 55 % unreacted, 28 % dissolved; JGR 2026: ~37 % initial).

**Mapping to the brief's form.** With q_f = Q_f/S_f:
$$ \frac{(\sum S_f q_f)^2}{\sum S_f\ \sum S_f q_f^2}=\frac{(\sum Q_f)^2}{\sum S_f\ \sum Q_f^2/S_f}=\frac{V\,d_Q^{[q\ \mathrm{read\ as}\ Q_f]}}{\sum S_f}=\frac{d_Q}{P_{32}} $$
So the identity in the request **holds algebraically** (VERIFIED), but the left side is d_Q/P32 for a flux-density reading, not d_Q, and not the literal published formula, which inserts the *flow* Q_f (not flux) in S_f Q_f. The two give different numbers unless S_f is uniform. The brief's own note ("older script used Q_f in place of q_f; corrected") therefore moved away from the literal text. Which one dfnWorks computes is UNVERIFIED. Recommended wording: "d_Q after Maillot et al. (2016), evaluated with the specific discharge q = Q/S as the weight, i.e. an area-weighted participation ratio (equal to d_Q/P32)". Quote both values if cheap.

Hyman 2020 reference: Hyman, J.D. (2020). Flow channeling in fracture networks: characterizing the effect of density on preferential flow path formation. *Water Resour. Res.* 56(9), e2020WR027986. doi:10.1029/2020WR027986. VERIFIED (accepted manuscript text; Crossref). **Not Front. Phys.**

---

## 6. Longitudinal dispersion from t16/t84

**VERIFIED (Eq. B1) and VERIFIED (derivation).**
Hyman 2026, Appendix B: "To estimate the longitudinal dispersion of the breakthrough curves, we use the method presented by Sahimi (2011). This method uses the solution to the advection-dispersion equations with constant coefficients to back out an effective longitudinal dispersion coefficient D_L via the equation"
$$ D_L=\frac{1}{8}\left(\frac{L_0-v\,t_{0.16}}{\sqrt{t_{0.16}}}-\frac{L_0-v\,t_{0.84}}{\sqrt{t_{0.84}}}\right)^{2}, \tag{B1} $$
"where v is a constant velocity, t_* = F^{-1}(*) is the time at which the CDF is equal to *, and L0 = 25 m is the domain length. We take v to be the median particle velocity defined as v = L0/t_0.5." Computed on the aggregate CDF over the ensemble.
Independent derivation: for a Gaussian arrival in 1D ADE, (L - v t)/sqrt(2 D t) = +1 at the 16th percentile and -1 at the 84th; subtracting gives 2 sqrt(2D), so D = (1/8)[...]^2 (VERIFIED algebra).
Original source: Sahimi, M. (2011). *Flow and Transport in Porous Media and Fractured Rock*, 2nd ed., Wiley-VCH, Weinheim. doi:10.1002/9783527636693 (reference list, Hyman 2026). The page/equation in Sahimi is UNVERIFIED (book not read). Kreft & Zuber (1978), *Chem. Eng. Sci.* 33(11), 1471-1480, doi:10.1016/0009-2509(78)85196-3 is cited by Hyman 2026 only for flux-weighted vs resident injection (VERIFIED in Sec. 3.1), **not for B1**; it is the proper citation for the flux-vs-resident concentration distinction relevant to our Eulerian pulse.
Our use: L = 1000 m, v = L/t50, alpha_L = D_L/v (our extension). Note Hyman calls the network "first-order" and warns of a wide range of velocities.

---

## 7. Breakthrough curve, tail exponent, first-arrival normalisation

**VERIFIED (definitions), tail-fit window UNVERIFIED.**
- Hyman 2026 Eq. (30-33): t(a) = sum over traversed edges of L_ij/v_ij; $f(t)=\frac{1}{N}\int_{\Omega_a} da\,\delta[t(a)-t]$; "We refer to f(t) as the breakthrough curve (BTC)"; $F(t)=\frac1N\int da\,H[t-t(a)]$ (CDF); CCDF = 1 - F (Appendix C). Particles flux-weighted at the inlet (Eqs. 27-28; Kreft & Zuber 1978).
- Hyman 2024 Eq. (18): $\psi(t,L)=\frac1M\int_{\Omega_a} da\, m(a)\,\delta[\tau(a,L)-t]$, with m(a) set by incoming flow rate.
- Tail: Hyman 2026 Eq. (34) "$\lim_{t\to\infty} f(t)\propto t^{-\gamma}$"; "linear least-squares fitting of the power-law form... in log-log coordinates. Note that the corresponding slope on a log-log plot is -γ; here we report γ (not -γ)." The fit window is **not given** in the text, so our window [2 t_peak, t where f = 1e-2 f_peak] is our choice; state it. Hyman 2024: alpha = 2.48 for both unreacted and dissolved (fit method not described).
- Normalisation: Hyman 2026: "All times have been normalized by the first arrival time in the tau = 0.0 case"; peak times "normalized by the peak of the tau = 0.0 snapshot" (Fig. 6b). Hyman 2024 Fig. 5: left, first arrival of the unreacted network; right, first arrival in each simulation.
- Ours differs: Eulerian pulse on a frozen field (numerical dispersion, first arrival smeared) and a second normalisation by tau_res = V_p/Q. Both our adaptations; the second is needed because Q is held fixed while V_p grows x10.

---

## 8. Gamma (replacement solid-volume ratio) and the permeability ceiling

**Gamma: VERIFIED. Ceiling: our derivation, algebra VERIFIED.**
Budek, A., Szymczak, P., Kang, P.K. (2026). Fractures regulate coupled dissolution-precipitation dynamics: regime map, optimal fracture conductance, and clogging. *Earth Planet. Sci. Lett.* 690, 120163. doi:10.1016/j.epsl.2026.120163. VERIFIED. Eq. (9), Sec. 2.5:
$$ \Gamma=\frac{\chi_E\,\nu_E}{\chi_A\,\nu_A} $$
"where nu_E and nu_A are the molar volumes of the precipitating and dissolving phases, respectively, and chi_E and chi_A account for the corresponding stoichiometric factors. When Gamma > 1 ... void space tends to decrease and pathways seal; conversely, when Gamma < 1 (e.g., ... gypsum-anhydrite ...) porosity can reopen." Fo = k2/k1 (Eq. 8). Kinetics there: first-order, Eq. (4) R_diss = k1 c_B, R_prec = k2 c_C.
Original: Budek, A. & Szymczak, P. (2025). Channeling, clogging and permeability oscillations: different macroscopic regimes in mineral replacement. *J. Geophys. Res. Solid Earth* 130(6), e2024JB031081. doi:10.1029/2024JB031081 (Crossref VERIFIED; text not read, so whether Gamma is defined identically there is UNVERIFIED). Related: Budek, Szawello, Voller, Szymczak (2026). Retreat to advance: self-blocking enables efficient mineral replacement. *Geotechnique Lett.* 16, 124-130. doi:10.1680/jgele.25.00094 (Crossref).
**Ours:** Gamma = V_cal/V_gyp = 36.934/74.69 = 0.4945 (chi_E = chi_A = 1, one Ca per CaCO3 and per CaSO4.2H2O; molar volumes VERIFIED in IJGGC App. C).

**Ceiling (ours).** If all gypsum dissolves and every dissolved Ca re-precipitates in the cell as calcite, solid volume fraction falls from vf0 to Gamma vf0, so
$$ \phi_\infty=\phi_0+v_{f0}(1-\Gamma),\qquad \frac{k}{k_0}\Big|_{n=1}=\frac{\phi_\infty}{\phi_0}=1+\frac{v_{f0}}{\phi_0}(1-\Gamma). $$
Numbers (VERIFIED arithmetic): phi0 = 0.1, vf0 = 0.9: 1 + 9(0.5055) = 5.55; phi0 = 0.05, vf0 = 0.95: 1 + 19(0.5055) = 10.6; gypsum-only: 1/phi0 = 10 and 20. Not a published result; Budek's statement that Gamma < 1 allows reopening is the qualitative support. It is an upper bound that needs complete in-place re-precipitation (the brief reports 5.35-5.41 achieved).

---

## 9. k-phi in PFLOTRAN, TST rate law

**VERIFIED (PFLOTRAN Theory Guide, Hyman papers).**
- Porosity: $\phi=1-\sum_m \phi_m$ (Theory Guide Eq. 28; Hyman 2024 Eq. 5).
- Permeability (Theory Guide Eqs. 30-32; Hyman 2024 Eqs. 6-7; Hyman 2024 IJGGC Eqs. A.8-A.9):
$$ k=k_0\,f(\phi,\phi_0,\phi_c,n),\qquad f=\begin{cases}\left(\dfrac{\phi-\phi_c}{\phi_0-\phi_c}\right)^{n}, & \phi>\phi_c\\[4pt] f_{\min}, & \phi\le\phi_c\end{cases} $$
"phi_c refers to a critical porosity below which the permeability is assumed to be constant with scale factor f_min and phi_0 is the initial porosity" (Hyman 2024, which sets phi0 = 0.01). The PFLOTRAN input cards PERMEABILITY_POWER (= n) and PERMEABILITY_CRITICAL_POROSITY (= phi_c) refer to "UPDATE_PERMEABILITY in users manual" (documentation.pflotran.org material_property_card); the card text itself gives no formula. The exponent value used in Hyman 2024 IJGGC is not stated in the extracted text (UNVERIFIED). Ours: phi_c = 0, n = 1 gives k/k0 = phi/phi0 (the card setting `PERMEABILITY_POWER 1` in deck_gypsum_calcite.py; note the reference phi0 is the MATERIAL porosity, per memory).
- Surface area (Theory Guide Eq. 34; Hyman IJGGC Eq. A.10): $A_m=A_m^0\,(\phi_m/\phi_m^0)^n\,\big((1-\phi)/(1-\phi_0)\big)^{n'}$, "typical value for n of 2/3".
- TST rate: Hyman IJGGC Eq. (A.4) $r_m=-A_m k_m\,(1-Q_m/K_m)$, "dissolution when Q_m/K_m < 1"; Hyman 2024 Eq. (3) for quartz: $R=k_{qz}A\,(1-[\mathrm{SiO_2(aq)}]/K_{eq})$. PFLOTRAN general form (Theory Guide Eq. 19): $I_m=-A_m\sum_l k_{ml}\,\mathcal P_{ml}\,|1-(K_mQ_m)^{1/\sigma_m}|^{\beta_m}\,\mathrm{sign}(1-K_mQ_m)$ (reconstructed from the garbled page; PFLOTRAN's K_m Q_m is the inverse ratio to Hyman's Q/K; sign convention "positive for precipitation").
- Kinetics numbers: IJGGC Table 1: k_gypsum 1.2e-8 to 1.62e-3 (mol m^-2 s^-1, "k' denotes LHS in log-space"); k_calcite 2e-9 to 5e-5; gypsum surface area 486 to 4670 (units not in extracted text). So k_gyp = 1.62e-3 and k_cal = 2.29e-5 are inside the sampled ranges (VERIFIED). **The 750 m^2/kg specific surface in the brief is not in the IJGGC Table (486-4670, units unclear): UNVERIFIED.** Table 2 brine: Ca 0.015648 M initial; injected CO3 0.5 M, Na 1.0 M, pH 7.07 -> 11.39 (VERIFIED).
- Lichtner, P.C., et al. (2015). PFLOTRAN User Manual (and Theory Guide), documentation.pflotran.org. Cited by Hyman for the code (VERIFIED as cited).

---

## 10. Damkohler definitions

**Hyman 2026 Eqs. 24-25: VERIFIED.** Hyman 2026 Sec. 2.4:
$$ \mathrm{Da}=\frac{2\,k\,w_0 L_0/Q_0}{1+2kb_0/(D\,\mathrm{Sh})},\qquad G=\frac{2kb_0}{D\,\mathrm{Sh}} \tag{24, 25} $$
"b0 and w0 the average initial aperture and fracture width, and L0 the total length of the network." Effective rate k_eff = k/(1 + 2kb/(D Sh)) (Eq. 12), k in m/s, Sh = 8; "G plays a similar role to the Thiele modulus". Da values 2e-4, 2e-3, 2e-2; G 0.1, 1, 5.

**Our per-fracture form** $\mathrm{Da}_f=\dfrac{k\,a\,V_f}{Q_f\,c_\mathrm{sat}}$ (mol m^-2 s^-1 x m^2 m^-3 x m^3 / (m^3 s^-1 x mol m^-3), dimensionless): since TST gives r = (k/c_sat)(c_sat - c), k' = k/c_sat is the first-order velocity constant, and a V_f is the reactive area, so Da_f = k' A_react / Q_f. Compare Hyman: 2 k w0 L0 is k times total reactive wall area (two walls) over Q0. Hence Da_f is Hyman's Da with **G = 0** (no Sherwood/diffusive limitation) applied to **one fracture** (A_react = a V_f, flow Q_f) instead of the network (L0, Q0). Not identical to the published network Da; it is a per-fracture analogue of Szymczak & Pachalieva-type fracture Da (memory: "published Da only"). Mapping is our derivation (VERIFIED algebra).
**Other published Da in the chemistry source:** IJGGC App. C Eq. (C.6-C.8): advective Da_I = r/v (extraction garbled) with r = k V_m (k mol m^-2 s^-1 times molar volume = velocity), diffusive Da_II = r L/D_m, Pe = vL/D_m; the authors state "little to no evidence that these dimensionless variables accounted for variation in any of the QoIs". Szymczak & Ladd 2009 use Da = k/(h0-based) with Pe Da = k h0/D (VERIFIED, Eq. 18 text).

---

## 11. Supporting citations for the "known" statements

| Statement | Source | Status |
|---|---|---|
| Channels follow the initial network structure; structural heterogeneity (lengths, connectivity) survives dissolution | Hyman 2026: "in the channeling regime... Several parallel inlet-to-outlet channels enlarge along their entire length"; "Atτ=0.0 the networks are already strongly channelized, f50% ≈ 0.8"; "uniform dissolution can equalize apertures, but the chief source of heterogeneity in a DFN, the wide range of pathway lengths, remains." Szawello et al. 2026 abstract: "uniform dissolution cannot eliminate heterogeneity resulting from the network topology"; the quenched disorder is "a structural heterogeneity that dissolution can modify only marginally"; "in the channeling regime, initially existing flow paths are uniformly enlarged along their entire length" | VERIFIED (text) |
| Szawello, T., Hyman, J.D., Kang, P.K., Szymczak, P. (2026). Structural barriers to complete homogenization and wormholing in dissolving porous and fractured rocks. *Int. J. Rock Mech. Min. Sci.* 200, 106431. doi:10.1016/j.ijrmms.2026.106431 (arXiv:2602.06279) | Crossref + arXiv text | VERIFIED |
| Heterogeneity partly erased by reaction | Hyman 2026 (Da = 2e-4 mild homogenization, d_Q increases); Szawello 2026 ("cannot eliminate", i.e. partial). Our "partly" wording is supported; "erased" is not | VERIFIED |
| Heterogeneity is a prerequisite for channeling | Hyman 2026 citing Menke et al. 2023 and Szawello et al. 2024 (GRL 51(20), e2024GL109940, doi:10.1029/2024GL109940) | VERIFIED (as cited) |
| SKB Forsmark FFM01 hydrogeological DFN | SKB TR-10-52 (2010), *Data report for the safety assessment SR-Site*, Table 6-75 (p. 337): sets NS, NE, NW, EW, HZ; Fisher kappa 17.8, 14.3, 12.9, 14.0, 15.2; size model (r0 = 0.038 m, k_r = 2.50, 2.70, 3.10, 3.10, 2.38); valid interval (r0, 564 m); P32,open(200-400 m) = 0.142, 0.345, 0.133, 0.081, 0.316 | VERIFIED (page image inspected). Brief's kappa 12.9-17.8 and k_r 2.38-3.10 match. Radii 15-564 m is our truncation; T parameters see finding 5 |
| Geological DFN (basis for the hydro-DFN) | Fox, A., La Pointe, P., Hermanson, J., Oehman, J. (2007). *Statistical geological discrete fracture network model, Forsmark modelling stage 2.2.* SKB R-07-46, Svensk Kaernbraenslehantering AB, Nov 2007. (Authors and title VERIFIED in TR-10-52 reference list and SKB search result.) Note the hydro-DFN above is from the hydrogeological work cited in TR-10-52 (Follin et al.), not R-07-46; I did not read R-07-46 | Bibliography VERIFIED; content UNVERIFIED |
| dfnWorks | Hyman, J.D., Karra, S., Makedonska, N., Gable, C.W., Painter, S.L., Viswanathan, H.S. (2015). dfnWorks: a discrete fracture network framework for modeling subsurface flow and transport. *Comput. Geosci.* 84, 10-19. doi:10.1016/j.cageo.2015.08.001 | VERIFIED (Crossref) |
| Graph flow on DFNs | Hyman, J.D., Hagberg, A., Srinivasan, G., Mohd-Yusof, J., Viswanathan, H. (2017). Predictions of first passage times in sparse discrete fracture networks using graph-based reductions. *Phys. Rev. E* 96(1), 013304. doi:10.1103/PhysRevE.96.013304. Hyman, J.D., Hagberg, A., Osthus, D., Srinivasan, S., Viswanathan, H., Srinivasan, G. (2018). Identifying backbones in three-dimensional discrete fracture networks: a bipartite graph-based approach. *Multiscale Model. Simul.* 16(4), 1948-1968. doi:10.1137/18M1180207 | VERIFIED (Hyman 2026 reference list; Crossref not rerun) |
| Graph-based reactive transport on DFN | Hyman et al. 2026 JGR (item 2); pipe network, k-clique per fracture, Reynolds flow | VERIFIED |
| First coupled gypsum-calcite DFN | Hyman, J.D., Murph, A.C., Boampong, L., Navarre-Sitchler, A., Carey, J.W., Stauffer, P., Viswanathan, H.S. (2024). Determining the dominant factors controlling mineralization in three-dimensional fracture networks. *Int. J. Greenh. Gas Control* 139, 104265. doi:10.1016/j.ijggc.2024.104265 | VERIFIED (title, volume, article, DOI in text). The author list printed is "Hyman, Murph, Boampong, Navarre-Sitchler, Carey, Stauffer, Viswanathan" |
| Coupled model Hyman 2026 TiPM | Hyman, Dell'Oca, Navarre-Sitchler, Viswanathan (2026). *Transp. Porous Media* 153, article 100. doi:10.1007/s11242-026-02352-y. Crossref title: "Modeling Coupled Dissolution-Precipitation and Flow in Fractured..." | VERIFIED (Crossref) |
| **BiGraFV** | No publication found in this search (no reference in any text read). Treat as **unpublished**; cite as "this work / in preparation". A manuscript exists in the project (Manuscript_1CES.pdf in Downloads, not read). | UNVERIFIED |

---

## Full citation list in one place
- Bell, R.; Dean, P.; Hibbins-Butler, D. (1970). J. Phys. C 3(10), 2111-2118. doi:10.1088/0022-3719/3/10/013.
- Budek, A.; Szymczak, P. (2025). J. Geophys. Res. Solid Earth 130(6), e2024JB031081. doi:10.1029/2024JB031081.
- Budek, A.; Szymczak, P.; Kang, P.K. (2026). Earth Planet. Sci. Lett. 690, 120163. doi:10.1016/j.epsl.2026.120163.
- Edwards, J.T.; Thouless, D.J. (1972). J. Phys. C 5(8), 807-820. doi:10.1088/0022-3719/5/8/007.
- Fox, A.; La Pointe, P.; Hermanson, J.; Oehman, J. (2007). SKB R-07-46.
- Fredd, C.N.; Fogler, H.S. (1998). AIChE J. 44(9), 1933-1949. doi:10.1002/aic.690440902.
- Golfier, F. et al. (2002). J. Fluid Mech. 457, 213-254. doi:10.1017/S0022112002007735.
- Hyman, J.D. (2020). Water Resour. Res. 56(9), e2020WR027986. doi:10.1029/2020WR027986.
- Hyman, J.D.; Hagberg, A.; Srinivasan, G.; Mohd-Yusof, J.; Viswanathan, H. (2017). Phys. Rev. E 96, 013304.
- Hyman, J.D.; Hagberg, A.; Osthus, D.; Srinivasan, S.; Viswanathan, H.; Srinivasan, G. (2018). Multiscale Model. Simul. 16(4), 1948-1968.
- Hyman, J.D.; Karra, S.; Makedonska, N.; Gable, C.W.; Painter, S.L.; Viswanathan, H.S. (2015). Comput. Geosci. 84, 10-19.
- Hyman, J.D.; Murph, A.C.; Boampong, L.; Navarre-Sitchler, A.; Carey, J.W.; Stauffer, P.; Viswanathan, H.S. (2024). Int. J. Greenh. Gas Control 139, 104265.
- Hyman, J.D.; Navarre-Sitchler, A.; Sweeney, M.R.; Pachalieva, A.; Carey, J.W.; Viswanathan, H.S. (2024). Geochem. Geophys. Geosyst. 25(7), e2024GC011550.
- Hyman, J.D.; Szawello, T.; Kang, P.K.; Szymczak, P. (2026). J. Geophys. Res. Solid Earth 131(3), e2025JB033004. Data: doi:10.5281/zenodo.18603084.
- Kreft, A.; Zuber, A. (1978). Chem. Eng. Sci. 33(11), 1471-1480.
- Lichtner, P.C. et al. (2015). PFLOTRAN User Manual / Theory Guide, documentation.pflotran.org.
- Maillot, J.; Davy, P.; Le Goc, R.; Darcel, C.; de Dreuzy, J.-R. (2016). Water Resour. Res. 52(11), 8526-8545. doi:10.1002/2016WR018973.
- Sahimi, M. (2011). Flow and Transport in Porous Media and Fractured Rock, 2nd ed., Wiley-VCH. doi:10.1002/9783527636693.
- SKB (2010). Data report for the safety assessment SR-Site. TR-10-52.
- Szawello, T.; Hyman, J.D.; Kang, P.K.; Szymczak, P. (2026). Int. J. Rock Mech. Min. Sci. 200, 106431. doi:10.1016/j.ijrmms.2026.106431.
- Szymczak, P.; Ladd, A.J.C. (2009). J. Geophys. Res. 114, B06203. doi:10.1029/2008JB006122.
- Szymczak, P.; Ladd, A.J.C. (2012). J. Fluid Mech. 702, 239-264. doi:10.1017/jfm.2012.174.

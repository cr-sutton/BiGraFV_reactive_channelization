# Literature for WORMHOLE_CHECKS Check 1: regime map of dissolving fractures (compact / wormhole / uniform)

Checked 4 Nov 2026. Sources read as text, not from summaries:
- LI = Li, Hu, Szawello, Yang, Chen, Szymczak, Zhou 2026, GRL 53, e2026GL123899. Local text
  `.../scratchpad/dl/Geophysical_Research_Letters___2026___Li___From_Core_to_Field__Pattern_Selection_in_Dissolving_Fractures.pdf.txt`.
  Page numbers are the journal's "x of 11". The text extraction drops spaces, minus signs and superscripts; where an equation is
  ambiguous this is stated. Supporting Information (Tables S1-S3, Figs S8-S14, Text S3) was NOT available.
- SL09 = Szymczak & Ladd 2009, JGR 114, F02021 (arXiv 0902.1374v2), `.../scratchpad/ref/sl2009.txt`.
- SL12 = Szymczak & Ladd 2012, JFM 702, 239-264 (arXiv 1204.0917), downloaded to `.../scratchpad/lit2/sl2012.txt`.
- SL18 = Starchenko & Ladd 2018, WRR 54, 7946-7959, doi 10.1029/2018WR022948. Accepted manuscript (OSTI 1484138) at
  `.../scratchpad/lit2/sl2018.txt`. Equation numbers below are the manuscript's; the final version may differ.
- (scratchpad = /private/tmp/claude-501/-Users-collin-Projects-bipartite-pflotran-src-alpha-study/4bb44bc2-48f5-4f4b-bcf1-243f8b14a913/scratchpad)

## 1. Li et al. 2026: the two groups, the boundaries, the validated range

All VERIFIED unless marked. n_s = number of reactive walls (n_s = 2 in their simulations and stability analysis, n_s = 1 in their salt
experiments, p3). q0 is the initial flow rate per unit fracture width (m2/s); the text calls it "the initial flow rate" and Pe = q0/Dm
being dimensionless implies per unit width. SL09 Eq. 26 (Pe = Q/(W D)) and SL18 Fig. 2 caption (q0 = Q/W) confirm this reading.

| Quantity | Definition in the paper | Where |
|---|---|---|
| Pe | `Pe = q0 / Dm` (q0 = Q/W, so Pe = v b / Dm with v = Q/(bW); b cancels) | Eq. 1, p3 |
| second Damkohler | `Da_II = ks b0 / Dm` (b0 initial mean aperture) | Eq. 2, p3 |
| effective rate | `keff(b) = ks / (1 + 2 ks b / (Dm Sh))` (depth-averaged model) | Sec. 2.2, p2 |
| penetration length | `lp = 1/kappa`, `kappa = q0/(2 Dm b0) (sqrt(1+4 Lambda^2) - 1)` (see note) | Eq. 3, p4 |
| diffusive-to-convective ratio | `Lambda = sqrt(n_s keff Dm b0 / q0^2)`; "ratio of the transverse diffusion length lt = [Dm b0/(n_s keff)]^(1/2) to the convective penetration length lp = q0/(n_s keff)" | Eq. 4, p4-5 |
| length-based effective Da | `Da_eff,L^-1 = 1/(kappa L) = q0/(n_s keff L)`, i.e. `Da_eff,L = n_s keff L / q0`; "= lp/L" | Eq. 5 p6; p8 |
| the two axes of the phase diagram | `Lambda^-1 = lp/lt` (no L) and `Da_eff,L^-1 = lp/L` | p8 (Sec. 3.2.3), Fig. 3a |

Note on Eq. 3: the extracted text shows "q0 / (n_s Dm b0)" in the prefactor; the quadratic Dm b0 kappa^2 + q0 kappa - n_s keff = 0 gives
a prefactor q0/(2 Dm b0), and SL12 Eq. 16/20 (kappa h0 = (Pe/2)(sqrt(1+4H)-1), with H = Da_eff/Pe = Lambda^2 for n_s = 2) agrees.
Eq. 3 as printed is therefore probably a text-extraction artefact. It does not matter for the boundaries: Eq. 5 and Eq. 6 are used directly.

Boundaries (VERIFIED, quotes):
- Uniform: "We take omega'_max < 0.1 as the operational criterion for a nearly flat dispersion curve. This condition is satisfied for kappa L <= 3.6"
  (p6) and "Da_eff,L^-1 = 1/(kappa L) = q0/(n_s keff L) ~ 0.278 (5)" (p6). Fig. 2 caption: "Da_eff,L^-1 >= 0.278". Uniform when
  `Da_eff,L^-1 >= 0.278`, i.e. `Da_eff,L <= 3.6`.
- Caveat they give: "the value Da_eff,L^-1 = 0.278 should be interpreted as an upper bound for the wormholing-to-uniform transition" (p6; derived
  in the reaction limit, "finite transport limitation reduces the growth rates").
- Compact: "omega_max < 0.1 ... This criterion yields the threshold Lambda^-1 ~ 0.237 (6)" (p6-7). Compact when `Lambda^-1 <= 0.237` (Fig. 2 caption).
  Caveat: "Finite transport limitation shifts the transition slightly toward larger Lambda^-1, so this value should be regarded as a lower bound for the
  compact-to-wormholing transition" (p7).
- Fig. 3a caption (p8): "The transition to uniform dissolution occurs at Da_eff,L^-1 = 0.278, whereas the transition from compact dissolution to
  wormholing occurs at Lambda^-1 = 0.237." Text p8: "The horizontal boundary Da_eff,L^-1 ~ 0.278 marks the onset of uniform dissolution, whereas
  the vertical boundary Lambda^-1 ~ 0.237 separates compact dissolution from wormholing."
- Between them: wormholing = `Lambda^-1 > 0.237` and `Da_eff,L^-1 < 0.278`.
- How L enters: only through Da_eff,L (Eq. 5). Compact/wormhole boundary is "length-independent" (p3-4, p7). Empirically "at fixed Da_II = 0.1 the
  critical Peclet number increases in proportion to L ... at fixed Pe = 300 the critical Da_II decreases in proportion to L^-1" (p3).
- Not stated in the text (UNVERIFIED): which regime wins in the corner Da_eff,L^-1 >= 0.278 and Lambda^-1 <= 0.237. This needs lt > 1.17 L, which is
  implausible for our fractures (lt is of order b).
- Naming: Li's "compact dissolution" is described as "dissolution remains confined near the inlet" and "the dissolution front remains nearly planar" (p4, p6). This
  matches SL18's "face dissolution". SL18's "compact wormhole" is a wormhole sub-type and belongs to Li's "wormholing". Li does not state this mapping, so the
  mapping is UNVERIFIED.
- Optimal-flow result (not needed for regime map): Psi = Lambda^-1 b0/L = beta = 0.0123, Eq. 7 (p9). Not used.

Validated range (what the text states):
- Fracture length L = 0.1 to 30 m (abstract; p7 "over fracture lengths ranging from 0.1 to 30 m"); 273 simulations with L = 0.1, 0.3, 1, 3, 10, 30 m
  (Sec. 2.2, p3), W = L/2, and extra widths at L = 0.1 m.
- Pe = 1.4 to 1000 ("Pe spans three orders of magnitude, from 1.4 to 1,000", p3, the experiments). Diagrams were scanned at fixed Da_II = 0.1 (Fig. 1b) and
  fixed Pe = 300 (Fig. 1c).
- Experiments: L = 0.1 m (b0 ~ 200 um) and L = 0.3 m (b0 ~ 400 um); NaCl, Dm = 1.61e-9 m2/s. Data from Detwiler 2003 and Elkhoury 2013 are added (p8).
- UNVERIFIED: the Da_II range, the Da_eff,L range, the Lambda range and the simulation apertures b0 (so the L/b0 range). They are in Tables S1-S3 and
  Figs S8-S14, which I could not obtain. The main text and the extracted figure captions print no axis limits.
- Single fractures only. The paper's conclusion: "further work is needed to test the framework in multi-fracture systems" (p10).
- Sherwood number: the text says Sh "depends on the number of reactive surfaces" (p2-3) but prints no value, so UNVERIFIED. Use SL12's Sh = 8 (below).

## 2. Starchenko & Ladd 2018 (and Starchenko et al. 2016 as cited there)

- Definitions (VERIFIED, manuscript Eqs 11, 12, 15-17): `Pe = Q/(W D) = q0/D` (Eq. 11); `Da_II = k h0/D` (Eq. 12); `Da = k L/q0 = Da_II L/(Pe h0)` (Eq. 15);
  `keff = k/(1 + 2 Da_II/Sh)`, Sh ~ 8 (Eq. 16); `Da_eff = n keff L/q0` (Eq. 17), n = 1 or 2 reactive surfaces. Sh = 7.54 is used "when the kinetics
  are clearly transport limited", Sh = 8 otherwise (Appendix A).
- Critical Da (VERIFIED): "the boundary between necked wormholes and uniform dissolution is largely independent of Pe [SL09], with the transition to
  uniform dissolution around Da_eff = 4 independent of the fracture length to aperture ratio" (Sec. 7). This equals Li's kappa L = 3.6 (0.278 = 1/3.6).
- Scaling with L (VERIFIED): "As the length of the fracture increases, the location of the phase boundary occurs at smaller Da_II (Fig. 4a)... the
  length-dependence ... can be almost eliminated by defining a Damkohler number on the scale of the fracture length, kL/D"; with k_eff L/q0 "the phase boundary
  becomes independent of Pe and system size (Fig. 4d), except at the lowest Peclet number (Pe = 2)" (Sec. 5). So critical Da_II is proportional to 1/L at fixed Pe.
  The boundary location was determined to 10 % at small Pe and 20 % at Pe = 200.
- Range they simulated: L/h0 = 500, 1000, 2000 (W = 250 h0), Pe = 2 to 200 (Sec. 5, Fig. 4), Da_II from 0.01 to 100 (Sec. 4). They also use 3D rough-fracture
  runs of Starchenko et al. 2016 at Pe = 40, Da_II = 0.5 with L = 10^3 h0 and 10^5 h0 (Sec. 7). Aspect ratios up to 10^5 are quoted.
  Experiments: L/h0 up to 2000-4000 (Garcia-Rios 2015).
- Face to compact-wormhole boundary: "at small flow rates (Pe < 4) and large reaction rates (Da_II > 1) the wormhole grows extremely slowly" (Sec. 4);
  at Pe = 2 "wormholes do not develop over the time scale of our simulations" (up to 37000 td); "the boundary between compact wormholes and face
  dissolution is [not] well defined" (Sec. 4, the manuscript has a garbled "Rather"). Compact to necked at Da_II = 1 occurs at Pe ~ 50. No closed-form boundary is given.
- Largest Da_eff in their data (Table A1, Garcia-Rios experiments C): face dissolution at Pe = 2.5, Da_eff = 3700; compact at Pe = 12, Da_eff = 880-890; necked at Pe = 62,
  Da_eff = 190; uniform at Pe = 740, Da_eff = 13-18. These are experimental maxima in the main phase diagram (Fig. 6). The Fig. 6 axis range itself is not in the text
  (UNVERIFIED).
- Local-equilibrium bound (VERIFIED, Sec. 7): "The phase diagram is bounded from below by a straight line with slope Pe Da_eff^inf = n Sh L/(2 h0)... Da_eff^inf is the
  transport limit of Da_eff." This is keff -> D Sh/(2 h0), so Da_eff -> `n Sh L /(2 h0 Pe)`: at Da -> infinity, Da_eff is set by aspect ratio and Pe only.

## 3. Szymczak & Ladd 2009 and 2012: the underlying definitions

SL09 (VERIFIED):
- `Pe = v h / D` with `v = Q/(W h)` (Eq. 1 and text; Eq. 26 `Pe = Q/(W D)`), `Da = k/v` (Eq. 2), `Pe Da = k h/D` (Eq. 25), `Da = k h W / Q` (Eq. 27).
- `k_t = Sh D/d_h`, `d_h = 2h`, Sh = 7.54 (constant concentration) to 8.24 (constant flux), "Sh = 8" used (Eqs 30-31 and following text); `keff = k kt/(k + kt)` (Eq. 33);
  `Da_eff^-1 = Da^-1 + 2 Pe/Sh` (Eq. 34). "uniform dissolution can now be uniquely associated with small Da_eff" (Sec. V, Fig. 9).
- Fig. 9 axis values are not in the text, so SL09's own Pe-Da_eff numerical boundaries are UNVERIFIED. The text gives only sampled Pe = 1/2 to 128, Da^-1 = 0 to 160.
- Length: "in the wormholing regime, the results ... are insensitive to further increases in the length of the domain. However, in the uniform-dissolution regime, the overall length
  of the fracture is important... the distinction between uniform dissolution and surface inundation is merely a matter of scale" (Sec. IV, p11-12).

SL12 (VERIFIED):
- `Pe = q0/D` (Eq. 17); `G = 2 k h0/(D Sh)` (Eq. 14, the same G as Hyman's, `G = 2 k b0/(D Sh)`); `keff = k/(1+G)` (Eq. 8); `Da_eff = 2 keff h0/q0 = 2 k h0/((1+G) q0)` (Eq. 18);
  `H = Da_eff/Pe` (Eq. 19); `kappa h0 = (Pe/2)(sqrt(1+4H) - 1)` (Eq. 20), `kappa h0 = Da_eff` for convection-dominated H -> 0 (Eq. 21).
- Relation to LI and SL18 (derived by me from the equations above; consistent algebra, not a quote): Li's `Da_eff,L = n_s keff L/q0` equals SL12's Da_eff times L/h0 (n_s = 2), and Li's
  `Lambda^2` equals SL12's `H` (n_s = 2).
- Finite length: "for short fractures, (kappa L < 2), the growth rate is maximum at zero wavevector" (Sec. VI E); conclusions say "kappa L <= 3". Treated "only in the reaction limit (G -> 0)".
- Sh used in all numerical work: 8 (Sec. II).

## 4. The local-equilibrium limit (Da -> infinity)

- SL09 covers Da -> infinity explicitly (VERIFIED, Sec. IV): "Above a threshold Damkohler number, Da > 1, the erosion patterns are largely determined by the Peclet number. Additional data
  (not shown) demonstrates that there is no difference in dissolution patterns at Da = 1, Da = 10 and Da -> infinity, except at small Peclet numbers, Pe < 1." The Da -> infinity runs used an absorbing wall (C = 0).
  "For small Pe and large Da the reactant saturates near the injection face. After a fast initial dissolution of material at the fluid inlet, the reaction front propagates extremely slowly, as
  there is almost no unsaturated fluid penetrating inside the fracture." Fig. 11 caption: "at the two higher Peclet numbers (8, 32) we used Da = infinity, but at Pe = 2 we used Da = 0.1, since
  the channels do not form at Da = infinity in this case." Wormhole front extent in the mass-transfer-limited regime: lambda_x ~ h0 Pe/Sh (Sec. VI).
- So the answer depends on Pe: at Da -> infinity, face dissolution/inundation for Pe of order 1 or below (SL09: no channels at Pe = 2; SL18: face dissolution at Pe = 2, "Pe < 4 and Da_II > 1" extremely slow wormhole growth),
  and wormholes (compact then necked) at larger Pe. Uniform dissolution needs Da_eff <~ 4, and at Da -> infinity Da_eff -> n Sh L/(2 h0 Pe), so uniform needs `Pe >~ n Sh L/(8 h0)`, i.e. very large Pe for large L/h0.
- Li et al.: they say their depth-averaged model "captures both reaction-limited and transport-limited regimes" (p2) and that Elkhoury 2013 found "the dissolution regime shifts from reaction-limited to transport-limited" with length (p2), but
  they never discuss Da -> infinity or print an explicit statement on it. They say the thresholds Eq. 5 and Eq. 6 are from the reaction-limit analytics and are respectively an upper bound and a lower bound once transport limitation is present
  (quotes in Sec. 1). Whether their data populate Da_eff,L as large as ours: UNVERIFIED.
- SL12 treats G -> infinity (transport-limited) in the linear stability of a semi-infinite fracture (Fig. 2: "diffusive limit (G = infinity)"). "For wider apertures (G >> 1), diffusional transport of reactant across the aperture
  has a stabilizing effect"; the finite-length analysis is reaction-limited only.

## 5. Formulas for an analysis script, and where our values sit

Inputs per fracture: L (length along flow), b (hydraulic aperture), Q_f (fracture flow), W (width), D = 1e-9 m2/s, k (surface rate constant in m/s, i.e. the volumetric-area-scaled rate as used in forsmark_damkohler.py), Sh = 8, n_s = 2.

```
q0     = Q_f / W                                  # = v*b; m2/s
Pe     = q0 / D                                   # Li Eq.1, SL09 Eq.1/26, SL12 Eq.17
keff   = k / (1 + 2*k*b/(D*Sh))                   # Li Sec 2.2, SL12 Eq.8, SL18 Eq.16
G      = 2*k*b/(D*Sh)                             # SL12 Eq.14 (Hyman's G)
DaII   = k*b/D                                    # Li Eq.2, SL18 Eq.12
Da_effL     = n_s*keff*L/q0                       # Li Eq.5 (inverse), SL18 Eq.17, SL12 Da_eff * L/b
Da_effL_inv = 1/Da_effL                           # = lp/L ; uniform if >= 0.278
Lam_inv     = q0/sqrt(n_s*keff*D*b)               # Li Eq.4 inverse = lp/lt ; compact if <= 0.237
regime = 'uniform' if Da_effL_inv >= 0.278 else ('compact(face)' if Lam_inv <= 0.237 else 'wormhole')
# transport (Da -> inf) limit, keff -> D*Sh/(2b):  Da_effL = n_s*Sh*L/(2*b*Pe) ;  Lam_inv = Pe*sqrt(2/(n_s*Sh))
```
Priority in the overlap corner is not given by Li (UNVERIFIED), so flag it rather than choosing one.

Equivalence with the project's existing quantity: `forsmark_damkohler.py` computes `da_f = 2*keff*w*L/Q` (keff transport-corrected, with the R area factor). Since q0 = Q/w, this is exactly Li's / SL18's
Da_eff,L (n_s = 2), so Da_f ~ 1e7 can be read directly as Da_eff,L = 1e7 (lp/L ~ 1e-7). The code uses Sh = 8, D = 1e-9, as above. One difference to keep in mind: the
project's k includes the PFLOTRAN mineral surface-area factor R (about 90-190 here); Li and SL define k per unit flat wall area. With R = 1 the numbers below change by a factor of ~1.5 (Da_eff,L) because the rate is already transport-limited.

Illustration computed by me (NOT from the literature): for network `phase1/L2_r15_p4.0_sg1.0_seed1`, initial state, using `compute_literature_damkohler.state0` with fluxes rescaled to the run rate, L = w = sqrt(S) as in forsmark_damkohler.py, 665 flowing fractures
(Q > 1e-3 Q_total), gypsum k_lin, D = 1e-9, Sh = 8. Script: `.../scratchpad/lit2/illus.py` (not in the repo).

| Quantity | unweighted p10 / p50 / p90 | flow-weighted p10 / p50 / p90 |
|---|---|---|
| Pe = Q/(wD) | 0.06 / 0.18 / 0.93 | 0.25 / 1.4 / 4.8 |
| Da_eff,L (k with R) | 4.6e6 / 2.2e7 / 8.4e7 | 1.7e6 / 4.9e6 / 2.2e7 |
| Lambda^-1 (k with R) | 0.021 / 0.066 / 0.33 | 0.088 / 0.50 / 1.7 |
| L/b (b = sqrt(12 k_perm) = 8e-5 m) | 3.3e5 / 5.5e5 / 1.0e6 | 4.2e5 / 8.1e5 / 1.8e6 |
| L median 42 m (max 348 m) | | |

Position relative to the validated range:
- Da_eff,L ~ 1e6 to 1e8 vs the uniform threshold 3.6: Da_eff,L^-1 ~ 1e-7 to 1e-6, far on the non-uniform side of the horizontal boundary; the uniform regime is excluded by a
  factor of about 1e6. That conclusion does not depend on the exact Sh, n_s or the 0.278 value.
- That value of Da_eff,L is a far extrapolation. The largest Da_eff in the SL18 table is 3.7e3 (a lab experiment); the 3D rough-fracture simulations at L = 1e5 h0, Pe = 40, Da_II = 0.5 give Da_eff ~ 2e3 (my arithmetic from
  Eqs 16-17 with Sh = 8, n = 2). Li's Da_eff,L range is UNVERIFIED (SI). Our L/b ~ 5e5 exceeds SL18's quoted maximum aspect ratio of 1e5 and Li's L/b0 range
  (not stated, UNVERIFIED; for the experiments L/b0 = 500 and 750 only).
- Our L (median 42 m, tail to ~350 m) is above Li's 30 m maximum for the tail, and within 0.1-30 m only for the shorter fractures.
- Pe: unweighted median ~0.2, flow-weighted median ~1.4, flow-weighted p90 ~5. Li's experiments cover Pe = 1.4 to 1000 (simulations: only Da_II = 0.1 and Pe = 300 slices are quoted), SL18 covers Pe = 2 to 200, SL09
  covers Pe = 1/2 to 128. So most fractures by count, and a large share by flow, have Pe at or below the lowest validated value, where SL18 and SL09 report that face dissolution/inundation occurs and
  even the Pe-independence of the boundary fails ("except at the lowest Peclet number (Pe = 2)", SL18 Sec. 5; SL09 "except at small Pe, Pe < 1").
- Compact vs wormhole in our regime: Li's criterion Lambda^-1 <= 0.237 puts the unweighted median fracture in "compact", and the flow-weighted median (0.5) in "wormholing". In the transport limit Li's criterion reduces to Pe <= 0.237*sqrt(n_s Sh/2) = 0.67 (n_s = 2, Sh = 8),
  and Li call 0.237 a lower bound that transport limitation shifts upward. The explicit simulation results in the Da -> infinity limit put the transition at Pe of order 2-4 (SL09 no channels at Pe = 2; SL18 face dissolution
  at Pe = 2, extremely slow growth for Pe < 4). So the Li boundary and the SL results are consistent only if the shift is substantial. The honest statement is that for Pe between ~0.7 and ~4 the
  regime is uncertain (compact/face versus wormhole), and the published diagrams do not resolve it at Da_eff,L of 1e6 or more.
- The boundaries were derived and checked on single fractures with uniform or mildly rough apertures; the paper itself says multi-fracture networks remain untested (p10).

Recommended wording for the report and figure: "Uniform dissolution is excluded by the Li et al. criterion (Da_eff,L^-1 = lp/L ~ 1e-7, boundary 0.278). Our Da_eff,L (1e6-1e8) and L/b (~5e5) lie
outside the range for which the compact/wormhole/uniform boundaries were validated (L = 0.1-30 m; Da_eff up to ~4e3 in the Starchenko & Ladd experiments); the separation of compact/face dissolution from wormholing at these
values is an extrapolation and is Pe-dependent (Pe = 0.2-5 here, partly below the validated Pe range of 1.4-1000)."

## Claim verdict list
1. Li groups = Lambda^-1 = lp/lt and Da_eff,L^-1 = lp/L (Pe, Da_II are the plotted simulation controls): matches Eqs 4-5, Fig. 3 (VERIFIED).
2. Boundaries 0.278 (uniform) and 0.237 (compact/wormhole): Eqs 5-6 (VERIFIED), with the upper/lower-bound caveats on p6-7.
3. Validated L 0.1-30 m: abstract (VERIFIED); Pe 1.4-1000 (VERIFIED); Da, G, aperture ranges UNVERIFIED (SI); Sh value in Li UNVERIFIED.
4. Starchenko & Ladd critical Da: Da_eff = n keff L/q0 ~ 4 for uniform/wormhole, independent of Pe and L/h0 (VERIFIED, accepted manuscript). Critical Da_II proportional to 1/L (VERIFIED). Exception at Pe = 2.
5. SL09/SL12 definitions: VERIFIED (Eqs above). SL09's numerical Fig. 9 boundaries UNVERIFIED (no axis values in text).
6. Da -> infinity: SL09 explicit (Pe-dependent, "no difference ... except at Pe < 1"); SL18 gives the transport-limit line Pe Da_eff^inf = n Sh L/(2 h0); Li does not discuss it explicitly (UNVERIFIED).

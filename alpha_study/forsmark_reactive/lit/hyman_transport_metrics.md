# Hyman et al. transport metrics: how to reproduce on our runs

Sources read as text (PDFKit extraction, so the JGR equations are slightly garbled, quoted forms below are reconstructed from them):
- Q24 = Hyman et al. 2024 G-cubed 25(7) e2024GC011550 (quartz, 30 DFNs, unreacted vs dissolved, two states only).
- J26 = Hyman, Szawello, Kang, Szymczak 2026 JGR Solid Earth 131 e2025JB033004 (30 DFNs, 25x10x10 m, L0 = 25 m; Da in {2e-4,2e-3,2e-2}, G in {0.1,1,5}; snapshots tau = 0, 0.1, 0.2, 0.5, 1.0).
- Not checked: Hyman 2019/2020, Cvetkovic 1999 (only cited; formulas below come from Q24/J26 themselves).

## Method common to both
- Particle tracking is post-processing on a frozen, steady flow field at each snapshot ("Apertures ... are updated only between snapshots"; J26 s3.1). Purely advective, no diffusion, 1e5 particles (J26 below Eq. 28; Q24 s3.3).
- Flux-weighted injection on the inlet plane (J26 Eq. 27-28): Q0 = int_inlet da Q(a); n(a) = ceil(N Q(a)/Q0). Equivalent to Q24's m(a) proportional to inflow rate at a.
- Intersections: complete mixing, exit fracture chosen with probability proportional to outflow rate (J26 s3.1.2; Q24 s2).
- Time proxy (J26 Eq. 26): tau = dV_tot / V0, dissolved volume over initial fracture volume. Q24 has no tau, only unreacted vs final state.

## (1) Breakthrough curve
- Q24 Eq. 18: psi(t,L) = (1/M) int_{Omega_a} da m(a) delta[tau(a,L) - t]; m(a) distributed by incoming flow rate. tau(a,L) = int_0^{l(L)} dl'/||v(a,l')|| (Eq. 17).
- J26 Eq. 30-32: t_ij = L_ij/v_ij; t(a) = sum over traversed edges; f(t) = (1/N) int da delta[t(a) - t]. "We refer to f(t) as the breakthrough curve." CDF F(t) = (1/N) int da H[t - t(a)] (Eq. 33); CCDF = 1 - F (Appendix C, Fig. C1-C2).
- So the BTC is a travel-time PDF of flux-weighted particles = outflow mass-flux (flux-concentration) for a flux-weighted pulse injection, normalised to unit area. Plotted as PDF vs normalised time, mean (thick) plus 95 % CI over 30 realisations (Fig. 5), log-log in the figures (power-law tails shown; the extracted text gives no explicit axis statement, check the figure image).
- Time normalisation: J26 "All times have been normalized by the first arrival time in the tau = 0.0 case". Q24 Fig. 5: left panel normalised by first arrival of the unreacted network; right panel by first arrival in each network (all first arrivals coincide) to compare scaling shapes.

## (2) Peak arrival time
- J26 Fig. 6b: "peak arrival times are normalized by the peak of the tau = 0.0 snapshot". Mean over 30 realisations, error bars 1 std (text of Fig. 6 caption; PDFs use 95 % CI). Peak location method (mode of binned PDF) is not specified in the text.

## (3) Tail exponent
- J26 Eq. 34: lim_{t->inf} f(t) proportional to t^-gamma. "The tail exponent is obtained by linear least-squares fitting of the power-law form in Eq. 34 to the BTC tail in log-log coordinates ... we report gamma (not -gamma)." Fit is on the PDF, not the CCDF; the time window of the "tail" is NOT given in the text (unverified; ask authors or choose and document). For CCDF-based fits the exponent would be gamma-1.
- Q24: psi(t,L) proportional to t^-alpha, alpha = 2.48 for both unreacted and dissolved (right panel, after first-arrival normalisation); fit method not described.
- J26 at Da=2e-2 (tau >= 0.5) shows dual scaling: primary near-exponential decay then power law; a single fit then depends on the window.

## (4) Lagrangian quantities
- beta (Cvetkovic et al. 1999), Q24 Eq. 19: beta(a;L) = int_0^{l(L)} 2 dl' / ( b(a,l') ||v(a,l')|| ). Distribution defined as Eq. 18 with tau replaced by beta. Fig. 6 left: normalised by min beta of unreacted networks; right: by each network's min beta. b = hydraulic aperture.
- Tortuosity: Q24 Eq. 20: chi(a,L) = l(a,L)/L. J26 Eq. 35-36: lambda(a) = sum L_ij, chi(a) = lambda(a)/L0 with L0 = 25 m; PDF as in Eq. 32. Result: tortuosity essentially unchanged by dissolution in Q24; mean and variance decrease with tau in J26, strongly at Da=2e-2.
- Effective aperture: Q24 Eq. 21-22: b_eff = 2 tau/beta (per particle, b_eff(a,L) = 2 tau(a;L)/beta(a;L)). Network value = first moment (mean) of b_eff over particles (flux-weighted, so emphasises channels). Compared with hydraulic-aperture PDF in Fig. 8.
- J26 also gives average Lagrangian velocity v_bar(a) = lambda(a)/t(a) (Eq. 37).

## (5) Longitudinal dispersion (J26 Appendix B, Eq. B1, after Sahimi 2011)
D_L = (1/8) * [ (L0 - v t_0.16)/sqrt(t_0.16) - (L0 - v t_0.84)/sqrt(t_0.84) ]^2
- t_* = F^-1(*), time at which CDF equals * (so t_0.16, t_0.84; t_0.5 median); L0 = 25 m; v = median particle velocity = L0/t_0.5.
- Computed on the aggregate CDF pooled over the ensemble ("variations between members ... are quite wide"), then normalised by D_L at tau = 0 (D_L^0), Fig. 6c. 1D-ADE constant-coefficient approximation.

## (6) Flux-weighted Eulerian velocity PDF (J26 Eq. 38-40)
- psi_e(v) = (1/V) int_Omega dx delta(v - v(x)); v(x) = edge velocity v_ij on edge ij (volume-weighted over edges).
- Steady space-Lagrangian psi_l(v) = (1/N) int da delta(v - v_l(a)); under ergodicity psi_l(v) = v psi_e(v)/<v_e> (Eq. 40). Fig. 9 plots the flux-weighted psi_e, velocities normalised by max of the tau=0 values; compared with particle-based v_bar PDFs (Fig. 8; stated not identical to the steady space-Lagrangian).
- Channelization indicator d_Q (Maillot 2016), Eq. 41, reconstructed: d_Q = (1/V) (sum_f S_f |Q_f|)^2 / (sum_f S_f Q_f^2), Q_f = half the absolute flow exchanged by fracture f with its neighbours; reported as d_Q/P32 (initial ~ 37 % in J26; Q24 Table 1: 55.6 % unreacted, 28.1 % dissolved). Confirm the exact form against the paper image before coding.

## (7) States, statistics, layout
- Q24: two states (unreacted, dissolved final), 30 networks, thin lines = individual realisations, thick = mean, shaded 95 % CI. Dirichlet pressure BC identical in the steady flow solves. Table 1: E[k_eff] 3.25e-15 -> 2.16e-13 m2.
- J26: 5 snapshots tau = 0, 0.1, 0.2, 0.5, 1.0 per (Da,G); one panel grid of Da (columns/rows) by G; mean of 30 +/- 95 % CI for PDFs (Figs 5, 8, 9, 7); symbols = mean, error bars = 1 std for scalar summaries vs tau (Figs 6, 10).
- Scalars vs tau: gamma (6a), peak time normalised (6b), D_L/D_L^0 (6c), d_Q/P32 (10).

## Reproducing from an Eulerian PFLOTRAN tracer pulse (frozen permeability)
Our own mapping (not from the papers):
- Flux-weighted pulse injection into the inlet = inlet tracer concentration pulse with the inflow face carrying the flow; outlet flux-weighted concentration c_out(t) = (sum_faces Q_i c_i)/(sum_faces Q_i). Then f(t) = c_out(t) Q_out / M_injected (area = 1 once t runs far enough); i.e. BTC = outflow mass-flux fraction per time. For a delta pulse this equals the travel-time PDF; for a finite pulse it is a convolution, so use a short pulse (<< t_peak) or deconvolve.
- Mass check: int f dt should be 1 (non-sorbing, no loss). CDF F(t) = cumulative outflow mass fraction; t_0.16, t_0.5, t_0.84 read directly from F, then Eq. B1 with v = L0/t_0.5 gives D_L; peak time = argmax f; first arrival = earliest t with F above a small threshold (definition affects normalisation, since particle first arrival is exact whereas the grid solution is smoothed).
- Differences: Hyman's tracking has zero diffusion and complete mixing at intersections; PFLOTRAN adds numerical (and molecular) dispersion, so early arrival is smeared, tail exponent fits need a window clear of the numerical-diffusion plateau, and the late tail may flatten at the detection limit. Use the same mesh on all snapshots so numerical dispersion is constant (Q24 notes a uniform mesh for this reason).
- Not obtainable from the Eulerian pulse alone: beta, b_eff, per-particle tortuosity (need pathlines or a particle/TDRW tool). The Eulerian velocity PDF (Eq. 38-40) needs only cell/face velocities: v per connection, volume-weighted psi_e, flux-weighted version v psi_e/<v>.
- Time proxy: tau = dV_dissolved/V0 from the reactive run (volume of the dissolved mineral over initial pore volume); our reactive runs would need this computed per snapshot (our own pore-volume axis is a different quantity).
- Ensemble statistics: compute metrics per realisation, then mean and 95 % CI of PDFs on common normalised time bins; D_L from the pooled CDF.

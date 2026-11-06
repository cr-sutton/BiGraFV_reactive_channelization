# Phase 1 interventions

One entry per stopped or re-run job: time, run, symptom, fix, retry list.

## Mon 2 Nov 22:28 — L2_r15_p4.0_sg0.0_seed3 gypcal (kept, not re-run)
- Symptom: PFLOTRAN stopped at t = 32,748 y (= PV) of 36,515, step 57,520: "Time step cut criteria exceeded" after
  KSP_DIVERGED_NANORINF. transport_cut_to_failure.vtk: fracture cell 217 has gypsum VF 0.985 (re-precipitated; start 0.9),
  porosity 0.015, Total CO3 15.9 M, pH -0.57; helper cells 2251/2258 (porosity 1, mineral-free) pH -0.7/-0.8, CO3 35-50 M.
  Same cell-closing mechanism as the 500 m cubic coupled run (memory: re-precipitated gypsum from the SO4 brine).
- Decision: keep the run. Its network state had plateaued: dissolved 0.9395 -> 0.9400 and k_eff 5.3353 -> 5.3353 between
  26,862 and 31,318 PV; pattern analysis and probes ran on every checkpoint up to 31,318 PV. Paired renders use that as "last".
- Not applied: --gypsum-area-porosity-power (changes the gypsum rate law in closing cells = physics) and a 0.057 tau dt rerun
  (10x cost, likely the same singular cell). For the user to decide if this recurs before the plateau.

## Mon 2 Nov 22:33 — three early stops found by a scan; retries with the direct solver (retry_2233.txt, tag phase1direct)
- The checker missed "Time step cut criteria exceeded" without a NaN; BAD now includes it.
- L2_r15_p4.0_sg0.5_seed2 gyponly: stopped at ~23k PV (last state 23,039). L2_r15_p4.0_sg1.0_seed2 gyponly: stopped after
  31,318 PV. Both: iterative transport solver KSP_DIVERGED_DTOL -> SNES_DIVERGED_LINEAR_SOLVE, 16 straight cuts (numerics).
- Fix (numerics only): DIRECT=1 NP=1 (direct LU, one rank), every other setting unchanged. The seed-3 gypcal run (22:28 entry)
  gets the same retry. Originals kept under tag phase1; if a retry finishes, it replaces the original in the analysis
  (paired figures read --tag; swap folders or point the script at phase1direct for these three).

## Mon 2 Nov 23:10 — direct-solver retries stopped; half-dt retry for one run
- The DIRECT=1 NP=1 retries ran at ~0.8 s/step (iterative NP=2: ~0.1 s/step), projected 13-14 h each. Killed both (and the
  retry queue before it reached the seed-3 gypcal line). Folders *__phase1direct are partial and must not be analysed.
- L2_r15_p4.0_sg1.0_seed2 gyponly: keep the original (stopped at 34,390 of 36,515 PV, 94 %, past the plateau).
- L2_r15_p4.0_sg0.0_seed3 gypcal: keep the original (22:28 entry, plateaued by 26,862 PV).
- L2_r15_p4.0_sg0.5_seed2 gyponly (stopped at 25,460 PV, last saved state 23,039): numerics-only retry on the iterative
  solver, NP=2, time-step cap 0.285 tau instead of 0.57 (retry_2310.txt, tag phase1dt0285). If it finishes, it replaces the
  original in the analysis; the halved cap is a numerical setting, physics unchanged.
- Note for the user: iterative-solver divergence hit 2 of the 6 seed-2 x4 gyponly runs. If it keeps recurring, consider a
  smaller dt cap for every gyponly run (comparable numerics) rather than per-run retries.

## Tue 3 Nov 00:03 — half-dt retry failed the same way; diagnosis: late-time cell closing, not time step
- L2_r15_p4.0_sg0.5_seed2 gyponly, dt cap 0.285 tau: stopped at 26,650 PV (original 25,460), KSP_DIVERGED_DTOL + 16 cuts.
  transport_cut_to_failure.vtk: cell 639 gypsum VF 1.001, porosity 0, permeability 0 (closed by RE-precipitated gypsum, even
  without carbonate); cell 2139 Total Ca = SO4 = 3.7 M, gypsum SI 480 (solute pile-up). Same mechanism as the 22:28 gypcal stop.
- So the three early stops share one cause: a cell closing by gypsum re-precipitation late in the run (after ~23k PV), when the
  network state has nearly plateaued. Halving dt does not help; the direct solver is too slow.
- Kept: every truncated run. Latest usable state per run: sg0.5 seed2 gyponly 26,650 PV (phase1dt0285; last saved state in
  that folder), sg1.0 seed2 gyponly 34,390 PV, sg0.0 seed3 gypcal 32,748 PV. No more retries for this cause.
- FOR THE USER (physics/regularisation decision, not applied):
  (a) porosity floor for gyponly too (--min-porosity 1e-3 --perm-min-scale 1e-6, as gypcal already has; gypcal still failed);
  (b) --gypsum-area-porosity-power P (gypsum area x (phi/phi0)^P): stops a closing cell reacting, but also raises the rate in
      every dissolving cell, so it changes physics network-wide;
  (c) --inert-helper-cells for gyponly (gypcal has it; gyponly does not) if the pile-up cell is a helper cell;
  (d) compare all runs at a common horizon (e.g. 23,000 PV, which every run reaches) instead of the nominal 36,515.
  Also worth checking whether re-precipitation in gyponly is physical (saturated water entering a slower cell) or a
  porosity-update artefact.

## Tue 3 Nov 02:29 — disk full ~02:10-02:20 (macOS update staging), 12 seed-4 runs lost; queue rebuilt
- Symptom: 17 flags at once. mpiexec "write error (No space left on device)" in several seed-4 runs; others died or hit NaN /
  step-cut 300-1,400 PV into runs that started inside the window. Disk now 93 GB free; local snapshot
  com.apple.os.update-MSUPrepareUpdate shows macOS staged an update overnight (transient tens of GB). Our campaign: 25 GB runs +
  15 GB ParaView. System update settings not touched.
- Action: paused then killed the main queue (pid 44347, its running jobs left alive). Rerun unchanged (infrastructure failure):
  seed 4 p4 sg0.5 gypcal, p4 sg1.0 both, p6 sg0.0 both, p6 sg0.5 both, p6 sg1.0 gypcal, p8 sg0.0 gypcal, p8 sg0.5 gypcal,
  p8 sg1.0 both. Kept running: seed 4 p6 sg1.0 / p8 sg0.0 / p8 sg0.5 gyponly and seed 5 p4 sg0.0 pair (complete outputs).
  New queue run_list_phase1_resume.txt (28 jobs: 12 seed-4 reruns + 16 seed-5 never started), MAX 5, caffeinate on it.
- If the early seed-4 gypcal NaNs (p6 sg0.5/sg1.0, p8 sg0.0/sg0.5/sg1.0 at 330-570 PV) recur on the rerun, they are real.
- check_runs.py now flags DISK below 25 GB free.

## Tue 3 Nov 03:17 — root cause of the early stops: outflow helper-cell pile-up (not network chemistry)
- New failures: seed-4 gyponly p6 sg0.0 (rerun, 9,200 PV), p6 sg1.0 (20,570), p8 sg0.0 (11,300), p8 sg0.5 (10,030).
- In every failure so far (also seed-2 p4 sg0.5 gyponly cell 639, seed-3 p4 sg0 gypcal cell 217, seed-4 p8 sg0 cell 781) the
  cell that closes with re-precipitated gypsum is a fracture cell DIRECTLY attached to an outflow boundary helper cell
  (boundary_right_e.ex; e.g. seed-4 x6: cell 3849, x = 500.0, volume 2.2e-4 m^3, single neighbour = closing cell 758). The
  helper cell holds Ca = SO4 = 0.5-3.7 M (SI up to 480), far above anything dissolution can make, so supersaturated water
  leaks back and seals the last fracture cell. This is the 25 Oct artefact documented in stabilize_graph_run.py (pressure-solve
  mass imbalance / tiny helper volume -> solute pile-up). Earlier entries calling it "late-time cell closing by gypsum
  re-precipitation" are superseded: it is a boundary-numerics problem, independent of sigma (same cell 758 at sg0 and sg1).
- Fix (input-only numerics, existing tool): STABILIZE="--dirichlet-outflow 2e5 --min-boundary-volume-frac 0.01 --tight-flow".
  New queue run_list_phase1_stab.txt (run_phase1_stab.sh, MAX 5, caffeinate on it): control (seed-1 p4 sg0 gyponly, tag
  phase1stab, to measure the fix's effect on a run that finished without it), the 4 seed-4 gyponly retries, and the 20 jobs
  never started. Resume queue killed (its 8 started jobs keep running with the old STABILIZE; retry them with the fix if they fail).
- FOR THE USER: seeds 1-3 (and some seed-4) ran without the fix. If the control shows a material difference, Phase 1 needs a
  consistent rerun of those with the fix (~10 h); if not, keep them and note the mixed boundary setting.

## Tue 3 Nov 03:57 — the 03:17 stabiliser failed at t = 0 on every run; testing the outflow face-area fix instead
- --tight-flow (flow RTOL 1e-12, ATOL 1e-14) cannot converge at the Hyman rate (SNES_DIVERGED_MAX_IT at step 0, 16 cuts), so
  all 25 jobs of run_list_phase1_stab.txt failed in 4 minutes (03:20-03:24). Their folders are unusable; the jobs must rerun.
  Lesson: test a fix on one run before queueing it.
- Root cause refined: graph outflow faces in boundary_right_e.ex have area 1000 m^2 at 1e-4-0.07 m from the cell centre — the
  Track H geometry that quantises the outflow at the Hyman rate and drives the helper-cell pile-up.
- Test (retry_test_exfix.txt, tag phase1exfix): EXFIX="--area-per-dist 1e-2" (exfix_outflow.py, Track H2 rule; new opt-in hook
  in run_km_graph_case_hyman.sh, env EXFIX) with the ORIGINAL stabiliser (--dirichlet-outflow 2e5 only), on
  seed-4 x6 sg0 gyponly (failed at 9,200 PV twice) and the seed-1 x4 sg0 gyponly control (finished cleanly without the fix).

## Tue 3 Nov 04:07 — outflow face fix validated; the 30 unfinished runs requeued with it
- Control (seed-1 x4 sg0 gyponly, EXFIX on vs original without): network gypsum mass equal to <= 3e-4 of the inventory up to
  10,533 PV (dissolved 0.7775 vs 0.7774); outflow water rate equal to 0.01 %. The fix does not change results, so the 60
  completed runs (no fix) stay as they are.
- Failing network (seed-4 x6 sg0 gyponly, EXFIX on) at 4,515 PV: every outflow cell at gypsum saturation (Ca 16.6 mM,
  SI max 1.0); old pile-up cell 3849 Ca 16.6 mM; old sealing cell 758 untouched (porosity 0.1, gypsum 0.9).
- Queue run_list_phase1_exfix.txt (run_phase1_exfix.sh: EXFIX="--area-per-dist 1e-2", STABILIZE="--dirichlet-outflow 2e5",
  MAX 5, caffeinate): the 29 remaining unfinished runs under the normal tag phase1 (folders overwritten). The 30th, seed-4 x6
  sg0 gyponly, is the test run itself: tag phase1exfix (use that folder for this run in the analysis).
- Everything earlier in this file about "late cell closing" and the phase1direct / phase1dt0285 / phase1stab folders is superseded;
  those folders are not used. Mixed setting to note: 60 runs without the face fix, 30 with it (shown equivalent by the control).
- Recommend EXFIX="--area-per-dist 1e-2" as the default for all future Hyman-rate graph runs (Phase 2).

## Tue 3 Nov 04:58 — control finished: EXFIX vs original, seed-1 x4 sg0 gyponly (all rows)
- dissolved: max |diff| 0.000826 (row k=50, value 0.5543)
- k_eff_ratio: max |diff| 0.0188 (row k=47, value 7.398)
- n90: max |diff| 1 (row k=0, value 277)
- dQ_P32: max |diff| 0.0455 (row k=50, value 17.13)
- end: dissolved 0.8958 vs 0.8959; k_eff 9.969 vs 9.954; rows 66 / 66
- Seed-4 x6 sg0 gyponly test with EXFIX passed its old failure point (9,200 PV) and is at 27,800 PV.
- Tue 3 Nov 08:10: abandoned retry folders (*_phase1direct, *_phase1dt0285, *_phase1stab) moved to phase1/_abandoned/ (not deleted). run_times.py marks runs with no output for 15 min and no wall time as dead.
- Tue 3 Nov 08:20: user approved EXFIX=--area-per-dist 1e-2 as the default for Phase 2 and all later Hyman-rate graph runs; now the default in run_km_graph_case_hyman.sh (EXFIX=none disables).

## Tue 3 Nov 09:16 — machine restart at ~08:46 (likely macOS installing the update staged overnight)
- All queues, PFLOTRAN runs and caffeinate were gone. Complete and kept: 87 runs incl. control and the seed-4 x6 sg0 exfix test.
- Lost: all 12 seed-5 x6/x8 runs (6 were mid-run, 6 never started). Relaunched via run_phase1_restart.sh /
  run_list_phase1_restart.txt (MAX 6, EXFIX by default, caffeinate on the queue); recurring check repointed.
- Tue 3 Nov 12:35: Phase 1 complete (90/90 + control). seed-4 x6 sg0 gyponly: the EXFIX test run renamed to the standard tag (gypsum__uncorrected_graph__phase1; ParaView folder too); the failed 03:20 attempt moved to _abandoned/.
- Tue 03 Nov 17:58: report refresh: x8 Phase 2 runs (gyponly phi0.05 seed1, 2 mM seeds 1-2) added to depth table, paired differences (x20 7 pairs; 2 mM 8 pairs, max 0.052), 2 mM inheritance 0.94-1.00; republished.
- Tue 03 Nov 19:01: fine probes complete (45/45 per chemistry): transport table, In-brief and 6.2 updated; Phase 2 x4-x8 complete (9 pairs each): depth table, paired table, 2 mM status updated; republished.
- Tue 03 Nov 20:52: user decision: keep networks, label the transmissivity depth mismatch (no rebuild); report Limits item updated.
- Wed 4 Nov 05:23: SLOW flag on L2_r15_p16.0_sg1.0_seed1 gyponly phase2_phi005 (projected 8.7 h). Expected: phi0 0.05 doubles the simulated years (3.08e4 y); x16 Phase 1 gyponly took 4.2-4.7 h. Acknowledged, no action.
- Wed 4 Nov 05:53: SLOW flag on x16 sg1.0 seed2 gyponly phase2_phi005 (projected 9.4 h), same expected cause; seeds 2-3 acknowledged.
- Wed 4 Nov ~11:00 (user request): queued for after the reactive queue: (b) paused-pulse stage movie (new probes on
  x6 sigma 1 seed 1 via phase1/run_anim_probes.sh -> snapanim_k plume probes at k = 0 + stage stills, snapseq_k BTC-only
  probes at every movie frame; make_pulse_movie.py -> figures/anim3/) and (c) the two wormhole checks
  (WORMHOLE_CHECKS.md). probe_frozen_state_tracer.py gained opt-in PROBE_VTK_DT / PROBE_VTK_UNTIL (default unchanged).
  Cron 0978d4ee replaced by 6b8d4f38 with these steps.
- Wed 4 Nov ~11:30 (user request): main clock switched from theoretical capacity time to the measured fraction of the
  fracture-cell gypsum dissolved (time_axes.clocks.diss reads patterns.csv; ~1 % of the gypsum sits in inert helper cells
  and is excluded). New figures *_diss.png (logit axis, default), stage_events_clocks.py -> phase1/stage_events_clocks.csv,
  section 3 rewritten (4 clocks), stage table / In brief / 5 / 5a / 5e / 6.1 re-quoted. Karen review: 4 MUST + 5 SHOULD +
  3 NICE applied. Republished 1793813521-8175. Also dq_baseline.py -> phase1/dq_baseline.csv (not in the report yet).
- Wed 4 Nov ~12:30 (user request): colloquium deck forsmark_reactive/deck/Forsmark_Reactive_Channels.pptx (26 slides, python-pptx), kept 1:1 with the report via deck/rebuild.sh; four-stages cartoon labels moved to the dissolved-fraction clock in the report SVG (not yet republished).
- Wed 4 Nov ~13:00 (user request): exploratory olivine-carbonation run prepared (deck_olivine_carbonation.py, lit/lit_olivine_carbonation.md). 1-y test on x6 sigma1 seed1 (explore_olivine/test_short): converged in 20 s; after 1 PV min porosity 0.10 -> 0.052, k/k0 min 0.52, k_eff -1.5 %, 21 fractures below 0.09. Full 300-y run (explore_olivine/run_olivine.sh) queued in cron 5ed53ec0 step (a2) for after the reactive queue.
- Wed 4 Nov 15:58: queue done (15:37). Started olivine run (run_olivine.sh) and paused-pulse probes (run_anim_probes.sh) in background; final analyses running.
- Wed 4 Nov 16:06: olivine run done (444 s). Inlet fractures seal from ~6 PV; at 13 PV k_eff 0.18, 52 at floor, overlap0 0.61, n90 458->674; at 300 PV k_eff 0.013, 1374 of 2714 at floor. Section 6.7 drafted. Wormhole bound (wormhole_bound.py) done; regime map running; pulse snapseq probes running.
- Wed 4 Nov ~17:25: final step done. x16 subsection (5f), paused-pulse movies (5e), wormhole bound + regime map (6.6), olivine exploration (6.7) added; Karen review: 5 MUST, 6 SHOULD, 3 NICE applied; report republished 1793831102-75d2; deck rebuilt (30 slides). Hourly job deleted.
- Wed 4 Nov ~17:30 (first logged as "Thu 5 Nov" by mistake): Phase 3 queue started (run_phase3.sh, run_list_phase3.txt, 30 runs): ceiling test at porosity 0.182 (gypsum-only x5.5, coupled x3.3; sigma 1, seeds 1-3, P32 x4/x6/x8) and rate test (rate-mult 0.1 and 10; x6 sigma 1 seeds 1-3; both chemistries). Ceiling matched through porosity, not n (user preference).
- Wed 4 Nov ~19:20: manuscript analyses back (breakthrough_predictor.py, master_curves.py, transport_channel_link.py, channel_turnover.py, depth_variability.py). Report section 8 added (8.1-8.5), sections renumbered; republished 1793837999-73af; deck rebuilt (32 slides).
- Wed 4 Nov 18:33: Phase 3: 15 started, 10 finished (coupled phi0182 x4/x6 in 25-240 s, gyponly x4 in 9-13 min; all reached FINAL_TIME, no cuts). Channelization started on finished runs. GitHub push of section-8 analyses done (channel_turnover.csv gzipped, >100 MB raw).
- Wed 4 Nov ~18:45: DFN validation scope back (DFN_VALIDATION_SCOPE.md): Phase 1 nets unmeshable (FRAM off); recommended 1 km x4 rFram h=1 m. Report 8.6 figure list and 8.7 DFN scope added, republished 1793839413-f02d; deck 33 slides.
- Wed 4 Nov 19:23: Phase 3 all 30 started, 24 finished; channelization started on 14 finished runs.
- Wed 4 Nov ~20:15: Phase 3 queue done 19:49. analyze_phase1_mechanism/stage_events_clocks extended to phase3 tags and rerun; phase3_tests.py -> phase3_ceiling.csv, phase3_rate.csv; depth_law.png now x3.3-x20; report 6.4 (ceiling test) and 8.8 (rate test) added. Karen review next.
- Wed 4 Nov ~20:45: Karen review of section 8 + Phase 3: 5 MUST (Da direction, Phase 2 not independent, 14/15 folds, depth-variability disclosure, rate offset sign) and 14 SHOULD + NICE applied; deck fixed and rebuilt (34 slides).
- Wed 4 Nov ~21:00: GitHub push done (Phase 3 + section 8). Overnight check job deleted; 8:00 report scheduled.
- Thu 5 Nov 08:00-10:00 (user: "do all 4"; mid-turn: include x16 everywhere before drafting figures):
  (1) rate-test outlier: coupled seed 1 at x0.1 has PR_pore 0.003 at one state because 72 fracture cells fill with re-precipitated
  gypsum (solids > 1, porosity floor) while carrying 0.41 % of the flow. New gypsum_reprecipitation_scan.py -> phase1/gypsum_reprecipitation.csv:
  56/60 Phase 1 coupled runs gain gypsum, 48/60 fill 1-12 cells (flow <= 1.2e-5); no gypsum-only run fills a cell. Report 5a, 6.5, 6.7, 8.8
  reworded. (2) x16 audit: make_phase1_channel_figures / make_candidate_figures / make_phase1_report_figures / make_phase1_figures /
  wormhole_regime_map now include x16 (26 report figures replaced); deck_numbers pools x4-x16 (stages_x4x8 kept for the x16 slide);
  report sections 1-6 re-quoted from requote_x16.py (old x4-x8 values reproduced first); channel_identity.py rebuilt as a script
  (reproduces the old CSV exactly, extended to x16 and Phase 2). Fine probes for the 30 x16 runs launched (run_fine_probes_x16.log;
  transport sections 5e/6.2/8.2 wait for them). (3) early_redistribution_predictor.py: report 8.5. (4) make_manuscript_figures.py ->
  manuscript_figures/Figure_1-8 (drafts). (5) DFN: dfn_validation/build_rfram_network.py (rFram x4 sg1 seed1, 1,605 fractures, 9 paths);
  mesh 758,183 cells in ~5 min; 2 NaN Voronoi volumes repaired (repair_uge_nan.py, uge_repair.json); DFN steady flow 2.87e-5 m3/s in = out,
  1.43x the graph; gate runs (one-cell gyponly+gypcal, Phase 1 settings) and the DFN smoke test (run_dfn_case.sh, 40 steps) running.
- Thu 5 Nov ~09:40: DFN smoke done (coupled 15.7 s/step, 9.2 GB; gypsum-only 16.6 s/step, 9.7 GB; 6 ranks, load ~22; no cuts;
  dt ramp identical to the graph). Projection: coupled to t_cap 2 ~4 h, gypsum-only to t_cap 1 ~59 h (1.5-3x the scope estimate).
  Gate (gate_check.py): depth, inheritance, breakthrough inside the Phase 1 x4 sigma 1 envelope; PR_V minimum at 0.08-0.11 dissolved
  (Phase 1 0.13-0.51; 1 of 120 Phase 1 runs below 0.12) and no PR_pore dip in the coupled run (0 of 120): atypical in stage timing.
  Recommended to the user: gate rFram seeds 2-3 before DFN lanes. Numbers-checker on the x16 re-quote: ~275 confirmed, 5 fixed.
- Thu 5 Nov ~11:00 (user request): paused-pulse movies redone (make_pulse_movie.py): no plume maps; the movie opens with a pulse
  through the unreacted network, then the reaction plays and pauses at each stage while that stage's breakthrough curve draws in.
  BTC now normalised concentration E = flux x tau_res against pore volumes since the pulse (frozen network's pore volume); the
  years panel is gone (its stretch was the added pore volume, tau_res 1.0 -> 7.1 y, not dispersion). "(main clock)" removed.
  New static figure pulse_btc_only_<mode>.png replaces pulse_stages_* in report 5e, deck slide 17 and manuscript Fig 7a.
  Old movie outputs kept in the scratchpad (anim3_v1). Seed 2-3 rFram gate runs running since 10:00.
- Thu 5 Nov ~11:15: rFram seeds 2-3 gated (gate_summary.py): Phase 1 leave-one-out baseline 7-14 of 16 inside; rFram 12/11/10.
  Seed 2 recommended (typical stage timing, strong channelization). Seed 2 DFN mesh started (no reactive DFN run launched).
- Thu 5 Nov ~11:40: seed 2 DFN mesh fails (LaGriT segfault in connect on fracture 329, radius 32 m, 1.5 m intersection segment;
  also with max_dist 9; h 0.95 changes the network to 1,454 fractures). Seed 3 meshed cleanly (766,560 cells, no NaN; Q_dfn/Q_graph
  1.17). Revised proposal: coupled DFN on seeds 1 and 3, gypsum-only on seed 1. Not launched (user: wait for the x16 probes).
- Thu 5 Nov 12:16-12:40: x16 fine probes done (30 runs x 10 states). analyze_phase1_tracer.py and transport_channel_link.py now include
  x16 (1,020 states). Report In brief, 5e (table + new "denser networks move less"), 6.2, 8.2 and deck re-quoted. dgamma vs PR_V
  rho -0.80 -> -0.75 pooled; within-run gyponly -0.88 -> -0.79; t50 models do not transfer to x16 (held-out R2 -0.9 to -3.2).

## 5 Nov 2026 15:26 - k-phi exponent test (user request)
- After the literature reviews (lit/lit_kphi_relations.md, lit_channel_depth.md) pointed to the x10 ceiling of n = 1 as the
  control on channel depth: P32 x6 sigma 1 seed 1, gyponly + gypcal, PERMEABILITY_POWER 3 (ceiling x1000), everything else
  as Phase 1, ends at capacity time 2. Tag kphi_n3, run_list_kphi_n3.txt, run_kphi_n3.sh; comparison kphi_n3_compare.py
  (n = 1 baseline on the same network, capacity time <= 2: depth 0.678 gyponly, 0.760 coupled).
- Thu 5 Nov 16:13: n = 3 pair done (no timestep cuts; gyponly 25,703 steps, gypcal 926). phase1/kphi_n3_compare.csv, capacity time <= 2,
  n = 1 -> n = 3: depth 0.678 -> 0.213 (gyponly), 0.760 -> 0.353 (gypcal); n90 min/start 0.50 -> 0.09, 0.61 -> 0.15; k_eff max x9.8 -> x727,
  x5.4 -> x135; breakthrough at dissolved 0.46 -> 0.27, 0.48 -> 0.31; inheritance 1.0 in all four. Stage 1 still present (PR_pore falls first);
  PR_V has two dips before breakthrough (channel competition: 0.21 at d 0.11, back to 0.45, 0.25 at d 0.20); after breakthrough PR_V
  recovers to 0.51 / 0.71 of start by capacity time 2 (n = 1: 0.95 / 0.98). One network only.

## 6 Nov 2026 ~10:30 - k-phi shape pilot E0 (user request; KPHI_WORKPLAN.md)
- Same ceiling x10, different k(phi) shape via PERMEABILITY_CRITICAL_POROSITY (new opt-in --perm-crit-por in deck_gypsum_calcite.py;
  default decks unchanged): n = 0.5 phi_c 0.0909 (concave), n = 2 phi_c -0.316, n = 8 phi_c -2.598 (near-exponential).
  Gyponly P32 x6 sigma 1 seed 1 to capacity time 2; tags kphiC10n05 / kphiC10n2 / kphiC10n8; run_list_kphi_e0.txt, run_kphi_e0.sh,
  3 at a time (NP 2) alongside the 2 km queue.

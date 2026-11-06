# Scale-up test (set 5 Nov 2026)

Question: do the four channel-formation stages found in Phase 1 (1000 x 250 x 250 m) hold on a larger domain?

Design
- Domain 2000 x 500 x 250 m: flow length x2, width x2, layer-2 thickness kept, 4x the Phase 1 volume.
- Same FFM01 layer 2 sets, rmin 15 m, rmax 564 m, transmissivity model, P32 scaling as Phase 1 (`build_one.sh`, same builder with `--domain-size`).
- Phase 1 run settings exactly: one-cell BiGraFV, one network pore volume per year, porosity 0.1, n = 1, gyponly + gypcal 0.5 M,
  checkpoints at capacity time 0.02-2, ends at capacity time 2 (like P32 x16), tracer probes at checkpoints.
- Set: P32 x4, x6, x8 x sigma 1.0, 0.5, 0.0 x seeds 1-5 = 45 networks, 90 runs. P32 x16 left out: about 300k cells,
  about 18 h per gypsum-only run.
- Queue order sigma 1.0 -> 0.5 -> 0.0 so a stop leaves complete ensembles. `run_list_scale2km.txt`, `run_scale2km.sh`, 6 runs x 2 ranks.

What changes with size (state these with the results)
- At 1 PV/yr the network residence time stays 1 yr, so the network-scale Damkoehler number is unchanged; each fracture holds the water
  for a shorter time (more fractures in series), so the per-fracture Da is lower.
- The largest fractures (r up to 564 m) are smaller relative to the domain.

Comparison, fixed before the results (same measures as dfn_validation/gate_check.py)
- Stage order on the dissolved fraction: PR_pore minimum -> outlet 5 % -> PR_V minimum -> breakthrough, events within capacity time <= 3.
- Dissolved fraction at each stage, depth (PR_V min / start) and inheritance (overlap0 at the n90 minimum), paired by
  (P32, sigma, seed) against the 1 km Phase 1 networks (different dfnGen output; pairing is by parameters, not by geometry).
- "Holds" = same stage order in every run and the 2 km medians inside the 1 km IQR for each P32. Report medians [IQR], n stated.

## Launch (5 Nov 2026 13:32)
- 45 networks built (19-54 s each). Medians 1 km -> 2 km: fractures x3.7-3.8, cells x3.7, node-disjoint paths 11/23/41 -> 16/41/78
  (x4/x6/x8), dead-end and backbone fractions unchanged.
- First 5 min, sharing the machine with the Plane-DFN egs_robust calibration queue (load ~34 on 14 cores): x8 gypsum-only
  1.2-1.3 s/step, coupled 1.8-2.1 s/step. To capacity time 2 (about 25,700 / 930 steps): x8 gypsum-only ~9 h per run.
- Estimate with that contention: sigma 1.0 done ~Fri 6 Nov 06:00, sigma 0.5 ~Fri 22:00, sigma 0.0 ~Sat 7 Nov 14:00 (+-30 %).
  Roughly half that if the machine were free.

## Incident and fix (5 Nov 14:00)
- The 2 km networks have the same folder names as the 1 km ones, and analyze_km_dissolution_patterns.py writes
  paraview/<net>__<run>, so the first finished 2 km run (x8 sigma 1 seed 3 coupled) overwrote the Phase 1 state files.
  Phase 1 copy regenerated from the 1 km run outputs (patterns.csv identical; mechanism measures match phase1_mechanism.csv
  to 1e-14). The other 5 threatened Phase 1 folders were backed up (_phase1_paraview_backup/) and restored after their
  2 km analysis; 2 km files moved to paraview/S2KM__*, Phase 1 leftovers removed from them.
- v1 runner stopped; v2 (run_queue_scale2km.py, run_scale2km_v2.sh) writes paraview/S2KM__* and adds analyze_channelization.py.
- compare_scale.py recomputes the mechanism measures at every state (state files are every 4th on >= 10,000-fracture nets);
  checked on a 1 km run against phase1_mechanism.csv (max relative difference 4e-7).
- DFN runs paused until the user says go.

## Interim results, Thu 5 Nov 20:20 (compare_scale.py; t_cap <= 2; σ1 only)
- ×8 σ1: 5/5 paired seeds both chemistries. 2 km vs 1 km medians (MW p, n 5 v 5):
  gyponly breakthrough 0.656 v 0.574 (0.22), depth 0.702 v 0.641 (0.15), inheritance 0.992 v 0.988;
  gypcal breakthrough 0.731 v 0.666 (0.42), depth 0.820 v 0.794 (0.22), inheritance 0.991 v 0.987. No measure significant.
- PR_V has an early (d < 0.35, front mid-domain) and a late (near outlet) dip at both scales. Early dip deepest:
  2 km ×6 s1 both chemistries; ×8 s4 gyponly (0.749 v 0.777); ×8 s1 gyponly is a tie (0.782 v 0.785, which makes the
  only PRpore_min > PRV_min case). 1 km ×6/×8 σ1: 5 of 20 runs. Coupled ×8 at 2 km: late dip deepest in 5/5.
- Per-200 m bins (scratchpad xbin2km.py) on ×6 s1 gyponly: focusing front travels inlet -> outlet, bins relax behind it,
  as in the 1 km xbin_channelization.pdf.
- Thu 23:10: ×6 σ1 complete (5 v 5 both chemistries). gyponly breakthrough 0.578 v 0.571, depth 0.663 v 0.678;
  gypcal breakthrough 0.676 v 0.584 (p 0.55), depth 0.786 v 0.760. σ1 ×6+×8 2 km: PRV_min <= breakthrough 20/20,
  PRpore_min <= PRV_min 19/20, coupled shallower than gyponly on the paired network 10/10. Early dip deepest 7/20
  (three within 0.02 of the late dip) v 5/20 at 1 km.
- Fri 00:00: ×4 σ1 complete; σ1 is now 15 v 15 per chemistry. Order at 2 km: PRV_min <= breakthrough 30/30,
  PRpore_min <= PRV_min 29/30. ×4: breakthrough 0.643 v 0.563 gyponly (MW p 0.056), 0.661 v 0.586 gypcal (0.31);
  depth 0.729 v 0.682, 0.868 v 0.779 (0.15). Early PR_V dip (d < 0.35) deeper than late dip, per 10 runs (both chem):
  1 km ×4/×6/×8 = 4/3/2; 2 km = 8/5/2 (Fisher ×4 2 km v 1 km p 0.17; 2 km ×4 v ×8 p 0.023). The d < 0.35 split is a
  post-hoc choice, not pre-registered.
- Fri 05:05: ×8 σ0.5 complete (5 v 5). Breakthrough 0.688 v 0.570 gyponly (p 0.15), 0.743 v 0.665 gypcal (0.42);
  depth 0.679 v 0.666, 0.801 v 0.802; inheritance 0.99 both. Early dip deeper 3/10 at 2 km v 2/10 at 1 km.
  Seed 1 (same geometry as σ1 seed 1) has its PRV_min at d 0.10/0.14, before PRpore_min, in both chemistries.
  σ check: same geometry across σ; log10 k std 0.27 (σ0.5) v 0.34 (σ1) at both scales, so σ0.5 and σ1 runs on one
  seed are close by construction (size-correlated T dominates the spread).
- Fri 08:00: ×6 σ0.5 complete (5 v 5). Breakthrough 0.636 v 0.492 gyponly (p 0.55), 0.676 v 0.574 gypcal (0.42); depth 0.657 v 0.670,
  0.775 v 0.770. Order: PRpore<=PRV 10/10, PRV<=breakthrough 10/10. Coupled shallower and later 5/5. Early dip deeper 4/10 (1 km 2/10).
  Complete cells now 5 of 9 (50 runs).
- Fri 09:00: ×4 σ0.5 complete; σ0.5 and σ1 now complete (60 runs at 2 km, 6 of 9 cells). ×4 σ0.5: breakthrough 0.642 v 0.569
  gyponly (p 0.056), 0.664 v 0.638 gypcal; depth 0.755 v 0.678, 0.846 v 0.784 (both p >= 0.15). Order 10/10; coupled shallower
  and later 5/5. Early dip deeper 7/10 (1 km 4/10). Pooled σ0.5+σ1: 2 km ×4 15/20 v ×8 5/20 (Fisher p 0.004); ×4 2 km v 1 km
  15/20 v 8/20 (p 0.054). σ0 running.

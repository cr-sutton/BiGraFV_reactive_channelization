# Manuscript assessment and next steps (4 Nov 2026, evening)

## Verdict

There is enough for one solid manuscript. It needs three targeted additions before submission:
1. A validation of the one-cell model in this regime.
2. A clean causal test of the depth law.
3. A short rate-robustness check.

Everything else can come from the data we already have. The olivine result is a good outlook paragraph, or a later short paper. It should not be part of this one.

## Proposed paper

**Working title.** Dissolution channels in kilometre-scale fracture networks are inherited, and their depth is set by how far permeability can grow.

**Venue.** WRR or JGR Solid Earth (the venue of Hyman et al. 2026). A GRL version is possible only if we cut down to inheritance, the clock and the depth law.

**Story, one figure each:**
1. **Set-up.** 60 Forsmark-statistics networks, 1 km long, with 1,587–8,229 fractures and two chemistries (120 runs), plus Phase 2.
2. **Channels are inherited.** At the strongest channel, the median share of the 90 %-flow set that was already there before reaction is 0.98 (lowest 0.92). This holds over P32 ×4–×16, σ and both chemistries. It extends Hyman et al. 2026 to kilometre scale, site statistics and mineral-filled fractures.
3. **Four stages, and stage 1 is new.** In filled fractures, open pore space and flow decouple first: PR_pore dips while PR_V holds. The two then realign. This cannot happen in open-fracture models, where pore space and fracture volume are the same thing.
4. **The clock is the mineral consumed, not the open volume gained.**
   - The measured dissolved fraction lines up chemistries and porosities (×1.16–1.20 spread of event times). Hyman's τ does not (×3.5).
   - With n = 1, τ is the mean permeability gain.
   - Capacity time predicts the clock before a run, until breakthrough.
5. **Depth law.** The channel depth is set by the permeability ceiling, not the chemistry. This is paired on the same networks at ×4–×16.
6. **Transport signature.** While the channel forms, t50/τ_res rises (0.79 → 0.90) and the tail steepens (γ 3.3 → 4.1), then both partly recover. The paused-pulse frames show it, which suggests tracer tests could diagnose the stage.
7. **Breakthrough is predicted by the initial flow field.** This is new (quick test, 4 Nov). It turns the model-dependent "compact front" into a testable statement.
   - The more unequal the initial flow, the less gypsum is dissolved at breakthrough: Spearman ρ = −0.57 (gypsum-only) and −0.60 (coupled) against the initial flow Gini, n = 60 runs each.
   - The dissolved fraction at breakthrough is about 0.77 (gypsum-only) and 0.86 (coupled) of the initial channel's volume share.
   - The wormhole scenario sets the error bar.
8. **Limits.**
   - One cell per fracture.
   - The wormhole regime is extrapolated.
   - The transmissivity law is the SKB 0–200 m law used at 200–400 m.
   - Outlook: precipitation that adds volume (olivine) does re-route.

## Analyses with the data we already have (no new runs)

| # | Analysis | Why | Effort |
|---|---|---|---|
| A | Breakthrough predictor: d_bt from initial flow Gini, n90 share and channel volume share; leave-one-P32-out cross-validation | Makes the compact-front result predictive rather than model-dependent | ½ day |
| B | Master curves: PR_V/PR_V0 against d/d_bt (and PR_pore) for all P32, σ and chemistry | The single "collapse" figure a reader remembers | ½ day |
| C | What sets depth beyond the ceiling: single runs vary 0.49–0.80 at fixed ceiling. Try σ, initial PR_V, backbone transmissivity spread, inlet/outlet degree, path redundancy (quick test: no topology metric has \|ρ\| > 0.4, so per-fracture variables are next) | Needed if the depth law is the headline | 1 day |
| D | Transport–channel link: γ and t50/τ_res against PR_V and PR_pore across all probed states | Turns transport into a field-observable diagnostic | ½ day |
| E | Who joins and leaves the channel (the 2–3 % turnover): position, size, transmissivity rank | Explains the 92 % floor | ½ day |
| F | d_Q note: size-proportional baseline (d_Q/P32 at proportional flow is 17–22 %, close to measured) | Methods point for the measures section; supports using PR_V | done; write up |

## New runs, in order of importance

1. **Validation (needed for review).**
   - Compare BiGraFV with a meshed DFN on a reduced Forsmark block (for example 250 m, one network per chemistry, same rate).
   - Compare inheritance, stage timing on d, depth and breakthrough.
   - Earlier TPL work found that the DFN channelizes more than the one-cell graph, and that mc4hd fixes most of the gap. The Forsmark block needs its own check.
   - Cost is the main unknown. The 500 m mc4hd was infeasible before; 250 m or a thinner slab may work.
   - Decision for you: DFN alone, or DFN plus mc4hd.
2. **Clean ceiling test (makes the depth law causal).** Keep the chemistry and porosity fixed and change only the ceiling with a permeability cap (`apply_aperture_cap.py`, as in the 29 Oct 1 mm cap run):
   - gypsum-only at φ0 = 0.1, capped at ×5.5, against coupled ×5.5;
   - gypsum-only at φ0 = 0.05, capped at ×10, against gypsum-only φ0 = 0.1.

   With σ = 1, seeds 1–3, P32 ×4–×8, that is 18 runs of 2–9 h each. If chemistry does not matter, the capped gypsum-only depth should match the coupled depth.
3. **Rate robustness.**
   - Run 0.1 and 10 pore volumes per year on 3 networks per chemistry. At Da_f of about 1e7 the stage timing on d should not move.
   - This answers "why 1 PV/yr" with data, not argument. It is about 12 runs; the 0.1 PV/yr runs are the longest.
4. **Optional:**
   - 5 seeds for Phase 2.
   - A Forsmark-relevant mineral: calcite dissolution by CO2-acidified water (`deck_acid_calcite.py` exists). This answers "why gypsum at Forsmark", but could be a second paper.
5. **Olivine (separate work).** Ensemble, surface-area range, pressure-dependent CO2, and a real porosity/permeability closure for sealing. This is a short-paper candidate on precipitation-driven rerouting in the one-cell model.

## Risks a reviewer will raise

- **Novelty against Hyman et al. 2026.** Inheritance in networks is known. Our new parts are mineral-filled fractures (the stage-1 decoupling, the ceiling law, and the mineral-consumed clock), kilometre scale on site statistics, the transport signature, and the breakthrough predictor. The paper should lead with these, not with inheritance alone.
- **The one-cell model.** Needs the validation run and the wormhole scenario. The BiGraFV methods paper (in preparation) should be submitted first or alongside, since this paper cites it as "this work, unpublished".
- **Depth law looks expected.** The cap test is what makes it a result.
- **Gypsum at Forsmark.** Frame Forsmark as realistic network structure and gypsum as a fast, capacity-limited model mineral, following Hyman et al. IJGGC 2024. Optionally add calcite.
- **Small Phase 2 samples.** Paired designs help. Adding seeds is cheap if asked.

## Suggested order

1. Analyses A, B and D (about 1.5 days).
2. Draft the figures and outline.
3. Launch the cap test and the rate test in parallel.
4. Scope the DFN validation cost on one block.
5. Write.

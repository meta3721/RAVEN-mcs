# RAVEN-MCS TMC review

- Date: 2026-10-09
- Manuscript: `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`, sha256 `6FC9BE0B8689B6C8849B2A07F55A84E25B2D8360BBFFCFB54F11A0C93C1C2B95`
- Artifacts read: `results_traffic_e1/round_v1/TE1_VERDICT.json`, `results_traffic_struct/round_v1/TS1_SUMMARY.json`, `tables/TS1_PAIRS.csv`
- Mode: full scientific review of this file. Proofs, Holm tables, and related work were not re-derived in this pass.

## Mode

`full`. Assessment only. No manuscript edits.

## Venue and assumptions

IEEE TMC, method plus measurement. Page count of the current build is 18. Overall stance uses 1–10. Dimensions use 1–5. Weights: Originality 0.10, Significance 0.15, Soundness 0.20, Evidence 0.25, Clarity 0.15, Reproducibility 0.10, Related work 0.05. A score of 3 or below carries a deduction and a repair condition. This is an absolute reading of the current file, not a fused progress score against an earlier draft.

## Paper summary

RAVEN-MCS builds a selection-corrected aggregation reference from pre-outcome histories and projects it into the current window's feasible set. The abstract's positive claim is structural: on SensorScope the projection is worth +0.768 percentage points of group mismatch over uniform weights. The abstract states that the protocol table is not an RMSE win. The ceiling section bounds recoverable prediction gain inside the weight class at the server step of that grid. The limitations section now reports an Adam replacement of that server step on NSW-Traffic: oracle-margin headroom on RMSE_μ is −1.49% with interval [−5.42%, +1.76%] and an 80% minimum detectable effect of 5.80% (15 seeds). The same runs reduce Δ_group by 0.0079 and Δ_{c-s} by 0.0099. The conclusion repeats that the RMSE_μ interval contains zero and that those runs reduce the two mismatches.

## Likely stance and calibrated score

**4/10, lean reject.** The structural account is the part a sympathetic reader can defend. The quantity the introduction sets up, deployment-target prediction, does not move by a detectable amount once the model is actually trained, and the absolute skill of the main RMSE table is still not on the page. Confidence is 4 on the NSW-Traffic paragraph and the two result files, and 3 on the proofs, the Holm tables, and related work.

## Quantitative scorecard

| Dimension | Score | Confidence | Deduction | Repair condition | Expected movement |
|---|---:|---:|---|---|---|
| Originality | 3 | 3 | The projection into a window feasible set is a real object. The surrounding program is close to participation reweighting, and this pass did not re-search prior art. | A literature pass that names the nearest aggregator and states the delta in one paragraph. | 3 → 4 only if that delta is sharper than the current abstract. |
| Significance | 2 | 4 | Prediction, the deployment quantity, has no detectable oracle-margin headroom. The SensorScope structural margin is 0.768 percentage points. On the Adam runs the mismatch reductions are 0.0079 and 0.0099. | Keep the paper as a negative measurement on prediction and a structural projection result, and show the absolute skill of RMSE_μ. | 2 → 3 if that scope is the contribution a TMC reader is asked to use. |
| Soundness | 4 | 4 | The learner-versus-weighting cause is gone. L2218–2221 still states a 2.8%–3.0% gap to a centralized model without stating that the reference is a short Adam run and the federated step is one normalized SGD step. | Name the two optimizers and the step budgets in that sentence, or delete the gap. | No change expected from wording alone. A matched-optimizer central run would be a different claim. |
| Evidence | 3 | 4 | Table RMSE values near 7.94 (SensorScope) and about 1.11 (U-Air) are not placed next to the training-mean or the test-mean constant. NSW-Traffic under Adam is an interpretable null: the interval contains 0 and the detectable effect is 5.80%. The mismatch reductions were scored after RMSE_μ was the endpoint. | Put the per-split target mean and a constant predictor beside RMSE_μ. Leave the mismatch numbers labeled as a later readout of the same runs. | 3 → 4 if the relative structural claims stay and the constant is disclosed. Disclosure will make the absolute RMSE look worse; that is the point of the repair. |
| Clarity | 3 | 4 | The new NSW-Traffic sentences state the null. They sit inside a limitations paragraph that also carries arrival bias, masking, deletion, and certificates. A reader still cannot see that the SensorScope test mean is far from the training mean. | One sentence at the RMSE definition: training and test target means on each block. | 3 → 4. |
| Reproducibility | 3 | 3 | Adam's step size and moment coefficients are in the text. The availability section does not point at the fifteen-seed runs. | Name the run directory and the seed range next to the existing bundle sentence. | 3 → 4. |
| Related work | 3 | 2 | No new literature search in this pass. | Insufficient evidence for a missing-citation finding. | Unchanged until a search is done. |

Weighted dimension mean: 3.05 / 5. The stance is not that mean. It is 4/10 because the unresolved decision is whether a TMC method paper can stand on a small structural projection and an explicit prediction null.

## Top strengths

- The abstract already refuses an RMSE win and locates the gain in the projection onto the feasible set (L79–L89).
- The ceiling is now scoped to the weight class at the server step of the grid (L2128–L2130), and the NSW-Traffic Adam result is the measurement that belongs there.
- The Adam numbers in L2222–L2232 match `TE1_VERDICT.json` and `TS1_SUMMARY.json`: mean H −0.014921, interval [−0.054230, +0.017568], MDE80 0.058027, Δ_group mean difference 0.007875, Δ_{c-s} mean difference 0.009940. The text says the mismatch contrasts were scored after the prediction contrast. That sentence is doing real work.
- K_r ≤ 3 on 15.1% of active windows matches the confirm-set share 0.150819. The feasible-set paragraph on SensorScope and U-Air still explains why those blocks cannot show a weight effect.

## Major/fatal concerns

No fatal invalidity of a printed theorem was established in this pass. The decision-relevant concern is evidence plus significance.

1. **Absolute RMSE is still uninterpretable on the two main blocks.** SensorScope training-split target mean is 0.301 and the test mean is 7.657; the best constant on the test labels is 2.088. U-Air is standardized on the training split, so its training mean is 0, and the test mean is −0.807, with a test-label constant of 0.678. None of these means appear in `main.tex`. A reader of Table III sees 7.94 and 1.11 and cannot tell skill from a level shift. The relative columns are invariant to a common shift. The omission matters because the introduction frames the work as completion quality.
2. **The prediction null is real, and it is coarse.** On NSW-Traffic the model can leave the constant: FedAvg under this Adam step is about 0.83 against a constant near 1.01 on the earlier screen, and the confirm headroom against the oracle-margin arm is −1.49% with an interval that reaches only +1.76%. The paper reports the headroom and the detectable effect. It does not report the absolute RMSE of those fifteen runs. "No detectable headroom" is the right claim next to a 5.80% detectable effect. It is not a proof that the effect is smaller than 0.5%.
3. **The mismatch reductions are a later readout.** L2227–L2230 says so. Fourteen of fifteen Δ_group differences are positive; one (seed 30012) is −0.00265. The intervals exclude 0. The reductions are about 2% of mismatch levels near 0.36 and 0.51. They do not replace the prediction endpoint, and they were not the endpoint fixed before the runs.
4. **L2218–2221 still pairs two different trainers.** Window FedAvg at the original step is 2.8%–3.0% above a centralized model on the same delivered data. The federated step is one normalized update per window. The centralized reference is Adam for a short minibatch budget. The paragraph no longer treats that gap as proof that the learner, rather than the weights, is the cause. The gap itself remains an unequal comparison.

## Writing and presentation concerns

- L2198–L2232 is one paragraph of arrival bias, masking, the original server step, the Adam replacement, and the later mismatch readout. The Adam result is the claim. It should be its own paragraph. This is presentation, not a new scientific hole.
- The conclusion sentence at L2258–L2261 is consistent with the limitations. It does not restate the 5.80% detectable effect, so a reader who stops at the conclusion can miss how coarse the null is.

## Format/venue concerns

The current build is 18 pages. This pass did not audit the template, anonymity, or the bibliography. The author line was not re-checked.

## Multi-reviewer panel

Reviewer: Best-justified
Lens: strongest accept case
Score / score tendency: 6/10 if the paper is read as a structural projection plus an explicit prediction null
Confidence: 3
Main positive signal: L79–L89 and L2222–L2232 agree. The method does not claim an RMSE win, and the Traffic measurement supports that refusal after the server step is replaced.
Main negative signal: the structural margin a reader can use is 0.768 percentage points on SensorScope, and 0.0079 on the Adam runs.
Evidence basis: abstract; limitations paragraph; TE1 and TS1 files
Score-change condition: disclose the split means and the constant next to RMSE_μ without turning the relative structural results into an absolute-skill claim.

Reviewer: Critical
Lens: strongest reject case
Score / score tendency: 3/10
Confidence: 4
Main positive signal: the null is printed, including the interval and the detectable effect.
Main negative signal: the introduction asks for completion under a deployment target. The measured deployment error does not improve, and on SensorScope it is not shown against a constant a reader can compute from the training mean.
Evidence basis: L71–L89; L2213–L2232; split means from the processed targets used by the scoring path
Score-change condition: either a deployment quantity that changes a decision by more than its own detectable effect, or a contribution statement that does not depend on prediction improvement. The second is partly done. The first is not in these runs.

Reviewer: Method / Soundness
Lens: causal claims and the optimizer comparison
Score / score tendency: 4/5
Confidence: 4
Main positive signal: L2230–L2232 no longer names the federated learner as the cause. The bound at L2128 is the weight class at a stated server step.
Main negative signal: L2218–2221 still reports the centralized gap across optimizers.
Evidence basis: those lines; the known central trainer is Adam for a short budget, while the federated update is one normalized step
Score-change condition: attribute that gap to the two update rules, or remove it.

Reviewer: Evidence / Experiment
Lens: whether the numbers support the claim now printed
Score / score tendency: 3/5
Confidence: 4
Main positive signal: the printed Adam headroom matches the verdict file. The mismatch intervals exclude 0 and the paper says they were scored afterwards.
Main negative signal: no constant beside the main RMSE table. The 5.80% detectable effect means the Traffic null cannot police a 0.5% prediction effect.
Evidence basis: TE1_VERDICT.json; TS1_PAIRS.csv; absence of a constant in main.tex
Score-change condition: add the constant and the split means. Do not add seeds to chase a 0.5% RMSE effect at this paired standard deviation.

Reviewer: Novelty / Positioning
Lens: prior art
Score / score tendency: insufficient evidence for a missing-paper finding; tendency 3/5 on the abstract's own delta
Confidence: 2
Main positive signal: the abstract's delta is the projection onto the feasible set, not a generic federated averager.
Main negative signal: no new search, so no named collision and no clearance.
Evidence basis: abstract only
Score-change condition: a search. Until then this role does not move the stance.

Reviewer: Writing / Clarity
Lens: whether the claim is recoverable
Score / score tendency: 3/5
Confidence: 4
Main positive signal: a reader who reaches L2224–L2232 can recover the null and the later mismatch readout.
Main negative signal: that reader still cannot recover why SensorScope RMSE sits near 7.9.
Evidence basis: L1600–L1604 states standardization for U-Air and NSW-Traffic and physical units for SensorScope, and does not state the split means
Score-change condition: the split-mean sentence at the metric definition.

Reviewer: Ethics / Reproducibility
Lens: audit of the new numbers
Score / score tendency: 3/5
Confidence: 3
Main positive signal: the Adam coefficients and step size are printed. The datasets are cited.
Main negative signal: the availability section does not name the fifteen-seed directory.
Evidence basis: L2222–L2224; L2263–L2274
Score-change condition: add the path and the seed range.

### Panel synthesis

Agreement: the prediction claim is a null, and the current text mostly says so. The structural projection is the remaining positive claim. Nobody treated the old learner-cause sentence as still present.
Disagreement: the best-justified reading would accept a negative measurement paper at 6/10 after the constant is disclosed. The critical reading rejects because the deployment error does not improve and the structural effects are small.
Decisive accept axis: none. The theory-plus-projection case is not strong enough, on the numbers in the abstract, to carry a TMC accept by itself.
Decisive reject axis: significance of the prediction problem the paper starts from, given a measured null whose detectable effect is 5.80%, plus absolute RMSE that a reader cannot interpret.
Unresolved evidence: proofs and Holm tables were not re-derived; related work was not searched.
Final calibrated stance: 4/10, lean reject.

## Concern-to-action table

| Concern | Severity | Where | Action | Owner |
|---|---|---|---|---|
| Split means and a constant predictor are absent beside RMSE_μ | Major | metric definition near L1600; Table III | Report training mean, test mean, and the constant on the same weights. Do not change the relative structural claims in the same edit. | ccf-paper-writer |
| Centralized gap mixes two trainers | Moderate | L2218–L2221 | Name both update rules, or delete the gap. | ccf-paper-writer |
| Adam absolute RMSE is absent | Moderate | L2224–L2226 | State the two arms' RMSE_μ levels next to the −1.49% headroom, so the null is not read as two untrained models. | ccf-paper-writer |
| Mismatch readout is easy to promote | Moderate | L2227–L2230 and L2258–L2261 | Keep the "scored after" sentence. Do not move these numbers into the abstract as a prespecified win. | ccf-paper-writer |
| New runs are not in the availability section | Moderate | L2263–L2274 | Name the directory and seeds 30006–30020. | ccf-paper-writer |
| Limitations paragraph carries too many results | Minor | L2198–L2232 | Give the Adam result its own paragraph. | ccf-paper-writer |
| Related-work clearance | Unresolved | — | Search before any novelty claim is raised or lowered. | ccf-literature-searcher |

## Recommended next CCFA owner

`ccf-paper-writer`, for the constant, the split means, and the centralized-gap sentence. `ccf-integrity-auditor` after those numbers are in the file. A literature search is optional and was not done here.

## Checks run

- Current limitations and conclusion text read at the lines cited.
- TE1 verdict and TS1 summary compared with the printed percentages.
- TS1 pair file counted: 14/15 Δ_group differences positive; seed 30012 is −0.00265.
- Prose-pattern script and a two-pass compile were not re-run in this review. The prior compile of this manuscript was 18 pages.
- No literature search. No proof re-derivation.

## Unresolved or unverified

- Whether every Holm statement and every table cell in the main results still matches its source file.
- Whether a closer aggregator already states the feasible-set projection.
- The author-anonymity and template audit.

## Output self-check

- Stance 4/10 is the reject axis above, not the average of the panel.
- Evidence 3 and Significance 2 each have a repair condition.
- The printed Adam numbers were checked against the verdict files.
- No manuscript text was edited by this review.

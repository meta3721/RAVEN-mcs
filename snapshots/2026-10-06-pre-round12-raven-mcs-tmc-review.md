# RAVEN-MCS — IEEE TMC review (current manuscript)

```text
Mode: full (scientific + writing + format). Assessment only; no prose rewrite.
Date: 2026-10-04
Venue and assumptions: IEEE TMC journal revision, method-plus-measurement paper.
  Page budget treated as TMC regular 12 pp, with the project's MOPC allowance up to 18 pp.
  Frozen score contract inherited from TMC-J-R4 (not modified):
  dimensions Originality / Soundness / Evidence / Clarity / Reproducibility /
  Significance / Related work / Terminology;
  weights 0.10 / 0.20 / 0.25 / 0.15 / 0.10 / 0.10 / 0.05 / 0.05;
  anchors 1-5; overall 1-10; |weighted delta| < 0.05 = unchanged.
Manuscript: TO_OVERLEAF_paper_tmc_r1_clean/main.tex (sha256 prefix 88ECD743…,
  2026-10-04 10:06, as frozen by the round-10 record audit), appendix.tex, supplemental.tex.
Prior review used only as the comparison baseline: ccfa-review-reports/raven-mcs-tmc-review-round9.md.
This pass re-read the abstract, contributions, (P2), the attribution and trained-rule
sections, the ceiling, the limitations, the availability paragraph, and Appendix K.
It did not re-derive the proofs and did not run a new literature search.
```

## Paper summary

RAVEN-MCS separates a public deployment target from the arrival law induced by opportunity, observation, and usable-update delivery, builds a selection-corrected reference from pre-outcome histories, and maps that reference into the current window's feasible aggregation set. The paper proves that the two risks are not interchangeable, and that an ideal sequential correction recovers compatible target mass without proving that deployment-target risk is optimized.

The empirical claim, as the current text states it, is narrower than the method's name. Against uniform server weights, the remaining structural gain is the projection of the corrected reference onto the feasible set: +0.768 pp of group mismatch on SensorScope, with the Design factor ζ worth a further +0.922 pp on that block. Uniform weights already close 68.96% (SensorScope) and 83.07% (U-Air) of the FedAvg-to-RAVEN group gap. The other terms of (P2), and debt at the frozen strength, stay inside a pre-registered ±0.10 band. No prediction contrast survives Holm. On U-Air, turning Design on costs 6.885% of RMSE_μ. City Scanner's non-inferiority test is reported as untestable (power about 0.15), and the deletion question is reported as unresolved.

## Likely stance and calibrated score

**Borderline negative, 5/10.** The manuscript is now internally consistent about what it measured. That consistency does not supply the missing result: alignment of structural mass is shown; conversion of that alignment into prediction is not; and the objective terms that define the calibration program are not shown to be necessary for the structural gain. The strongest unresolved weakness is still Evidence (weight 0.25).

Relative to the round-9 review of the pre-P0 text: **unchanged**. Weighted readiness sum 3.25 → 3.25 (delta 0.00, below the 0.05 threshold). The P0 sentences discharged the round-9 wording defects H1, H2, H3, H4, H6, and H9. None of those repairs moves a dimension across an anchor, because the Clarity raise also required the still-open "recoverable" disambiguation, and Evidence did not move.

## Quantitative scorecard

Absolute readiness of the current manuscript. Confidence is separate from the score.

| Dimension | Score | Weight | Confidence | Deduction | Repair condition | Expected movement |
|---|---|---|---|---|---|---|
| Originality | 2 | 0.10 | medium | The added objects are deployment-target semantics, a three-layer pre-outcome factorization, and a finite-window feasible set. Convex matching to a known composition and two-stage IPW are prior ingredients, and the paper says so (L258–263). The nearest public neighbours (FedPALS, FedIPW) were not re-searched this pass. | A constraint-and-information mapping that states an irreducible difference from those two lines. | +1 Originality, not enough alone to move the stance. |
| Soundness | 5 | 0.20 | medium | No deduction on the claims re-read this pass. The (P2) paragraph now matches `MYOPIC_DIAG.json`: the ℓ₁ surface is flat (median range 1e-13), and the tie-break, not the group objective alone, moves the endpoint by 0.0107 pp (1.05140 vs 1.06213). Proofs were not re-derived. | None on this axis from the current text. A proof error found on a fresh derivation would lower it. | none |
| Evidence | 3 | 0.25 | high | No prediction contrast survives Holm (L2096–2101: SensorScope p_Holm = 1.000; U-Air best raw p = 0.027, Holm 0.133). The ceiling section bounds the recoverable RMSE gap at \|H\| ≤ 0.217% on U-Air. Uniform weights close most of the structural gap. City Scanner H2 is untestable at the declared 2% margin (power 0.120 at r = 1, at most 0.153). The deletion primary is inconclusive. | One pre-registered endpoint, on a setting where the headroom is large enough to detect, where alignment changes prediction or a deployment decision. Adding seeds on the current blocks will not do this: the ceiling says the headroom is below the detectable effect. | +1 Evidence, and this is the change that would move the stance to 6. |
| Clarity | 4 | 0.15 | high | The contribution list, the (P2) mechanism, and the attribution paragraph now say the same thing. What remains is density: contribution 3 still carries the verdict, the prediction caveat, and the κ exclusion in one bullet, and "recoverable" means both "uniform weights close this gap" (L1819) and "the ceiling on RMSE gain" (L2106). | Split that bullet, and give the two uses of "recoverable" different words. | +1 Clarity. Weighted sum would become 3.40 (improved vs round 9) without moving the 5/10 stance. |
| Reproducibility | 2 | 0.10 | medium | The availability paragraph (L2203–2221) inventories Table II, the Holm family, T-Drive, NSW, and City Scanner. It does not name the ladder, band-decision, debt-strength, or trained-rule artifacts that carry +0.768, +0.922, the ±0.10 band, and ε_impl. The round-10 bundle audit found those files under `w1/` and found `verify.py` clean; a reader of the paragraph alone cannot find them. | Name that subtree, or the index file, in the availability paragraph. | +1 Reproducibility. |
| Significance | 2 | 0.10 | medium | The large measured effect is the Design switch on one block, and it is a cost on RMSE_μ as well as a gain on client–stratum mismatch. The paper's own decomposition says most of the FedAvg structural gap is uniform weights. | A task where the structural gain changes a quantity a deployment would act on. | +1 Significance, only together with the Evidence repair. |
| Related work | 3 | 0.05 | medium | Positioning is honest about prior ingredients. The irreducibility claim against the closest convex-match and two-stage IPW papers is still a sentence, not a mapping. Not re-searched this pass. | The mapping named under Originality. | +1 if the mapping shows a real difference; −1 if it does not. |
| Terminology | 3 | 0.05 | high | ε_impl is now in one unit system (Appendix K, L105–120): at most 2.42e-5 in Δ units, 1.21e-3 pp, 17% of the frozen debt contrast and 0.13–0.16% of the two headline contrasts. The remaining defect is the double use of "recoverable". | One sentence that renames one of the two uses. | +1 Terminology, bundled with the Clarity repair. |

Weighted sum = 0.10×2 + 0.20×5 + 0.25×3 + 0.15×4 + 0.10×2 + 0.10×2 + 0.05×3 + 0.05×3 = **3.25**. Overall **5/10**.

## Top strengths

- The central negative results are printed, not implied. The abstract, contribution 4, §VII, and the conclusion agree that the projection and the Design factor carry the structural gain, and that the other frozen terms do not.
- The (P2) mechanism now cites its own measurement. Flatness at 1e-13 and the 0.0107 pp tie-break are both on the page, and both match `results_w1_ladder/round_v3/MYOPIC_DIAG.json`.
- Limitations match the later experiments. City Scanner power "about 0.15" matches the measured 0.120–0.153. The five-model-seed trace outlier matches the B0-b probe (+24% to +38%). "Deletion unresolved at n = 10, r = 3" matches `C1_PRIMARY.json`'s inconclusive reading.
- Appendix K's ε_impl arithmetic is internally consistent with pp = Δ/2×100, which the previous draft was not.

## Major concerns

**E1. Alignment is not shown to buy accuracy.** Severity: major. Evidence basis: L2096–2101 and §VII-F (L2106–2124). No registered prediction contrast survives Holm. The ceiling measurement puts the oracle gap at most 0.217% on U-Air, inside or at the edge of the detectable effect. Affected criterion: Evidence, Significance. Fix class: new evidence, not wording. Owner: `ccf-experiment-designer`, then `ccf-paper-writer` only after a result exists. Score-impact condition: a pre-registered endpoint with headroom above the detectable effect, where the structural arm wins or is non-inferior on a decision quantity. Expected movement: Evidence 3→4 and the stance 5→6. Repeating the current blocks will not meet this condition.

**E2. The program the method is named for is not the part that moves the endpoint.** Severity: major for venue fit, not a correctness error. Evidence basis: L229–237, L247–255, L1826–1856. At the frozen configuration the objective terms beyond the reference anchor, and the debt recursion, are not shown to contribute; imposing C_r and projecting onto it is. Uniform weights close 68.96% and 83.07% of the FedAvg group gap. The paper states this. The consequence is that a TMC reader is being asked to adopt a calibration program whose measured content is a convex projection plus a configuration switch. Affected criteria: Significance, Originality. Fix class: either a setting where those terms move an endpoint, or a contribution statement that leads with the projection and the Design factor and treats (P2)'s other terms as the uniqueness device they are shown to be. The second is a writing change and does not by itself raise Evidence. Owner: `ccf-paper-writer` for the statement; `ccf-experiment-designer` if a new setting is attempted.

## Moderate concerns

**M1. "Recoverable" names two quantities.** L1819 uses it for the share of the structural gap that uniform weights close. L2106 uses it for the RMSE ceiling inside C_r. A reader can carry the first number into the second. Evidence basis: those two sites. Affected: Clarity, Terminology. Fix class: writing. Owner: `ccf-paper-writer`. Score-impact: Clarity 4→5 if this and the contribution-bullet split are done; stance unchanged.

**M2. The availability paragraph does not point at the artifacts for the new numbers.** L2203–2221 lists the frozen Table II bundle. The ladder files that support +0.768, +0.922, the band, and ε_impl sit in the bundle's `w1/` tree (round-10 audit: present, verifier clean) and are not named. Affected: Reproducibility. Fix class: one paragraph. Owner: `ccf-paper-writer`. Score-impact: Reproducibility 2→3.

**M3. The privacy sentence is still attached to the coverage-gate sentence.** L2174–2176 ends the limitations with "Design is not opened from Gate_t. Federated learning itself does not provide a privacy guarantee." The statement is right and is in the right section; the antecedent is wrong. Fix class: writing. Owner: `ccf-paper-writer`. No score movement by itself.

## Writing and presentation concerns

- Contribution 3 (L215–237) is one bullet that states a theorem, a negative verdict, a κ exclusion, and a pointer to a prediction table. It is where a reader decides what the method contributes. Split the verdict from the theorem.
- The Design-switch equation (L2040–2053) is correctly labelled as a chart fitted to one U-Air row. Keep that label next to any later citation of the 1.39 threshold so it is not read as a general law.
- The limitations paragraph (L2149–2176) is a list of unrelated caveats. It is accurate. It is hard to audit because each sentence changes subject.

## Format and venue concerns

- `main.pdf` is 17 pp (round-10 audit). That fits an 18 pp MOPC allowance and exceeds a 12 pp regular TMC article. The submission has to declare which track it is on. This is not charged as a technical defect.
- Anonymity is not applicable to a journal revision. Authors in the current source are not re-checked here.

## Claim–evidence audit

| Claim | Where | Evidence | Strength |
|---|---|---|---|
| Deployment and arrival risks are not interchangeable | Abstract; contribution 1 | Stated as a proof under differing laws | Adequate, conditional on the proof (not re-derived this pass) |
| Ideal sequential correction recovers compatible target mass and does not prove risk optimization | Abstract; contribution 2 | Theorem statement with A1–A3 | Adequate as a scoped theorem |
| The remaining structural gain is the projection; other frozen terms are inside the band | Abstract; contribution 4; L1826–1856 | 20 paired seeds, bootstrap CIs, Holm, ±0.10 band; 0.0107 pp tie-break matches `MYOPIC_DIAG.json` | Strong for the structural claim; the claim is now the right size |
| Design on costs 6.885% RMSE_μ and gains 4.990% client–stratum mismatch on U-Air | Abstract; L1992–1996 | Holm-significant ablation on that block | Adequate for that block; the paper does not generalize it |
| No Holm-significant RMSE win | Table III caption; L2096–2101 | The registered prediction family | Strong as a negative result |
| Trained projection rules improve structure and not prediction | L2079–2101 | 20 seeds; Holm on both endpoints | Adequate, and correctly marked as new rules rather than frozen RAVEN |
| City Scanner non-inferiority is untestable; deletion is unresolved; one trace is a trace-level outlier | L2162–2169 | `A1_POWER.csv` (power 0.120–0.153); `C1_PRIMARY.json` (inconclusive); B0-b five model seeds | Adequate, and matched to the artifacts |
| ε_impl ≤ 2.42e-5 and the printed ratios | Appendix K | Consistent with pp = Δ/2×100 and the two headline contrasts | Adequate |

## Multi-reviewer panel

```text
Reviewer: Best-justified
Lens: strongest defensible accept case
Score / score tendency: 6/10
Confidence: high
Main positive signal: the structural attribution is measured, pre-registered, and no longer over-claimed.
Main negative signal: a measurement paper still has to show that the measurement matters to the venue's decision.
Evidence basis: L79–85, L239–255, L1811–1856, MYOPIC_DIAG.json
Score-change condition: a deployment quantity that moves with the projection.

Reviewer: Critical
Lens: strongest reject case
Score / score tendency: 4/10
Confidence: high
Main positive signal: the negative results are disclosed, so this is not an over-claim rejection.
Main negative signal: the named calibration program is not shown to be necessary, and prediction does not move.
Evidence basis: L229–237, L2096–2124
Score-change condition: the Evidence repair in E1. Wording repairs will not move this reviewer.

Reviewer: Method / soundness
Lens: whether the causal sentences match the diagnostics
Score / score tendency: 6/10 on soundness; does not raise the paper's stance
Confidence: medium (proofs not re-derived)
Main positive signal: the flat-surface sentence and the 0.0107 pp tie-break now agree with MYOPIC_DIAG.json.
Main negative signal: none found in the sections re-read. Insufficient evidence on the proofs themselves.
Evidence basis: L964–980; MYOPIC_DIAG.json d_myo_tb = 1.05140, d_unif = 1.06213
Score-change condition: a counterexample in the proof, or a diagnostic that contradicts L975–977.

Agreement: the structural result is real and correctly scoped; the prediction result is a measured null.
Disagreement: whether honest scoping of a null is enough for TMC. The sympathetic reviewer says the measurement is the contribution. The critical reviewer says the venue's decision quantity did not move.
Decisive accept axis: a task where the projection changes a decision, not another structural ablation.
Decisive reject axis: Evidence. Uniform weights plus a projection explain the structural table, and RMSE does not follow.
Unresolved evidence: irreducibility versus FedPALS and FedIPW (not re-searched); the proofs (not re-derived).
Final calibrated stance: 5/10, borderline negative. The critical axis decides, because it is the one the venue scores on.
```

## Concern-to-action table

| ID | Severity | Action | Owner | Stance effect |
|---|---|---|---|---|
| E1 | Major | Do not add seeds on SensorScope, U-Air, or City Scanner to chase a prediction win. The ceiling and the City Scanner power calculation say those tests cannot succeed. A new setting needs headroom above its own detectable effect, pre-registered before the run. | ccf-experiment-designer | The only action that can move 5→6 |
| E2 | Major | Lead the contribution list with the projection and the Design factor. Keep (P2)'s other terms as the uniqueness device. | ccf-paper-writer | None by itself |
| M1 | Moderate | Rename one of the two uses of "recoverable". Split contribution 3. | ccf-paper-writer | Clarity 4→5; stance unchanged |
| M2 | Moderate | Point the availability paragraph at the `w1/` ladder artifacts. | ccf-paper-writer | Reproducibility 2→3; stance unchanged |
| M3 | Minor | Detach the privacy sentence from the Gate_t sentence. | ccf-paper-writer | None |

## Recommended next CCFA owner

`ccf-paper-writer` for M1–M3 only. Those edits make the current claims easier to audit and do not change the stance. `ccf-experiment-designer` owns E1, and only if a setting with detectable prediction headroom is actually proposed. Do not treat another Holm pass on the existing blocks as that setting.

## Checks run

- Re-read current `main.tex` abstract, contributions, (P2) L944–982, attribution L1811–1856, trained rules L2079–2101, ceiling L2103–2146, Design gate L2007–2029, limitations L2149–2176, availability L2203–2241.
- Re-read Appendix K (`supplemental.tex` L94–121) and checked ε_impl against pp = Δ/2×100: 2.42e-5 Δ = 1.21e-3 pp; 2.42e-5 / 1.46e-4 = 17% of the 0.0073 pp debt contrast; 2.42e-5 against 0.922 pp and 0.768 pp is 0.13% and 0.16%.
- Checked L975–977 against `results_w1_ladder/round_v3/MYOPIC_DIAG.json` (`d_myo_tb` 1.051402, `d_unif` 1.062134).
- Checked L2162–2169 against `results_gatekeeping/round_v1/EXECUTION_REPORT.md` (power 0.120–0.153; B0-b five model seeds; Part B primary inconclusive).

## Unresolved or unverified

- Proofs in §VI were not re-derived.
- FedPALS and FedIPW were not re-searched; the related-work score carries the previous pass's uncertainty.
- The feasibility-violation range "8.23 to 21.73" at L1834 was not re-located in the evidence tree this pass. Round 9 left it unverified rather than contradicted. It stays unverified.
- Page count and bundle hashes are taken from the round-10 record audit, not re-measured.

## Output self-check

- Section order follows the full-review contract, with the claim audit placed before the panel.
- The 5/10 stance matches the Evidence deduction and the panel's decisive reject axis.
- Relative progress (unchanged, delta 0.00) and absolute readiness (3.25, 5/10) are stated separately and not averaged.
- No cell is filled with an unmeasured result. The City Scanner and ε_impl numbers cited above were checked against the named files.
- H1, H2, H3, H4, H6, and H9 from round 9 are treated as discharged in the current text, not re-opened.

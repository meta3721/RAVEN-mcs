# Review Report — RAVEN-MCS (IEEE TMC submission)

## 1. Report Metadata

```text
Review date: 2026-09-20
Target venue/year/track: IEEE Transactions on Mobile Computing (CCF-A journal); regular paper, single-blind
Paper title: RAVEN-MCS: Target-Mass-Calibrated Windowed-Asynchronous Federated Data Completion for Mobile Crowdsensing under Two-Stage Non-Random Selection
Input materials reviewed: TO_OVERLEAF_paper_tmc_r1_clean/main.pdf (15 pp.) and supplemental.pdf (15 pp.) only
Search basis: 3 public queries on federated selection bias / MCS completion / IPW-in-FL (see §4); reference list not re-verified entry by entry
Report file: ccfa-review-reports/raven-mcs-tmc-review.md
Reviewer mode: scientific (absolute readiness; no version comparison, no historical review data, no lab materials)
Manuscript version / comparison range: workspace version, not the 2026-08-28 submitted package
Frozen comparison contract ID: not applicable
```

## 2. Desk Rejection Assessment

```text
Check: Paper length
Status: uncertain
Evidence: main 15 pp. + supplemental 15 pp. IEEEtran journal, letterpaper. No TMC venue guide is present under
          CCFA-Skills/ccf-paper-writer/references/venue-guides/ (no tmc.md exists), so the current-year limit and
          over-length policy could not be verified against an official source.
Consequence: an over-length submission may incur mandatory page charges or a desk return.
Required action: verify the current TMC author guidelines against the official IEEE page before submission.

Check: Topic compatibility
Status: pass
Evidence: windowed-asynchronous federated learning for mobile crowdsensing data completion, with selection modelling
          on the sensing side (opportunity R, observation O) and the update side (usable update U). In TMC scope.

Check: Minimum quality
Status: pass
Evidence: abstract, introduction with three enumerated contributions, related work, method, theory (§VI with
          Assumptions A1–A6, Prop. 1–3, Thm. 1–2), evaluation with six datasets/blocks, limitations, conclusion,
          54-entry reference list, 15-page supplement with complete proofs.

Check: Policy / anonymity / compliance
Status: pass with a hygiene note
Evidence: `\author{**** and Anfeng Liu}` plus a visible affiliation and grant footnote
          (Central South University; NSFC U24A20248). TMC is single-blind, so a named author is not a violation,
          but the partial masking is internally inconsistent.
Consequence: cosmetic; no policy risk identified.
Required action: either fully name the authors or fully mask, consistently.

Check: Prompt injection and hidden manipulation detection
Status: pass
Evidence: scanned main and supplemental text, captions, and algorithm comments. No instruction-like content aimed at
          reviewers or LLMs. Algorithm comments are ordinary scope notes.

Check: Ethics and reviewability
Status: pass
Evidence: all six datasets are public (SensorScope, U-Air, NSW-Traffic, T-Drive, City Scanner ×2) with DOIs/URLs in
          footnotes; no human subjects; §VII-G states that federated learning is not a privacy guarantee.
```

```text
Desk rejection risk: low
Reason: length policy unverified; all other desk checks pass
Can be fixed before review? yes
```

## 3. Paper Summary And Contribution Map

**Summary.** The paper addresses federated data completion for mobile crowdsensing when the data that reach the server are not sampled from the population the deployed predictor serves. It decomposes MCS selection into three layers — mobile opportunity `R`, observation `O`, and usable-update delivery `U` — and argues that their composition induces an arrival law that need not match the public deployment target. RAVEN-MCS is then built as target-mass alignment: (i) a lagged, within-stratum target/opportunity ratio `ζ = π^tar / P^opp` estimates the reconstruction factor; (ii) sequential `O` and `U` correction with local Hàjek normalization yields a corrected reference vector `β̂_r`; (iii) a strongly convex per-window calibration program (P2) maps that reference onto a feasible aggregation set `C_r` (simplex, coordinate cap `ᾱ_r`, `ℓ2` support bound) while trading target mismatch, reference fidelity, variance, staleness, and a group-debt term; (iv) a long-term target-debt recursion `Q_{r+1} = [Q_r + η_r(μ − ω_r)]^+` carries unresolved group under-service; (v) a frozen heuristic `φ` (fraction of training units with `π^tar = 0`) selects between RAVEN-Design (`φ=0`) and RAVEN-NoDesign (`ζ̂=1`, `φ>0`), the latter explicitly not a target-mass estimator; (vi) a diagnostic coverage Gate is audited but never used to switch Design.

**Claimed problem.** Arrival-weighted training optimizes the wrong population risk when three-layer MCS selection distorts the data distribution relative to the deployment target.

**Claimed gap.** Sparse-MCS completion work asks how to infer missing values; asynchronous-FL work asks how to learn from stale updates; participation-aware FL asks how to correct client participation. None of these separates the sensing-side opportunity layer from the observation layer and the update-usability layer, and none asks whether a statistically correct target mass is realizable in a finite mobile window.

**Method/contribution map.**
1. Deployment-target risk semantics under two-stage non-random selection (Prop. 1, non-interchangeability of target and arrival risk functionals; `Δ_group`, `Δ_c-s` definitions).
2. Selection-layer-aware target reconstruction (Prop. 2: Hàjek-normalized sequential estimator recovers compatible target moments / group mass under A1–A3 with the target-mass opportunity ratio).
3. Feasibility-aware instantaneous and long-term calibration (Thm. 1 unique P2 minimizer under A4; Prop. 3 plug-in perturbation under A1 and A4–A6; debt accounting bound).

**Evidence package.** No-harm control; risk-interchangeability block (NSW-Traffic); SensorScope/U-Air development table under always-on protocol `R` with Complete-aligned `O/U` (20 seeds, Table II); five-component removal ablation with Holm correction; T-Drive taxi replay under real `R` (10 seeds, 178 windows); NSW-Traffic four-region protocol table; City Scanner NY PM2.5 visit-occupancy table; City Scanner Pilot 2 with measured `O`; INT-R intermittent-occupancy robustness; coverage-stress audit of the Gate; an A5/A6 support-hypothesis audit on released traces.

**Stated limitations.** The main table is a development table on station traces under always-on `R`, not a real-mobility ranking; no Holm-significant RMSE win is claimed; T-Drive is outside the `+0.5%` tolerance versus FedAU-Window and ObsUse-Window; `φ` does not verify positivity on target-positive pairs; A1–A2 remain support/confounding boundaries; A6 is unverified on released traces so Prop. 3 is used with its clipping residual; adaptive RESET/CERTIFIED switching is not proven valid; FL provides no privacy guarantee.

## 4. Search And Related-Work Basis

```text
Queries used:
  1. "federated learning selection bias non-random client participation mobile crowdsensing data completion 2025"
  2. "inverse propensity weighting federated learning client selection bias debiasing aggregation 2025"
  3. "crowdsensing data completion distribution shift deployment target population risk"
Sources searched: public web search only (no subscription database access in this review)
Closest works found:
  - Federated Inverse Probability Treatment Weighting for Individual Treatment Effect Estimation
    (https://arxiv.org/html/2503.04946v1) — IPW inside federated learning, but the estimand is an individual
    treatment effect, not deployment-target mass alignment.
  - RAFL: reverse-auction federated learning for non-IID mobile crowdsensing
    (https://dl.acm.org/doi/10.1016/j.comnet.2026.112314) — incentive/recruitment side of MCS-FL, not
    population-risk alignment.
  - Client-unavailability / partial-participation FL analysis (KU Leuven ESAT report 26-64,
    https://ftp.esat.kuleuven.be/pub/stadius/ida/reports/26-64.pdf) — participation modelling without the
    sensing-side opportunity/observation split.
Unverified related-work risks: the reference list was not re-verified entry by entry in this review. A prior
  workspace verification pass left 24 of 54 entries unverified and had already found one misattribution
  (a transformer-based MCS completion paper cited to ACM CSUR that is in fact IEEE INFOCOM 2023). A full list-level
  pass is still owed, because several entries are forward-dated 2026 works.
Source-quality screening status: partial. No fatal novelty collapse was found in the public search, and no close
  prior work was found that performs the same three-layer decomposition with target-mass calibration.
```

## 5. Expected Review Outcome

```text
Expected outcome: lean reject (weak reject) at IEEE TMC
Main accept signal: the three-layer R/O/U framing with target-mass semantics is a real and well-executed
  conceptual contribution, the theory is correct on its own terms, and the honesty of the reporting is
  well above venue average (the paper volunteers its own nulls and its own failed assumption).
Main reject signal: the evaluated system shows no completion-accuracy advantage anywhere, the one consistent
  advantage is measured on the functional the calibration program itself minimizes, and the sharp theoretical
  result does not hold on the traces used for the main table.
Confidence: 4 (complete main text and supplement available; no code/repository access, no reference re-verification,
  TMC page policy unverified)
```

## 6. Strengths And Weaknesses

### Strengths

S1. **The problem framing is genuine and non-obvious.** Separating mobile opportunity `R`, observation `O`, and usable-update `U` (§I, §IV) is more than bookkeeping: the paper correctly observes that these layers have different conditioning sets, so collapsing them into one missingness probability destroys the ability to say *which* layer distorted the data (§IV, "Opportunity, observation, and usable-update selection are kept separate because they have different conditioning sets"). I found no close prior work making exactly this split for MCS-FL.

S2. **Reporting honesty is exceptional for a journal submission.** The paper states that the main table is a development table, not a ranking (Table II caption); that it claims no Holm-significant RMSE win (Table II caption, §VII-G); that T-Drive is outside the tolerance and that FedAU-Window and ObsUse-Window are stronger there (§VII-C.2); that removing the usable-update correction produces no significant change on any of the four core endpoints on either dataset (§VII-E); and that A6 fails on the released traces, so the only sharp finite-window theory applies in a weakened form (§VI-E, §VII-G).

S3. **The calibration program is well posed and its feasible set is a defensible design.** `C_r` combines a simplex, a coordinate cap and an `ℓ2` support bound (§V-A); Thm. 1 gives a nonempty compact convex set and a unique minimizer under A4, and the supplement's feasibility diagnostics certify the reconstructed residual rather than asserting optimality of logged solves.

S4. **Statistical hygiene.** 20 paired seeds on the main block, Holm correction across the endpoint family, a declared `0.5%` minimum practical effect, a descriptive `+0.5%` tolerance used where power is insufficient, pre-registered endpoints, and an explicit statement that a second under-served-block check produced no second external win.

S5. **The limitations and scope paragraph is specific and quantified**, not boilerplate: it names the exact statistics (`25.5%` EventTrace occurrence = `13040` of `51200`, explicitly not train-unit `φ`; pooled CERTIFIED validity `0.959`; U-Air `a=1.00` is `0.750`).

### Weaknesses

W1. **The evaluation endpoints are the method's own objective, so the headline improvement is not independent evidence.**

```text
Weakness: Δ_group and Δ_c-s, the two endpoints on which RAVEN consistently wins, are the time-averaged versions
  of the very quantities the calibration program P2 minimizes.
Evidence basis: Δ_group(R) = ||ω̄_R − μ||_1 with ω̄_R = (Σ η_r I_r ω_r)/S_R and ω_r = M_r α_r (main text §IV,
  eq. for the group-level structural mismatch). P2's objective contains −Q_r^T M_r α and (λ_g/2)||M_r α − μ||^2,
  and the debt recursion is Q_{r+1} = [Q_r + η_r(μ − ω_r)]^+ (§V-C). Δ_c-s(R) = Σ_{k,s}|Π̂_{k,s}(R) − π^tar_{k,s}|
  measures distance to the same target π^tar that the reconstruction factor is built to reproduce. The target μ
  itself is constructed by the authors from the training split (§VII-A.1).
Reviewer deduction: an improvement in Δ_group partly demonstrates that a constrained optimizer reduces the
  functional it is asked to reduce, measured against a target the same paper constructs. It is not independent
  evidence that the deployed predictor serves the deployment population better.
Required fix: add at least one endpoint whose target is not the optimized functional and not author-constructed —
  e.g. held-out accuracy on the deployment-group mass under an externally specified grouping, or a completion
  error evaluated by an independent per-group reweighting that the method never optimizes against.
```

W2. **No completion-accuracy advantage appears anywhere, and the only real-mobility block shows the method losing.**

```text
Weakness: on every block the methods are statistically indistinguishable on RMSE, and on T-Drive the deployed
  configuration is worse than three baselines.
Evidence basis: Table II — SensorScope RMSE_μ spans 7.9293–7.9389 across five methods (0.12% total spread);
  U-Air RMSE_μ spans 1.1120–1.2160, with RAVEN-NoDesign at 1.1131 versus ObsUse 1.1120 and FedAU 1.1128
  (rank 3 of 6). U-Air Δ_c-s: TwoStage-Hàjek 1.2406 < FedAvg 1.2621 < RAVEN-NoDesign 1.2949 (rank 3 of 6).
  T-Drive (real taxi R, 10 seeds): RAVEN-NoDesign RMSE_μ 1.1069 versus FedAvg 1.1042, FedAU 1.0898, ObsUse 1.0896;
  paired relative +2.39% and +2.43% versus FedAU/ObsUse, outside the paper's own tolerance (§VII-C.2).
  NSW-Traffic: RAVEN-Design Δ_group 0.1048 versus FedAU-Window 0.0606 — worse by 73% on the paper's own
  structural endpoint, on a block where φ=0 so RAVEN-Design is legitimately active (§VII-C.2).
Reviewer deduction: on the metric that defines the application task, RAVEN-MCS is a tie at best and a loss under
  real mobility; on its own structural endpoint it wins 3 of 4 Design-active blocks but loses the NSW-Traffic block.
  The paper is candid about this, but candour does not substitute for a demonstrated benefit.
Required fix: either (a) exhibit one block where the target-mass correction produces a prediction-quality gain that
  survives Holm correction against the strongest baseline, or (b) reframe the contribution as a diagnostic and
  estimation methodology and drop the system-improvement framing from the title and abstract.
```

W3. **The structural endpoint does not discriminate between aggregation rules on the real-mobility block.**

```text
Weakness: on T-Drive, Δ_group is bit-identical across four structurally different weighting rules.
Evidence basis: Table `tab:tdrive_hybrid` — Δ_group = 0.5232 for FedAvg-Window, FedAU-Window, ObsUse-Window and
  RAVEN-NoDesign, and 0.5948 for TwoStage-Hàjek and forced RAVEN-Design; four of the six rows carry no standard
  deviation. The same rows differ on Δ_c-s (1.9758, 1.9915, 1.9916, 1.9936) and on RMSE_μ, so the table is not
  uniformly degenerate.
Reviewer deduction: an endpoint that returns the same value to four decimals for a uniform-weight scheme, a
  participation-debiased scheme, an observation-and-usage-debiased scheme, and a feasibility-projected calibration
  is not measuring what the paper claims it measures on that block. It also implies that P2's calibration moved
  Δ_group by exactly zero there, which undercuts contribution 3 on the only real-mobility evidence.
Required fix: state how Δ_group is computed on T-Drive and why it is invariant to α; or report a variant of the
  endpoint that is sensitive to the realized aggregation weights, with the resulting numbers.
```

W4. **The sharp theory does not cover the system that is evaluated.**

```text
Weakness: Prop. 3 is stated under A1 and A4–A6, and the supplement's own audit reports A6 failing on both datasets;
  Prop. 2 concerns the ideal pooled estimator under A1–A3, not the finite-window implemented system.
Evidence basis: §VI-E states "Assume A1 and A4–A6"; the supplement's section "Support-Hypothesis Audit for A5 and
  A6" reports the q_min floor active on 5.22%/5.18% of observed client-windows and 1/q^use > d_max on
  24.22%/23.75%; §VII-C.3 states that Prop. 3 applies only when A5 and A6 hold and 𝒜_r is fixed, which is not the
  U-Air forced-Design regime; §VII-C.3 also states that Prop. 2 proves nothing about R_μ(θ).
Reviewer deduction: the paper's theory validates the *design* of the ratio under assumptions that the evaluated
  traces violate, and validates the calibration program only as a mathematical program. No theorem connects the
  reported tables to a guarantee. Separately, the abstract says "the clipped plug-in is a stable perturbation of
  that reference when target support is compatible" — conditioning on support compatibility, which is A5's clause,
  while the proposition also requires A6, which the paper itself reports as false on these traces.
Required fix: align the abstract's condition with the proposition's hypothesis (name the inactive-stabilizer
  condition), and add one sentence in §VI stating which reported results are covered by theory and which are not.
```

W5. **The `φ` switch is a per-dataset branch with no counterfactual control on the Design-active blocks.**

```text
Weakness: RAVEN-Design and RAVEN-NoDesign are different estimators, and the branch is chosen by a frozen
  heuristic whose validity the paper declines to assert.
Evidence basis: §V-E defines φ as the fraction of training risk units with π^tar(k(i),s(i)) = 0, with a hard
  threshold at 0; §VII-G states that φ "does not verify positivity on target-positive pairs"; the assignments are
  SensorScope/NSW-Traffic/City Scanner → Design, U-Air/T-Drive → NoDesign (§VII-G). The U-Air reversal is
  diagnosed by a forced-Design run (Fig. `fig:w1_design_gate`), and forced Design is worse there.
Reviewer deduction: the paper demonstrates the reversal in one direction (forcing Design where φ>0 hurts) but never
  runs the converse — forcing NoDesign on the φ=0 blocks where the headline structural wins are claimed. Without
  that control, the reader cannot separate the benefit of target-mass reconstruction from the benefit of the
  Design/NoDesign weighting difference, and the headline result rests on a heuristic that is explicitly not a
  validity test.
Required fix: report forced RAVEN-NoDesign on SensorScope (and ideally City Scanner), the mirror image of the
  existing forced-Design U-Air row.
```

W6. **The three-layer claim is exercised only partly by the evidence.**

```text
Weakness: the main comparison holds O and U at Complete-aligned controls and R always on, so the main table
  exercises only the opportunity-layer ratio; the ablation then reports that the usable-update layer is inert.
Evidence basis: §VII-A.2 ("On SensorScope and U-Air, protocol R is always-on"; O and U Complete-aligned);
  §VII-E ("removing Use produces no significant change in any of the four core endpoints on either dataset");
  measured O appears only for City Scanner Pilot 2 (§VII-A.1), and measured U appears nowhere.
Reviewer deduction: the central motivation is a three-layer composition, but the evaluated system varies one
  layer, and the third layer is shown to have no isolated empirical effect. The "two-stage" (O then U) half of the
  contribution is asserted rather than demonstrated.
Required fix: add at least one block with measured U (or state plainly in §I that U-correctness is carried
  theoretically and is not empirically identified in this paper).
```

W7. **The impossibility results that justify the paper's modest guarantee are never stated in the main text.**

```text
Weakness: §VI-F's lead paragraph names four barrier results but states none of them, so their hypotheses are
  invisible to a reader of the main paper.
Evidence basis: §VI-F refers to "the positive pairwise lower-bound barrier proposition", "the availability-induced
  barrier corollary", "the false-safe Gate corollary" and "the arbitrary-drift applicability boundary proposition",
  all defined only in the supplement's aggregate-coverage section. A reader cannot see the conditions
  P(X_t=0|F_{t−})>α or a<1−α.
Reviewer deduction: these results are what demote the coverage contribution from a certificate to a diagnostic
  Gate. Keeping them out of the main text costs the paper the ability to defend its own scope.
Required fix: promote the four statements into one compact proposition plus one corollary in §VI-F (proofs stay in
  the supplement), or at minimum state the two hypotheses inline.
```

W8. **Mechanical prose defects from an appendix-pointer convention.**

```text
Weakness: descriptive appendix pointers are spliced into sentences at the position where a citation or connective
  belongs, producing ungrammatical text in the submitted manuscript.
Evidence basis (current build): §I contributions-and-evaluation paragraph ("a City Scanner New York PM2.5
  visit-occupancy table the City Scanner visit-occupancy ranking table in the supplemental material, and a Pilot~2
  table with measured observation the City Scanner Pilot~2 measured-O ranking table in the supplemental
  material---are not mixed into that development table"); §VII-A.1 City Scanner paragraphs; the Table `tab:datasets`
  caption; §VII-C.2 NSW-Traffic and City Scanner topic sentences; §VII-G. The identical defect in §IV-E and §VI-F
  was repaired earlier in this editing session; at least six further instances remain in the reviewed build.
Reviewer deduction: this reads as broken English in the introduction, the dataset descriptions and a table caption,
  i.e. in exactly the places a reviewer forms a first impression.
Required fix: mechanical pass replacing each spliced pointer with a proper connective or parenthetical, e.g.
  "see the City Scanner visit-occupancy ranking table in the supplemental material".
```

W9. **`g`, the regime descriptor on which Assumption 1 and Theorem 2 condition, is never defined.**

```text
Weakness: both the assumption and the theorem are stated conditional on g, and g has no definition or
  operationalization anywhere in the paper.
Evidence basis: Assumption 1 ("Conditioned on the frozen public regime descriptor g") and Thm. 2
  (P(C^LCB_t ≤ C_t | g) ≥ 1−α); the supplement's proof of Thm. 2 uses g only as a conditioning symbol that rides
  through the randomized-rank argument. No section defines how g is computed or frozen.
Reviewer deduction: a conditional guarantee whose conditioning object is undefined cannot be checked or
  reproduced; it also makes the assumption unfalsifiable as written.
Required fix: define g (what covariates, computed from what window, frozen by whom and when) where the Gate is
  defined in §V-E.
```

## 7. Potentially Missing Related Work

```text
Work: Federated Inverse Probability Treatment Weighting for Individual Treatment Effect Estimation
Status: searched (https://arxiv.org/html/2503.04946v1)
Why relevant: closest published instance of inverse-propensity weighting inside federated learning, which is the
  mechanism RAVEN-MCS uses at the opportunity and observation layers.
Overlap: shares the IPW-in-FL mechanism; differs in estimand (individual treatment effect versus
  deployment-target mass).
Needed comparison: a citation in §II acknowledging IPW-within-FL as prior mechanism, with one sentence on why the
  target-mass estimand differs. No experimental comparison required.

Work: RAFL — reverse-auction federated learning for non-IID mobile crowdsensing
Status: searched (https://dl.acm.org/doi/10.1016/j.comnet.2026.112314)
Why relevant: recent MCS-FL work that also treats non-IID participation.
Overlap: participation handling on the client-selection side only; no sensing-side opportunity/observation split.
Needed comparison: citation only.

Work: client-unavailability / partial-participation FL analysis
Status: searched (https://ftp.esat.kuleuven.be/pub/stadius/ida/reports/26-64.pdf)
Why relevant: models clients unavailable during training, the closest analogue of the U layer.
Overlap: availability modelling without the MCS three-layer decomposition.
Needed comparison: citation only.

Work: reference-list verification
Status: unverified
Why relevant: the workspace verification record left 24 of 54 entries unverified and had already found one
  misattribution. Several entries are forward-dated 2026 works.
Needed comparison: a complete entry-level verification pass before submission.
```

## 8. Claim-Evidence Audit

| Claim | Where stated | Evidence provided | Strength | Reviewer deduction | Required fix |
| --- | --- | --- | --- | --- | --- |
| Target and arrival risk functionals are not interchangeable when the laws differ | Abstract; §VI-B Prop. 1 | Proof in supplement | Strong (but elementary) | Correct; a short argument that two different laws give different weighted expectations. The value is the framing, not the proposition. | None; do not present Prop. 1 as the theoretical depth |
| The ideal sequential correction recovers compatible target moments / group mass | Abstract; §VI-C Prop. 2 | Proof under A1–A3; supplement | Adequate | Applies to the ideal pooled estimator with known ratios, not to the implemented finite-window system. The paper says so. | Add one sentence stating the finite-window gap, quantitatively if possible |
| Calibration is uniquely solvable | Abstract; §VI-D Thm. 1 | Proof under A4; supplement feasibility diagnostics | Strong | Correct as a statement about the program; the paper explicitly does not claim post-hoc optimality of logged solves. | None |
| The clipped plug-in is a stable perturbation of the reference | Abstract; §VI-E Prop. 3 | Proof under A1, A4–A6; supplement A5/A6 audit | Weak as stated | The abstract conditions on "target support is compatible" (A5) while the proposition needs A6 as well, and the audit reports A6 failing on both datasets. | Align the abstract condition with the proposition's hypothesis |
| Long-term target debt gives an accounting bound | §V-B; §VII-E | Deterministic recursion; supplement proof | Adequate | The bound is real but the empirical effect is `0.0141%/0.0040%` (SensorScope) and `0.0043%/0.0024%` (U-Air), far below the paper's own `0.5%` threshold. | None; keep as accounting only, as the paper already does |
| A coverage Gate with conditional validity | §VI-F Thm. 2 | Proof under Assumption 1; barriers in supplement | Adequate | Conditional on an undefined descriptor `g`, and the paper states adaptive switching is unproven and that the Gate never switches Design. | Define `g`; state the barriers in the main text |
| RAVEN reduces structural mismatch (`Δ_group`, `Δ_c-s`) | Abstract; §VII-C.1, §VII-D | Table II, City Scanner tables, ablation with Holm correction | Weak | `Δ_group` is the minimized functional of P2 measured against an author-constructed target; NSW-Traffic contradicts it; T-Drive shows it constant across four methods. | Add an endpoint independent of the optimized functional |
| RAVEN improves completion accuracy | Abstract (correctly negated: "not an RMSE win"); §VII-C | Table II, T-Drive | Absent | No block shows a Holm-significant prediction gain; T-Drive is a loss. The paper does not claim one, which is correct but leaves the system contribution thin. | Either produce one such block or drop the system-improvement framing |
| Three-layer selection causes the mismatch | §I; §IV | Main table varies only `R`; ablation shows `U` inert | Weak | The O and U layers are controlled in the main block and the U layer has no isolated empirical effect. | Add a measured-`U` block or narrow the claim |
| The `φ` heuristic assigns the method appropriately | §V-E; §VII-G | Forced-Design U-Air diagnostic | Adequate (one-sided) | Only the Design-where-`φ>0` direction is tested; the converse control is missing. | Add forced-NoDesign on SensorScope |

## 9. Experiment / Benchmark / Reproducibility Audit

**Baselines.** Five same-backbone baselines (FedAvg-Window, FedAsync-Window, TimeAlign-Agg, Local-Hàjek, TwoStage-Hàjek) plus two windowed participation baselines (FedAU-Window, ObsUse-Window), plus central-all and central-delivered reference rows and a RAVEN-SimOracle controlled reference. TimeAlign-Agg is labelled a windowed aggregator "in the spirit of" a cited work and explicitly not an official reproduction, which is honest and acceptable. Local-Hàjek collapsing onto FedAvg is explained in the supplement (uniform realized within-client Hàjek weights) rather than left as an unexplained coincidence — good practice.

**Datasets.** Six blocks: SensorScope and U-Air (main comparison + ablation, station traces), NSW-Traffic (risk interchangeability + four-region ranking), T-Drive (real taxi `R`), City Scanner NY PM2.5 (visit occupancy `R`), City Scanner Pilot 2 (measured `O`). All public, with DOIs/URLs. The paper is explicit that SensorScope and U-Air contain no mobile clients and that `h(i)` is a UTC four-group map. Using non-mobile traces for a mobile-computing claim is a real scope limitation, but it is disclosed and partly offset by T-Drive and City Scanner.

**Metrics.** `RMSE_μ`, `WorstGroupRMSE`, `Δ_group`, `Δ_c-s`, tail RMSE, ESS, worst-group tolerances. The endpoint set is conventional, but see W1: the two structural endpoints are the optimized functional and an author-constructed target.

**Statistical rigor.** 20 paired seeds on the main block, 10 seeds and 178 windows on T-Drive, Holm correction across the endpoint family, a declared `0.5%` minimum practical effect, and a descriptive `+0.5%` tolerance used explicitly in place of significance where power is insufficient. The paper distinguishes the TEST-seed slice (`30011`–`30020`) from all 20 seeds when reporting paired relatives, which is careful.

**Robustness / failure cases.** INT-R intermittent occupancy; coverage-stress audit of the Gate (pooled CERTIFIED validity `0.959`, U-Air `a=1.00` is `0.750`); the A5/A6 support audit; the under-served-block pre-registered check that produced no second external win. This is an unusually complete failure-reporting surface.

**Implementation details.** Window-close aggregation order, lagged opportunity state (`ρ_opp`, clipping constants `p_min`, `q_min`, `a_max`, `d_max`), `α_max=0.5`, `E_min=3`, `n_min=19`, `α=0.05`, `τ_cov=0.05`, frozen `φ` per block, `s_max=5`, opportunity forgetting `0.95`.

**Artifacts and reproducibility.** Released EventTraces and a public reproduction bundle are referenced, with frozen hashes and a support-hypothesis audit script. The repository could not be inspected in this review, so reproducibility is scored on the manuscript's self-reported detail plus the presence of an audit trail.

**Limitations.** The limitations paragraph is specific and quantified (see S5) and is one of the paper's stronger features.

## 10. Multi-Reviewer Panel

```text
Reviewer: Best-justified (accept case)
Expertise: mobile crowdsensing systems
Likely score: 6 (borderline positive)
Confidence: 4
Main positive signal: the R/O/U decomposition with target-mass semantics is a clean, transferable idea, and the
  paper does not pretend to more than it shows. Table II plus the T-Drive and City Scanner blocks is a broad
  evidence surface for a journal paper.
Main negative signal: the idea is better than the demonstrated benefit.
Evidence basis: §I contributions; §IV; §VII datasets and blocks.
Score-change condition: one block with a Holm-significant prediction gain under a real-mobility `R` moves this to 7.
```

```text
Reviewer: Critical (reject case)
Expertise: statistical evaluation of networked learning systems
Likely score: 3 (reject)
Confidence: 4
Main positive signal: none that changes the decision.
Main negative signal: the headline endpoint is the objective function. Δ_group is ||ω̄ − μ||_1, and P2 minimizes
  ||M_r α − μ||^2 with a debt term on the same μ; μ is author-constructed. An improvement is therefore partly
  tautological, and no independent endpoint separates the methods.
Evidence basis: §IV Δ_group definition; §V-C P2 objective and debt recursion; §VII-A.1 μ construction; Table II.
Fatal concern if any: not fatal on its own, because the paper does not claim an accuracy win — but the remaining
  contribution is a diagnostic methodology, which is a weak basis for a TMC regular paper.
Score-change condition: an endpoint whose target is external to the method, showing a corrected gain.
```

```text
Reviewer: Method / soundness
Expertise: federated optimization and inverse-probability estimation
Likely score: 4
Confidence: 4
Main positive signal: the sequential factorization R→O→U with distinct legal histories is correctly motivated,
  and Hàjek normalization with local weights is the right estimator class for the ratio regime. Thm. 1 is correct
  and the feasible set is sensible.
Main negative signal: the sharp finite-window result needs A6, which the paper's own audit falsifies on the
  evaluated traces; the abstract's condition is weaker than the proposition's hypothesis.
Evidence basis: §VI-E Prop. 3 and its scope sentence; supplement A5/A6 audit; abstract sentence on the clipped
  plug-in.
Score-change condition: restate the abstract condition to match A6, and state explicitly which reported results
  are covered by theory. Would not change the overall stance on its own.
```

```text
Reviewer: Evidence / ablation
Expertise: empirical evaluation of ML systems
Likely score: 4
Confidence: 4
Main positive signal: the ablation is complete and honest — it reports that the usable-update layer has no
  significant effect, that debt is far below the practical threshold, and that Inst trades endpoints.
Main negative signal: the T-Drive Δ_group column is identical (0.5232) for four structurally different weighting
  rules, which suggests the endpoint is invariant to the aggregation weights on that block, and hence that the
  calibration contributed nothing there.
Evidence basis: Table `tab:tdrive_hybrid`; Table II; §VII-E ablation paragraphs.
Score-change condition: an explanation of the T-Drive Δ_group computation, or a weight-sensitive variant of the
  endpoint, would remove the suspicion of a degenerate metric.
```

```text
Reviewer: Novelty / positioning
Expertise: mobile crowdsensing and federated learning
Likely score: 4
Confidence: 3
Main positive signal: the three-layer decomposition with the target-mass estimand is not present in the closest
  works found; IPW-in-FL exists but for a different estimand.
Main negative signal: the individual pieces (IPW, Hàjek normalization, simplex-constrained calibration, debt) are
  all classical; the novelty is compositional, and the paper says so. Whether a compositional novelty of this kind
  clears the TMC bar depends on the benefit demonstrated, which is thin.
Evidence basis: §I "RAVEN's novelty is therefore not inverse-probability weighting or Hàjek normalization as such";
  public search results.
Score-change condition: sharper positioning against IPW-in-FL and participation-bias FL, with a demonstration that
  the three-layer split buys something a one-layer correction cannot.
```

```text
Reviewer: Writing / clarity
Expertise: scientific writing
Likely score: 4
Confidence: 5
Main positive signal: the contribution list, the scope sentences after each proposition, and the limitations
  paragraph are unusually disciplined; the reader always knows what is and is not claimed.
Main negative signal: the appendix-pointer convention produces ungrammatical sentences in at least six places,
  including the introduction, two dataset paragraphs and a table caption; the paper also carries a heavy
  apparatus (A1–A6, six barriers, five components) for its demonstrated payoff.
Evidence basis: §I evaluation paragraph; §VII-A.1; Table `tab:datasets` caption; §VII-C.2; §VII-G.
Score-change condition: a mechanical prose pass would move clarity to 5 and materially improve first impressions.
```

```text
Reviewer: Ethics / reproducibility
Expertise: research data and audit practice
Likely score: 5
Confidence: 3
Main positive signal: all datasets public with links; no human subjects; an explicit statement that FL is not a
  privacy guarantee; released traces with frozen hashes; an audit of the method's own assumptions, including one
  that fails.
Main negative signal: the reference list has unverified entries and previously contained a misattribution, and
  repository access was unavailable in this review so released artifacts could not be checked.
Evidence basis: §VII-A.1 footnotes; §VII-G; workspace verification record.
Score-change condition: a complete reference-verification pass; unchanged otherwise.
```

```text
Reviewer: Domain application
Expertise: deployed MCS operations
Likely score: 3
Confidence: 4
Main positive signal: opportunity and observation are genuinely different operational problems, and separating
  them matches field practice.
Main negative signal: the main evidence comes from station traces with no mobile clients and with O/U held as
  controlled layers; the only real-mobility block shows no gain. Practitioners would also ask about the
  zero-opportunity support: how much of the deployment target is even reachable? The audit reports
  min π^opp = 6.33e-4 and that 22.8%/23.8% of client-windows have zero usable margin, but the size of the
  compatible support — the set on which A1's compatibility identity can hold at all — is not reported.
Evidence basis: §VII-A.1; §VII-C.2; supplement A5/A6 audit.
Score-change condition: reporting the reachable target-support fraction per map, and one measured-U block.
```

```text
Reviewer: Reproducibility
Expertise: experimental infrastructure
Likely score: 4
Confidence: 3
Main positive signal: seeds, window counts (100 windows), s_max, ρ_opp = 0.95, clipping constants, α_max, E_min,
  n_min, α, τ_cov, and per-block φ are all specified, and frozen-hash manifests are referenced.
Main negative signal: the released artifacts could not be inspected here; the P2 invocation state logs appear to
  carry no active-set list (which is why the supplement's audit must mark one A5 clause unmeasurable), so a
  reproducer cannot verify the shared-support clause either.
Evidence basis: supplement A5/A6 audit limits paragraph; §VII-A.
Score-change condition: preserve and release the active-set list per window so the shared-support clause becomes
  auditable.
```

```text
Reviewer: Novice advocate
Expertise: first-year graduate reader
Likely score: 3
Confidence: 4
Main positive signal: the abstract is honest and the three contributions are clearly enumerated; Fig. 1 conveys
  the framework.
Main negative signal: the paper needs A1–A6, four barriers, six datasets and five ablation components before the
  payoff appears, and the payoff is a diagnostic ratio rather than an accuracy gain; several sentences are
  ungrammatical; Assumption 1 conditions on an undefined symbol.
Evidence basis: abstract; §I; §VI; §VII.
Score-change condition: a prose pass and a one-paragraph "what to take away" statement in §VII.
```

```text
Agreement: all reviewers accept that the framing is a real contribution, that the theory is correct on its own
  terms, and that the reporting honesty is above average. All reviewers also agree that the demonstrated benefit
  is thin relative to the apparatus.
Disagreement: the best-justified reviewer treats the diagnostic result as a publishable contribution; the critical
  reviewer treats an endpoint equal to the objective as fatal to the empirical claim. The disagreement is about the
  standard for an empirical contribution, not about the facts.
Decisive positive axis: a genuinely new and transferable problem decomposition, honestly evaluated.
Decisive negative axis: no independent endpoint shows benefit, and the only consistent gain is measured on the
functional the method minimizes against an author-constructed target.
Unresolved evidence: how Δ_group is computed on T-Drive and why it is invariant to α; the size of the compatible
  target support per map; the missing forced-NoDesign control on φ=0 blocks; whether a measured-U block exists.
AC stance: lean reject at the current evidence level, with a clear and achievable path to borderline-accept if an
  independent endpoint shows a corrected gain.
```

## 11. Concerns Table

| ID | Severity | Concern | Evidence basis | Affected criterion | Fix class | Required action | Owner skill | Score-change condition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | major | `Δ_group`/`Δ_c-s` are the minimized functional measured against an author-constructed target, so the headline gains are partly self-referential | §IV Δ_group/Δ_c-s definitions; §V-C P2 objective and debt recursion; §VII-A.1 `μ` construction | Evidence, Soundness | experiment | Add an endpoint whose target is external to the method and not author-constructed | ccf-experiment-designer | +1 overall if a corrected, statistically significant gain appears on such an endpoint |
| C2 | major | No completion-accuracy advantage on any block; T-Drive is a loss and NSW-Traffic is worse on `Δ_group` | Table II (RMSE_μ spreads 7.9293–7.9389 and 1.1120–1.2160); `tab:tdrive_hybrid` (+2.39%/+2.43%); §VII-C.2 NSW `Δ_group` 0.1048 vs 0.0606 | Evidence, Significance | experiment | Produce one prediction-quality win that survives Holm, or drop the system-improvement framing | ccf-experiment-designer / ccf-paper-writer | +1 overall with one such block; no change from reframing alone |
| C3 | major | T-Drive `Δ_group` is identical (0.5232) across four different weighting rules, so the endpoint does not discriminate aggregation there | `tab:tdrive_hybrid`: 0.5232 for FedAvg/FedAU/ObsUse/RAVEN-NoDesign, 0.5948 for TwoStage/forced-Design; no std on four rows | Evidence | experiment | Explain the `Δ_group` computation on that block or report a weight-sensitive variant | ccf-experiment-designer | +0.5 overall if explained and the endpoint is shown to be informative |
| C4 | major | Prop. 3 needs A6, which the paper's own audit reports false on the evaluated traces; the abstract conditions only on support compatibility | §VI-E "Assume A1 and A4–A6"; supplement A5/A6 audit; abstract sentence on the clipped plug-in; §VII-C.3 scope sentence | Soundness | writing / method/soundness | Align the abstract condition with A6; state which reported results theory covers | ccf-paper-writer | +0.5 overall via credibility; no stance change alone |
| C5 | major | The `φ` switch is a per-dataset branch with no forced-NoDesign control on the `φ=0` blocks where the structural wins are claimed | §V-E `φ` definition; §VII-G ("does not verify positivity on target-positive pairs"); Fig. `fig:w1_design_gate` forces Design only on U-Air | Evidence, Soundness | experiment | Add forced RAVEN-NoDesign on SensorScope | ccf-experiment-designer | +0.5 overall if the Design-vs-NoDesign gap is separated from the target-mass effect |
| C6 | moderate | The three-layer claim is exercised only through `R` in the main table; measured `O` appears once and measured `U` never, and the `U` ablation is null | §VII-A.2 (always-on `R`, Complete-aligned `O/U`); §VII-E ("removing Use produces no significant change") | Evidence, Significance | experiment | Add a measured-`U` block or narrow the claim in §I | ccf-experiment-designer | +0.5 overall with a measured-`U` block |
| C7 | moderate | The four impossibility results that justify §VI-F are named but not stated in the main text | §VI-F lead paragraph vs the supplement's aggregate-coverage section | Clarity, Significance | writing | Promote the four statements into one proposition plus one corollary, or state the two hypotheses inline | ccf-paper-writer | +0.5 clarity only |
| C8 | moderate | Spliced appendix pointers produce ungrammatical sentences in ≥6 places, including the introduction, two dataset paragraphs and a table caption | §I evaluation paragraph; §VII-A.1; Table `tab:datasets` caption; §VII-C.2; §VII-G | Clarity | writing | Mechanical prose pass replacing each spliced pointer with a connective or parenthetical | ccf-humanization / ccf-paper-writer | Clarity 4→5 |
| C9 | moderate | `g` is undefined although Assumption 1 and Thm. 2 condition on it; the compatible target support size is never reported | Assumption 1; Thm. 2; supplement Thm. 2 proof; no definition anywhere | Soundness, Reproducibility | method/soundness | Define `g` in §V-E; report the reachable-support fraction per map | ccf-paper-writer | Clarity/Reproducibility up; no overall change alone |
| C10 | minor | Reference list not fully verified: 24 of 54 entries unverified and one misattribution previously found | workspace literature-verification record; §4 of this report | Positioning, Reproducibility | related-work | Complete entry-level verification, especially forward-dated 2026 entries | ccf-literature-searcher | Prevents a desk-level credibility problem |
| C11 | minor | Author masking is inconsistent (`****` beside a named co-author, visible affiliation and grant) | title-page author block | Format | venue-mismatch | Name all authors or mask consistently | ccf-submission-checker | None |
| C12 | minor | TMC page/over-length policy unverified; 15 main pages plus a 15-page supplement | no `tmc.md` venue guide present; current-year rules not checked | Format | venue-mismatch | Check the official TMC author guidelines before submission | ccf-submission-checker | Could become a desk risk |

## 12. AC / Meta-Review

**Reviewer consensus.** All ten perspectives agree on the facts and on the paper's unusual honesty. All agree the framing is a real contribution and that the demonstrated benefit is thin. None found a novelty collapse, an invalid proof, a fabrication signal, or an ethics problem.

**Reviewer disagreement.** The best-justified and critical reviewers split on what an empirical contribution must show. The best-justified reviewer accepts a rigorously reported diagnostic result as publishable; the critical reviewer holds that an endpoint equal to the optimized functional cannot support an empirical contribution claim. The disagreement is about the evidentiary bar, not about the paper's content, and it is not resolvable by re-reading the manuscript.

**Decisive acceptance axis.** A new, transferable decomposition of MCS selection into layers with distinct legal histories, combined with unusually disciplined claim scoping and one of the most complete failure-reporting surfaces in a submission of this type.

**Decisive rejection axis.** The evaluated system shows no independent benefit: the task metric is a tie everywhere and a loss under real mobility, and the only consistent improvement is measured on the functional the calibration program minimizes, against a target the same paper constructs.

**AC stance.** Lean reject at the current evidence level. The manuscript is not far from borderline-accept, and the gap is evidentiary rather than conceptual — but it is not closable by rewriting. It requires at least one new endpoint or block.

**Discussion risks.** The most likely discussion failure mode is a reviewer discovering W1 or W3 late and re-reading the whole evaluation as over-claimed. That risk is mitigated by the paper's own candour but not eliminated, because the abstract still leads with structural alignment.

## 13. Quantitative Scores

### Scorecard

| Dimension | Score (1-5) | Confidence (1-5) | Evidence basis | Deduction / score-change condition |
|:---|:---:|:---:|:---|:---|
| Novelty | 3 | 4 | §I contribution 1; §IV R/O/U split; §I "novelty is therefore not IPW or Hàjek normalization as such" | Deduction: the components are classical and the novelty is compositional; the three-layer split is the genuinely new part but is under-demonstrated empirically (C6). Raise to 4 with a demonstration that the split buys something a one-layer correction cannot. |
| Soundness | 3 | 4 | §VI-E Prop. 3 scope; supplement A5/A6 audit; abstract condition mismatch; undefined `g` (C9) | Deduction: the derivations are correct but the sharp result's hypothesis is falsified on the evaluated traces and the coverage theorem conditions on an undefined object. Raise to 4 by aligning abstract and proposition conditions, defining `g`, and stating theory coverage explicitly. |
| Evidence | 3 | 4 | Table II; `tab:tdrive_hybrid`; ablation with Holm correction; T-Drive `Δ_group` constant at 0.5232 across four methods | Deduction: the evidence surface is broad, statistically careful and honestly reported, but the separating endpoints are the optimized functional (C1) and no independent endpoint separates the methods (C2); one endpoint is degenerate on the real-mobility block (C3). Raise to 4 with one independent endpoint showing a corrected gain. |
| Significance | 3 | 4 | §I; `Δ_group` wins in 3 of 4 Design-active blocks but loses NSW-Traffic; T-Drive loss under real `R` | Deduction: an important and well-posed problem, but the demonstrated practical payoff is a diagnostic ratio. Raise to 4 with one real-mobility accuracy or worst-group win. |
| Clarity | 3 | 5 | §I contribution list; scope sentences after each proposition; ≥6 spliced-pointer sentences (C8); Assumption 1 conditioning on undefined `g` | Deduction: contribution recoverability is good and scope statements are excellent, but first-impression passages are ungrammatical and the apparatus is heavy. Raise to 4 with a mechanical prose pass. |
| Reproducibility | 4 | 3 | §VII-A constants (`α_max=0.5`, `E_min=3`, `n_min=19`, `α=0.05`, `τ_cov=0.05`, `ρ_opp=0.95`, per-block `φ`); frozen-hash manifests; release references | Deduction: manuscript-level detail is strong; the repository could not be inspected, and the missing per-window active-set list makes one A5 clause unauditable. Raise to 5 with released active-set logs and verified references. |
| Ethics / Limitations | 5 | 4 | §VII-G; public datasets with links; "FL does not provide a privacy guarantee"; audit of a failing assumption; reporting of a null ablation | Deduction: none. The limitations are specific, quantified and repeated where relevant, and the paper audits its own assumption to a negative result. |

**Overall:** 4 (weak reject)  | **Scholarly Confidence:** 4

**Recommendation:** weak-reject

**Verdict:** One independent endpoint showing a statistically corrected benefit — ideally on a block with real mobility — raises this to 6 (borderline positive), and adding the measured-`U` block and the forced-NoDesign control would raise it to 7. Conversely, if a reviewer concludes that an endpoint equal to the objective cannot support *any* empirical claim, the paper falls to 3, because the remaining contribution is a diagnostic methodology.

### Score-change conditions

| Change | Condition | Likely affected dimensions | Expected movement |
| --- | --- | --- | --- |
| Raise score | One endpoint whose target is external to the method, showing a Holm-significant corrected gain | Evidence, Significance | +1 overall |
| Raise score | Forced RAVEN-NoDesign on SensorScope plus a measured-`U` block | Evidence, Soundness | +0.5 to +1 overall |
| Raise score | Mechanical prose pass, define `g`, align the abstract condition with A6, state the barriers inline | Clarity, Soundness | +0.5 overall (mostly credibility) |
| Lower score | A reviewer treats `Δ_group` as the objective function and concludes no empirical claim survives | Evidence, Significance | −1 overall |
| Lower score | T-Drive `Δ_group` invariance is shown to indicate a degenerate metric rather than a genuine invariance | Evidence | −0.5 overall |
| No quick change | A real-mobility block with independently measured `O` and `U` and an external target map | Evidence | Requires new data collection; unlikely before submission |

## 14. Questions For Authors

1. **On T-Drive, how is `Δ_group` computed, and why does it take the value `0.5232` for FedAvg-Window, FedAU-Window, ObsUse-Window and RAVEN-NoDesign alike, while `Δ_c-s` and RMSE_μ differ across the same rows?** Does this indicate that `Δ_group` is invariant to the realized aggregation weights on that block? If so, what did P2's calibration contribute there?

2. **What is the size of the compatible target support per map** — the set on which A1's compatibility identity can hold with `P^opp > 0`? The audit reports `min π^opp = 6.33e-4` and that 22.8%/23.8% of client-windows have zero usable margin, but not what fraction of the deployment target is reachable at all. Without this, the practical scope of the reconstruction claim is unknown.

3. **What happens under forced RAVEN-NoDesign on SensorScope?** The paper reports the converse (forced Design on U-Air, which is worse). Without the mirror run, the SensorScope structural gain cannot be separated from the Design/NoDesign weighting difference.

4. **Which of the reported results are covered by theory?** Prop. 2 covers the ideal pooled estimator under A1–A3; Prop. 3 needs A1 and A4–A6, and A6 fails on the released traces. Is any reported table entry covered by a non-vacuous guarantee? If not, please say so explicitly in §VI rather than only in the limitations.

5. **What is `g`?** Assumption 1 and Thm. 2 both condition on "the frozen public regime descriptor `g`", which is never defined. What variables compose it, over what window is it computed, and how is it frozen?

6. **Is there a measured-`U` block?** The ablation reports no significant effect from removing usable-update correction on either dataset, and `U` is a Complete-aligned control everywhere. Should the abstract and §I be narrowed to "opportunity and observation layers are empirically identified; the usable-update layer is carried theoretically"?

## 15. Score Revision Criteria

```text
Raising the score would require:
  - one endpoint whose target is external to the method (not Δ_group, not Δ_c-s against π^tar), showing a
    Holm-significant corrected gain; or
  - forced RAVEN-NoDesign on SensorScope isolating the target-mass effect from the weighting difference; or
  - a measured-U block, plus explicit narrowing of the three-layer claim; or
  - (clarity-only) a mechanical prose pass, a definition of g, and alignment of the abstract's condition with A6.
Lowering the score would be triggered by:
  - evidence that Δ_group on T-Drive is degenerate rather than genuinely invariant; or
  - a failed reference verification revealing further misattributions; or
  - a reviewer concluding that no empirical claim survives when the separating endpoint is the objective.
Concerns unlikely to change before submission:
  - the absence of a real-mobility block with independently measured O and U (needs new data);
  - the fact that Δ_group's target μ is author-constructed (inherent to the design);
  - the compositional rather than modular nature of the novelty.
```

## 16. Action Plan And CCFA Handoffs

```text
Priority: P0
Action: Determine how Δ_group is computed on T-Drive and why it is invariant across four weighting rules; if it is
        degenerate, replace it with a weight-sensitive structural endpoint and re-run the T-Drive ranking.
Owner skill: ccf-experiment-designer
Input needed: the T-Drive Δ_group computation path and the per-method realized α for that block
Expected output: an explanation plus, if needed, corrected T-Drive structural numbers
Handoff required: yes

Priority: P0
Action: Add one endpoint whose target is external to the method, and report whether the SensorScope / City Scanner
        structural gains survive on it.
Owner skill: ccf-experiment-designer
Input needed: a held-out or externally specified grouping for the target mass
Expected output: a table row that either confirms or refutes the structural gain independently
Handoff required: yes

Priority: P1
Action: Run forced RAVEN-NoDesign on SensorScope (mirror of the existing forced-Design U-Air row).
Owner skill: ccf-experiment-designer
Input needed: the existing SensorScope protocol traces and the NoDesign branch
Expected output: a paired comparison isolating target-mass reconstruction from the weighting difference
Handoff required: yes

Priority: P1
Action: Report the compatible target support per map, and preserve/release the per-window active-set list so A5's
        shared-support clause becomes auditable.
Owner skill: ccf-experiment-designer (table via ccf-visual-composer)
Input needed: the frozen π^tar and P^opp maps plus the P2 invocation states
Expected output: a support-coverage table in the supplement
Handoff required: yes

Priority: P1
Action: Align the abstract's condition for Prop. 3 with A6, define g in §V-E, and state explicitly in §VI which
        results are and are not covered by theory.
Owner skill: ccf-paper-writer
Input needed: the current §VI text and the A5/A6 audit result
Expected output: scope-aligned abstract, definition of g, one coverage sentence in §VI
Handoff required: yes

Priority: P2
Action: Mechanical prose pass over the ≥6 spliced appendix pointers (introduction, dataset paragraphs, Table
        `tab:datasets` caption, §VII-C.2, §VII-G).
Owner skill: ccf-humanization / ccf-paper-writer
Input needed: the locations listed in C8
Expected output: grammatical sentences with proper connectives
Handoff required: yes

Priority: P2
Action: Promote the four barrier statements into one proposition plus one corollary in §VI-F and keep the proofs in
        the supplement.
Owner skill: ccf-paper-writer
Input needed: the supplement statements of the four results
Expected output: self-contained §VI-F scope paragraph
Handoff required: no

Priority: P2
Action: Complete entry-level reference verification, prioritizing forward-dated 2026 entries.
Owner skill: ccf-literature-searcher
Input needed: reference.bib
Expected output: a per-entry verification record
Handoff required: yes

Priority: P3
Action: Verify the current TMC page limit and over-length policy; make author masking consistent.
Owner skill: ccf-submission-checker
Input needed: the official TMC author guidelines
Expected output: a pass/fail format note
Handoff required: no
```

```text
Checks run:
  - desk checks (length, topic, minimum quality, policy, injection, ethics) on main.pdf and supplemental.pdf
  - three-pass read of main.pdf (15 pp.) and supplemental.pdf (15 pp.)
  - enumeration of every headline number in Table II, the T-Drive hybrid table, the dataset table and the ablation
  - cross-check of the four barrier results against their main-text pointers
  - cross-check of Prop. 3's hypothesis against the supplement's A5/A6 audit and the abstract's wording
  - arithmetic check of Δ_group / Δ_c-s definitions against the P2 objective and debt recursion
  - search for undefined symbols (g), ungrammatical spliced pointers, and unreferenced floats
  - three public related-work queries
Checks skipped:
  - repository and released-artifact inspection (no access in this review)
  - full re-verification of all 54 bibliography entries
  - official current-year TMC page and policy verification (no tmc venue guide in the skill library)
  - independent recomputation of any reported statistic from raw traces
Unresolved risks:
  - whether Δ_group on T-Drive is a degenerate metric (C3) — the single highest-value item to resolve
  - whether any reported result is covered by a non-vacuous theorem
  - the size of the compatible target support, which bounds the reconstruction claim's practical reach
  - 24 unverified bibliography entries, several forward-dated
```

## Output Self-Check

1. Section order matches the fixed output contract (metadata through action plan). ✓
2. Every table has valid Markdown separators with a consistent column count per row. ✓
3. Scores, confidence and recommendation are internally consistent: 4/10 weak-reject corresponds to "one major concern or multiple moderate concerns", and five major concerns are listed; confidence 4 reflects a complete main text and supplement with no repository access. ✓
4. Field lists use parallel grammar. ✓
5. Causal chains are explicit (claim → evidence basis → deduction → required fix) in §6, §8 and §11. ✓
6. Language is consistent English; no mixed-width punctuation. ✓
7. No placeholder tokens remain. ✓
8. No generic filler: every concern names a location, a number, and an owner skill. ✓

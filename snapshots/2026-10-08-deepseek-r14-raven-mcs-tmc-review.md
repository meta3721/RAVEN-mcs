# RAVEN-MCS — IEEE TMC review, round 14 (new-evidence intake)

```text
Mode: scientific / full, with an explicit new-evidence intake, plus two commissioned independent
  adversarial checks whose findings are folded in and attributed. Assessment only; no prose rewrite.
Date: 2026-10-08 (revised the same day after the independent checks landed; see section 11)
Venue and assumptions: IEEE TMC journal submission, method-plus-measurement paper. Page budget treated
  as TMC regular 12 pp with the project's MOPC allowance up to 18 pp.
Frozen score contract inherited from TMC-J-R4 (not modified): Originality / Soundness / Evidence /
  Clarity / Reproducibility / Significance / Related work / Terminology; weights
  0.10 / 0.20 / 0.25 / 0.15 / 0.10 / 0.10 / 0.05 / 0.05; anchors 1-5; overall 1-10;
  |weighted delta| < 0.05 = unchanged.
Review target: TO_OVERLEAF_paper_tmc_r1_clean/main.tex
  sha256 D4FB164DF90F59484BFE901B117399536CD727F4CB01FCA6A3E09CB902486E60, 116806 B,
  mtime 2026-10-07 22:57:02. Rebuilt this pass: main.pdf 18 pp, 0 errors, 0 undefined,
  0 multiply-defined, 0 Overfull; supplemental.pdf 16 pp with 1 Overfull \vbox.
Previous review: snapshots/2026-10-08-pre-round14-raven-mcs-tmc-review.md, sha256 FB2DC038F7CF2274...,
  which scored main.tex 68D9B44F17A4E48D... (116379 B, mtime 2026-10-07 17:05).
New evidence reviewed: the S1' server-optimizer round, results_server_optimizer/round_v1/
  (instruction sha256 14b09cbfafa40db0..., driver sha256 308007730989dafc...,
  frozen config sha256 a041ba42e9c139f7...), together with the repository's own frozen E3 run tree.
```

## 1. What changed in the manuscript, and why this is not a plain version comparison

The manuscript changed **after** the round-13 review, and I was not told. It was `68D9B44F…`
(116 379 B, 17:05) when I reviewed it and is `D4FB164D…` (116 806 B, 22:57) now — a net **+6 lines**. I
reconstructed the round-13 target byte-exactly from the two blocks I had removed from it earlier
(verified against `68D9B44F17A4E48D…`, 116 379 B, at `_r13_build/main_prev_68D9B44F.tex`) and diffed.
The change is one hunk, `+8/−2`, entirely inside the NSW-Traffic sentence of the Limitations
subsection:

* **Removed**: "for every local budget from $2$ to $20$ steps" — a coverage overstatement I charged in
  round 13 (`NEW-r13-1`), because only four budgets (2, 5, 10, 20) were run and the 2-step rung was
  inherited from the sealed E2 grid rather than trained.
* **Added**: a mechanism sentence ("The server applies η times the step-normalized client update once
  per window, so the global step equals one gradient step whatever the local budget, and raising that
  budget from 2 to 20 steps leaves the gap unchanged") and three measured numbers (0.26 %–0.40 %
  total-norm movement on all three blocks, mostly through the output bias; the centralized reference
  "trained with Adam" moving its first layer by 12 %).
* `On that block the federated learner…` became `The federated learner, not the weighting, therefore
  limits the prediction endpoint.`

I recomputed the three added numbers rather than accepting the prose: 0.26 %–0.40 % is right
(0.261404 / 0.396509 / 0.278629 % on seeds 30001–30003); "mostly through the output bias" is right
(`head.8.bias` is the top-1 tensor by squared movement for both frozen and FedAdam arms, 29.6–43.0 %);
and "trained with Adam … by 12 %" is right in substance — `central_real.py` L106 really does use
`torch.optim.Adam`, and `central_all` moves `head.0.weight` by 12.1524 %. Two precision notes: 12 %
matches `central_all` (12.15 %), not `central_delivered` (11.20 %), so "the centralized reference"
needs disambiguation; and the mechanism sentence is an **algebraic identity** of the step-normalized
update, not a measurement.

Because the manuscript *text* changed by one hunk while the *evidence base* changed by a whole
experiment, this review reports the two separately, as the contract requires.

## 2. Relative-progress scorecard (text only, `68D9B44F` → `D4FB164D`)

| Dimension | Historical | Current | Delta | Weight | Explained by |
|---|---:|---:|---:|---:|---|
| Originality | 2 | 2 | 0 | 0.10 | no new contribution claim |
| Soundness | **4** | 0.20 | high | The "no arm beats a constant, therefore no skill" reading is **withdrawn** (section 3): the constant was an oracle over the test split while the arms are fitted on the train split, whose target location differs by +7.36 on SensorScope and −0.81 on U-Air. What remains is one printed inference — L2220–L2221 derives a learner-level limit from an optimizer and step-count contrast the sentence itself names. The theorems, the structural construction and the relative comparisons are untouched. | Delete or condition L2220–L2221; attribute the limit to the frozen server step, or retrain the centralized comparator under the same optimizer | +1 |
| Evidence | 3 | 0.25 | high | Unchanged from round 13 in kind: still no pre-registered endpoint whose headroom exceeds its own detectable effect and which changes a prediction or a deployment decision. Added this round: the undisclosed train → test target-location shift that dominates the SensorScope and U-Air absolute errors (section 3), a reporting gap rather than an invalidity. | Report the per-split target statistics next to the absolute RMSE; one pre-registered endpoint on a block whose target is concentrated at the aggregation level | +1 |
| Clarity | 4 | 0.15 | high | The round-13 overstatement is fixed. Still open: L2160–L2162 calls `+0.768` "the small margin" while L1834 calls it "above the `0.5` pp practical line" and L2092 gives `p_Holm = 2.7×10^{-5}`; L2207's `0.17 %` bound is crossed by its own source (0.1747 %); and the new "centralized reference" does not say whether it means `central_all` (12.15 %) or `central_delivered` (11.20 %). | Fix the three sites | +1 |
| Reproducibility | 2 | 2 | 0 | 0.10 | unchanged; the edit adds three more numbers that are in no index |
| Significance | 2 | 2 | 0 | 0.10 | unchanged |
| Related work | 3 | 3 | 0 | 0.05 | not re-searched |
| Terminology | 4 | 4 | 0 | 0.05 | no collision |

**Weighted progress delta = 0.00 → classification `unchanged`.** The revision fixed one of the three
clarity deductions I charged in round 13 and added one comparable presentation problem. Removing the
false exhaustiveness claim was correct and the replacement mechanism sentence is accurate.

## 3. A finding I withdrew, and the narrower one that replaced it

**Withdrawal (2026-10-08, after the author pointed at the split statistics).** An earlier version of
this section reported that on SensorScope and U-Air every deposited arm is 60–282 % worse than the
best constant predictor, and inferred that those arms have no skill and that the paper's endpoint
measurements are therefore vacuous. **That inference is wrong and is withdrawn.** The comparison is
arithmetically correct, but the constant it uses is an *oracle* constant: it knows the **test-split**
target mean, which a model fitted on the train split cannot know. What it actually measures is a
train-to-test target-level shift:

| block | train target mean (sd) | validation | **test** | has the test location left the train location? |
|---|---:|---:|---:|---|
| SensorScope | **+0.3006** (1.1554) | +2.0186 (2.8301) | **+7.6572** (2.0878) | **yes, by +7.36** |
| U-Air | **−0.0000** (1.0000, standardised) | −0.1456 (1.2596) | **−0.8066** (0.6781) | **yes, by −0.81, with a scale change** |
| NSW-Traffic | **+0.0000** (1.0000) | +0.0088 (0.9945) | **+0.0027** (1.0067) | **no, effectively identical** |

The degeneracy appears on exactly the two blocks whose test location has moved, and skill appears on
exactly the one block whose location has not. Decomposing SensorScope's reported error (RMSE 7.9144,
MSE 62.638) gives 58.279 (93.0 %) from the level gap and 4.359 (7.0 %) from the target's own spread,
so the reported `RMSE_μ` there is dominated by the shift rather than by prediction quality.

**Attribution, also conceded.** These arms share one windowed server step in this repository
(`theta <- theta - eta * sum_i alpha_i u_i` with a step-normalised client update), and swapping the
aggregation weights leaves them all near initialisation. That is a property of **this implementation**,
not of the algorithms the arms are named after: neither McMahan's FedAvg nor Xie's FedAsync was tested
on these data, and the paper already states that these are not official reproductions and that FedCure
is not included. Statements in this report are therefore about this repository's re-implementations
only.

The measurements below are retained because they are what the withdrawal rests on, and because they
bound how much the arms differ from one another.

### The retained measurements

I scored **every arm present in the frozen E3 run tree**, seed 30001, and a sample from the other six
trees that hold SensorScope/U-Air evidence, through the repository's own prediction path
(`runner._predict` + `_mu_weights_for_test` + `metrics.rmse_mu`). My re-computed `RMSE_μ` reproduces
every stored value exactly (e.g. SensorScope `fedavg_window` 7.9144 vs stored 7.914361980993586), so
the comparison is apples-to-apples with the paper's own metric.

`RMSE_μ` is a weighted root-mean-square error with weights normalised to one, so the best constant
predictor is the weighted mean of the target and its error is the target's weighted standard
deviation.

| block | target weighted mean | target weighted sd | zero predictor | arms scored | arms better than the best constant |
|---|---:|---:|---:|---:|---:|
| SensorScope | 7.6572 | **2.0878** | 7.9367 | 11 (+79 across other trees) | **0** |
| U-Air | −0.8066 | **0.6781** | 1.0537 | 11 (+79 across other trees) | **0** |
| NSW-Traffic | 0.0027 | 1.0067 | 1.0067 | 6 | 6 (−0.1 % to −4.2 %) |

The same pattern holds in every tree that produced the paper's SensorScope/U-Air numbers —
`results_h_headroom` (the ceiling's own trees), `results_h_response_shift`, `results_gate_dose`,
`results_w1_ladder`, `results_int_r`, `results_active_set_repair` — with 0 of 90 scored checkpoints
better than the constant. Because the level shift is common to all arms, this bounds the arms'
**mutual** differences; it does not licence the skill inference that is withdrawn above.

### What survives after the withdrawal, and what does not

* **The relative comparisons survive.** The level shift is common to every arm on a block, so the Holm
  family, `H`, and the paired-difference MDEs are not invalidated by it. My earlier claim that they are
  uninformative because the arms are non-learners is withdrawn.
* **One reporting gap remains**, narrower than what I first wrote: the train → validation → test
  target-location shift on SensorScope (+0.30 → +2.02 → +7.66) and U-Air (0.00 → −0.81) is nowhere
  disclosed, and on SensorScope it accounts for 93 % of the reported squared error, so a reader cannot
  tell whether `RMSE_μ ≈ 7.91` reflects predictive quality or a level extrapolation. This is a
  disclosure and interpretability point, not a validity point, and the split statistics plus one
  sentence fix it.
* **"No prediction-endpoint contrast survives Holm correction" (L2100–L2105)** stands as written.
* **The new Limitations sentence (L2220–L2221) is still the paper's weakest claim**, and the rebuttal
  does not address it: it infers a learner-level cause from an optimizer and step-count contrast that
  the sentence itself discloses.
* **The ceiling's `H ≈ 0` on SensorScope and U-Air cannot be tested** in the current evidence: the
  level shift and the shared server step both sit between the arms and the endpoint. On NSW-Traffic,
  the one block with neither problem, `H` has mean −0.0807 but 4 of 5 seeds are positive
  (+0.0208, +0.0091, +0.0061, +0.0174, −0.4570), the median is +0.0091, and dropping the one outlier
  gives +0.0134 with CI [+0.0076, +0.0191] — slightly *above* the 0.5 % bar. S1' therefore neither
  strengthens nor refutes the ceiling; it shows that the question is not settled.

## 4. What the S1' round does and does not establish

S1' replaced only the federated server step, on the frozen checkpoints, data, model, weights, scenario
and seeds, and ran gates before any grid run (identity test: 32/32 deterministic fields equal and a
byte-identical final checkpoint; determinism; a reads-after-update audit). Its arithmetic is sound:
`MOVEMENT.csv` reconciles with all 129 checkpoints at ratio 1.0000; the frozen baselines are
0.261404 / 0.396509 / 0.278629 %; the FedAdam arms at `η_s*` move 18.366235 / 7.311324 / 9.151184 %
= 70.26× / 18.44× / 32.84×; `H`, the 10 000-draw percentile bootstrap and `MDE80` reproduce to the
last digit. I verified the override is an identity on all three blocks myself, including the traffic
block that amendment A2 had excluded from G0.

| block | frozen fedavg | FedAdam fedavg | central_delivered | FedAdam vs central | movement frozen → FedAdam |
|---|---:|---:|---:|---:|---|
| SensorScope | 7.90894 | 7.84527 | 7.95260 | −1.35 % | 0.262 % → 2.49 / 6.11 / 18.37 % |
| U-Air | 1.15992 | 0.97749 | 1.17357 | −16.71 % | 0.427 % → 2.80 / 7.31 / 22.06 % |
| NSW-Traffic | (no E3 arm) | 0.83509 | 0.97377 | −14.24 % | → 4.05 / 9.15 / 22.02 % |

**Three readings, and the first two are retractions of what an uncritical reading would say.**

1. **"The server optimizer makes the federated learner train" holds on NSW-Traffic only.** There the
   FedAdam arm is 17.8 % better than the best constant with prediction sd 0.565 against a target sd of
   1.007 and correlation +0.590 — genuine learning. On SensorScope the FedAdam arm is still +281 %
   worse than a constant, and on U-Air it moves from +78.6 % to **+54.7 % worse than a constant**:
   the apparent "−15.7 % improvement" is a near-constant moving toward zero, not the model learning.
2. **"The ceiling argument is strengthened" is therefore withdrawn.** That reading is defensible only
   on NSW-Traffic, where the oracle-margin member (`raven_simoracle`) is worse than FedAvg. On
   SensorScope and U-Air the round reproduces the degeneracy rather than resolving it. Note also that
   the round's `H` uses `raven_simoracle`, not the paper's "best member evaluated on true margins"
   (L2113–L2115), so even on traffic it is a bound from one member, not the class maximum.
3. **The federated-versus-centralized comparison is not like-for-like, and on two blocks not
   meaningful at all.** The centralized reference is `torch.optim.Adam` at `lr = 1e-3` for
   `max(local_steps*10, 20) = 20` minibatch steps of 32 units (`central_real.py` L106/L111–L117;
   `runner.py` central branch), moving 2.31–3.33 % of its total norm; the federated arms get one
   step-normalized SGD update per window for 100 windows, moving 0.26–0.43 %. Both are severely
   undertrained, and on SensorScope and U-Air both are worse than a constant, so `N3' PASS`
  (0.986505 / 0.832921 / 0.857589) compares the FedAdam federated arm against the frozen `central_delivered` reference; on SensorScope and U-Air that comparison sits inside the same train-to-test level shift as the rest of those blocks (section 3), so it inherits that caveat rather than establishing federated superiority over a fair centralized counterpart.
   whether the federated learner learns. `S1P_REPORT.md` deviation 7 concedes that the like-for-like
   control was not run.

## 5. Absolute-readiness scorecard (current manuscript, with the new evidence)

| Dimension | Score | Weight | Confidence | Deduction | Repair condition | Expected movement |
|---|---:|---:|---|---|---|---|
| Originality | 2 | 0.10 | medium | Unchanged: the objects are deployment-target semantics, a three-layer pre-outcome factorization and a finite-window feasible set, with convex matching and two-stage IPW declared as prior ingredients. FedPALS/FedIPW not re-searched. | A constraint-and-information mapping stating an irreducible difference | +1, not enough alone |
| Soundness | **2** | 0.20 | high | **`newly_revealed_by_evidence`.** On SensorScope and U-Air all 11 arms, including both centralized references, are 60–282 % worse than the unconditional-mean predictor under the paper's own metric, and the models' prediction sd is 0.023–0.198 against target sds of 2.088 and 0.678. The paper's central measured quantities (ceiling `H`, the paired-difference MDEs, the Holm family) are computed on those models and reported as properties of "these endpoints" (L2128), and L2220–L2221 attributes a learner-level limit from an optimizer contrast. The alignment theorems themselves are untouched. | Disclose the degeneracy and report a mean/unconditional baseline next to every `RMSE_μ`; re-run the ceiling and the Holm family on a configuration that at least fits the target mean; state which claims are class-level and which are configuration-level | +2 to +3 if the measurements are redone; the theorems alone do not carry the measurement claims |
| Evidence | **2** | 0.25 | high | **`newly_revealed_by_evidence`.** The evidence package is large, precisely documented and reproducible — and on two of three blocks it measures noise around a constant. No naive baseline appears anywhere in main.tex, supplemental.tex or appendix.tex, so the reader cannot detect this. This sits at the boundary of 1 ("central evidence misleading"); it is 2 rather than 1 because the evidence exists, is auditable, and the traffic block is sound. | One pre-registered endpoint on a block whose target is concentrated at the aggregation level, with headroom above its detectable effect, measured on an arm that beats the unconditional baseline | +1 is not available without the Soundness repair first |
| Clarity | 3 | 0.15 | high | The round-13 overstatement is fixed. Still open: L2160–L2162 calls `+0.768` "the small margin" while L1834 calls it "above the `0.5` pp practical line" and L2092 gives `p_Holm = 2.7×10^{-5}`; L2207's `0.17 %` bound is crossed by its own source (0.1747 %); the new "centralized reference" does not say whether it means `central_all` or `central_delivered`; and nothing in the text lets a reader see that the arms do not fit the target mean. | Fix the three sites and add the baseline column | +1 after the Soundness repair |
| Reproducibility | 2 | 0.10 | high | Unchanged and now further behind: the released bundle still differs from the paper on 3 of 9 figure files and five tables, three drivers are lost, `w1/PAPER_NUMBERS.csv` has zero rows for the values added at 17:05 and 22:57, and the shipped `main.pdf` is the **2026-10-06 20:45** artifact — two revisions behind (890 040 B / 17 pp against the current 18 pp / 893 440 B rebuild). Credit where due: the artifacts are complete enough that I found the degeneracy from them, which is what reproducibility is for. | Deposit or name the supporting trees, add the index rows, refresh the PDF and the bundle | +1 |
| Significance | 2 | 0.10 | medium | Unchanged for the manuscript as written, and now constrained by §3: the measurement contribution rests on comparisons among non-learners. The S1' round does contain one genuinely positive, decision-relevant result — on NSW-Traffic a server-optimizer change yields a model 17.8 % better than the unconditional baseline where the frozen pipeline was not — but none of it is in the paper. | Write up the traffic result as part of the contribution and show a deployment decision that changes | +1 to +2 |
| Related work | 3 | 0.05 | medium | Not re-searched; irreducible-positioning gap unchanged. | The mapping named under Originality | ±1 |
| Terminology | 4 | 0.05 | high | Residual note: "closable gap" vs "closed by uniform weights" remain two near-identical names for two different objects. | Fold the names together | none |

Weighted readiness = 0.10×2 + 0.20×4 + 0.25×3 + 0.15×4 + 0.10×2 + 0.10×2 + 0.05×3 + 0.05×4 = **3.10**.

**Overall stance: 4/10, lean reject.** Round 13 was 5/10 borderline at 3.30, and I first wrote 3/10 here on the strength of the finding withdrawn in section 3; that score was not justified and this correction raises it. What remains is one moderate methodological concern (L2220–L2221 derives a learner-level cause from an optimizer contrast) plus one reporting gap (the undisclosed train → test target-level shift). Neither is fatal, no theorem and no printed number is affected, and the relative comparisons stand. If the level shift is stated as an intended out-of-period evaluation and the per-split target statistics are reported, this moves to 5/10.

## 6. Claim-evidence audit of the affected claims

| Claim | Where | Evidence provided | Strength | Deduction | Required fix |
|---|---|---|---|---|---|
| Structural alignment within a descriptive +0.5 % worst-group tolerance, **not** an RMSE win | Abstract L87–L89 | 20-seed Holm family; the ceiling | **weak** | The family is computed on arms that do not fit the target mean on two blocks, so "not an RMSE win" is true of non-learners | Add the baseline column; re-run on a configuration that fits the mean |
| The canonical program "does not prove that deployment-target risk is optimized" | Abstract L77–L79 | Theorem with A1–A3 | adequate | Unaffected | none |
| No recoverable gain: headroom did not reach the 0.5 % bar | L2113–L2119 | Frozen stress grid; SS MDE 0.17–0.36 pp; U-Air \|H\| ≤ 0.217 % | **weak on SS/UA** | `H` is a difference of two near-constant predictors there; only NSW-Traffic shows a learned comparison | Re-measure on arms that beat the unconditional baseline |
| "The gap is a property of these endpoints rather than of an over-easy regime" | L2125-L2128 | Propensity hardening (-15-21x) | **not testable on SS/UA with the current evidence** | The level shift and the shared windowed server step both sit between the arms and the endpoint, so `H` near 0 there cannot separate "no recoverable gain" from "the members do not differ". The degenerate-predictor rationale I first gave is withdrawn (section 3); on NSW-Traffic, the one clean block, `H` is one outlier away from being positive | Report the split statistics; test the ceiling on the block without a level shift |
| "The federated learner, not the weighting, therefore limits the prediction endpoint" | L2220–L2221 | Frozen arms' 0.26–0.40 % movement vs the Adam reference's 12 % | **contradicted / non sequitur** | The contrast is an optimizer and step-count asymmetry the sentence itself discloses; on two blocks both sides are worse than a constant | Delete or condition; attribute to the frozen server step |
| "The server applies η times the step-normalized client update once per window…" | L2214–L2216 | `window_runner.py` L1155–L1167; `client.py` L104–L107 | **strong — verified** | Accurate, and an algebraic identity rather than a measurement | none |
| "the federated parameters move 0.26%–0.40% … mostly through the output bias" | L2217–L2218 | frozen checkpoints vs seed-reconstructed init | **strong — verified** | 0.261404 / 0.396509 / 0.278629 %; `head.8.bias` top-1 | none |
| "the centralized reference, trained with Adam, moves its first layer by 12%" | L2219 | `central_all` `head.0.weight` = 12.1524 % | strong, one ambiguity | 12 % matches `central_all` (12.15 %), not `central_delivered` (11.20 %); the training is 20 Adam steps | Name the arm and the step count |
| "window FedAvg stays 2.8%–3.0% above a centralized model trained on the same delivered data" | L2213 | E2-referenced S1 ladder (1.0278–1.0296) | adequate for that runner | True of the E2 runner and the frozen step; on traffic the FedAdam arm is −14.24 % against the same reference | State the runner and the asymmetry |
| Masking up to 40 % raises ρ_r to 0.388 with no prediction cost above 0.17 % | L2205–L2209 | `DOSE_SUMMARY.csv` | adequate | `0.17 %` is crossed by its own source (0.1747 %) — round-13 `F-L`, still open | write `0.175 %` or a containing bound |
| The projection is worth `+0.768` pp and is "the small margin" | L1834 vs L2160–L2162 | `PART_A_REPORT.md` L15/L17 | contradictory | Round-13 `F-H`, still open | Re-word L2160–L2162 |

## 7. Multi-reviewer panel


> **Read this panel with section 3.** The best-justified, critical and adversarial entries below were written before the withdrawal, and their "worse than a constant / no skill" premises are superseded by it. Their remaining content - the structural contribution is untouched, the new numbers at L2214-L2221 are correct, the comparator is not like-for-like, the round's arithmetic reproduces - is unaffected and still stands.
```text
Reviewer: Best-justified
Lens: strongest defensible case
Score / score tendency: 4/10
Confidence: high
Main positive signal: the structural contribution stands on its own. Nothing in this review touches
  the three-layer pre-outcome factorization, the finite-window feasible set, or the alignment theorem,
  and the paper's own hedges ("does not prove that deployment-target risk is optimized", "not an RMSE
  win") are honest. The pipeline is also demonstrably capable of learning: on NSW-Traffic the FedAdam
  arm beats the unconditional baseline by 17.8 % where the frozen arm did not.
Main negative signal: the measurement half of a method-plus-measurement paper currently measures two
  blocks of non-learners and says nothing about it.
Evidence basis: L1775-L1860; L2100-L2128; DO_THE_ARMS_LEARN.json; ALL_ARMS_VS_CONSTANT.json
Score-change condition: add the unconditional baseline, re-run the ceiling and the Holm family where
  the arms actually fit the mean.

Reviewer: Critical
Lens: strongest reject case
Score / score tendency: 2/10
Confidence: high
Main positive signal: the arithmetic everywhere is exact and the artifacts are complete enough to be
  audited, which is how the defect was found.
Main negative signal: on SensorScope the best arm is 265.6 % worse than a constant and on U-Air 60.3 %
  worse, yet the paper reports MDEs of 0.17-0.36 pp as evidence of sensitivity and concludes the gap is
  "a property of these endpoints". A reader cannot detect this from the text because no naive baseline
  appears anywhere. The declared contribution is a measurement that cannot discriminate.
Evidence basis: section 3 table; grep for naive|persistence|constant predictor|mean predictor across
  main.tex, supplemental.tex, appendix.tex -> zero matches
Score-change condition: none available by wording alone; requires new measurements.

Reviewer: Method / soundness (commissioned independent check)
Lens: whether the causal sentences match the diagnostics
Score / score tendency: 3/10
Confidence: high on the round, medium on the proofs (not re-derived)
Main positive signal: the S1' gates are unusually strong - the override is proven to be an identity on
  all three blocks (32/32 deterministic fields equal, byte-identical checkpoints), determinism is shown,
  and the reads-after-update audit names the one stale log field; every load-bearing number I checked
  reproduced.
Main negative signal: the round's own H uses raven_simoracle rather than the paper's "best member on
  true margins"; on SS/UA both arms of H are constant-equivalent; and Stage C actually ran only on
  traffic, because the driver skips the blocks its own K_r clause excludes, so the SS/UA H values in
  the round are re-used Stage A output.
Evidence basis: R13_S1PRIME_REVIEW.md; s1p_driver.py L836; S1P_STAGE_C_H.json
Score-change condition: an optimizer-matched control plus H recomputed under FedAdam.

Reviewer: Adversarial / falsification (commissioned independent check)
Lens: try to break the round's four claims
Score / score tendency: 2/10
Confidence: high
Main positive signal: claim 2 (movement) is established - MOVEMENT.csv reconciles with all 129
  checkpoints at ratio 1.0000 - and the H/bootstrap/MDE80 arithmetic reproduces to the last digit.
Main negative signal: claim 1's inference is rejected (PASS on two blocks is motion of a near-zero
  constant), claim 3's reading is weakened (traffic's mean H of -0.0807 is one outlier seed: the five
  values are +0.0208, +0.0091, +0.0061, +0.0174, -0.4570; median +0.0091, 4/5 positive,
  drop-the-outlier mean +0.0134 with CI [+0.0076, +0.0191]), and claim 4 splits by block. I reproduced
  the constant-predictor comparison independently and it holds.
Evidence basis: R13_S1PRIME_ADVERSARIAL_REVIEW.md; DO_THE_ARMS_LEARN.json; ALL_ARMS_VS_CONSTANT.json
Score-change condition: a matched-effort centralized reference.

Reviewer: Reproducibility auditor
Lens: can a reader rebuild the printed numbers from what the paper names
Score / score tendency: 2/5 on this dimension
Confidence: high
Main positive signal: every number I tested is recomputable from the frozen tree, and the round's
  artifacts let an auditor discover the degeneracy.
Main negative signal: bundle drift (3 of 9 figure files, five tables), three lost drivers, zero index
  rows for the newly added numbers, and a shipped PDF two revisions behind.
Evidence basis: bundle sweep; PAPER_NUMBERS.csv; main.pdf 2026-10-06
Score-change condition: deposit or name the sources and refresh the PDF.

Panel synthesis:
Agreement: the structural/theorem contribution is untouched; the new numbers at L2214-L2221 are
  correct; the measurement program on SensorScope and U-Air does not support claims about endpoints.
Disagreement: whether "the arms are worse than a constant" is a disclosure problem (sympathetic) or a
  fatal validity problem (critical). The disagreement is factual and is settled by adding the baseline:
  if the arms cannot beat the mean, no endpoint claim survives; if they can once trained, the paper
  needs new runs.
Decisive accept axis: a configuration in which the arms beat the unconditional baseline, with the
  ceiling and the Holm family recomputed there.
Decisive reject axis: a measurement contribution computed on non-learners with no naive baseline
  disclosed anywhere in main, supplemental or appendix.
Unresolved evidence: proofs not re-derived; FedPALS/FedIPW not re-searched; the delta_group question is
  unanswerable from the artifacts because the only delta_group column available is affected by the
  table defect in section 8.
Final calibrated stance: 3/10, reject - evidence-and-protocol fatal risk, not a refuted theorem.
```

## 8. Defects found in this round's own artifacts (all mine or inherited, none affect the verdict)

| ID | Defect | Status |
|---|---|---|
| A1 | `tables/STAGE_A_GRID.csv` copies the **selected-`η_s`** test value into all three `η_s` rows: `s1p_driver.py` merges the test rows on `(block, seed)` and omits `eta_s`. Reproduced: SensorScope CSV `7.845273 ×3` against run dirs `7.870630 / 7.891182 / 7.845273`; U-Air `0.977494 ×3` against `1.095797 / 0.977494 / 1.033618`; traffic `0.835094 ×3` against `0.874426 / 0.835094 / 0.915626`. `N3'` is unaffected (the selected-`η_s` value is correct and the run directories carry it), but the table cannot evidence `η_s` sensitivity. | **fixed in this pass** |
| A2 | `Stage C` ran only on NSW-Traffic; `s1p_driver.py` L836 skips blocks its own `K_r` clause excludes, and the SensorScope/U-Air H values in the round are re-used Stage A output. | disclosed; no number changes |
| A3 | `MDE80` computed at n = 5 where the instruction's section 6 says n = 15 (amendment A3); no verdict changes because every conditional is False while the mean H is negative. | disclosed |
| A4 | `kr_le3_share` is read from one cell's `run_dir` (seed 30001: 73/97, 49/74, 11/99) rather than pooled (0.7549 / 0.7539 / 0.1385). Direction unchanged; the label is misleading. | disclosed |
| A5 | The driver's Stage C `DictWriter` field list cannot emit the delivered 18-column `STAGE_C_H.csv`, and no script writes `MOVEMENT.csv` or `STAGE_B_GRID.csv`; the delivered tables' numbers are correct (all 129 movement rows reconcile) but they were assembled by hand. | disclosed |
| A6 | The `_validation_mu` docstring and `S1P_FROZEN_CONFIG.json` describe the weights as built by `TargetBuilder(split='validation')`; the full frame is passed and `TargetBuilder` filters internally. The code is correct and provably leak-free (validation/test unit overlap 0, time-index overlap 0), but the description is wrong. | disclosed |
| A7 | The frozen configuration was written four times (`fe84a4c6` → `57b4bcec` → `f56f224c` → `a041ba42`, the last on disk). SensorScope `η_s* = 0.01` and U-Air `η_s* = 0.003` were already selected at the first freeze and both `N3'` ratios are byte-identical across all four, so pre-registration survives; the interim `f56f224c` freeze is undisclosed. | disclosed |
| A8 | All 87 run ledgers record `runner_source_hash`, `method_source_hash`, `source_manifest_hash` and `dataset_hash` as null, `src/raven_mcs/e3/real_runner/runner.py` is untracked in git, and its mtime is after the SensorScope/U-Air Stage A runs. No number is invalidated (the current tree reproduces all 75 checkpoint-derived `final_metrics.json`, and I re-verified the identity property), but that provenance is inference rather than witness. | disclosed |

## 9. Concern-to-action table

| ID | Severity | Action | Owner | Stance effect |
|---|---|---|---|---|
| R14-1 | **Fatal** | Add the unconditional-mean (and zero) baseline next to every reported `RMSE_μ`, and state plainly that on SensorScope and U-Air all arms are worse than it. This is a disclosure that must happen regardless of what else is done. | user; `ccf-paper-writer` | Soundness 2→3 |
| R14-2 | **Fatal** | Re-run the ceiling `H` and the Holm family on a configuration whose arms beat the unconditional baseline. Without this the measurement contribution cannot be claimed. | `ccf-experiment-designer` | the only route back to a competitive stance |
| R14-3 | Major | Delete or condition L2220–L2221; the conclusion at L2244–L2246 already models the right hedge ("in the tested family"). | `ccf-paper-writer` | Soundness/Clarity |
| R14-4 | Major | Retrain the centralized comparator under the same optimizer and step budget as the federated arms before any federated-versus-centralized sentence. | `ccf-experiment-designer` | Soundness |
| R14-5 | Moderate | Name which centralized arm the 12 % refers to and state the 20-step Adam budget at L2219. | `ccf-paper-writer` | Clarity |
| R14-6 | Moderate | Fix the two remaining clarity defects: L2160–L2162's "the small margin" against L1834/L2092, and L2207's `0.17 %` bound that its source crosses. | `ccf-paper-writer` | Clarity |
| R14-7 | Moderate | Refresh the shipped PDF (two revisions stale) and index the numbers added at 17:05 and 22:57. | user; `ccf-paper-writer` | Reproducibility |
| R14-8 | Minor | Record the eight artifact disclosures of section 8 in the round's own report so future readers are not misled by A1/A2/A4. | user | none |

## 10. Checks run

- Hash and provenance: current `main.tex` `D4FB164D…` (116 806 B, 22:57); round-13 target `68D9B44F…`
  reconstructed byte-exactly and verified against the recorded hash; diff enumerated (one hunk, +8/−2).
- Rebuild in fixed order out of tree: `main.pdf` **18 pp**, 0 errors, 0 undefined, 0
  multiply-defined, 0 Overfull; `supplemental.pdf` 16 pp with 1 Overfull `\vbox`. The tree's own
  `main.pdf` is `2026-10-06 20:45`, 890 040 B, 17 pp.
- **Constant-predictor audit (run, then withdrawn as evidence - kept for audit).** All 11 SensorScope arms, all 11 U-Air arms and all 6 NSW-Traffic arms in the frozen E3 tree were scored at seed 30001 through `runner._predict` + `_mu_weights_for_test` + `metrics.rmse_mu`, each recomputation matching the stored `RMSE_mu` exactly, and 90 further checkpoints were scored across the six other trees holding SensorScope/U-Air evidence. The arithmetic stands (`DO_THE_ARMS_LEARN.json`, `ALL_ARMS_VS_CONSTANT.json`, `PAPER_TREES_VS_CONSTANT.json`), but the skill inference drawn from it is withdrawn in section 3.
  scored seed 30001 through `runner._predict` + `_mu_weights_for_test` + `metrics.rmse_mu`, each
  recomputation matching the stored `RMSE_mu` exactly; weighted target mean, target sd, zero predictor,
  prediction sd and correlation reported per arm. Written to `DO_THE_ARMS_LEARN.json` and
  `ALL_ARMS_VS_CONSTANT.json`.
- Baseline search: `naive|persistence|constant predictor|predicting the mean|mean predictor|
  unconditional|reference RMSE|baseline RMSE|prior mean` across `main.tex`, `supplemental.tex`,
  `appendix.tex` → **zero matches**.
- The three numbers added at 22:57 recomputed from frozen checkpoints against a seed-reconstructed
  initial θ on seeds 30001–30003: 0.261404 / 0.396509 / 0.278629 %; `head.8.bias` top-1 for both frozen
  and FedAdam arms (29.6–43.0 % of squared movement); `central_all` `head.0.weight` 12.1524 %,
  `central_delivered` 11.1986 %.
- Optimizer asymmetry verified in code: `central_real.py` L106 (`torch.optim.Adam`, `lr=1e-3`),
  L111–L117 (minibatch loop), `runner.py` central branch (`local_steps=max(local_steps*10, 20)`);
  `window_runner.py` L1155–L1167 and `client.py` L104–L107 for the federated step.
- Two commissioned independent checks read in full and folded in with attribution:
  `_r13_build/R13_S1PRIME_REVIEW.md` and `_r13_build/R13_S1PRIME_ADVERSARIAL_REVIEW.md`, plus their
  scripts and raw outputs. Their dimension numbers came from their own baselines rather than from
  TMC-J-R4, so only their findings and directions are used here, mapped onto the frozen contract.
- Review evidence pack: `results_server_optimizer/round_v1/REVIEW_EVIDENCE_PACK.json`.

## 11. Unresolved or unverified

- The proofs in §VI were not re-derived.
- FedPALS and FedIPW were not re-searched.
- Whether a matched-effort centralized reference changes any `N3'` verdict is not determinable here; no
  such artifact exists. `R14-4` is a recommendation, not a result.
- The `delta_group` question cannot be answered from this workspace: the only `delta_group` column
  available is in `STAGE_A_GRID.csv`, which carries defect A1.
- **Revision log for this canonical file.** Three positions, all dated 2026-10-08, kept so the path is auditable. (1) First version: Soundness 3 / Evidence 3 / overall 2.90, 4/10, asserting that the S1' round *strengthens* the ceiling argument and that the federated arm "beats the centralized reference by 1.4–16.7 %" — both **withdrawn**. (2) Second version: after two commissioned independent checks returned, Soundness 2 / Evidence 2 / overall 2.30, 3/10, asserting that on SensorScope and U-Air every deposited arm is worse than the constant predictor and therefore has no skill — **the inference withdrawn**; the arithmetic was right but the constant was an oracle over the test split, and the deciding split statistics are in section 3. (3) This version: Soundness 4 / Evidence 3 / Clarity 4 / overall **3.10**, 4/10, with the train-to-test target-level shift as the surviving, narrower finding. The author's rebuttal is what forced position (3).
- The 22:57 edit's authorization is unconfirmed in the workspace; it is treated as a normal authorial
  revision so that the review assesses the text that exists.

## 12. Output self-check

- Section order follows the review contract; the text-only progress card and the readiness card are
  kept separate and confidence is reported as a third field.
- Every score of 3 or below carries a deduction and a repair condition; the large movement is
  attributed to `newly_revealed_by_evidence` with the exact measurement cited, and the text-only card
  is not penalised for a claim that pre-dates the revision.
- The decisive new finding was verified first-hand through the repository's own metric path, not
  accepted from a subordinate's summary, and it is stated with the numbers needed to refute it.
- Two earlier claims of mine are explicitly withdrawn rather than quietly edited.
- No prose was rewritten, no ledger updated by this report, no acceptance probability claimed.

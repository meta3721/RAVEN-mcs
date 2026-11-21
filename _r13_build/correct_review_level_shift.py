"""Correct the round-14 review: withdraw the 'no skill / worse than a constant' finding, replace it with
the train-to-test target-level shift, and re-score."""
from __future__ import annotations

import pathlib

P = pathlib.Path(r"C:\Cursor\raven.mcs\_r13_build\raven-mcs-tmc-review-r14.md")
t = P.read_text(encoding="utf-8")
EDITS = []

# --- 1. replace the section-3 opening with the withdrawal and the corrected finding ---
EDITS.append((
"""## 3. The decisive finding: on two of the three blocks, no arm beats the unconditional mean

I scored **every arm present in the frozen E3 run tree**, seed 30001, through the repository's own
prediction path (`runner._predict` + `_mu_weights_for_test` + `metrics.rmse_mu`). My re-computed
`RMSE_μ` reproduces every stored value exactly (e.g. SensorScope `fedavg_window` 7.9144 vs stored
7.914361980993586), so the comparison below is apples-to-apples with the paper's own metric.""",
"""## 3. A finding I withdrew, and the narrower one that replaced it

**Withdrawal (2026-10-08, after the author pointed at the split statistics).** An earlier version of
this section reported that on SensorScope and U-Air every deposited arm is 60-282 % worse than the
best constant predictor, and inferred that those arms have no skill and that the paper's endpoint
measurements are therefore vacuous. **That inference is wrong and is withdrawn.** The comparison
itself is arithmetically correct, but the constant it uses is an *oracle* constant: it knows the
**test-split** target mean, which a model fitted on the train split cannot know. The correct reading
is a train-to-test target-level shift, not a lack of skill:

| block | train target mean (sd) | validation | **test** | has the test location left the train location? |
|---|---:|---:|---:|---|
| SensorScope | **+0.3006** (1.1554) | +2.0186 (2.8301) | **+7.6572** (2.0878) | **yes, by +7.36** |
| U-Air | **-0.0000** (1.0000, standardised) | -0.1456 (1.2596) | **-0.8066** (0.6781) | **yes, by -0.81, with a scale change** |
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
is not included. Statements below are therefore about this repository's re-implementations only.

The measurements that follow are retained because they are what the withdrawal rests on, and because
they bound how much the arms differ from one another."))

# --- 2. replace the consequences block ---
EDITS.append((
"""### What this does to the paper's measurements

* **The ceiling.** L2125–L2128 concludes the oracle gap "is a property of these endpoints rather than
  of an over-easy regime". On SensorScope and U-Air the gap `H` is a difference between two
  near-constant predictors, so `H ≈ 0` there is what one expects from two constants and carries no
  information about the endpoint or about the method class. The claim is not supported on those two
  blocks.
* **The Holm family and the MDEs.** L2119–L2125 quotes a SensorScope paired-difference MDE of
  0.17–0.36 pp and U-Air |H| ≤ 0.217 %. Those intervals quantify noise between models that do not fit
  the target mean; a tight interval around a degenerate comparison is not sensitivity.
* **"No prediction-endpoint contrast survives Holm correction" (L2100–L2105).** True as arithmetic,
  but among non-learners the statement is close to vacuous.
* **The new Limitations sentence.** L2220–L2221 infers a learner-level cause from an optimizer
  contrast; given the above, the correct statement is stronger and more damaging: on two of three
  blocks the comparison is between models that have not learned even the unconditional mean.""",
"""### What survives after the withdrawal, and what does not

* **The relative comparisons survive.** The level shift is common to every arm on a block, so the Holm
  family, `H`, and the paired-difference MDEs are not invalidated by it. My earlier claim that they are
  "uninformative because the arms are non-learners" is withdrawn.
* **One real reporting gap remains**, and it is narrower than what I first wrote: the train -> validation
  -> test target-location shift on SensorScope (+0.30 -> +2.02 -> +7.66) and U-Air (0.00 -> -0.81) is
  nowhere disclosed, and on SensorScope it accounts for 93 % of the reported squared error. A reader
  cannot tell from the paper whether `RMSE_μ ≈ 7.91` reflects predictive quality or a level
  extrapolation. This is a disclosure and interpretability point, not a validity point, and it is
  fixable with the split statistics and one sentence.
* **"No prediction-endpoint contrast survives Holm correction" (L2100–L2105)** stands as written,
  subject to the same disclosure.
* **The new Limitations sentence (L2220–L2221) is still the paper's weakest claim**, and the author's
  rebuttal does not address it: it infers a learner-level cause from an optimizer and step-count
  contrast that the sentence itself discloses."""))

# --- 3. score rows ---
EDITS.append((
"""| Soundness | **2** | 0.20 | high | **`newly_revealed_by_evidence`.** On SensorScope and U-Air all 11 arms, including both centralized references, are 60–282 % worse than the unconditional-mean predictor under the paper's own metric, and the models' prediction sd is 0.023–0.198 against target sds of 2.088 and 0.678. The paper's central measured quantities (ceiling `H`, the paired-difference MDEs, the Holm family) are computed on those models and reported as properties of "these endpoints" (L2128), and L2220–L2221 attributes a learner-level limit from an optimizer contrast. The alignment theorems themselves are untouched. | Disclose the degeneracy and report a mean/unconditional baseline next to every `RMSE_μ`; re-run the ceiling and the Holm family on a configuration that at least fits the target mean; state which claims are class-level and which are configuration-level | +2 to +3 if the measurements are redone; the theorems alone do not carry the measurement claims |""",
"""| Soundness | **4** | 0.20 | high | The "no arm beats a constant, therefore no skill" reading is **withdrawn** (section 3): the constant was an oracle over the test split while the arms are fitted on the train split, whose target location differs by +7.36 on SensorScope and -0.81 on U-Air. What remains is one printed inference — L2220–L2221 derives a learner-level limit from an optimizer and step-count contrast the sentence itself names. The theorems, the structural construction and the relative comparisons are untouched. | Delete or condition L2220–L2221; state the frozen server step as the limit, or retrain the centralized comparator under the same optimizer | +1 |"""))

EDITS.append((
"""| Evidence | **2** | 0.25 | high | **`newly_revealed_by_evidence`.** The evidence package is large, precisely documented and reproducible — and on two of three blocks it measures noise around a constant. No naive baseline appears anywhere in main.tex, supplemental.tex or appendix.tex, so the reader cannot detect this. This sits at the boundary of 1 ("central evidence misleading"); it is 2 rather than 1 because the evidence exists, is auditable, and the traffic block is sound. | One pre-registered endpoint on a block whose target is concentrated at the aggregation level, with headroom above its detectable effect, measured on an arm that beats the unconditional baseline | +1 is not available without the Soundness repair first |""",
"""| Evidence | 3 | 0.25 | high | Unchanged from round 13 in kind: still no pre-registered endpoint whose headroom exceeds its own detectable effect and which changes a prediction or a deployment decision. Added this round: the undisclosed train -> test target-location shift that dominates the SensorScope and U-Air absolute errors (section 3), which is a reporting gap rather than an invalidity. | Report the per-split target statistics next to the absolute RMSE; one pre-registered endpoint on a block whose target is concentrated at the aggregation level | +1 Evidence |"""))

EDITS.append((
"""| Clarity | 3 | 0.15 | high | The round-13 overstatement is fixed. Still open: L2160–L2162 calls `+0.768` "the small margin" while L1834 calls it "above the `0.5` pp practical line" and L2092 gives `p_Holm = 2.7×10^{-5}`; L2207's `0.17 %` bound is crossed by its own source (0.1747 %); the new "centralized reference" does not say whether it means `central_all` or `central_delivered`; and nothing in the text lets a reader see that the arms do not fit the target mean. | Fix the three sites and add the baseline column | +1 after the Soundness repair |""",
"""| Clarity | 4 | 0.15 | high | The round-13 overstatement is fixed. Still open: L2160–L2162 calls `+0.768` "the small margin" while L1834 calls it "above the `0.5` pp practical line" and L2092 gives `p_Holm = 2.7×10^{-5}`; L2207's `0.17 %` bound is crossed by its own source (0.1747 %); and the new "centralized reference" does not say whether it means `central_all` (12.15 %) or `central_delivered` (11.20 %). | Fix the three sites | +1 |"""))

EDITS.append((
"""Weighted readiness = 0.10×2 + 0.20×2 + 0.25×2 + 0.15×3 + 0.10×2 + 0.10×2 + 0.05×3 + 0.05×4 = **2.30**.

**Overall stance: 3/10, reject.** Round 13 was 5/10 borderline negative at 3.30; the intervening
revision is a wash on the text, and the change is entirely evidence-driven. The calibration band is
"clear reject: fatal technical, novelty, evidence, policy, or venue issue", and the fatal-risk triage
names two entries that apply — "a main claim lacks evidence" and "the study design or evaluation
protocol is invalid". The one mitigating fact is that the failure is a *disclosure and protocol*
failure with a known repair, not a refuted theorem: the structural alignment results (L1775–L1860)
are untouched by anything in this review, and the traffic block shows the pipeline can learn.""",
"""Weighted readiness = 0.10×2 + 0.20×4 + 0.25×3 + 0.15×4 + 0.10×2 + 0.10×2 + 0.05×3 + 0.05×4 = **3.10**.

**Overall stance: 4/10, lean reject.** Round 13 was 5/10 borderline at 3.30, and I first wrote 3/10
here on the strength of the finding withdrawn in section 3; that score was not justified and the
correction raises it. What remains is one moderate methodological concern (L2220–L2221 derives a
learner-level cause from an optimizer contrast) plus one reporting gap (the undisclosed train -> test
target-level shift). Neither is fatal, no theorem or printed number is affected, and the relative
comparisons stand. If the level shift is stated as an intended out-of-period evaluation and the
per-split target statistics are reported, this moves to 5/10."""))

# --- 4. revision log ---
EDITS.append((
"""- **Revision log for this canonical file.** The first version of this round-14 review, written earlier
  on 2026-10-08, scored the manuscript Soundness 3 / Evidence 3 / Clarity 4 / overall 2.90 with a 4/10
  stance, and asserted that the S1' round "strengthens" the ceiling argument and that the federated arm
  "beats the centralized reference by 1.4–16.7 %". Two commissioned independent checks then returned,
  I reproduced their decisive measurement myself, and both of those assertions are **withdrawn** in
  sections 3 and 4. The corrected finding is materially worse for the paper, and it is recorded here
  rather than silently replacing the earlier text.""",
"""- **Revision log for this canonical file.** Three successive positions, all dated 2026-10-08, kept so
  the path is auditable. (1) First version: Soundness 3 / Evidence 3 / overall 2.90, 4/10, asserting
  that the S1' round *strengthens* the ceiling argument and that the federated arm "beats the
  centralized reference by 1.4–16.7 %" — both **withdrawn**. (2) Second version: after two commissioned
  independent checks returned, Soundness 2 / Evidence 2 / overall 2.30, 3/10, asserting that on
  SensorScope and U-Air every deposited arm is worse than the constant predictor and therefore has no
  skill — **the inference withdrawn**; the arithmetic was right but the constant was an oracle over the
  test split. (3) This version: Soundness 4 / Evidence 3 / Clarity 4 / overall **3.10**, 4/10, with the
  train-to-test target-level shift as the surviving, narrower finding. The author's rebuttal is what
  forced position (3), and the split statistics that decided it are in section 3."""))

for old, new in EDITS:
    n = t.count(old)
    assert n == 1, f"anchor count {n} for: {old[:80]!r}"
    t = t.replace(old, new)

# section-3 heading reference used elsewhere in the file
t = t.replace("`newly_revealed_by_evidence` is attributed to it in section 3", "`newly_revealed_by_evidence` is attributed to it in section 3")
t = t.replace("**`newly_revealed_by_evidence`.** The Limitations sentence asserts",
              "The Limitations sentence asserts")

P.write_text(t, encoding="utf-8")
print("review corrected: withdrawal recorded, section 3 replaced, scores revised to 3.10 / 4-10")
print("lines:", len(t.splitlines()))

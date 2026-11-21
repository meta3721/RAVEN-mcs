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
* **The ceil ing's `H ≈ 0` on SensorScope and U-Air cannot be tested** in the current evidence: the
  level shift and the shared server step both sit between the arms and the endpoint. On NSW-Traffic,
  the one block with neither problem, `H` has mean −0.0807 but 4 of 5 seeds are positive
  (+0.0208, +0.0091, +0.0061, +0.0174, −0.4570), the median is +0.0091, and dropping the one outlier
  gives +0.0134 with CI [+0.0076, +0.0191] — slightly *above* the 0.5 % bar. S1' therefore neither
  strengthens nor refutes the ceiling; it shows that the question is not settled.


# Warning (not inserted into the manuscript): a third-party rewrite removed the abstract's refusals

Recorded 2026-10-11. Assessment only. **No manuscript file was modified by this session for this item.**

## What happened

While computing the training-mean-predictor comparison, the manuscript changed under this session without
any write from it. All of this session's writes in that interval went to `_r13_build/` and
`results_paper_ceiling/`.

| | before | after |
|---|---|---|
| sha256 | `3CC106CA4B6087D9D6A47D69936ABF0CD95914B0285E1A86D3C938ACB5AD161C` | `6D6BE86C824FECDC6115819A9A7C234B2C8C2F3E3071E4B72606B452BBD83F3A` |
| size | 119922 B | 117624 B (-2298 B) |
| lines | 2345 | 2314 (-31) |
| abstract block | `8ad25984072ed33e` | `193bb6a8750f98af` changed |
| contribution list | `82c33423ed680a72` | `bb86d60ce90cd0c5` changed |
| title | `b917a3c614517ece` | unchanged |
| build | 18 pp | 18 pp, 0 errors, 0 Overfull, 0 undefined, em dashes 0 |
| ceiling-ladder insertions | absent | absent (this was not option A, B or C) |

## Removed from the abstract

1. `It does not prove that deployment-target risk is optimized.`
2. `The protocol development table reports structural alignment within a descriptive $+0.5\%$ worst-group tolerance, not an RMSE win.`
3. The U-Air cost disclosure: `turning Design on costs $6.885\%$ of $\mathrm{RMSE}_{\mu}$ and improves client--stratum mismatch by $4.990\%$`.
4. `On a T-Drive taxi replay, FedAU-Window and ObsUse-Window remain strongest.  No ranking jointly measures $R$, $O$, and $U$.`

## Added to the abstract

The two theorems (`prove unique solvability and plug-in stability of the calibration program`), the
recovery statement, `Paired component comparisons isolate the roles of correction and feasibility`, and
`characterize structural alignment and its relationship to deployment-weighted prediction error`.

## Removed from the contribution list

- The final bullet, which carried the measurement's own limits, including that no other objective term of
  (P2) is shown to contribute at the frozen configuration and that the prediction half's reading is the
  small Inst entry of the ablation table.
- `This is the formal basis for asking whether a model is trained for the population it is meant to serve,
  not whether completion RMSE is optimized.`
- `Usable-update correction is a third sequential factor, not an isolated empirical driver.`
- The self-limiting bullet title `What the measurement does not attribute`, replaced by
  `Component attribution relative to uniform aggregation`.

## Added to the contribution list

The plug-in stability claim (Lipschitz perturbation, not amplified in `alpha`), the sentence that the
Design factor is fixed by the deployment before the window opens, and the coverage-bound diagnostic
sentence.

## Why this needs the author's decision

- **Materiality.** The abstract no longer tells a reader that the prediction half is a null. The specific
  numbers survive in the body (the limitations paragraph still reports `-1.49%`, the `5.80%` detectable
  effect, and the two constants), so the paper does not contradict itself, but a reader of the abstract
  alone would not learn the negative result. The humanization policy's rule is that an observed result
  must not be hidden when omission would make the paper materially misleading; whether that threshold is
  crossed here is a judgement this session is flagging rather than asserting.
- **It undoes part of two completed repair rounds.** The two-constant disclosure and the metric
  definition are intact (`test-fitted constant` x4, `training-mean predictor` x5, `0.175` present), but the
  abstract-level disclosure that those constants exist to qualify is gone.
- **It invalidates the current review target.** Round 17 was written against `3CC106CA...` and its
  Clarity and Soundness reasoning rested in part on the abstract refusing both the optimisation claim and
  the RMSE win. Those refusals no longer exist, so a re-review against `6D6BE86C...` is required before
  the scorecard can be quoted.
- **It frees page budget.** 2298 B and 31 lines were released, so the ceiling ladder that was blocked at
  19 pp would very likely fit now. The blocked round should be re-measured rather than assumed.

## Recommended decisions

1. Re-run the review against `6D6BE86C...` (round 18), because round 17's target is superseded.
2. Decide the abstract's refusals explicitly: restore the two refusals and the cost disclosure, or record
   that the authors intend the abstract to carry only the positive readings.
3. Re-measure the ceiling-ladder insertion against the new baseline before treating the CW round as
   blocked.

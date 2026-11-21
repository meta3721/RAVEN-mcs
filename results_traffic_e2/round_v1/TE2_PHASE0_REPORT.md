# TE2 Phase 0 — power gate

Mode: re-scoring of stored checkpoints only. **No training run was executed.** Phase 0 exists
because the previous round skipped it and ended with an 80 % minimum detectable effect of 5.80 %
against an estimate of 1.49 %, i.e. it could not resolve the bar it was aimed at.

## Primary cell as realised

- priority rule: the region holding the largest share of the frozen pre-outcome target mass under
  `kappa = 1`; the realised masses are `region0 0.232558`, `region1/2/3 0.255814` each, so **three
  regions tie and the rule as written is not well defined**. The run resolved the tie by ascending
  region id, giving **region1**; an explicit tie-break must be added to the
  pre-registration before any confirmatory run.
- `kappa = 5` on that region gives region shares {'region0': 0.11494252873563215, 'region1': 0.6321839080459773, 'region2': 0.12643678160919536, 'region3': 0.12643678160919536} —
  a **top-1 share of 0.6322**, against the design table's analytic
  `0.6250` for four equal regions. Close, because the frozen regions are nearly equal.
- concentrated weight vector sha256 `ad8d43762f1f1cb3389a0abfdab0dc0bd003f70c5c8489fe4cb1ae22b3508483`.

**Correction to the design's own diagnostic.** The design listed `effective groups` at the *group*
level; that metric is wrong for this treatment. Multiplying whole regions by a constant leaves the
172 group masses nearly uniform inside each region, so the group-level effective count stays near 126
of 172 and says nothing. The concentration this design exploits is at the **region** level, where the
realised top-1 share is 0.6322 and the effective number of regions is about 2.9 of 4. A later `kappa`
must be judged on the region-level share.

## Scores under the concentrated criterion (20 frozen seeds, 30001-30020)

| arm | mean `RMSE_mu`, concentrated target | mean under the frozen target |
|---|---:|---:|
| `local_hajek` | 1.014396 | 1.003491 |
| `inst_cal` | 1.014463 | 1.003481 |
| `debt_cal` | 1.014568 | 1.003476 |
| `raven_simoracle` | 1.014471 | 1.003478 |

## The gate

`n = 20`, `t = (2.093024, 0.860951)`, bar = 2 % of the control's concentrated error =
`0.020288`.

| contrast | mean `D` | sd `D` | `MDE80` | bootstrap 95 % | `MDE80 <= 2 % bar` |
|---|---:|---:|---:|---|---|
| `local_hajek - debt_cal` | -0.000172 | 0.000898 | 0.000593 | [-0.00056, +0.00021] | **True** |
| `local_hajek - inst_cal` | -0.000067 | 0.000473 | 0.000312 | [-0.00026, +0.00014] | **True** |
| `local_hajek - raven_simoracle` | -0.000075 | 0.000470 | 0.000310 | [-0.00027, +0.00013] | **True** |

**Verdict: `CONTINUE`.** The realised `MDE80` is 34 to 65 times smaller than the bar, so the
design can resolve effects far below the 2 % the decision rule needs. No `TE2_BLOCKED.md` is written.

## Two caveats that the next step must carry

1. **The sd is a lower bound.** These checkpoints were trained under the *uniform* target, so all four
   arms predict almost the same thing and their spread on the concentrated criterion is small by
   construction. In the real round the arms are trained *for* the concentrated target and can diverge
   much more, so the realised paired sd will be larger and the realised `MDE80` correspondingly
   larger. The gate therefore establishes that the *scoring path* is precise enough, not that the
   confirmatory round will be powered.
2. **No arm is separated here, and the control is nominally best.** Mean `D` is negative for every
   treatment, i.e. the P2 arms are very slightly *worse* than the no-P2 control under the concentrated
   criterion, and every interval contains zero. That is the expected reading for models trained
   against a different criterion, and it is precisely why the round's treatment has to be a training
   run rather than a re-scoring. It is not evidence about the design's question.

## Cost of the next step, for the decision

- step 3 (primary cell, `kappa = 5`, four arms, 20 seeds) 80 runs, about 55 minutes;
- step 4 (ladder `kappa in {1,2,10}` plus the single-region limit) 320 runs more;
- step 5 (priority-region sensitivity) 240 runs more;
- total 640 runs, about 7 hours on the same single-threaded path.

Because of caveat 1 the honest ordering is to run step 3 first and re-estimate the paired sd from
arms that were actually trained for the concentrated target, before committing to steps 4 and 5.

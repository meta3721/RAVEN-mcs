# Do the paper's models beat the training-mean predictor?

Assessment only. **No manuscript file was touched.** The question matters because the training-mean
predictor is the paper's no-information baseline: it uses only the training split, so it is the right
comparator for skill, whereas the test-fitted constant is an oracle over the same labels the arms are
scored on.

## The baseline, recomputed from the data and checked against the manuscript

| block | training-split target mean | training-mean predictor `RMSE_mu` | manuscript prints | match | test-fitted constant | test target mean |
|---|---:|---:|---:|---|---:|---:|
| SensorScope | +0.3006 | **7.6471** | 7.647 | True | 2.0878 | +7.6572 |
| U-Air | -0.0000 | **1.0537** | 1.054 | True | 0.6781 | -0.8066 |
| NSW-Traffic | +0.0000 | **1.0067** | 1.007 | True | 1.0067 | +0.0027 |

The baseline is therefore exactly reproducible, and the level shift it exposes is the mechanism:
SensorScope's training target mean is `+0.3006` while its test target mean is `+7.6572`, a factor of
25. On U-Air the shift is `-0.0000` to `-0.8066`. On NSW-Traffic the two coincide, which is why the
training-mean predictor and the test-fitted constant take the same value there.

## Verdict per block

### SensorScope (training-mean predictor 7.6471)

| model as printed | `RMSE_mu` | versus the training-mean predictor | beats it? |
|---|---:|---:|---|
| ObsUse-Window | 7.9293 | **+3.69 %** | no |
| TwoStage-Hájek | 7.9309 | **+3.71 %** | no |
| FedAU-Window | 7.9364 | **+3.78 %** | no |
| RAVEN-Design | 7.9380 | **+3.80 %** | no |
| RAVEN-NoDesign | 7.9384 | **+3.81 %** | no |
| FedAvg-Window | 7.9389 | **+3.82 %** | no |

**0 of 6 beat it.**

### U-Air (training-mean predictor 1.0537)

| model as printed | `RMSE_mu` | versus the training-mean predictor | beats it? |
|---|---:|---:|---|
| FedAvg-Window | 1.1119 | **+5.52 %** | no |
| ObsUse-Window | 1.1120 | **+5.53 %** | no |
| FedAU-Window | 1.1128 | **+5.61 %** | no |
| RAVEN-NoDesign | 1.1131 | **+5.64 %** | no |
| RAVEN-Design | 1.1954 | **+13.45 %** | no |
| TwoStage-Hájek | 1.2202 | **+15.80 %** | no |

**0 of 6 beat it.**

### NSW-Traffic (training-mean predictor 1.0067, the same value as the test-fitted constant)

| model | `RMSE_mu` | versus the training-mean predictor | beats it? |
|---|---:|---:|---|
| central_all (tree, 20 seeds) | 0.9538 | **-5.25 %** | yes |
| fedavg_window, Adam step (TE1, 15 confirm seeds) | 0.9671 | **-3.93 %** | yes |
| raven_simoracle, Adam step (TE1, 15 confirm seeds) | 0.9731 | **-3.34 %** | yes |
| central_delivered (tree, 20 seeds) | 0.9754 | **-3.11 %** | yes |
| local_hajek = inst_cal = debt_cal = raven_simoracle (tree, 20 seeds) | 1.0035 | **-0.32 %** | yes |

**5 of 5 beat it**, but the four P2 arms beat it by
only `0.32 %`, which is consistent with the concentration ladder's finding that this weight class has
about `0.02 %` to `0.1 %` of room on this block.

## What this means

1. **On both air-quality blocks, no model in the paper beats a constant computed from the training
   split.** All six printed U-Air rows and all six SensorScope rows are worse, by `3.7 %` to `15.8 %`.
2. **The reason is the level shift, not the aggregation rule.** When the target level moves by far more
   than the residual spread, a constant carries the level error alone while a fitted model carries the
   same level error plus estimation variance, so the model loses. The printed ratio between the two
   constants, `3.7x` on SensorScope and `1.6x` on U-Air, is exactly that spread difference.
3. **This is the sharpest form of the paper's own negative and it supports its thesis**, since it shows
   the deployment-level error is governed by the target's level rather than by the weights. The
   manuscript prints the baseline and says the absolute column is read against it, but it does not
   state the verdict, so a reader must do this arithmetic.
4. **NSW-Traffic is the exception and the model class does have skill there**, because its training and
   test levels coincide; that is also why the two baselines coincide at `1.0067`.

## Provenance of the numbers compared

- The SensorScope and U-Air rows are the manuscript's printed values. An earlier scan of
  `artifacts/e3_formal_runs_r1/runs/{sensorscope,uair}` reproduced the SensorScope row exactly
  (`fedavg_window` 20-seed mean `7.9389`) but not the U-Air row, and the difference is explained by an
  existing audit rather than by a conflict: `results_seed_path_audit_r1/C3_CELL_DIFF.md` records that
  three U-Air seeds (30007, 30016, 30018) do not aggregate in their last window, so run-time
  `RMSE_mu` came from the in-memory mirror while the paper's convention is the theta copy, and that
  audit updated the affected cells on 2026-09-29. The paper's U-Air FedAvg row is also the later
  `fedavg_window_current` (`1.1119 +/- 0.0603`, matching the print to the digit), not the frozen
  `fedavg_window` (`1.1923`) that the scanned tree still holds.
- The NSW-Traffic rows come from the frozen E3 tree (20 seeds) and from the Adam-replacement tree
  (15 confirm seeds); the four P2 arms are identical to four decimal places there.
- No number in this report was estimated or rounded from a model output; the baseline was recomputed
  and the arm values are read from the manuscript or from `final_metrics.json`.


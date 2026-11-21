# DYNAMIC_COV_FEATURE_AUDIT

Object to predict: current-window `π^{opp}_{k,s,r}` (EventTrace risk-set event-mark mass).
Not predicted: pooled static `π^{opp}_{k,s}`.

## Features used by TARGET_LAW_RULE_V1 / C_cov (Gate)

| feature | pre-window legal? | source | update stage |
|---|---|---|---|
| completed-window `π^{opp}_{k,s,t}` for `t<r` | yes | EventTrace risk-set marks after window `t` closes; stored in `F_{r-}` history | after window `t` completes, never current R |
| rolling mean of last `L` completed masses | yes | deterministic function of lagged masses | `F_{r-}` |
| window max-residual `R_t` for `t<r` | yes | `π̂_t − π^{realized}_t` on completed windows | `F_{r-}` |
| conformal quantile `q_r` of `{R_t: t<r}` | yes | order statistic of lagged residuals | `F_{r-}` |
| frozen `π^{tar}` / `π_safe` | yes | TARGET_LAW_RULE_V1 + PI_SAFE_RULE_V1 | offline freeze |
| current R / current opportunity counts | **no** | — | forbidden as Gate input |
| current O / U / loss / Y | **no** | — | forbidden |
| dataset name | **no** | — | forbidden |

## Features not used (available, legal, unused)

Time-of-day / weekday of window `r` from public clock, mobility covariates, ridge/multinomial predictors. R1d uses the simplest rolling predictor only.

## Calibration unit

One residual per **window** (`R_t` = max over target-positive pairs). Events inside a window are not treated as iid calibration samples.

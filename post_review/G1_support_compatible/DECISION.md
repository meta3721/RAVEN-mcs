# Path A decision

**PATH_A_FAILS. TEST stays closed.**

## What the repair did

Support-compatible target
\(\pi^{\mathrm{sc}}=(\pi^{\mathrm{test,feas}}+\pi^{\mathrm{opp}})/2\)
sets U-Air \(\pi^{\mathrm{tar}}=0\) from 25.5% of risk units to **0%**. That was the G1 mechanism.

VAL 30001–30010 only (n=10 per dataset). Positive percent = SCL worse than the named reference.

## U-Air (the W1 problem)

| Metric | SCL | original Design | No-Design | SCL vs No-Design | SCL vs original |
|---|---:|---:|---:|---:|---:|
| \(\Delta_{\mathrm{group}}\) | 1.018 | 1.102 | 1.023 | **−0.53%** | −7.61% |
| RMSE\(_\mu\) | 1.102 | 1.180 | 1.098 | **+0.40%** | −6.58% |
| Tail RMSE | 1.106 | 1.188 | 1.102 | **+0.42%** | −6.92% |
| \(\Delta_{c\text{-}s}\) | 1.287 | 1.238 | 1.301 | **−1.14%** | +3.94% |

Intended non-inferiority vs No-Design (not worse by 0.5%): **all three primaries pass**. Structural direction on \(\Delta_{c\text{-}s}\) is kept. The old +7% reversal is gone on VAL.

## SensorScope (do-not-break)

| Metric | SCL vs original Design |
|---|---:|
| \(\Delta_{\mathrm{group}}\) | **+0.57%** |
| \(\Delta_{c\text{-}s}\) | +0.27% |
| RMSE\(_\mu\) | −0.00% |

The pre-registered SS rule fails: \(\Delta_{\mathrm{group}}\) is 0.07 points past the 0.5% bound. RMSE is flat. SCL is still better than No-Design on SS \(\Delta_{\mathrm{group}}\) (−0.83%).

## Why this is a fail, not a tune

The 1/2 barycenter was frozen. Tightening it after seeing SS \(\Delta_{\mathrm{group}}\) would be post-hoc. TEST is not opened.

A first script inequality (`pct >= -0.5` with this sign convention) treated the U-Air \(\Delta_{\mathrm{group}}\) *improvement* as a fail. That is a coding error. The intended gate is “not worse by 0.5%.” After that correction, the binding fail is SensorScope vs original Design, not U-Air vs No-Design.

## What is allowed next

Path A as a **universal** default is rejected.

Honest leftovers (pick one; new protocol before any TEST look):

1. **Path B**: keep original Design on SensorScope; default U-Air to `raven_wo_design`.
2. **Dataset-conditional SCL**: SCL on U-Air only, original Design on SensorScope. That is a new pre-registration, not a silent rescue of Path A.

Do not retune the mixture weight. Do not rewrite the paper yet.

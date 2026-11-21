# Path B decision

**PATH_B_ACCEPTED.**  
Paper default is `raven_gated`: SensorScope → `raven`, U-Air → `raven_wo_design`.

VAL 30001–30010 confirmed the pre-declared assignment. TEST 30011–30020 was opened once. No retuning.

## Default

| Dataset | Default | Why |
|---|---|---|
| SensorScope | Design on (`raven`) | Frozen support is compatible (\(\pi^{\mathrm{tar}}=0\) on 0% of units) |
| U-Air | Design off (`raven_wo_design`) | Frozen support is not (\(\pi^{\mathrm{tar}}=0\) on 25.5% of units) |

This is not a new estimator and not “robust Design.” Design stays in the method family; it is not a universal headline component.

## TEST (30011–30020, one look)

Positive percent = first method worse.

**U-Air default = No-Design**

| Metric | Gated | Full Design | Oracle-Design | Gated vs Design |
|---|---:|---:|---:|---:|
| \(\Delta_{\mathrm{group}}\) | 1.010 | 1.083 | 1.083 | **−6.73%** |
| RMSE\(_\mu\) | 1.128 | 1.202 | 1.203 | **−6.10%** |
| Tail RMSE | 1.133 | 1.211 | 1.212 | **−6.39%** |
| \(\Delta_{c\text{-}s}\) | 1.288 | 1.229 | 1.230 | **+4.88%** |

Gated U-Air gives back the \(\Delta_{c\text{-}s}\) Design had bought by hurting the three primaries. That trade is now explicit.

**SensorScope default = full Design**

| Metric | Design | No-Design | Design vs No-Design |
|---|---:|---:|---:|
| \(\Delta_{\mathrm{group}}\) | 1.024 | 1.035 | **−1.07%** |
| RMSE\(_\mu\) | 7.951 | 7.952 | −0.01% |
| \(\Delta_{c\text{-}s}\) | 1.277 | 1.284 | **−0.54%** |

TEST agrees with VAL: keep Design on SensorScope.

## Claim ceiling

Allowed:

- RAVEN-MCS is a windowed async method whose Design ratio is used when the public target is support-compatible.
- On SensorScope, Design is part of the default and helps \(\Delta_{\mathrm{group}}\) / \(\Delta_{c\text{-}s}\) without RMSE cost.
- On U-Air, the default drops Design because the test target zeros train-only strata and changes \(A_r\). Full Design still improves \(\Delta_{c\text{-}s}\) and still worsens the primaries, including under oracle \(p,q\).

Forbidden:

- “Design is necessary / universally stable.”
- Hiding the U-Air full-Design reversal.
- Selling Path B as a new robustness module.
- Rewriting the paper in this step.
- Starting G2 until the writing claim is locked.

## Code / sealed artifacts

Sealed E3/E4 trees are unchanged. `raven` still means full Design. The paper default is the dataset gate above, recorded here, not a silent change to the sealed runner.

# G1 diagnosis report (W1 + W4)

Date: 2026-08-23  
Scope: SensorScope + U-Air, seeds 30001–30020, Complete-aligned EventTraces.  
No new training. Sealed E3/E4 numbers are read-only.

## What was measured

1. Three-layer propensity panel from EventTraces + frozen \(\pi^{\mathrm{tar}}/\pi^{\mathrm{opp}}\) + lagged \(\hat p,\hat q\) replay (same lag as `WindowRunner`).
2. Six diagnostic figures under `figures/`.
3. Sealed method contrast already in the formal trees:
   - Estimated-Design = `raven` (E3)
   - Oracle-Design = `raven_simoracle` (E3; generator \(p,q\))
   - No-Design = `raven_wo_design` (E4)

Atomic `p_obs_true_by_unit` is present on **100%** of risk units. Oracle is not invented.

## Step 3 contrast (the gate)

U-Air, 20/20 seeds, relative to No-Design (positive = worse):

| Metric | Estimated | Oracle | vs No-Design (est / ora) |
|---|---:|---:|---|
| \(\Delta_{\mathrm{group}}\) | 1.092 | 1.092 | **+7.50% / +7.48%** |
| RMSE\(_\mu\) | 1.191 | 1.191 | **+7.07% / +7.11%** |
| Tail RMSE | 1.200 | 1.200 | **+7.45% / +7.49%** |
| \(\Delta_{c\text{-}s}\) | 1.233 | 1.234 | **−4.75% / −4.69%** (better) |

Oracle vs Estimated on U-Air primaries is noise: \(\Delta_{\mathrm{group}}\) −0.02%, RMSE +0.03%.  
Oracle is worse than No-Design on the three primaries in **20/20** seeds.

SensorScope: Design (estimated or oracle) is slightly better on \(\Delta_{\mathrm{group}}\) (−1.23% / −1.03%) and RMSE-flat. No U-Air-style reversal.

## Three-layer panel

### Opportunity / Design

Production Design already uses the **frozen generator joint** \(\pi^{\mathrm{opp}}\), not the online EMA. Opportunity is not an estimated-propensity problem.

| | SensorScope | U-Air |
|---|---:|---:|
| TV(realized, frozen \(\pi^{\mathrm{opp}}\)) | 0.061 | 0.056 |
| TV(realized, \(\pi^{\mathrm{tar}}\)) | 0.289 | **0.424** |
| fraction of risk units with \(\pi^{\mathrm{tar}}=0\) | 0.000 | **0.255** |
| \(\zeta\) p50 / p95 / max | 0.80 / 2.78 / 3.71 | 1.04 / 4.52 / 4.52 |
| clip rate (Design / No-Design / Oracle-\(p\)) | 0.047 / 0 / 0 | 0.057 / ~0 / 0.054 |

\(\zeta\) never approaches \(a_{\max}=20\). Clipping is modest. The U-Air-specific signal is **zero target mass on 25.5% of risk units**.

### Observation

| | SensorScope | U-Air |
|---|---:|---:|
| \(\hat p\) Brier / ECE / AUC | 0.172 / 0.059 / 0.786 | 0.170 / 0.058 / 0.789 |
| \(p_{\mathrm{true}}\) Brier / ECE / AUC | 0.212 / 0.002 / 0.564 | 0.211 / 0.001 / 0.565 |
| \(\hat p < p_{\min}\) | 0 | 0.008% |

Generator \(p\) is essentially two atoms (0.1925, 0.35): well calibrated, weak discrimination. Plug-in \(\hat p\) discriminates better and is moderately miscalibrated. That gap does **not** move the U-Air endpoints: Oracle-\(p\) Design still reverses.

Mean \(|a_{\mathrm{Design}}-\,a_{\mathrm{oracle}\,p}|\) = 1.14 on U-Air, vs \(|a_{\mathrm{Design}}-\,a_{\mathrm{NoDesign}}|\) = 2.99. The Design switch dominates the \(p\)-estimation switch.

### Use

\(\hat q\) is **not** constant (std ≈ 0.14) but is poorly calibrated (ECE 0.11 on U-Air; reliability plateau). Oracle \(q\) is well calibrated. Because `raven_simoracle` already consumes true \(q\) and still reverses, Use misspecification is not the W1 driver.

## Support, not clip, is the U-Air mechanism

Replay \(A_r\) overlap (Design vs No-Design):

- U-Air: **51.6%** of windows keep the same active set (Phase A: 52.9%)
- SensorScope: **100%**

Seed-level correlations on U-Air (reversal vs diagnostics) are weak: clip −0.22, ESS +0.23, same-\(A_r\) −0.03, \(\hat p\) Brier ≈ 0. All 20 seeds reverse (range +3.6% to +12.8% on \(\Delta_{\mathrm{group}}\)). Between-seed clip/ESS does not sort the reversal.

## Misspecification (weight-level only)

Scaling \(\hat p\) by 0.8 / 1.2 changes Design weights (U-Air mean \(|\Delta a|\) 0.66 / 0.50). This is a sensitivity check, not a method. Omitted-covariate replay and val clipping / \(\lambda\) Pareto were **not** run.

## Honest gaps

- No new misspecified-2 training.
- No val clip grid and no \(\lambda_g:\lambda_\beta\) Pareto. Those are P2-hierarchy tools; the oracle contrast already says the reversal is not estimator error.
- Replay clip rates are a bit higher than the stored `clip_rate_stage1` in `final_metrics.json` (same order; stored value is a run-mean of a slightly different aggregation). Do not treat the two as bit-identical.

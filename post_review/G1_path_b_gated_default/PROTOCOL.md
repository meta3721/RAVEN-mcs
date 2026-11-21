# Path B protocol — dataset-gated default

Pre-registered as the G1 fallback after Path A failed as a universal default.
Date: 2026-08-24

## Rule (no free parameter, no test labels)

Paper default `raven_gated`:

| Dataset | Default method | Reason (G1, frozen tables) |
|---|---|---|
| SensorScope | `raven` (Design on) | \(\pi^{\mathrm{tar}}=0\) on 0% of risk units; \(A_r\) overlap 100% |
| U-Air | `raven_wo_design` (Design off) | \(\pi^{\mathrm{tar}}=0\) on 25.5% of risk units; \(A_r\) overlap 51.6% |

The switch uses the **dataset identity** and the already-computed support-incompatibility diagnostic. It does not use test RMSE, test \(\Delta\), or any new threshold search.

This is claim narrowing. No new estimator. No SCL. No G1-B `zeta_tilde`.

## Seeds

- VAL: 30001–30010 — confirmation only
- TEST: 30011–30020 — one look after VAL confirmation, no retuning

## VAL confirmation (must all hold)

1. U-Air: sealed `raven` is worse than `raven_wo_design` on the means of \(\Delta_{\mathrm{group}}\), RMSE\(_\mu\), Tail RMSE.
2. SensorScope: sealed `raven` is not worse than `raven_wo_design` on \(\Delta_{\mathrm{group}}\) (mean relative change \(\le +0.5\%\), positive = raven worse).
3. SensorScope: sealed `raven` \(\Delta_{c\text{-}s}\) mean \(\le\) `raven_wo_design`.

If any fail: stop, do not open TEST.

## TEST look (report only)

Report `raven_gated` vs sealed `raven`, `raven_wo_design`, and `raven_simoracle`.
Do not pick a different default from TEST numbers.

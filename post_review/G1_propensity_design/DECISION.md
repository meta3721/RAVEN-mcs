# G1 decision

**VERDICT_G1 = DESIGN_TARGET_OR_SUPPORT**

Handbook row used:

> Oracle/Estimated 都反转，且与 ESS/clipping 无关  
> → Design target 本身可能不适合该 dataset  
> → 重新审计 client-share \(\lambda^{\mathrm{tar}}_{k|s}\) 与 support-compatible target construction

## Why this row, not the others

| Candidate row | Why not |
|---|---|
| Propensity reliability / G1-B gating first | Oracle-Design ≈ Estimated-Design. Opportunity is already frozen generator \(\pi^{\mathrm{opp}}\). Reversal is 20/20 with true \(p,q\). |
| P2 \(\lambda_g:\lambda_\beta\) hierarchy first | Oracle still reverses on RMSE, not only \(\Delta_{\mathrm{group}}\). Phase A already showed Design changes \(A_r\). A \(\lambda\) grid cannot repair a support change. |
| Use is unused because \(q\) is constant | \(\hat q\) is not constant; it is miscalibrated. Irrelevant to W1 because Oracle-\(q\) still reverses. |

## What is true

1. W1 is real and **not** an estimated-propensity artifact (W4 does not explain W1).
2. U-Air Design trades \(\Delta_{c\text{-}s}\) (−4.8%) for worse \(\Delta_{\mathrm{group}}\) / RMSE / Tail (~+7%).
3. The U-Air-specific mechanism is **support-incompatible target mass**: 25.5% of risk units have \(\pi^{\mathrm{tar}}=0\); only 51.6% of windows keep the same \(A_r\). SensorScope has neither (0% zero-target, 100% same \(A_r\)) and Design does not reverse.
4. SensorScope is allowed to keep Design. Do not drop Design globally from the method.

## What is forbidden next

- Do not implement G1-B `zeta_tilde` as if plug-in \(\hat\zeta\) were the bug.
- Do not start a test-tuned clip grid or \(\lambda\) Pareto to “fix” U-Air RMSE.
- Do not rewrite the paper yet.
- Do not start G2/G3/G4.

## Allowed next (only one scientific fork)

Choose **one** pre-declared path, then stop and re-gate:

**A. Support-compatible target (preferred scientific repair)**  
Rebuild \(\pi^{\mathrm{tar}}\) so train-only strata cannot zero out a client that still has observations. Any new formula needs III–VI theory audit. Then re-run Estimated vs No-Design on val seeds only.

**B. Dataset-gated default (claim narrowing, no new mechanism)**  
Keep Design on SensorScope; default U-Air to `raven_wo_design` (or a pre-registered support gate that is exactly “skip Design when \(\pi^{\mathrm{tar}}=0\)”). This is a paper-claim change, not a new estimator. Val-only rule; one test look.

Path B is the honest fallback if A is not ready before submission. It is not hidden as “robust Design.”

G1 is closed as a diagnosis gate. G1-B is not authorized.

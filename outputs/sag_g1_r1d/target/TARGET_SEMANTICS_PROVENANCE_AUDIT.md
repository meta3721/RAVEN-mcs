# TARGET_SEMANTICS_PROVENANCE_AUDIT

Question: who is the RAVEN-MCS deployment population? Freeze one `ϖ^{tar}` only if the authority uniquely determines it. Do not choose a law because it restores U-Air OFF or changes RMSE.

Authority order: Spec v1.2 → PostAudit III–VI → R1d instruction. Manuscript figure-table seal is used only for the already-frozen `h(i)` / `μ_g` protocol.

## Candidate A — train-supported atomic target (R1c)

| field | value |
|---|---|
| source/provenance | R1c `build_frozen_atomic_target_law`: uniform on train+supported atoms; `μ` and `π` derived from that law |
| scientific meaning | deployment mass = training support |
| uses outcomes / labels | no |
| uses test-side public metadata | no (test units receive zero `ϖ`) |
| compatible with Sections III–VI? | **No as `I_dep`.** PostAudit places `ϖ` on `I_dep` and defines `R_μ` as deployment-target risk. Proposition 1 requires the arrival law not be substituted for the deployment law by convention. Making `ϖ` = train support **by construction** collapses that distinction. |
| previously used in manuscript? | TABLE I / Section III freeze **group masses** `μ` from train-split TOD occupancy, not the claim that `I_dep` is the training table |
| previously used in experiments? | SAG G1-R1c only |
| target = training support by construction? | **Yes** |

## Candidate B — public deployment / test-support target

| field | value |
|---|---|
| source/provenance | PostAudit: public, label-independent atomic law on `I_dep`. Spec Algorithm 1: construct public/train-side targets, evaluate on unseen test. Runtime evaluation: `_predict(split="test")` and `_mu_weights_for_test` (per-test-unit weight `μ_g / n_{test,g}`). E3 production used uniform-on-test for the old spatial×time `h(i)` (not reused as paper `h(i)`). |
| scientific meaning | deployment population = units the deployed predictor is judged on (evaluation/public support) |
| uses outcomes / labels | no |
| uses test-side public metadata? | **Yes** (`split`, `support_flag`, `spatial_id`, `absolute_time`, sealed `s(i)`). Public metadata ≠ test outcome. |
| compatible with Sections III–VI? | **Yes** for `I_dep`. Test labels remain forbidden. |
| previously used in manuscript? | Evaluation of `R_μ` is on the held-out population. Manuscript freezes **`μ_g` from train-split**, so Candidate B cannot be “uniform on test” (that would recompute `μ` from test TOD occupancy). |
| previously used in experiments? | E3 test-uniform for old groups; evaluation weights already use train-frozen `μ_g` on test units |
| target = training support by construction? | **No** |

Within Candidate B, two atomic constructions are conceivable:

1. Uniform on test-supported atoms → `μ_g` = test TOD occupancy. Conflicts with TABLE I / Section III (`μ` = train-split mass).
2. `μ_g` frozen from train TOD occupancy, then `ϖ_i = μ_{h(i)} / n_{I_dep,h(i)}` on test-supported atoms. Matches manuscript `μ`, PostAudit `I_dep`, and `_mu_weights_for_test`.

(2) is the unique atomic law on Candidate B given the frozen `μ_g`.

## Candidate C — external / publicly specified deployment target

No external census, service-level agreement, or operator-supplied SS/U-Air deployment measure exists in the repository or sealed artifacts. **Not available.**

## Freeze decision

Evidence uniquely supports Candidate B construction (2), recorded as `TARGET_LAW_RULE_V1`.

Not used: Gate ON/OFF, RMSE, `Δ_group`, or any outcome.

Forbidden: test Y, test residuals, test predictions, current-window R/O/U.

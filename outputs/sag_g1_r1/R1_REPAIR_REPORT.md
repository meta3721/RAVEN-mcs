# 1. Executive Verdict

STRUCTURAL_CERTIFICATE_TOO_CONSERVATIVE

R1 is a 1-seed certificate diagnostic (SensorScope 30001, U-Air 30001). Frozen `tau_*` were not changed. This is not a 5-seed result and 5-seed was not started.

Old G1 Δ/service logs are **void** (BUG_CONFIRMED on the previous logger). New metrics recompute from raw states. `C_cov` is no longer current-window R coverage, but the repaired LCB is still 0 after cold start. Independently, `B_tot` median ≈ 17.6 > `tau_safe=4`.

---

# 2. Counterfactual Metric Audit

**Why old G1 had Δβ == ΔM == service_diff**

That was a logger bug, not a data coincidence:

- `service_diff` was assigned `float(delta_m)`.
- `ΔM` was `0.5‖mix^D − mix^0‖_1` (the service mix), not `‖M^D − M^0‖_2`.
- `Δβ` used the same `0.5‖·‖_1` helper, so the three numbers could collapse.

**R1 definitions (PostAudit / Spec)**

- `Δβ = ‖β^D − β^0‖_2`
- `ΔM = ‖M^D − M^0‖_2` (operator 2-norm)
- `ΔV = ‖V^D − V^0‖_2` with `v_k = S²_{k,r-} / max(n_eff,1) + v_floor`
- `service_diff_l1 = ‖M^D α^D − M^0 α^0‖_1` (α from the same P2 as the trainer)

Raw-state recompute matches the new logs on every dumped common-nonempty window (`audit/COUNTERFACTUAL_METRIC_RECOMPUTE.csv`: True).

**Why new ΔM is exactly 0**

Raw `M^D` and `M^0` are identical one-hot composition columns (same O, same target-group ids). Design vs No-Design changes `ζ` and therefore `β`/`α`/`m`, not the column support of `M`. Window 0 SensorScope: `Δβ=0.295`, `ΔM=0`, `service_diff_l1=0.288`. So service is **not** a copy of ΔM anymore.

**Why new ΔV is ~0**

`n_eff^D = n_eff^0` on the dumped windows (same O mask). Then `V` is the same diagonal. Residual `1e-16` is floating point, not a distinct variance perturbation. This is a data fact given shared O, not a leftover alias.

Synthetic Cases A–D PASS (`tests/unit/test_counterfactual_metrics_independent.py`).

---

# 3. C_cov Repair

**Formula**

`C_cov_LCB(r) = ∑_{k,s} π^tar(k,s) 1{lower_π_opp(k,s,r) ≥ π_safe}`

**lower_π_opp**

Empirical-Bernstein one-sided LCB on completed-window opportunity *masses* (uniform over pairs present in that finished window). Current R is not used. Same history ⇒ deterministic.

**π_safe**

Not in Spec / PostAudit / `thresholds.json`. Provisional = 10th percentile of public `π_opp_joint` on `{π^tar>0}`.

- SensorScope: 6.33e-4 (q05=q10; q25=7.73e-4); 440 target-positive pairs
- U-Air: 1.39e-3 (q05=q10=q25); 216 pairs
- Status: **PI_SAFE_REQUIRES_FREEZE_DECISION** (not a frozen tau)

**Old vs new**

Old realized-R coverage is stuck at 0.018 (SS) / ~0.02 (U-Air). New `C_cov_LCB` is 0 after lookback (not equal to that fraction). Tests: `test_c_cov_semantics.py`, `test_c_cov_target_mass.py`.

The LCB is still too tight to certify target mass: 440 pairs, each window only a handful appear, so almost every pair LCB is 0.

---

# 4. B_tot Decomposition

`B_M_pre = √K` with `K` = unique clients in the sealed EventTrace (8 on both datasets). Rule: `sqrt_K_prewindow_client_roster`. No assertable client–group support mask was found, so no tighter deterministic `B_M` was installed. `B_M_cf = max(‖M^D‖_2, ‖M^0‖_2) = 1` (one-hot columns) is **diagnostic only**.

`B_Q = ‖Q_{r-}‖_2`. `B_srv = √|G|(ΔM_UCB + B_M_pre D_α_UCB)`.

## SensorScope

| piece | median | p95 |
|---|---:|---:|
| B_M_pre | 2.828 | 2.828 |
| B_M_cf (oracle) | 1 | 1 |
| Δβ_UCB | 0.415 | 0.661 |
| ΔM_UCB | 0 | 0 |
| ΔV_UCB | ~0 | ~0 |
| D_α_UCB | 0.415 | 0.661 |
| B_srv | 17.39 | 27.75 |
| 2 δ_A | 0.063 | 0.34 |
| 2 δ_cal | 0.10 | 0.10 |
| B_tot | **17.55** | 27.91 |

## U-Air

| piece | median | p95 |
|---|---:|---:|
| B_M_pre | 2.828 | 2.828 |
| B_M_cf (oracle) | 1 | 1 |
| Δβ_UCB | 0.474 | 0.577 |
| 2 δ_A | 1.48 | 2.00 |
| B_tot | **17.66** | 21.68 |

**Bottleneck.** ΔM=0, so `B_srv ≈ √|G_runtime| · B_M_pre · Δβ_UCB`. The live `M` is one-hot over the *fine* target-group map (`|G|≈220`, `√|G|≈14.8`), not the paper’s 4 deployment groups. That is why `B_tot` sits near 18, not near 2. Replacing `|G|` by 4 without coarsening `M` would be an illegal bound. `ratio_BM = B_M_pre / B_M_cf ≈ 2.8` is real slack but not the dominant factor.

---

# 5. Certificate Coverage

Formal target **0.95**. Domain: `A^D = A^0 ≠ ∅` only. Width = UCB − actual.

| dataset | n_common | joint | β | M | V | mean width β | β UCB/actual | β exact-zero |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SensorScope | 97 | 0.938 | 0.948 | 1.00 | 0.990 | 0.288 | 3.42 | 0.155 |
| U-Air | 31 | 0.967 | 0.967 | 1.00 | 1.00 | 0.350 | 4.18 | 0.355 |

1-seed sample is small (especially U-Air n=31). Joint SS 0.938 is under 0.95; U-Air 0.967 meets it. Widths are now finite (old G1 `mean_width_*` was NaN). M/V actuals are exactly 0, so UCB/actual is undefined there.

---

# 6. One-Seed Gate Diagnostic

Frozen: `τ_cov=0.05`, `τ_ret=0.05`, `τ_ESS=1`, `τ_clip=0.95`, `τ_A=0.35`, `τ_safe=4`, `δ_cal=0.05`.

## SensorScope 30001 (100 windows)

| certificate | pass rate |
|---|---:|
| C_cov ≥ 0.05 | **0.00** |
| C_ret ≥ 0.05 | 1.00 |
| C_ESS ≥ 1 | 1.00 |
| C_clip ≤ 0.95 | 1.00 |
| δ_A ≤ 0.35 | 0.98 |
| B_tot ≤ 4 | **0.00** |

ON = **0 / 100**. Reasons: 8 `OFF_COLD_START`, 92 `OFF_LOW_COVERAGE` (first fail; B_tot would fail next).

## U-Air 30001 (80 windows)

| certificate | pass rate |
|---|---:|
| C_cov ≥ 0.05 | **0.00** |
| C_ret ≥ 0.05 | 1.00 |
| C_ESS ≥ 1 | 0.96 |
| C_clip ≤ 0.95 | 1.00 |
| δ_A ≤ 0.35 | **0.00** |
| B_tot ≤ 4 | **0.00** |

ON = **0 / 80**. Reasons: 8 cold start, 72 `OFF_LOW_COVERAGE`. `δ_A` still blocks the unsafe regime if coverage were ever to pass.

SAG ≡ No-Design on RMSE / WorstGroup / Δ (ON rate 0). Always-D still hurts U-Air prediction and helps SensorScope structure, as in G1.

---

# 7. Scientific Interpretation

SensorScope compatible regime: **no legal ON window** after a correct `C_cov` formula, independent Δ metrics, and a legal `√K` `B_M_pre`.

U-Air support-unsafe regime: `δ_A_UCB` pass rate is 0, so the active-set certificate still separates the unsafe dataset.

The two hard certificates that never pass on SensorScope are (1) pair-mass EB `C_cov_LCB` and (2) `B_tot` inflated by fine `|G|` and `√K·Δβ`. Neither was “fixed” by retuning τ (τ were not touched).

---

# 8. Next Decision

**Do not start 5-seed G1-R2.**

Unique structural blocker for a legal ON on SensorScope, even if `C_cov` were later made to pass: **`B_tot` under the live fine-group `M` is ~4× `τ_safe` and cannot be tightened without a legal coarsening of `M` to the paper’s deployment groups, or a new predictable bound authorized at the theory layer.**

Secondary recorded first-fail: `C_cov_LCB=0` because per-pair EB LCBs on rare opportunity masses do not certify `π^tar` mass.

`π_safe` still requires an explicit freeze decision. Do not lower `τ_cov` / `τ_safe` to manufacture ON.

Files: `outputs/sag_g1_r1/` (`R1_VERDICT.json`, `audit/`, `coverage/`, `safety_bound/`, `diagnostic/`, `configs/`, `tests/test_summary.json`).

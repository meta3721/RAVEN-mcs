# Executable instruction: W1 round v5.1 — close R4 with an exact oracle, unblock R3, finish R1 wording

```text
Mode: design + one execution prompt. This file starts no run. No training in this round.
Contract: CCFA-Skills/ccf-experiment-designer. Protocol, not publication prose.
Input: results_w1_ladder/round_v5/ (EXECUTION_REPORT.md, GATES_V5.csv, A1_*, WORSTGROUP_V5.csv, R1A_*),
       round_v4/ Part B runs, artifacts/e3_formal_runs_r1/runs/, RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv,
       results_seed_path_audit_r1/ (record items 46-47).
Output: results_w1_ladder/round_v5_1/ only. round_v5/ is frozen from now on (read-only).
Forbidden: editing src/, main.tex/appendix.tex/supplemental.tex, round_v1..v5, tdrive_protocol_seal_r1/, artifacts/;
           training; resuming X1; PATH_A NO2; full build(); git commit/push.
Every rule below that differs from round_v5/PREREG.md is an AMENDMENT and must be listed in AMENDMENTS.md
with its reason, written and hashed (MANIFEST.sha256) before any v5.1 number is computed.
```

## 0 Diagnosis of round v5

### 0.1 What v5 settled

- **The trained runs are internally exact.** Self-replay reproduces both structural endpoints to ≤ 5.8e-15 on 120/120 runs. α is bit-exact on 118/120 runs; the other 2 differ by 6.45e-9 and 1 ULP, and their endpoints still agree to ≤ 4.4e-15.
- **M_r, μ, β̂ and the active set do not depend on the server rule.** This is the v5 result combined with the v4/v5 checks: the masses are bit-identical across arms, β̂ is bit-identical to frozen `raven`, and B-G1 passes 120/120.
  - Consequence: **any server rule's structural endpoints can be computed exactly by replay, without training.** Only the prediction endpoints need a trained model.
- **R1 is closed.** There is no benefit row, and the alignment-to-accuracy dose-response slope includes 0 on both datasets (the U-Air point estimate even has the opposite sign). The θ-based robustness repetition left every verdict unchanged.

### 0.2 Three of the v5 failures come from my v5 protocol, not from the method

1. **The G-self condition "α L∞ = 0" was too strict.** A convex solver reproduces α only up to its tolerance. Process-level caching of the parameterized CVXPY problem is enough to move α by 1e-9, while the endpoints still agree to 1e-15.
   - The stop was correct by the letter of the protocol, but the condition is not informative.
   - Amendment AM-1 below fixes it.
2. **The G-xref grid mixed problem definitions with solver noise.**
   - The β axis `raw` vs `β/Σβ` is not a perturbation. It projects a different point, so it gives a different problem with a different optimum.
   - For a strictly convex projection the optimum is unique, so "spread across solver paths" is the wrong ruler. The right ruler is the distance to the exact optimum.
   - The debt rule's near-LP conditioning (quadratic weight 1e-3) comes from how it was written. It equals the projection of β+κMᵀQ_r onto C_r, so it can be solved exactly too.
   - So "reference not numerically stable" is a property of the reference code, not of the rule. It **must not** go into the paper (the E-v5-1 draft text has to be rewritten).
3. **A2-G0 did not account for a known defect.** The 18 failing rows (U-Air × seeds 30007/30016/30018 × all 6 arms) are the documented mirror/θ trigger: when the final window does not aggregate, the run-time metric evaluates the in-memory module instead of the saved θ (record items 46–47). The paper already uses θ as the canonical source for these cells (17 frozen + 3 θ).
   - The v5 PREREG should have included that rule.
   - The re-scored values match Table II per seed to 1.9e-9, which confirms that θ is correct.
   - The 1e-10 tolerance on WorstGroupRMSE was also too tight: the summation path differs, giving 2.4e-9 (1.9e-9 relative).

### 0.3 One v5 reading needs a vocabulary fix (the decision is unchanged)

For U-Air `proj_beta − uniform_window` (+0.262 %, 90 % CI [+0.00118, +0.00504]), the CI lies inside the margin δ_P and **also excludes 0**. The v5 rule let "equivalent" and "harm (lower bound > 0)" overlap. The honest label is **"equivalent within 0.5 %, with a nonzero cost of +0.26 %"**.

U-Air `proj_beta − fedavg_window` (+0.357 %) leaves the margin, but Holm-adjusted TOST gives p = 0.26. It is a directional cost, not a multiplicity-robust harm claim.

Under either reading Part B stays closed, because adding seeds to overturn a cost reading is ruled out.

## 1 Amendments (write to AMENDMENTS.md first, then hash)

| id | replaces (round_v5/PREREG.md) | new rule | reason |
|---|---|---|---|
| AM-1 | G-self: α L∞ = 0 | α L∞ ≤ 1e-8 **and** \|Δ_group\|, \|Δ_c-s\| ≤ 1e-12 | solver tolerance; v5 measured 6.45e-9 with endpoints ≤ 4.4e-15 |
| AM-2 | G-xref via spread over a grid | **O-gate**: distance of each implementation to an exact oracle (§2) | strictly convex problems have a unique optimum; the raw/normalized β axis was a different problem |
| AM-3 | A2-G0 "any mismatch stops" | three-part G0 (§3) with a θ-canonical rule for pre-identified trigger runs | known defect documented before v5 (record items 46–47); the paper already uses θ |
| AM-4 | WorstGroupRMSE tolerance 1e-10 absolute | 1e-8 relative | different summation path; 1.9e-9 relative observed |
| AM-5 | TOST labels | 5 labels: `equivalent_zero` (CI ∋ 0, inside δ), `equivalent_cost` / `equivalent_gain` (inside δ, CI excludes 0), `harm` / `benefit` (outside δ, CI excludes 0), `inconclusive` | v5 labels overlapped |

Thresholds kept from v5 (not changed): δ_P = 0.5 %, δ_WG = +0.5 %, Holm families, bootstrap 10 000 seed 20261002, implementation budget 5e-6 (= 1e-3 × 0.005).

## 2 A1′ (R4) — exact oracle for both trained rules

### 2.1 Oracle

`scripts/w1_v51_oracle.py`, numpy only (no CVXPY):

- `P_C(v)`: Euclidean projection onto C_r = {Σx = 1, 0 ≤ x ≤ ā, ‖x‖² ≤ 1/ē}.
  - Inner step: capped-simplex projection x(τ) = clip(v − τ, 0, ā), with τ found by bisection to 1e-15 (or the exact breakpoint sort).
  - If ‖x‖² ≤ 1/ē, stop.
  - Otherwise solve the KKT system x(λ, τ) = clip((v − τ)/(1 + 2λ), 0, ā) for λ > 0 with ‖x‖² = 1/ē: bisection on λ outside, τ inside.
  - Edge cases: K = 1 gives x = 1; if the feasible set is the single point (ā = 1/K or ē = K), return the uniform weights.
- `proj_beta` oracle: α_r = P_C(β̂_r / Σβ̂_r).
- `proj_beta_debt` oracle (closed loop, exact): α_r = P_C(β̂_r/Σβ̂_r + κ M_rᵀ Q_r), Q_{r+1} = max(Q_r + 0.01(μ − M_r α_r), 0), Q_0 = 0, κ = 1000.
  - In the self-check below, verify algebraically that this equals the minimizer of −Q_rᵀM_rα + (1/(2κ))‖α − β‖² on C_r.
- Inputs per run: `active_clients` and `beta_hat` from the run's own `window_metrics.json`; M_r and μ from `W.build_case(ds, "R_on", "raven_wo_use", seed)` (verified equal in v5).

### 2.2 Oracle gates (must pass before anything is compared)

- **O-G0 (KKT).** Per window: primal feasibility ≤ 1e-13; the stationarity residual of the KKT conditions ≤ 1e-12; complementary slackness ≤ 1e-12. Report the maxima. One failing window stops A1′.
- **O-G1 (objective).** On 200 randomly drawn windows, take a CVXPY CLARABEL solve with fresh problem and tolerance 1e-12, project it back onto C_r, and evaluate the objective. The oracle objective must be ≤ that value + 1e-12. This checks only that the oracle is optimal. It is not a target.
- **O-G2 (uniform control).** Feeding β = uniform weights must return the uniform weights exactly when they are feasible.

### 2.3 Measurements

For each arm ∈ {`proj_beta`, `proj_beta_debt`}, each dataset, and each of 20 seeds:

| quantity | definition |
|---|---|
| `alpha_linf_trained` | max over windows of ‖α_trained − α_oracle‖∞ |
| `eps_impl_group`, `eps_impl_cs` | \|endpoint(trained α) − endpoint(oracle α)\| |
| `alpha_linf_ref`, `eps_ref_*` | the same, for the v3/v4 stored reference paths (`proj_seq`, `kappa_seq`) |
| `first_q_div` (debt only) | first window where Q_trained and Q_oracle differ by > 1e-12 |

Verdict per arm × dataset, preregistered before computation:
- **`certified`**: max over seeds of `eps_impl` ≤ 5e-6. The trained run is an implementation of the rule within budget.
- **`approximate`**: `eps_impl` > 5e-6. Report the oracle's structural endpoints as the rule's values. The trained run's RMSE_μ is then the RMSE of an approximate implementation, and its size `eps_impl` is reported next to it.

### 2.4 Re-check the v4 structural contrasts on oracle values

Recompute the Δ_group and Δ_c-s rows of `round_v4/TRADEOFF_PAIRED.csv` (same contrasts, same Holm families) with the oracle endpoints in place of the trained ones. Report side by side with v4: pp difference, CI, p_holm, and whether the verdict changes. A verdict change is reported as such and is not smoothed over.

Output: `A1P_ORACLE_GATES.json`, `A1P_IMPL.csv`, `A1P_STRUCT_PAIRED.csv`, and `GATES_V51.csv` with gates B-G1, G-self (AM-1), O-G0, O-gate, and the columns `observed, tolerance, tolerance_source, pass`.

## 3 A2′ (R3) — worst-group scores with the θ-canonical rule

### 3.1 Three-part G0 (AM-3, AM-4)

- **G0-a.** On all non-trigger rows, the checkpoint re-score equals `final_metrics.json` within ≤ 1e-12 on RMSE_μ, Head and Tail. Expected: 222/222 (SensorScope 120, U-Air 102).
- **G0-b.** The trigger set is fixed in advance as {U-Air} × {30007, 30016, 30018} × all 6 arms = 18 rows. For each of them:
  - confirm the trigger in the run's own `window_metrics.json`: the final window is inactive or has no α;
  - confirm that the θ re-score matches Table II per seed (frozen arms) within 1e-8 relative.
  - Any trigger outside the set, or any listed row that lacks the trigger, stops A2′.
- **G0-c.** The stored WorstGroupRMSE of the frozen arms is reproduced within 1e-8 relative.

**Canonical score:** θ re-score for every row. It equals `final_metrics` on non-trigger rows, and it is the paper's own rule on trigger rows.

### 3.2 Analysis

Run exactly as in v5 §A2 (unchanged): the same contrast list, bootstrap, Wilcoxon and Holm per dataset × WorstGroupRMSE. Add the non-inferiority test with δ_WG = +0.5 % against `fedavg_window` and frozen `raven`, using the 5 labels of AM-5. Also report `argmax_group`; v5 raw data says R2 in 240/240, and that needs confirming.

Output: `WORSTGROUP_V51.csv`, `WORSTGROUP_PAIRED.csv`, `WORSTGROUP_NI.csv`, and `TRADEOFF_V51.csv`. The latter is v4 columns with RMSE_μ/Head/Tail in θ-canonical form and WorstGroupRMSE filled in, plus a `source ∈ {final_metrics, theta_trigger}` column.

## 4 A3′ (R1) — final wording, no new decision

1. Re-run the v5 TOST, MDE and dose-response on `TRADEOFF_V51.csv` (θ-canonical) with the AM-5 labels. Print the v5 preregistered table and the v5.1 table side by side. **The v5 decision (R1 closed) is not re-opened.**
2. Add the secondary endpoint: WorstGroupRMSE TOST from A2′.
3. Re-sourcing check for the paper: recompute the U-Air RMSE_μ rows of `round_v4/TRADEOFF_PAIRED.csv` (mean difference, CI, p_holm) on θ-canonical values and list every number that differs from v4 at the 4th significant digit. These are manuscript cells (§VII Part B, the U-Air RMSE values 1.19248 / 1.19037 / 1.19112 …).

## 5 Report and errata

`round_v5_1/EXECUTION_REPORT.md`: amendments table, A1′ oracle gates and verdicts, the A1′ structural re-check, A2′ G0 and tables, A3′ side-by-side tables.

`round_v5_1/ERRATA_FOR_PAPER.md` **supersedes** the round_v5 version:
- **E-v51-1** (replaces E-v5-1). Mechanism sentence:
  - the trained rules reproduce their replay exactly;
  - the earlier residual came from the reference solver, not from drifting inputs;
  - the rule values are certified against an exact projection oracle, or reported as approximate, with `eps_impl`.
  - **Delete the phrase "reference not numerically stable".**
- **E-v51-2.** Worst-group readings and non-inferiority verdicts for the trained rules (from A2′).
- **E-v51-3.** Prediction statement in AM-5 vocabulary:
  - SensorScope: four `equivalent_zero` rows expected; print whatever the data shows.
  - U-Air: `proj_beta − uniform_window` = equivalent with a nonzero cost of +0.26 %; `proj_beta − fedavg_window` = directional cost of +0.36 %, not Holm-robust.
  - No alignment-to-accuracy slope on either dataset.
  - Never "better".
- **E-v51-4.** The list of θ-re-sourced U-Air Part B cells from A3′ item 3.

## 6 Execution order and cost

AMENDMENTS.md + hash → A1′ (seconds to minutes, numpy) → A2′ (re-score already done in v5; only G0 re-classification and analysis, minutes) → A3′ (seconds) → report.

No training. Part B (R1b) stays closed regardless of the A3′ numbers.

## 7 Result templates (placeholders only)

`A1P_IMPL.csv`: `ds, arm, seed, alpha_linf_trained, eps_impl_group, eps_impl_cs, alpha_linf_ref, eps_ref_group, eps_ref_cs, first_q_div, verdict`

`A1P_STRUCT_PAIRED.csv`: `ds, endpoint, contrast, pp_v4, pp_oracle, ci_lo_oracle, ci_hi_oracle, p_holm_v4, p_holm_oracle, verdict_changed`

`WORSTGROUP_NI.csv`: `ds, arm, comparator, mean_rel_diff, ci90_lo, ci90_hi, margin, label_AM5, p_holm`

No-fabrication status: every cell is TBD. The numbers in §0 are the round_v5 measurements and the record items they cite.

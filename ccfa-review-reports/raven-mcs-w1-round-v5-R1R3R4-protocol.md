# Executable instruction: W1 round v5 — audit items R1 / R3 / R4 (revised)

```text
Mode: design + one execution prompt. This file starts no run.
Contract: CCFA-Skills/ccf-experiment-designer. Protocol, not publication prose.
Source of R1/R3/R4: ccfa-review-reports/raven-mcs-experiment-design-audit.md §6.
Input: results_w1_ladder/round_v4/ (Part B runs, TRAIN_GATES.csv, TRADEOFF*.csv), artifacts/e3_formal_runs_r1/runs/.
Output: results_w1_ladder/round_v5/ only. Do not edit src/, the manuscript, round_v1..v4, or tdrive_protocol_seal_r1/.
Part A is read-only (no training). Part B trains, and only runs if Part A's decision rule says so AND the user writes "授权 v5 Part B".
Paper edits are paused. Items for the manuscript go to round_v5/ERRATA_FOR_PAPER.md, not into main.tex.
```

## 0 Verdict on the three proposed items

| Item | As proposed | Verdict | Revised form |
|---|---|---|---|
| R1 | New prediction-endpoint experiment: raven / proj_beta / uniform / fedavg (+1 alignment-only arm), 2 ds × 20 seeds, Holm per ds × endpoint | **Not as stated.** Part B v4 is already that experiment (same arms, same 20 seeds, same Holm family). A rerun is a replication of a known null, and repeating until something passes is a forking-paths violation. | **R1a** read-only equivalence / power / dose-response on the existing 20 seeds; **R1b** (new data, gated) only if R1a shows the test is underpowered for a pre-declared effect size, and then with a single pre-declared primary contrast. |
| R3 | Fill the empty `WorstGroupRMSE` column | **Appropriate, and cheap.** Every Part B run kept `checkpoints/final.pt`; no retraining is needed. | Re-score checkpoints on the test split with the same code path as the E3 supplement (`_predict` + `_wrmse_block`), behind a reproduction gate. Add a formal non-inferiority reading. |
| R4 | Freeze `M_r` so B-G2/B-G3 pass at 1e-9 | **Wrong diagnosis, wrong fix.** `M_r` does not drift (verified below). Freezing it changes nothing and would turn a closed-loop gate into an open-loop one. | Split the gate into a **self-replay** identity (must be exact) and a **cross-implementation** check whose tolerance comes from measured solver sensitivity. Fix the reference side, not the method. Also serialize the verdicts (audit R8). |

### 0.1 Facts already verified (2026-10-03, read-only, seeds 30001/30002, both datasets)

1. Per-window mass inputs in `proj_beta` and `proj_beta_debt` runs vs. the frozen `raven` run (same seed, join on window × client × atomic unit, 441/441 rows): `w_atomic`, `target_client_stratum_mass`, `normalization_denominator` and `eta_r` all differ by **0.0**. Only `alpha_client` differs, which is expected.
2. The observation propensity is updated only from trace features and `rec.O` (`window_runner._update_lagged_estimators`, L1310-1322). It does not read the model, so "`p_hat` is model-dependent" (PART_B_REPORT §1) is unsupported.
3. Trained `proj_beta` α vs. a fresh `proj_Cr(β̂/Σβ̂)` computed from the run's own logged `beta_hat`: **max |Δα| = 0** on all windows.
4. Plugging the trained α into the replay case (`W.build_case(ds,"R_on","raven_wo_use",seed)`) reproduces the run's own `Delta_group` to **≤ 6.7e-16**. So the replay `M_r` equals the run's `M_r`.
5. The replay's own α (`proj_seq(case, betas)` with un-normalized β̂ and the cached parameterized problem) differs from the trained α by **1.9e-7 to 6.4e-6** in L∞.
6. The B-G2 reference column is read from `round_v3/SOURCE_LADDER.csv` (an older replay); B-G3 from `DEBT_STRENGTH_V4.csv` (default CLARABEL tolerance, κ = 1000 ⇒ quadratic weight 1e-3, near-LP conditioning). Per-seed residuals: `proj_beta` 4e-9 to 2e-8, `proj_beta_debt` 2e-7 to 2.6e-5.

Conclusion: **the trained runs are internally exact; the residual is on the reference side** (solver tolerance, β normalization, problem caching, and debt-path conditioning amplified through `Q`). The manuscript's current sentence "the residual tracks composition and mass inputs that vary weakly with the model trajectory" is false and goes into ERRATA (E-v5-1).

### 0.2 What "Holm made it worse" actually means

Holm did not change any data. On SensorScope no prediction contrast was significant even before adjustment (raw Wilcoxon p ≈ 0.43–0.67 on the rows checked; Holm = 1.000 on all). On U-Air the best raw p was 0.027, and Holm over the family removes it (0.133). The one U-Air signal points to **harm**: `proj_beta − uniform_window` RMSE_μ = +0.00312 (+0.26 %), raw p = 0.027. R1a must test that direction explicitly instead of looking for a gain.

## 1 Claim → evidence matrix (this round only)

| Claim to be tested | Endpoint | Evidence | Part |
|---|---|---|---|
| C-R4: trained server-weight rules are exactly the rules evaluated in replay | α per window, Δ_group, Δ_c-s | self-replay identity + solver-sensitivity band | A1 |
| C-R3: trained rules do not worsen the worst region | WorstGroupRMSE, per-region RMSE R0–R3 | checkpoint re-scoring, paired CI, Holm, NI test | A2 |
| C-R1: structural alignment does / does not convert to prediction at the measured scale | RMSE_μ (primary), WorstGroupRMSE, Head/Tail | TOST equivalence, MDE, seed-level dose-response | A3 (+B1 if gated) |

## 2 Part A — read-only

### A0 PREREG (write before computing anything)

`round_v5/PREREG.md` with sha256 recorded in `MANIFEST.sha256`. It must contain, verbatim, the margins and families in A2/A3 below. No margin, family or contrast may change after A0 is hashed.

### A1 (R4 + R8) Gate re-specification

Arms: `proj_beta`, `proj_beta_debt` (κ = 1000), `uniform_window` as control. 2 ds × 20 seeds.

**A1-G-self (must be exact).** Rebuild α per window from the run's own logged inputs (`window_metrics.json`: `active_clients`, `beta_hat`; `M_r` from `W.build_case`, verified equal in §0.1-4) using **the same aggregator class from `scripts/w1_v4_train.py`** (import it; fresh instance per run so `Q` starts at 0). Pass: α L∞ = 0 and |Δ_group − final_metrics|, |Δ_c-s − final_metrics| ≤ 1e-12 on 40/40 runs per arm. Any failure: stop A1 and report the first diverging window.

**A1-sens (solver sensitivity).** For each run, recompute α with the replay path (`proj_seq`, `kappa_seq`) under a grid:
- CLARABEL tolerance ∈ {default, 1e-10, 1e-12};
- β input ∈ {raw, β/Σβ};
- problem object ∈ {cached parameterized, fresh per window}.

Record per cell: α L∞ vs. trained, |ΔΔ_group|, |ΔΔ_c-s|, first diverging window, and for the debt arm the window where `Q` first differs by > 1e-12.

**A1-G-xref (cross-implementation).** Tolerance τ_x := 10 × the largest endpoint spread across the A1-sens grid **for that arm and dataset**, declared in PREREG as this formula, not as a number. Pass if trained-vs-reference endpoint residual ≤ τ_x on all seeds **and** τ_x ≤ 1e-3 × the smallest claimed effect for that arm (0.005 in Δ_group units ⇒ τ_x ≤ 5e-6). If the second condition fails, the arm stays "exploratory: reference not numerically stable" and that is the reported result. Do not tighten or loosen afterwards.

**A1-R8.** Write `GATES_V5.csv`, one row per (ds, arm, seed, gate) with gate ∈ {B-G1, G-self, G-xref}, columns `observed`, `tolerance`, `tolerance_source`, `pass`. Do not modify `round_v4/TRAIN_GATES.csv`; state in the report that its `pass` column reflects B-G1 only.

Forbidden: freezing or overwriting `M_r`, changing the trained aggregators, re-running training to "make the gate pass".

### A2 (R3) Worst-group re-scoring from checkpoints

Runs: the 120 Part B runs + frozen `fedavg_window`, `inst_cal`, `raven` (20 seeds each, both datasets).

**A2-G0 (reproduction gate).** Load each `checkpoints/final.pt` into a runner built by the same factory as the run (`build_full_runner` with the run's `config_snapshot.json`), predict on the test split, and recompute `RMSE_mu`, `Head_RMSE`, `Tail_RMSE`. Pass: ≤ 1e-10 vs. `final_metrics.json` on every run. For frozen arms also reproduce their stored `WorstGroupRMSE` ≤ 1e-10. One failure ⇒ stop A2 and report; do not fall back to retraining without asking.

**A2-score.** `WorstGroupRMSE = max_g wRMSE_g` with the μ-weights and `_wrmse_block` of `scripts/run_nodesign_supplement.py` (L234-239). Also store `WG_R0..R3` and `argmax_group`.

**A2-analysis** (per dataset; no pooling):
- Paired contrasts: the same list as `round_v4/TRADEOFF_PAIRED.csv` (endpoint = WorstGroupRMSE).
- Bootstrap 10 000, seed 20261002; Wilcoxon; Holm family = one dataset × WorstGroupRMSE.
- **Non-inferiority (pre-declared):** for each trained arm vs. `fedavg_window` and vs. frozen `raven`, margin δ_WG = +0.5 % of the comparator's mean WorstGroupRMSE (the paper's existing descriptive line, now as a formal margin). One-sided 95 % bootstrap upper bound of the relative difference < δ_WG ⇒ "non-inferior"; > δ_WG with lower bound > 0 ⇒ "inferior"; otherwise "inconclusive". Holm over the NI family of that dataset.
- Report which group is worst and whether `argmax_group` changes between arms.

If a frozen arm has no `final.pt`, use its stored `WorstGroupRMSE` and mark the row `source=frozen_record`; A2-G0 then applies only to the arms that do.

Output: `WORSTGROUP_V5.csv` (per run), `WORSTGROUP_PAIRED.csv`, `WORSTGROUP_NI.csv`, and a filled `TRADEOFF_V5.csv` (copy of v4 columns + WG filled; v4 file untouched).

### A3 (R1a) What the existing 20 seeds can and cannot say about prediction

Uses only `round_v4/TRADEOFF.csv` and frozen arms. Endpoint RMSE_μ primary, WorstGroupRMSE (from A2) secondary.

1. **Equivalence (TOST).** Margin δ_P = 0.5 % of the comparator's mean RMSE_μ per dataset (declared in A0). Contrasts: `proj_beta − uniform_window`, `proj_beta − fedavg_window`, `raven − proj_beta`, `proj_beta_debt − proj_beta`. Outcome per row ∈ {equivalent, harm (lower bound > 0), benefit (upper bound < 0), inconclusive}. Holm within dataset × TOST family.
2. **MDE.** From the observed paired SD, the minimum detectable effect at α = 0.05 (two-sided, Holm-adjusted for the family size actually used), power 0.8, n = 20; and the n needed to detect 0.25 % and 0.5 % RMSE_μ.
3. **Seed-level dose-response (pre-declared, one test per dataset).** Across the 20 seeds and the four contrasts above, regress the paired RMSE_μ difference on the paired Δ_group difference (seed as random intercept, or a simple pooled-within-seed slope with seed-cluster bootstrap). H0: slope = 0. This tests "more alignment ⇒ lower error" without new runs. Report slope, 95 % CI, and the RMSE change implied by the largest observed Δ_group gain.

**A3 decision rule (written in A0, applied mechanically):**
- If every primary row is "equivalent" or the dose-response CI excludes the effect needed for a 0.25 % RMSE_μ gain at the observed Δ_group range ⇒ **R1 is closed as a measured null. Part B is not run.** The paper reports equivalence within δ_P (later, when edits resume).
- If U-Air `proj_beta − uniform_window` is "harm" ⇒ report it as a harm finding; Part B is not run to overturn it.
- Only if rows are "inconclusive" **and** MDE > δ_P ⇒ Part B may be proposed to the user.

### A4 Report

`round_v5/EXECUTION_REPORT.md`: A1 gate table, A1-sens grid, A2 tables, A3 decision with the rule quoted, and `ERRATA_FOR_PAPER.md` containing at least:
- E-v5-1: replace the "M_r varies with model trajectory" explanation by the A1 finding.
- E-v5-2: trained-rule WorstGroupRMSE readings (from A2), with NI verdicts.
- E-v5-3: the prediction-endpoint statement in its A3 form (equivalent / inconclusive / harm), never "better".

## 3 Part B — gated (R1b)

Runs only if A3's rule allows it and the user writes "授权 v5 Part B".

- **One primary hypothesis per dataset**, chosen in A0 before Part A runs: H1 = `proj_beta − uniform_window` on RMSE_μ (the contrast that isolates the projection, which is the paper's carried claim). Every other contrast is secondary/exploratory and labelled so.
- **New seeds only**: n from A3-MDE for δ = 0.25 % (cap: 60 new seeds per dataset; if the required n exceeds the cap, do not run and report the n). Seeds 30101 onward, disjoint from 30001–30020.
- Arms: `uniform_window`, `proj_beta`, `fedavg_window`, frozen `raven`. No new "alignment-only" arm: `proj_beta` already is the alignment-only variant (same policy, server weights changed only).
- Gates: B-G0 exact replay (≤ 1e-12), B-G1 active set, A1-G-self exact, A2-G0. G-xref uses the τ_x formula from A1.
- One run per seed, analyzed once. No extension of n after looking. Report regardless of sign.

## 4 Forbidden in this round

- Editing `src/`, `main.tex`, `appendix.tex`, `supplemental.tex`, or any round_v1..v4 file.
- Freezing/overwriting `M_r`, or any change that makes the gate pass by changing the method.
- Changing Holm families, switching to one-sided tests, dropping contrasts, or changing δ after A0.
- Pooling datasets. Re-running Part B v4. Resuming X1. Ingesting PATH_A NO2. Running full `build()` of `build_public_repro_bundle.py`.
- Committing or pushing.

## 5 Execution priority and cost

1. A0 → A1 (minutes; CPU solves only).
2. A2 (≈ 240 checkpoint evaluations: 120 Part B + 120 frozen; no training).
3. A3 (seconds) → decision.
4. Part B only under the A3 rule + explicit authorization.

## 6 Result templates (placeholders only)

`GATES_V5.csv`: `ds, arm, seed, gate, observed, tolerance, tolerance_source, pass`

`WORSTGROUP_NI.csv`: `ds, arm, comparator, mean_rel_diff, ub95_one_sided, margin, verdict, p_holm`

`R1A_TOST.csv`: `ds, contrast, mean_diff, rel_diff, ci90_lo, ci90_hi, margin, verdict, p_tost_holm, mde_n20, n_for_0.25pct, n_for_0.5pct`

`R1A_DOSE.csv`: `ds, slope, ci_lo, ci_hi, implied_rmse_change_at_max_dgroup, verdict`

No-fabrication status: every cell above is TBD. The only numbers in this file are the §0.1 diagnostics, reproducible from the round_v4 artefacts.

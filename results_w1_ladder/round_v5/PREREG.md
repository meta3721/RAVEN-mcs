# W1 round v5 — PREREG (A0)

Protocol: `results_w1_ladder/round_v5/PROTOCOL.md`
(sha256 `06eb85247d8cdcb4f43bfc8916d1ca6c59ee52848ead03722738914e7172589e`,
byte-identical copy of `ccfa-review-reports/raven-mcs-w1-round-v5-R1R3R4-protocol.md`).

This file is written **before** any A1/A2/A3 computation. Its sha256 is recorded in
`results_w1_ladder/round_v5/MANIFEST.sha256`. No margin, family, contrast, or
operational definition below may change after that hash is taken.

Scope executed in this round: A1, A2, A3, A4. **Part B is not executed**
(the authorization phrase is absent); A3's decision rule is applied mechanically.

---

## 1 Verbatim protocol text that fixes the margins, families and contrasts

### 1.1 A2 non-inferiority margin δ_WG (protocol §2 A2-analysis)

> **Non-inferiority (pre-declared):** for each trained arm vs. `fedavg_window` and vs.
> frozen `raven`, margin δ_WG = +0.5 % of the comparator's mean WorstGroupRMSE (the
> paper's existing descriptive line, now as a formal margin). One-sided 95 % bootstrap
> upper bound of the relative difference < δ_WG ⇒ "non-inferior"; > δ_WG with lower
> bound > 0 ⇒ "inferior"; otherwise "inconclusive". Holm over the NI family of that
> dataset.

### 1.2 A2 paired family and contrasts (protocol §2 A2-analysis)

> Paired contrasts: the same list as `round_v4/TRADEOFF_PAIRED.csv` (endpoint =
> WorstGroupRMSE).
> Bootstrap 10 000, seed 20261002; Wilcoxon; Holm family = one dataset × WorstGroupRMSE.

### 1.3 A3 equivalence margin δ_P, contrasts and family (protocol §2 A3.1)

> **Equivalence (TOST).** Margin δ_P = 0.5 % of the comparator's mean RMSE_μ per dataset
> (declared in A0). Contrasts: `proj_beta − uniform_window`, `proj_beta − fedavg_window`,
> `raven − proj_beta`, `proj_beta_debt − proj_beta`. Outcome per row ∈ {equivalent, harm
> (lower bound > 0), benefit (upper bound < 0), inconclusive}. Holm within dataset × TOST
> family.

### 1.4 τ_x (protocol §2 A1-G-xref)

> Tolerance τ_x := 10 × the largest endpoint spread across the A1-sens grid **for that arm
> and dataset**, declared in PREREG as this formula, not as a number. Pass if
> trained-vs-reference endpoint residual ≤ τ_x on all seeds **and** τ_x ≤ 1e-3 × the
> smallest claimed effect for that arm (0.005 in Δ_group units ⇒ τ_x ≤ 5e-6). If the
> second condition fails, the arm stays "exploratory: reference not numerically stable"
> and that is the reported result. Do not tighten or loosen afterwards.

Numerical form of the second condition, taken from the protocol itself:
`τ_x ≤ 1e-3 × 0.005 = 5e-6`. The "smallest claimed effect" 0.005 in Δ_group units is the
smallest claimed group-endpoint gain of the trained rules over `uniform_window` recorded
in the round-4 audit (`ccfa-review-reports/raven-mcs-experiment-design-audit.md` C10:
+0.768 pp SensorScope / +0.286 pp U-Air; 0.286 pp = 0.00572 Δ_group units; the protocol
fixes the bound at 0.005).

### 1.5 A3 decision rule (protocol §2 A3, applied mechanically)

> **A3 decision rule (written in A0, applied mechanically):**
> - If every primary row is "equivalent" or the dose-response CI excludes the effect
>   needed for a 0.25 % RMSE_μ gain at the observed Δ_group range ⇒ **R1 is closed as a
>   measured null. Part B is not run.** The paper reports equivalence within δ_P (later,
>   when edits resume).
> - If U-Air `proj_beta − uniform_window` is "harm" ⇒ report it as a harm finding; Part B
>   is not run to overturn it.
> - Only if rows are "inconclusive" **and** MDE > δ_P ⇒ Part B may be proposed to the user.

### 1.6 A2 secondary (protocol §2 A3.2 / A3.3)

> **MDE.** From the observed paired SD, the minimum detectable effect at α = 0.05
> (two-sided, Holm-adjusted for the family size actually used), power 0.8, n = 20; and the
> n needed to detect 0.25 % and 0.5 % RMSE_μ.
> **Seed-level dose-response (pre-declared, one test per dataset).** Across the 20 seeds
> and the four contrasts above, regress the paired RMSE_μ difference on the paired Δ_group
> difference (seed as random intercept, or a simple pooled-within-seed slope with
> seed-cluster bootstrap). H0: slope = 0. This tests "more alignment ⇒ lower error"
> without new runs. Report slope, 95 % CI, and the RMSE change implied by the largest
> observed Δ_group gain.

---

## 2 Frozen operational definitions (no free parameters after this point)

### 2.1 Data and arms

* Datasets: `sensorscope`, `uair`. **Never pooled.** Seeds 30001–30020 (20 per arm/dataset).
* Trained arms (Part B v4 runs, re-scored read-only):
  `results_w1_ladder/round_v4/train/v4/C0_frozen/<ds>/<arm>/seed<seed>/`
  for `uniform_window`, `proj_beta`, `proj_beta_debt` (A1, A2, A3).
* Frozen arms: `artifacts/e3_formal_runs_r1/runs/<ds>/<arm>/seed<seed>/` for
  `fedavg_window`, `inst_cal`, `raven` (A2, A3).
* A1 replays take `M_r`, `mu`, `w_atomic`, `pi_tar` from
  `W.build_case(ds, "R_on", "raven_wo_use", seed, pi_tar_for(ds))`
  (the round-v2/v3/v4 R_on ruler; verified identical across the state-bearing Design-on
  arms by round-v2 G1 and by protocol §0.1-1/§0.1-4).

### 2.2 A1-G-self (must be exact)

For each (ds, arm, seed) and each **active** window `j` of that run's own
`window_metrics.json`, in the order given there:

1. `clients_j` = `active_clients`, `beta_j` = `beta_hat` (both logged by the run);
   `M_j` = `build_case(...)["M"][j]`, `mu` = `build_case(...)["mu"]`.
2. Payload = `WindowAggregateInput(client_ids=clients_j, raw_counts=zeros(K),
   total_masses=zeros(K), compositions=M_j, beta_hat=beta_j, mu=mu)`, `K=len(clients_j)`.
3. `alpha_j = AggregatorClass().compute_server_weights(payload)` where `AggregatorClass` is
   imported from `scripts/w1_v4_train.py` (`UniformWindowAggregator`,
   `ProjBetaAggregator`, `ProjBetaDebtAggregator`), **a fresh instance per run** so that
   `Q_0 = 0` for the debt arm. The class is imported, never copied; `w1_v4_train`'s
   `wr.get_aggregator` / `POLICY_MAP` registration patch is applied by importing it.
4. Endpoints: `Δ_group`, `Δ_c-s` recomputed from the rebuilt α sequence with
   `w1_ladder.endpoints(case, alpha)` (i.e. `w1_replay.delta_group` over `M_r`, `mu`, and
   `w1_replay.delta_cs` over the run-ruler `pair_state`/`pi_tar`).

Alignment precondition (recorded, not a gate): `len(act) == case["n"]` and
`active_clients` equal window-by-window to the case. A mismatch is reported for that run
and the run is excluded from the G-self denominator with `status=misaligned`.

Pass (per run): `α L∞ vs the run's logged α == 0.0` **and**
`|Δ_group − final_metrics.Delta_group| ≤ 1e-12` **and**
`|Δ_c-s − final_metrics.Delta_c_s| ≤ 1e-12`.
Pass (per arm): 40/40 runs (2 datasets × 20 seeds).
On any failure: **stop A1**, report the first diverging window (smallest `j` with
`α L∞ > 0`), and do not proceed to A1-sens/G-xref for that arm.

### 2.3 A1-sens (solver sensitivity)

Grid axes (12 cells per run), computed on the same case and the same logged `beta_hat`:

* `beta_input` ∈ {`raw`, `norm`} — `norm` = `beta / beta.sum()`; `raw` = the logged `beta_hat`.
* `problem` ∈ {`cached`, `fresh`} — `cached` reuses one parameterized cvxpy `Problem` per
  `(K, cell)` (the `w1_v4_proj.proj_Cr` / `kappa_seq` style); `fresh` builds a new
  `Problem` per window (the `w1_v4_train` trained-aggregator style).
* `tol` ∈ {`default`, `1e-10`, `1e-12`} — CLARABEL `tol_gap_abs = tol_gap_rel = tol_feas = tol`;
  `default` means the call passes no tolerance arguments (the `kappa_seq` style).

Solve path per arm (faithful re-implementation of the replay functions, with the two extra
axes exposed; `scripts/w1_v4_proj.py` is **not** modified):

* `proj_beta`: projection onto `C_r` (Euclidean projection of the β input), i.e. the
  `proj_seq`/`proj_Cr` problem.
* `proj_beta_debt`: `argmin_{a∈C_r} −Q^T M a + (1/(2κ)) ||a − β||²`, `κ = 1000`,
  `Q_{r+1} = max(Q_r + 0.01 (mu − M_r a_r), 0)`, `Q_0 = 0` (the `kappa_seq` problem).
* `uniform_window`: analytic `α = 1/K`; no solver path. The grid therefore degenerates to a
  single cell, spread `0`, and `τ_x = 0` for this arm.

`C_r` in all cells: `sum(a)=1`, `a ≥ 0`, `a ≤ alpha_bar(0.5, K)`,
`||a||² ≤ 1/ess_ball_bound(3.0, K)`. Solver CLARABEL with SCS fallback for the debt path,
exactly as the two replay functions do.

Reference cell `R*` = the cell that reproduces the **unmodified** repository replay path:
`beta_input = raw`, `problem = cached`, `tol = 1e-10` for `proj_beta`
(`proj_seq → proj_Cr` uses `TOL = 1e-10`) and `tol = default` for `proj_beta_debt`
(`kappa_seq` passes no tolerance arguments). A fidelity check records
`α L∞` between cell `R*` and the imported `w1_v4_proj.proj_seq` / `kappa_seq` themselves.

Recorded per (ds, arm, seed, cell): `alpha_linf_vs_trained`, `abs_dd_group`,
`abs_dd_cs`, `first_diverging_window` (first `j` with per-window
`|α_j^cell − α_j^trained|_∞ > 0`), and for the debt arm `first_q_diverging_window`
(first `j` with `|Q_j^cell − Q_j^trained|_∞ > 1e-12`, where `Q^trained` is the Q trajectory
obtained by replaying the run's **own logged α** through the same recursion).

### 2.4 τ_x and A1-G-xref

`τ_x(arm, ds) = 10 × max over seeds, over endpoints E ∈ {Δ_group, Δ_c-s}, of
(max over the 12 grid cells of E − min over the 12 grid cells of E)`.

`residual(seed) = max(|Δ_group^trained − Δ_group^{R*}|, |Δ_c-s^trained − Δ_c-s^{R*}|)`.

Pass (per arm/dataset): `residual ≤ τ_x` on all 20 seeds **and** `τ_x ≤ 5e-6`.
If `τ_x > 5e-6`, the arm is reported as **"exploratory: reference not numerically stable"**
and that is the result; no tightening or loosening afterwards.

Additionally reported read-only (not part of the pass rule): the residual against the
*stored* round-v3/v4 reference columns actually used by the round-v4 gates
(B-G2 column `round_v3/SOURCE_LADDER.csv` `rule=B1, src=raven` for `proj_beta`;
B-G3 column `round_v4/DEBT_STRENGTH_V4.csv` `kappa=1000` for `proj_beta_debt`;
`round_v2/FRONTIER.csv` `d_unif_*` for `uniform_window`), because protocol §0.1-6
identifies those files as the reference columns behind the round-4 gate failures.

### 2.5 A1-R8 — `GATES_V5.csv`

One row per (ds, arm, seed, gate), gate ∈ {`B-G1`, `G-self`, `G-xref`}:

| gate | observed | tolerance | tolerance_source | pass |
|---|---|---|---|---|
| `B-G1` | number of windows whose `active_clients` differ from the frozen E3 `raven` run for the same (ds, seed) | `0` | exact active-set identity vs `artifacts/e3_formal_runs_r1/runs/<ds>/raven/seed<seed>/window_metrics.json` | `observed == 0` |
| `G-self` | `max(α L∞, |ΔΔ_group|, |ΔΔ_c-s|)` | `1e-12` | PREREG §2.2 (α must be exactly 0; both endpoints ≤ 1e-12) | `α L∞ == 0` and both endpoint errors ≤ 1e-12 |
| `G-xref` | `residual(seed)` (§2.4) | `τ_x(arm, ds)` | PREREG §2.4 = protocol §2 A1-G-xref formula | `residual ≤ τ_x` for all seeds of the arm **and** `τ_x ≤ 5e-6` |

`round_v4/TRAIN_GATES.csv` is read-only in this round and is not modified; its `pass`
column reflects B-G1 only (protocol §A1-R8; stated in `EXECUTION_REPORT.md`).

### 2.6 A2 (R3) — worst-group re-scoring

* **A2-G0**: for every one of the 240 runs (120 Part B + 120 frozen), build the runner with
  `raven_mcs.training.window_runner.build_full_runner` using the run's own
  `config_snapshot.json` (`dataset`, `method`, `seed`, `local_steps`), the frozen EventTrace
  `artifacts/e3_formal_runs_r1/eventtraces/<ds>/seed<seed>/training_eventtrace`, the frozen
  target bundle (`production_target_bundle`) and the sealed support; load
  `checkpoints/final.pt` into `runner.theta` and `runner.model`; predict the test split with
  `raven_mcs.e3.real_runner.runner._predict(runner, ds, "test")`; recompute `RMSE_mu`,
  `Head_RMSE`, `Tail_RMSE` with `rmse_mu`, `_mu_weights_for_test`, `_head_tail_rmse`
  exactly as `run_e3_real` does. Pass: all three ≤ 1e-10 vs `final_metrics.json` on every
  run. For the frozen arms `fedavg_window` and `raven`, also reproduce the **stored**
  `WorstGroupRMSE` of `RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv`
  ≤ 1e-10. `inst_cal` has no stored `WorstGroupRMSE` in any frozen artefact: the row is
  marked `source=frozen_record_absent` and G0 for it covers `RMSE_mu/Head/Tail` only.
  **One failure ⇒ stop A2 and report; no fallback to retraining.**
* **A2-score**: `WorstGroupRMSE = max_g wRMSE_g` over the four UTC six-hour blocks
  `g ∈ {R0,R1,R2,R3}`, with the μ-weights `_mu_weights_for_test(pred, mu)` and the verbatim
  `_wrmse_block` of `scripts/run_joint_ou_cs_p2.py` (the function used at
  `scripts/run_nodesign_supplement.py` L234-239). Block id of a test unit =
  `int(part[5:])` for the `block<k>` part of its target-group string (identical to
  `RepeatableTimeOfDayMapper()` on `absolute_time`; verified equal in recon). This is the
  paper's four-block worst-group definition (Table II per-seed file
  `TABLE_II_WORSTGROUP_PER_SEED.csv`, `RMSE_block0..3`; precedent
  `scripts/audit_table2_uair_fedavg.py:block_rmse`). Groups with no test unit give `NaN`
  and are excluded from the max. Store `WG_R0..WG_R3` and `argmax_group`.
  For frozen arms without a reproducible checkpoint the row would carry
  `source=frozen_record`; in this round every frozen arm has `final.pt` (120/120), so no
  row uses that path.
* **A2-analysis** (per dataset, never pooled): contrasts as §1.2 —
  `proj_beta − uniform_window`, `raven − proj_beta`, `proj_beta − fedavg_window`,
  `uniform_window − fedavg_window`, `proj_beta_debt − proj_beta`; paired per seed;
  bootstrap 10 000 resamples with `numpy.random.default_rng(20261002)` (one generator per
  (ds, endpoint) family, resampling the paired differences); two-sided Wilcoxon
  (`scipy.stats.wilcoxon`, exact-free default) and Holm within the 5-row family of that
  dataset. `WorstGroupRMSE` is the endpoint; `RMSE_mu`, `argmax_group` change and the worst
  block are reported descriptively.
* **A2 NI**: `rel_diff(seed) = (WG_arm − WG_comparator)/WG_comparator`. Bootstrap 10 000 with
  the same RNG seed 20261002 of the per-seed relative differences; `mean_rel_diff` = mean of
  the per-seed relative differences; `ub95_one_sided` = 95th percentile,
  `lb95_one_sided` = 5th percentile of the bootstrap distribution of that mean.
  `margin = 0.005 × mean(WG_comparator)` in relative units (`δ_WG = +0.5 %`).
  Verdict: `ub95_one_sided < margin` ⇒ non-inferior; else
  `ub95_one_sided > margin` and `lb95_one_sided > 0` ⇒ inferior; else inconclusive.
  `p_raw` = fraction of bootstrap replicates `≥ margin` (bootstrap p for
  `H0: rel ≥ δ_WG`), Holm-adjusted within the 6-row NI family of that dataset ⇒ `p_holm`
  (this is the same quantity the bound rule reads: `ub95 < margin ⟺ p_raw < 0.05`).
  The NI family is the 3 trained arms × 2 comparators per dataset.
  "Trained arms" = `uniform_window`, `proj_beta`, `proj_beta_debt` (the three arms Part B v4
  trained); comparators = `fedavg_window`, `raven`.

### 2.7 A3 (R1a)

* Endpoint primary `RMSE_mu` from `round_v4/TRADEOFF.csv` (240 rows, 6 arms × 2 datasets ×
  20 seeds); secondary `WorstGroupRMSE` from A2.
* **TOST**: four contrasts (§1.3), paired per seed, `diff = RMSE_mu(a) − RMSE_mu(b)`.
  Bootstrap 10 000 with `numpy.random.default_rng(20261002)` per (ds) TOST family;
  `ci90_lo/ci90_hi` = 5th/95th percentiles of the bootstrap distribution of the mean
  difference. `margin = δ_P = 0.005 × mean(RMSE_mu of the comparator)` (absolute units);
  `rel_diff = mean_diff / mean(RMSE_mu comparator)`. Verdict:
  `ci90_lo > −margin and ci90_hi < +margin` ⇒ `equivalent`; else `ci90_lo > 0` ⇒ `harm`;
  else `ci90_hi < 0` ⇒ `benefit`; else `inconclusive`.
  `p_lower` = fraction of bootstrap replicates `≤ −margin`, `p_upper` = fraction `≥ +margin`,
  `p_tost = max(p_lower, p_upper)`, Holm within the 4-row family of that dataset ⇒
  `p_tost_holm`.
* **MDE**: `mde_n20 = (z_{1−α*/2} + z_{0.8}) × sd(diff) / sqrt(20)` with
  `sd(diff)` the observed paired SD (`ddof=1`), `α* = 0.05 / m` the Holm-adjusted
  two-sided level with `m = 4` (the family size actually used: one dataset × TOST),
  `z` from `scipy.stats.norm.ppf`; `power = 0.8`. Reported both absolutely and as a
  percentage of the comparator mean (`mde_n20_rel_pct`). `n_for_pct = ceil(((z_{1−α*/2} +
  z_{0.8}) × sd / (pct × mean(RMSE_mu comparator)))²)` for `pct ∈ {0.25 %, 0.5 %}`.
* **Dose-response** (one test per dataset): the 4 contrasts × 20 seeds = 80 paired
  observations; `y = ΔRMSE_mu` (contrast difference), `x = ΔΔ_group` (same contrast,
  `Delta_group` difference). OLS slope through the pooled 80 points (no per-seed
  intercept; seed is the cluster). 95 % CI from a seed-cluster bootstrap: 10 000
  resamples of the 20 seeds with replacement (`default_rng(20261002)`), refitting the
  pooled slope on the resampled clusters; `ci_lo/ci_hi` = 2.5th/97.5th percentiles.
  `implied_rmse_change_at_max_dgroup = slope × min(ΔΔ_group over the 80 observations)`
  (the largest observed alignment gain is the most negative `ΔΔ_group`; "more alignment ⇒
  lower error" means slope > 0 and a negative implied change). Verdict `slope_ci_excludes_0`
  if the CI excludes 0, else `slope_ci_includes_0`.
* **Decision inputs**: `needed = −0.0025 × mean(RMSE_mu of the comparator of the primary
  contrast)` per dataset = the RMSE_mu change corresponding to a 0.25 % gain. The
  dose-response CI "excludes the effect needed for a 0.25 % gain at the observed Δ_group
  range" iff `ci_lo(implied change) > needed`. The primary contrast is
  `proj_beta − uniform_window` (protocol §3 H1) with comparator `uniform_window`.

---

## 3 Stop rules carried into execution (verbatim, protocol §2/§4)

> Any failure: stop A1 and report the first diverging window.

> One failure ⇒ stop A2 and report; do not fall back to retraining without asking.

> If the second condition fails, the arm stays "exploratory: reference not numerically
> stable" and that is the reported result.

Forbidden in this round (protocol §4): editing `src/`, `main.tex`, `appendix.tex`,
`supplemental.tex`, or any `round_v1..v4` file; freezing/overwriting `M_r`; changing Holm
families, switching to one-sided tests, dropping contrasts, or changing δ after A0;
pooling datasets; re-running Part B v4; resuming X1; ingesting PATH_A NO2; running full
`build()` of `build_public_repro_bundle.py`; committing or pushing. Part B additionally
requires the exact phrase `授权 v5 Part B`, which is absent.

## 4 No-fabrication statement

Every cell written in this round is reproducible from the artefacts listed in §2 by the
scripts `scripts/w1_v5_a1.py`, `scripts/w1_v5_a2.py`, `scripts/w1_v5_a3.py`. If a step
cannot be executed, the cell is written `TBD` with the reason in
`round_v5/EXECUTION_REPORT.md`; no value is imputed.

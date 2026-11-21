# W1 round v5 — EXECUTION_REPORT (A1 / A2 / A3 / A4)

Protocol: `results_w1_ladder/round_v5/PROTOCOL.md`
(sha256 `06eb85247d8cdcb4f43bfc8916d1ca6c59ee52848ead03722738914e7172589e`,
byte-identical to `ccfa-review-reports/raven-mcs-w1-round-v5-R1R3R4-protocol.md`).
Preregistration: `PREREG.md`, sha256
`13ff49e5dc0a79faa5b52dadc304d2488b6e9809449472937daf617061d4d154`, recorded in
`MANIFEST.sha256` **before** any A1/A2/A3 computation.

Round executed: A0 (PREREG) → A1 → A2 → A3 → A4. **Part B was not run**: the decision
rule of protocol §2 A3 closes R1 as a measured null and, independently, the
authorization phrase `授权 v5 Part B` is absent.

All writes are confined to `results_w1_ladder/round_v5/` and `scripts/w1_v5_*.py`.
No `src/`, manuscript, `round_v1..round_v4`, `tdrive_protocol_seal_r1/` or `artifacts/`
file was modified; no git command was run.

---

## 0 `round_v4/TRAIN_GATES.csv` (protocol §A1-R8) — read-only, unchanged

**`results_w1_ladder/round_v4/TRAIN_GATES.csv` is not modified by this round and must not
be modified.** Its `pass` column reflects **B-G1 only** (per-window active-client identity
against the frozen E3 `raven` run, plus the round-v4 B-G2/B-G3 endpoint comparison that
was folded into the same column by `scripts/w1_v4_check.py` at that time); it is not a
statement about self-replay identity or about cross-implementation solver stability.
Round v5 writes its own gate file, `GATES_V5.csv`, whose `pass` column is the tri-gate
(B-G1 / G-self / G-xref) result defined in PREREG §2.5.

---

## 1 A1 (R4 + R8) — gate re-specification

Script: `scripts/w1_v5_a1.py` (parts `A1_*_part_*.csv`, merged into `A1_GSELF.csv`,
`A1_SENS_GRID.csv`, `A1_SENS_SUMMARY.csv`, `GATES_V5.csv`, `A1_SUMMARY.json`).
Secondary read-only cross-check: `scripts/w1_v5_xref_legacy.py` → `A1_LEGACY_XREF.csv`.
Failure diagnosis: `scripts/w1_v5_probe_gself.py` → `A1_GSELF_FAIL_DIAG.json`.

Work: 3 arms × 2 datasets × 20 seeds = 120 runs. Each run rebuilt α window-by-window from
its **own** logged `active_clients` / `beta_hat` with M_r, mu taken from
`W.build_case(ds,"R_on","raven_wo_use",seed)` and the aggregator class imported from
`scripts/w1_v4_train.py` (fresh instance per run, so `Q_0 = 0`), then replayed the same
windows on the 12-cell sensitivity grid. 0 solver fallbacks to SCS on all cells.

### 1.1 A1-G-self — 118/120 exact; **2 failures ⇒ protocol stop rule triggered**

| quantity | result |
|---|---|
| B-G1 active-set identity | 120/120 runs, 0 mismatching windows (all 6 arm×dataset cells 20/20) |
| α L∞ = 0 | 118/120 runs exact (`alpha_linf` is exactly `0.0`; the other 118 rows have max 0.0) |
| endpoint errors | over all 120 runs: max \|Δ_group − final_metrics\| = 8.88e-16, max \|Δ_c-s − final_metrics\| = 5.77e-15 (tolerance 1e-12) |
| **failures** | `uair` / `proj_beta` / seed 30001 and seed 30011 |

Failure detail (protocol: *"Any failure: stop A1 and report the first diverging window"*):

| ds | arm | seed | α L∞ | **first diverging window** | worst window | endpoint errors |
|---|---|---|---|---|---|---|
| uair | proj_beta | 30001 | 6.452e-09 | **0** (6.45e-9 first appears at window 3) | w=3, K=3 | \|Δ_group\|=4.44e-15, \|Δ_c-s\|=6.66e-16 |
| uair | proj_beta | 30011 | 1.110e-16 (1 ULP) | **37** | w=37, K=6 | \|Δ_group\|=4.44e-16, \|Δ_c-s\|=2.22e-16 |

Mechanism (`A1_GSELF_FAIL_DIAG.json`): the divergence is **solver-level, not rule-level**.
(1) The α-renormalization guard at `src/raven_mcs/training/window_runner.py` L1151 does not
fire: `|Σα − 1| ≤ 2.39e-10` in both the logged and the rebuilt sequence (threshold 1e-8).
(2) The rebuilt α has the same support (same number of non-zero entries) and the same
per-window sum to ≤6e-13. (3) The endpoints agree to ≤1e-15 on both failing runs. The
projection QP is therefore reproducible at the endpoint level but not bit-exactly in α.
**A1 is stopped here**: no A1-dependent pass is claimed for the `proj_beta`/U-Air cell as
a bit-exact identity. The grid and G-xref numbers below were produced in the same
preregistered pass and are reported as measured; nothing was re-run, tightened or relaxed.

### 1.2 A1-sens grid

`A1_SENS_GRID.csv`: 12 cells × 80 solver-arm runs + 40 single-cell analytic control runs.

Cell definition: `proj_beta` = Euclidean projection of the β input onto C_r; `proj_beta_debt`
= `argmin_{C_r} −Q^T M a + (1/(2κ))‖a−β‖²`, κ=1000, `Q_{r+1}=max(Q_r+0.01(μ−M_r a_r),0)`,
`Q_0=0`; `C_r` = {Σa=1, a≥0, a≤alpha_bar(0.5,K), ‖a‖²≤1/ess_ball_bound(3,K)}.
Reference cell `R*` = the unmodified repository replay path: `raw`/`cached`/`1e-10` for
`proj_beta` (`proj_seq → proj_Cr`) and `raw`/`cached`/CLARABEL-default for `proj_beta_debt`
(`kappa_seq`). Fidelity of `R*` against the imported repository functions: α L∞ = 3.34e-08
(SensorScope `proj_seq`) / 6.45e-09 (U-Air `proj_seq`) / **exactly 0.0** for `kappa_seq` on
both datasets.

| ds | arm | spread Δ_group | spread Δ_c-s | **τ_x** | τ_x ≤ 5e-6 | max α L∞ over grid | solver fails |
|---|---|---|---|---|---|---|---|
| sensorscope | proj_beta | 4.645e-06 | 5.778e-06 | **5.778e-05** | no | 1.76e-04 | 0 |
| sensorscope | proj_beta_debt | 1.289e-04 | 9.551e-05 | **1.289e-03** | no | 5.68e-03 | 0 |
| sensorscope | uniform_window | 0.0 | 0.0 | **0.0** | yes | 0.0 | 0 |
| uair | proj_beta | 5.877e-06 | 6.191e-06 | **6.191e-05** | no | 1.82e-04 | 0 |
| uair | proj_beta_debt | 6.460e-05 | 5.919e-05 | **6.460e-04** | no | 7.91e-04 | 0 |
| uair | uniform_window | 0.0 | 0.0 | **0.0** | yes | 0.0 | 0 |

Which axis moves the endpoint (median \|cell − trained\| in Δ_group units):

| arm | β input | problem object | CLARABEL tolerance |
|---|---|---|---|
| proj_beta | `raw` 8.20e-07 / `norm` 5.47e-08 (SS); 2.59e-07 / 1.97e-08 (UA) | `cached` 1.15e-08 / `fresh` 1.20e-06 (SS); 3.48e-09 / 7.92e-07 (UA) | 1e-10, 1e-12, default all ≈4.5e-07 (SS) / 1.3e-07 (UA) |
| proj_beta_debt | `raw` 1.04e-05 / `norm` 5.57e-06 (SS); 1.23e-05 / 1.23e-05 (UA) | `cached` 1.29e-05 / `fresh` 3.65e-06 (SS); 2.39e-05 / 6.19e-06 (UA) | 1e-10 8.89e-06, 1e-12 8.58e-06, default 1.40e-06 (SS); 1.29e-05, 1.30e-05, 6.35e-06 (UA) |

Dominant axes: for `proj_beta` the **problem-object** axis (fresh-per-window vs cached
parameterized, i.e. the solver's from-scratch vs warm-started path); for `proj_beta_debt`
the **problem-object** and **tolerance** axes together — consistent with the near-LP
conditioning of the debt objective at κ=1000 (quadratic weight 1e-3).

Debt-arm `Q` divergence (`A1_SENS_GRID.csv.first_q_diverging_window`, threshold 1e-12):
for the cell that matches the trained rule (`norm`/`fresh`/default) `Q` never diverges
(`NaN`, α L∞ = 0); every other cell diverges at window 3–5 (SensorScope) / 5 (U-Air), and
the near-tie cell `raw`/`fresh`/default only at window 65–96 (SensorScope) / 54–63 (U-Air).

### 1.3 A1-G-xref — both trained arms: **"exploratory: reference not numerically stable"**

| ds | arm | R* residual, max over seeds | τ_x | residual ≤ τ_x | τ_x ≤ 5e-6 | verdict |
|---|---|---|---|---|---|---|
| sensorscope | proj_beta | 2.083e-06 | 5.778e-05 | yes | **no** | exploratory: reference not numerically stable |
| sensorscope | proj_beta_debt | 8.624e-05 | 1.289e-03 | yes | **no** | exploratory: reference not numerically stable |
| sensorscope | uniform_window | 5.773e-15 | 0.0 | **no** (degenerate) | yes | see note |
| uair | proj_beta | 2.674e-06 | 6.191e-05 | yes | **no** | exploratory: reference not numerically stable |
| uair | proj_beta_debt | 4.976e-05 | 6.460e-04 | yes | **no** | exploratory: reference not numerically stable |
| uair | uniform_window | 8.882e-16 | 0.0 | **no** (degenerate) | yes | see note |

Per protocol §2 A1-G-xref the second condition (τ_x ≤ 1e-3 × 0.005 = 5e-6) fails for both
trained solver arms, so **that is the reported result** for them; the formula is not
tightened or loosened afterwards. `GATES_V5.csv` therefore has 0/120 passing `G-xref` rows.

Note on the `uniform_window` control: it has no solver path, so its grid is the single
analytic rule, spread = 0 and τ_x = 0 exactly. Its residual (`≤8.9e-16`) is the pure
floating-point gap between `w1_ladder.endpoints()` and the runner's own `delta_group()` —
the strict inequality `residual ≤ 0` cannot be met by any float computation. This is a
degenerate case of the preregistered formula, not a numerical instability of the control.

### 1.4 A1 secondary: trained endpoints vs the *stored* round-v3/v4 reference columns

`A1_LEGACY_XREF.csv` (read-only, not part of the pass rule) reproduces protocol §0.1-6 and
audit item C10 exactly:

| ds | arm | max \|Δ_group\| vs stored reference | max \|Δ_c-s\| vs stored reference | stored reference |
|---|---|---|---|---|
| sensorscope | proj_beta | 2.07e-06 | 4.70e-07 | `round_v3/SOURCE_LADDER.csv` rule=B1 src=raven |
| sensorscope | proj_beta_debt | 2.89e-05 | 1.43e-05 | `round_v4/DEBT_STRENGTH_V4.csv` κ=1000 |
| sensorscope | uniform_window | 0.0 | 0.0 | `round_v2/FRONTIER.csv` d_unif_* |
| uair | proj_beta | 2.67e-06 | 2.67e-06 | `round_v3/SOURCE_LADDER.csv` rule=B1 src=raven |
| uair | proj_beta_debt | 3.77e-05 | 3.72e-05 | `round_v4/DEBT_STRENGTH_V4.csv` κ=1000 |
| uair | uniform_window | 0.0 | 0.0 | `round_v2/FRONTIER.csv` d_unif_* |

---

## 2 A2 (R3) — **STOPPED at A2-G0**

Script: `scripts/w1_v5_a2.py`. Raw output: `A2_part_*.csv`; merged G0 evidence:
`WORSTGROUP_V5.csv` (240 rows), `A2_G0_FAILURES.csv` (18 rows), `A2_G0_SUMMARY.json`,
`A2_STOP.json`.

Work done: 240/240 runs re-scored from `checkpoints/final.pt` — 120 Part B v4 runs
(`uniform_window`, `proj_beta`, `proj_beta_debt`) and 120 frozen runs (`fedavg_window`,
`inst_cal`, `raven`), both datasets, 20 seeds each. Every run has a checkpoint, so **no row
uses the `source=frozen_record` path**. Runner built with
`build_full_runner` from each run's own `config_snapshot.json`, the frozen EventTrace
`artifacts/e3_formal_runs_r1/eventtraces/<ds>/seed<seed>/training_eventtrace`, the frozen
target bundle and the sealed support; prediction by
`raven_mcs.e3.real_runner.runner._predict(runner, ds, "test")`.

### 2.1 A2-G0 result

| block | rows | pass | max \|ΔRMSE_mu\| | max \|ΔHead\| | max \|ΔTail\| |
|---|---|---|---|---|---|
| SensorScope | 120 | **120/120** | 0.0 | 0.0 | 0.0 |
| U-Air | 120 | **102/120** | 5.661e-02 | 5.361e-02 | 5.947e-02 |
| frozen stored `WorstGroupRMSE` (fedavg_window, raven × 2 ds) | 80 | 7/80 at 1e-10 | — | — | max diff 2.355e-09 |

**The 18 failing rows are all `uair` and all at seeds 30007, 30016, 30018, for all six
arms** (`A2_G0_FAILURES.csv`):

| ds | arm | seed | recomputed RMSE_mu | stored final_metrics RMSE_mu | \|Δ\| | published checkpoint-based `RMSE_mu` | \|Δ\| vs published |
|---|---|---|---|---|---|---|---|
| uair | raven | 30007 | 1.189413 | 1.142487 | 4.693e-02 | 1.189413 | ≤2e-09 |
| uair | raven | 30016 | 1.152670 | 1.170926 | 1.826e-02 | 1.152670 | ≤2e-09 |
| uair | raven | 30018 | 1.181723 | 1.125360 | 5.636e-02 | 1.181723 | ≤2e-09 |
| uair | fedavg_window | 30007 | 1.193597 | 1.145170 | 4.843e-02 | 1.193597 | ≤2e-09 |
| uair | fedavg_window | 30016 | 1.144226 | 1.167526 | 2.330e-02 | 1.144226 | ≤2e-09 |
| uair | fedavg_window | 30018 | 1.178757 | 1.123620 | 5.514e-02 | 1.178757 | ≤2e-09 |
| uair | uniform_window | 30007 | 1.192228 | 1.144463 | 4.777e-02 | — | — |
| uair | uniform_window | 30016 | 1.144878 | 1.165949 | 2.107e-02 | — | — |
| uair | uniform_window | 30018 | 1.178425 | 1.122450 | 5.598e-02 | — | — |
| uair | proj_beta | 30007 | 1.189428 | 1.142453 | 4.698e-02 | — | — |
| uair | proj_beta | 30016 | 1.159220 | 1.174167 | 1.495e-02 | — | — |
| uair | proj_beta | 30018 | 1.184238 | 1.127628 | 5.661e-02 | — | — |
| uair | proj_beta_debt | 30007 | 1.187525 | 1.140623 | 4.690e-02 | — | — |
| uair | proj_beta_debt | 30016 | 1.160029 | 1.176599 | 1.657e-02 | — | — |
| uair | proj_beta_debt | 30018 | 1.179586 | 1.123468 | 5.612e-02 | — | — |
| uair | inst_cal | 30007 | 1.189412 | 1.142486 | 4.693e-02 | — | — |
| uair | inst_cal | 30016 | 1.152631 | 1.170900 | 1.827e-02 | — | — |
| uair | inst_cal | 30018 | 1.181723 | 1.125360 | 5.636e-02 | — | — |

Corroboration that this is an artefact defect and not a defect of this round's code:

* Over all 240 rows this round's checkpoint-based recomputation agrees with the
  independently published checkpoint-based table
  `RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv` to **1.89e-09**
  (`RMSE_mu`) and **2.36e-09** (`WorstGroupRMSE`); restricted to U-Air, 1.84e-09.
* The same three seeds are already recorded as a known mixed-sourcing defect in
  `results_seed_path_audit_r1/C_IMPACT_RECALC.csv` and in
  `ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md` §2A N3
  ("the two disagreeing at seeds 30007 / 30016 / 30018 by 2–5 %, with 30016 and 30018
  inside the TEST window").
* SensorScope reproduces **bit-exactly** (max \|Δ\| = 0.0 on all three endpoints), so the
  pipeline itself is exact; only the U-Air tree at those three seeds is internally
  inconsistent (its `final_metrics.json` is not reproducible from its own
  `checkpoints/final.pt`).
* The residual `WorstGroupRMSE` difference against the stored Table II column
  (max 2.36e-09 vs the 1e-10 gate) is a floating-point path difference, i.e. 7 orders of
  magnitude below any reported effect (\|Δ\|/WorstGroupRMSE ≤ 1.9e-09 relative).

### 2.2 Stop applied

Protocol §2 A2-G0, quoted: *"One failure ⇒ stop A2 and report; do not fall back to
retraining without asking."* Therefore:

* **No** A2-score analysis was performed: `WORSTGROUP_PAIRED.csv` and `WORSTGROUP_NI.csv`
  are written as TBD stubs whose every field is `TBD_A2_G0_STOP` with the reason recorded
  here and in `A2_STOP.json`.
* **`TRADEOFF_V5.csv`** keeps the exact round-v4 columns, its `WorstGroupRMSE` column is
  left empty and a `WG_status` column is set to `TBD_A2_G0_STOP` on every row
  (`round_v4/TRADEOFF.csv` untouched).
* `WORSTGROUP_V5.csv` is the **A2-G0 evidence file** (240 per-run rows with `d_rmse`,
  `d_head`, `d_tail`, `WorstGroupRMSE`, `WG_R0..R3`, `argmax_group`, `g0_pass`,
  `a2_status`). These per-run readings are raw recomputations, **not validated scores**;
  no paired contrast, bootstrap, Wilcoxon, Holm or non-inferiority verdict exists for
  them in this round.
* Had the rule been scoped per dataset, SensorScope alone would have been scoreable
  (120/120 G0 rows exact). It is flagged here as informational only; the preregistered
  rule was applied as written.

### 2.3 Raw (unvalidated) worst-group descriptives — no inferential verdict

Reported only because protocol §2 A2-analysis asks which group is worst and whether
`argmax_group` changes between arms; these are the raw per-run recomputations, not
gate-passed scores, and no paired/NI/Holm statement accompanies them:

* The worst of the four UTC blocks is **R2 in all 240 runs** (`argmax_group = 2`
  everywhere), so `argmax_group` never changes between arms on this data.
* Mean `WorstGroupRMSE` by arm (20 seeds): SensorScope 8.6699 (`proj_beta`) … 8.6720
  (`uniform_window`); U-Air 1.2596 (`fedavg_window`) … 1.2647 (`proj_beta`). Spread across
  arms is ≈2e-03 (SS) and ≈5e-03 (UA), i.e. ≤0.05 % relative, before any interval is
  attached. Under the preregistered NI device (δ_WG = +0.5 % of the comparator mean) all
  these point differences would sit far inside the margin, but **no NI verdict is claimed**,
  because the gate that must precede it failed.

---

## 3 A3 (R1a) — equivalence / power / dose-response on the existing 20 seeds

Script: `scripts/w1_v5_a3.py`. Outputs: `R1A_TOST.csv` (primary endpoint, 8 rows),
`R1A_TOST_WG.csv` (secondary endpoint = TBD stub: A2 stopped), `R1A_DOSE.csv`,
`A3_SUMMARY.json`. Input: `round_v4/TRADEOFF.csv` alone for the primary endpoint.

### 3.1 TOST (δ_P = 0.5 % of the comparator's mean RMSE_mu; family = one dataset × 4 contrasts)

| ds | contrast | mean diff | rel | 90 % CI | margin δ_P | verdict | p_tost (Holm) |
|---|---|---|---|---|---|---|---|
| sensorscope | proj_beta − uniform_window | −0.002057 | −0.026 % | [−0.006221, +0.002199] | 0.039697 | equivalent | 0.0000 |
| sensorscope | proj_beta − fedavg_window | −0.001643 | −0.021 % | [−0.005897, +0.002694] | 0.039694 | equivalent | 0.0000 |
| sensorscope | raven − proj_beta | +0.000739 | +0.009 % | [−0.000905, +0.002371] | 0.039686 | equivalent | 0.0000 |
| sensorscope | proj_beta_debt − proj_beta | +0.001170 | +0.015 % | [−0.002201, +0.004935] | 0.039686 | equivalent | 0.0000 |
| uair | proj_beta − uniform_window | +0.003120 | +0.262 % | [+0.001181, +0.005037] | 0.005947 | equivalent | 0.0152 |
| uair | proj_beta − fedavg_window | +0.004240 | +0.357 % | [+0.000051, +0.008773] | 0.005941 | **harm** | 0.2601 |
| uair | raven − proj_beta | −0.001363 | −0.114 % | [−0.002336, −0.000421] | 0.005962 | equivalent | 0.0000 |
| uair | proj_beta_debt − proj_beta | −0.002103 | −0.176 % | [−0.003885, −0.000324] | 0.005962 | equivalent | 0.0015 |

Four verdicts per dataset: SensorScope = {equivalent, equivalent, equivalent, equivalent};
U-Air = {equivalent, **harm**, equivalent, equivalent}. No row is `benefit`, none is
`inconclusive`.

Reading of the one `harm` row, stated without over-claim: the 90 % CI for
`proj_beta − fedavg_window` on U-Air lies strictly above zero and strictly outside the
δ_P margin on the harmful side, so the preregistered CI rule labels it `harm`; its
Holm-adjusted TOST p-value is 0.2601, i.e. the departure from equivalence does **not**
survive the family adjustment. It is a directional reading, not a multiplicity-robust
harm claim. The decision rule's harm clause names `proj_beta − uniform_window`, which is
`equivalent` on U-Air.

### 3.2 MDE (α = 0.05 two-sided, Holm-adjusted to the family actually used, m = 4 ⇒ z = 2.4977; power 0.8 ⇒ z = 0.8416; n = 20)

| ds | contrast | paired SD | MDE at n = 20 | MDE as % of comparator mean | n for 0.25 % | n for 0.5 % |
|---|---|---|---|---|---|---|
| sensorscope | proj_beta − uniform_window | 0.011614 | 0.008672 | 0.109 % | 4 | 1 |
| sensorscope | proj_beta − fedavg_window | 0.011858 | 0.008854 | 0.112 % | 4 | 1 |
| sensorscope | raven − proj_beta | 0.004532 | 0.003384 | 0.043 % | 1 | 1 |
| sensorscope | proj_beta_debt − proj_beta | 0.009909 | 0.007399 | 0.093 % | 3 | 1 |
| uair | proj_beta − uniform_window | 0.005404 | 0.004035 | 0.339 % | 37 | 10 |
| uair | proj_beta − fedavg_window | 0.012227 | 0.009130 | 0.768 % | 189 | 48 |
| uair | raven − proj_beta | 0.002695 | 0.002012 | 0.169 % | 10 | 3 |
| uair | proj_beta_debt − proj_beta | 0.005051 | 0.003772 | 0.316 % | 33 | 9 |

MDE > δ_P holds for exactly one row: U-Air `proj_beta − fedavg_window`
(0.009130 > 0.005941). Every other row has MDE < δ_P (the next largest is U-Air
`proj_beta − uniform_window`, 0.004035 < 0.005947). That single row is nevertheless *not*
`inconclusive` (it is the `harm` row), so the "inconclusive **and** MDE > δ_P" branch of
the decision rule is not reachable on this data.

### 3.3 Seed-level dose-response (one test per dataset; 4 contrasts × 20 seeds = 80 paired observations; seed-cluster bootstrap)

| ds | slope | 95 % CI | verdict | largest observed Δ_group gain | implied RMSE_mu change at that gain | 95 % CI of the implied change | change needed for a 0.25 % gain | CI excludes the needed effect |
|---|---|---|---|---|---|---|---|---|
| sensorscope | +0.032458 | [−0.096635, +0.152484] | slope CI includes 0 | −0.069718 | −0.002263 | [−0.010631, +0.006737] | −0.019848 | **yes** |
| uair | −0.107875 | [−0.252297, +0.046050] | slope CI includes 0 | −0.053893 | +0.005814 | [−0.002482, +0.013597] | −0.002973 | **yes** (marginal) |

Neither dataset shows a positive alignment→accuracy slope; the U-Air point estimate has the
opposite sign. The "excludes the needed effect" result is decisive for SensorScope and
*marginal* for U-Air (−0.002482 vs the required −0.002973); this is reported as such.

### 3.4 A3 decision (rule quoted verbatim from protocol §2 A3, applied mechanically)

> - If every primary row is "equivalent" or the dose-response CI excludes the effect
>   needed for a 0.25 % RMSE_μ gain at the observed Δ_group range ⇒ **R1 is closed as a
>   measured null. Part B is not run.** The paper reports equivalence within δ_P (later,
>   when edits resume).
> - If U-Air `proj_beta − uniform_window` is "harm" ⇒ report it as a harm finding; Part B
>   is not run to overturn it.
> - Only if rows are "inconclusive" **and** MDE > δ_P ⇒ Part B may be proposed to the user.

Mechanical application:

| clause | condition | result |
|---|---|---|
| 1a | every primary row "equivalent" | SensorScope yes; U-Air no (one `harm`) ⇒ clause 1a not satisfied |
| 1b | dose-response CI excludes the effect needed for a 0.25 % gain | **yes for both datasets** (SensorScope decisively, U-Air marginally) ⇒ **clause 1b satisfied** |
| 2 | U-Air `proj_beta − uniform_window` is "harm" | no (it is `equivalent`, +0.262 % inside δ_P = 0.594 %) |
| 3 | rows "inconclusive" **and** MDE > δ_P | no inconclusive rows exist ⇒ not reachable |

**Decision: R1 is closed as a measured null. Part B is not run.** The decision is
independent of clause 1a and of the harm reading in §3.1; it comes from clause 1b.
Per protocol §3, Part B would additionally require the phrase `授权 v5 Part B`, which the
user has not written.

### 3.5 Exploratory robustness (not preregistered, not part of the decision)

Because A2-G0 showed the three U-Air seeds are internally inconsistent, the U-Air TOST and
dose-response were repeated with `RMSE_mu` replaced by the checkpoint-based recomputation
(`scripts/w1_v5_a3_robust.py` → `A3_ROBUSTNESS_Uair.csv`, `A3_ROBUSTNESS_Uair_DOSE.csv`).
All four verdicts are unchanged (`equivalent`, `harm`, `equivalent`, `equivalent`); the
slope changes from −0.1079 to −0.1224 and stays CI-including-0. The preregistered
`R1A_*` files and the decision are untouched.

Caveat carried forward: 5 of the 6 U-Air arms' `RMSE_mu` in `round_v4/TRADEOFF.csv`
(the three frozen arms from the E3 tree, the three trained arms from their own
`final_metrics.json` written by the same driver) are not reproducible from their
checkpoints at seeds 30007/30016/30018. SensorScope is unaffected (exact).

---

## 4 Deliverables in `results_w1_ladder/round_v5/`

`PROTOCOL.md`, `PREREG.md`, `MANIFEST.sha256`, `GATES_V5.csv`, `A1_SENS_GRID.csv`
(+ `A1_SENS_SUMMARY.csv`, `A1_GSELF.csv`, `A1_GSELF_FAIL_DIAG.json`, `A1_LEGACY_XREF.csv`,
`A1_SUMMARY.json`, `A1_*_part_*.csv`), `WORSTGROUP_V5.csv`, `WORSTGROUP_PAIRED.csv`
(TBD), `WORSTGROUP_NI.csv` (TBD), `TRADEOFF_V5.csv` (WG column TBD), `R1A_TOST.csv`,
`R1A_TOST_WG.csv` (TBD), `R1A_DOSE.csv`, `A2_G0_SUMMARY.json`, `A2_G0_FAILURES.csv`,
`A2_STOP.json`, `A3_SUMMARY.json`, `A3_ROBUSTNESS_Uair*.csv|json`,
`EXECUTION_REPORT.md`, `ERRATA_FOR_PAPER.md`.

## 5 Steps that could not be executed (TBD) and why

| step | status | reason |
|---|---|---|
| A1-G-self pass for `uair`/`proj_beta` | **failed** | 2/40 runs non-bit-exact (6.45e-09 and 1 ULP); protocol stop rule invoked; first diverging windows 0 and 37 |
| A1-G-xref pass for `proj_beta`, `proj_beta_debt` | **failed (by design of the rule)** | τ_x = 5.78e-05 … 1.29e-03 ≫ 5e-6 ⇒ "exploratory: reference not numerically stable" |
| A2-score (`WorstGroupRMSE` readings as validated scores) | **TBD** | A2-G0 failed on 18 U-Air rows; protocol stop rule |
| A2 paired contrasts / bootstrap / Wilcoxon / Holm | **TBD** | same |
| A2 non-inferiority verdicts vs `fedavg_window` and frozen `raven` | **TBD** | same |
| A2 `TRADEOFF_V5.csv` WG column | **TBD** | same |
| A3 secondary endpoint (`WorstGroupRMSE`) TOST | **TBD** | depends on A2 |
| Part B (R1b) | **not run** | A3 decision rule closes R1 as a measured null; authorization phrase absent |

## 6 Reproduction

```text
python scripts/w1_v5_a1.py --run --arms proj_beta --datasets sensorscope      # x6 parts
python scripts/w1_v5_a1.py --merge
python scripts/w1_v5_xref_legacy.py
python scripts/w1_v5_probe_gself.py
python scripts/w1_v5_a2.py --run --datasets <ds> --group <trained|frozen>     # x4 parts
python scripts/w1_v5_a2.py --merge
python scripts/w1_v5_a3.py
python scripts/w1_v5_a3_robust.py
```
All are read-only with respect to the repository outside `results_w1_ladder/round_v5/`.

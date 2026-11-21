# PREREG — endpoint screen S1 (bias, group-bias, exceedance)

```text
Mode: design + one execution prompt. This file starts no run.
Contract: CCFA-Skills/ccf-experiment-designer. Protocol, not publication prose.
Purpose: decide whether any later training on a non-RMSE endpoint is allowed.
         This round does not train and does not authorize training by itself.
Inputs: frozen checkpoints and final_metrics only.
  SensorScope / U-Air arms fedavg_window, raven:
    artifacts/e3_formal_runs_r1/runs/<ds>/<arm>/seed30001–30020/
  SensorScope / U-Air arms uniform_window, proj_beta, proj_beta_debt:
    results_w1_ladder/round_v4/train/v4/C0_frozen/<ds>/<arm>/seed30001–30020/
  City Scanner arms fedavg_window, raven (descriptive only):
    results_c1_cityscanner/round_v1/runs/cityscanner_nyc_pm25/<arm>/seed32001–32010/
  Δ_group: the run's own final_metrics.json (or CS_ACCEPTED.json). Do not recompute it.
Output: results_endpoint_screen/round_v1/ only.
Forbidden: editing src/, the manuscript, any existing results directory, artifacts/;
           training; fitting a threshold or a mean on test labels; pooling datasets;
           Holm on this screen; git commit/push.
Write PREREG.md with the rules below copied verbatim, hash it into MANIFEST.sha256,
and only then score. No threshold, contrast, or decision rule may change after the hash.
```

## 0 What this screen decides

Existing RMSE dose–response slopes have confidence intervals that contain 0. This file asks whether three other functionals of the **same** test predictions move with Δ_group. It does not create new predictions.

| endpoint | definition | datasets |
|---|---|---|
| `E_mix` | absolute bias of the μ-weighted mean, \|Σ_i w_i (ŷ_i − y_i)\| | SS, U-Air; CS descriptive |
| `E_group` | Σ_g μ_g \|b_g\|, b_g = mean residual inside deployment group g | same |
| `E_dec` | μ-weighted 0-1 loss of the exceedance 1{y > t}, t = 35 | U-Air only for the decision; CS descriptive |

SensorScope's target is `ambient_temperature` in °C. It has no PM2.5 threshold. `E_dec` is not computed there and cannot open the path.

## 1 Scoring

### 1.1 Predictions

Reuse the path in `scripts/w1_v5_a2.py`: `build_full_runner` from the run's `config_snapshot.json`, then `raven_mcs.e3.real_runner.runner._predict(runner, ds, "test")`. Weights `w` come from `_mu_weights_for_test(pred, mu)` in the same module. `mu` is the frozen target vector already used to score that run (length 220 on SensorScope, 144 on U-Air, 4 on City Scanner). A missing key or a length mismatch is a hard stop.

`E_mix` and `E_group` are computed in the same units as that run's stored `RMSE_μ` (U-Air stays in the standardized units of `final_metrics.json`).

### 1.2 Groups

`g` is `pred["groups"]`, the deployment group `h(i)`, not the four UTC blocks used for WorstGroupRMSE. A group with no test unit is dropped and `μ` is renormalized over the groups that appear. Record `n_groups_scored` and the dropped mass. If dropped mass > 0.01, stop and report; do not silently continue.

`b_g` is the unweighted mean of `ŷ − y` on test units in `g`. Then

```text
E_mix   = |Σ_g μ_g b_g|
E_group = Σ_g μ_g |b_g|
```

`E_mix` is the error of one aggregate. `E_group` does not cancel across groups. Both are required.

### 1.3 Exceedance

`t = 35` μg/m³, declared here as a constant on the instantaneous reading. It is not a 24-hour average and it is not fit to these labels.

U-Air `y` at predict time is train-standardized (`apply_train_zscore_standardization`: subtract `dataset.target_mean`, divide by `dataset.target_std`, train split only). Invert with those two frozen scalars before applying `t`. The run's `metric_scale_policy.json` field `sigma` must match `dataset.target_std` within 1e-6; otherwise `E_dec` stops. Do not estimate the mean from the test split.

```text
E_dec = Σ_i w_i · 1{ 1{ŷ_i > t} ≠ 1{y_i > t} }
```

with `w` recomputed on the physical-scale vectors. Also store the base rate `Σ_i w_i 1{y_i > t}`. If that rate is below 0.02 or above 0.98, the dataset's `E_dec` is `inapplicable`. Inapplicable does not open the path and is not a gate failure.

### 1.4 Reproduction gate, before any slope

Recompute `RMSE_μ` with `rmse_mu` on the same `(ŷ, y, w)` and compare with the stored value.

| block | rule |
|---|---|
| SensorScope, all 100 runs | \|Δ\| ≤ 1e-12 against `final_metrics.json` |
| U-Air, seeds other than {30007, 30016, 30018} | \|Δ\| ≤ 1e-12 against `final_metrics.json` |
| U-Air, those three seeds, all five arms | the checkpoint score is canonical (the known mirror/θ trigger). Record both numbers. Do not fail the gate because they differ. |
| City Scanner, 20 runs | \|Δ\| ≤ 1e-12 against `CS_ACCEPTED.json` |

One unexpected failure stops the round. No slope is interpreted. Do not fall back to retraining.

## 2 Dose–response

Per dataset, same construction as `scripts/w1_v5_a3.py` lines 131–157.

Contrasts, difference = first − second, on the 20 shared seeds:

```text
proj_beta − uniform_window
proj_beta − fedavg_window
raven − proj_beta
proj_beta_debt − proj_beta
```

Pool the four contrasts (80 paired rows). Regress the paired endpoint difference on the paired `Δ_group` difference with `np.polyfit` degree 1. Seed-cluster bootstrap, 10 000 resamples, generator seed `20261004`. Report the slope and the 2.5 / 97.5 percentiles.

A positive slope means a lower `Δ_group` (the first arm more aligned) comes with a lower endpoint. That is the only direction that can open the path.

City Scanner uses the single contrast `raven − fedavg_window`, 10 traces, and is stored in a separate file. It is not part of the decision.

## 3 Decision (apply mechanically after the gate passes)

For each of `E_mix` and `E_group`, and for `E_dec` on U-Air:

| slope 95% CI | label |
|---|---|
| contains 0 | `null` |
| entirely above 0 | `open` |
| entirely below 0 | `harm` |
| `E_dec` base rate outside [0.02, 0.98], or SS | `inapplicable` |

**The weighting path stays closed unless the same endpoint is `open` on both SensorScope and U-Air.** `E_dec` has no SensorScope twin, so it cannot open the path in this round; an U-Air `open` on `E_dec` is recorded as a candidate and still requires a separate authorization before any protocol that would train.

`harm` closes that endpoint. It is not retested to flip the sign.

Write `SCREEN_DECISION.json`:

```text
gate: pass | fail
E_mix:  {sensorscope: label, uair: label, path: closed | open}
E_group:{sensorscope: label, uair: label, path: closed | open}
E_dec:  {uair: label, path: closed}
weighting_path: closed | open
```

`weighting_path = open` only if `E_mix.path` or `E_group.path` is `open`. Anything else, including a single-dataset `open`, is `closed`.

## 4 Outputs

`PREREG.md`, `MANIFEST.sha256`, `SCREEN_RUNS.csv`, `SCREEN_DOSE.csv`, `SCREEN_DECISION.json`, `EXECUTION_REPORT.md`.

`SCREEN_RUNS.csv` columns:

```text
ds, arm, seed, source, RMSE_mu_recomputed, RMSE_mu_stored, rmse_abs_diff,
E_mix, E_group, E_dec, base_rate, n_groups_scored, dropped_mu_mass,
Delta_group, units
```

`E_dec` and `base_rate` are empty on SensorScope. `units` is `stored_RMSE_units` for `E_mix` and `E_group`, and `ug_per_m3` for `E_dec`.

`SCREEN_DOSE.csv` columns:

```text
ds, endpoint, n_obs, slope, ci_lo, ci_hi, label, in_decision
```

City Scanner rows have `in_decision = no`.

## 5 What this round must not do

- Train, or write a follow-up protocol inside the report. The decision file is the only handoff.
- Choose `t` from the test histogram, or add a second threshold after seeing `E_dec`.
- Pool SensorScope with U-Air.
- Treat a City Scanner slope, a `harm` label, or an `inapplicable` label as permission to train.
- Edit the paper's `0.027` token or the ceiling paragraph. Those are separate from this screen.

## 6 Cost

About 220 checkpoint evaluations (100 + 100 + 20), no training. The slope step is seconds.

No-fabrication status: every result cell is empty until the executor fills it. The only numbers fixed above are the declared constant `t = 35`, the bootstrap size and seed, the known U-Air trigger seeds, and the group counts taken from the manuscript's dataset table.

---

# Executor amendments (declared before the hash; no rule above is changed)

```text
A1. `_mu_weights_for_test` and `_predict` live in
    raven_mcs/e3/real_runner/runner.py, not in the module that defines
    `build_full_runner` (raven_mcs/training/window_runner.py). Import sites follow the file.
    No weight definition changes.
A2. `rmse_mu`'s third positional parameter is named `target_weights`; it is passed
    positionally. No metric definition changes.
A3. City Scanner ensemble weights. The instruction gives the arm paths and the
    frozen evidence, but no loader. The frozen evidence fixes the identity and it is
    asserted before use: CS_PHI_DECISION.json states dataset = cityscanner_nyc_pm25,
    atomic_sha256 = bcb3c07f1cbb0bad8799d5094930722f5af4cb26df2f335898953d4ea4104b55,
    n_train_units = 9343, n_test_units = 2090; the sha256 of
    data/processed/cityscanner_nyc_pm25/atomic_units.parquet equals it. The setup is
    rebuilt from CS_PHI_DECISION.mu + CS_TRAIN_SETUP.json (mu renormalized, asserted
    within 1e-12) + build_pi_target(split="test") + build_occupancy_pi_opp, with
    n_groups=4, local_steps=2, s_max=5, and the gate patch
    runner._decide_g_r = p2._skip_unused_gate, as the frozen driver did
    (CS_ACCEPTED.json: design_on=true, gate_unused=true).
    NOTE, recorded because it is a live discrepancy in the repo: the existing
    reconstruction driver scripts/run_nodesign_supplement.py loads
    data/processed/cityscanner_nyc_p2_measured_o for this block, a different dataset
    (13029 rows vs 14723; atomic_sha256 06e2953afad17b27… vs bcb3c07f1cbb0bad…).
    That driver is NOT used here. City Scanner is descriptive only and is not part of
    the decision, so if its 20-run gate does not reach 1e-12 the discrepancy is
    reported as a City-Scanner-only finding and does not stop the SensorScope/U-Air
    decision.
A4. SensorScope scaler. load_paper_dataset does not z-score SensorScope, so its
    _scaler_* attributes are absent; that is expected (its metrics are already in °C)
    and no inversion is applied there.
A5. Operational change of zero decision weight: the City Scanner gate tolerance is
    applied as an equality check that is reported, never silently relaxed.
A6. E_dec scale provenance. §1.3 requires the run's metric_scale_policy.json `sigma`
    to match dataset.target_std within 1e-6. Measured: that file exists in the
    artifacts/e3_formal_runs_r1 runs (uair sigma = 17.36325121670317 = target_std, so
    E_dec is evaluable there), but it does NOT exist anywhere in the
    results_w1_ladder/round_v4/train/v4/C0_frozen run directories, for either dataset.
    Those runs are the three trained arms (uniform_window, proj_beta, proj_beta_debt).
    Their stored RMSE_mu does reproduce exactly from their checkpoints (gate row 1/2),
    so their endpoint units are the stored ones, but the runs never declare a physical
    scale, so the §1.3 inversion cannot be licensed from their own artifacts.
    Treatment, declared before scoring: E_dec is left empty (NaN) for a run that has no
    metric_scale_policy.json, those rows drop out of the E_dec regression, and both the
    per-arm evaluable counts and the base-rate range are reported. The other two
    endpoints (E_mix, E_group) need no scale inversion and are computed for every run.
    Consequence for the decision: U-Air E_dec is evaluated on the frozen arms only. It
    cannot open the weighting path in this round regardless (§3), and if the reduced
    sample makes its CI contain 0 the label is `null`, i.e. also not open. The
    weighting_path outcome is therefore unchanged either way; the reduced sample is
    reported as a coverage limitation, not repaired by substituting a foreign sigma.
```

# PREREG — response-shift headroom (scheme 2), Stage A

```text
Mode: design + one execution prompt. This file starts no method-comparison training.
Contract: CCFA-Skills/ccf-experiment-designer. Protocol, not publication prose.
Why this round exists: the endpoint screen did not open a weighting path, and training
on those endpoints is not approved. This round asks a different question: on a label
shift the model cannot represent, does oracle reweighting move RMSE_μ at all?
Output: results_h_response_shift/round_v1/ only.
Forbidden: editing src/, the manuscript, results_h_headroom/, any other results directory, artifacts/;
           training proj_beta, uniform_window, proj_beta_debt, or frozen RAVEN;
           adding seeds or magnitudes after seeing H; git commit/push.
Stage A is read-only and is the only stage this file authorizes by itself.
Stage B trains the headroom pair only, and only after the user writes "授权 H 测量".
The current request says training is not approved, so an executor that sees only that
sentence runs Stage A and stops.
```

## 0 What is already known, and what this changes

The existing H grid (`scripts/run_h_headroom.py`) varied tilt, tail scale, a diurnal-blind backbone, and the target. Its GO rule (`H ≥ 0.005` and a positive interval lower bound) did not fire. That backbone still receives `spatial_id`. A deployment-group offset is then a function of features the model sees, so a flexible fit can absorb it.

This round adds an offset the declared model cannot write as a function of its inputs, and it leaves the frozen EventTrace, `μ`, and selection probabilities unchanged. Only the labels move.

## 1 Stage A — mass gap, no training

For each dataset in `{sensorscope, uair}` and each frozen trace `artifacts/e3_formal_runs_r1/eventtraces/<ds>/seed30001`–`seed30005`:

- `μ` is the frozen deployment-group target used by the E3 runner.
- `π_arr(g)` is the share of training atomic units in deployment group `g` (`target_group`), among units that appear in the trace.
- Record `‖π_arr − μ‖₁` per trace, plus the median over the five traces.

**Stop before Stage B** if that median is `< 0.02` on a dataset. A group offset cannot create reweighting headroom when the arrival mass already matches `μ`. Write the numbers to `MASS_GAP.csv` and set `stage_B = forbidden` for that dataset. Do not loosen 0.02 after seeing the values.

## 2 The shift (locked before any run)

Apply it in the new script after `apply_train_zscore_standardization`, so `c` is in the same units as stored `RMSE_μ`. Do not edit `src/`.

```text
groups = sorted unique target_group ids
s(g) = +1 if the group's index in that list is even, else −1
δ_raw(unit) = c * s(g(unit))
δ_bar = mean of δ_raw over train atomic units only
δ(unit) = δ_raw(unit) − δ_bar
```

Add `δ(unit)` to every split's `target_value` and to the matching client `potential_measurement`. `c = 0` gives `δ = 0` exactly. The same `δ` is used for both arms. Val and test use the train `δ_bar`; they do not recompute it.

Grid: `c ∈ {0, 0.5, 1, 2}`. No other magnitude.

## 3 The model (locked)

A script-local subclass, not a change to `CommonNDMF`:

- Start from `DiurnalBlindNDMF` in `scripts/run_h_headroom.py` (hour features zeroed, weekday and trend kept).
- Force `spatial_index` to all zeros in `forward`, so every station shares one embedding row.

The deployment group is spatial id crossed with the UTC block. The block entered through the hour features, which are zeroed. The spatial id is zeroed. Weekday and trend do not identify the group. Call this backbone `feature_blind`.

## 4 Stage B — H only, gated

Runs only where Stage A left `stage_B = allowed`, and only with the phrase `授权 H 测量`.

| item | rule |
|---|---|
| Arms | `fedavg_window` and `raven_simoracle` only |
| Traces | the frozen C0 traces (`θ = 1.25`, tail scale `0.55`, `test_share`). Do not regenerate traces. |
| Seeds | `30001`–`30005`. Not extended. |
| Cells | `c` grid × 2 datasets × 2 arms × 5 seeds = 80 runs, fewer if Stage A forbids a dataset |
| Driver | new `scripts/h_response_shift.py`, importing the frozen runner and `run_arm` pattern from `scripts/run_h_headroom.py`. New outputs only under `results_h_response_shift/round_v1/`. |
| Oracle choice | `raven_simoracle` is fixed. Do not also run the NoDesign oracle and then keep the better one. |

### 4.1 Driver check, one seed, before the grid

`c = 0`, backbone = the production full model (not `feature_blind`), SensorScope and U-Air, seed `30001`, both arms. Compare `RMSE_μ` with the existing C0 run at `results_h_headroom/` for that seed. Pass: absolute difference `≤ 1e-6`. A missing reference file is reported, not treated as a pass. A failure stops Stage B.

The `feature_blind` model at `c = 0` is not required to match that reference. It is the baseline of the grid.

### 4.2 Estimand

Paired over the five seeds,

```text
H = (RMSE_μ(fedavg_window) − RMSE_μ(raven_simoracle)) / RMSE_μ(fedavg_window)
```

Interval: the Student-t interval used by `run_h_headroom.py` (`stats.t.ppf(0.975, n−1)`). One cell per dataset × `c`.

### 4.3 Decision

| cell | GO |
|---|---|
| `c = 0`, `feature_blind` | never. Record it. If its interval lies entirely above 0 and `H ≥ 0.01`, stop: the blind model itself, not the shift, is producing headroom. |
| `c > 0` | GO only if `H ≥ 0.01` and the interval lower bound is `> 0` |

**Round decision:** `GO` if any `c > 0` cell is GO; otherwise `STOP`.

`STOP` ends the scheme. The report does not propose training `proj_beta` or uniform weights. A later comparison would need a new protocol and the phrase `授权偏移对比`, which is not part of this file.

`GO` writes the winning cells into `H_DECISION.json` and stops at the same line. Listing a cell is not permission to train the comparison.

## 5 Outputs

`PREREG.md` (this rule set, hashed in `MANIFEST.sha256` before Stage A numbers are computed), `MASS_GAP.csv`, `H_SEED_ROWS.csv`, `H_SUMMARY.csv`, `H_DECISION.json`, `EXECUTION_REPORT.md`.

`H_SUMMARY.csv` columns:

```text
ds, c, backbone, n, H, ci_lo, ci_hi, fedavg_RMSE_mu, oracle_RMSE_mu, go, note
```

`H_DECISION.json`: `{stage_A, stage_B_ran, decision: GO | STOP | BLOCKED, winning_cells: []}`.

## 6 Cost

Stage A is a pass over five traces × two datasets. Stage B, if authorized and not blocked, is 80 training runs of the existing windowed runner, two arms, five seeds, frozen traces.

No-fabrication status: every result cell is empty until the executor fills it. `c`, the sign rule, the seeds, `H ≥ 0.01`, and the mass-gap bar `0.02` are declarations, not measurements.

---

# Executor amendments (declared before the hash; no rule above is changed)

```text
A-H1  Interpreting "among units that appear in the trace". The trace records, per
      window and client, both a risk set (`risk_set_unit_ids`, the units that could have
      been delivered) and the actually observed units (`observed_unit_ids`). The arrival
      mass π_arr is a property of what ARRIVES, so the primary computation uses the union
      of `observed_unit_ids` over all windows and clients. Because the choices are not
      numerically close, the union of `risk_set_unit_ids` is computed and reported as a
      companion column (`l1_conditional_riskset`, `l1_all_groups_riskset`), and the
      primary/companion labels are fixed here, before the numbers exist. Every trace unit
      is checked against the atomic table: units not in the `split == "train"` rows are
      counted and reported (`n_observed_not_in_train_split`); they are not silently
      dropped and they do not enter π_arr.
A-H2  ‖π_arr − μ‖₁, and the treatment of groups with no trace unit. μ lives on all 220
      (SensorScope) / 144 (U-Air) deployment groups. Units in a group that never appears
      in the trace cannot be recovered by any reweighting of that trace, so the frozen
      μ cannot be matched there by construction. Two quantities are therefore recorded:
        (i) `l1_conditional` = L1 between π_arr and μ, both renormalized onto the groups
            that appear in the trace. This is the headroom that reweighting could in
            principle use, and it is the quantity the 0.02 bar is applied to;
        (ii) `l1_all_groups` = L1 with π_arr extended by zeros and μ left unnormalized,
            i.e. including the mass sitting on absent groups. Reported for completeness.
      The bar is applied to (i) because (ii) measures an unrecoverable deficit, not a
      reweighting opportunity. `mu_mass_on_absent_groups` is reported so (ii)'s excess
      over (i) is auditable. Both definitions are fixed before the numbers exist.
A-H3  μ is the same frozen target the E3 runner uses, taken via
      `production_target_bundle`, and is seed-independent; it is read once per dataset.
A-H4  Stage B is not executed in this round. The request accompanying this file does not
      contain the phrase "授权 H 测量", so §0's stop rule applies: Stage A runs and the
      round ends. `H_DECISION.json` is written with `decision = BLOCKED` and
      `stage_B_ran = false`, and H_SEED_ROWS.csv / H_SUMMARY.csv are written empty with
      their declared columns and no rows, so that their absence cannot later be read as
      a result.
```

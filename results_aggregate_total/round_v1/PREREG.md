# PREREG — scheme C: error of the deployment total

```text
Mode: design + one execution prompt. This file starts no training.
Contract: CCFA-Skills/ccf-experiment-designer. Protocol, not publication prose.
Why scheme 2 is not run: Stage A measured ‖π_arr − μ‖₁ = 0.56750 (SensorScope)
and 0.60147 (U-Air), 25–30× the 0.02 bar, with 15–23% of μ on groups that receive
no delivered unit (results_h_response_shift/round_v1/EXECUTION_REPORT.md).
Reweighting those traces cannot move that mass, and the offset grid is not executed.
This round asks whether the composition the runs already produced changes the
deployment total of the label. It does not fit a model and does not use ŷ.
Output: results_aggregate_total/round_v1/ only.
Forbidden: editing src/, the manuscript, any existing results directory, artifacts/;
           training; loading City Scanner checkpoints; citing
           results_endpoint_screen/round_v1/SCREEN_DOSE_provisional_WITHDRAWN.csv
           as a result; pooling datasets; git commit/push.
Write PREREG.md with these rules, hash it into MANIFEST.sha256, then compute.
```

## 0 Estimand

Let `m_g` be the unweighted mean of the test-split label in deployment group `g`. Let `ω̄` be the run's accumulated composition, the same vector `Δ_group = ‖ω̄ − μ‖₁` is computed from. Both `ω̄` and `μ` sum to 1, so

```text
E = |(ω̄ − μ) · m|
```

is unchanged if a constant is added to every `m_g`. It is the absolute error of the deployment total `Σ_g ω̄_g m_g` against the total under `μ`. It uses the label means, not the model's residuals. That is the difference from the screened `E_mix`.

## 1 Inputs

Datasets: SensorScope and U-Air only. City Scanner stays out. Its checkpoint replay failed the screen, and this estimand does not need that replay.

Arms, 20 seeds `30001`–`30020`:

| arm | window_metrics and stored Δ_group |
|---|---|
| `fedavg_window`, `raven` | `artifacts/e3_formal_runs_r1/runs/<ds>/<arm>/seed<seed>/` |
| `uniform_window`, `proj_beta`, `proj_beta_debt` | `results_w1_ladder/round_v4/train/v4/C0_frozen/<ds>/<arm>/seed<seed>/` |

`μ` is the frozen deployment-group vector (length 220 and 144).

## 2 Reconstruct ω̄ without training

`ω̄` is the average of `coverage_mix(M_r, α_r)` over active windows (`window_runner.py`: `omega_sum += η ω`, `scale += η`, `η` constant). Rebuild it with the replay path that already matched trained `Δ_group` to `1e-15` on the seeds checked in round v5: logged `alpha` and `active_clients` from the run's `window_metrics.json`, `M_r` from `W.build_case(ds, "R_on", "raven_wo_use", seed)`.

**Gate, before any E is interpreted.** On every run, `|‖ω̄ − μ‖₁ − stored Delta_group| ≤ 1e-8`. One failure stops the round. U-Air seeds `30007`, `30016`, `30018` use the same structural file as the other seeds: `Δ_group` is not the mirror/θ prediction quantity. They are not a special case here.

## 3 Group means

Read test-split labels from the paper dataset loader, after the train-only z-score is inverted with `dataset.target_mean` and `dataset.target_std`. Do not refit those two scalars on the test split. SensorScope is then in °C, U-Air in μg/m³.

`m_g` is the unweighted mean of those labels on test units in `g`. A group with no test unit is dropped. Renormalize `ω̄` and `μ` on the groups that remain, then compute `E`. Record the dropped `μ` mass.

**Stop** if that dropped mass is `> 0.05` on a dataset. Do not impute `m_g` from the training split.

## 4 What reweighting cannot remove

Groups with no delivered unit in the trace have `ω̄_g = 0` for every arm. Report, per trace and not as the decision:

```text
E_floor = min |(ω − μ) · m|
```

over `ω` supported on the delivered groups, `ω ≥ 0`, `Σ ω = 1`. This is one linear program per trace, solved at a fixed tolerance of `1e-10`, not by a training run. Also report `E − E_floor` per arm. The decision below uses `E`, and the report quotes the floor beside it.

## 5 Dose–response and decision

Same four contrasts as `scripts/w1_v5_a3.py`, difference = first − second, 20 seeds, contrasts pooled within a dataset (80 rows):

```text
proj_beta − uniform_window
proj_beta − fedavg_window
raven − proj_beta
proj_beta_debt − proj_beta
```

Regress the paired `E` difference on the paired `Δ_group` difference (`np.polyfit`, degree 1). Seed-cluster bootstrap, 10 000 resamples, generator seed `20261005`. A positive slope means a lower `Δ_group` comes with a lower total error.

| 95% CI | label |
|---|---|
| contains 0 | `null` |
| entirely above 0 | `open` |
| entirely below 0 | `harm` |

**The aggregate path opens only if both datasets are `open`.** One dataset, a `null`, or a `harm` leaves `aggregate_path = closed`. `harm` is not retested to flip the sign. This file does not train either way. An `open` result is permission to write a later protocol, not to start one inside the report.

## 6 Outputs

`PREREG.md`, `MANIFEST.sha256`, `TOTAL_RUNS.csv`, `TOTAL_FLOOR.csv`, `TOTAL_DOSE.csv`, `TOTAL_DECISION.json`, `EXECUTION_REPORT.md`.

`TOTAL_RUNS.csv`:

```text
ds, arm, seed, Delta_group_stored, Delta_group_rebuilt, rebuild_abs_diff,
E, E_floor, E_minus_floor, dropped_mu_mass, n_groups_scored, units
```

`units` is `degree_Celsius` or `ug_per_m3`.

`TOTAL_DECISION.json`:

```text
gate: pass | fail
sensorscope: label
uair: label
aggregate_path: closed | open
```

## 7 Cost

No training. Rebuilding `ω̄` is the replay arithmetic already used on these runs, plus one small linear program per trace (10 traces). The slope step is seconds.

No-fabrication status: every result cell is empty until filled. The mass-gap figures in the header are the Stage A measurements already written to `results_h_response_shift/round_v1/MASS_GAP.csv`. The bars `1e-8`, `0.05`, and the bootstrap seed are declarations.

---

# Executor amendments (declared before the hash; no rule above is changed)

```text
A-C1  §2's `W.build_case(ds, "R_on", "raven_wo_use", seed)` reads
      `p2_invocation_states.json` from `artifacts/e4_core_mechanism_ablation_r1/runs`.
      Measured before writing this file: that tree holds the five ablation arms x 20
      seeds x 2 datasets, and `raven_wo_use` has 20/20 non-empty state files per
      dataset. It is used exactly as §2 names it. It is NOT read from the run being
      scored: `fedavg_window` and `raven` have no `p2_invocation_states.json` under
      `artifacts/e3_formal_runs_r1/runs` at all, and the three trained arms under
      `results_w1_ladder/round_v4/train/v4/C0_frozen` have empty `{}` (3 bytes) in all
      120 cells. So the instruction's own path is the only available one, and it is
      followed.
A-C2  Windows: §2 says "over active windows". The rebuild uses, per run, the active
      windows of THAT RUN's `window_metrics.json` (`active == true`), and pairs them
      positionally with the case's `M_r`. Measured for SensorScope seed 30001: the case
      carries 97 windows and each of `raven`, `fedavg_window`, `proj_beta` has exactly
      97 active windows, so no truncation occurs there. If any run's active-window count
      differs from its case's M count the pairing is truncated to the shorter and the
      truncation is recorded per run in TOTAL_RUNS.csv (`n_windows_used`,
      `n_windows_active`, `n_windows_case_M`); a mismatch greater than 0 is reported,
      never silently absorbed.
A-C3  The declared `eta` is constant (§2 says so). The rebuild therefore accumulates
      `omega_sum += omega` over the used windows and divides by their count, which is
      `omega_bar` when `eta` is constant; `eta` is not re-read from artefacts.
A-C4  Two different published compositions exist and only one is §0's `ω̄`. The rebuild
      uses `coverage_mix(M_r, alpha_r)` with the α logged in `window_metrics.json`, i.e.
      the window-close rule's own weights. That choice is validated, not asserted: a
      pre-hash probe on SensorScope seed 30001 reproduced the stored `Delta_group` to
      |diff| = 4.4e-16 (`raven`), 2.2e-16 (`fedavg_window`) and 6.7e-16 (`proj_beta`),
      all far inside the 1e-8 gate. The probe is re-run as the gate itself on all 200
      runs.
A-C5  `E_floor` is one LP per (dataset, trace) over ω supported on the groups that have
      a delivered unit, `ω >= 0`, `Σ ω = 1`, minimising `|(ω − μ)·m|`. SOLVER: the same
      CLARABEL path the corpus uses, tolerance `1e-10` as declared. Because it is an
      absolute value, the LP is solved twice (minimise `+(ω−μ)·m` and `−(ω−μ)·m`) and
      the smaller objective is reported, with the achieved `|(ω−μ)·m|` recomputed from
      the returned ω rather than taken from the solver's objective.
A-C6  A group is dropped from the score when it has no TEST unit (§3) — that governs the
      renorm and the 0.05 stop. `E_floor` additionally restricts ω to groups with a
      DELIVERED unit. Both restrictions are applied on the intersection used for the
      renormalised vectors, and both are reported.
```

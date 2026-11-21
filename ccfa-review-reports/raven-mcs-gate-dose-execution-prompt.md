# Executable instruction: dose–response of the Design gate (does ρ predict the prediction cost of Design?)

```text
Mode: design + execution prompt.
Contract: CCFA-Skills/ccf-experiment-designer. Protocol, not publication prose.
Why this round exists: the Evidence axis needs one pre-registered link from a structural
quantity to a prediction quantity, on an effect larger than its detectable size. Changing the
weights inside a fixed active set moves RMSE_μ by ≤ 0.3 % in both supports (round_v3). The one
factor that moves it by more than the MDE is the support factor behind the Design gate
(U-Air: RMSE_μ −6.885 %, Δ_c-s +4.990 % on removing Design). The manuscript fixes that gate as
a binary rule (eq:design_gate, D_r = on ⇔ ρ_r = 0) and calls its switch point "a decision chart
fitted to this U-Air ablation row, not a general law" (main.tex L2050–2051). This round measures
the law.
Output: results_gate_dose/round_v1/ only.
Driver: new scripts/gate_dose.py. Do not edit src/.
Forbidden: editing src/, the manuscript, artifacts/, any existing results_* directory;
           choosing masked keys after any run; adding levels, seeds or arms after any run;
           changing the endpoint, the estimator, the bootstrap seed or the decision rule;
           pooling the two datasets for a decision; git commit/push.
Training starts only after the user writes "授权门控剂量". Section 2 (the m = 0 gate) is part of
that authorization; if it fails, nothing else runs.
```

## 0 What is already measured

- Within a fixed active set, oracle reweighting moves U-Air `RMSE_μ` by −0.27 % [−0.80, +0.26] (narrow support) and −0.22 % [−0.72, +0.28] (wide support), 20 seeds (`results_h_headroom/round_v3`).
- Switching the support factor alone, on the same traces and configs, moves U-Air `RMSE_μ` by −5.2 to −6.4 %, `Δ_group` by −5.9 to −9.2 %, and `Δ_c-s` by +3.1 to +4.8 %, same sign on 240/240 seed pairs (`results_regime_b_endpoints/round_v1/P0_REPORT.md`).
- The gate input on the manuscript's blocks: SensorScope `ρ = 0` (Design on), U-Air `ρ = 35.4 %` (Design off).
- `raven_wo_design` reproduces its frozen artifact bit-exactly (`results_active_set_repair/round_v1/C1_RAVEN_WO_DESIGN_REPRO.json`, seeds 30001–30002, `RMSE_μ`, `Δ_group`, `Δ_c-s` all `|Δ| = 0`).
- The decision endpoint at 35 µg/m³ is saturated on U-Air (`P2D_REPORT.md`). It is not used here.

## 1 Factor, levels and arms (locked)

**Factor.** The deployment target is restricted by masking a fraction `m` of the *positive* target keys `(client_id, opportunity_stratum)`. A masked key gets `pi_tar = 0`. This raises the realized `ρ` while leaving the EventTrace, the model, the seeds and the training configuration unchanged.

**Mask construction, fixed now.**

- Candidate keys: the keys with `pi_tar > 0` under the production test-split target, sorted lexicographically.
- Order: one permutation from `numpy.random.default_rng(20261007)`, one per dataset, drawn once.
- Level `m` masks the first `round(m · n_positive)` keys of that order. The sets are nested, so a key masked at a lower level stays masked at every higher level.
- Write the permutation, `n_positive` and each level's key list to `MASKS.json`, and put its sha256 in `MANIFEST.sha256`, before any training.

**Levels.**

| dataset | `m` levels | where the m = 0 cells come from |
|---|---|---|
| SensorScope | 0, 0.10, 0.25, 0.40 | stored artifacts, after the section 2 gate |
| U-Air | 0, 0.10, 0.20 | stored artifacts, after the section 2 gate |

SensorScope covers the region where the manuscript's gate switches (ρ from 0 upward). U-Air starts at its native 35.4 % and extends it. U-Air cannot be moved below its native ρ without inventing target mass on keys with no test units, so it has no lower level.

**One consistent target per level.** Every consumer of the target reads the same masked test split:

- the client–stratum `pi_target` passed to `run_e3_real` (`pi_target_override`);
- the group target `μ` used by `Δ_group` and by the `RMSE_μ` test weights (rebuilt from the masked test split, the same way `run_h_headroom.injected` patches `production_target_bundle`);
- the client–stratum target used by `Δ_c-s`.

Before training, list those consumers in `TARGET_WIRING.json`. Assert three things on each dataset:

- At `m = 0`, each one equals the production object (hash equality).
- At every `m`, `μ_g` equals the masked test-unit share of group `g` to 1e-12.
- At every `m`, `Σ_g μ_g = 1` and `Σ pi_tar = 1` to 1e-12.

**Arms.** `raven` (Design on) and `raven_wo_design` (Design off): the pair behind `tab:e4_ablation`'s Design row. `local_steps = 2`, the frozen configuration, no other change. No FedAvg, no oracle arm, no third arm.

**Seeds.** 30001–30020, the frozen EventTraces under `artifacts/e3_formal_runs_r1/eventtraces/<ds>/seed<seed>/`. No trace is regenerated.

**Run count.** 8 gate runs + SensorScope 3 levels × 20 seeds × 2 arms + U-Air 2 levels × 20 × 2 = 8 + 120 + 80 = **208** training runs.

## 2 Gate at m = 0 (runs first; a failure stops the round)

Run the new driver at `m = 0`, seeds 30001 and 30002, both arms, both datasets (8 runs). Compare each run with its stored artifact:

- `raven`: `artifacts/e3_formal_runs_r1/runs/<ds>/raven/seed<seed>/final_metrics.json`
- `raven_wo_design`: `artifacts/e4_core_mechanism_ablation_r1/runs/<ds>/raven_wo_design/seed<seed>/final_metrics.json`

Pass requires, on all 8 runs:

- `|ΔRMSE_μ| ≤ 1e-9`
- `|ΔΔ_group| ≤ 1e-9`
- `|ΔΔ_c-s| ≤ 1e-9`
- identical `active_clients` on every window

Any miss writes `GATE.json` with `pass: false` (a JSON boolean) and stops. There is no waiver list and no second rule. If the gate passes, the `m = 0` cells for all 20 seeds are the stored artifacts.

## 3 Scoring rule (fixed now)

- `RMSE_μ`, `Δ_group`, `Δ_c-s` and `Tail_RMSE` are read from each run's `final_metrics.json`.
- One exception: a run whose last window is inactive (`window_metrics[-1].active == false`) is scored by re-scoring its saved θ checkpoint, the paper's canonical rule (the `P2C_ADDENDUM.md` §C1 criterion).
- For runs whose last window is active, check stored against θ re-score to ≤ 1e-8. A miss stops the round.
- List every θ-scored run in `THETA_SCORED.csv`. The primary analysis includes them. A sensitivity analysis excludes them.

**Realized ρ** per (dataset, level, seed): `scripts/c1_deletion_driver.py::rho_for` semantics, imported or copied verbatim. That is, the share of U = 1 delivered risk units on non-test splits whose `(client, stratum)` has `pi_tar ≤ 0` under that level's target. ρ uses no model output. Compute it before any training and write it to `RHO.csv`. At `m = 0` it must reproduce SensorScope `0` and the U-Air value the supplemental reports (mean ≈ 0.354); a mismatch beyond 1e-6 stops the round.

## 4 Estimand, hypotheses and decision (fixed now)

Per (dataset, level, seed), the paired relative Design cost:

```text
r_e = (M_e(raven) − M_e(raven_wo_design)) / M_e(raven_wo_design),    e ∈ {RMSE_μ, Δ_group, Δ_c-s, Tail}
```

Positive `r_RMSE` means Design on predicts worse.

**H1 (primary, prediction).** On each dataset, regress `r_RMSE` on realized `ρ` across all (level, seed) cells: ordinary least squares, slope `b`. Interval: a seed-cluster bootstrap that resamples the 20 seeds with all their levels, 10 000 draws, `numpy` seed `20261007`, percentile 95 %.

| dataset | role | label |
|---|---|---|
| SensorScope | primary | `open` if CI lower bound > 0; `harm` if CI upper bound < 0; else `null` |
| U-Air | replication over high ρ | the same three labels |

`gate_law = supported` if and only if SensorScope is `open` and U-Air is not `harm`. Any other combination is `not supported`. Do not retest a `harm`. Do not add levels or seeds to an `null`.

**H2 (tested only if H1 supports the law).** At SensorScope `m = 0`, non-inferiority of Design on: the upper 95 % Student-t bound of `r_RMSE` (n = 20) must be below `+0.5 %`. This is the gate's claim that Design costs nothing when `ρ = 0`.

**Descriptive, no decision.** The same slope and interval for `r_Δc-s`, `r_Δgroup` and `r_Tail`, and the per-level means with Student-t intervals. Also the crossover `ρ* = −a / b` from the H1 fit, with its bootstrap interval, reported only when H1 is `open`. `ρ*` is a fitted number, not a new gate.

## 5 What each outcome licenses

- **`gate_law = supported`.** The paper may state that a pre-outcome structural statistic predicts the sign and size of the prediction cost of the alignment factor, with the measured slope and interval, on these two blocks. It may not say that alignment improves prediction.
- **SensorScope `null`.** Design cost does not track ρ at this size. The binary gate stays a rule fitted to U-Air, as the manuscript already says.
- **`harm`.** Reported as measured. It contradicts the gate's direction and goes into the limitations section.
- **Any outcome.** No change to `main.tex` from this file. A writing pass needs a separate request.

## 6 Result tables

`results_gate_dose/round_v1/tables/DOSE_CELLS.csv`: one row per (dataset, level, seed). Columns: `rho`, the four endpoints for each arm, the four `r_e`, `theta_scored`, source path.

`tables/DOSE_SUMMARY.csv`:

| dataset | level m | mean ρ | n | r_RMSE mean [95 % CI] | r_Δc-s | r_Δgroup | r_Tail |
|---|---|---|---|---|---|---|---|
| SensorScope | 0 / 0.10 / 0.25 / 0.40 | TBD | 20 | TBD | TBD | TBD | TBD |
| U-Air | 0 / 0.10 / 0.20 | TBD | 20 | TBD | TBD | TBD | TBD |

`tables/DOSE_SLOPES.csv`: dataset × endpoint, slope `b`, intercept `a`, bootstrap CI, label (H1 rows only for `RMSE_μ`), primary and θ-excluded sensitivity.

`DOSE_DECISION.json`: gate pass, H1 labels, `gate_law`, H2 result or `not_tested`, `ρ*` or `null`.

## 7 Execution order

| Priority | Step | Cost | Stop |
|---|---|---|---|
| P0 | `MASKS.json`, `TARGET_WIRING.json`, `RHO.csv`, `MANIFEST.sha256` | no training | any wiring assertion, or the m = 0 ρ check, fails |
| P1 | gate, m = 0, seeds 30001–30002, both arms, both datasets | 8 trains | any of the four gate checks fails |
| P2 | SensorScope m ∈ {0.10, 0.25, 0.40} and U-Air m ∈ {0.10, 0.20}, 20 seeds, two arms | 200 trains | a θ re-score check fails, or a run is missing |
| P3 | tables, H1, H2 if licensed, `DOSE_DECISION.json` | none | `INCOMPLETE` if any cell is missing |

## 8 Known limits, stated before the run

- A level changes ρ and the deployment target together. Both arms see the same target within a level, so `r_e` is a within-level contrast. The slope is across targets that differ only by which keys are masked.
- Masked keys are random, not structured. A structured mask, such as a whole time block, would be a different experiment and is not part of this one.
- Two datasets, no City Scanner. City Scanner's target is a four-region lookup with every region positive, so its ρ cannot be dosed the same way.

## 9 No-fabrication status

Every number in sections 4–6 is `TBD` until the driver writes it. The section 0 values are read from the named files. No result is claimed here.

Next owner after `DOSE_DECISION.json`: report the labels. `ccf-paper-writer` only on a later request, and only for wording section 5 licenses.

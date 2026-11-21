# HANDOFF: INT-R round v2 (recalibrate occupancy, then audit, then train)

Paste this to the executor AI:

```text
You are the INT-R-E3 round_v2 executor for repo C:\Cursor\raven.mcs.
Read this entire file and post_review/B_intermittent_protocol_R/PROTOCOL_V2.json.
Execute §10 in order. Do not invent numbers. Do not edit the manuscript.
Do not overwrite round_v1 or always-on formal traces.
Do not use Y / RMSE / residuals / seeds 30001–30020 / seed 31001 to pick (alpha, beta).
If occupancy gates fail, stop. If the calibrator ladder is exhausted, stop and ask the human.
Python: C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe
```

This round exists because **round_v1 failed INT-R-OCC-1** (U-Air seed 30001 mean active fraction 0.31875). v1 evidence stays frozen under `results_int_r/round_v1/` and `artifacts/e3_int_r_eventtraces/`. You are **not** allowed to fit occupancy to seed 30001. You add a **dummy-seed stability screen** that uses only occupancy draws.

Parent contract (unchanged): `HANDOFF_EXECUTOR.md`. If this file and the parent disagree on occupancy calibration, **this file wins**. If they disagree on SCD, Gate, datasets, methods, or claim ceiling, **the parent wins**.

```text
Experiment ID: INT-R-E3
Round directory: results_int_r/round_v2/
Trace root: artifacts/e3_int_r_eventtraces_v2/
Python: C:\Cursor\raven.mcs\.venv_new\Scripts\python.exe
Paper method: support-conditional Design (SCD), NOT coverage Gate
```

---

## 0. Role and stop conditions

You implement calibrator v2, regenerate INT-R traces into a **new** directory, re-run occupancy gates, train the mandatory matrix if gates pass, write CSVs, and stop.

Stop and ask the human if any of the following happens:

- You cannot generate traces without using labels, RMSE, or residuals.
- Calibrator v2 exhausts the stability ladder in §3.5 (no feasible pair).
- You would need to overlay T-Drive GPS onto SensorScope/U-Air stations.
- You would need to change SCD using INT-R RMSE.
- INT-R-OCC-1..5 fail on the new traces (do not waive; do not loosen the ladder after seeing 30001).
- GPU/CPU budget is insufficient for the mandatory matrix. Occupancy+audit still counts; stop after writing the audit.

Do not start SAG / certificate / T-Drive ranking / NSW-Traffic E3. Do not edit `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`. Do not `git push`. Do not commit unless the human asks.

### Forbidden seed use (hard)

| Seed family | Allowed for |
| --- | --- |
| 29999 | T-Drive scalar match only (SensorScope K=8, 100 windows), same as v1 |
| 28001–28020 | Stability screen only (occupancy draws; both horizons) |
| 30001–30020 | Generate + audit + train **after** (alpha, beta) is frozen |
| 31001 | Smoke only |

Do not put `30001` in `occupancy.py`. Grep gate: occupancy calibrator source must not contain `30001`, `rmse`, `y_i`, `test_error`.

---

## 1. Why v1 failed (context; not a fitting target)

v1 calibrated a two-state Markov on **one** SensorScope draw (seed 29999) and picked a very sticky pair (`alpha≈0.939`, `beta≈0.960`). Process mean active fraction is near 0.40, but K=8 and short horizons (100 / 80) make single-seed \(\hat\rho\) noisy. OCC-3 (TV mismatch) passed. Training did not start. Do not reuse v1 traces for v2 ranking.

---

## 2. Frozen inputs (do not retune from RMSE)

Copy from the parent brief / paper. Do not change them to improve RMSE or to make seed 30001 pass.

```text
E3/E4 seeds: 30001 .. 30020
Canary: 31001
Calibration seed: 29999
Stability seeds: 28001 .. 28020
Datasets: sensorscope, uair
K logical FL clients: 8
Windows: SensorScope 100, U-Air 80
  (from artifacts/e3_multidataset_protocol_closure_r1/E3_DATASET_HORIZON_FREEZE.json
   via load_horizon; do not hardcode a different horizon)
mean_observation_rate: 0.35
s_max: 5
theta_align: 1.25, tail blocks {2, 3}
P2 lambdas: lambda_group=1.0, lambda_beta=1.0, lambda_v=0.1, lambda_s=0.1, alpha_max=0.5, ESS=3.0
TARGET_LAW_RULE_V1 hash: 86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07
```

**SCD freeze (paper, not Gate):**

```text
SensorScope SCD: method key raven (Design ON)
U-Air SCD: method key raven_wo_design (Design OFF)
U-Air full Design diagnostic: method key raven
Gate_t / aggregate_coverage / Design_t := Gate_t: OFF for every INT-R ranking run
```

Do not re-choose SCD after seeing INT-R RMSE.

**RNG (unchanged from v1, already implemented):**

```text
occupancy_rng(dataset, seed) = default_rng(seed + 10007 * dataset_id + 17)
dataset_id: sensorscope=0, uair=1
r3 rng: default_rng(seed + 13)
Scheme: always advance r3 through every client, then drop the event row when A=0
```

Existing code: `src/raven_mcs/e3/int_r/occupancy.py`, `src/raven_mcs/e3/real_runner/generator_r3.py`. Unit tests: `tests/unit/test_int_r_occupancy.py`. Keep the always-advance scheme. Do not switch to a new RNG scheme unless those tests break.

---

## 3. Calibrator v2 (the only scientific change)

v1 `calibrate_markov` stays as a reference. Add `calibrate_markov_v2` (or a `version="v2"` flag). Do not delete v1.

Public scalar targets (unchanged):

```text
rho_star = 0.425
B_star   = 0.38
rho_window_cal = [0.40, 0.45]     # seed 29999 SensorScope only
B_window_cal   = [0.30, 0.45]
occ1_window    = [0.35, 0.50]     # stability screen and later OCC-1
```

Burstiness: same as v1 / G3. Pooled gaps, `ddof=1`, \(B=(\sigma-\mu)/(\sigma+\mu)\).

### 3.1 Step A — T-Drive scalar match (same as v1)

Grid: `alpha, beta = linspace(0.55, 0.98, 22)`.

For each cell, simulate occupancy with the **existing v1 cell_seed formula** (do not change it):

```text
cell_seed = 29999
  + (int(round(alpha * 1e6)) % 10007)
  + 97 * (int(round(beta * 1e6)) % 10007)
A = simulate_occupancy(n_clients=8, n_windows=100, spec, rng=default_rng(cell_seed))
```

This is SensorScope geometry only. No U-Air fit. No atomic \(Y\).

Keep the cell if \(\hat\rho \in [0.40, 0.45]\). Among those, mark `both=true` if \(\hat B \in [0.30, 0.45]\) and finite. Score (same as v1):

```text
score = (rho_hat - 0.425)^2 + 0.25 * (B_hat - 0.38)^2
```

If no cell has \(\hat\rho\) in window: stop and ask the human (same as v1). Do not Bernoulli unless the human says so.

### 3.2 Step B — stability screen (new; occupancy only)

For every rho-feasible cell from Step A, evaluate 40 occupancy draws:

```text
for seed in 28001 .. 28020:
  for (dataset, T) in [("sensorscope", 100), ("uair", 80)]:
      A = simulate_occupancy(
            n_clients=8,
            n_windows=T,
            spec,
            rng=occupancy_rng(dataset, seed),   # MUST be occupancy_rng, not cell_seed
          )
      rho = A.mean()
      hit if rho in [0.35, 0.50]
```

`n_checks = 40`. Record `hits`, `mean_rho`, `std_rho` (`ddof=1` over the 40 rhos).

This uses U-Air **horizon length** and occupancy RNG dataset id. It does **not** use U-Air labels, stations beyond K=8, or E3 seeds.

### 3.3 Step C — ladder (pre-registered; do not skip)

Apply the **tightest** level that has at least one rho-feasible cell. Do not jump to a looser level because you remember v1 seed 30001.

| Level | Rule |
| --- | --- |
| L40 | `hits == 40` |
| L36 | `hits >= 36` |
| L32 | `hits >= 32` |
| L_mean | dummy `mean_rho ∈ [0.40, 0.45]` and `std_rho <= 0.06` |

Procedure:

1. If any **both=true** cell passes L40, restrict to those cells. Else if any rho-feasible cell passes L40, restrict to those (`burstiness_miss` may be true).
2. Else repeat (1) at L36, then L32, then L_mean.
3. If still empty on the 22-point grid: **once**, expand the grid to `linspace(0.55, 0.98, 44)` and repeat Steps A–C from scratch. Record `grid_expanded=true`.
4. If still empty: **stop**. Do not use Bernoulli. Do not peek at 30001–30020 occupancy. Ask the human.

### 3.4 Step D — pick one pair

Among cells that survive the winning level:

1. Prefer `both=true` over rho-only.
2. Minimize Step A `score` (seed-29999 SensorScope).
3. If tied, minimize dummy `std_rho`.
4. If still tied, take the smaller `alpha`, then smaller `beta`.

Freeze **one** `(alpha, beta, rho0=0.425)`. Reuse it on both datasets. Do not fit a second pair on U-Air.

Write `results_int_r/round_v2/INT_R_OCCUPANCY_SPEC.json` with at least:

```text
family, alpha, beta, rho0, burstiness_miss,
calibrator_version=v2_stability_screen,
stability_level, stability_hits, stability_n_checks=40,
stability_mean_rho, stability_std_rho, grid_expanded,
calibration_seed=29999, stability_seeds=28001..28020,
calibration_replay (seed 29999 SensorScope occupancy_rng replay, same as v1 stage_calibrate),
git_commit
```

Also write `INT_R_CALIBRATION_GRID.csv` (one row per rho-feasible cell: alpha, beta, rho_cal, B_cal, score, hits, mean_rho, std_rho, both). This is occupancy-only. It is not a ranking table.

### 3.5 What you must not do

- Do not reject a pair because v1 U-Air 30001 was 0.31875.
- Do not include 30001–30020 in the 40 checks.
- Do not retune after generate/audit. If OCC-1 fails on the new traces, stop.
- Do not target T-Drive cell coverage 0.547.

---

## 4. Paths (do not mix rounds)

```text
v1 keep:     results_int_r/round_v1/
v1 keep:     artifacts/e3_int_r_eventtraces/
v2 write:    results_int_r/round_v2/
v2 traces:   artifacts/e3_int_r_eventtraces_v2/{dataset}/seed{seed}/training_eventtrace/
always-on:   artifacts/e3_formal_runs_r1/   (do not touch)
```

Trace layout must match v1 **working** layout (`training_eventtrace/`), not the unused `complete_aligned_int_r/` path in the parent brief.

Script: add `scripts/run_int_r_v2.py` by copying `scripts/run_int_r_v1.py` and pointing `OUT` / `TRACE_ROOT` at v2. Keep stages: `calibrate|smoke|generate|audit|train`. Generate must use `--force` equivalent so it cannot reuse v1 parquet files (different root already prevents that; still do not copy v1 traces).

**Bug to keep fixed:** `load_event_trace` returns `(EventTrace, identity)`. Unpack it. v1 audit crashed until this was fixed.

---

## 5. Smoke (not evidence)

Reuse v1 smoke logic against calibrator v2 / generator. Write `results_int_r/round_v2/INT_R_SMOKE.json`. Do not put smoke numbers in ranking tables.

Add unit tests:

- Stability seeds are exactly 28001–28020.
- `calibrate_markov_v2` / occupancy module text has no `30001`, `rmse`, `y_i`, `test_error`.
- Forced `A=1` still matches always-on r3 (existing test).
- A dummy spec with low persistence has higher dummy hit-rate than v1’s sticky pair on seeds 28001–28003 (qualitative; do not hardcode v1 alpha). Optional; skip if flaky.

---

## 6. Generate

```text
python scripts/run_int_r_v2.py --stage generate --start-seed 30001 --end-seed 30020
```

Both datasets. Shared EventTrace per `(dataset, seed)`. Occupancy spec from the frozen v2 JSON. Do not overwrite v1.

---

## 7. Occupancy audit (before any training)

Same six cells as v1: `{sensorscope, uair} × {30001, 30010, 30020}`.

Write `results_int_r/round_v2/tables/INT_R_OCC.csv` and `INT_R_OCC_GATES.json`.

Gates (unchanged thresholds):

```text
INT-R-OCC-1: mean active fraction in [0.35, 0.50] on both datasets, seed 30001
INT-R-OCC-2: burstiness > 0 on both datasets, seed 30001 (Markov required in this round)
INT-R-OCC-3: TV(pi_opp, mu) > 0.05 on both datasets, seed 30001
INT-R-OCC-4: no Y/RMSE in occupancy code path
INT-R-OCC-5: A=0 client-windows have no event rows
```

TV uses A=1 risk sets, train units only, four UTC blocks, public \(\mu\). Copy v1 `_tv_opp_mu` (with the tuple unpack fix).

If any gate fails: **stop**. Do not start `--stage train`. Do not lower OCC-1. Do not go back to a looser ladder level.

Optional diagnostic (not a gate): `INT_R_OCC_ALL_SEEDS.csv` for 30001–30020 after freeze. Do not use it to pick a new `(alpha, beta)`.

---

## 8. Train (only if all five gates pass)

Mandatory matrix, same traces:

| Paper name | Key | Where |
| --- | --- | --- |
| FedAvg-Window | `fedavg_window` | SS + UA |
| TwoStage-Hajek | `twostage_hajek` | SS + UA |
| FedAU-Window | `fedau_window` | SS + UA |
| ObsUse-Window | `obsuse_window` | SS + UA |
| RAVEN-MCS (SCD) | `raven` on SS, `raven_wo_design` on UA | both |
| RAVEN full Design | `raven` | U-Air diagnostic only |
| Design-off | `raven_wo_design` | SensorScope E4 only |

Seeds 30001–30020. `run_e3_real(..., local_steps=2)`. Runner currently uses `device="cpu"`. Resume via `INT_R_ACCEPTED.json` markers under `results_int_r/round_v2/runs/`.

Do not add FedCure. Do not rank Traffic or T-Drive. Do not turn Gate on.

Priority if budget is cut: SS 20 seeds (FedAvg, FedAU, ObsUse, SCD) → U-Air same four + SCD → remaining methods (TwoStage, UA full Design, SS Design-off). Write a partial ledger; leave unfinished table cells as `TBD`.

### Metrics

Per run store at least: `RMSE_mu`, `Delta_group`, `Delta_c_s`, `Head_RMSE`, `Tail_RMSE`, **`WorstGroupRMSE`**.

`run_e3_real` may not emit WorstGroupRMSE. Compute it as in G2: max of four UTC-block test RMSEs, \(\mu\)-weighted, same `h(i)` as paper Table II. Recipe: `post_review/G2_external_baselines/run_g2.py` (loop `g in range(4)`, `_wrmse`, then `max`). Do not substitute Head/Tail for WorstGroup. Do not invent.

After all runs, write:

```text
tables/INT_R_E3.csv
  dataset, method, rmse_mu_mean, rmse_mu_std, worstgroup_mean, worstgroup_std,
  delta_group_mean, delta_group_std, delta_cs_mean, delta_cs_std

tables/INT_R_E4_DESIGN.csv
  dataset, removed, delta_group_pct, delta_cs_pct, rmse_mu_pct, tail_rmse_pct, holm_star_flags
```

`mean ± std` over 20 paired seeds. Use `TBD` only for unfinished cells. Never invent a finished number. Do not copy always-on Table II into INT-R-E3.

Optional: `INT_R_VS_ALWAYS_ON.csv` by **parsing** the sealed paper Table II CSV (do not retype from memory):

```text
RAVEN_MCS_FINAL_FIGURE_TABLE_PAPER_SPECIFICATION_SEAL_R1/05_PROVENANCE/FINAL_TABLE_SOURCES/TABLE_II_MAIN_EFFECTIVENESS.csv
```

Pre-registered tests (report; do not open extra looks): parent brief §6. Holm vs FedAU/ObsUse is reported, not a unique-win claim unless both Holm-adjusted \(p<0.05\) **and** the paper’s 0.5% rule.

---

## 9. Manifest and log

`results_int_r/round_v2/INT_R_MANIFEST.json`:

```text
occupancy_family, alpha, beta, rho_star, B_star,
calibrator_version, stability_level, calibration_seed, stability_seeds,
rng_scheme=always_advance_r3_rng_then_drop_A0_rows,
scd_rule, gate_used=false, generator_version, git_commit
```

`results_int_r/round_v2/EXECUTION_LOG.md`: commands, git hash, gate JSON, failures, wall time. No manuscript edits. No claim that SensorScope/U-Air contain mobile clients.

---

## 10. Execution order

1. Implement `calibrate_markov_v2` + v2 script paths + unit tests. Keep v1 files intact.
2. `--stage calibrate`. Freeze spec. If ladder exhausted, stop.
3. `--stage smoke`.
4. `--stage generate` seeds 30001–30020 both datasets.
5. `--stage audit`. If gates fail, stop.
6. `--stage train` mandatory matrix.
7. Write CSVs + manifest + EXECUTION_LOG. Stop.

---

## 11. Claim ceiling

Unchanged from parent §11. INT-R is robustness unless the human promotes it. Do not call occupancy “T-Drive \(R\)” or real mobility. If ranking disagrees with always-on, report it. Do not hide it. Do not retune occupancy after RMSE.

---

## 12. Integrity

- Round v1 remains the failed-OCC-1 record. Do not delete it.
- Do not fill INT-R-E3 until those runs finish.
- Do not reuse always-on or v1 RMSE (v1 has none).
- Do not change seeds, \(\mu\), or SCD after seeing metrics.
- Python 3.11 from `.venv_new`.

```text
No-fabrication status: this brief contains no v2 experimental results.
v1 OCC-1 failure is already recorded in results_int_r/round_v1/; do not treat it as a calibration target.
```

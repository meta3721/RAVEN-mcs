# INT-R-E3 execution log (round_v2)

Occupancy calibrator v2 froze a less sticky Markov pair. Audit gates INT-R-OCC-1..5 passed. Training finished (240/240). Manuscript not edited.

## Environment

- Repo: `C:\Cursor\raven.mcs`
- Python: `.venv_new\Scripts\python.exe`
- Git HEAD: `5c4243761c8c5999bb9ec08a25969bef4ad0cdd6`
- Results: `results_int_r/round_v2/`
- Traces: `artifacts/e3_int_r_eventtraces_v2/`
- v1 left untouched: `results_int_r/round_v1/`, `artifacts/e3_int_r_eventtraces/`
- Paper method: SCD (SensorScope Design ON / U-Air Design OFF). Gate unused.

## Commands

1. `pytest tests/unit/test_int_r_occupancy.py` — 7 passed
2. `python scripts/run_int_r_v2.py --stage calibrate`
3. `python scripts/run_int_r_v2.py --stage smoke`
4. `python scripts/run_int_r_v2.py --stage generate --start-seed 30001 --end-seed 30020`
5. `python scripts/run_int_r_v2.py --stage audit` — all five gates pass
6. `python scripts/run_int_r_v2.py --stage train` — 240 runs, exit 0, wall ~56 min
7. `python scripts/run_int_r_v2.py --stage recompute_worst` — four-UTC WorstGroupRMSE from checkpoints (no retrain)

## Frozen occupancy (calibrator v2)

- family: `two_state_markov`
- alpha ≈ 0.77524, beta ≈ 0.83667, rho0 = 0.425
- calibrator_version: `v2_stability_screen`
- stability_level: **L40** (40/40 dummy draws in [0.35, 0.50])
- stability_mean_rho: 0.41989, stability_std_rho: 0.03021
- grid_expanded: false
- burstiness_miss: **true** (L40 had no both=true cell; rho-feasible L40 pair kept; do not claim T-Drive burstiness matching)
- calibration replay (seed 29999 SensorScope occupancy_rng): mean active 0.44, pooled burstiness 0.12793
- RNG: always advance r3 rng, then drop A=0 rows

## Smoke

See `INT_R_SMOKE.json`. Forced A=1 matches always-on. Inactive windows have no event rows. Occupancy source has no rmse / Y_i / test_error and no `30001` literal.

## Audit (seed 30001 unless noted)

| Gate | Result | Note |
| --- | --- | --- |
| INT-R-OCC-1 | PASS | SS 0.4525, U-Air 0.4953, both in [0.35, 0.50] |
| INT-R-OCC-2 | PASS | burstiness > 0 on both datasets |
| INT-R-OCC-3 | PASS | TV 0.309 (SS) and 0.225 (UA), both > 0.05 |
| INT-R-OCC-4 | PASS | occupancy.py grep |
| INT-R-OCC-5 | PASS | A=0 client-windows have no event rows |

Official six-cell table: `tables/INT_R_OCC.csv`.

## Train

- Schedule: 240 cells. Ledger `n=240`. Status `REAL_PATH_EXECUTED`.
- Tables: `tables/INT_R_E3.csv`, `tables/INT_R_E4_DESIGN.csv`
- Manifest: `INT_R_MANIFEST.json` (`gate_used=false`)

First train pass stored WorstGroupRMSE from `pred["groups"]` ids 0–3, which are fine spatial×block labels, not the paper four UTC blocks. That column was recomputed from the same checkpoints using `RepeatableTimeOfDayMapper` (G2 / Table II). RMSE_μ, Δ_group, Δ_c-s were not changed.

Solver warnings (`cvxpy` / CLARABEL “Solution may be inaccurate”) appeared on many runs. Runs were still accepted with finite metrics. Recorded, not cleaned after seeing RMSE.

## Integrity

- Did not retune occupancy after RMSE.
- Did not change SCD.
- Did not overwrite v1 or always-on formal traces.
- Did not edit `main.tex`.
- INT-R remains a robustness block unless the human promotes it.

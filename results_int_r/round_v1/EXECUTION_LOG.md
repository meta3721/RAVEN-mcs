# INT-R-E3 execution log (round_v1)

Stopped before training. Occupancy gate INT-R-OCC-1 failed. No RMSE numbers were produced. Manuscript not edited.

## Environment

- Repo: `C:\Cursor\raven.mcs`
- Python: `.venv_new\Scripts\python.exe`
- Git HEAD at freeze/calibrate: `5c4243761c8c5999bb9ec08a25969bef4ad0cdd6`
- Traces: `artifacts/e3_int_r_eventtraces/{sensorscope,uair}/seed30001..30020/`
- Results: `results_int_r/round_v1/`
- Paper method wiring: SCD (SensorScope Design ON / U-Air Design OFF). Gate unused.

## Commands

1. Occupancy unit tests (passed earlier): `pytest tests/unit/test_int_r_occupancy.py`
2. Calibrate: `python scripts/run_int_r_v1.py --stage calibrate`
3. Smoke: `python scripts/run_int_r_v1.py --stage smoke`
4. Generate: `python scripts/run_int_r_v1.py --stage generate --start-seed 30001 --end-seed 30020`
5. Audit: `python scripts/run_int_r_v1.py --stage audit` (failed INT-R-OCC-1)
6. Train: **not started**

## Frozen occupancy (seed 29999, SensorScope K=8, 100 windows)

- family: `two_state_markov`
- alpha ≈ 0.93905, beta ≈ 0.95952, rho0 = 0.425
- calibration replay: mean active 0.41125, pooled burstiness 0.43716
- burstiness_miss: false
- RNG: always advance r3 rng, then drop A=0 rows; occupancy rng = `seed + 10007*dataset_id + 17`

## Smoke

See `INT_R_SMOKE.json`. Forced A=1 matches always-on after dropping `occupancy_A`. Inactive windows have no event rows. Occupancy source has no rmse / Y_i / test_error.

## Audit gates (seed 30001 unless noted)

| Gate | Result | Note |
| --- | --- | --- |
| INT-R-OCC-1 | FAIL | U-Air seed 30001 mean active fraction = 0.31875, below [0.35, 0.50]. SensorScope 30001 = 0.4075 (pass). |
| INT-R-OCC-2 | PASS | burstiness > 0 on both datasets, seed 30001 |
| INT-R-OCC-3 | PASS | TV(pi_opp, mu) = 0.282 (SS) and 0.253 (UA), both > 0.05 |
| INT-R-OCC-4 | PASS | occupancy.py grep |
| INT-R-OCC-5 | PASS | A=0 client-windows have no event rows |

Official six-cell table: `tables/INT_R_OCC.csv`.
All 40 seeds (diagnostic only, not a gate): `tables/INT_R_OCC_ALL_SEEDS.csv`.

Ensemble occupancy (not used to retune):

- SensorScope 20 seeds: mean 0.3988, std 0.0550, 15/20 in [0.35, 0.50]
- U-Air 20 seeds: mean 0.4044, std 0.0769, 11/20 in [0.35, 0.50]

Cause: sticky Markov (high alpha/beta) plus K=8 and short horizons (100 / 80 windows) gives large seed-level variance around a process mean near 0.40. This is not a label leak and not a TV collapse.

## Stop rule applied

HANDOFF: do not train if occupancy gates fail. INT-R-OCC-3 (mismatch destruction) is not the failing gate. INT-R-OCC-1 is.

Did not retune (alpha, beta) after seeing seed 30001. Did not change SCD. Did not overlay T-Drive GPS. Did not edit `main.tex`.

## Human decision needed

1. Waive INT-R-OCC-1 on existing traces and start `--stage train` (ensemble mean rho is on target; TV mismatch intact).
2. Amend the calibrator with a multi-draw occupancy constraint that does not use Y/RMSE, regenerate traces 30001–30020, re-audit, then train.
3. Stop Option B here.

Do not invent INT-R-E3 numbers until a train stage finishes.

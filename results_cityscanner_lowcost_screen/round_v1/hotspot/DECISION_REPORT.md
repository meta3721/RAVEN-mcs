# City Scanner hotspot screen decision

- Written: 2026-10-19T00:39:19.820145+00:00
- Driver: `results_cityscanner_lowcost_screen/round_v1/screen_cityscanner.py`
- Python: `.venv_new/Scripts/python.exe`
- Experiment: hotspot. The target-shift scheme is outside this plan.

## Commands

From `C:/Cursor/raven.mcs`:

1. `audit --experiment hotspot`
2. `predict --canary`
3. `predict --remaining`
4. `baselines`
5. `select-baseline --experiment hotspot`
6. `hotspot --split test`
7. `report --experiment hotspot`

Protocol status: `NO_PROTOCOL_PASS`.

`P2_VS_PROJECTION_UNRESOLVED` remains in force.

## Block results

### visit

- Screen status: `FAIL_SCREEN`
- Failed gates: practical_line, lower_bound, beats_all_six
- Fail description: small gain
- Validation-selected b_H: `Delivered-SpatialMean`
- Test J RAVEN: 0.0307499
- Test J b_H: 0.0322678
- D: 0.00151793
- G: 0.0470417
- Capture H RAVEN: 0.253075
- Capture H b_H: 0.227933
- Delta H: 0.0251425
- RMSE cost: -0.189364
- WorstGroupRMSE cost: -0.41642
- 3-day 95% interval for D: -0.00124487 to 0.00457178
- 3-day one-sided 98.75% lower bound: -0.00162029
- 7-day median D: 0.00148607
- 7-day 95% interval: -0.00122714 to 0.00432516
- Calendar days: 30; qualified dates: 24
- Uniform-random reference J: 0.0304293
- RAVEN has the smaller test J than: Delivered-SpatialMean, Delivered-CellBlockMean
- These candidates have the smaller test J: fedavg_window, twostage_hajek, fedau_window, obsuse_window, Fixed-Ensemble

### measured-O

- Screen status: `FAIL_SCREEN`
- Failed gates: practical_line, lower_bound, capture, beats_all_six
- Fail description: small gain
- Validation-selected b_H: `Delivered-CellBlockMean`
- Test J RAVEN: 0.149936
- Test J b_H: 0.156476
- D: 0.00654
- G: 0.0417954
- Capture H RAVEN: 0.229566
- Capture H b_H: 0.252137
- Delta H: -0.0225709
- RMSE cost: -0.233832
- WorstGroupRMSE cost: -0.272414
- 3-day 95% interval for D: -0.0177403 to 0.0323555
- 3-day one-sided 98.75% lower bound: -0.0214534
- 7-day median D: 0.00635318
- 7-day 95% interval: -0.0171547 to 0.0285806
- Calendar days: 25; qualified dates: 20
- Uniform-random reference J: 0.155683
- RAVEN has the smaller test J than: fedau_window, obsuse_window, Delivered-CellBlockMean
- These candidates have the smaller test J: fedavg_window, twostage_hajek, Delivered-SpatialMean, Fixed-Ensemble

## Five questions

The gain does not enter an inspection decision. visit is FAIL_SCREEN; measured-O is FAIL_SCREEN. `PASS_SCREEN` is the status that would mark a block as worth an independent data check.

On visit, the validation-selected control is `Delivered-SpatialMean`. Test D is 0.00151793 training standard deviations and G is 0.0470417. RAVEN has the smaller J than Delivered-SpatialMean, Delivered-CellBlockMean. The candidates with the smaller J are fedavg_window, twostage_hajek, fedau_window, obsuse_window, Fixed-Ensemble.
On measured-O, the validation-selected control is `Delivered-CellBlockMean`. Test D is 0.00654 training standard deviations and G is 0.0417954. RAVEN has the smaller J than fedau_window, obsuse_window, Delivered-CellBlockMean. The candidates with the smaller J are fedavg_window, twostage_hajek, Delivered-SpatialMean, Fixed-Ensemble.

The prediction cost is the full-test RMSE_mu ratio minus one, and the same form for WorstGroupRMSE. The block results above give both costs against b_H. A negative cost means RAVEN has the smaller full-test error. The frozen guard is 5 percent on each cost.

The 10 percent and 30 percent budgets are in `hotspot/SUMMARY.csv`. They do not replace the 20 percent decision.

The scores use the existing City Scanner test splits. Those splits have already been used in this project, so this screen is an old-test exploration. The two blocks can share raw sampling.

The same-protocol projection comparison remains open: `P2_VS_PROJECTION_UNRESOLVED`.

This round does not write the result into the paper and does not start training.

## Figures

- `hotspot/fig_paired_j_diff.png`
- `hotspot/fig_budget_jh.png`

## Stage timing

- audit --experiment hotspot ended 2026-10-18T15:56:27.499084+00:00 cpu 0.01562s wall 0.03058s
- predict --canary ended 2026-10-18T15:56:33.477113+00:00 cpu 0s wall 1.647s
- predict --canary ended 2026-10-19T00:34:33.593972+00:00 cpu 0.875s wall 0.9892s
- predict --canary ended 2026-10-19T00:34:35.863569+00:00 cpu 0.625s wall 0.6417s
- predict --canary ended 2026-10-19T00:34:36.377856+00:00 cpu 0.1094s wall 0.1321s
- predict --remaining ended 2026-10-19T00:34:55.544997+00:00 cpu 0.8281s wall 0.8213s
- predict --remaining ended 2026-10-19T00:35:25.733191+00:00 cpu 0.5938s wall 0.6192s
- predict --remaining ended 2026-10-19T00:35:48.580329+00:00 cpu 0.4688s wall 1.162s
- baselines ended 2026-10-19T00:36:06.119323+00:00 cpu 1.703s wall 2.119s
- select-baseline --experiment hotspot ended 2026-10-19T00:36:27.770279+00:00 cpu 9.688s wall 11.21s
- hotspot --split test ended 2026-10-19T00:36:47.597012+00:00 cpu 10.89s wall 11.12s
- hotspot --split test ended 2026-10-19T00:38:55.503055+00:00 cpu 10.81s wall 11.11s

# City Scanner C1 ranking report

Experiment-designer execution. No commit. Table II / `tab:tdrive_hybrid` / `tab:traffic_four_region` numeric cells unchanged. Manuscript prose is `ccf-paper-writer`.

## Contract

- Dataset: City Scanner NYC PM2.5 cells (`cityscanner_nyc_pm25`), Zenodo `10.5281/zenodo.7961851`, CC BY 4.0.
- \(Y\): mean finite `pm25` in 500 m \(\times\) 30 min cell. Clients = `spatial_id`, not vehicles.
- \(h(i)\): four quadrants from median \(g_x,g_y\), no \(Y\). \(s(i)\): `region::block::weekday`.
- \(R\): real visit occupancy. \(O/U\): controlled \(p_{\mathrm{obs}}=0.35\), \(s_{\max}=5\). Hybrid. Not end-to-end MCS.
- \(\phi_{\mathrm{train\_unit}}=0/9343=0\). Frozen before RMSE. Design ON. SCD = `raven`. No extra `raven_wo_design` row.
- \(\pi^{\mathrm{tar}}\): `build_pi_target` (not support-compatible mixture). \(\pi^{\mathrm{opp}}\): empirical train occupancy.
- Seeds `32001`--`32010`, 100 windows, `local_steps=2`, device `cpu`. Gate unused.
- Kill bar (frozen before RMSE): SCD paired mean relative vs **both** FedAU and ObsUse \(\le -0.5\%\) on WorstGroupRMSE **or** RMSE\(_\mu\).

## Matrix

`C1_KILL_AUDIT.json` `status=PASS`. `c1_kill=true`. 5 methods \(\times\) 10 seeds = 50 `REAL_PATH_EXECUTED` cells. Same-seed EventTrace hashes are consistent. `n_windows=100` on every cell. `train_full_design_extra=false`.

Sources: `tables/CS_E3.csv`, `tables/CS_E3_SUMMARY.csv`, `tables/CS_E3_PAIRED.csv`.

| Method | RMSE_μ | WorstGroupRMSE | Δ_group | Δ_{c-s} |
|---|---|---|---|---|
| FedAvg-Window | 0.2379 ± 0.0839 | 0.2489 ± 0.0856 | 0.1953 ± 0.0342 | 0.8123 ± 0.0191 |
| TwoStage-Hájek | 0.2510 ± 0.1044 | 0.2629 ± 0.1068 | 0.0952 ± 0.0307 | 0.5305 ± 0.0286 |
| FedAU-Window | 0.2582 ± 0.1028 | 0.2700 ± 0.1048 | 0.3216 ± 0.0412 | 1.1403 ± 0.0538 |
| ObsUse-Window | 0.2566 ± 0.1004 | 0.2685 ± 0.1023 | 0.3187 ± 0.0414 | 1.1369 ± 0.0547 |
| RAVEN-MCS (SCD) | 0.2549 ± 0.1057 | 0.2671 ± 0.1079 | 0.0706 ± 0.0266 | 0.5676 ± 0.0311 |

Paired mean relative difference (SCD minus comparator, 10 seeds):

| Comparator | RMSE_μ | WorstGroupRMSE |
|---|---|---|
| FedAU-Window | **−1.71%** | **−1.56%** |
| ObsUse-Window | **−1.34%** | **−1.23%** |
| FedAvg-Window | +5.59% | +5.80% |

Kill bar is vs FedAU **and** ObsUse only. Both RMSE_μ and WorstGroupRMSE clear \(\le -0.5\%\) vs both comparators, so `C1_KILL=true`.

FedAvg-Window remains lowest on RMSE_μ and WorstGroupRMSE. That does not undo the kill bar. Do not write “SCD is the strongest City Scanner method.” Do not mix this ranking into Table II.

## Numerical note

One P2 window on `raven` seed 32006 returned a slightly negative \(\alpha\) (CLARABEL “solution may be inaccurate”). The experiment driver clipped negatives and renormalized, matching the NSW four-region driver. Lambdas, \(p_{\mathrm{obs}}\), \(s_{\max}\), \(\phi\), grid, and windows were not retuned. Shared `aggregation/methods.py` was not edited.

## Writing

Independent appendix ranking table only. Hybrid: real visit \(R\), controlled \(O/U\). Not an end-to-end MCS system. Clients are cells, not the few City Scanner vehicles.

Do not change Table II / T-Drive hybrid / NSW four-region cells. Manuscript insertion is `ccf-paper-writer`.

## Unchanged

- Table II: SensorScope SCD RMSE_μ 7.9380 / WorstGroup 8.6707; U-Air SCD 1.1131 / 1.1703
- T-Drive hybrid SCD 1.1069 / 1.3106; vs FedAU/ObsUse +2.39% / +2.43%
- NSW four-region: FedAU Δ_group 0.0606 vs SCD 0.1048
- Author block
- `tdrive_protocol_seal_r1/`

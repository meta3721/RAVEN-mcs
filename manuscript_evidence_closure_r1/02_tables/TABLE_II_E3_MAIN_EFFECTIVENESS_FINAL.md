# Table II — E3 main effectiveness (SensorScope, U-Air)

Values are mean ± std over 20 paired seeds. Lower is better. Bold = numerical best among primary methods (not a significance claim). † = Holm-significant vs RAVEN (RAVEN better if the baseline is marked and the mean is higher).

Traffic E3 is excluded (NOT_COMPARABLE cross-vintage).

## SensorScope

| Method | RMSE_μ | Tail RMSE | Δ_group | Δ_{c,s} | Class |
|---|---|---|---|---|---|
| FedAvg-Window | 7.9389 ± 0.0459 | 8.4610 ± 0.0466 | 1.0558 ± 0.0288 † | 1.2903 ± 0.0306 † | primary |
| FedAsync-Window | 7.9391 ± 0.0457 | 8.4612 ± 0.0465 | 1.0558 ± 0.0287 † | 1.2906 ± 0.0307 † | primary |
| TimeAlign-Agg | 7.9395 ± 0.0455 | 8.4616 ± 0.0463 | 1.0561 ± 0.0282 † | 1.2904 ± 0.0304 † | primary |
| Local-Hajek | 7.9389 ± 0.0459 | 8.4610 ± 0.0466 | 1.0558 ± 0.0288 † | 1.2903 ± 0.0306 † | primary |
| TwoStage-Hajek | **7.9309 ± 0.0543** | **8.4528 ± 0.0553** | 1.0353 ± 0.0347 † | 1.2910 ± 0.0324 † | primary |
| Inst-Cal | 7.9380 ± 0.0473 | 8.4601 ± 0.0481 | 1.0141 ± 0.0305 | 1.2644 ± 0.0312 | primary |
| Debt-Cal | 7.9399 ± 0.0463 | 8.4620 ± 0.0471 | 1.0272 ± 0.0275 | 1.2710 ± 0.0298 | primary |
| RAVEN-MCS | 7.9380 ± 0.0473 | 8.4600 ± 0.0481 | **1.0139 ± 0.0305** | **1.2644 ± 0.0312** | primary |

*Reference-only (not a competitive baseline set):*

| Method | RMSE_μ | Tail RMSE | Δ_group | Δ_{c,s} | Class |
|---|---|---|---|---|---|
| Central-All | 7.6004 ± 0.0695 | 8.1056 ± 0.0765 | — | — | reference_only |
| Central-Delivered | 7.9291 ± 0.0759 | 8.4470 ± 0.0794 | — | — | reference_only |
| RAVEN-SimOracle | 7.9373 ± 0.0455 | 8.4594 ± 0.0463 | 1.0160 ± 0.0327 | 1.2709 ± 0.0301 | reference_only |

## U-Air

| Method | RMSE_μ | Tail RMSE | Δ_group | Δ_{c,s} | Class |
|---|---|---|---|---|---|
| FedAvg-Window | **20.6317 ± 1.1263** | **20.7810 ± 1.1909** | 1.1218 ± 0.0417 † | 1.2621 ± 0.0309 † | primary |
| FedAsync-Window | 20.6324 ± 1.1246 | 20.7818 ± 1.1891 | 1.1223 ± 0.0416 † | 1.2619 ± 0.0310 † | primary |
| TimeAlign-Agg | 20.6351 ± 1.1153 | 20.7847 ± 1.1794 | 1.1218 ± 0.0417 † | 1.2630 ± 0.0310 † | primary |
| Local-Hajek | **20.6317 ± 1.1263** | **20.7810 ± 1.1909** | 1.1218 ± 0.0417 † | 1.2621 ± 0.0309 † | primary |
| TwoStage-Hajek | 21.1130 ± 1.2428 † | 21.2868 ± 1.3089 † | 1.1196 ± 0.0445 † | 1.2406 ± 0.0297 † | primary |
| Inst-Cal | 20.6818 ± 1.1435 | 20.8336 ± 1.2096 | 1.0924 ± 0.0479 | 1.2334 ± 0.0320 | primary |
| Debt-Cal | 20.6504 ± 1.1348 | 20.8006 ± 1.2012 | 1.0976 ± 0.0457 | 1.2400 ± 0.0314 | primary |
| RAVEN-MCS | 20.6816 ± 1.1435 | 20.8334 ± 1.2096 | **1.0924 ± 0.0479** | **1.2334 ± 0.0320** | primary |

*Reference-only (not a competitive baseline set):*

| Method | RMSE_μ | Tail RMSE | Δ_group | Δ_{c,s} | Class |
|---|---|---|---|---|---|
| Central-All | 18.3281 ± 0.9834 | 18.3638 ± 1.0196 | — | — | reference_only |
| Central-Delivered | 20.4566 ± 1.7039 | 20.6320 ± 1.7582 | — | — | reference_only |
| RAVEN-SimOracle | 20.6874 ± 1.1360 | 20.8396 ± 1.2017 | 1.0922 ± 0.0483 | 1.2342 ± 0.0325 | reference_only |

RAVEN consistently reduces structural mismatch (Δ_group, Δ_{c,s}) on both comparable datasets.
Prediction (RMSE_μ, Tail RMSE) remains competitive, with selective rather than universal gains.

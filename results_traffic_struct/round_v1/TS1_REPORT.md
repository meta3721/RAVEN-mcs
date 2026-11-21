# TS1: structural readout from the TE1 confirm runs

- Instruction: `ccfa-review-reports/raven-mcs-traffic-struct-readout-execution-prompt.md`, sha256 `8d4790bc635b1d49c14eb8a62e33eafad011171557e46e4f43b45142f4c7e413`
- TE1 state at read: verdict `NO-GO-H`, `n_analysis = 15`
- Analysis set: NSW-Traffic, TE1 confirm seeds 30006-30020, arms `C1_fedavg/traffic/fedavg_window` and `C1_simoracle/traffic/raven_simoracle`
- Both stored metrics are mismatches; a smaller value is the better arm; `D_s(m) = m(fedavg, s) - m(raven_simoracle, s)`, so positive D favours the oracle-margin arm.

## Labels

| metric | n | n_missing | mean D | sd D | bootstrap 95% | MDE80 | label |
|---|---:|---:|---:|---:|---|---:|---|
| `Delta_group` | 15 | 0 | 0.007875 | 0.006121 | [0.005050, 0.011032] | 0.004762 | **SEPARATED-ORACLE** |
| `Delta_c_s` | 15 | 0 | 0.009940 | 0.006574 | [0.006725, 0.013242] | 0.005114 | **SEPARATED-ORACLE** |

Applicability strings seen across the 30 files: `['APPLICABLE']`.

## Missing pairs

None: every one of the 15 pairs carried both fields as `APPLICABLE` with finite values for both metrics.

## What this round does not claim

- TE1 is not reopened and RMSE_mu is not re-scored
- no transfer claim from the frozen-server-step tables
- these 15 seeds are not combined with any other seed
- a separated contrast would be a property of this pipeline and these two arms, not a deployment decision and not E1

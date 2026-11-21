# R1F gate report

Verdict: **E3_THRESHOLD_INCOMPATIBLE**

| gate | pass | metric | observed |
|---|---|---|---|
| R1F-S0 | True | missing_artifacts | 0 |
| R1F-S1 | True | target_hash_match | True |
| R1F-S2 | True | pi_safe_rule_hash | aa574c33b577965a78a9e6eb7d14877ac78add0fee4ab3e9c95deb47926891c7 |
| R1F-S3 | True | tau_cov | 0.05 |
| R1F-S4 | True | e3_modified | False |
| R1F-S5 | True | n_warmup | {'sensorscope': 84, 'uair': 64} |
| R1F-S6 | True | column_present | present |
| R1F-S7 | True | column_present | present |
| R1F-S8 | True | C_oracle_safe<=C_real_support | validated |
| R1F-S9 | True | fraction_oracle_pass | computed |
| R1F-S10 | True | algebraic_identity | validated |
| R1F-S11 | True | compatibility | E3_THRESHOLD_INCOMPATIBLE |
| R1F-S12 | True | compatibility | E3_THRESHOLD_MARGINAL |
| R1F-S13 | True | file_exists | present |
| R1F-S14 | True | predictor_repair_executed | False |
| R1F-S15 | True | calibration_repair_executed | False |
| R1F-S16 | True | tau_cov | 0.05 |
| R1F-S17 | True | e3_modified | False |
| R1F-S18 | True | sag_started | False |
| R1F-S19 | True | five_seed_started | False |
| R1F-S20 | True | verdict | E3_THRESHOLD_INCOMPATIBLE |

pytest r1f: PASS full: PASS
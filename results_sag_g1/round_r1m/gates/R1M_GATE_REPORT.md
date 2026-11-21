# R1m gate report

| id | name | pass | evidence |
|---|---|---|---|
| R1M-S0 | R1l theory freeze unchanged | True | target=86fd55f7e0bf tau=0.05 alpha=0.05 n_min=19 |
| R1M-S1 | raven_mcs resolves to aggregate_coverage | True | aggregate_coverage |
| R1M-S2 | legacy gate bypass absent | True | raven.legacy_only |
| R1M-S3 | stress grid unchanged | True | [1.0, 0.8, 0.6, 0.4, 0.2] |
| R1M-S4 | oracle ground truth frozen | True | 82444e4f49534485 |
| R1M-S5 | predictor family frozen | True | AGGREGATE_COVERAGE_RIDGE_V1 |
| R1M-S6 | feature spec frozen | True | 6cd0b52dd7ce8f06 |
| R1M-S7 | ridge alpha fixed | True | 1.0 |
| R1M-S8 | predictor snapshot frozen per block | True | R1M_PREDICTOR_SNAPSHOT_AUDIT.csv |
| R1M-S9 | refit only after RESET | True | R1M_RESET_AUDIT.csv |
| R1M-S10 | n_min=19 | True | 19 |
| R1M-S11 | finite-sample k_n not clipped | True | k_n unclipped |
| R1M-S12 | same-a same-block calibration only | True | R1M_CALIBRATION_BUFFER_AUDIT.csv |
| R1M-S13 | no current-window calibration leakage | True | current_window_in_buffer |
| R1M-S14 | no future leakage | True | future_score_count |
| R1M-S15 | C_LCB formula correct | True | max(0, C_hat-q) |
| R1M-S16 | Gate_t from C_LCB only | True | Gate=1{C_LCB>=tau} |
| R1M-S17 | Design_t equals Gate_t | True | Design_t := Gate_t |
| R1M-S18 | RESET rule frozen | True | MISCOVERAGE_TRIGGERED_RESET_V1 |
| R1M-S19 | RESET only after completed miscoverage | True | n_reset_events=10 |
| R1M-S20 | RESET restarts WARMUP | True | next window RESET then WARMUP |
| R1M-S21 | primary SensorScope a=.4 complete | True | n=62 |
| R1M-S22 | secondary U-Air a=.2 complete | True | n=53 |
| R1M-S23 | full stress track complete | True | n=575 |
| R1M-S24 | validity quantified | True | 0.9588477366255144 |
| R1M-S25 | false-safe quantified | True | 0.0 |
| R1M-S26 | false-unsafe quantified | True | 0.2553191489361702 |
| R1M-S27 | duty cycle quantified | True | 0.4226086956521739 |
| R1M-S28 | non-vacuity quantified | True | 0.0 |
| R1M-S29 | binomial intervals reported | True | R1M_BINOMIAL_SAFETY_INTERVALS.csv |
| R1M-S30 | no post-hoc predictor tuning | True | alpha frozen before results |
| R1M-S31 | no post-hoc RESET tuning | True | MISCOVERAGE_TRIGGERED_RESET_V1 |
| R1M-S32 | source snapshot complete | True | R1M_SOURCE_SNAPSHOT_MANIFEST.csv |
| R1M-S33 | no SAG | True | sag_started=False |
| R1M-S34 | no 5-seed | True | five_seed_started=False |
| R1M-S35 | final verdict artifact-derived | True | R1M_CERTIFICATE_TOO_CONSERVATIVE |

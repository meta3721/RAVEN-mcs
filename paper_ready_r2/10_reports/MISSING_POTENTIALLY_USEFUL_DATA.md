# Missing potentially useful data R2

No CORE E1–E4 metric cells are missing from the 240/600/E3 main comparable matrices.

- **E4_MAE_mu_in_240_csv** (OPTIONAL): Use supporting RUNLEVEL_SEALED_SCALARS_R2.csv; do not treat as core 240-cell metric
- **E4_RMSE_rho_in_240_csv** (OPTIONAL): supporting extraction only
- **Debt_trajectory_sealed_series** (SUPPORTING): Leave MISSING_NOT_RECORDED
- **ESS_trajectory_sealed_series** (SUPPORTING): Use run-level ESS scalar as supporting
- **P2_runtime_only** (SUPPORTING): Leave P2-only runtime MISSING_NOT_RECORDED
- **SensorScope_sampling_interval** (SUPPORTING): MISSING_NOT_RECORDED
- **UAir_sampling_interval** (SUPPORTING): MISSING_NOT_RECORDED
- **TDrive_opportunity_EventTrace_split_freeze** (CORE for a future T-Drive block; not CORE for current E1-E4 paper): Protocol seal before any formal T-Drive runs
- **E1_dataset_checksum** (SUPPORTING): PARTIAL_BUT_PAPER_SAFE

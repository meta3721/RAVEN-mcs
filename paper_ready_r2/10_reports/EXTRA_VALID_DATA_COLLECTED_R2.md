# Extra valid data collected in R2

Supporting diagnostics only. Not new RQ answers.

- Run-level sealed scalars: `280` rows in `02_supporting_data/diagnostics_r2/RUNLEVEL_SEALED_SCALARS_R2.csv` (ESS, MAE_mu, RMSE_rho, clip rates, Q norms, runtime_seconds, solver_status).
- Per-window active-client / a_r_size: `25200` rows in `WINDOW_ACTIVE_CLIENTS_R2.csv`.
- MAE_mu and RMSE_rho exist in sealed `final_metrics.json` even though the 240-cell CSV marked them MISSING_NOT_RECORDED; they are packaged here as supporting extraction, not as new core E4 metrics.
- Debt trajectory, ESS trajectory, and P2-only runtime remain MISSING_NOT_RECORDED (not present as series in sealed window_metrics.json).

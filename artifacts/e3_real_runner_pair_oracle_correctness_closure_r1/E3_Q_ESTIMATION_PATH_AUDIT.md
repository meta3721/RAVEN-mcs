# q Estimation Path Audit

{
  "q_true_path": "EventTrace.oracle_q from fixed-prestate M_MC replay (SimOracle only)",
  "q_hat_path": "FullWindowRunner online estimator; legal feedback only",
  "features": [
    "bias",
    "hour_block",
    "planned_workload_pre",
    "registration/prestate"
  ],
  "forbidden": [
    "test labels",
    "realized future U contemporaneous as feature",
    "Y outcomes"
  ],
  "update_timing": "after window close legal feedback",
  "clipping": "q_min floor in runner",
  "smoke_demonstrates_non_constant": true,
  "status": "Q_HAT_PATH_READY"
}

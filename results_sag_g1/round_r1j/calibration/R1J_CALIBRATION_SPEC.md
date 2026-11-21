# Calibration freeze

{
  "calibration_id": "CONTEXT_STRATIFIED_WINDOW_MAX_CONFORMAL_V1",
  "residual": "max_{target-positive pairs} (hat_pi_opp - pi_opp_realized)",
  "stratum": "availability_level a",
  "same_a_only": true,
  "no_cross_a_borrow": true,
  "no_oracle_grouping": true,
  "delta_cal": 0.05,
  "quantile": "conformal_upper_residual from dynamic_cov.py (R1d formula)",
  "lookback_min": 8,
  "warmup_if_calib_lt": 8,
  "lower_pi_opp": "max(0, hat_pi_opp - q_{r,a})",
  "C_cov_dynamic": "sum pi_tar * 1{lower_pi_opp >= pi_safe}",
  "tau_cov": 0.05
}
hash: `799925094167e6eac068757bbe787743f3df38dfd843f5f7abcdedae609c8d28`

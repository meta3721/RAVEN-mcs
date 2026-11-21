# Predictor freeze

{
  "model_id": "CONTEXT_AVAILABILITY_PRESENCE_V1",
  "implementation": "sklearn.linear_model.LogisticRegression L2",
  "C": 1.0,
  "solver": "lbfgs",
  "random_state": 30001,
  "lookback_L": 8,
  "fit_protocol": "expanding_window_refit_windows_strictly_before_r",
  "label": "1{pi_opp_realized >= pi_safe}",
  "hat_pi_opp_map": "p * max(pi_safe, pair_expanding_mean_realized_mass_same_a)",
  "features": [
    "log1p_hist_active_count",
    "lag1_active",
    "lag2_active",
    "rolling_active_rate_L8",
    "rolling_pi_opp_mean_L8",
    "rolling_pi_opp_trend_L8",
    "hour_of_day_unit",
    "weekend_flag",
    "availability_level",
    "rolling_active_rate_times_a"
  ],
  "uses_current_mask": false,
  "uses_current_ROU": false,
  "uses_oracle_label": false,
  "model_zoo": false,
  "tie_break": "sklearn lbfgs deterministic random_state=30001",
  "numerical_tolerance": 1e-12,
  "seed": 30001
}
hash: `fb5ebd1fa9d33e9be3384038a076a54db7d7a149d5d52d3e0379de8fbcf82f60`

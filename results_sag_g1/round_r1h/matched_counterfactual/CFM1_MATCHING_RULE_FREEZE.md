# CF-M1 matching rule (frozen before run)

{
  "cf_id": "CF-M1",
  "paired_with": "CF0_E3v1_logical_window",
  "natural_hour_alignment": "train_natural_windows_sorted_by_time_index[window_id]",
  "matched_inputs": [
    "per_client_risk_set_size",
    "client_set_from_cf0",
    "candidate_budget_equals_risk_set_size",
    "seed",
    "target_law",
    "pi_safe",
    "tau_cov"
  ],
  "unique_change": "sample from same-natural-hour pool instead of global train pool",
  "without_replacement": true,
  "cross_time_fill": false,
  "replacement_padding": false,
  "deficit_rule": "sample_count = min(cf0_budget, available_in_natural_hour); log deficit; do not steal from other hours",
  "seed": 30001,
  "rng_salt": 13,
  "tau_cov": 0.05
}

hash: `272edf7acbc16d181dab4167914206f94a4d5c9a4f105aec1edf26f3f5b739f3`

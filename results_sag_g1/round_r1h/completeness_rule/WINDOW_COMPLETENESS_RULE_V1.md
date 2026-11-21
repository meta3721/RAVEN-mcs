# WINDOW_COMPLETENESS_RULE_V1

Outcome-blind. Forbidden: C_oracle_safe, oracle_pass, C_cov, Gate, residuals.

{
  "rule_id": "WINDOW_COMPLETENESS_RULE_V1",
  "uses_oracle": false,
  "uses_c_cov": false,
  "uses_gate": false,
  "uses_predictor": false,
  "native_slot": "processed hourly UTC hour (time_index)",
  "expected_span_seconds": 3600.0,
  "partial_if_time_coverage_ratio_below": 0.5,
  "edge_n": 3,
  "full_interior": "same-split previous and next hours exist and are \u00b11 hour contiguous; slot is a native 1h hour",
  "full_boundary": "native 1h hour complete, but missing previous or next hour inside the same split",
  "partial_left_right": "observed timestamp span inside the hour is < 50% of 3600s, or split cuts records inside the hour",
  "sparse_within_hour_not_partial": "If the processed matrix is one record per spatial_id per hour, low entity count is not PARTIAL.",
  "forbidden_fields": [
    "C_oracle_safe",
    "oracle_pass",
    "C_cov",
    "Gate",
    "residual"
  ]
}

hash: `a785be7a5ddd80e2a5643f3f65710507db73d9e2191f955d7a9beb03a5b28334`

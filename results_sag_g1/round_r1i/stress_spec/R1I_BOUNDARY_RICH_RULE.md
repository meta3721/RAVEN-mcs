# BOUNDARY_RICH routing rule

{
  "BOUNDARY_RICH": {
    "fraction_safe_lo": 0.2,
    "fraction_safe_hi": 0.8,
    "n_safe_min": 5,
    "n_unsafe_min": 5,
    "not_all_on_split_edge": true,
    "not_single_tiny_cluster_max": 3,
    "not_all_partial": true,
    "note": "20/80 is an internal routing rule, not a paper theorem"
  },
  "BOUNDARY_NEAR": {
    "abs_margin_max": 0.01,
    "role": "visualization / subgroup audit only; next round must still use the full track"
  },
  "MILD_SAFE_EXISTS": {
    "a_in": [
      1.0,
      0.8
    ],
    "fraction_safe_min": 0.8
  },
  "SEVERE_UNSAFE_EXISTS": {
    "a_in": [
      0.4,
      0.2
    ],
    "fraction_safe_max": 0.2
  },
  "MIN_CROSSING_WINDOWS": 5,
  "frozen_before_oracle_summary": true
}
hash: `8ce49db22cf620efd5dcf0bb243e9ff031bfaf02eba64dedac856617c8244fc3`

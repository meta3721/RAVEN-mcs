# E3-v1 root-cause attribution

Primary codes: **RC-A+RC-B+RC-C+RC-D**

- RC-A TEMPORAL_CONTINUITY_LOSS: True
- RC-B NATURAL_COOCCURRENCE_LOSS: True
- RC-C SAMPLING_DENSITY_DISTORTION: True
- RC-D TARGET_OPPORTUNITY_POPULATION_MISMATCH: True

Strict claim 'sampling caused ceiling': True

Cross-time train-pool resampling (E3-v1) removes natural co-occurrence and temporal continuity. CF1/CF2 restore within-window membership at the frozen k=4 cap; treat them as diagnostics, not E3-v2.

[
  {
    "dataset": "sensorscope",
    "raw_lag1_jaccard": 0.8333333333333334,
    "e3_lag1_jaccard": 0.012217412217412217,
    "cf0_mean_oracle": 0.018335267991494025,
    "cf1_mean_oracle": 0.06852142509896524,
    "cf2_mean_oracle": 0.06852142509896524,
    "cf1_minus_cf0": 0.05018615710747121,
    "cf2_minus_cf1": 0.0,
    "tv_distance": 0.45454545454545675
  },
  {
    "dataset": "uair",
    "raw_lag1_jaccard": 0.8343949044585988,
    "e3_lag1_jaccard": 0.01952983725135624,
    "cf0_mean_oracle": 0.02785908931082979,
    "cf1_mean_oracle": 0.09333333333333334,
    "cf2_mean_oracle": 0.09333333333333334,
    "cf1_minus_cf0": 0.06547424402250354,
    "cf2_minus_cf1": 0.0,
    "tv_distance": 0.36810990490616774
  }
]

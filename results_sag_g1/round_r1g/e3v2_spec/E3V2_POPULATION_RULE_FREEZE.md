# E3-v2 population rule freeze

{
  "protocol_version": "e3-v2-time-aligned-v1",
  "train_records": "atomic.split == train (frozen processed split / horizon.json time_index bounds)",
  "validation_records": "atomic.split == validation",
  "test_deployment_records": "atomic.split == test (I_dep / public evaluation support)",
  "deployment_entities": "spatial_id mapped through frozen E3 spatial_to_client (SensorScope E1 map; U-Air client-i%8)",
  "risk_set": "all_units_present_in_the_real_hour_for_that_client_no_global_resample",
  "candidate_set": "identical to risk_set in E3-v2 (no extra candidate sampler)",
  "subsampling": "none_protocol_level_full_natural_cooccurrence",
  "cross_time_resample": false,
  "uses_current_R_O_U_for_membership": false,
  "seed": 30001,
  "tau_cov": 0.05
}

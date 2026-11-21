# Nested availability mask

{
  "rule_id": "R1I_NESTED_HASH_MASK_V1",
  "namespace": "RAVEN_MCS_R1I_AVAIL_V1",
  "u_definition": "SHA256(namespace|dataset|base_seed|window_id|entity_id)[:8] / 2^64 in [0,1)",
  "available_iff": "u_e_r < a",
  "nested": true,
  "independent_redraw_per_level": false,
  "outcome_fields_forbidden": [
    "C_oracle_safe",
    "oracle_pass",
    "C_cov",
    "Gate",
    "pi_tar_weight",
    "opportunity_richness"
  ],
  "entity_id": "spatial_id",
  "salt_varies_by_dataset": false,
  "salt_varies_by_oracle": false,
  "base_seed": 30001
}

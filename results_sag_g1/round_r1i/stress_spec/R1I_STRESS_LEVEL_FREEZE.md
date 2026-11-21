# R1I stress level freeze

Mechanism: **EXOGENOUS_ENTITY_AVAILABILITY_THINNING_V1**.

Grid (frozen, coarse, not searched from R1h crossing):

- a = 1.00 (must reproduce natural E3-v2)
- a = 0.80
- a = 0.60
- a = 0.40
- a = 0.20

Coarse grid is used so the stress surface is pre-registered and auditable.
This round does **not** add 0.50 / 0.55 / 0.65 or any midpoint, even if a crossing falls between levels.

{
  "mechanism": "EXOGENOUS_ENTITY_AVAILABILITY_THINNING_V1",
  "physical_meaning": "Before each real E3-v2 window, an exogenous availability retention a in (0,1] is applied to deployment entities (spatial_id). Unavailable entities contribute no opportunity records in that window.",
  "A_GRID": [
    1.0,
    0.8,
    0.6,
    0.4,
    0.2
  ],
  "a_1_reproduces_natural": true,
  "coarse_fixed_grid": true,
  "level_search_from_r1h": false,
  "forbidden_midpoints": [
    0.5,
    0.55,
    0.65
  ],
  "pair_level_deletion": false,
  "pi_tar_weighted_deletion": false,
  "opportunity_richness_deletion": false,
  "dataset_specific_adaptive_rule": false,
  "seed": 30001,
  "tau_cov": 0.05
}

hash: `3d1646e198498032516f0ed348e82eddb53a28d1c964652c4cd631ed14951c85`

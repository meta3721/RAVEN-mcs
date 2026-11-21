# E3-v1 generation DAG

```
raw dataset (Zenodo SensorScope / U-Air matrix)
  → processed atomic_units.parquet (absolute_time, time_index, spatial_id, split)
  → train/val/test split (horizon.json time_index bounds)
  → train pool grouped by (client, opportunity_stratum)
  → abstract logical window_id = 0..N-1
  → per window, per client: sample stratum ~ pi_opp_joint; risk k=min(4,|pool|) from GLOBAL train pool
  → EventTrace freeze (no UTC schedule in metadata)
  → pi_opp_realized = window_opportunity_masses(risk_set (client,stratum) events)
  → C_real_support / C_oracle_safe (R1f)
```

| edge | timestamp | temporal order | same-window co-occurrence | resample | shuffle | replacement | mix across raw time | spatial identity | public/pre-window | current R/O/U |
|------|-----------|----------------|--------------------------|----------|---------|-------------|---------------------|------------------|-------------------|---------------|
| raw → atomic | kept as absolute_time | yes (time_index) | yes | no | no | no | no | spatial_id | n/a | no |
| atomic → split | kept | yes | yes | no | no | no | no | yes | public split | no |
| pool construction | dropped from clock | train units mixed | broken | pool union | sorted unique | no | YES | mapped to client | n/a | no |
| window construction | **lost** (index clock) | logical only | no | new sample each window | RNG | without replacement inside window | YES | via unit_id lookup | no UTC | risk set is current R |
| sealed EventTrace | metadata has no UTC | abstract | sampled only | yes | seed 30001 | replace=False | yes | unit_id retained | no | R/O/U stored but not a public clock |

Inputs to generator: atomic (train split), spatial_to_client, seed, num_windows (100/80).
Outputs: EventTrace events with risk_set_unit_ids; opportunity_stratum in features.

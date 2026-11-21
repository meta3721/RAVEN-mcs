# E3 protocol semantics audit

Answers are artifact- and source-derived only.

## 1. Window semantics

- E3 windows are **abstract logical windows**, not wall-clock windows.
- Generator version: `e3-complete-aligned-r3-v1`
- Window duration constant: `1.0` (index-time units)

## 2. Risk set formation

- Risk sets are sampled from the **train pool** per client/stratum.
- Sampling is independent of dataset `absolute_time` / UTC.
- `e3_generator_samples_train_pool_independent_of_wall_clock`: True

## 3–6. Temporal structure

- Original time continuity preserved in raw dataset: **not carried into sealed E3 trace clock**.
- Real TOD preserved: **no** (`eventtrace_metadata_has_utc_schedule=False`).
- Weekday/weekend: **not encoded** in sealed E3 metadata keys.
- Spatial co-occurrence: preserved via spatial_id → client mapping at generation, then abstract windows.

## 7–8. Sampling effects

- Candidate/risk sets are **re-sampled** from train pool each window.
- This can **disperse** natural opportunity density relative to deployment-time co-occurrence.

## 9–11. Population alignment

- Target law population: **train-split public atomic units** → frozen TARGET_LAW_RULE_V1.
- Realized opportunity population: **sampled train-pool risk sets inside abstract E3 windows**.
- **Support-density mismatch exists**: deployment target law vs sampled opportunity law differ.

## 12–14. Threshold regime

- tau_cov=`0.05` was frozen for paper Gate semantics before G0/G1.
- E3-v1 does **not** faithfully simulate a natural wall-clock deployment regime.
- **Protocol-induced coverage ceiling present**: max realized support in R1e was below tau on SensorScope.

## Metadata evidence

- metadata keys: ['dataset', 'generator', 'notes', 'num_clients', 'num_windows', 's_max', 'seed']
- reason: Sealed E3 EventTrace metadata stores only dataset/seed/num_windows/num_clients/s_max/generator. The complete-aligned R3 generator clocks windows as abstract index time (deadline = window_id + 1.0), not UTC. Risk sets are sampled from the train pool independently of dataset absolute_time. RepeatableTimeOfDayMapper requires a UTC datetime; raw window_id is not a legal input. Reusing the E2 300-window SensorScope schedule would invent a mapping that is not the sealed E3 protocol. No frozen window_id -> UTC timestamp table exists. Inferring the block from the current window's first EventTrace row would use current-window event presence and is forbidden.

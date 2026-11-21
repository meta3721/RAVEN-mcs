# T-Drive real-mobility protocol seal R1

Round: `RAVEN-MCS-TDRIVE-REAL-MOBILITY-PROTOCOL-SEAL-R1`

## 1. Executive decision

**A. TDRIVE_PROTOCOL_R1_SEALED_READY_FOR_1SEED_CANARY**

This round is a protocol seal, not an experiment. Formal training runs = 0. Paper-result runs = 0. Canary = 0.

## 2. Zero-run attestation

training_started = false; formal_run_started = false; canary_started = false; raw/processed unmodified.

## 3. Raw T-Drive identity

MSR T-Drive trajectory sample under `data/raw/tdrive_speed`. Manifest data_hash `7a0e197eeb8ba5230b364ae08d66b53ffbfdb82fc9caf5458a8c5557004387e8`. Status `HASH_BOUND`.

## 4. Processed T-Drive identity

`atomic_units.parquet` rows=435516; `client_measurements.parquet` rows=2236407. Status `HASH_BOUND`. Files were not rewritten.

## 5. Speed-target semantics

Consecutive GPS haversine km / dt hours; keep 5–120 km/h; dt in (0, 0.25] h. Y = mean reference-fleet speed in 500 m × 30 min cell×slot.

## 6. Timezone

Naive T-Drive clocks are Beijing wall-clock. Adapter labels them UTC without converting. Paper timezone = Beijing local coinciding with processed timestamps. Do not apply +8.

## 7. Client identity

One client-fleet taxi = one federated client (`vehicle::{id}`). Reference fleet (30%, seed 26001) builds Y only. n_clients=5867.

## 8. Spatial grid

Regular 500 m cells over lon 116.0–116.8, lat 39.6–40.2. spatial_id = gXXXX_YYYY. n_cells=9994.

## 9. Time slots

30-minute floor of processed timestamps. n_slots=297.

## 10. Atomic-unit definition

i = (spatial_id, time_slot); unit_id = `{spatial_id}_t{time_index:05d}`; Y_i = km/h speed.

## 11. Deployment target h(i)

`PRE_REGISTERED_PROTOCOL_FALLBACK`: H1–H4 Beijing-local time-of-day. Processed `target_group` (spatial×block) is recovered but is not paper h(i).

## 12. Target mu

Test-support frequency of atomic units over H1–H4. No speed labels. sum(mu)=1 within 1e-12.

## 13. Opportunity stratum s(i)

Processed `opportunity_stratum` = spatial_id × 4 TOD blocks × weekday/weekend. Distinct from h(i).

## 14. Real mobility opportunity R

R=1 iff processed client_measurements contains (k, i). REAL_FROM_TDRIVE. Independent of method and of seeds 30001–30010.

## 15. Observation O

Adapter valid-speed filter is DETERMINISTIC_DATA_QUALITY. EventTrace adds controlled p_obs=0.35. Label: REAL_MOBILITY_OPPORTUNITY + DETERMINISTIC_DATA_QUALITY + CONTROLLED_OBSERVATION. Not a recorded sensor-failure log.

## 16. Usable update U

E3 Complete-aligned compute/network/deadline/staleness (s_max=5). CONTROLLED_EXPERIMENTAL. T-Drive does not record these.

## 17. Real-vs-controlled selection-layer disclosure

Only R is guaranteed real-mobility-derived. O/U are controlled experimental layers after real opportunity.

## 18. Train/validation/test split

Recovered processed TemporalSplitConfig 60/20/20 by unique time slots. Not the chronological fallback. E9 yaml is not this protocol.

## 19. Leakage audit

Status: `PASS`. No unit or slot overlap; chronological partitions; train-only scaler; h/q do not use test outcomes.

## 20. Seed policy

Formal paired seeds: 30001, 30002, 30003, 30004, 30005, 30006, 30007, 30008, 30009, 30010. All five methods share one exogenous EventTrace per seed.

## 21. EventTrace schema/generator

Generator `tdrive-complete-aligned-r1-v1`: R from client_measurements; O/U from E3 stage2 transfer. Method-independent. E3 station spatial_to_client generator is not used as-is.

## 22. EventTrace micro-fixture

Non-paper fixture seed 31999: taxis=2, cells=4, slots=3. Status `PASS`. No model fitting.

## 23. Five-method set

- M1 FedAvg-Window (`fedavg_window`)
- M2 FedAsync-Window (`fedasync_window`)
- M3 TimeAlign-Agg (`flamf_timealign_adapted`)
- M4 TwoStage-Hajek (`twostage_hajek`)
- M5 RAVEN-MCS (`raven`)

No Local-Hajek, Inst-Cal, Debt-Cal, SimOracle, Central, or ablations.

## 24. RAVEN config

Transfer of E3/E4 full RAVEN: λ_group=1.0, λ_β=1.0, λ_v=0.1, λ_s=0.1, alpha_max=0.5, e_min/ESS=3.0. Not T-Drive test-tuned.

## 25. Baseline configs

Same backbone, split, preprocessing, and matched-seed EventTrace. TimeAlign canonical ID is `flamf_timealign_adapted`. Not intentionally weakened.

## 26. Primary/secondary metrics

Primary: Delta_group, Delta_c_s, RMSE_mu. RMSE_rho classified `NOT_REQUIRED_FOR_TDRIVE_PRIMARY_CLAIM`.

## 27. Statistical protocol

Paired Wilcoxon two-sided; Holm within each primary metric vs four baselines (m=4); α=0.05; EPS_ZERO=1e-12.

## 28. Pre-registered claim decision rules

Strong / partial / no-clear external consistency, or counterevidence. Success is not defined as an RMSE_mu win.

## 29. Future 1-seed Canary plan

5 methods × seed 30001. Every row `NOT_AUTHORIZED_YET`. Not executed.

## 30. Future 50-run formal matrix

5 methods × 10 seeds = 50 rows, all `NOT_AUTHORIZED_YET`. Not executed.

## 31. Method/data compatibility

Offline classification COMPATIBLE for all five methods. No training used.

## 32. External-validity wording

Allowed: real trajectories determine the opportunity process. Forbidden: claiming network/compute/federated-update traces are recorded T-Drive logs.

## 33. Protocol source freeze

See `13_freeze/TDRIVE_PROTOCOL_SOURCE_FREEZE.json` and the master JSON/MD.

## 34. Protocol diagnostics

See `14_diagnostics/`. Previews are `NOT_FOR_PAPER_USE`.

## 35. Gates

42/42 all_pass=True
- TDPS-G1 PASS: formal/training started false
- TDPS-G2 PASS: canary started false
- TDPS-G3 PASS: HASH_BOUND
- TDPS-G4 PASS: HASH_BOUND
- TDPS-G5 PASS: RECOVERED
- TDPS-G6 PASS: FROZEN
- TDPS-G7 PASS: FROZEN
- TDPS-G8 PASS: 500
- TDPS-G9 PASS: 30
- TDPS-G10 PASS: FROZEN
- TDPS-G11 PASS: PRE_REGISTERED_PROTOCOL_FALLBACK
- TDPS-G12 PASS: sum_ok=True
- TDPS-G13 PASS: FROZEN
- TDPS-G14 PASS: REAL_FROM_TDRIVE
- TDPS-G15 PASS: O labelled
- TDPS-G16 PASS: CONTROLLED_EXPERIMENTAL
- TDPS-G17 PASS: crosswalk
- TDPS-G18 PASS: FROZEN
- TDPS-G19 PASS: PASS
- TDPS-G20 PASS: [30001, 30002, 30003, 30004, 30005, 30006, 30007, 30008, 30009, 30010]
- TDPS-G21 PASS: FROZEN
- TDPS-G22 PASS: generator hashes
- TDPS-G23 PASS: PASS
- TDPS-G24 PASS: 5
- TDPS-G25 PASS: n_identity=5
- TDPS-G26 PASS: TRANSFER_FROM_E3_E4_FULL_RAVEN
- TDPS-G27 PASS: n_baselines=4
- TDPS-G28 PASS: ('Delta_group', 'Delta_c_s', 'RMSE_mu')
- TDPS-G29 PASS: Delta_group = ||omega_hat - mu||_1
- TDPS-G30 PASS: client × opportunity_stratum s(i)
- TDPS-G31 PASS: RMSE_mu = sqrt(sum_i varpi_i^tar (Yhat_i - Y_i)^2)
- TDPS-G32 PASS: NOT_REQUIRED_FOR_TDRIVE_PRIMARY_CLAIM
- TDPS-G33 PASS: stats
- TDPS-G34 PASS: claim rules
- TDPS-G35 PASS: n=50
- TDPS-G36 PASS: n_canary=5
- TDPS-G37 PASS: n=5
- TDPS-G38 PASS: wording seal
- TDPS-G39 PASS: source freeze
- TDPS-G40 PASS: master keys
- TDPS-G41 PASS: no result-dependent choice
- TDPS-G42 PASS: no test-metric protocol choices

## 36. Remaining blockers

None for protocol seal.

## 37. Exact recommended next action

If status A: return this package. Do **not** start Canary until a separate instruction authorizes 5 methods × seed 30001.

If not A: do not start Canary; resolve the named blocker without running T-Drive experiments.

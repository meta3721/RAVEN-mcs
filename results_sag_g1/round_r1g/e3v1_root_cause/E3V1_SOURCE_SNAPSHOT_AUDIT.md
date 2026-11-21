# E3-v1 source snapshot audit

git: `a7f02f08cba2c7038d60d41d24042fbc57c402fd`

Each sealed E3-v1 EventTrace is produced by `generate_complete_aligned_r3`
(`src/raven_mcs/e3/real_runner/generator_r3.py`) from processed atomic units
loaded by `load_paper_dataset`. Window clock is `deadline = window_id + WINDOW_DURATION`
with `WINDOW_DURATION=1.0` index units, not UTC. Risk sets are `rng.choice(train_pool, k=min(4,n), replace=False)`
independent of `absolute_time`.

- `dataset_loader` ← `src/raven_mcs/e3/canary/dataset_load.py` sha256=`785bc0390031…`
- `raw_timestamp_parser` ← `src/raven_mcs/data/processed_dataset.py` sha256=`2a7053d2eb65…`
- `window_slice` ← `src/raven_mcs/data/window_dataset.py` sha256=`8c450f055595…`
- `split_horizon_ss` ← `configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json` sha256=`b31cd16c3b42…`
- `split_horizon_uair` ← `configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json` sha256=`ff1625527f11…`
- `e3_eventtrace_generator` ← `src/raven_mcs/e3/real_runner/generator_r3.py` sha256=`1f69508128c4…`
- `risk_set_sampler` ← `src/raven_mcs/e3/real_runner/generator_r3.py` sha256=`1f69508128c4…`
- `opportunity_constructor` ← `src/raven_mcs/e3/real_runner/generator_r3.py` sha256=`1f69508128c4…`
- `deadline_constructor` ← `src/raven_mcs/e3/real_runner/constants.py` sha256=`e6cd04f53b1a…`
- `target_law_builder` ← `src/raven_mcs/sag/target_law.py` sha256=`660b96130690…`
- `realized_opportunity_builder` ← `src/raven_mcs/sag/dynamic_cov.py` sha256=`dbe4b1584634…`
- `time_mapper` ← `src/raven_mcs/sag/window_context.py` sha256=`6bede846a782…`
- `eventtrace_serializer` ← `src/raven_mcs/simulation/event_trace.py` sha256=`39b87ea551c7…`
- `seed_config` ← `src/raven_mcs/e3/real_runner/constants.py` sha256=`e6cd04f53b1a…`
- `stratum_seal` ← `src/raven_mcs/e3/stratum_seal/remap.py` sha256=`706a252f3afb…`
- `client_mapping` ← `src/raven_mcs/e3/semantic_alignment/client_mapping.py` sha256=`53511264eb8b…`

# E3-v2 EventTrace schema

protocol_version: `e3-v2-time-aligned-v1`

Fields:
- `protocol_version`
- `dataset`
- `seed`
- `split_id`
- `window_id`
- `window_start_utc`
- `window_end_utc`
- `timezone`
- `public_context_hash`
- `risk_set_hash`
- `candidate_set_hash`
- `target_law_hash`
- `pi_safe_rule_hash`
- `tau_cov`
- `raw_window_source_hash`
- `event_count`
- `user_count`
- `spatial_support`
- `logical_deadline_fields`
- `optional_original_record_ids_hash`

Reviewer mapping: `window_id` → `window_start_utc`/`window_end_utc` → raw atomic `time_index` via `raw_window_source_hash`.

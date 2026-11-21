# E3-v2 window rule freeze

{
  "protocol_version": "e3-v2-time-aligned-v1",
  "window_duration_hours": 1,
  "window_alignment": "utc_hour_floor",
  "timezone": "UTC",
  "timestamp_source": "processed_atomic.absolute_time",
  "start_time_rule": "UTC hour floor of the atomic absolute_time shared by the window",
  "end_time_rule": "window_start + 1 hour",
  "boundary_inclusion": "half_open_[start, end)",
  "missing_timestamp_handling": "atomic rows without parseable UTC absolute_time are excluded from all windows",
  "duplicate_timestamp_handling": "rows sharing the same spatial_id and UTC hour are kept as distinct unit_ids",
  "cross_day_handling": "windows do not span UTC midnight; each UTC hour is its own window",
  "weekday_weekend_availability": "derived from window_start_utc before the window begins",
  "public_pre_window_fields": [
    "window_start_utc",
    "window_end_utc",
    "hour_of_day",
    "weekday",
    "weekend_flag"
  ],
  "prior_justification": "SensorScope and U-Air processed matrices use time_unit=hour; E3-v1 WINDOW_DURATION=1.0 was already frozen as a one-slot duration. E3-v2 reuses that 1-hour native sampling period as a UTC-aligned real window. Duration is not chosen from R1f oracle pass rates.",
  "chosen_from_r1f_oracle": false
}

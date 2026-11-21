# P0 data audit

Status: INVALID_RUN

{
  "source_rows": 12430,
  "source_IDs": 49,
  "source_unique_ID_dates": 9707,
  "missing_fields_whole_source": {
    "PM25cf1": 0,
    "RH": 17,
    "TempC": 184,
    "PM25FM": 0
  },
  "exact_duplicate_rows_collapsed": 38,
  "target_window_rows": 2987,
  "target_window_devices": 28,
  "unique_reference_events_all_types": 2258,
  "event_device_reuses": 307,
  "conflict_keys": 381
}

No accepted representative or evaluation panel was frozen. See conflicts.csv and site_map.csv. Reference numeric values from A/T are not exported. Source dictionary defines PM25FM and PM25cf1 in ug/m3; NA is the source missing marker. The initial CSV index is not an observation field. Data conflicts are not averaged or deleted.

## Final interpretation

22 mapped sites are candidates before support filtering, not a final cohort. Fixed reference/device selection and V/T support remain unassessed because381 keys have unresolved values. See FAILURE_REPORT.md and SOURCE_IDENTITY_REVIEW.md. P1 NOT_RUN.

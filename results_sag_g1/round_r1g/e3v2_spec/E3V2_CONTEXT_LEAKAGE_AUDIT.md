# E3-v2 context leakage audit

Allowed: window_start_utc, hour_of_day, weekday, weekend_flag, lagged public summaries.
Forbidden: current R/O/U, current realized opportunity, labels, Gate outcomes, dataset-name Gate feature.
public_context_from_start smoke: True

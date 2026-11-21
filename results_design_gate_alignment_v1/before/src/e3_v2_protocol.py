"""E3-v2 protocol rules. Frozen before oracle precheck. Not a SAG runner."""

from __future__ import annotations

from typing import Any

from raven_mcs.utils.hashing import sha256_json

PROTOCOL_VERSION = "e3-v2-time-aligned-v1"
WINDOW_DURATION_HOURS = 1
TIMEZONE = "UTC"
TIMESTAMP_SOURCE = "processed_atomic.absolute_time"
ALIGNMENT = "utc_hour_floor"
BOUNDARY = "half_open_[start, end)"
SEED = 30001
TAU_COV = 0.05
RISK_SET_RULE = "all_units_present_in_the_real_hour_for_that_client_no_global_resample"
SUBSAMPLING = "none_protocol_level_full_natural_cooccurrence"


def window_rule_payload() -> dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "window_duration_hours": WINDOW_DURATION_HOURS,
        "window_alignment": ALIGNMENT,
        "timezone": TIMEZONE,
        "timestamp_source": TIMESTAMP_SOURCE,
        "start_time_rule": "UTC hour floor of the atomic absolute_time shared by the window",
        "end_time_rule": "window_start + 1 hour",
        "boundary_inclusion": BOUNDARY,
        "missing_timestamp_handling": "atomic rows without parseable UTC absolute_time are excluded from all windows",
        "duplicate_timestamp_handling": "rows sharing the same spatial_id and UTC hour are kept as distinct unit_ids",
        "cross_day_handling": "windows do not span UTC midnight; each UTC hour is its own window",
        "weekday_weekend_availability": "derived from window_start_utc before the window begins",
        "public_pre_window_fields": [
            "window_start_utc",
            "window_end_utc",
            "hour_of_day",
            "weekday",
            "weekend_flag",
        ],
        "prior_justification": (
            "SensorScope and U-Air processed matrices use time_unit=hour; "
            "E3-v1 WINDOW_DURATION=1.0 was already frozen as a one-slot duration. "
            "E3-v2 reuses that 1-hour native sampling period as a UTC-aligned real window. "
            "Duration is not chosen from R1f oracle pass rates."
        ),
        "chosen_from_r1f_oracle": False,
    }


def population_rule_payload() -> dict[str, Any]:
    return {
        "protocol_version": PROTOCOL_VERSION,
        "train_records": "atomic.split == train (frozen processed split / horizon.json time_index bounds)",
        "validation_records": "atomic.split == validation",
        "test_deployment_records": "atomic.split == test (I_dep / public evaluation support)",
        "deployment_entities": "spatial_id mapped through frozen E3 spatial_to_client (SensorScope E1 map; U-Air client-i%8)",
        "risk_set": RISK_SET_RULE,
        "candidate_set": "identical to risk_set in E3-v2 (no extra candidate sampler)",
        "subsampling": SUBSAMPLING,
        "cross_time_resample": False,
        "uses_current_R_O_U_for_membership": False,
        "seed": SEED,
        "tau_cov": TAU_COV,
    }


def window_rule_hash() -> str:
    return sha256_json(window_rule_payload())


def population_rule_hash() -> str:
    return sha256_json(population_rule_payload())

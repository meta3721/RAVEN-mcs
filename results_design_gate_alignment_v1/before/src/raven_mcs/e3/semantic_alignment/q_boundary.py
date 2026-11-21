"""Legal q-feature boundary for Stage-2 usability (registration/prestate only)."""

from __future__ import annotations

from typing import Any

from raven_mcs.propensity.leakage import assert_q_features_leakage_free

ALLOWED_Q_FEATURES: list[dict[str, Any]] = [
    {"name": "bias", "source": "constant", "timestamp_availability": "registration", "prestate_poststate": "prestate", "allowed": True, "justification": "intercept"},
    {"name": "model_age", "source": "EventTrace.tau at registration", "timestamp_availability": "registration", "prestate_poststate": "prestate", "allowed": True, "justification": "staleness known at download"},
    {"name": "device_class", "source": "device_profile encoding", "timestamp_availability": "registration", "prestate_poststate": "prestate", "allowed": True, "justification": "device state at attempt"},
    {"name": "network_budget", "source": "network_profile encoding", "timestamp_availability": "registration", "prestate_poststate": "prestate", "allowed": True, "justification": "bandwidth/energy proxy at registration"},
    {"name": "deadline_slack_pre", "source": "propensity.usable.deadline_slack_pre", "timestamp_availability": "registration", "prestate_poststate": "prestate", "allowed": True, "justification": "expected remaining window time before outcomes"},
    {"name": "expected_compute_time_prior", "source": "device tier prior", "timestamp_availability": "registration", "prestate_poststate": "prestate", "allowed": True, "justification": "expected compute time prior, not realized delay"},
    {"name": "expected_net_budget_prior", "source": "network tier prior", "timestamp_availability": "registration", "prestate_poststate": "prestate", "allowed": True, "justification": "expected network budget prior, not realized delay"},
    {"name": "local_workload_m", "source": "raw_workload / risk-set size", "timestamp_availability": "registration", "prestate_poststate": "prestate", "allowed": True, "justification": "sample size known at registration"},
    {"name": "historical_success_rate", "source": "lagged U history", "timestamp_availability": "pre-window", "prestate_poststate": "prestate", "allowed": True, "justification": "one-window-lagged only"},
]

FORBIDDEN_Q_FEATURES: list[dict[str, Any]] = [
    {"name": "future_target_values", "allowed": False, "justification": "target leakage"},
    {"name": "realized_delivery_U", "allowed": False, "justification": "poststate label"},
    {"name": "future_latency", "allowed": False, "justification": "poststate"},
    {"name": "post_update_loss", "allowed": False, "justification": "downstream"},
    {"name": "test_labels", "allowed": False, "justification": "test leakage"},
    {"name": "realized_target_group_performance", "allowed": False, "justification": "outcome leakage"},
    {"name": "hour_sin_as_q_proxy_for_geography", "allowed": False, "justification": "too close to opportunity/observation geography; not Stage-2 usability"},
    {"name": "time_block_as_q_feature", "allowed": False, "justification": "opportunity/target geography; not registration compute/network state"},
]


def q_feature_boundary_payload() -> dict[str, Any]:
    allowed_names = tuple(f["name"] for f in ALLOWED_Q_FEATURES if f["allowed"])
    # Core runner names must pass leakage denylist
    assert_q_features_leakage_free(("bias", "model_age", "device_class", "network_budget", "deadline_slack_pre"))
    return {
        "allowed_features": ALLOWED_Q_FEATURES,
        "forbidden_features": FORBIDDEN_Q_FEATURES,
        "runner_core_feature_names": [
            "bias",
            "model_age",
            "device_class",
            "network_budget",
            "deadline_slack_pre",
        ],
        "allowed_names": list(allowed_names),
        "status": "Q_FEATURE_BOUNDARY_READY",
    }

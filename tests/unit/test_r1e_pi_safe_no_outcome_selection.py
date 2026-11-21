"""pi_safe rule excludes outcomes, residuals, and Gate ON/OFF."""

from __future__ import annotations

from raven_mcs.sag.target_law import PI_SAFE_RULE_V1


def test_r1e_pi_safe_no_outcome_selection() -> None:
    banned = {
        "labels",
        "test_outcomes",
        "test_prediction_residuals",
        "current_window_events",
        "gate_ON_OFF",
    }
    assert banned.issubset(set(PI_SAFE_RULE_V1["excludes"]))
    assert PI_SAFE_RULE_V1["data_source"] == "public_pi_opp_joint_on_target_positive_pairs"

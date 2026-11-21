"""Stage 1 uses the frozen R1d coverage / vacuity stop rules."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import stage1_stop_status


def test_r1e_stage1_stop_rules() -> None:
    assert stage1_stop_status(joint_coverage=0.80, c_cov_zero_fraction=0.1, coverage_slides=False) == "DYNAMIC_COV_NOT_CALIBRATED"
    assert stage1_stop_status(joint_coverage=0.95, c_cov_zero_fraction=0.1, coverage_slides=True) == "DYNAMIC_COV_NOT_CALIBRATED"
    assert stage1_stop_status(joint_coverage=0.95, c_cov_zero_fraction=0.2, coverage_slides=False) == "STAGE1_DYNAMIC_COV_CALIBRATED_NONVACUOUS"
    assert stage1_stop_status(joint_coverage=0.95, c_cov_zero_fraction=0.95, coverage_slides=False) == "DYNAMIC_COV_TOO_CONSERVATIVE"

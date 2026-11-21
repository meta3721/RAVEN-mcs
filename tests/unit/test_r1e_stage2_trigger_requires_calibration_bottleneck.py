"""Stage 2 is allowed only when point is non-vacuous and LCB is vacuous."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import stage2_trigger_status


def test_r1e_stage2_trigger_requires_calibration_bottleneck() -> None:
    assert stage2_trigger_status(point_zero_fraction=0.95, c_cov_zero_fraction=0.99) == "R1E_POINT_PREDICTOR_NONVACUITY_NOT_ACHIEVED"
    assert stage2_trigger_status(point_zero_fraction=0.20, c_cov_zero_fraction=0.95) == "GLOBAL_CALIBRATION_DOMINATES_NONVACUITY"
    assert stage2_trigger_status(point_zero_fraction=0.20, c_cov_zero_fraction=0.10) == "NO_STAGE2"

from raven_mcs.sag.r1l_block import BlockMachine


def test_current_window_not_in_own_calibration() -> None:
    m = BlockMachine()
    step = m.prewindow_step(regime_change_detected=False, completed_past_for_refit=[])
    n_before = len(m.calibration_buffer)
    assert step["n_cal"] == n_before
    m.append_completed_window(0.4)
    assert len(m.calibration_buffer) == n_before + 1

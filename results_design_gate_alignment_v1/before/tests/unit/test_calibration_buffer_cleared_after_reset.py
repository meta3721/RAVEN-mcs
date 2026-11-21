from raven_mcs.sag.r1l_block import BlockMachine


def test_calibration_buffer_cleared_after_reset() -> None:
    m = BlockMachine()
    for _ in range(4):
        m.append_completed_window(0.2)
    assert m.calibration_buffer
    out = m.reset_and_open_next_block([0.2] * 4)
    assert out["calibration_buffer_cleared"] is True
    assert m.calibration_buffer == []

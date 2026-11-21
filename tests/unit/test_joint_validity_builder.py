from raven_mcs.sag.r1j_calibration import joint_valid

def test_joint_validity_builder() -> None:
    pairs = [("c0", "s0")]
    ok, d = joint_valid({("c0", "s0"): 0.01}, {("c0", "s0"): 0.02}, pairs)
    assert ok is True
    ok, d = joint_valid({("c0", "s0"): 0.05}, {("c0", "s0"): 0.01}, pairs)
    assert ok is False

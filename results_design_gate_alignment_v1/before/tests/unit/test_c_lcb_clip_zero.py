from raven_mcs.sag.r1l_conformal import c_lcb

def test_c_lcb_clip_zero() -> None:
    assert c_lcb(0.08, 0.03) == 0.05
    assert c_lcb(0.01, 0.03) == 0.0

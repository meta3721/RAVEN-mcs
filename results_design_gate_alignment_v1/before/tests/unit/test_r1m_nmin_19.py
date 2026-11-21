from raven_mcs.sag.r1l_spec import ALPHA, N_MIN, n_min


def test_r1m_nmin_19() -> None:
    assert N_MIN == 19
    assert n_min(ALPHA) == 19
    assert n_min(0.05) == 19

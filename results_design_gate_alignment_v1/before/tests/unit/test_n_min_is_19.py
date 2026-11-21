from raven_mcs.sag.r1l_spec import ALPHA, N_MIN, n_min

def test_n_min_is_19() -> None:
    assert N_MIN == 19 == n_min() == n_min(ALPHA)

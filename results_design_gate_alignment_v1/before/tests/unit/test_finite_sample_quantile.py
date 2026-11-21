from raven_mcs.sag.r1l_conformal import c_lcb, finite_sample_conformal_quantile
from raven_mcs.sag.r1l_spec import k_n


def test_finite_sample_quantile() -> None:
    assert finite_sample_conformal_quantile(list(range(18)))[2] is True
    q, n, warmup = finite_sample_conformal_quantile(list(range(19)))
    assert warmup is False
    assert n == 19
    assert k_n(19) == 19
    assert q == 18.0
    assert c_lcb(1.0, 0.2) == 0.8
    assert c_lcb(0.1, 0.2) == 0.0

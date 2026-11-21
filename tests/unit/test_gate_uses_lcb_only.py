from raven_mcs.sag.r1l_design import gate_from_certificate
from raven_mcs.sag.r1l_spec import TAU_COV


def test_gate_uses_lcb_only() -> None:
    assert gate_from_certificate(certificate_state="CERTIFIED", c_lcb=.05, tau_cov=TAU_COV) == 1
    assert gate_from_certificate(certificate_state="CERTIFIED", c_lcb=.049, tau_cov=TAU_COV) == 0
    for state in ("WARMUP", "RESET"):
        assert gate_from_certificate(certificate_state=state, c_lcb=1., tau_cov=TAU_COV) == 0

from raven_mcs.sag.availability_stress import TAU_COV
from raven_mcs.sag.r1l_spec import TAU_COV as R1L_TAU


def test_r1m_tau_unchanged() -> None:
    assert TAU_COV == 0.05
    assert R1L_TAU == 0.05

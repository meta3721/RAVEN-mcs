"""R1m frozen theory constants. Must match R1l / R1i."""

from raven_mcs.sag.availability_stress import A_GRID, TAU_COV
from raven_mcs.sag.r1l_spec import ALPHA, N_MIN
from raven_mcs.sag.r1m_spec import RIDGE_ALPHA
from raven_mcs.sag.target_law import freeze_target_law_rule_v1


def test_r1m_frozen_theory_constants() -> None:
    assert TAU_COV == 0.05
    assert ALPHA == 0.05
    assert N_MIN == 19
    assert RIDGE_ALPHA == 1.0
    assert list(A_GRID) == [1.0, 0.8, 0.6, 0.4, 0.2]
    assert freeze_target_law_rule_v1()["hash"] == (
        "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"
    )

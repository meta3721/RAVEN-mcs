from raven_mcs.sag.availability_stress import BOUNDARY_NEAR_MARGIN

def test_boundary_near_rule_unchanged() -> None:
    assert BOUNDARY_NEAR_MARGIN == 0.01

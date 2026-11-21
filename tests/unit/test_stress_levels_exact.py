from raven_mcs.sag.availability_stress import A_GRID

def test_stress_levels_exact() -> None:
    assert tuple(float(x) for x in A_GRID) == (1.00, 0.80, 0.60, 0.40, 0.20)

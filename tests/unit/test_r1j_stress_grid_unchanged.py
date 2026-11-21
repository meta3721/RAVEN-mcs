from raven_mcs.sag.availability_stress import A_GRID

def test_r1j_stress_grid_unchanged() -> None:
    assert tuple(float(x) for x in A_GRID) == (1.00, 0.80, 0.60, 0.40, 0.20)

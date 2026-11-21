from pathlib import Path
from raven_mcs.sag.availability_stress import A_GRID, stress_level_payload
ROOT = Path(__file__).resolve().parents[2]

def test_no_adaptive_stress_level_added() -> None:
    assert list(A_GRID) == [1.0, 0.8, 0.6, 0.4, 0.2]
    assert 0.50 not in A_GRID and 0.55 not in A_GRID and 0.65 not in A_GRID
    assert stress_level_payload()["level_search_from_r1h"] is False
    grid = (ROOT / "src/raven_mcs/sag/availability_stress.py").read_text(encoding="utf-8")
    assert "A_GRID = (1.00, 0.80, 0.60, 0.40, 0.20)" in grid

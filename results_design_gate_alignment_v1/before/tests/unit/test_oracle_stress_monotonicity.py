from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]

def test_oracle_stress_monotonicity() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1i/oracle_stress/R1I_MONOTONICITY_AUDIT.csv")
    assert frame["real_monotone"].astype(bool).all()
    assert frame["oracle_monotone"].astype(bool).all()

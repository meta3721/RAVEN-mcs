from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]

def test_a1_reproduces_natural() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1i/oracle_stress/R1I_BASELINE_REPRODUCTION_AUDIT.csv")
    assert frame["oracle_match"].astype(bool).all()
    assert frame["entity_count_match"].astype(bool).all()
    assert float(frame["abs_diff_oracle"].max()) < 1e-9

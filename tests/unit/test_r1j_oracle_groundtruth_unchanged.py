from pathlib import Path
import pandas as pd
from raven_mcs.utils.hashing import sha256_file
ROOT = Path(__file__).resolve().parents[2]

def test_r1j_oracle_groundtruth_unchanged() -> None:
    src = ROOT / "results_sag_g1/round_r1i/oracle_stress/R1I_ORACLE_STRESS_BY_WINDOW.csv"
    freeze = pd.read_csv(ROOT / "results_sag_g1/round_r1j/freeze/R1J_ORACLE_FREEZE_MANIFEST.csv")
    assert (freeze["source_sha256"] == sha256_file(src)).all()

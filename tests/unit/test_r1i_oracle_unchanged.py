from pathlib import Path
import json
from raven_mcs.utils.hashing import sha256_file
ROOT = Path(__file__).resolve().parents[2]

def test_r1i_oracle_unchanged() -> None:
    frozen = json.loads((ROOT / "results_sag_g1/round_r1k/freeze/R1K_THEORY_AND_ORACLE_HASHES.json").read_text(encoding="utf-8"))
    src = ROOT / "results_sag_g1/round_r1i/oracle_stress/R1I_ORACLE_STRESS_BY_WINDOW.csv"
    assert frozen["oracle_sha256"] == sha256_file(src)

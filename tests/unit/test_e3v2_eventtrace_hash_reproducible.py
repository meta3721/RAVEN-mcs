from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_e3v2_eventtrace_hash_reproducible() -> None:
    summary = pd.read_csv(ROOT / "results_sag_g1/round_r1g/e3v2_oracle_precheck/E3V2_ORACLE_PRECHECK_SUMMARY.csv")
    assert summary["replay_hash_match"].astype(str).str.lower().isin(["true", "1"]).all()

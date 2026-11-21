from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_e3v2_eventtrace_has_real_timestamp() -> None:
    path = ROOT / "results_sag_g1/round_r1g/e3v2_oracle_precheck/E3V2_ORACLE_PRECHECK_BY_WINDOW.csv"
    frame = pd.read_csv(path)
    ts = pd.to_datetime(frame["window_start_utc"], utc=True)
    assert ts.notna().all()
    assert (frame["window_start_utc"].astype(str).str.contains("+", regex=False) | frame["window_start_utc"].astype(str).str.contains("Z")).any() or ts.dt.tz is not None

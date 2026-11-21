from pathlib import Path
import pandas as pd
from e3_v2_context import WHITELIST

ROOT = Path(__file__).resolve().parents[2]


def test_e3v2_public_context_whitelist() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1g/e3v2_spec/E3V2_PUBLIC_CONTEXT_WHITELIST.csv")
    forbidden = frame.loc[frame["allowed"].astype(str).str.lower().isin(["false", "0"])]
    assert "current_R" in set(forbidden["feature"])
    assert any(r["feature"] == "window_start_utc" and r["allowed"] for r in WHITELIST)

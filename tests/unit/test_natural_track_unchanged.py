from pathlib import Path
import pandas as pd
from raven_mcs.utils.hashing import sha256_file
ROOT = Path(__file__).resolve().parents[2]

def test_natural_track_unchanged() -> None:
    freeze = pd.read_csv(ROOT / "results_sag_g1/round_r1i/R1I_INPUT_FREEZE_MANIFEST.csv")
    ss = freeze.loc[freeze["artifact"] == "E3-v2 EventTrace SS"].iloc[0]
    current = sha256_file(ROOT / str(ss["path"]))
    assert current == ss["sha256"]
    verdict = ROOT / "results_sag_g1/round_r1i/summary/R1I_VERDICT.json"
    import json
    payload = json.loads(verdict.read_text(encoding="utf-8"))
    assert payload.get("natural_track_rewritten") is False

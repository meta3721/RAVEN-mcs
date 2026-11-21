from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_certificates_source_in_snapshot() -> None:
    frame = pd.read_csv(
        ROOT / "results_sag_g1/round_r1l_v13/source_snapshot/R1L_V13_SOURCE_SNAPSHOT_MANIFEST.csv"
    )
    blob = " ".join(frame["source_path"].astype(str).tolist())
    assert "certificates.py" in blob
    snap = ROOT / "results_sag_g1/round_r1l_v13/source_snapshot/certificates.py"
    assert snap.is_file()
    assert "formal_aggregate_coverage" in snap.read_text(encoding="utf-8")

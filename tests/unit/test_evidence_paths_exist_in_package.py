from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_evidence_paths_exist_in_package() -> None:
    frame = pd.read_csv(ROOT / "results_sag_g1/round_r1l_v11/audit/R1L_V11_EVIDENCE_PATH_AUDIT.csv")
    assert not frame.empty
    assert bool(frame["pass"].all())
    for rel in frame["evidence_file"]:
        path = ROOT / "results_sag_g1" / str(rel)
        assert path.is_file(), rel
        assert not str(rel).startswith("src/"), rel

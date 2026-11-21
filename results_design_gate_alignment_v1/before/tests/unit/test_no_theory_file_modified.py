from pathlib import Path
import json
from raven_mcs.utils.hashing import sha256_file
ROOT = Path(__file__).resolve().parents[2]
def test_no_theory_file_modified() -> None:
    """R1k itself did not edit tex. Later R1l may seal theory in Overleaf."""
    frozen = json.loads((ROOT / "results_sag_g1/round_r1k/freeze/R1K_THEORY_AND_ORACLE_HASHES.json").read_text(encoding="utf-8"))
    snap = ROOT / "results_sag_g1/round_r1k/source_snapshot"
    mapping = {
        "TO_OVERLEAF_paper_tmc_r1_clean/main.tex": snap / "main.tex",
        "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex": snap / "appendix.tex",
        "TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex": snap / "supplemental.tex",
    }
    for rel, path in mapping.items():
        assert frozen["paper_tex_sha256"][rel] == sha256_file(path)
    verdict = json.loads((ROOT / "results_sag_g1/round_r1k/summary/R1K_VERDICT.json").read_text(encoding="utf-8"))
    assert verdict.get("theory_file_modified") is False
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1k.py").read_text(encoding="utf-8")
    assert "main.tex" not in "".join(line for line in src.splitlines() if "write_text" in line)

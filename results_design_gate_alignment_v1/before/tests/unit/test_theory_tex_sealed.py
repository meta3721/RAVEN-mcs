from pathlib import Path
import json
from raven_mcs.sag.r1l_spec import PAPER_TEX
from raven_mcs.utils.hashing import sha256_file
ROOT = Path(__file__).resolve().parents[2]

REQUIRED_MAIN = (
    "eq:agg_Ct",
    "prop:pairwise-lcb-barrier",
    "cor:availability-barrier",
    "thm:agg-lcb",
    "cor:false-safe-gate",
    "prop:drift-boundary",
    "ass:score-exchangeability",
    "alg:agg_certificate",
    "WARMUP",
    "CERTIFIED",
    "RESET",
)
REQUIRED_APP = (
    "app:agg_coverage_proofs",
    "app:proof_agg_lcb",
    "app:nmin",
)


def test_theory_tex_sealed() -> None:
    frozen = json.loads((ROOT / "results_sag_g1/round_r1l/freeze/R1L_PAPER_TEX_HASHES.json").read_text(encoding="utf-8"))
    for rel in PAPER_TEX:
        assert frozen["paper_tex_sha256"][rel] == sha256_file(ROOT / rel)
    main = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
    appendix = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex").read_text(encoding="utf-8")
    for tok in REQUIRED_MAIN:
        assert tok in main
    for tok in REQUIRED_APP:
        assert tok in appendix
    assert "n_{\\min}=19" in main
    assert "Proof sketch" not in appendix
    verdict = json.loads((ROOT / "results_sag_g1/round_r1l/summary/R1L_VERDICT.json").read_text(encoding="utf-8"))
    assert verdict.get("theory_tex_edited") is True

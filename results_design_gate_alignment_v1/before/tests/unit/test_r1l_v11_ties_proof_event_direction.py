from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _thm() -> str:
    p = ROOT / "results_sag_g1/round_r1l_v11/proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md"
    tex = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex"
    return p.read_text(encoding="utf-8") + "\n" + tex.read_text(encoding="utf-8")


def test_r1l_v11_ties_proof_event_direction() -> None:
    text = _thm()
    assert "smaller than the jittered" not in text
    assert "can only shrink the coverage event" not in text
    assert r"{R_t^\star \le k_n}" in text or "R_t^\\star \\le k_n" in text
    assert "subseteq" in text.lower() or r"\subseteq" in text
    assert "If A\\subset B" in text or "If $A\\subset B$" in text or "if $A\\subset B$" in text.lower() or "A\\subset B" in text


def test_r1l_v11_randomized_rank_ties() -> None:
    text = _thm()
    assert "Continuous" in text
    assert "R_t" in text and "uniform" in text.lower()
    assert "lexicograph" in text.lower() or "tie-break" in text.lower()


def test_r1l_v11_k_orderstat_valid() -> None:
    from raven_mcs.sag.r1l_spec import k_n

    assert k_n(19) == 19
    assert k_n(18) == 19
    text = _thm()
    assert "k_n" in text and "n+1" in text.replace(" ", "")

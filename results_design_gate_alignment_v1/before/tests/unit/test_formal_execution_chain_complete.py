from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_formal_execution_chain_complete() -> None:
    text = (ROOT / "results_sag_g1/round_r1l_v13/interface/R1L_V13_FORMAL_EXECUTION_CHAIN.md").read_text(
        encoding="utf-8"
    )
    for token in (
        "raven_mcs",
        "aggregate_coverage",
        "compute_certificates",
        "formal_aggregate_coverage",
        "Gate_t",
        "Design_t",
        "window-close",
        "window_runner",
    ):
        assert token in text
    for step in ("STEP 1", "STEP 2", "STEP 3", "STEP 4", "STEP 5", "STEP 6", "STEP 7", "STEP 8", "STEP 9"):
        assert step in text

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_e3v1_generation_dag_complete() -> None:
    text = (ROOT / "results_sag_g1/round_r1g/e3v1_root_cause/E3V1_GENERATION_DAG.md").read_text(encoding="utf-8")
    for token in ("raw dataset", "EventTrace", "pi_opp_realized", "resample", "timestamp"):
        assert token in text

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_no_posthoc_reset_tuning() -> None:
    reset = (ROOT / "src/raven_mcs/sag/r1m_reset.py").read_text(encoding="utf-8")
    spec = (ROOT / "src/raven_mcs/sag/r1m_spec.py").read_text(encoding="utf-8")
    assert "MISCOVERAGE_TRIGGERED_RESET_V1" in reset
    assert "CUSUM" not in reset
    assert "ADWIN" not in reset
    assert "Page-Hinkley" not in reset and "PageHinkley" not in reset
    assert "second_detector\": False" in spec or '"second_detector": False' in spec

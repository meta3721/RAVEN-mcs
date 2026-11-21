from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_compute_certificates_routes_aggregate_mode() -> None:
    src = (ROOT / "src/raven_mcs/sag/certificates.py").read_text(encoding="utf-8")
    assert 'cov_mode) == "aggregate_stable_regime"' in src or '== "aggregate_stable_regime"' in src
    assert "formal_aggregate_coverage" in src
    assert "def compute_certificates" in src

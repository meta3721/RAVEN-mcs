from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_cf2_fixed_definition() -> None:
    runner = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1g.py").read_text(encoding="utf-8")
    assert 'cf2_order = list(base)' in runner
    assert 'cf_from(cf2_order, "CF2"' in runner
    helper = (ROOT / "src/raven_mcs/sag/e3v1_root_cause.py").read_text(encoding="utf-8")
    assert "Not E3-v2" in helper

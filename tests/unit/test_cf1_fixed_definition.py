from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_cf1_fixed_definition() -> None:
    src = (ROOT / "src/raven_mcs/sag/e3v1_root_cause.py").read_text(encoding="utf-8")
    assert "subsample_within_window" in src
    runner = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1g.py").read_text(encoding="utf-8")
    assert 'cf_from(cf1_order, "CF1"' in runner
    assert "permutation" in runner

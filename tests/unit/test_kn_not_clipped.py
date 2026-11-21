from pathlib import Path

from raven_mcs.sag.r1l_spec import k_n

ROOT = Path(__file__).resolve().parents[2]


def test_kn_not_clipped() -> None:
    conf = (ROOT / "src/raven_mcs/sag/r1l_conformal.py").read_text(encoding="utf-8")
    track = (ROOT / "src/raven_mcs/sag/r1m_track.py").read_text(encoding="utf-8")
    assert "min(k" not in conf
    assert "min(k_n" not in conf
    assert "clip" not in conf.lower() or "MUST NOT clip" in conf
    assert "min(k_n" not in track
    assert k_n(19) == 19
    assert k_n(18) == 19
    assert k_n(18) > 18

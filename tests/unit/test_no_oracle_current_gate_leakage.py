from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = [
    "src/raven_mcs/sag/r1m_features.py",
    "src/raven_mcs/sag/r1m_predictor.py",
    "src/raven_mcs/sag/r1m_track.py",
    "src/raven_mcs/sag/r1l_design.py",
]


def test_no_oracle_current_gate_leakage() -> None:
    blob = "\n".join((ROOT / p).read_text(encoding="utf-8") for p in FILES)
    assert "current_oracle_safe" not in blob
    feat = (ROOT / "src/raven_mcs/sag/r1m_features.py").read_text(encoding="utf-8")
    assert "oracle_safe" not in feat
    from raven_mcs.sag.r1l_design import DesignConfiguration, configured_decide_gate_and_design
    for hidden in (0,1):
        rec=configured_decide_gate_and_design({'certificate_state':'WARMUP','oracle_safe':hidden,'current_C':hidden,'current_mask':hidden},configuration=DesignConfiguration(True,'explicit_test'),window_id=0)
        assert rec['Design_t']==1 and rec['Gate_t']==0

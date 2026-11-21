from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_legacy_gate_absent_from_formal_path() -> None:
    design = (ROOT / "src/raven_mcs/sag/r1l_design.py").read_text(encoding="utf-8")
    assert "FORMAL_GATE_MODE" in design
    assert "dataset_name_controls_design" in design
    src = (ROOT / "src/raven_mcs/training/window_runner.py").read_text(encoding="utf-8")
    start = src.index("if mode == FORMAL_GATE_MODE:")
    end = src.index("LEGACY experiment / ablation path", start)
    formal = src[start:end]
    for banned in ("always_on", "always_off", "uses_design_ratio", "dataset_name", "gated_default"):
        assert banned not in formal
    audit = ROOT / "results_sag_g1/round_r1l_v12/audit/R1L_V12_LEGACY_GATE_AUDIT.csv"
    text = audit.read_text(encoding="utf-8")
    assert "formal_path" in text

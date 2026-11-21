from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_sensor_a040_audit_complete() -> None:
    csv = ROOT / "results_sag_g1/round_r1j/boundary_eval/R1J_SENSORSCOPE_A040_BOUNDARY_AUDIT.csv"
    md = ROOT / "results_sag_g1/round_r1j/boundary_eval/R1J_SENSORSCOPE_A040_BOUNDARY_SUMMARY.md"
    assert csv.is_file() and md.is_file()
    assert "false-safe" in md.read_text(encoding="utf-8").lower() or "false-safe" in md.read_text(encoding="utf-8")

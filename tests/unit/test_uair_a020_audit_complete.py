from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_uair_a020_audit_complete() -> None:
    assert (ROOT / "results_sag_g1/round_r1j/boundary_eval/R1J_UAIR_A020_BOUNDARY_AUDIT.csv").is_file()
    assert (ROOT / "results_sag_g1/round_r1j/boundary_eval/R1J_UAIR_A020_BOUNDARY_SUMMARY.md").is_file()

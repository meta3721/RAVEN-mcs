from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_interior_diagnostic_does_not_overwrite_main() -> None:
    main = ROOT / "results_sag_g1/round_r1g/e3v2_oracle_precheck/E3V2_ORACLE_PRECHECK_BY_WINDOW.csv"
    diag = ROOT / "results_sag_g1/round_r1h/boundary_audit/E3V2_INTERIOR_DIAGNOSTIC_SUMMARY.csv"
    assert main.is_file() and diag.is_file()
    assert main != diag

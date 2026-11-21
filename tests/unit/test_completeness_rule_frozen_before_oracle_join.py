from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]

def test_completeness_rule_frozen_before_oracle_join() -> None:
    src = (ROOT / "src/raven_mcs/experiments/run_sag_g1_r1h.py").read_text(encoding="utf-8")
    assert src.find("WINDOW_COMPLETENESS_RULE_V1.md") < src.find("E3V2_WINDOW_COMPLETENESS_AUDIT_NO_ORACLE.csv")
    blind = pd.read_csv(ROOT / "results_sag_g1/round_r1h/boundary_audit/E3V2_WINDOW_COMPLETENESS_AUDIT_NO_ORACLE.csv")
    assert "C_oracle_safe" not in blind.columns
    assert "oracle_safe" not in blind.columns

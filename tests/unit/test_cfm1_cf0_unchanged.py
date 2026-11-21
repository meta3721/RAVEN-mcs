from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]

def test_cfm1_cf0_unchanged() -> None:
    r1g = pd.read_csv(ROOT / "results_sag_g1/round_r1g/e3v1_counterfactual_diagnostics/E3V1_ROOT_CAUSE_COUNTERFACTUAL_SUMMARY.csv")
    r1h = pd.read_csv(ROOT / "results_sag_g1/round_r1h/matched_counterfactual/CFM1_ORACLE_COMPARISON.csv")
    for dataset in ("sensorscope", "uair"):
        g0 = float(r1g.loc[(r1g["dataset"] == dataset) & (r1g["cf_id"] == "CF0"), "mean_C_oracle_safe"].iloc[0])
        warm = r1h.loc[(r1h["dataset"] == dataset) & (r1h["is_warmup_eligible"] == True)]  # noqa: E712
        assert abs(float(warm["C_oracle_safe_CF0"].mean()) - g0) < 1e-6

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_cf0_matches_e3v1() -> None:
    r1f = pd.read_csv(ROOT / "results_sag_g1/round_r1f/oracle_ceiling/ORACLE_COVERAGE_CEILING_BY_WINDOW.csv")
    cf = pd.read_csv(ROOT / "results_sag_g1/round_r1g/e3v1_counterfactual_diagnostics/E3V1_ROOT_CAUSE_COUNTERFACTUAL.csv")
    for dataset in ("sensorscope", "uair"):
        a = r1f.loc[(r1f["dataset"] == dataset) & (r1f["is_warmup_eligible"] == True), "C_oracle_safe"].mean()  # noqa: E712
        b = cf.loc[(cf["dataset"] == dataset) & (cf["cf_id"] == "CF0"), "C_oracle_safe"].mean()
        assert abs(float(a) - float(b)) < 1e-9

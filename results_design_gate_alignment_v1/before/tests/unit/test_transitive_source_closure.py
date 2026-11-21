from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def test_transitive_source_closure() -> None:
    frame = pd.read_csv(
        ROOT / "results_sag_g1/round_r1l_v13/audit/R1L_V13_TRANSITIVE_SOURCE_CLOSURE.csv"
    )
    req = frame["required_for_formal_chain"].astype(str).str.lower().isin(["true", "1"])
    required = frame[req]
    assert not required.empty
    included = required["included_in_snapshot"].astype(str).str.lower().isin(["true", "1"])
    passed = required["pass"].astype(str).str.lower().isin(["true", "1"])
    assert bool(included.all())
    assert bool(passed.all())
    files = set(required["source_file"].astype(str))
    assert any("certificates.py" in f for f in files)
    assert any("aggregate_certificate.py" in f for f in files)
    assert any("window_runner.py" in f for f in files)
    assert any("method_policy.py" in f for f in files)

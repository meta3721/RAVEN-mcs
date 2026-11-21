"""Attribution layers use the frozen C_cov identity, not pair counts."""

from __future__ import annotations

import pandas as pd

from raven_mcs.experiments.run_sag_g1_r1e import attribute_windows
from raven_mcs.sag.certificates import c_cov_from_opportunity_lcb


def test_r1e_nonvacuity_attribution_identity() -> None:
    pred = pd.DataFrame(
        [
            {"dataset": "sensorscope", "window_id": 16, "cold_start": 0, "pi_tar": 0.8, "pi_hat_opp": 0.05, "lower_pi_opp": 0.02, "pi_opp_realized": 0.1, "q_max_residual": 0.03, "client": "a", "stratum": "s"},
            {"dataset": "sensorscope", "window_id": 16, "cold_start": 0, "pi_tar": 0.2, "pi_hat_opp": 0.001, "lower_pi_opp": 0.0, "pi_opp_realized": 0.0, "q_max_residual": 0.03, "client": "b", "stratum": "s"},
        ]
    )
    frame, summary = attribute_windows(pred, pi_safe=0.01, dataset="sensorscope")
    assert abs(float(frame.iloc[0]["C_real_support"]) - 0.8) < 1e-12
    assert abs(float(frame.iloc[0]["C_point"]) - 0.8) < 1e-12
    assert abs(float(frame.iloc[0]["C_lcb"]) - 0.8) < 1e-12
    lowers = {
        ("a", "s"): {"lower_pi_opp": 0.02},
        ("b", "s"): {"lower_pi_opp": 0.0},
    }
    formal = c_cov_from_opportunity_lcb({("a", "s"): 0.8, ("b", "s"): 0.2}, lowers, 0.01)
    assert abs(float(frame.iloc[0]["C_lcb"]) - float(formal["C_cov_LCB"])) < 1e-12
    assert summary["n_warmup"] == 1

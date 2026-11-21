"""PI_SAFE_RULE_V1 is q10 only."""

from __future__ import annotations

from raven_mcs.sag.certificates import provisional_pi_safe_from_public_opp
from raven_mcs.sag.target_law import PI_SAFE_RULE_V1, freeze_pi_safe_rule_v1


def test_r1e_pi_safe_rule_q10_frozen() -> None:
    assert PI_SAFE_RULE_V1["quantile"] == 0.10
    assert PI_SAFE_RULE_V1["rule_id"] == "PI_SAFE_RULE_V1"
    frozen = freeze_pi_safe_rule_v1(value_sensorscope=0.001, value_uair=0.002)
    assert frozen["quantile"] == 0.10
    masses = {("a", "s"): 0.04, ("b", "s"): 0.01, ("c", "s"): 0.02}
    pi = {k: 1.0 / 3.0 for k in masses}
    q10 = provisional_pi_safe_from_public_opp(pi, masses, quantile=0.10)
    q05 = provisional_pi_safe_from_public_opp(pi, masses, quantile=0.05)
    assert q10["pi_safe"] != q05["pi_safe"]
    assert frozen["quantile"] == 0.10

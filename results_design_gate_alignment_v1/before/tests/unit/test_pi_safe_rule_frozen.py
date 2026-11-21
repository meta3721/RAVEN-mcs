"""π_safe rule is frozen as PI_SAFE_RULE_V1; ON/OFF must not retune q."""

from __future__ import annotations

from raven_mcs.sag.certificates import provisional_pi_safe_from_public_opp
from raven_mcs.sag.target_law import PI_SAFE_RULE_V1, freeze_pi_safe_rule_v1, pi_safe_rule_hash


def test_pi_safe_rule_frozen() -> None:
    assert PI_SAFE_RULE_V1["rule_id"] == "PI_SAFE_RULE_V1"
    assert PI_SAFE_RULE_V1["quantile"] == 0.10
    assert "gate_ON_OFF" in PI_SAFE_RULE_V1["excludes"]
    assert "labels" in PI_SAFE_RULE_V1["excludes"]

    pi_target = {("k1", "s1"): 0.7, ("k2", "s2"): 0.3}
    pi_opp = {("k1", "s1"): 0.04, ("k2", "s2"): 0.01}
    a = provisional_pi_safe_from_public_opp(pi_target, pi_opp, quantile=0.10)
    _on_rate = 0.99
    b = provisional_pi_safe_from_public_opp(pi_target, pi_opp, quantile=0.10)
    assert a["pi_safe"] == b["pi_safe"]
    assert abs(a["pi_safe"] - _on_rate) > 0.5

    frozen = freeze_pi_safe_rule_v1(value_sensorscope=0.001, value_uair=0.002)
    assert frozen["frozen"] is True
    assert frozen["hash"] == pi_safe_rule_hash()
    assert frozen["quantile"] == 0.10
    assert frozen["rule_id"] == "PI_SAFE_RULE_V1"

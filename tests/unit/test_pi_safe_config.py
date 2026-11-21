"""π_safe must have an explicit provenance record."""

from __future__ import annotations

from raven_mcs.sag.certificates import provisional_pi_safe_from_public_opp


def test_pi_safe_has_source_record() -> None:
    pi_target = {("k1", "s1"): 0.7, ("k2", "s2"): 0.3}
    pi_opp = {("k1", "s1"): 0.04, ("k2", "s2"): 0.01, ("k3", "s3"): 0.95}
    rec = provisional_pi_safe_from_public_opp(pi_target, pi_opp, quantile=0.10)
    assert rec["status"] == "PI_SAFE_REQUIRES_FREEZE_DECISION"
    assert rec["frozen"] is False
    assert rec["source"]
    assert rec["pi_safe"] == rec["candidates"]["q10"]
    assert "q05" in rec["candidates"]
    assert "q25" in rec["candidates"]

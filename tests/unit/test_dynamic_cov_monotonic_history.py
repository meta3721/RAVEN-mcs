"""Growing F_{r-} history does not read the current window."""

from __future__ import annotations

from raven_mcs.sag.dynamic_cov import dynamic_lower_pi_opp


def _row(mass_a: float) -> dict:
    return {
        "opp_mass_by_pair": {"k|s": mass_a, "k2|s": 1.0 - mass_a},
        "opp_count_by_pair": {"k|s": mass_a * 10, "k2|s": (1.0 - mass_a) * 10},
        "opp_event_total": 10.0,
    }


def test_dynamic_cov_monotonic_history() -> None:
    pairs = [("k", "s"), ("k2", "s")]
    hist = [_row(0.4) for _ in range(16)]
    a = dynamic_lower_pi_opp(hist, pairs, lookback=8, delta=0.05, min_calib=8)
    longer = hist + [_row(0.4)]
    b = dynamic_lower_pi_opp(longer, pairs, lookback=8, delta=0.05, min_calib=8)
    assert a["n_calib"] >= 8
    assert b["n_calib"] == a["n_calib"] + 1
    current = _row(0.99)
    c = dynamic_lower_pi_opp(hist, pairs, lookback=8, delta=0.05, min_calib=8)
    assert c["lowers"][("k", "s")]["lower_pi_opp"] == a["lowers"][("k", "s")]["lower_pi_opp"]
    assert current["opp_mass_by_pair"]["k|s"] == 0.99

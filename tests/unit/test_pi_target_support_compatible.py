"""Support-compatible Design target (G1 Path A)."""

from __future__ import annotations

import pandas as pd

from raven_mcs.correction.pi_target import (
    build_pi_target,
    build_pi_target_support_compatible,
)


def _atomic() -> pd.DataFrame:
    rows = []
    # Client A: s0 in train+test, s1 train-only. Client B: s0 train+test.
    specs = [
        ("u0", "stA", "client-A", "s0", "test"),
        ("u1", "stA", "client-A", "s0", "train"),
        ("u2", "stA", "client-A", "s1", "train"),
        ("u3", "stB", "client-B", "s0", "test"),
        ("u4", "stB", "client-B", "s0", "train"),
    ]
    for uid, sid, _client, stratum, split in specs:
        rows.append(
            {
                "unit_id": uid,
                "spatial_id": sid,
                "opportunity_stratum": stratum,
                "target_group": 0 if stratum == "s0" else 1,
                "target_group_main": "g0" if stratum == "s0" else "g1",
                "split": split,
                "support_flag": True,
            }
        )
    return pd.DataFrame(rows)


def test_support_compatible_fills_train_only_stratum() -> None:
    atomic = _atomic()
    mapping = {"stA": "client-A", "stB": "client-B"}
    test = build_pi_target(atomic, mapping, split="test")
    test_map = {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in test.itertuples()
    }
    assert test_map[("client-A", "s1")] == 0.0

    pi_opp = {
        ("client-A", "s0"): 0.25,
        ("client-A", "s1"): 0.25,
        ("client-B", "s0"): 0.50,
    }
    sc = build_pi_target_support_compatible(
        atomic, mapping, split="test", pi_opp_joint=pi_opp
    )
    sc_map = {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in sc.itertuples()
    }
    assert abs(sum(sc_map.values()) - 1.0) < 1e-12
    assert sc_map[("client-A", "s1")] > 0.0
    assert sc_map[("client-A", "s1")] == 0.5 * 0.0 + 0.5 * 0.25
    assert all(v >= 0.0 for v in sc_map.values())

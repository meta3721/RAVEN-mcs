"""Paper h(i) map is frozen and shared across methods/seeds/windows."""

from __future__ import annotations

from raven_mcs.sag.deployment_groups import N_H_GROUPS, build_paper_h_payload, unit_to_h


def _toy_atomic():
    import pandas as pd

    times = pd.to_datetime(
        [
            "2020-01-01T01:00:00Z",
            "2020-01-01T07:00:00Z",
            "2020-01-01T13:00:00Z",
            "2020-01-01T19:00:00Z",
        ],
        utc=True,
    )
    return pd.DataFrame({
        "unit_id": ["u0", "u1", "u2", "u3"],
        "absolute_time": times,
        "split": ["train", "train", "train", "train"],
        "support_flag": [True, True, True, True],
        "target_group": ["fine0", "fine1", "fine2", "fine3"],
        "opportunity_stratum": ["s0", "s1", "s2", "s3"],
        "spatial_id": ["n0", "n1", "n2", "n3"],
        "time_index": [0, 1, 2, 3],
    })


def test_h_map_independent_of_method_seed_window() -> None:
    atomic = _toy_atomic()
    a = unit_to_h(build_paper_h_payload(atomic, dataset="toy"))
    b = unit_to_h(build_paper_h_payload(atomic, dataset="toy"))
    assert a == b
    assert a["u0"] == 0
    assert a["u1"] == 1
    assert a["u2"] == 2
    assert a["u3"] == 3
    assert set(a.values()) <= set(range(N_H_GROUPS))

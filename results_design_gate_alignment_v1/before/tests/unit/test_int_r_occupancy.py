"""INT-R occupancy unit tests. Smoke only; not ranking evidence."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from raven_mcs.e3.int_r.occupancy import (
    CALIBRATION_SEED,
    OccupancySpec,
    STABILITY_SEEDS,
    occupancy_metrics,
    occupancy_rng,
    simulate_occupancy,
    stability_screen,
)
from raven_mcs.e3.real_runner.generator_r3 import generate_complete_aligned_r3


def _atomic() -> tuple[pd.DataFrame, dict[str, str]]:
    rows = []
    for split, t0 in (("train", 0), ("test", 10)):
        for i, spatial in enumerate(["n0", "n1"]):
            for block in (0, 2):
                t = t0 + block
                uid = f"{spatial}_t{t:05d}"
                rows.append(
                    {
                        "unit_id": uid,
                        "spatial_id": spatial,
                        "absolute_time": pd.Timestamp("2020-01-01", tz="UTC")
                        + pd.Timedelta(hours=int(t)),
                        "time_index": int(t),
                        "target_value": 1.0 + i,
                        "split": split,
                        "target_group": f"{spatial}::block{block}",
                        "opportunity_stratum": f"{spatial}::block{block}::weekday",
                    }
                )
    return pd.DataFrame(rows), {"n0": "client-000", "n1": "client-001"}


def _strip_occ(events: pd.DataFrame) -> pd.DataFrame:
    out = events.copy()

    def _drop(feat):
        feat = dict(feat)
        feat.pop("occupancy_A", None)
        return feat

    out["opportunity_features"] = out["opportunity_features"].map(_drop)
    return out.sort_values(["window_id", "client_id"]).reset_index(drop=True)


def test_always_on_r3_draws_match_when_occupancy_forced_one() -> None:
    atomic, mapping = _atomic()
    kwargs = dict(
        dataset="sensorscope",
        atomic=atomic,
        spatial_to_client=mapping,
        seed=31001,
        num_windows=3,
        m_mc=8,
    )
    t0, _, _, _ = generate_complete_aligned_r3(**kwargs, occupancy_spec=None)
    forced = OccupancySpec(family="two_state_markov", alpha=1.0, beta=0.0, rho0=1.0)
    t1, _, _, audit = generate_complete_aligned_r3(**kwargs, occupancy_spec=forced)
    assert int(audit["n_event_rows"]) == int(audit["n_client_windows"])
    a = _strip_occ(t0.events)
    b = _strip_occ(t1.events)
    pd.testing.assert_frame_equal(a, b, check_dtype=False)


def test_inactive_client_windows_have_no_event_rows() -> None:
    atomic, mapping = _atomic()
    spec = OccupancySpec(family="bernoulli_iid", alpha=0.0, beta=1.0, rho0=0.3)
    trace, _, _, audit = generate_complete_aligned_r3(
        dataset="sensorscope",
        atomic=atomic,
        spatial_to_client=mapping,
        seed=31001,
        num_windows=6,
        m_mc=8,
        occupancy_spec=spec,
    )
    assert int(audit["n_event_rows"]) < int(audit["n_client_windows"])
    A = audit["occupancy_matrix"]
    clients = audit["occupancy_client_ids"]
    present = set(zip(trace.events["client_id"].astype(str), trace.events["window_id"].astype(int)))
    for t in range(A.shape[0]):
        for j, cid in enumerate(clients):
            key = (str(cid), int(t))
            if int(A[t, j]) == 0:
                assert key not in present
                # no empty risk-set row either
            else:
                assert key in present
                row = trace.events[
                    (trace.events["client_id"].astype(str) == cid)
                    & (trace.events["window_id"] == t)
                ].iloc[0]
                assert int(row["opportunity_features"]["occupancy_A"]) == 1


def test_occupancy_module_has_no_label_leakage_strings() -> None:
    src = Path(__file__).resolve().parents[2] / "src" / "raven_mcs" / "e3" / "int_r" / "occupancy.py"
    text = src.read_text(encoding="utf-8").lower()
    for banned in ("rmse", "y_i", "test_error", "residual"):
        assert banned not in text


def test_occupancy_rng_independent_of_r3_seed_offset() -> None:
    a = occupancy_rng("sensorscope", 30001)
    b = occupancy_rng("sensorscope", 30001)
    spec = OccupancySpec(family="two_state_markov", alpha=0.8, beta=0.7, rho0=0.425)
    A1 = simulate_occupancy(n_clients=8, n_windows=20, spec=spec, rng=a)
    A2 = simulate_occupancy(n_clients=8, n_windows=20, spec=spec, rng=b)
    assert np.array_equal(A1, A2)
    met = occupancy_metrics(A1)
    assert 0.0 < met["mean_active_frac"] < 1.0
    assert met["n_windows"] == 20
    assert CALIBRATION_SEED == 29999


def test_stability_seeds_are_frozen_dummy_family() -> None:
    assert STABILITY_SEEDS == tuple(range(28001, 28021))
    assert len(STABILITY_SEEDS) == 20
    assert 31001 not in STABILITY_SEEDS
    table_seed = 30_000 + 1
    assert table_seed not in STABILITY_SEEDS


def test_occupancy_module_has_no_e3_table_seed_literal() -> None:
    src = Path(__file__).resolve().parents[2] / "src" / "raven_mcs" / "e3" / "int_r" / "occupancy.py"
    text = src.read_text(encoding="utf-8")
    assert "30001" not in text
    lower = text.lower()
    for banned in ("rmse", "y_i", "test_error", "residual"):
        assert banned not in lower


def test_stability_screen_returns_forty_checks() -> None:
    spec = OccupancySpec(family="two_state_markov", alpha=0.8, beta=0.8, rho0=0.425)
    out = stability_screen(
        spec=spec,
        n_clients=8,
        n_windows_by_dataset={"sensorscope": 100, "uair": 80},
    )
    assert int(out["n_checks"]) == 40
    assert 0 <= int(out["hits"]) <= 40
    assert np.isfinite(out["mean_rho"])

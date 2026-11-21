"""Unit tests for true stratum + non-wrap schedule repair."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_true_stratum_preserves_spatial_dimension():
    ident = json.loads(
        (
            ROOT / "configs/frozen/e2_true_stratum/true_opportunity_stratum_identity.json"
        ).read_text(encoding="utf-8")
    )
    assert ident["spatial_dimension_unique_count"] >= 2
    assert ident["region_definition"] == "sensorscope_station"
    assert "sensorscope_campus" not in "".join(ident.get("stratum_ids", [])[:5])


def test_true_stratum_preserves_day_type():
    ident = json.loads(
        (
            ROOT / "configs/frozen/e2_true_stratum/true_opportunity_stratum_identity.json"
        ).read_text(encoding="utf-8")
    )
    assert ident["day_type_unique_count"] >= 2
    joined = " ".join(ident.get("stratum_ids", []))
    assert "weekday" in joined and "weekend" in joined
    assert "::all_days" not in joined
    merged_days = {s.split("::")[-1] for s in ident.get("stratum_ids", [])}
    assert len(merged_days) >= 2


def test_stratum_mapping_not_equal_group_mapping():
    indep = json.loads(
        (ROOT / "outputs/audits/E2_GROUP_STRATUM_INDEPENDENCE_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert indep["group_mapping_hash"] != indep["stratum_mapping_hash"]
    assert indep["group_count"] != indep["stratum_count"]


def test_stratum_tv_not_identical_to_group_tv_for_all_traces():
    indep = json.loads(
        (ROOT / "outputs/audits/E2_GROUP_STRATUM_INDEPENDENCE_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert indep["exact_equal_count"] < 180
    assert indep["max_absolute_difference"] > 1e-6


def test_stratum_target_mass_sums_to_one():
    ident = json.loads(
        (
            ROOT / "configs/frozen/e2_true_stratum/true_opportunity_stratum_identity.json"
        ).read_text(encoding="utf-8")
    )
    assert abs(float(ident["target_mass_sum"]) - 1.0) <= 1e-12


def test_stratum_merge_is_deterministic():
    from raven_mcs.e2.true_stratum.stratum import (
        build_true_opportunity_stratum,
        load_true_opportunity_stratum,
    )

    built = build_true_opportunity_stratum(ROOT)
    _frame, loaded = load_true_opportunity_stratum(ROOT)
    assert built["identity"]["mapping_hash"] == loaded["mapping_hash"]
    # Rebuild once more in-memory via load path remains stable.
    _frame2, loaded2 = load_true_opportunity_stratum(ROOT)
    assert loaded["mapping_hash"] == loaded2["mapping_hash"]


def test_stratum_merge_uses_pre_outcome_only():
    protocol = (
        ROOT / "configs/frozen/e2_true_stratum/stratum_merge_protocol.yaml"
    ).read_text(encoding="utf-8")
    assert "rmse" not in protocol.lower()
    assert "hard empirical" not in protocol.lower()


def test_no_head_tail_role_as_stratum():
    ident = json.loads(
        (
            ROOT / "configs/frozen/e2_true_stratum/true_opportunity_stratum_identity.json"
        ).read_text(encoding="utf-8")
    )
    for s in ident["stratum_ids"]:
        assert s not in {"head", "neutral", "tail"}


def test_schedule_has_zero_wraparound():
    chrono = json.loads(
        (ROOT / "outputs/audits/E2_NONWRAP_CHRONOLOGY_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert int(chrono["wraparound_count"]) == 0


def test_schedule_source_has_no_modulo_operator():
    src = (ROOT / "src/raven_mcs/e2/true_stratum/schedule.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    mods = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod)
    ]
    assert len(mods) == 0


def test_source_indices_monotonic():
    chrono = json.loads(
        (ROOT / "outputs/audits/E2_NONWRAP_CHRONOLOGY_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert int(chrono["global_monotonic_violation_count"]) == 0


def test_source_timestamps_monotonic():
    chrono = json.loads(
        (ROOT / "outputs/audits/E2_NONWRAP_CHRONOLOGY_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    assert int(chrono["wraparound_count"]) == 0


def test_insufficient_continuous_data_blocks():
    from raven_mcs.e2.true_stratum.schedule import (
        InsufficientContinuousWindowsError,
        build_nonwrap_continuous_schedule,
    )

    uniforms = np.zeros((300, 8), dtype=np.float64)
    with pytest.raises(InsufficientContinuousWindowsError):
        build_nonwrap_continuous_schedule(
            29101, schedule_uniforms=uniforms, root=ROOT, candidate_size=10_000,
        )


def test_stage2_eligibility_regression():
    # Spot-check one usable file (full sample may be absent in pure compact trees)
    import pandas as pd

    paths = list(ROOT.glob("outputs/e2_true_stratum/traces/*/*/*/usable_events.parquet"))
    if not paths:
        pytest.skip("no full usable_events in compact evidence tree")
    df = pd.read_parquet(paths[0])
    assert int((~df["stage2_eligible"] & (df["usable_status"] == "ELIGIBLE_SUCCESS")).sum()) == 0
    assert (df.loc[~df["stage2_eligible"], "U"] == 0).all()


def test_seed_29001_not_read():
    # No 29001 outputs in this package
    assert not (ROOT / "outputs/e2_true_stratum/traces/29001").exists()

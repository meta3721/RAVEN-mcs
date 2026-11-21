"""Unit tests for E3 Canary R1 core helpers."""

from __future__ import annotations

from raven_mcs.e3.canary.constants import CANARY_SEED, FORMAL_SEEDS, PHASE1, PHASE2
from raven_mcs.e3.canary.schedule import build_canary_matrix
from raven_mcs.e3.canary.seed_audit import audit_canary_seed
from raven_mcs.e3.canary.traffic_reuse_guard import (
    CanaryTrafficSealedMethodBlocked,
    assert_canary_schedulable,
    build_traffic_reuse_guard_evidence,
)


def test_canary_seed_disjoint() -> None:
    audit = audit_canary_seed(CANARY_SEED)
    assert audit["status"] == "PASS"
    assert CANARY_SEED not in FORMAL_SEEDS


def test_matrix_has_28_and_skips_traffic_sealed_five() -> None:
    matrix = build_canary_matrix()
    assert matrix["n_logical_runs"] == 28
    assert len(PHASE1) == 11
    assert len(PHASE2) == 17
    traffic = [r for r in matrix["rows"] if r["dataset"] == "traffic"]
    assert len(traffic) == 6
    sealed = set(matrix["traffic_do_not_rerun"])
    assert not any(r["method"] in sealed for r in traffic)


def test_traffic_reuse_guard_blocks_sealed_five() -> None:
    evidence = build_traffic_reuse_guard_evidence()
    assert evidence["duplicate_blocked"] is True
    try:
        assert_canary_schedulable(dataset="traffic", method="raven", seed=CANARY_SEED)
        raise AssertionError("expected block")
    except CanaryTrafficSealedMethodBlocked:
        pass

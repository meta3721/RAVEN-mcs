"""E3 EventTrace hash stable vs R1e provenance."""

from __future__ import annotations

from pathlib import Path

from raven_mcs.experiments.sag_runtime import attach_unified_target, prepare_sag_bundle

ROOT = Path(__file__).resolve().parents[2]
SEED = 30001


def test_r1f_e3_trace_hash_frozen() -> None:
    for dataset in ("sensorscope", "uair"):
        prepared = attach_unified_target(
            prepare_sag_bundle(root=ROOT, dataset=dataset, seed=SEED),
            root=ROOT,
        )
        trace_hash = str(prepared["identity"].get("trace_hash"))
        assert len(trace_hash) == 64
        prepared2 = attach_unified_target(
            prepare_sag_bundle(root=ROOT, dataset=dataset, seed=SEED),
            root=ROOT,
        )
        assert str(prepared2["identity"].get("trace_hash")) == trace_hash

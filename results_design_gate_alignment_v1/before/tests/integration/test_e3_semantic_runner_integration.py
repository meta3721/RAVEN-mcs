"""Integration: call the same run_e3_unified entry used by future Canary."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from raven_mcs.e3.semantic_alignment.constants import CANARY_SEED
from raven_mcs.e3.semantic_alignment.runner import REQUIRED_METRIC_FIELDS, run_e3_unified

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts/e3_semantic_alignment_and_runner_integration_closure_r1"


def test_run_e3_unified_emits_pair_and_metrics(tmp_path):
    ds = "uair"
    target = json.loads((ART / "E3_UAIR_TARGET_SEMANTICS_R2.json").read_text(encoding="utf-8"))
    atomic = pd.read_parquet(ROOT / "data/processed/uair/atomic_units.parquet")
    unit_to_group = {str(r.unit_id): str(r.target_group) for r in atomic.itertuples(index=False)}
    et_dir = ART / "eventtraces" / ds / f"seed{CANARY_SEED}" / "training_eventtrace"
    out = run_e3_unified(
        root=ROOT,
        run_dir=tmp_path / "run",
        dataset=ds,
        seed=CANARY_SEED,
        method="local_hajek",
        eventtrace_dir=et_dir,
        target_mu=target["mu"],
        unit_to_group=unit_to_group,
        mode="semantic_dry",
        ledger_path=tmp_path / "ledger.jsonl",
    )
    assert out["status"] == "PAIR_STATE_RUNNER_INTEGRATED"
    assert (tmp_path / "run" / "pair_state.parquet").is_file()
    metrics = json.loads((tmp_path / "run" / "final_metrics.json").read_text(encoding="utf-8"))
    for field in REQUIRED_METRIC_FIELDS:
        assert field in metrics
    ledger = (tmp_path / "ledger.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert any('"event": "START"' in line or '"event":"START"' in line for line in ledger)
    assert any('"event": "FINISH"' in line or '"event":"FINISH"' in line for line in ledger)

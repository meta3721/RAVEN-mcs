"""Index sealed E2 Traffic records as formal evidence without execution."""
from __future__ import annotations
import json
from pathlib import Path
from .metric_scale import convert_metrics
from raven_mcs.utils.serialization import dump_json

def index_reused(root: Path, art: Path, traffic_policy: dict) -> list[dict]:
    manifest = json.loads((root / "artifacts/e3_protocol_reuse_and_readiness_r1/E3_REUSED_E2_TRAFFIC_BLOCK_MANIFEST.json").read_text(encoding="utf-8"))
    rows = []
    for rec in manifest["records"]:
        metrics = json.loads(Path(rec["result_path"]).read_text(encoding="utf-8"))
        rows.append({"dataset": "traffic", "kind": "reused", "seed": rec["seed"], "method": rec["method"],
          "provenance": {"source_experiment": "E2-TRAFFIC", "result_path": rec["result_path"], "result_hash": rec["result_hash"]},
          "metrics": convert_metrics(metrics, traffic_policy)})
    if len(rows) != 100: raise ValueError(f"expected 100 sealed records, got {len(rows)}")
    dump_json({"records": rows, "n_reused": len(rows), "execution": "NOT_RERUN"}, art / "reused_traffic" / "E3_REUSED_TRAFFIC_EVIDENCE_INDEX.json")
    return rows

#!/usr/bin/env python3
"""Prepare E3 formal evidence; intentionally does not execute formal runs."""
from __future__ import annotations
import csv, json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.e3.canary.dataset_load import load_paper_dataset, verify_dataset_hash
from raven_mcs.e3.formal.constants import FORMAL_SEEDS, art_path
from raven_mcs.e3.formal.eventtrace import link_traffic_e2_trace
from raven_mcs.e3.formal.matrix import build_formal_matrix
from raven_mcs.e3.formal.metric_scale import policy
from raven_mcs.e3.formal.reuse import index_reused
from raven_mcs.utils.serialization import dump_json
ART = art_path(ROOT)
def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    hashes = {d: verify_dataset_hash(ROOT, d) for d in ("sensorscope", "uair", "traffic")}
    policies = {d: policy(d, sigma=getattr(load_paper_dataset(ROOT,d), "target_std", None)) for d in ("sensorscope","uair","traffic")}
    traffic_reused = policy("traffic", reused=True, sigma=getattr(load_paper_dataset(ROOT,"traffic"), "target_std", None))
    dump_json(hashes, ART/"E3_FORMAL_DATASET_HASH_AUDIT.json"); dump_json(policies, ART/"E3_FORMAL_METRIC_SCALE_POLICY.json"); dump_json(traffic_reused, ART/"E3_TRAFFIC_REUSED_METRIC_SCALE_POLICY.json")
    audit = [link_traffic_e2_trace(ROOT, ART, seed) | {"seed": seed} for seed in FORMAL_SEEDS]
    with (ART/"E3_TRAFFIC_EVENTTRACE_REUSE_AUDIT.csv").open("w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=sorted({k for r in audit for k in r})); w.writeheader(); w.writerows(audit)
    dump_json({"rows": audit, "status": "PASS_NO_REGENERATION"}, ART/"E3_TRAFFIC_EVENTTRACE_REUSE_AUDIT.json")
    dump_json({"rows":[{"dataset":d,"seed":s,"status":"LAZY_ON_EXECUTION"} for d in ("sensorscope","uair") for s in FORMAL_SEEDS] + audit}, ART/"E3_FORMAL_EVENTTRACE_MANIFEST.json")
    dump_json(build_formal_matrix(), ART/"E3_FORMAL_RUN_MATRIX.json"); index_reused(ROOT, ART, traffic_reused)
    dump_json({"round":"E3-FORMAL-RUNS-R1","phase":0,"status":"PHASE0_READY","formal_execution_started":False,"created_utc":datetime.now(timezone.utc).isoformat()}, ART/"E3_FORMAL_RUNS_STOP_STATUS.json")
    return 0
if __name__ == "__main__": raise SystemExit(main())

#!/usr/bin/env python3
"""E3C-G1..G25 multidataset protocol closure gates."""
from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd

from raven_mcs.e3.protocol_closure.constants import CANARY_SEED, EPS_ZERO, FORMAL_SEEDS, M_MC
from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_multidataset_protocol_closure_r1"
E2_STOP = ROOT / "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1/STOP_STATUS.json"


def _junit_ok(path: Path) -> bool:
    if not path.is_file():
        return False
    root = ET.parse(path).getroot()
    suites = root.findall(".//testsuite") or ([root] if root.tag == "testsuite" else [])
    if not suites:
        return False
    return all(int(s.attrib.get("failures", 0)) == 0 and int(s.attrib.get("errors", 0)) == 0 for s in suites)


def main() -> int:
    reuse = json.loads((ART / "E3_TRAFFIC_REUSE_FINAL_MANIFEST.json").read_text(encoding="utf-8"))
    ss = json.loads((ART / "E3_SENSORSCOPE_PROTOCOL.json").read_text(encoding="utf-8"))
    ua = json.loads((ART / "E3_UAIR_PROTOCOL.json").read_text(encoding="utf-8"))
    tr = json.loads((ART / "E3_TRAFFIC_PROTOCOL.json").read_text(encoding="utf-8"))
    ss_h = json.loads((ART / "E3_SENSORSCOPE_HORIZON_AUDIT.json").read_text(encoding="utf-8"))
    ua_h = json.loads((ART / "E3_UAIR_HORIZON_AUDIT.json").read_text(encoding="utf-8"))
    traffic_new = json.loads((ART / "E3_TRAFFIC_NEW_METHOD_PROTOCOL.json").read_text(encoding="utf-8"))
    pair = json.loads((ART / "E3_PAIR_METRIC_DEFINITION.json").read_text(encoding="utf-8"))
    schema = json.loads((ART / "E3_PAIR_STATE_SCHEMA_V1.json").read_text(encoding="utf-8"))
    metrics = json.loads((ART / "E3_METRIC_OUTPUT_SCHEMA.json").read_text(encoding="utf-8"))
    delta_g = json.loads((ART / "E3_DELTA_GROUP_DEFINITION.json").read_text(encoding="utf-8"))
    oracle = json.loads((ART / "E3_SIMORACLE_PROTOCOL.json").read_text(encoding="utf-8"))
    central = json.loads((ART / "E3_CENTRAL_REFERENCE_PROTOCOL.json").read_text(encoding="utf-8"))
    flamf = json.loads((ART / "E3_FLAMF_STATUS.json").read_text(encoding="utf-8"))
    canon = json.loads((ART / "E3_METHOD_CANONICALIZATION.json").read_text(encoding="utf-8"))
    hashes = json.loads((ART / "E3_METHOD_SOURCE_HASHES.json").read_text(encoding="utf-8"))
    seeds = json.loads((ART / "E3_FORMAL_SEED_FREEZE.json").read_text(encoding="utf-8"))
    matrix = json.loads((ART / "E3_METHOD_MATRIX_FINAL.json").read_text(encoding="utf-8"))
    canary = json.loads((ART / "E3_REAL_RUNNER_CANARY_PLAN_FINAL.json").read_text(encoding="utf-8"))
    ledger = json.loads((ART / "E3_LEDGER_SCHEMA_V1.json").read_text(encoding="utf-8"))
    stats = json.loads((ART / "E3_STATISTICAL_PROTOCOL_FINAL.json").read_text(encoding="utf-8"))
    stop = json.loads((ART / "E3_MULTIDATASET_PROTOCOL_CLOSURE_STOP_STATUS.json").read_text(encoding="utf-8"))

    e2_ok = E2_STOP.is_file() and json.loads(E2_STOP.read_text(encoding="utf-8")).get("status") == "E2_TRAFFIC_SCIENTIFICALLY_SEALED"
    g1 = e2_ok

    blocked = False
    try:
        assert_schedulable_e3_run(dataset="traffic", scenario="complete_aligned", seed=30001, method="raven")
    except DuplicateReusedTrafficRunBlocked:
        blocked = True
    g2 = int(reuse.get("reusable_run_count", 0)) == 100 and blocked and len(reuse.get("records", [])) == 100

    g3 = ss.get("readiness_status", "").startswith("READY") and "data_identity" in ss and ss["data_identity"].get("spatial_units") == 55
    g4 = ss.get("complete_aligned_generator", {}).get("status") in {"READY", "READY_REUSE_E2"}
    g5 = ss_h.get("status", "").startswith("READY") and int(ss_h.get("chosen_E3_formal_windows", 0)) > 0

    g6 = ua.get("readiness_status", "").startswith("READY") and ua["data_identity"].get("spatial_units") == 36
    g7 = ua.get("complete_aligned_generator", {}).get("status") in {"READY", "READY_REUSE_E2"}
    g8 = ua_h.get("status", "").startswith("READY") and int(ua_h.get("chosen_E3_formal_windows", 0)) > 0

    g9 = len(traffic_new.get("rows", [])) >= 10 and tr.get("readiness_status", "").startswith("READY")
    g10 = pair.get("status") == "PAIR_METRIC_READY" and "Delta_pair" in pair
    g11 = "required_columns" in schema and _junit_ok(ROOT / "logs/e3_multidataset_protocol_closure_unit.xml")
    g12 = (
        "omega_hat" in str(delta_g.get("formula", ""))
        and "mu" in str(delta_g.get("formula", ""))
        and any(m["metric"] == "MAE_mu" for m in metrics.get("metrics", []))
        and any(m["metric"] == "Tail_RMSE" for m in metrics.get("metrics", []))
        and any(m["metric"] == "delta_ref" for m in metrics.get("metrics", []))
    )
    g13 = oracle.get("M_MC") == M_MC and Path(ART / "E3_SIMORACLE_READINESS.csv").is_file()
    g14 = central.get("status") in {"CENTRAL_REFERENCE_READY", "CENTRAL_REFERENCE_BLOCKED"}
    g15 = flamf.get("status") == "EXCLUDED_WITH_REASON"
    g16 = canon.get("n_canonical_semantic_methods") == len(canon.get("canonical_methods", [])) and any(
        a.get("alias") == "timealign_agg" and a.get("classification") == "ALIAS_ONLY" for a in canon.get("aliases", [])
    )
    g17 = isinstance(hashes.get("methods"), dict) and hashes["methods"].get("raven", {}).get("implementation_hash")
    g18 = list(seeds.get("formal_seeds")) == FORMAL_SEEDS and seeds.get("canary_seed") == CANARY_SEED and seeds.get("execute_canary_this_round") is False
    g19 = "NEW_RUNS_REQUIRED" in matrix.get("totals", {}) and int(matrix["totals"].get("REUSED_TRAFFIC_RUNS", 0)) == 100
    g20 = canary.get("execute_in_this_round") is False and set(canary.get("datasets", {})) >= {"sensorscope", "uair", "traffic"}
    g21 = "attempt_id" in ledger.get("START_fields", []) and ledger.get("attempt_integrity", {}).get("duplicate_START_visible") is True
    g22 = stats.get("EPS_ZERO") == EPS_ZERO and stats.get("primary_metric") == "RMSE_mu"
    g23 = bool(stop.get("no_training")) and stop.get("canary_executed") is False and not any(ART.rglob("*.pt"))
    g24 = _junit_ok(ROOT / "logs/e3_multidataset_protocol_closure_unit.xml")
    # G25 checked after hash finalization; if missing yet, fail
    hv = ART / "E3_CLOSURE_HASH_VERIFICATION.json"
    g25 = hv.is_file() and json.loads(hv.read_text(encoding="utf-8")).get("mismatch_count") == 0

    vals = [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12, g13, g14, g15, g16, g17, g18, g19, g20, g21, g22, g23, g24, g25]
    gates = {f"E3C-G{i}": bool(v) for i, v in enumerate(vals, start=1)}
    dump_json(gates, ART / "gate_results.json")
    dump_json({"failed": [k for k, v in gates.items() if not v]}, ART / "gate_diagnostics.json")
    failed = [k for k, v in gates.items() if not v]
    print(json.dumps({"all_pass": len(failed) == 0, "failed": failed, "gates": gates}, indent=2))
    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

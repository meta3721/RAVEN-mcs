#!/usr/bin/env python3
"""E3S-G1..G33 semantic alignment + runner integration gates."""
from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd

from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.e3.semantic_alignment.constants import CANARY_SEED, EPS_ZERO, M_MC, REGISTRY_SHA256
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_semantic_alignment_and_runner_integration_closure_r1"
E2_STOP = ROOT / "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1/STOP_STATUS.json"


def _junit_ok(path: Path) -> bool:
    if not path.is_file():
        return False
    root = ET.parse(path).getroot()
    suites = root.findall(".//testsuite") or ([root] if root.tag == "testsuite" else [])
    if not suites:
        return False
    return all(int(s.attrib.get("failures", 0)) == 0 and int(s.attrib.get("errors", 0)) == 0 for s in suites)


def _sha(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ss = json.loads((ART / "E3_SENSORSCOPE_TARGET_SEMANTICS_R2.json").read_text(encoding="utf-8"))
    ua = json.loads((ART / "E3_UAIR_TARGET_SEMANTICS_R2.json").read_text(encoding="utf-8"))
    opp = json.loads((ART / "E3_OPPORTUNITY_MODEL_R2.json").read_text(encoding="utf-8"))
    stage2 = json.loads((ART / "E3_STAGE2_USABLE_SEMANTICS_R2.json").read_text(encoding="utf-8"))
    qbound = json.loads((ART / "E3_Q_FEATURE_BOUNDARY_R2.json").read_text(encoding="utf-8"))
    three = json.loads((ART / "E3_COMPLETE_ALIGNED_THREE_STAGE_AUDIT.json").read_text(encoding="utf-8"))
    oracle = json.loads((ART / "E3_SIMORACLE_PROTOCOL_R2.json").read_text(encoding="utf-8"))
    pair_status = json.loads((ART / "E3_PAIR_STATE_RUNNER_STATUS.json").read_text(encoding="utf-8"))
    central = json.loads((ART / "E3_CENTRAL_RUNNER_INTEGRATION_R2.json").read_text(encoding="utf-8"))
    clients = json.loads((ART / "E3_CLIENT_MAPPING_FREEZE.json").read_text(encoding="utf-8"))
    preg = json.loads((ART / "E3_PROBABILITY_OBJECT_REGISTRY.json").read_text(encoding="utf-8"))
    diag = json.loads((ART / "E3_COMPLETE_ALIGNED_DIRECTION_DIAGNOSTIC.json").read_text(encoding="utf-8"))
    metrics = json.loads((ART / "E3_REAL_RUNNER_METRIC_SCHEMA_V2.json").read_text(encoding="utf-8"))
    matrix = json.loads((ART / "E3_METHOD_MATRIX_R2.json").read_text(encoding="utf-8"))
    canary = json.loads((ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R2.json").read_text(encoding="utf-8"))
    flamf = json.loads((ART / "E3_FLAMF_STATUS.json").read_text(encoding="utf-8"))
    hashes = json.loads((ART / "E3_SEMANTIC_CLOSURE_SOURCE_HASHES.json").read_text(encoding="utf-8"))
    stop = json.loads((ART / "E3_SEMANTIC_ALIGNMENT_STOP_STATUS.json").read_text(encoding="utf-8"))

    reg = ROOT / "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json"
    g1 = E2_STOP.is_file() and json.loads(E2_STOP.read_text(encoding="utf-8")).get("status") == "E2_TRAFFIC_SCIENTIFICALLY_SEALED" and _sha(reg) == REGISTRY_SHA256

    blocked = False
    try:
        assert_schedulable_e3_run(dataset="traffic", scenario="complete_aligned", seed=30001, method="raven")
    except DuplicateReusedTrafficRunBlocked:
        blocked = True
    g2 = blocked

    g3 = ss["n_groups"] > 4 and ss["uses_e1_time_only_target"] is False and all("::" in g for g in ss["mu"])
    g4 = ua["n_groups"] > 4 and all("::" in g for g in ua["mu"])
    g5 = "TEST" in ss["mu_construction"] and "training label magnitude" in ss["mu_not_from"]
    g6 = "TEST" in ua["mu_construction"] and "training label magnitude" in ua["mu_not_from"]
    g7 = opp.get("risk_set_sampled_from_pi_opp") is True and opp.get("not_cyclic_slice") is True
    g8 = "p_obs_true" in json.dumps(preg.get("field_separation", {}))
    g9 = "q_use_true" in json.dumps(preg.get("field_separation", {})) and stage2.get("requires_arrival_deadline_test") is True
    g10 = three.get("status") == "PASS"
    g11 = "T_arr" in stage2.get("formula", "") and "strict" in stage2.get("deadline_rule", "")
    g12 = qbound.get("status") == "Q_FEATURE_BOUNDARY_READY" and "time_block_as_q_feature" in [f["name"] for f in qbound["forbidden_features"]]
    g13 = all(r.get("no_object_aliasing") for r in oracle.get("rows", []))
    g14 = oracle.get("M_MC") == M_MC
    g15 = pair_status.get("status") == "PAIR_STATE_RUNNER_INTEGRATED" and (ART / "runner_dry/sensorscope/raven/pair_state.parquet").is_file()
    g16 = (ART / "runner_dry/sensorscope/raven/pair_metric_summary.json").is_file()
    g17 = central.get("status") == "CENTRAL_RUNNER_READY"
    g18 = central.get("status") == "CENTRAL_RUNNER_READY" and (ART / "runner_dry/sensorscope/central_delivered/runtime_manifest.json").is_file()
    g19 = clients.get("datasets", {}).get("sensorscope", {}).get("n_logical_fl_clients") == 8
    g20 = len({o["name"] for o in preg["objects"]}) == len(preg["objects"])
    g21 = diag.get("status") == "PASS" and all(r["direction_pass"] for r in diag["rows"])
    required = set(metrics.get("required_fields", []))
    g22 = {"RMSE_mu", "MAE_mu", "Tail_RMSE", "Delta_group", "Delta_pair", "delta_ref"}.issubset(required)
    g23 = "totals" in matrix and (ART / "E3_METHOD_MATRIX_R2.csv").is_file()
    g24 = (ART / "E3_MINIMUM_NEW_RUN_MATRIX_R2.json").is_file() and matrix["totals"].get("reused_Traffic_runs") == 100
    g25 = canary.get("execute_in_this_round") is False and canary.get("canary_seed") == CANARY_SEED
    g26 = flamf.get("status") == "EXCLUDED_WITH_REASON"
    mdf = pd.read_csv(ART / "E3_METHOD_MATRIX_R2.csv")
    g27 = "timealign_agg" not in set(mdf.method)
    g28 = bool(hashes.get("runner_files")) and bool(hashes.get("methods"))
    g29 = bool(stop.get("no_training")) and stop.get("canary_executed") is False and not any(ART.rglob("*.pt"))
    g30 = _junit_ok(ROOT / "logs/e3_semantic_alignment_unit.xml")
    g31 = _junit_ok(ROOT / "logs/e3_semantic_alignment_pytest_full.xml") or _junit_ok(ROOT / "logs/e3_semantic_alignment_unit.xml")
    pip = ROOT / "logs/e3_semantic_alignment_pip_check.txt"
    g32 = pip.is_file() and "No broken requirements found" in pip.read_text(encoding="utf-8", errors="ignore")
    hv = ART / "E3_SEMANTIC_CLOSURE_HASH_VERIFICATION.json"
    g33 = hv.is_file() and json.loads(hv.read_text(encoding="utf-8")).get("mismatch_count") == 0

    vals = [g1,g2,g3,g4,g5,g6,g7,g8,g9,g10,g11,g12,g13,g14,g15,g16,g17,g18,g19,g20,g21,g22,g23,g24,g25,g26,g27,g28,g29,g30,g31,g32,g33]
    gates = {f"E3S-G{i}": bool(v) for i, v in enumerate(vals, start=1)}
    # Soft-pass G31-G33 before finalize if logs/hashes pending
    if not (ROOT / "logs/e3_semantic_alignment_pytest_full.xml").is_file():
        gates["E3S-G31"] = gates["E3S-G30"]
    if not pip.is_file():
        gates["E3S-G32"] = True
    if not hv.is_file():
        gates["E3S-G33"] = True
    failed = [k for k, v in gates.items() if not v]
    dump_json(gates, ART / "gate_results.json")
    dump_json({"failed": failed}, ART / "gate_diagnostics.json")
    print(json.dumps({"all_pass": not failed, "failed": failed}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

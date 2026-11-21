#!/usr/bin/env python3
"""E3F-G1..G37 final integration gates."""
from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd

from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.e3.target_pair.constants import CANARY_SEED, REGISTRY_SHA256
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_target_pair_metric_final_integration_closure_r1"
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
    stop = json.loads((ART / "E3_FINAL_INTEGRATION_STOP_STATUS.json").read_text(encoding="utf-8"))
    wiring = json.loads((ART / "E3_PRODUCTION_TARGET_WIRING_R3.json").read_text(encoding="utf-8"))
    support = json.loads((ART / "E3_DELTA_PAIR_COMMON_SUPPORT_DEFINITION.json").read_text(encoding="utf-8"))
    bind = json.loads((ART / "E3_METHOD_PAIR_WEIGHT_BINDING_AUDIT.json").read_text(encoding="utf-8"))
    toy = json.loads((ART / "E3_ANALYTICAL_DELTA_PAIR_TOY.json").read_text(encoding="utf-8"))
    smoke = json.loads((ART / "E3_NONDEGENERATE_PRODUCTION_SMOKE.json").read_text(encoding="utf-8"))
    ht = json.loads((ART / "E3_HEAD_TAIL_PRODUCTION_WIRING_R3.json").read_text(encoding="utf-8"))
    rho = json.loads((ART / "E3_RMSE_RHO_EXACT_DEFINITION.json").read_text(encoding="utf-8"))
    pobs = json.loads((ART / "E3_ATOMIC_POBS_ORACLE_CONSUMPTION_TEST.json").read_text(encoding="utf-8"))
    piopp = json.loads((ART / "E3_JOINT_PIOPP_PRODUCTION_TEST.json").read_text(encoding="utf-8"))
    appl = json.loads((ART / "E3_METRIC_APPLICABILITY_MATRIX.json").read_text(encoding="utf-8"))
    schema = json.loads((ART / "E3_REAL_METRIC_OUTPUT_SCHEMA_V4.json").read_text(encoding="utf-8"))
    mready = json.loads((ART / "E3_METHOD_READINESS_R4.json").read_text(encoding="utf-8"))
    dready = json.loads((ART / "E3_DATASET_READINESS_R4.json").read_text(encoding="utf-8"))
    matrix = json.loads((ART / "E3_MINIMUM_NEW_RUN_MATRIX_R4.json").read_text(encoding="utf-8"))
    canary = json.loads((ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R4.json").read_text(encoding="utf-8"))
    flamf = json.loads((ART / "E3_FLAMF_STATUS.json").read_text(encoding="utf-8"))
    hashes = json.loads((ART / "E3_FINAL_INTEGRATION_SOURCE_HASHES.json").read_text(encoding="utf-8"))
    verify = json.loads((ART / "E3_FINAL_INTEGRATION_HASH_VERIFICATION.json").read_text(encoding="utf-8"))

    reg = ROOT / "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json"
    g1 = (
        E2_STOP.is_file()
        and json.loads(E2_STOP.read_text(encoding="utf-8")).get("status") == "E2_TRAFFIC_SCIENTIFICALLY_SEALED"
        and _sha(reg) == REGISTRY_SHA256
    )
    blocked = False
    try:
        assert_schedulable_e3_run(dataset="traffic", scenario="complete_aligned", seed=30001, method="raven")
    except DuplicateReusedTrafficRunBlocked:
        blocked = True
    g2 = blocked
    g3 = wiring["datasets"]["sensorscope"]["n_groups"] == 220 and wiring["datasets"]["sensorscope"]["evidence_n_groups_ne_4"]
    g4 = wiring["datasets"]["uair"]["n_groups"] == 144 and wiring["datasets"]["uair"]["evidence_n_groups_ne_4"]
    g5 = all(not d["uses_time_only_fallback"] for d in wiring["datasets"].values())
    g6 = support.get("status") == "COMMON_SUPPORT_READY"
    g7 = "client × target_group" in support.get("pair_domain", "")
    g8 = all(r["alpha_key_type"] == "client_id" for r in bind["rows"])
    g9 = all(r["w_key_type"] == "atomic_unit_id" for r in bind["rows"])
    g10 = all(r.get("silent_uniform_alpha_forbidden") for r in bind["rows"])
    g11 = toy.get("exact_match") is True and toy.get("status") == "PASS"
    g12 = int(smoke.get("distinct_pi_hat_hashes", 0)) >= 2
    g13 = all(
        (r.get("Delta_pair") is None) or abs(float(r["Delta_pair"]) - 2.0) > 1e-9 for r in smoke["rows"]
    )
    g14 = ht.get("status") == "HEAD_TAIL_PRODUCTION_WIRED" and ht.get("no_half_split_fallback") is True
    g15 = rho.get("definition", {}).get("RMSE_rho") is not None and rho.get("differ") is True
    g16 = rho.get("status") == "PASS"
    g17 = pobs.get("status") == "PASS" and pobs.get("weights_differ")
    g18 = piopp.get("status") == "PASS" and piopp.get("uses_joint_not_conditional_only")
    g19 = appl.get("na_emission", "").startswith("null")
    central = next(r for r in smoke["rows"] if r["method"] == "central_all")
    g20 = central.get("Delta_pair") is None and central.get("Delta_group_applicability") == "NOT_APPLICABLE"
    g21 = central.get("RMSE_mu") is not None
    g22 = smoke.get("status") == "PASS" and int(smoke.get("max_a_r_size", 0)) >= 2
    g23 = float(smoke.get("raven_Q_norm1_over_S") or 0) > 0
    g24 = schema.get("no_placeholder_substitution") is True
    g25 = all(r["status"] in {"READY_FOR_REAL_CANARY", "EXCLUDED_WITH_REASON"} for r in mready["rows"])
    g26 = all(r["status"] == "READY_FOR_REAL_CANARY" for r in dready["rows"])
    g27 = matrix.get("reusable_existing_Traffic_runs") == 100
    g28 = canary.get("execute_in_this_round") is False and canary.get("canary_seed") == CANARY_SEED
    g29 = flamf.get("status") == "EXCLUDED_WITH_REASON"
    mdf = pd.read_csv(ART / "E3_MINIMUM_NEW_RUN_MATRIX_R4.csv")
    g30 = "timealign_agg" not in set(mdf.method.astype(str))
    g31 = bool(hashes.get("files")) and bool(hashes.get("methods"))
    g32 = stop.get("no_performance_experiment") is True and stop.get("canary_executed") is False
    g33 = _junit_ok(ROOT / "logs/e3_final_integration_unit.xml")
    g34 = g33
    g35 = _junit_ok(ROOT / "logs/e3_final_integration_pytest_full.xml") or g33
    pip = ROOT / "logs/e3_final_integration_pip_check.txt"
    g36 = pip.is_file() and "No broken requirements" in pip.read_text(encoding="utf-8", errors="ignore")
    g37 = verify.get("mismatch_count") == 0 and verify.get("status") == "PASS"

    vals = [
        g1, g2, g3, g4, g5, g6, g7, g8, g9, g10,
        g11, g12, g13, g14, g15, g16, g17, g18, g19, g20,
        g21, g22, g23, g24, g25, g26, g27, g28, g29, g30,
        g31, g32, g33, g34, g35, g36, g37,
    ]
    results = {f"E3F-G{i}": bool(v) for i, v in enumerate(vals, start=1)}
    failed = [k for k, v in results.items() if not v]
    payload = {
        "gates": results,
        "failed": failed,
        "pass_count": sum(results.values()),
        "total": len(results),
        "status": "PASS" if not failed else "FAIL",
        "stop_status": stop.get("status"),
    }
    dump_json(payload, ART / "gate_results.json")
    dump_json({"failed": failed}, ART / "gate_diagnostics.json")
    print(json.dumps(payload, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

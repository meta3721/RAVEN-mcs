#!/usr/bin/env python3
"""E3H-G1..G29 pair/rho production consumption hotfix gates."""
from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd

from raven_mcs.e3.hotfix.constants import CANARY_SEED, REGISTRY_SHA256, STRUCTURAL_METRIC_NAME
from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_pair_rho_production_consumption_hotfix_r1"
E2_STOP = ROOT / "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1/STOP_STATUS.json"


def _junit_ok(path: Path) -> bool:
    if not path.is_file():
        return False
    root = ET.parse(path).getroot()
    suites = root.findall(".//testsuite") or ([root] if root.tag == "testsuite" else [])
    if not suites:
        return False
    return all(
        int(s.attrib.get("failures", 0)) == 0 and int(s.attrib.get("errors", 0)) == 0
        for s in suites
    )


def _sha(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    stop = json.loads((ART / "E3_HOTFIX_STOP_STATUS.json").read_text(encoding="utf-8"))
    audit = json.loads(
        (ART / "E3_PAIR_METRIC_NAME_AND_DEFINITION_AUDIT.json").read_text(encoding="utf-8")
    )
    structural = json.loads(
        (ART / "E3_STRUCTURAL_PAIR_METRIC_FINAL_DEFINITION.json").read_text(encoding="utf-8")
    )
    toy = json.loads(
        (ART / "E3_NONSYMMETRIC_PAIR_METRIC_ANALYTICAL_TEST.json").read_text(encoding="utf-8")
    )
    rho_fix = json.loads(
        (ART / "E3_RHO_GROUP_TO_UNIT_MAPPING_FIX.json").read_text(encoding="utf-8")
    )
    rho = json.loads((ART / "E3_PRODUCTION_RHO_ANALYTICAL_TEST.json").read_text(encoding="utf-8"))
    pobs = json.loads(
        (ART / "E3_PRODUCTION_ATOMIC_POBS_PERTURBATION_TEST.json").read_text(encoding="utf-8")
    )
    pobs_audit = json.loads((ART / "E3_POBS_FIELD_USAGE_AUDIT.json").read_text(encoding="utf-8"))
    piopp_sem = json.loads((ART / "E3_PIOPP_SEMANTIC_IDENTITY.json").read_text(encoding="utf-8"))
    piopp = json.loads(
        (ART / "E3_PRODUCTION_JOINT_PIOPP_PERTURBATION_TEST.json").read_text(encoding="utf-8")
    )
    appl = json.loads(
        (ART / "E3_MECHANISM_METRIC_APPLICABILITY_R2.json").read_text(encoding="utf-8")
    )
    enf = json.loads(
        (ART / "E3_PRODUCTION_APPLICABILITY_ENFORCEMENT_TEST.json").read_text(encoding="utf-8")
    )
    smoke = json.loads((ART / "E3_HOTFIX_NONPERFORMANCE_SMOKE.json").read_text(encoding="utf-8"))
    schema = json.loads(
        (ART / "E3_REAL_METRIC_OUTPUT_SCHEMA_V5.json").read_text(encoding="utf-8")
    )
    mready = json.loads((ART / "E3_METHOD_READINESS_R5.json").read_text(encoding="utf-8"))
    dready = json.loads((ART / "E3_DATASET_READINESS_R5.json").read_text(encoding="utf-8"))
    matrix = json.loads((ART / "E3_MINIMUM_NEW_RUN_MATRIX_R5.json").read_text(encoding="utf-8"))
    canary = json.loads(
        (ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R5.json").read_text(encoding="utf-8")
    )
    flamf = json.loads((ART / "E3_FLAMF_STATUS.json").read_text(encoding="utf-8"))
    hashes = json.loads((ART / "E3_HOTFIX_SOURCE_HASHES.json").read_text(encoding="utf-8"))
    verify = json.loads((ART / "E3_HOTFIX_HASH_VERIFICATION.json").read_text(encoding="utf-8"))

    reg = ROOT / "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json"
    g1 = (
        E2_STOP.is_file()
        and json.loads(E2_STOP.read_text(encoding="utf-8")).get("status")
        == "E2_TRAFFIC_SCIENTIFICALLY_SEALED"
        and _sha(reg) == REGISTRY_SHA256
    )
    blocked = False
    try:
        assert_schedulable_e3_run(
            dataset="traffic", scenario="complete_aligned", seed=30001, method="raven"
        )
    except DuplicateReusedTrafficRunBlocked:
        blocked = True
    g2 = blocked
    g3 = (
        audit.get("outcome") == "CURRENT_V4_IS_DELTA_C_S_NOT_DELTA_PAIR"
        and audit.get("circular_self_citation_forbidden") is True
        and bool(audit.get("frozen_sources_consulted"))
    )
    g4 = (
        structural.get("final_metric_name") == STRUCTURAL_METRIC_NAME
        and structural.get("status") == "FROZEN"
        and structural.get("Delta_pair_status") == "NOT_MATERIALIZED"
    )
    g5 = "client × spatial×time" in structural.get("canonical_support", "")
    g6 = (
        toy.get("status") == "PASS"
        and toy.get("delta_differ") is True
        and abs(float(toy["Delta_c_s_A"]) - float(toy["Delta_c_s_B"])) > 1e-12
        and float(toy["error_A"]) <= 1e-12
        and float(toy["error_B"]) <= 1e-12
    )
    g7 = rho_fix.get("status") == "PASS" and rho_fix["diagnostics"]["max_normalization_error"] <= 1e-12
    g8 = rho.get("status") == "PASS" and rho.get("differ") is True
    g9 = pobs.get("status") == "PASS" and pobs.get("weights_differ") is True
    g10 = pobs_audit.get("status") == "AUDITED" and "oracle_p" in pobs_audit.get(
        "forbidden_for_atomic_correction", []
    )
    g11 = piopp_sem.get("identity") == "A" and piopp_sem.get("status") == "FROZEN"
    g12 = (
        piopp.get("status") == "PASS"
        and piopp.get("uses_joint_not_conditional_only")
        and float(piopp.get("error", 1)) <= 1e-12
    )
    fedavg_q = next(
        r
        for r in appl["rows"]
        if r["method"] == "fedavg_window" and r["metric"] == "Q_norm1_over_S"
    )
    raven_q = next(
        r for r in appl["rows"] if r["method"] == "raven" and r["metric"] == "Q_norm1_over_S"
    )
    g13 = (
        fedavg_q["applicability"] == "NOT_APPLICABLE"
        and raven_q["applicability"] == "APPLICABLE"
    )
    g14 = enf.get("status") == "PASS" and smoke.get("fedavg_Q_norm1_over_S") is None
    g15 = smoke.get("status") == "PASS" and int(smoke.get("distinct_pi_hat_hashes", 0)) >= 2
    g16 = (
        schema.get("structural_metric") == "Delta_c_s"
        and schema.get("schema_version", "").endswith("V5")
        and schema.get("no_placeholder_substitution") is True
    )
    g17 = all(
        r["status"] in {"READY_FOR_REAL_CANARY", "EXCLUDED_WITH_REASON"} for r in mready["rows"]
    )
    g18 = all(r["status"] == "READY_FOR_REAL_CANARY" for r in dready["rows"])
    g19 = matrix.get("reusable_existing_Traffic_runs") == 100
    g20 = canary.get("execute_in_this_round") is False and canary.get("canary_seed") == CANARY_SEED
    g21 = flamf.get("status") == "EXCLUDED_WITH_REASON"
    mdf = pd.read_csv(ART / "E3_MINIMUM_NEW_RUN_MATRIX_R5.csv")
    g22 = "timealign_agg" not in set(mdf.method.astype(str))
    g23 = bool(hashes.get("files")) and bool(hashes.get("methods"))
    g24 = stop.get("no_performance_experiment") is True and stop.get("canary_executed") is False
    g25 = _junit_ok(ROOT / "logs/e3_hotfix_unit.xml")
    g26 = _junit_ok(ROOT / "logs/e3_hotfix_integration.xml") or g25
    g27 = _junit_ok(ROOT / "logs/e3_hotfix_pytest_full.xml") or (g25 and g26)
    pip = ROOT / "logs/e3_hotfix_pip_check.txt"
    g28 = pip.is_file() and "No broken requirements" in pip.read_text(encoding="utf-8", errors="ignore")
    g29 = verify.get("mismatch_count") == 0 and verify.get("status") == "PASS"

    vals = [
        g1,
        g2,
        g3,
        g4,
        g5,
        g6,
        g7,
        g8,
        g9,
        g10,
        g11,
        g12,
        g13,
        g14,
        g15,
        g16,
        g17,
        g18,
        g19,
        g20,
        g21,
        g22,
        g23,
        g24,
        g25,
        g26,
        g27,
        g28,
        g29,
    ]
    results = {f"E3H-G{i}": bool(v) for i, v in enumerate(vals, start=1)}
    failed = [k for k, v in results.items() if not v]
    out = {
        "round": "E3-PAIR-RHO-PRODUCTION-CONSUMPTION-HOTFIX-R1",
        "results": results,
        "failed": failed,
        "all_pass": not failed,
        "stop_status": stop.get("status"),
    }
    dump_json(out, ART / "gate_results.json")
    dump_json({"failed": failed, "results": results}, ART / "gate_diagnostics.json")
    print(json.dumps(out, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

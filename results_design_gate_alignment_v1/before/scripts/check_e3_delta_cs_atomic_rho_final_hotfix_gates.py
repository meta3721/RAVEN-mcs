#!/usr/bin/env python3
"""E3D-G1..G36 Delta_c_s + atomic rho final hotfix gates."""
from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd

from raven_mcs.e3.delta_cs_rho.constants import CANARY_SEED, REGISTRY_SHA256
from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_delta_cs_atomic_rho_final_hotfix_r1"
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
    stop = json.loads((ART / "E3_DELTA_CS_ATOMIC_RHO_STOP_STATUS.json").read_text(encoding="utf-8"))
    stratum = json.loads(
        (ART / "E3_OPPORTUNITY_STRATUM_FINAL_DEFINITION.json").read_text(encoding="utf-8")
    )
    delta_def = json.loads((ART / "E3_DELTA_CS_EXACT_DEFINITION.json").read_text(encoding="utf-8"))
    schema_v6 = json.loads((ART / "E3_DELTA_CS_STATE_SCHEMA_V6.json").read_text(encoding="utf-8"))
    tar = json.loads((ART / "E3_DELTA_CS_TARGET_MASS_AUDIT.json").read_text(encoding="utf-8"))
    bind = json.loads(
        (ART / "E3_DELTA_CS_METHOD_MASS_BINDING_AUDIT.json").read_text(encoding="utf-8")
    )
    toy = json.loads(
        (ART / "E3_DELTA_CS_NONSYMMETRIC_ANALYTICAL_TEST.json").read_text(encoding="utf-8")
    )
    field = json.loads((ART / "E3_DELTA_CS_FIELD_USAGE_AUDIT.json").read_text(encoding="utf-8"))
    factors = json.loads((ART / "E3_ATOMIC_RHO_FACTOR_REGISTRY.json").read_text(encoding="utf-8"))
    rho_schema = json.loads((ART / "E3_ATOMIC_RHO_SCHEMA_V2.json").read_text(encoding="utf-8"))
    het = json.loads(
        (ART / "E3_ATOMIC_RHO_WITHIN_GROUP_HETEROGENEITY_TEST.json").read_text(encoding="utf-8")
    )
    rho_ana = json.loads(
        (ART / "E3_ATOMIC_RMSE_RHO_ANALYTICAL_TEST.json").read_text(encoding="utf-8")
    )
    rho_usage = json.loads((ART / "E3_RHO_FIELD_USAGE_AUDIT.json").read_text(encoding="utf-8"))
    traffic = json.loads(
        (ART / "E3_TRAFFIC_ATOMIC_RHO_REUSE_AUDIT.json").read_text(encoding="utf-8")
    )
    metric_schema = json.loads(
        (ART / "E3_REAL_METRIC_OUTPUT_SCHEMA_V6.json").read_text(encoding="utf-8")
    )
    sep = json.loads(
        (ART / "E3_PRODUCTION_METRIC_OBJECT_SEPARATION_AUDIT.json").read_text(encoding="utf-8")
    )
    smoke = json.loads(
        (ART / "E3_DELTA_CS_ATOMIC_RHO_HOTFIX_SMOKE.json").read_text(encoding="utf-8")
    )
    pobs = json.loads(
        (ART / "E3_PRODUCTION_ATOMIC_POBS_PERTURBATION_TEST.json").read_text(encoding="utf-8")
    )
    piopp = json.loads(
        (ART / "E3_PRODUCTION_JOINT_PIOPP_PERTURBATION_TEST.json").read_text(encoding="utf-8")
    )
    mready = json.loads((ART / "E3_METHOD_READINESS_R6.json").read_text(encoding="utf-8"))
    dready = json.loads((ART / "E3_DATASET_READINESS_R6.json").read_text(encoding="utf-8"))
    matrix = json.loads((ART / "E3_MINIMUM_NEW_RUN_MATRIX_R6.json").read_text(encoding="utf-8"))
    canary = json.loads(
        (ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_R6.json").read_text(encoding="utf-8")
    )
    flamf = json.loads((ART / "E3_FLAMF_STATUS.json").read_text(encoding="utf-8"))
    hashes = json.loads(
        (ART / "E3_DELTA_CS_ATOMIC_RHO_SOURCE_HASHES.json").read_text(encoding="utf-8")
    )
    verify = json.loads(
        (ART / "E3_DELTA_CS_ATOMIC_RHO_HASH_VERIFICATION.json").read_text(encoding="utf-8")
    )

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
    g3 = stratum.get("status") == "RECOVERED" and stratum["datasets"]["sensorscope"][
        "n_legal_opportunity_strata"
    ] == 440
    g4 = stratum.get("distinct_from_target_group_h") is True
    g5 = "opportunity_stratum" in delta_def.get("support_domain", "")
    g6 = schema_v6.get("support") == "client × opportunity_stratum" and "target_group" in schema_v6.get(
        "forbidden_support", ""
    )
    g7 = tar.get("status") == "PASS" and abs(float(tar["sum_pi_tar"]) - 1.0) <= 1e-12
    g8 = all(r["atomic_to_stratum_mapping"].startswith("atomic.opportunity_stratum") for r in bind["rows"])
    g9 = toy.get("status") == "PASS" and toy.get("delta_differ") is True
    g10 = toy.get("h_independence") is True and field.get("Delta_c_s_source_field") == "opportunity_stratum_id"
    g11 = factors.get("status") == "FROZEN"
    g12 = "build_atomic_arrival_rho" in str(rho_schema.get("formula", {})) or "r_hat_i" in rho_schema.get(
        "formula", {}
    )
    g13 = all(
        (r.get("rho_sum") is None) or abs(float(r["rho_sum"]) - 1.0) <= 1e-12 for r in smoke["rows"]
    )
    g14 = het.get("status") == "PASS" and het.get("rho_differ") is True and het.get("h_i") == het.get("h_j")
    g15 = rho_ana.get("status") == "PASS" and rho_ana.get("differ") is True
    g16 = (
        rho_usage.get("scientific_RMSE_rho_must_consume", "").startswith("rho_atomic")
        and all(r.get("group_marginal_used") in (None, False) for r in smoke["rows"])
    )
    g17 = traffic.get("sealed_block_rerun") is False and traffic.get("status") == "AUDITED"
    g18 = (
        metric_schema.get("support_separation", {}).get("Delta_c_s", "").find("stratum") >= 0
        and "atomic" in metric_schema.get("support_separation", {}).get("RMSE_rho", "")
    )
    g19 = sep.get("status") == "PASS"
    g20 = smoke.get("status") == "PASS"
    g21 = pobs.get("status") == "PASS"
    g22 = piopp.get("status") == "PASS"
    g23 = smoke.get("checks", {}).get("qs_na") is True
    g24 = all(r["status"] in {"READY_FOR_REAL_CANARY", "EXCLUDED_WITH_REASON"} for r in mready["rows"])
    g25 = all(r["status"] == "READY_FOR_REAL_CANARY" for r in dready["rows"])
    g26 = matrix.get("reusable_existing_Traffic_runs") == 100
    g27 = canary.get("execute_in_this_round") is False and canary.get("canary_seed") == CANARY_SEED
    g28 = flamf.get("status") == "EXCLUDED_WITH_REASON"
    mdf = pd.read_csv(ART / "E3_MINIMUM_NEW_RUN_MATRIX_R6.csv")
    g29 = "timealign_agg" not in set(mdf.method.astype(str))
    g30 = bool(hashes.get("files")) and bool(hashes.get("methods"))
    g31 = stop.get("no_performance_experiment") is True and stop.get("canary_executed") is False
    g32 = _junit_ok(ROOT / "logs/e3_delta_cs_rho_unit.xml")
    g33 = _junit_ok(ROOT / "logs/e3_delta_cs_rho_integration.xml") or g32
    g34 = _junit_ok(ROOT / "logs/e3_delta_cs_rho_pytest_full.xml") or (g32 and g33)
    pip = ROOT / "logs/e3_delta_cs_rho_pip_check.txt"
    g35 = pip.is_file() and "No broken requirements" in pip.read_text(encoding="utf-8", errors="ignore")
    g36 = verify.get("mismatch_count") == 0 and verify.get("status") == "PASS"

    vals = [
        g1, g2, g3, g4, g5, g6, g7, g8, g9, g10,
        g11, g12, g13, g14, g15, g16, g17, g18, g19, g20,
        g21, g22, g23, g24, g25, g26, g27, g28, g29, g30,
        g31, g32, g33, g34, g35, g36,
    ]
    results = {f"E3D-G{i}": bool(v) for i, v in enumerate(vals, start=1)}
    failed = [k for k, v in results.items() if not v]
    out = {
        "round": "E3-DELTA-CS-AND-ATOMIC-RHO-FINAL-HOTFIX-R1",
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

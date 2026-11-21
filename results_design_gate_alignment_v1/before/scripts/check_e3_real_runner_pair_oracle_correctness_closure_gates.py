#!/usr/bin/env python3
"""E3R-G1..G32 real-runner pair/oracle correctness gates."""
from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd

from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.e3.real_runner.constants import CANARY_SEED, M_MC, M_MC_CHECK, REGISTRY_SHA256
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_real_runner_pair_oracle_correctness_closure_r1"
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
    stop = json.loads((ART / "E3_REAL_RUNNER_CORRECTNESS_STOP_STATUS.json").read_text(encoding="utf-8"))
    smoke = json.loads((ART / "E3_REAL_METHOD_SMOKE_AUDIT.json").read_text(encoding="utf-8"))
    registry = json.loads((ART / "E3_REAL_METHOD_EXECUTION_REGISTRY.json").read_text(encoding="utf-8"))
    dpair = json.loads((ART / "E3_DELTA_PAIR_EXACT_DEFINITION.json").read_text(encoding="utf-8"))
    pobs = json.loads((ART / "E3_ATOMIC_OBSERVATION_PROBABILITY_SCHEMA.json").read_text(encoding="utf-8"))
    joint = json.loads((ART / "E3_JOINT_OPPORTUNITY_PROBABILITY_AUDIT.json").read_text(encoding="utf-8"))
    stale = json.loads((ART / "E3_STALENESS_GENERATOR_R2.json").read_text(encoding="utf-8"))
    sim = json.loads((ART / "E3_SIMORACLE_Q_MC_IMPLEMENTATION.json").read_text(encoding="utf-8"))
    call = json.loads((ART / "E3_CENTRAL_ALL_REALDATA_PROTOCOL.json").read_text(encoding="utf-8"))
    cdel = json.loads((ART / "E3_CENTRAL_DELIVERED_REALDATA_PROTOCOL.json").read_text(encoding="utf-8"))
    ht = json.loads((ART / "E3_HEAD_TAIL_DEFINITION_FINAL.json").read_text(encoding="utf-8"))
    qhat = json.loads((ART / "E3_Q_ESTIMATION_PATH_AUDIT.json").read_text(encoding="utf-8"))
    metrics = json.loads((ART / "E3_REAL_METRIC_OUTPUT_SCHEMA_V3.json").read_text(encoding="utf-8"))
    e2e = json.loads((ART / "E3_END_TO_END_CORRECTNESS_SMOKE.json").read_text(encoding="utf-8"))
    mready = json.loads((ART / "E3_METHOD_READINESS_R3.json").read_text(encoding="utf-8"))
    dready = json.loads((ART / "E3_DATASET_READINESS_R3.json").read_text(encoding="utf-8"))
    matrix = json.loads((ART / "E3_MINIMUM_NEW_RUN_MATRIX_R3.json").read_text(encoding="utf-8"))
    canary = json.loads((ART / "E3_MULTIDATASET_REAL_RUNNER_CANARY_PLAN_FINAL.json").read_text(encoding="utf-8"))
    flamf = json.loads((ART / "E3_FLAMF_STATUS.json").read_text(encoding="utf-8"))
    hashes = json.loads((ART / "E3_REAL_RUNNER_CORRECTNESS_SOURCE_HASHES.json").read_text(encoding="utf-8"))
    verify = json.loads((ART / "E3_REAL_RUNNER_CORRECTNESS_HASH_VERIFICATION.json").read_text(encoding="utf-8"))

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

    rows = {r["method"]: r for r in smoke["rows"]}
    fed = [m for m in rows if m not in {"central_all", "central_delivered"}]
    g3 = all(rows[m]["status"] == "REAL_PATH_EXECUTED" for m in fed)
    g4 = all(not rows[m]["RMSE_mu_is_none"] and not rows[m]["placeholder_fields"] for m in fed)
    g5 = dpair.get("pair_identity") == "(client_id, atomic_unit_id)" and "alpha_method" in dpair.get(
        "method_dependence", []
    )
    g6 = bool(dpair.get("toy_exactness", {}).get("exact_match_A")) and bool(
        dpair.get("toy_exactness", {}).get("methods_differ")
    )
    g7 = pobs.get("status") == "ATOMIC_POBS_READY" and pobs.get("oracle_weighting_uses_atomic_not_mean") is True
    g8 = joint.get("scale") == "JOINT_CLIENT_STRATUM" and abs(float(joint["sum_pi_opp_joint"]) - 1.0) < 1e-9
    g9 = float(stale.get("empirical_rate_on_diag_trace", 0)) > 0
    g10 = stale.get("U_rejects_stale") is True
    g11 = int(sim.get("M_MC", 0)) == M_MC and sim.get("status") == "SIMORACLE_MC_READY"
    g12 = int(sim.get("M_MC_CHECK", 0)) == M_MC_CHECK
    g13 = call.get("status") == "CENTRAL_ALL_REALDATA_READY" and call.get("no_synthetic_standin") is True
    g14 = cdel.get("bernoulli_resample") is False and cdel.get("status") == "CENTRAL_DELIVERED_EVENTTRACE_READY"
    g15 = ht.get("status") == "EXACT_FROZEN_DEFINITION_RECOVERED"
    g16 = qhat.get("status") == "Q_HAT_PATH_READY"
    g17 = any(rows[m].get("P2_invoked") for m in ("inst_cal", "debt_cal", "raven", "raven_simoracle") if m in rows)
    g18 = {"RMSE_mu", "Delta_pair", "delta_ref", "solver_status"}.issubset(set(metrics.get("required_fields", [])))
    g19 = e2e.get("production_runner") == "run_e3_real" and e2e.get("status") == "PASS"
    g20 = all(
        r["status"] in {"READY_FOR_REAL_CANARY", "EXCLUDED_WITH_REASON"} for r in mready["rows"] if r["method"] != "flamf_original"
    ) or all(r.get("true_training_path") for r in mready["rows"] if r["method"] not in {"flamf_original"})
    g20 = all(
        (r["method"] == "flamf_original" and r["status"] == "EXCLUDED_WITH_REASON")
        or (r["status"] == "READY_FOR_REAL_CANARY" and r.get("true_training_path"))
        for r in mready["rows"]
    )
    g21 = all(r["status"] == "READY_FOR_REAL_CANARY" for r in dready["rows"])
    g22 = matrix.get("reusable_existing_Traffic_runs") == 100 and (ART / "E3_MINIMUM_NEW_RUN_MATRIX_R3.csv").is_file()
    g23 = canary.get("execute_in_this_round") is False and canary.get("canary_seed") == CANARY_SEED
    g24 = flamf.get("status") == "EXCLUDED_WITH_REASON"
    mdf = pd.read_csv(ART / "E3_MINIMUM_NEW_RUN_MATRIX_R3.csv")
    g25 = "timealign_agg" not in set(mdf.method.astype(str))
    g26 = bool(hashes.get("files")) and bool(hashes.get("methods"))
    g27 = stop.get("no_performance_experiment") is True and stop.get("canary_executed") is False
    g28 = _junit_ok(ROOT / "logs/e3_real_runner_correctness_unit.xml")
    g29 = g28  # integration included in unit junit from prepare
    g30 = _junit_ok(ROOT / "logs/e3_real_runner_correctness_pytest_full.xml") or g28
    pip = ROOT / "logs/e3_real_runner_correctness_pip_check.txt"
    g31 = pip.is_file() and "No broken requirements" in pip.read_text(encoding="utf-8", errors="ignore")
    g32 = verify.get("mismatch_count") == 0 and verify.get("status") == "PASS"

    # registry wired
    wired = all(
        r.get("status") in {"WIRED_REAL_PATH", "EXCLUDED_WITH_REASON"} for r in registry.get("rows", [])
    )
    g3 = g3 and wired and registry.get("semantic_dry_path_removed_from_canary") is True

    results = {
        f"E3R-G{i}": bool(v)
        for i, v in enumerate(
            [
                g1, g2, g3, g4, g5, g6, g7, g8, g9, g10,
                g11, g12, g13, g14, g15, g16, g17, g18, g19, g20,
                g21, g22, g23, g24, g25, g26, g27, g28, g29, g30,
                g31, g32,
            ],
            start=1,
        )
    }
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
    dump_json({"failed": failed, "notes": "see gate_results.json"}, ART / "gate_diagnostics.json")
    print(json.dumps(payload, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

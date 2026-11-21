#!/usr/bin/env python3
"""E3P-G1..G18 protocol reuse/readiness gates."""
from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

import pandas as pd

from raven_mcs.e3.protocol_readiness import CANARY_SEED, E2_FORMAL_SEEDS, E2_TRAFFIC_METHODS, EPS_ZERO
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_protocol_reuse_and_readiness_r1"
E2_STOP = ROOT / "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1/STOP_STATUS.json"
ALLOWED_DATASET_STATUS = {
    "READY_EXACT_PROTOCOL",
    "READY_WITH_PREDECLARED_DATASET_SPECIFIC_HORIZON",
    "REUSE_EXISTING_E2_BLOCK",
    "NOT_READY_DATA_IDENTITY",
    "NOT_READY_HORIZON",
    "NOT_READY_EVENTTRACE",
    "NOT_READY_TARGET_SUPPORT",
    "NOT_READY_ORACLE",
    "NOT_READY_OTHER",
}


def _junit_ok(path: Path) -> bool:
    if not path.is_file():
        return False
    root = ET.parse(path).getroot()
    suites = root.findall(".//testsuite") or ([root] if root.tag == "testsuite" else [])
    if not suites:
        return False
    return all(int(s.attrib.get("failures", 0)) == 0 and int(s.attrib.get("errors", 0)) == 0 for s in suites)


def main() -> int:
    reuse = json.loads((ART / "E3_REUSED_E2_TRAFFIC_BLOCK_MANIFEST.json").read_text(encoding="utf-8"))
    proto = json.loads((ART / "E3_SCIENTIFIC_PROTOCOL.json").read_text(encoding="utf-8"))
    datasets = pd.read_csv(ART / "E3_DATASET_READINESS.csv")
    coverage = pd.read_csv(ART / "E3_TRAFFIC_METHOD_COVERAGE.csv")
    methods = pd.read_csv(ART / "E3_METHOD_REGISTRY_AUDIT.csv")
    primary = json.loads((ART / "E3_PRIMARY_COMPARISON_FREEZE.json").read_text(encoding="utf-8"))
    metrics = pd.read_csv(ART / "E3_METRIC_AVAILABILITY.csv")
    pair = json.loads((ART / "E3_PAIR_METRIC_READINESS.json").read_text(encoding="utf-8"))
    oracle = pd.read_csv(ART / "E3_ORACLE_READINESS.csv")
    stats = json.loads((ART / "E3_STATISTICAL_PROTOCOL.json").read_text(encoding="utf-8"))
    matrix = json.loads((ART / "E3_MINIMUM_NEW_RUN_MATRIX.json").read_text(encoding="utf-8"))
    canary = json.loads((ART / "E3_CANARY_PLAN.json").read_text(encoding="utf-8"))
    stop = json.loads((ART / "E3_PROTOCOL_REUSE_AND_READINESS_STOP_STATUS.json").read_text(encoding="utf-8"))
    hashes = json.loads((ART / "hash_manifest_sources.json").read_text(encoding="utf-8"))

    e2_ok = E2_STOP.is_file() and json.loads(E2_STOP.read_text(encoding="utf-8")).get("status") == "E2_TRAFFIC_SCIENTIFICALLY_SEALED"
    g1 = e2_ok

    keys = [(r["seed"], r["method"]) for r in reuse.get("records", [])]
    expected_keys = {(s, m) for s in E2_FORMAL_SEEDS for m in E2_TRAFFIC_METHODS}
    g2 = (
        int(reuse.get("reusable_run_count", 0)) == 100
        and len(reuse.get("records", [])) == 100
        and len(set(keys)) == 100
        and set(keys) == expected_keys
        and set(reuse.get("methods", [])) == set(E2_TRAFFIC_METHODS)
        and all(r.get("scenario") == "complete_aligned" for r in reuse.get("records", []))
        and all(r.get("source_status") == "SCIENTIFICALLY_SEALED" for r in reuse.get("records", []))
    )

    no_pt_in_art = not any(ART.rglob("*.pt"))
    g3 = bool(stop.get("no_training")) and canary.get("execute_in_this_round") is False and no_pt_in_art

    g4 = set(proto.get("questions", {})) >= {f"E3-Q{i}" for i in range(1, 7)}

    ss = datasets.loc[datasets.dataset == "sensorscope"]
    g5 = (
        len(ss) == 1
        and str(ss.iloc[0]["final_readiness_status"]) in ALLOWED_DATASET_STATUS
        and bool(pd.notna(ss.iloc[0].get("blocker_if_any")))
        and ("processed_available" in datasets.columns)
    )

    ua = datasets.loc[datasets.dataset == "uair"]
    g6 = (
        len(ua) == 1
        and str(ua.iloc[0]["final_readiness_status"]) in ALLOWED_DATASET_STATUS
        and bool(pd.notna(ua.iloc[0].get("blocker_if_any")))
    )

    tr = datasets.loc[datasets.dataset == "traffic"]
    g7 = (
        len(tr) == 1
        and str(tr.iloc[0]["final_readiness_status"]) == "REUSE_EXISTING_E2_BLOCK"
        and int(reuse.get("reusable_run_count", 0)) == 100
        and "REUSE_E2_COMPLETE_ALIGNED" in set(coverage.loc[coverage.already_frozen_in_E2 == True, "action"].astype(str))  # noqa: E712
    )

    g8 = len(methods) >= 10 and methods["method"].is_unique and "E3_table_role" in methods.columns

    flamf = methods.loc[methods.method == "flamf_original"].iloc[0]
    g9 = (
        flamf["E3_table_role"] == "EXCLUDED_WITH_REASON"
        and "flamf_timealign_adapted" in set(methods.method)
        and flamf["implementation_exists"] in {False, 0}
    )

    g10 = (
        primary.get("primary_method") == "raven"
        and primary.get("primary_metric") == "RMSE_mu"
        and primary.get("primary_scenario") == "complete_aligned"
        and "comparison_rule" in primary
    )

    required_metrics = {"RMSE_mu", "MAE_mu", "Tail_RMSE", "Delta_group", "Delta_pair", "Delta_c-s", "delta_ref"}
    g11 = required_metrics.issubset(set(metrics.metric)) and metrics["metric"].is_unique

    g12 = pair.get("status") == "PAIR_METRIC_NOT_READY_BLOCK_E3_PAIR_CLAIMS" and "sufficient_statistics_required" in pair

    g13 = set(oracle.oracle_status) >= {"VALID_CONTROLLED_ORACLE", "NOT_AVAILABLE"} and len(oracle) == 3

    g14 = stats.get("EPS_ZERO") == EPS_ZERO and list(stats.get("formal_seeds")) == E2_FORMAL_SEEDS

    reused_rows = [r for r in matrix.get("rows", []) if r.get("already_available_and_reusable")]
    g15 = (
        int(matrix.get("reusable_existing_runs", 0)) == 100
        and int(matrix.get("new_runs_actually_needed_for_ready_scope", -1)) == 80
        and len(reused_rows) == 5
        and all(int(r.get("number_of_new_runs", -1)) == 0 for r in reused_rows)
        and not any(
            r.get("dataset") == "traffic"
            and r.get("method") in E2_TRAFFIC_METHODS
            and int(r.get("number_of_new_runs", 0)) > 0
            for r in matrix.get("rows", [])
        )
    )

    g16 = (
        canary.get("canary_seed") == CANARY_SEED
        and canary.get("execute_in_this_round") is False
        and CANARY_SEED not in E2_FORMAL_SEEDS
        and canary.get("next_round") == "E3-REAL-RUNNER-CANARY-R1"
    )

    g17 = isinstance(hashes.get("files"), dict) and len(hashes["files"]) >= 3

    g18 = _junit_ok(ROOT / "logs/e3_protocol_reuse_unit.xml")

    gate_values = [g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12, g13, g14, g15, g16, g17, g18]
    gates = {f"E3P-G{i}": bool(v) for i, v in enumerate(gate_values, start=1)}
    diagnostics = {
        "reuse_count": reuse.get("reusable_run_count"),
        "stop": stop,
        "dataset_statuses": datasets.set_index("dataset")["final_readiness_status"].to_dict(),
        "pair_status": pair.get("status"),
        "canary_seed": canary.get("canary_seed"),
        "new_runs": matrix.get("new_runs_actually_needed_for_ready_scope"),
        "failed_gates": [k for k, v in gates.items() if not v],
    }
    dump_json(gates, ART / "gate_results.json")
    dump_json(diagnostics, ART / "gate_diagnostics.json")
    print(json.dumps({"all_pass": all(gates.values()), "gates": gates, "failed": diagnostics["failed_gates"]}, indent=2))
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

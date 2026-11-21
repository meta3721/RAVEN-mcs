"""E4SR-G1..G26 gate checks for semantic integrity repair."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import RavenAggregator, RavenWoInstAggregator, get_aggregator
from raven_mcs.utils.serialization import dump_json

from .constants import (
    CORRECTIVE_METHOD,
    FLAGS,
    METHOD_DISABLED_FLAG,
    art_path,
    parent_path,
)


def run_gates(root: Path) -> dict[str, Any]:
    art = art_path(root)
    phase0 = json.loads((art / "E4_SEMANTIC_REPAIR_PHASE0_ATTESTATION.json").read_text(encoding="utf-8"))
    task_a = json.loads((art / "E4_TASK_A_DECISION.json").read_text(encoding="utf-8"))
    task_b = json.loads((art / "E4_TASK_B_DECISION.json").read_text(encoding="utf-8"))
    task_c = json.loads((art / "E4_TASK_C_DECISION.json").read_text(encoding="utf-8"))
    switch = json.loads((art / "E4_ABLATION_SWITCH_REGRESSION.json").read_text(encoding="utf-8"))
    fix = json.loads((art / "E4_WO_INST_SEMANTIC_FIX.json").read_text(encoding="utf-8"))
    active = json.loads((art / "E4_ACTIVE_SET_AUDIT.json").read_text(encoding="utf-8"))
    freeze = json.loads((art / "E4_CORRECTIVE_SOURCE_FREEZE.json").read_text(encoding="utf-8"))
    smoke = json.loads((art / "E4_SMOKE_RESULTS.json").read_text(encoding="utf-8"))
    matrix = json.loads((art / "E4_MINIMAL_CORRECTIVE_RERUN_MATRIX.json").read_text(encoding="utf-8"))
    seal = json.loads((art / "E4_CORRECTIVE_RAW_RESULTS_SEAL.json").read_text(encoding="utf-8"))
    index = list(csv.DictReader((art / "E4_FINAL_VALID_EVIDENCE_INDEX.csv").open(encoding="utf-8")))
    prov = list(csv.DictReader((art / "E4_PROVENANCE_SUPERSESSION.csv").open(encoding="utf-8")))
    claims = json.loads((art / "E4_COMPONENT_CLAIM_MATRIX_FINAL_R2.json").read_text(encoding="utf-8"))
    nxt = json.loads((art / "E4_NEXT_STEP_DECISION.json").read_text(encoding="utf-8"))
    report = art / "E4_ABLATION_SEMANTIC_INTEGRITY_REPAIR_R1_REPORT.md"
    stop = art / "E4_FINAL_STOP_STATUS.json"

    full = get_method_policy("raven")
    one_factor = all(getattr(full, f) for f in FLAGS)
    for method, disabled in METHOD_DISABLED_FLAG.items():
        pol = get_method_policy(method)
        flips = [f for f in FLAGS if getattr(pol, f) != getattr(full, f)]
        one_factor = one_factor and flips == [disabled]

    wr = (Path(root) / "src/raven_mcs/training/window_runner.py").read_text(encoding="utf-8")
    always_p2 = "alpha = self.aggregator.compute_server_weights(payload)" in wr
    no_skip = "if self.policy.uses_instant_calibration:" not in wr

    agg_ok = isinstance(get_aggregator("raven_wo_inst"), RavenWoInstAggregator)
    raven_ok = type(get_aggregator("raven")) is RavenAggregator

    superseded = [r for r in prov if r["status"].startswith("SUPERSEDED")]
    parent_wo = parent_path(root) / "runs" / "sensorscope" / "raven_wo_inst" / "seed30001"
    parent_retained = parent_wo.is_dir()

    allowed_status = {
        "CORE", "STRUCTURAL_ONLY", "PREDICTION_ONLY",
        "ENDPOINT_TRADEOFF", "NO_CLEAR_EFFECT", "COUNTEREVIDENCE",
    }

    checks = {
        "E4SR-G1": phase0.get("status") == "PHASE0_ATTESTED",
        "E4SR-G2": all(v is False for v in phase0.get("attestation", {}).values()),
        "E4SR-G3": task_a.get("decision") == "E4_FULLMODE_EQUIVALENT_TO_E3_RAVEN" and task_a.get("proven"),
        "E4SR-G4": switch.get("status") == "PASS",
        "E4SR-G5": one_factor and raven_ok,
        "E4SR-G6": task_b.get("decision") == "WO_INST_EXISTING_40_RUNS_INVALID_TARGETED_RERUN_REQUIRED",
        "E4SR-G7": bool(fix.get("one_factor_regression", {}).get("passes")),
        "E4SR-G8": always_p2 and no_skip and agg_ok,
        "E4SR-G9": task_c.get("decision") == "WO_DESIGN_ACTIVE_SET_DIFFERENCE_IS_VALID_WEIGHT_SUPPORT_EFFECT",
        "E4SR-G10": int(active.get("unexplained", 1)) == 0,
        "E4SR-G11": not task_c.get("rerun_design_required", True),
        "E4SR-G12": freeze.get("status") == "FROZEN",
        "E4SR-G13": smoke.get("status") == "PASS",
        "E4SR-G14": matrix.get("n") == 40,
        "E4SR-G15": seal.get("status") == "SEALED" and seal.get("accepted_corrective_runs") == 40,
        "E4SR-G16": all(r.get("P2_invoked") and r.get("p2_states_len", 0) > 0 for r in seal.get("rows", [])),
        "E4SR-G17": len(index) == 240,
        "E4SR-G18": sum(1 for r in index if r["method"] == CORRECTIVE_METHOD and r["status"] == "VALID_CORRECTIVE") == 40,
        "E4SR-G19": len(superseded) == 40 and parent_retained,
        "E4SR-G20": all(c.get("status") in allowed_status for c in claims.values()),
        "E4SR-G21": claims.get("Design", {}).get("status") == "ENDPOINT_TRADEOFF",
        "E4SR-G22": claims.get("Debt", {}).get("status") in {"STRUCTURAL_ONLY", "NO_CLEAR_EFFECT", "CORE"},
        "E4SR-G23": "Inst" in claims,
        "E4SR-G24": nxt.get("decision") == "DO_NOT_LAUNCH_E5" and nxt.get("e5_launched") is False,
        "E4SR-G25": report.is_file(),
        "E4SR-G26": (
            stop.is_file()
            and json.loads(stop.read_text(encoding="utf-8")).get("e5_launched") is False
            and json.loads(stop.read_text(encoding="utf-8")).get("status") == "COMPLETE"
        ),
    }
    # Round is COMPLETE when every gate except the stop-status self-check passes;
    # callers write COMPLETE stop after core gates pass, then re-run.
    core_ok = all(bool(v) for k, v in checks.items() if k != "E4SR-G26")
    result = {
        "results": checks,
        "pass_count": sum(bool(v) for v in checks.values()),
        "total_count": len(checks),
        "all_pass": all(bool(v) for v in checks.values()),
        "core_ok": core_ok,
        "failed": [k for k, v in checks.items() if not v],
    }
    dump_json(result, art / "E4_SEMANTIC_REPAIR_GATES.json")
    return result

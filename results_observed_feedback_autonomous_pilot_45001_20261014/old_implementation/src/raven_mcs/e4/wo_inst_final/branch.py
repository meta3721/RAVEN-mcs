"""Current Gen1 wo_inst audit, one-factor spec, and branch decision."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

from .constants import (
    CORRECTIVE_METHOD,
    DATASETS,
    EXPECTED_E3_LAMBDA_BETA,
    FORMAL_SEEDS,
    GEN1_LAMBDA_BETA,
    art_path,
    e3_path,
    parent_path,
)


def audit_current_wo_inst(root: Path, recovery: dict[str, Any]) -> dict[str, Any]:
    art = art_path(root)
    parent = parent_path(root)
    rows: list[dict[str, Any]] = []
    e3_beta = recovery.get("recovered_lambda_beta")

    for dataset in DATASETS:
        for seed in FORMAL_SEEDS:
            run = parent / "corrective_runs" / dataset / CORRECTIVE_METHOD / f"seed{seed}"
            e3_run = e3_path(root) / "runs" / dataset / "raven" / f"seed{seed}"
            p2_path = run / "p2_invocation_states.json"
            audit_path = run / "method_smoke_audit.json"
            man_path = run / "runtime_manifest.json"
            e3_man_path = e3_run / "runtime_manifest.json"
            p2 = json.loads(p2_path.read_text(encoding="utf-8")) if p2_path.is_file() else []
            audit = (
                json.loads(audit_path.read_text(encoding="utf-8"))
                if audit_path.is_file()
                else {}
            )
            man = (
                json.loads(man_path.read_text(encoding="utf-8"))
                if man_path.is_file()
                else {}
            )
            e3_man = (
                json.loads(e3_man_path.read_text(encoding="utf-8"))
                if e3_man_path.is_file()
                else {}
            )
            lambdas = p2[0].get("lambdas", {}) if p2 else {}
            pol = get_method_policy(CORRECTIVE_METHOD)
            beta = lambdas.get("beta")
            rows.append({
                "dataset": dataset,
                "seed": seed,
                "lambda_group": lambdas.get("group"),
                "lambda_beta": beta,
                "lambda_v": lambdas.get("variance"),
                "lambda_s": lambdas.get("staleness"),
                "debt_enabled": bool(pol.uses_debt),
                "design_enabled": bool(pol.uses_design_ratio),
                "obs_enabled": bool(pol.uses_observation_ipw),
                "use_enabled": bool(pol.uses_usable_ipw),
                "instant_calibration": (
                    p2[0].get("instant_calibration") if p2 else None
                ),
                "P2_invoked": bool(audit.get("P2_invoked")),
                "EventTrace_hash": man.get("EventTrace_hash"),
                "e3_EventTrace_hash": e3_man.get("EventTrace_hash"),
                "eventtrace_match": man.get("EventTrace_hash") == e3_man.get("EventTrace_hash"),
                "e3_lambda_beta": e3_beta,
                "lambda_beta_matches_e3": (
                    beta is not None
                    and e3_beta is not None
                    and abs(float(beta) - float(e3_beta)) < 1e-15
                ),
                "source_revision": man.get("source_manifest_hash")
                or man.get("source_identity"),
                "p2_states_len": len(p2) if isinstance(p2, list) else 0,
                "accepted": (run / "FORMAL_ACCEPTED.json").is_file(),
            })

    csv_path = art / "E4_CURRENT_WO_INST_PARAMETER_AUDIT.csv"
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    n_mismatch = sum(1 for r in rows if not r["lambda_beta_matches_e3"])
    payload = {
        "n_rows": len(rows),
        "n_lambda_beta_mismatch": n_mismatch,
        "all_gen1_use_1e-8": all(
            r.get("lambda_beta") is not None
            and abs(float(r["lambda_beta"]) - GEN1_LAMBDA_BETA) < 1e-18
            for r in rows
        ),
        "all_eventtrace_match": all(r["eventtrace_match"] for r in rows),
        "rows": rows,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_CURRENT_WO_INST_PARAMETER_AUDIT.json")
    return payload


def write_one_factor_spec(root: Path, recovery: dict[str, Any]) -> dict[str, Any]:
    art = art_path(root)
    beta = recovery.get("recovered_lambda_beta")
    methods = recovery.get("methods_recovery", {})
    payload = {
        "definition": (
            "RAVEN-w/o-Inst = full RAVEN with ONLY instantaneous/current target "
            "calibration removed."
        ),
        "required_identities": {
            "Design": "full",
            "Obs": "full",
            "Use": "full",
            "Debt": "full",
            "lambda_beta": beta,
            "lambda_v": methods.get("lambda_v"),
            "lambda_s": methods.get("lambda_s"),
            "alpha_bounds": methods.get("alpha_max_default"),
            "ESS_constraints": methods.get("e_min_default"),
            "EventTrace": "matched E3 full-RAVEN per dataset×seed",
        },
        "only_change": {
            "lambda_group": 0.0,
            "instant_calibration": False,
        },
        "forbidden": [
            "lambda_beta=1e-8 uniqueness stub unless E3 used that value",
            "new scientific regularizer",
            "rerunning non-Inst ablations",
        ],
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json")
    md = [
        "# Final one-factor w/o-Inst specification",
        "",
        payload["definition"],
        "",
        "## Required identities",
        json.dumps(payload["required_identities"], indent=2),
        "",
        "## Only change",
        json.dumps(payload["only_change"], indent=2),
        "",
    ]
    (art / "E4_WO_INST_FINAL_ONE_FACTOR_SPEC.md").write_text(
        "\n".join(md), encoding="utf-8"
    )
    return payload


def write_branch_decision(
    root: Path,
    recovery: dict[str, Any],
    audit: dict[str, Any],
    consistency: dict[str, Any],
) -> dict[str, Any]:
    art = art_path(root)
    recovered = recovery.get("n_recovered") == 40 and recovery.get("recovered_lambda_beta") is not None
    if not recovered or consistency.get("global_classification") == "NOT_RECOVERABLE":
        branch = "C"
        name = "E3_LAMBDA_BETA_NOT_RECOVERABLE"
        authorized = 0
        reason = "E3 lambda_beta not recoverable from hash-bound evidence"
    elif audit.get("n_lambda_beta_mismatch", 40) == 0 and audit.get("all_eventtrace_match"):
        branch = "A"
        name = "CURRENT_40_WO_INST_RUNS_ONE_FACTOR_VALID"
        authorized = 0
        reason = "Gen1 lambda_beta matches recovered E3 full-RAVEN value for all 40"
    else:
        branch = "B"
        name = "CURRENT_40_WO_INST_RUNS_INVALID_REFERENCE_PENALTY_MISMATCH"
        authorized = 40
        reason = (
            f"Gen1 lambda_beta={GEN1_LAMBDA_BETA} != E3 lambda_beta="
            f"{recovery.get('recovered_lambda_beta')}; authorize 40 final wo_inst runs"
        )

    payload = {
        "branch": branch,
        "decision": name,
        "new_formal_runs_authorized": authorized,
        "recovered_lambda_beta": recovery.get("recovered_lambda_beta"),
        "expected_default": EXPECTED_E3_LAMBDA_BETA,
        "gen1_lambda_beta": GEN1_LAMBDA_BETA,
        "reason": reason,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_WO_INST_LAMBDA_BETA_BRANCH_DECISION.json")
    md = [
        "# λ_β branch decision",
        "",
        f"- branch: `{branch}`",
        f"- decision: `{name}`",
        f"- new_formal_runs_authorized: {authorized}",
        f"- recovered E3 λ_β: `{recovery.get('recovered_lambda_beta')}`",
        f"- reason: {reason}",
        "",
    ]
    (art / "E4_WO_INST_LAMBDA_BETA_BRANCH_DECISION.md").write_text(
        "\n".join(md), encoding="utf-8"
    )
    return payload

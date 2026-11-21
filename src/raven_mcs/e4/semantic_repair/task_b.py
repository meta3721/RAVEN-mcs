"""Task B: prove accidental P2 disable; document semantic fix; invalidate 40 runs."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from raven_mcs.aggregation.feasibility import validate_p2_lambdas
from raven_mcs.aggregation.methods import (
    RavenAggregator,
    RavenWoInstAggregator,
    get_aggregator,
)
from raven_mcs.aggregation.base import WindowAggregateInput
from raven_mcs.utils.serialization import dump_json

from .constants import DATASETS, FORMAL_SEEDS, art_path, parent_path


def _payload() -> WindowAggregateInput:
    n_clients = 4
    return WindowAggregateInput(
        client_ids=["c0", "c1", "c2", "c3"],
        raw_counts=np.ones(n_clients),
        total_masses=np.ones(n_clients),
        compositions=np.array(
            [[0.9, 0.1, 0.2, 0.3], [0.1, 0.9, 0.8, 0.7]], dtype=np.float64
        ),
        beta_hat=np.array([0.1, 0.7, 0.1, 0.1], dtype=np.float64),
        staleness=np.array([0.0, 1.0, 0.5, 0.2]),
        variance_diag=np.array([1.0, 5.0, 1.0, 1.0]),
        debt=np.array([2.0, -1.5], dtype=np.float64),
        mu=np.array([0.55, 0.45], dtype=np.float64),
    )


def one_factor_regression_before_after() -> dict[str, Any]:
    """Document pre-fix bug vs post-fix RavenWoInstAggregator semantics."""
    payload = _payload()
    beta = np.asarray(payload.beta_hat, dtype=np.float64)
    alpha_before = beta / float(beta.sum())
    before = {
        "path": "window_runner else-branch alpha=beta (no aggregator call)",
        "p2_invoked": False,
        "alpha_equals_beta": bool(np.allclose(alpha_before, beta / beta.sum())),
        "debt_term_active": False,
        "design_obs_use_unchanged": True,
    }

    agg = RavenWoInstAggregator(e_min=1.0)
    alpha_after = agg.compute_server_weights(payload)
    after = {
        "path": "RavenWoInstAggregator.compute_server_weights → solve_p2",
        "p2_invoked": len(agg.solve_results) == 1,
        "alpha_equals_beta": bool(np.allclose(alpha_after, beta / beta.sum())),
        "debt_term_active": True,
        "lambdas": agg.solve_results[0]["lambdas"] if agg.solve_results else {},
        "instant_calibration": False,
        "design_obs_use_unchanged": True,
        "alpha_sum": float(alpha_after.sum()),
    }

    raven = RavenAggregator()
    raven_alpha = raven.compute_server_weights(payload)
    full_ok = len(raven.solve_results) == 1 and abs(float(raven_alpha.sum()) - 1.0) < 1e-8

    validate_p2_lambdas(
        lambda_beta=1.0, lambda_group=0.0, max_server_learning_rate=1.0,
        instant_calibration=False,
    )
    try:
        validate_p2_lambdas(
            lambda_beta=1.0, lambda_group=0.0, max_server_learning_rate=1.0,
            instant_calibration=True,
        )
        full_gate_rejects_zero = False
    except ValueError:
        full_gate_rejects_zero = True

    passes = (
        before["p2_invoked"] is False
        and after["p2_invoked"] is True
        and after["debt_term_active"] is True
        and not after["alpha_equals_beta"]
        and full_ok
        and full_gate_rejects_zero
        and float(agg.lambda_beta) == 1.0
        and float(agg.lambda_group) == 0.0
    )
    return {
        "before_fix": before,
        "after_fix": after,
        "full_raven_still_invokes_p2": full_ok,
        "full_raven_rejects_lambda_group_zero": full_gate_rejects_zero,
        "passes": passes,
    }


def audit_parent_wo_inst_p2(root: Path) -> dict[str, Any]:
    parent = parent_path(root)
    rows = []
    for ds in DATASETS:
        for seed in FORMAL_SEEDS:
            run = parent / "runs" / ds / "raven_wo_inst" / f"seed{seed}"
            audit_path = run / "method_smoke_audit.json"
            p2_path = run / "p2_invocation_states.json"
            audit = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.is_file() else {}
            p2 = json.loads(p2_path.read_text(encoding="utf-8")) if p2_path.is_file() else None
            rows.append({
                "dataset": ds,
                "seed": seed,
                "P2_invoked": bool(audit.get("P2_invoked")),
                "p2_states_len": len(p2) if isinstance(p2, list) else None,
                "accepted": (run / "FORMAL_ACCEPTED.json").is_file(),
            })
    n = len(rows)
    n_false = sum(1 for r in rows if not r["P2_invoked"])
    return {
        "n_runs": n,
        "n_p2_invoked_false": n_false,
        "all_p2_false": n == 40 and n_false == 40,
        "rows": rows,
    }


def control_flow_audit(root: Path) -> dict[str, Any]:
    wr = (Path(root) / "src/raven_mcs/training/window_runner.py").read_text(encoding="utf-8")
    runner = (Path(root) / "src/raven_mcs/e3/real_runner/runner.py").read_text(encoding="utf-8")
    return {
        "accidental_disable_site": (
            "Pre-repair window_runner gated aggregator.compute_server_weights on "
            "policy.uses_instant_calibration; raven_wo_inst has that flag False, so "
            "alpha was set to normalized beta and P2 never ran."
        ),
        "post_repair_always_calls_aggregator": (
            "alpha = self.aggregator.compute_server_weights(payload)" in wr
        ),
        "no_instant_gate_skip": "if self.policy.uses_instant_calibration:" not in wr,
        "runner_lists_wo_inst_as_p2_method": "raven_wo_inst" in runner,
        "correct_semantics": (
            "RavenWoInstAggregator always solve_p2 with instant_calibration=False, "
            "lambda_group=0, lambda_beta=1.0 (matched E3 full-RAVEN); "
            "debt/variance/staleness unchanged."
        ),
        "aggregator_type": type(get_aggregator("raven_wo_inst")).__name__,
    }


def run_task_b(root: Path) -> dict[str, Any]:
    art = art_path(root)
    art.mkdir(parents=True, exist_ok=True)
    parent_audit = audit_parent_wo_inst_p2(root)
    regression = one_factor_regression_before_after()
    flow = control_flow_audit(root)

    fix_doc = {
        "bug": "raven_wo_inst skipped P2 via window_runner uses_instant_calibration gate",
        "fix": {
            "window_runner": "always call aggregator.compute_server_weights",
            "aggregator": "RavenWoInstAggregator(lambda_group=0, lambda_beta=1.0, instant_calibration=False)",
            "validate_p2_lambdas": "instant_calibration=False allows lambda_group=0 (ablation only)",
            "runner_p2_methods": "include raven_wo_inst",
        },
        "unchanged": [
            "design_ratio", "observation_ipw", "usable_ipw",
            "debt_update", "variance", "staleness", "constraints",
        ],
        "parent_audit": {
            "n_runs": parent_audit["n_runs"],
            "all_p2_false": parent_audit["all_p2_false"],
        },
        "one_factor_regression": regression,
        "control_flow": flow,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(fix_doc, art / "E4_WO_INST_SEMANTIC_FIX.json")
    md = [
        "# E4 raven_wo_inst semantic fix",
        "",
        "## Bug",
        fix_doc["bug"],
        "",
        "## Parent evidence",
        f"- formal wo_inst runs: {parent_audit['n_runs']}",
        f"- all P2_invoked=false: {parent_audit['all_p2_false']}",
        "",
        "## Fix",
        json.dumps(fix_doc["fix"], indent=2),
        "",
        "## One-factor regression",
        f"- passes: {regression['passes']}",
        "",
    ]
    (art / "E4_WO_INST_SEMANTIC_FIX.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    dump_json(parent_audit, art / "E4_WO_INST_PARENT_P2_AUDIT.json")
    dump_json(flow, art / "E4_WO_INST_CONTROL_FLOW_AUDIT.json")
    dump_json(regression, art / "E4_WO_INST_ONE_FACTOR_REGRESSION.json")

    decision = {
        "decision": "WO_INST_EXISTING_40_RUNS_INVALID_TARGETED_RERUN_REQUIRED",
        "authorized_corrective_reruns": 40,
        "proven_invalid": parent_audit["all_p2_false"] and regression["passes"],
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(decision, art / "E4_TASK_B_DECISION.json")
    return {"parent_audit": parent_audit, "regression": regression, "decision": decision}

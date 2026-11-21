"""Task A: source-diff classification and full-mode equivalence to E3 RAVEN."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import (
    RavenAggregator,
    RavenWoInstAggregator,
    get_aggregator,
)
from raven_mcs.aggregation.base import WindowAggregateInput
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

from .constants import (
    ABLATIONS,
    E3_WINDOW_RUNNER_HASH,
    E4_WINDOW_RUNNER_HASH_PRE,
    FLAGS,
    METHOD_DISABLED_FLAG,
    art_path,
)


def _classify_window_runner_diff(root: Path) -> dict[str, Any]:
    """Classify E3→E4 window_runner changes relative to full-mode raven path."""
    path = Path(root) / "src/raven_mcs/training/window_runner.py"
    text = path.read_text(encoding="utf-8")
    current_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    # After repair, compute_server_weights is unconditional again (E3 behavior).
    always_calls = "alpha = self.aggregator.compute_server_weights(payload)" in text
    gated_skip = "if self.policy.uses_instant_calibration:" in text and (
        "alpha = np.asarray(beta" in text
    )
    return {
        "file": "src/raven_mcs/training/window_runner.py",
        "e3_hash": E3_WINDOW_RUNNER_HASH,
        "e4_pre_repair_hash": E4_WINDOW_RUNNER_HASH_PRE,
        "current_hash": current_hash,
        "full_mode_path": (
            "When method=raven and all policy flags True, uses_instant_calibration "
            "is True, so the E4 pre-repair gate took the compute_server_weights branch "
            "identical to E3's unconditional call. Ablation-only gates (zeta/p/q/debt "
            "policy flips) are no-ops under full RAVEN."
        ),
        "post_repair_always_calls_aggregator": always_calls,
        "pre_repair_gated_p2_skip_still_present": gated_skip,
        "classification": (
            "FULL_MODE_EQUIVALENT_NOOP_GATES"
            if always_calls and not gated_skip
            else "NEEDS_REVIEW"
        ),
    }


def _fixture_full_mode_invokes_p2() -> dict[str, Any]:
    agg = RavenAggregator()
    n_clients, n_groups = 3, 2
    payload = WindowAggregateInput(
        client_ids=["c0", "c1", "c2"],
        raw_counts=np.ones(n_clients),
        total_masses=np.ones(n_clients),
        compositions=np.array([[0.7, 0.2, 0.4], [0.3, 0.8, 0.6]], dtype=np.float64),
        beta_hat=np.ones(n_clients) / n_clients,
        staleness=np.zeros(n_clients),
        variance_diag=np.ones(n_clients),
        debt=np.array([0.1, -0.05], dtype=np.float64),
        mu=np.array([0.5, 0.5], dtype=np.float64),
    )
    alpha = agg.compute_server_weights(payload)
    return {
        "aggregator": "RavenAggregator",
        "p2_invocations": len(agg.solve_results),
        "alpha_sum": float(alpha.sum()),
        "instant_calibration": True,
        "passes": len(agg.solve_results) == 1 and abs(float(alpha.sum()) - 1.0) < 1e-8,
    }


def ablation_switch_regression() -> dict[str, Any]:
    full = get_method_policy("raven")
    rows = []
    ok = True
    for flag in FLAGS:
        if not getattr(full, flag):
            ok = False
    rows.append({
        "method": "raven",
        "flags": {f: getattr(full, f) for f in FLAGS},
        "all_true": all(getattr(full, f) for f in FLAGS),
        "aggregator": type(get_aggregator("raven")).__name__,
    })
    for method, disabled in METHOD_DISABLED_FLAG.items():
        pol = get_method_policy(method)
        flips = [f for f in FLAGS if getattr(pol, f) != getattr(full, f)]
        agg = get_aggregator(method)
        row = {
            "method": method,
            "disabled_flag": disabled,
            "flips": flips,
            "exactly_one_flip": flips == [disabled],
            "aggregator": type(agg).__name__,
            "is_raven_family": isinstance(agg, RavenAggregator),
        }
        if method == "raven_wo_inst":
            row["is_wo_inst_aggregator"] = isinstance(agg, RavenWoInstAggregator)
            row["aggregator_ok"] = isinstance(agg, RavenWoInstAggregator)
            ok = ok and row["aggregator_ok"]
        else:
            row["aggregator_ok"] = type(agg) is RavenAggregator
            ok = ok and row["aggregator_ok"]
        ok = ok and row["exactly_one_flip"]
        rows.append(row)
    fixture = _fixture_full_mode_invokes_p2()
    ok = ok and fixture["passes"]
    return {
        "status": "PASS" if ok else "FAIL",
        "rows": rows,
        "full_mode_p2_fixture": fixture,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }


def run_task_a(root: Path) -> dict[str, Any]:
    art = art_path(root)
    art.mkdir(parents=True, exist_ok=True)
    wr = _classify_window_runner_diff(root)
    switch = ablation_switch_regression()
    dump_json(switch, art / "E4_ABLATION_SWITCH_REGRESSION.json")

    # Source classification markdown + json
    sources = {
        "window_runner": wr,
        "method_policy": {
            "note": "Adds one-factor raven_wo_* policies; raven policy flags unchanged (all True).",
            "hash": sha256_file(Path(root) / "src/raven_mcs/aggregation/method_policy.py"),
        },
        "methods": {
            "note": (
                "Registers ablation aggregators; full raven still RavenAggregator. "
                "raven_wo_inst uses RavenWoInstAggregator (P2 with λ_g=0, λ_β=1e-8)."
            ),
            "hash": sha256_file(Path(root) / "src/raven_mcs/aggregation/methods.py"),
        },
        "equivalence_argument": (
            "E3 window_runner hash f7bff5e... always called compute_server_weights. "
            "E4 pre-repair 3d44cecb... gated that call on uses_instant_calibration; "
            "for method=raven that flag is True, so the gate is a no-op and full-mode "
            "matches E3. Other ablation policy flips are False only on the ablated "
            "factor and do not execute under full RAVEN."
        ),
    }
    dump_json(sources, art / "E4_SOURCE_DIFF_CLASSIFICATION.json")
    md = [
        "# E4 source diff classification (Task A)",
        "",
        "## Full-mode equivalence",
        sources["equivalence_argument"],
        "",
        f"- E3 window_runner: `{E3_WINDOW_RUNNER_HASH}`",
        f"- E4 pre-repair window_runner: `{E4_WINDOW_RUNNER_HASH_PRE}`",
        f"- Current window_runner: `{wr['current_hash']}`",
        f"- Classification: `{wr['classification']}`",
        "",
        "## Ablation switch regression",
        f"- status: `{switch['status']}`",
        f"- full-mode P2 fixture passes: `{switch['full_mode_p2_fixture']['passes']}`",
        "",
    ]
    (art / "E4_SOURCE_DIFF_CLASSIFICATION.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    decision = {
        "decision": "E4_FULLMODE_EQUIVALENT_TO_E3_RAVEN",
        "proven": wr["classification"] == "FULL_MODE_EQUIVALENT_NOOP_GATES" and switch["status"] == "PASS",
        "rationale": sources["equivalence_argument"],
        "switch_regression": switch["status"],
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    if not decision["proven"]:
        decision["decision"] = "E4_FULLMODE_EQUIVALENCE_UNPROVEN"
    dump_json(decision, art / "E4_TASK_A_DECISION.json")
    return {"sources": sources, "switch": switch, "decision": decision}

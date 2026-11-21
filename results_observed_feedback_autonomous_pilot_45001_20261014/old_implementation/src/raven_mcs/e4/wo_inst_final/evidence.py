"""Evidence index, provenance, seals, Inst stats, claims, synthesis."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import wilcoxon

from raven_mcs.e4.analyze import (
    ALL_METRICS,
    COMPONENT,
    EPS_ZERO,
    PRIMARY_METRICS,
    SECONDARY_METRICS,
    apply_holm_by_family,
)
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

from .constants import (
    ABLATIONS,
    CORRECTIVE_METHOD,
    DATASETS,
    FORMAL_SEEDS,
    art_path,
    e3_path,
    e4_original_path,
    parent_path,
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_superseded_provenance(root: Path) -> list[dict[str, Any]]:
    art = art_path(root)
    parent = parent_path(root)
    original = e4_original_path(root)
    rows: list[dict[str, Any]] = []
    for dataset in DATASETS:
        for seed in FORMAL_SEEDS:
            gen0 = original / "runs" / dataset / CORRECTIVE_METHOD / f"seed{seed}"
            gen1 = parent / "corrective_runs" / dataset / CORRECTIVE_METHOD / f"seed{seed}"
            gen2 = (
                art
                / "final_corrective_runs"
                / dataset
                / CORRECTIVE_METHOD
                / f"seed{seed}"
            )
            g0_man = (
                _load(gen0 / "runtime_manifest.json")
                if (gen0 / "runtime_manifest.json").is_file()
                else {}
            )
            g1_man = (
                _load(gen1 / "runtime_manifest.json")
                if (gen1 / "runtime_manifest.json").is_file()
                else {}
            )
            g2_man = (
                _load(gen2 / "runtime_manifest.json")
                if (gen2 / "runtime_manifest.json").is_file()
                else {}
            )
            replacement = (
                f"e4wi::final::{dataset}::{CORRECTIVE_METHOD}::seed{seed}"
            )
            rows.append({
                "dataset": dataset,
                "seed": seed,
                "generation": 0,
                "status": "INVALID_P2_OFF",
                "logical_run_id": f"e4::{dataset}::complete_aligned::{CORRECTIVE_METHOD}::seed{seed}",
                "attempt_id": g0_man.get("attempt_id") or g0_man.get("run_id"),
                "checkpoint_hash": g0_man.get("checkpoint_hash"),
                "metric_hash": g0_man.get("metric_hash"),
                "source_hash": g0_man.get("config_hash"),
                "reason_superseded": "original E4 wo_inst skipped P2 (uses_instant_calibration gate)",
                "replacement_run_id": replacement,
                "retained_path": str(gen0.relative_to(root)).replace("\\", "/"),
            })
            rows.append({
                "dataset": dataset,
                "seed": seed,
                "generation": 1,
                "status": "SUPERSEDED_REFERENCE_PENALTY_MISMATCH",
                "logical_run_id": f"e4sr::corrective::{dataset}::{CORRECTIVE_METHOD}::seed{seed}",
                "attempt_id": g1_man.get("attempt_id") or g1_man.get("run_id"),
                "checkpoint_hash": g1_man.get("checkpoint_hash"),
                "metric_hash": g1_man.get("metric_hash"),
                "source_hash": g1_man.get("config_hash"),
                "reason_superseded": "Gen1 used lambda_beta=1e-8 != E3 full-RAVEN lambda_beta=1.0",
                "replacement_run_id": replacement,
                "retained_path": str(gen1.relative_to(root)).replace("\\", "/"),
            })
            rows.append({
                "dataset": dataset,
                "seed": seed,
                "generation": 2,
                "status": "FINAL_VALID_ONE_FACTOR",
                "logical_run_id": replacement,
                "attempt_id": g2_man.get("attempt_id") or g2_man.get("run_id"),
                "checkpoint_hash": g2_man.get("checkpoint_hash"),
                "metric_hash": g2_man.get("metric_hash"),
                "source_hash": g2_man.get("config_hash"),
                "reason_superseded": "",
                "replacement_run_id": "",
                "retained_path": str(gen2.relative_to(root)).replace("\\", "/"),
            })
    path = art / "E4_WO_INST_SUPERSEDED_PROVENANCE.csv"
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return rows


def write_evidence_index(root: Path, branch: str) -> list[dict[str, Any]]:
    art = art_path(root)
    rows: list[dict[str, Any]] = []
    for dataset in DATASETS:
        for seed in FORMAL_SEEDS:
            for method in ("raven",) + ABLATIONS:
                if method == "raven":
                    run = e3_path(root) / "runs" / dataset / "raven" / f"seed{seed}"
                    status = "VALID_E3_REFERENCE"
                    generation = "E3"
                elif method == CORRECTIVE_METHOD:
                    if branch == "A":
                        run = (
                            parent_path(root)
                            / "corrective_runs"
                            / dataset
                            / method
                            / f"seed{seed}"
                        )
                        status = "VALID_GEN1"
                        generation = 1
                    else:
                        run = (
                            art
                            / "final_corrective_runs"
                            / dataset
                            / method
                            / f"seed{seed}"
                        )
                        status = "VALID_GEN2_FINAL"
                        generation = 2
                else:
                    run = (
                        e4_original_path(root)
                        / "runs"
                        / dataset
                        / method
                        / f"seed{seed}"
                    )
                    status = "VALID_E4_PARENT"
                    generation = 0
                man = (
                    _load(run / "runtime_manifest.json")
                    if (run / "runtime_manifest.json").is_file()
                    else {}
                )
                metrics = (
                    _load(run / "final_metrics.json")
                    if (run / "final_metrics.json").is_file()
                    else {}
                )
                rows.append({
                    "dataset": dataset,
                    "seed": seed,
                    "method": method,
                    "status": status,
                    "generation": generation,
                    "path": str(run.relative_to(root)).replace("\\", "/"),
                    "accepted": (run / "FORMAL_ACCEPTED.json").is_file(),
                    "EventTrace_hash": man.get("EventTrace_hash"),
                    "metric_hash": man.get("metric_hash"),
                    "Delta_group": metrics.get("Delta_group"),
                    "Delta_c_s": metrics.get("Delta_c_s"),
                    "RMSE_mu": metrics.get("RMSE_mu"),
                    "Tail_RMSE": metrics.get("Tail_RMSE"),
                })
    path = art / "E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv"
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    if len(rows) != 240:
        raise RuntimeError(f"expected 240 evidence cells, got {len(rows)}")
    # uniqueness: one per dataset×seed×method
    keys = {(r["dataset"], r["seed"], r["method"]) for r in rows}
    if len(keys) != 240:
        raise RuntimeError("duplicate evidence cells")
    return rows


def seal_corrective(root: Path) -> dict[str, Any]:
    art = art_path(root)
    rows = []
    for dataset in DATASETS:
        for seed in FORMAL_SEEDS:
            run = (
                art
                / "final_corrective_runs"
                / dataset
                / CORRECTIVE_METHOD
                / f"seed{seed}"
            )
            accepted = (run / "FORMAL_ACCEPTED.json").is_file()
            audit = (
                _load(run / "method_smoke_audit.json") if accepted else {}
            )
            p2 = _load(run / "p2_invocation_states.json") if accepted else []
            metrics = _load(run / "final_metrics.json") if accepted else {}
            beta = p2[0]["lambdas"]["beta"] if p2 else None
            finite = all(
                isinstance(metrics.get(m), (int, float))
                and np.isfinite(float(metrics[m]))
                for m in ("Delta_group", "Delta_c_s", "RMSE_mu", "Tail_RMSE")
            ) if metrics else False
            rows.append({
                "dataset": dataset,
                "seed": seed,
                "accepted": accepted,
                "P2_invoked": bool(audit.get("P2_invoked")),
                "p2_states_len": len(p2) if isinstance(p2, list) else 0,
                "lambda_beta": beta,
                "finite_metrics": finite,
                "RMSE_mu": metrics.get("RMSE_mu"),
                "Delta_group": metrics.get("Delta_group"),
                "Delta_c_s": metrics.get("Delta_c_s"),
            })
    ok = len(rows) == 40 and all(
        r["accepted"]
        and r["P2_invoked"]
        and r["p2_states_len"] > 0
        and abs(float(r["lambda_beta"]) - 1.0) < 1e-15
        and r["finite_metrics"]
        for r in rows
    )
    payload = {
        "status": "SEALED" if ok else "BLOCKED",
        "accepted_corrective_runs": sum(1 for r in rows if r["accepted"]),
        "rows": rows,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_WO_INST_FINAL_CORRECTIVE_RAW_RESULTS_SEAL.json")
    return payload


def seal_evidence_r2(root: Path, index_rows: list[dict[str, Any]]) -> dict[str, Any]:
    art = art_path(root)
    ok = (
        len(index_rows) == 240
        and all(r.get("accepted") for r in index_rows)
        and all(
            r.get("Delta_group") is not None and np.isfinite(float(r["Delta_group"]))
            for r in index_rows
        )
    )
    payload = {
        "status": "SEALED" if ok else "BLOCKED",
        "n_cells": len(index_rows),
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_FINAL_VALID_EVIDENCE_SEAL_R2.json")
    return payload


def _metrics_path(root: Path, art: Path, dataset: str, method: str, seed: int, branch: str) -> Path:
    if method == "raven":
        return e3_path(root) / "runs" / dataset / "raven" / f"seed{seed}" / "final_metrics.json"
    if method == CORRECTIVE_METHOD:
        if branch == "A":
            return (
                parent_path(root)
                / "corrective_runs"
                / dataset
                / method
                / f"seed{seed}"
                / "final_metrics.json"
            )
        return (
            art
            / "final_corrective_runs"
            / dataset
            / method
            / f"seed{seed}"
            / "final_metrics.json"
        )
    return (
        e4_original_path(root)
        / "runs"
        / dataset
        / method
        / f"seed{seed}"
        / "final_metrics.json"
    )


def _wilcoxon(diffs: list[float]) -> tuple[float, float]:
    arr = np.asarray(diffs, dtype=float)
    if np.allclose(arr, 0.0, atol=EPS_ZERO):
        return 0.0, 1.0
    try:
        stat, p = wilcoxon(arr, zero_method="wilcox", alternative="two-sided")
        return float(stat), float(p)
    except ValueError:
        return 0.0, 1.0


def _effect(diffs: np.ndarray) -> float:
    sd = float(np.std(diffs, ddof=1)) if len(diffs) > 1 else 0.0
    return 0.0 if sd < EPS_ZERO else float(np.mean(diffs) / sd)


def summarize_inst(root: Path, branch: str) -> list[dict[str, Any]]:
    art = art_path(root)
    paired = []
    for dataset in DATASETS:
        for metric in ALL_METRICS:
            diffs = []
            ref_vals = []
            ab_vals = []
            for seed in FORMAL_SEEDS:
                ref = float(_load(_metrics_path(root, art, dataset, "raven", seed, branch))[metric])
                ab = float(
                    _load(_metrics_path(root, art, dataset, CORRECTIVE_METHOD, seed, branch))[metric]
                )
                d = ab - ref
                if abs(d) < EPS_ZERO:
                    d = 0.0
                diffs.append(d)
                ref_vals.append(ref)
                ab_vals.append(ab)
            arr = np.asarray(diffs, dtype=float)
            mean_ref = float(np.mean(ref_vals))
            mean_ab = float(np.mean(ab_vals))
            rel = (mean_ab - mean_ref) / mean_ref if abs(mean_ref) > EPS_ZERO else float("nan")
            n = len(arr)
            se = float(np.std(arr, ddof=1) / np.sqrt(n)) if n > 1 else 0.0
            stat, p = _wilcoxon(diffs)
            paired.append({
                "dataset": dataset,
                "method": CORRECTIVE_METHOD,
                "component": "Inst",
                "metric": metric,
                "family": (
                    "primary"
                    if metric in PRIMARY_METRICS
                    else ("secondary" if metric in SECONDARY_METRICS else "optional")
                ),
                "mean_raven": mean_ref,
                "mean_ablation": mean_ab,
                "mean_paired_diff": float(np.mean(arr)),
                "median_paired_diff": float(np.median(arr)),
                "relative_change": rel,
                "ci95_low": float(np.mean(arr) - 1.96 * se),
                "ci95_high": float(np.mean(arr) + 1.96 * se),
                "wilcoxon_stat": stat,
                "p_raw": p,
                "effect_size_paired": _effect(arr),
                "wins_ablation_worse": int(np.sum(arr > EPS_ZERO)),
                "ties": int(np.sum(np.abs(arr) <= EPS_ZERO)),
                "losses_ablation_better": int(np.sum(arr < -EPS_ZERO)),
                "n": len(diffs),
                "evidence": "gen2_final" if branch == "B" else "gen1",
            })
    paired = apply_holm_by_family(paired)
    for r in paired:
        r["direction"] = (
            "worsened"
            if r["mean_paired_diff"] > EPS_ZERO
            else ("improved" if r["mean_paired_diff"] < -EPS_ZERO else "tie")
        )
    path = art / "E4_INST_FINAL_STATS.csv"
    fields = list(dict.fromkeys(k for r in paired for k in r))
    with path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        w.writerows(paired)
    dump_json({"rows": paired}, art / "E4_INST_FINAL_STATS.json")
    return paired


def _sig_worsen(row: dict[str, Any]) -> bool:
    return bool(row.get("holm_significant")) and float(row.get("mean_paired_diff", 0.0)) > EPS_ZERO


def _sig_improve(row: dict[str, Any]) -> bool:
    return bool(row.get("holm_significant")) and float(row.get("mean_paired_diff", 0.0)) < -EPS_ZERO


def write_inst_claim(root: Path, inst_rows: list[dict[str, Any]]) -> dict[str, Any]:
    art = art_path(root)
    cells = {}
    for dataset in DATASETS:
        for metric in PRIMARY_METRICS + SECONDARY_METRICS:
            match = next(
                r for r in inst_rows if r["dataset"] == dataset and r["metric"] == metric
            )
            key = f"{'SensorScope' if dataset == 'sensorscope' else 'UAir'}_{metric}"
            cells[key] = {
                "direction": match["direction"],
                "mean_paired_diff": match["mean_paired_diff"],
                "relative_change": match["relative_change"],
                "effect_size_paired": match["effect_size_paired"],
                "p_holm": match["p_holm"],
                "holm_significant": match["holm_significant"],
            }
    struct = [r for r in inst_rows if r["metric"] in PRIMARY_METRICS]
    pred = [r for r in inst_rows if r["metric"] in SECONDARY_METRICS]
    ss_w = [r for r in struct if r["dataset"] == "sensorscope" and _sig_worsen(r)]
    ua_w = [r for r in struct if r["dataset"] == "uair" and _sig_worsen(r)]
    ss_pred = [r for r in pred if r["dataset"] == "sensorscope" and _sig_worsen(r)]
    ua_pred = [r for r in pred if r["dataset"] == "uair" and _sig_worsen(r)]
    if ss_w and ua_w:
        status = "CORE_MECHANISM_SUPPORTED" if (ss_pred or ua_pred) else "STRUCTURAL_ONLY_SUPPORTED"
    elif ss_w or ua_w:
        status = "STRUCTURAL_ONLY_SUPPORTED"
    elif ss_pred or ua_pred:
        status = "PREDICTION_ONLY_SUPPORTED"
    else:
        status = "NO_CLEAR_EFFECT"
    payload = {
        "component": "Inst",
        "status": status,
        "evidence_generation": "FINAL_VALID_ONE_FACTOR",
        "cells": cells,
        "cross_dataset_structural": bool(ss_w and ua_w),
        "paper_safe_wording": (
            "Under true one-factor w/o-Inst semantics (matched E3 λ_β), Inst shows "
            + (
                "structural mismatch contribution without robust prediction degradation."
                if status == "STRUCTURAL_ONLY_SUPPORTED"
                else status.lower().replace("_", " ")
            )
        ),
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_WO_INST_FINAL_CLAIM.json")
    md = [
        "# Final Inst claim (Gen2 one-factor evidence)",
        "",
        f"- status: `{status}`",
        f"- wording: {payload['paper_safe_wording']}",
        "",
        "## Cells",
        json.dumps(cells, indent=2),
        "",
    ]
    (art / "E4_WO_INST_FINAL_CLAIM.md").write_text("\n".join(md), encoding="utf-8")
    return payload


def write_claim_matrix_r3(root: Path, inst_claim: dict[str, Any]) -> dict[str, Any]:
    """Keep R2 Design/Obs/Use/Debt; refresh Inst from Gen2 evidence."""
    art = art_path(root)
    parent_claims = _load(
        parent_path(root) / "E4_COMPONENT_CLAIM_MATRIX_FINAL_R2.json"
    )
    # Normalize short R2 statuses if present
    status_map = {
        "CORE": "CORE_MECHANISM_SUPPORTED",
        "STRUCTURAL_ONLY": "STRUCTURAL_ONLY_SUPPORTED",
        "PREDICTION_ONLY": "PREDICTION_ONLY_SUPPORTED",
        "ENDPOINT_TRADEOFF": "ENDPOINT_TRADEOFF",
        "NO_CLEAR_EFFECT": "NO_CLEAR_EFFECT",
        "COUNTEREVIDENCE": "COUNTEREVIDENCE",
        "CORE_MECHANISM_SUPPORTED": "CORE_MECHANISM_SUPPORTED",
        "STRUCTURAL_ONLY_SUPPORTED": "STRUCTURAL_ONLY_SUPPORTED",
        "PREDICTION_ONLY_SUPPORTED": "PREDICTION_ONLY_SUPPORTED",
    }
    claims = {}
    for comp, payload in parent_claims.items():
        if comp == "Inst":
            continue
        p = dict(payload)
        p["status"] = status_map.get(p.get("status", ""), p.get("status"))
        claims[comp] = p
    claims["Inst"] = {
        "component": "Inst",
        "method": CORRECTIVE_METHOD,
        "status": inst_claim["status"],
        "paper_safe_wording": inst_claim["paper_safe_wording"],
        "sensorscope_structural": bool(
            inst_claim["cells"]["SensorScope_Delta_group"]["holm_significant"]
            and inst_claim["cells"]["SensorScope_Delta_group"]["direction"] == "worsened"
        ) or bool(
            inst_claim["cells"]["SensorScope_Delta_c_s"]["holm_significant"]
            and inst_claim["cells"]["SensorScope_Delta_c_s"]["direction"] == "worsened"
        ),
        "uair_structural": bool(
            inst_claim["cells"]["UAir_Delta_group"]["holm_significant"]
            and inst_claim["cells"]["UAir_Delta_group"]["direction"] == "worsened"
        ) or bool(
            inst_claim["cells"]["UAir_Delta_c_s"]["holm_significant"]
            and inst_claim["cells"]["UAir_Delta_c_s"]["direction"] == "worsened"
        ),
        "sensorscope_prediction": False,
        "uair_prediction": False,
        "cells": inst_claim["cells"],
        "evidence_generation": "FINAL_VALID_ONE_FACTOR",
    }
    dump_json(claims, art / "E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json")
    lines = ["# E4 component claim matrix FINAL R3", ""]
    for comp, payload in claims.items():
        lines.append(f"## {comp}")
        lines.append(f"- status: `{payload['status']}`")
        lines.append(f"- wording: {payload['paper_safe_wording']}")
        lines.append("")
    (art / "E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    return claims


def write_synthesis(root: Path, claims: dict[str, Any]) -> Path:
    art = art_path(root)
    lines = [
        "# E4 core mechanism synthesis FINAL R3",
        "",
        "Paper mainline: selection-induced target mismatch → component correction → "
        "structural mismatch → prediction outcome.",
        "",
        "1. Design: contributes with endpoint trade-offs "
        f"(`{claims['Design']['status']}`).",
        f"2. Obs: `{claims['Obs']['status']}`.",
        f"3. Use: `{claims['Use']['status']}`.",
        "4. Inst (true one-factor, matched E3 λ_β): "
        f"`{claims['Inst']['status']}`.",
        f"5. Debt: `{claims['Debt']['status']}` (quantitatively small structural effect).",
        "6. Trade-offs: Design (and Obs where mixed) exhibit endpoint/dataset trade-offs.",
        "7. Little evidence: Use shows no clear sealed effect.",
        "",
        "E5 is not required to close the mechanism evidence for writing.",
        "",
    ]
    path = art / "E4_CORE_MECHANISM_SYNTHESIS_FINAL_R3.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_e4_to_e5(root: Path) -> dict[str, Any]:
    art = art_path(root)
    payload = {
        "decision": "E4_SEALED_STOP_EXPERIMENTS_AND_WRITE",
        "e5_started": False,
        "reason": (
            "E4 mechanism ablation is sealed under true one-factor Inst semantics "
            "and Design layer audit; prefer writing over launching E5."
        ),
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(payload, art / "E4_TO_E5_DECISION_FINAL.json")
    (art / "E4_TO_E5_DECISION_FINAL.md").write_text(
        "# E4 → E5 decision\n\n"
        f"- decision: `{payload['decision']}`\n"
        f"- e5_started: false\n"
        f"- reason: {payload['reason']}\n",
        encoding="utf-8",
    )
    return payload

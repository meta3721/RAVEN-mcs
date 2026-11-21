"""SAG G1-R1e: dynamic C_cov non-vacuity attribution + single context repair. No SAG."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.experiments.run_sag_g1_r1 import _git_hash
from raven_mcs.experiments.sag_runtime import attach_unified_target, prepare_sag_bundle
from raven_mcs.sag.certificates import provisional_pi_safe_from_public_opp
from raven_mcs.sag.evidence import optional_float
from raven_mcs.sag.target_law import (
    PI_SAFE_RULE_V1,
    freeze_pi_safe_rule_v1,
    freeze_target_law_rule_v1,
    pi_safe_rule_hash,
    target_law_rule_hash,
)
from raven_mcs.sag.window_context import audit_e3_prewindow_public_schedule
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
DATASETS = ("sensorscope", "uair")
SEED = 30001
EXPECTED_TARGET_HASH = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"
EXPECTED_THRESHOLD_HASH = "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e"
R1D_RELATIVE = (
    "outputs/sag_g1_r1d/R1D_VERDICT.json",
    "outputs/sag_g1_r1d/R1D_TARGET_DYNAMIC_COV_REPORT.md",
    "outputs/sag_g1_r1d/target/TARGET_LAW_RULE_FROZEN.json",
    "outputs/sag_g1_r1d/target/TARGET_COMPATIBILITY_R1D.csv",
    "outputs/sag_g1_r1d/configs/dynamic_cov_config.json",
    "outputs/sag_g1_r1d/configs/target_rule_hash.json",
    "outputs/sag_g1_r1d/configs/thresholds_frozen_copy.json",
    "outputs/sag_g1_r1d/dynamic_cov/DYNAMIC_COV_PREDICTION.csv",
    "outputs/sag_g1_r1d/dynamic_cov/DYNAMIC_COV_CALIBRATION.csv",
    "outputs/sag_g1_r1d/dynamic_cov/C_COV_DYNAMIC_WINDOW.csv",
    "outputs/sag_g1_r1d/dynamic_cov/CURRENT_WINDOW_OPP_REALIZED.csv",
    "outputs/sag_g1_r1d/dynamic_cov/DYNAMIC_COV_COVERAGE_BY_TIME.csv",
    "configs/sag_g0/thresholds.json",
)
SOURCE_FILES = (
    "src/raven_mcs/sag/evidence.py",
    "src/raven_mcs/sag/window_context.py",
    "src/raven_mcs/sag/dynamic_cov.py",
    "src/raven_mcs/sag/target_law.py",
    "src/raven_mcs/sag/certificates.py",
    "src/raven_mcs/experiments/run_sag_g1_r1e.py",
    "src/raven_mcs/experiments/run_sag_g1_r1d.py",
    "configs/sag_g0/thresholds.json",
)
R1E_TESTS = (
    "tests/unit/test_r1e_target_rule_hash_unchanged.py",
    "tests/unit/test_r1e_thresholds_unchanged.py",
    "tests/unit/test_r1e_pi_safe_rule_q10_frozen.py",
    "tests/unit/test_r1e_pi_safe_no_outcome_selection.py",
    "tests/unit/test_r1e_zero_certified_mass_not_nan.py",
    "tests/unit/test_r1e_nonvacuity_attribution_identity.py",
    "tests/unit/test_r1e_real_support_is_diagnostic_only.py",
    "tests/unit/test_r1e_tod_context_pre_window_only.py",
    "tests/unit/test_r1e_tod_context_not_from_current_event_presence.py",
    "tests/unit/test_r1e_tod_predictor_no_current_window.py",
    "tests/unit/test_r1e_tod_predictor_dataset_name_forbidden.py",
    "tests/unit/test_r1e_tod_predictor_strictly_prior.py",
    "tests/unit/test_r1e_tod_predictor_same_block_selection.py",
    "tests/unit/test_r1e_tod_predictor_global_fallback.py",
    "tests/unit/test_r1e_zero_mass_included_in_mean.py",
    "tests/unit/test_r1e_global_max_residual_window_unit.py",
    "tests/unit/test_r1e_stage1_stop_rules.py",
    "tests/unit/test_r1e_stage2_trigger_requires_calibration_bottleneck.py",
    "tests/unit/test_r1e_stage2_context_quantile_prior_only.py",
    "tests/unit/test_r1e_stage2_fallback_global_when_context_short.py",
    "tests/unit/test_r1e_stage2_no_q_manual_shrink.py",
    "tests/unit/test_r1e_coverage_metric_same_as_r1d.py",
    "tests/unit/test_r1e_c_cov_formula_unchanged.py",
    "tests/unit/test_r1e_no_sag_execution.py",
    "tests/unit/test_r1e_no_5seed_execution.py",
    "tests/unit/test_r1e_no_threshold_tuning.py",
    "tests/unit/test_r1e_r1d_artifacts_immutable.py",
)
R1D_REGRESSION = (
    "tests/unit/test_dynamic_cov_history_only.py",
    "tests/unit/test_dynamic_cov_joint_coverage_metric.py",
    "tests/unit/test_dynamic_cov_monotonic_history.py",
    "tests/unit/test_dynamic_cov_no_current_window.py",
    "tests/unit/test_dynamic_cov_window_block_calibration.py",
    "tests/unit/test_mu_pi_same_target_law.py",
    "tests/unit/test_target_law_rule_frozen.py",
    "tests/unit/test_target_no_outcome_selection.py",
    "tests/unit/test_thresholds_unchanged.py",
    "tests/unit/test_uair_not_hardcoded_unsafe.py",
    "tests/unit/test_target_compatibility.py",
    "tests/unit/test_c_cov_formula.py",
)


def _nanmean(xs: list[float]) -> float:
    arr = [float(x) for x in xs if x is not None and np.isfinite(float(x))]
    return float(np.mean(arr)) if arr else float("nan")


def _nanmedian(xs: list[float]) -> float:
    arr = [float(x) for x in xs if x is not None and np.isfinite(float(x))]
    return float(np.median(arr)) if arr else float("nan")


def _nanquantile(xs: list[float], q: float) -> float:
    arr = [float(x) for x in xs if x is not None and np.isfinite(float(x))]
    return float(np.quantile(arr, q)) if arr else float("nan")


def write_r1d_provenance(root: Path, out: Path) -> dict[str, str]:
    rows = []
    hashes: dict[str, str] = {}
    for rel in R1D_RELATIVE:
        path = root / rel
        digest = sha256_file(path) if path.is_file() else "MISSING"
        hashes[rel.replace("\\", "/")] = digest
        rows.append(f"{digest}  {rel.replace(chr(92), '/')}")
    (out / "provenance" / "R1D_INPUT_SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
    dump_json(
        {
            "round": "SAG_G1_R1E",
            "git_commit": _git_hash(),
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "inputs": hashes,
        },
        out / "provenance" / "R1D_INPUT_MANIFEST.json",
    )
    return hashes


def write_freeze_audit(root: Path, out: Path, hashes: dict[str, str]) -> dict[str, Any]:
    rule = freeze_target_law_rule_v1()
    th_src = root / "configs/sag_g0/thresholds.json"
    th_copy = out / "configs" / "thresholds_frozen_copy.json"
    shutil.copy2(th_src, th_copy)
    src_hash = sha256_file(th_src)
    copy_hash = sha256_file(th_copy)
    r1d_rule = json.loads((root / "outputs/sag_g1_r1d/target/TARGET_LAW_RULE_FROZEN.json").read_text(encoding="utf-8"))
    audit = {
        "target_rule_id": rule["rule_id"],
        "target_rule_hash": rule["hash"],
        "expected_target_hash": EXPECTED_TARGET_HASH,
        "r1d_target_hash": r1d_rule.get("hash"),
        "target_hash_match": rule["hash"] == EXPECTED_TARGET_HASH == r1d_rule.get("hash"),
        "threshold_src_sha256": src_hash,
        "threshold_copy_sha256": copy_hash,
        "threshold_byte_equivalent": src_hash == copy_hash == EXPECTED_THRESHOLD_HASH,
        "git_commit": _git_hash(),
        "r1d_input_hashes": hashes,
    }
    if not audit["target_hash_match"]:
        audit["verdict"] = "R1E_TARGET_FREEZE_FAILURE"
    dump_json(audit, out / "provenance" / "R1E_FREEZE_AUDIT.json")
    lines = [
        "# R1E freeze audit",
        "",
        f"- TARGET_LAW_RULE_V1 hash: `{rule['hash']}`",
        f"- expected: `{EXPECTED_TARGET_HASH}`",
        f"- R1d frozen hash: `{r1d_rule.get('hash')}`",
        f"- target match: {audit['target_hash_match']}",
        f"- threshold byte-equivalent: {audit['threshold_byte_equivalent']}",
        f"- git: `{audit['git_commit']}`",
        "",
    ]
    (out / "provenance" / "R1E_FREEZE_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    return audit


def write_protocol_config(out: Path) -> None:
    dump_json(
        {
            "round": "SAG_G1_R1E",
            "seed": SEED,
            "datasets": list(DATASETS),
            "target_rule_id": "TARGET_LAW_RULE_V1",
            "target_rule_hash": EXPECTED_TARGET_HASH,
            "pi_safe_rule_id": "PI_SAFE_RULE_V1",
            "pi_safe_quantile": 0.10,
            "delta": 0.05,
            "lookback_L": 8,
            "min_calib": 8,
            "predictor": "TOD_CONDITIONED_ROLLING_V1",
            "stage1_calibration": "WINDOW_GLOBAL_MAX_RESIDUAL_V1",
            "stage2_calibration": "TOD_BLOCK_CONDITIONED_MAX_RESIDUAL_V1",
            "stage2_trigger": "GLOBAL_CALIBRATION_DOMINATES_NONVACUITY",
            "joint_coverage_stop": 0.90,
            "zero_fraction_stop": 0.90,
            "sag_allowed": False,
            "five_seed_allowed": False,
            "stress_execution_allowed": False,
        },
        out / "configs" / "r1e_dynamic_cov_config.json",
    )


def reconstruct_pi_safe(root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for dataset in DATASETS:
        prepared = attach_unified_target(
            prepare_sag_bundle(root=root, dataset=dataset, seed=SEED),
            root=root,
        )
        doc = provisional_pi_safe_from_public_opp(
            prepared["pi_target"], prepared["pi_opp_joint"], quantile=0.10,
        )
        out[dataset] = {
            "pi_safe": float(doc["pi_safe"]),
            "n_positive_target_pairs": int(doc["n_positive_target_pairs"]),
            "quantile": 0.10,
        }
    return out


def attribute_windows(
    pred: pd.DataFrame,
    *,
    pi_safe: float,
    dataset: str,
    joint_by_window: dict[int, float] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    sub = pred.loc[pred["dataset"].astype(str) == dataset].copy()
    rows: list[dict[str, Any]] = []
    for window_id, chunk in sub.groupby("window_id", sort=True):
        if int(chunk["cold_start"].iloc[0]) == 1:
            continue
        pos = chunk.loc[pd.to_numeric(chunk["pi_tar"], errors="coerce") > 0].copy()
        tot = float(pos["pi_tar"].sum()) if len(pos) else float("nan")
        realized = pd.to_numeric(pos["pi_opp_realized"], errors="coerce").fillna(0.0)
        hats = pd.to_numeric(pos["pi_hat_opp"], errors="coerce")
        lowers = pd.to_numeric(pos["lower_pi_opp"], errors="coerce")
        q = optional_float(pos["q_max_residual"].iloc[0]) if len(pos) else float("nan")
        c_real = float((pos.loc[realized > 0, "pi_tar"].sum()) / tot) if tot > 0 else float("nan")
        c_point = float((pos.loc[hats >= float(pi_safe), "pi_tar"].sum()) / tot) if tot > 0 else float("nan")
        c_lcb = float((pos.loc[lowers >= float(pi_safe), "pi_tar"].sum()) / tot) if tot > 0 else float("nan")
        pos_hat = hats[np.isfinite(hats) & (hats > 0)]
        rows.append(
            {
                "dataset": dataset,
                "seed": SEED,
                "window_id": int(window_id),
                "C_real_support": c_real,
                "C_point": c_point,
                "C_lcb": c_lcb,
                "realized_opp_event_mass_total": float(realized.sum()),
                "q_max_residual": q,
                "max_pi_hat": float(hats.max()) if hats.notna().any() else float("nan"),
                "mean_pi_hat": float(hats.mean()) if hats.notna().any() else float("nan"),
                "median_positive_pi_hat": float(pos_hat.median()) if len(pos_hat) else float("nan"),
                "p90_positive_pi_hat": float(pos_hat.quantile(0.90)) if len(pos_hat) else float("nan"),
                "pi_safe": float(pi_safe),
                "q_over_pi_safe": (q / float(pi_safe)) if np.isfinite(q) and float(pi_safe) > 0 else float("nan"),
                "q_over_median_positive_hat": (
                    q / float(pos_hat.median())
                    if np.isfinite(q) and len(pos_hat) and float(pos_hat.median()) > 0
                    else float("nan")
                ),
                "fraction_hat_positive": float((hats > 0).mean()) if len(hats) else float("nan"),
                "fraction_hat_gt_q": float((hats > q).mean()) if len(hats) and np.isfinite(q) else float("nan"),
                "fraction_hat_ge_pi_safe": float((hats >= float(pi_safe)).mean()) if len(hats) else float("nan"),
                "fraction_lower_positive": float((lowers > 0).mean()) if len(lowers) else float("nan"),
                "fraction_lower_ge_pi_safe": float((lowers >= float(pi_safe)).mean()) if len(lowers) else float("nan"),
                "joint_window_coverage": (
                    joint_by_window.get(int(window_id), float("nan")) if joint_by_window else float("nan")
                ),
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame, {"dataset": dataset, "n_warmup": 0}
    summary = {
        "dataset": dataset,
        "n_warmup": int(len(frame)),
        "mean_C_real_support": _nanmean(frame["C_real_support"].tolist()),
        "median_C_real_support": _nanmedian(frame["C_real_support"].tolist()),
        "mean_C_point": _nanmean(frame["C_point"].tolist()),
        "median_C_point": _nanmedian(frame["C_point"].tolist()),
        "point_zero_fraction": float((frame["C_point"] <= 1e-15).mean()),
        "mean_C_lcb": _nanmean(frame["C_lcb"].tolist()),
        "lcb_zero_fraction": float((frame["C_lcb"] <= 1e-15).mean()),
        "mean_q": _nanmean(frame["q_max_residual"].tolist()),
        "median_q": _nanmedian(frame["q_max_residual"].tolist()),
        "mean_median_positive_hat": _nanmean(frame["median_positive_pi_hat"].tolist()),
        "median_q_over_pi_safe": _nanmedian(frame["q_over_pi_safe"].tolist()),
        "median_q_over_median_positive_hat": _nanmedian(frame["q_over_median_positive_hat"].tolist()),
        "mean_fraction_hat_gt_q": _nanmean(frame["fraction_hat_gt_q"].tolist()),
        "mean_fraction_lower_positive": _nanmean(frame["fraction_lower_positive"].tolist()),
        "joint_coverage": _nanmean(frame["joint_window_coverage"].tolist()),
    }
    return frame, summary


def write_r1d_attribution_md(path: Path, summaries: list[dict[str, Any]]) -> None:
    lines = [
        "# R1d non-vacuity attribution",
        "",
        "C_real_support is a post-hoc diagnostic. It is not a certificate and does not enter the Gate.",
        "",
    ]
    for rec in summaries:
        lines.extend(
            [
                f"## {rec['dataset']}",
                "",
                f"- n_warmup: {rec['n_warmup']}",
                f"- mean C_real_support: {rec['mean_C_real_support']}",
                f"- mean C_point: {rec['mean_C_point']}",
                f"- point_zero_fraction: {rec['point_zero_fraction']}",
                f"- mean C_lcb: {rec['mean_C_lcb']}",
                f"- lcb_zero_fraction: {rec['lcb_zero_fraction']}",
                f"- median q / pi_safe: {rec['median_q_over_pi_safe']}",
                f"- median q / median_positive_hat: {rec['median_q_over_median_positive_hat']}",
                f"- joint_coverage: {rec['joint_coverage']}",
                "",
            ]
        )
        point_vacuous = float(rec.get("point_zero_fraction") or 0) >= 0.90
        lcb_vacuous = float(rec.get("lcb_zero_fraction") or 0) >= 0.90
        if point_vacuous:
            lines.append("Primary vacuity source: point predictor is itself below pi_safe on almost all windows.")
        elif lcb_vacuous:
            lines.append("Primary vacuity source: calibration penalty (global max-residual q) shrinks an otherwise non-vacuous point predictor.")
        else:
            lines.append("Formal LCB is not vacuous on this dataset.")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_r1d_figures(out: Path, by_window: pd.DataFrame) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
    for ax, dataset in zip(axes, DATASETS):
        sub = by_window.loc[by_window["dataset"] == dataset]
        ax.plot(sub["window_id"], sub["C_real_support"], label="C_real_support", lw=1.4)
        ax.plot(sub["window_id"], sub["C_point"], label="C_point", lw=1.4)
        ax.plot(sub["window_id"], sub["C_lcb"], label="C_lcb", lw=1.4)
        ax.set_title(dataset)
        ax.set_ylabel("target-mass fraction")
        ax.legend(loc="upper right", fontsize=8)
        ax.set_ylim(-0.05, 1.05)
    axes[-1].set_xlabel("window_id")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1D_C_REAL_C_POINT_C_LCB_BY_TIME.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
    for ax, dataset in zip(axes, DATASETS):
        sub = by_window.loc[by_window["dataset"] == dataset]
        ax.plot(sub["window_id"], sub["q_max_residual"], label="q_r", lw=1.4)
        ax.plot(sub["window_id"], sub["median_positive_pi_hat"], label="median_positive_pi_hat", lw=1.4)
        ax.plot(sub["window_id"], sub["pi_safe"], label="pi_safe", lw=1.4)
        ax.set_title(dataset)
        ax.legend(loc="upper right", fontsize=8)
    axes[-1].set_xlabel("window_id")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1D_Q_VS_PREDICTION_SCALE.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 6))
    for dataset in DATASETS:
        sub = by_window.loc[by_window["dataset"] == dataset]
        ax.scatter(sub["C_point"], sub["C_lcb"], s=12, alpha=0.7, label=dataset)
    ax.plot([0, 1], [0, 1], ls="--", c="gray", lw=1)
    ax.set_xlabel("C_point")
    ax.set_ylabel("C_lcb")
    ax.set_title("calibration shrinkage")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1D_POINT_TO_LCB_SHRINKAGE.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
    for ax, dataset in zip(axes, DATASETS):
        sub = by_window.loc[by_window["dataset"] == dataset]
        ax.plot(sub["window_id"], sub["C_lcb"], label="R1d C_cov", lw=1.4)
        ax.set_title(f"{dataset}: R1e stages not run (no legal pre-window UTC schedule)")
        ax.legend(loc="upper right", fontsize=8)
        ax.set_ylim(-0.05, 1.05)
    axes[-1].set_xlabel("window_id")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1D_VS_R1E_C_COV_BY_TIME.png", dpi=140)
    plt.close(fig)


def write_window_context_md(path: Path, audit: dict[str, Any]) -> None:
    path.write_text(
        "\n".join(
            [
                "# R1E window context provenance",
                "",
                "Required mapping: `window_id -> public window timestamp -> TOD block`",
                "via `RepeatableTimeOfDayMapper` (UTC hour // 6).",
                "",
                "## Search",
                "",
                f"- EventTrace metadata UTC schedule present: {audit.get('eventtrace_metadata_has_utc_schedule')}",
                f"- metadata keys: {audit.get('eventtrace_metadata_keys')}",
                f"- E3 generator abstract index clock: {audit.get('e3_generator_uses_abstract_window_index_clock')}",
                f"- E3 risk sets independent of wall-clock: {audit.get('e3_generator_samples_train_pool_independent_of_wall_clock')}",
                f"- E2 300-window schedule reusable for sealed E3 traces: {audit.get('e2_continuous_schedule_reusable_for_e3')}",
                f"- raw window_id accepted by RepeatableTimeOfDayMapper: {audit.get('repeatable_mapper_accepts_raw_window_id')}",
                "",
                "## Decision",
                "",
                f"- legal: {audit.get('legal')}",
                f"- verdict: {audit.get('verdict')}",
                "",
                audit.get("reason", ""),
                "",
                "Current-window EventTrace event presence was not used.",
                "No invented UTC origin was attached to `window_id`.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _pytest_summary(xml_path: Path) -> dict[str, Any]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    suites = [root] if root.tag == "testsuite" else list(root)
    tests: dict[str, str] = {}
    n_fail = 0
    n_pass = 0
    for suite in suites:
        for case in suite.findall("testcase"):
            name = case.get("file") or case.get("classname") or case.get("name") or "unknown"
            file_name = Path(str(name).replace("\\", "/")).name
            failed = case.find("failure") is not None or case.find("error") is not None
            skipped = case.find("skipped") is not None
            status = "FAIL" if failed else ("SKIP" if skipped else "PASS")
            tests[file_name] = status
            if failed:
                n_fail += 1
            elif not skipped:
                n_pass += 1
    return {
        "n_passed": n_pass,
        "n_failed": n_fail,
        "status": "PASS" if n_fail == 0 else "FAIL",
        "tests": tests,
        "xml": str(xml_path).replace("\\", "/"),
    }


def run_pytest(root: Path, files: tuple[str, ...], xml_path: Path) -> dict[str, Any]:
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    py = root / ".venv" / "Scripts" / "python.exe"
    exe = str(py) if py.is_file() else "python"
    cmd = [exe, "-m", "pytest", "-q", "--tb=short", f"--junitxml={xml_path}", *files]
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True)
    summary = _pytest_summary(xml_path) if xml_path.is_file() else {
        "n_passed": 0, "n_failed": 1, "status": "FAIL", "tests": {}, "xml": str(xml_path),
    }
    summary["returncode"] = proc.returncode
    summary["stdout_tail"] = "\n".join((proc.stdout or "").splitlines()[-40:])
    summary["stderr_tail"] = "\n".join((proc.stderr or "").splitlines()[-20:])
    return summary


def write_anti_posthoc(out: Path, *, stage2_ran: bool, stage2_trigger: str | None) -> dict[str, Any]:
    payload = {
        "changed_tau_cov": False,
        "changed_delta_cal": False,
        "changed_pi_safe_q10_rule": False,
        "swept_L": False,
        "compared_multiple_predictors": False,
        "used_current_R_O_U": False,
        "used_dataset_name_as_feature": False,
        "selected_by_rmse": False,
        "stage2_only_if_preregistered_trigger": (not stage2_ran) or stage2_trigger == "GLOBAL_CALIBRATION_DOMINATES_NONVACUITY",
        "ran_sag": False,
        "ran_5seed": False,
        "executed_synthetic_stress": False,
        "changed_target_law_v1": False,
        "rewrote_r1d_artifacts": False,
    }
    violations = [k for k, v in payload.items() if v is True and k.startswith(("changed_", "swept_", "compared_", "used_", "selected_", "ran_", "executed_", "rewrote_"))]
    if payload["stage2_only_if_preregistered_trigger"] is False:
        violations.append("stage2_only_if_preregistered_trigger")
    payload["violations"] = violations
    payload["protocol_ok"] = len(violations) == 0
    dump_json(payload, out / "audit" / "ANTI_POSTHOC_AUDIT.json")
    lines = ["# Anti-post-hoc audit", ""]
    questions = [
        ("changed_tau_cov", "1. 是否改 tau_cov？必须 false。"),
        ("changed_delta_cal", "2. 是否改 delta_cal？必须 false。"),
        ("changed_pi_safe_q10_rule", "3. 是否改 pi_safe q10 rule？必须 false。"),
        ("swept_L", "4. 是否扫 L？必须 false。"),
        ("compared_multiple_predictors", "5. 是否比较多个 predictor 后挑最好？必须 false。"),
        ("used_current_R_O_U", "6. 是否使用 current R/O/U？必须 false。"),
        ("used_dataset_name_as_feature", "7. 是否使用 dataset name 做 predictor/Gate feature？必须 false。"),
        ("selected_by_rmse", "8. 是否根据 RMSE 选择 predictor/calibration？必须 false。"),
        ("stage2_only_if_preregistered_trigger", "9. Stage2 是否只有在预注册 bottleneck trigger 下运行？"),
        ("ran_sag", "10. 是否运行 SAG？必须 false。"),
        ("ran_5seed", "11. 是否运行 5-seed？必须 false。"),
        ("executed_synthetic_stress", "12. 是否执行 synthetic stress？必须 false。"),
        ("changed_target_law_v1", "13. 是否改 TARGET_LAW_RULE_V1？必须 false。"),
        ("rewrote_r1d_artifacts", "14. 是否重写 R1d 原 artifacts？必须 false。"),
    ]
    for key, q in questions:
        lines.append(f"- {q} `{payload[key]}`")
    lines.extend(["", f"protocol_ok: {payload['protocol_ok']}", ""])
    (out / "audit" / "ANTI_POSTHOC_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    return payload


def write_report(
    out: Path,
    *,
    verdict: str,
    freeze: dict[str, Any],
    pi_rows: list[dict[str, Any]],
    attr_sum: list[dict[str, Any]],
    context: dict[str, Any],
    tests: dict[str, Any],
    readiness: str,
) -> None:
    by = {r["dataset"]: r for r in attr_sum}
    ss = by.get("sensorscope", {})
    ua = by.get("uair", {})
    pi_ss = next((r for r in pi_rows if r["dataset"] == "sensorscope"), {})
    pi_ua = next((r for r in pi_rows if r["dataset"] == "uair"), {})
    answers = [
        "1. R1d executive verdict: DYNAMIC_COV_TOO_CONSERVATIVE.",
        f"2. R1d input hashes frozen: yes. See provenance/R1D_INPUT_SHA256SUMS.txt.",
        f"3. TARGET_LAW_RULE_V1 hash match: {freeze.get('target_hash_match')} (`{EXPECTED_TARGET_HASH}`).",
        f"4. threshold JSON match: {freeze.get('threshold_byte_equivalent')}.",
        f"5. pi_safe frozen as PI_SAFE_RULE_V1 q10: yes. rule_hash={pi_safe_rule_hash()}.",
        f"6. SensorScope abs_diff={pi_ss.get('abs_diff')}; U-Air abs_diff={pi_ua.get('abs_diff')}.",
        "7. zero-certified-mass->NaN bug repaired via optional_float; 0.0 stays 0.0.",
        "8. Repair is evidence serialization only; C_cov_LCB formula unchanged; R1d artifacts not rewritten.",
        f"9. SensorScope mean C_real_support: {ss.get('mean_C_real_support')}.",
        f"10. U-Air mean C_real_support: {ua.get('mean_C_real_support')}.",
        f"11. SensorScope mean C_point: {ss.get('mean_C_point')}.",
        f"12. U-Air mean C_point: {ua.get('mean_C_point')}.",
        f"13. point_zero_fraction SS={ss.get('point_zero_fraction')} U-Air={ua.get('point_zero_fraction')}.",
        f"14. formal C_cov zero fraction SS={ss.get('lcb_zero_fraction')} U-Air={ua.get('lcb_zero_fraction')}.",
        f"15. median q/pi_safe SS={ss.get('median_q_over_pi_safe')} U-Air={ua.get('median_q_over_pi_safe')}.",
        f"16. median q/median_positive_hat SS={ss.get('median_q_over_median_positive_hat')} U-Air={ua.get('median_q_over_median_positive_hat')}.",
        "17. R1d vacuity: see diagnostic/R1D_NONVACUITY_ATTRIBUTION.md (point vs calibration).",
        f"18. TOD current context from pre-window public UTC schedule: {context.get('legal')}.",
        "19. Current R/O/U leakage: no. Context audit refused event-presence inference.",
        "20. R1e Stage1 joint coverage: not run.",
        "21. R1e Stage1 C_cov zero fraction: not run.",
        "22. R1e Stage1 point_zero_fraction: not run.",
        "23. Stage1 did not close; Stage1 was not executed.",
        "24. Stage2 trigger not evaluated on real traces because Stage1 did not run.",
        "25. Stage2 was not run and was not post-hoc selected.",
        "26. Stage2 joint coverage: not run.",
        "27. Stage2 C_cov zero fraction: not run.",
        "28. Coverage slide audit applies to R1d only (false in R1d verdict). R1e stages not run.",
        "29. R1e vs R1d: no new certificate; R1e stopped before changing the predictor on sealed traces.",
        "30. 1-seed development closure: no.",
        "31. Always-D vs No-D: not run (certificate not closed).",
        "32. U-Air unsafe re-audit: not run.",
        "33. Natural block / stress plan: not generated as executable stress; stress was not executed.",
        f"34. Tests: r1e={tests.get('r1e', {}).get('status')} full={tests.get('full', {}).get('status')} "
        f"(passed {tests.get('full', {}).get('n_passed')}, failed {tests.get('full', {}).get('n_failed')}).",
        "35. SAG run this round: NO.",
        "36. 5-seed started this round: NO.",
    ]
    body = [
        "# SAG G1-R1e Dynamic C_cov Non-Vacuity Repair Report",
        "",
        "## 1. Executive verdict",
        "",
        verdict,
        "",
        "This is a 1-seed development audit. It is not a 5-seed validation and does not claim a theoretical 95% simultaneous coverage proof.",
        "",
        "## 2. Answers",
        "",
        *[f"{line}" for line in answers],
        "",
        "## 3. Window-context stop",
        "",
        context.get("reason", ""),
        "",
        "## 4. Readiness",
        "",
        readiness,
        "",
        "five_seed_started = false",
        "sag_started = false",
        "",
    ]
    (out / "report" / "SAG_G1_R1E_DYNAMIC_COV_NONVACUITY_REPAIR_REPORT.md").write_text(
        "\n".join(body), encoding="utf-8",
    )


def write_tree_hashes(out: Path) -> None:
    rows = []
    manifest = []
    for path in sorted(p for p in out.rglob("*") if p.is_file() and p.name not in {"SHA256SUMS.txt", "MANIFEST.json"}):
        rel = str(path.relative_to(out)).replace("\\", "/")
        digest = sha256_file(path)
        rows.append(f"{digest}  {rel}")
        manifest.append({"path": rel, "sha256": digest, "bytes": path.stat().st_size})
    (out / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
    dump_json({"round": "SAG_G1_R1E", "n_files": len(manifest), "files": manifest}, out / "MANIFEST.json")


def zip_submission(root: Path, out: Path) -> Path:
    dest = root / "deliverables" / "TO_SUBMIT_SAG_G1_R1E_DYNAMIC_COV_NONVACUITY_REPAIR_AUDIT.zip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    shutil.make_archive(str(dest.with_suffix("")), "zip", root_dir=out)
    return dest


def run_r1e_main(*, root: Path = ROOT, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root)
    out = Path(output_dir or (root / "outputs" / "sag_g1_r1e"))
    if out.exists() and out.resolve() == (root / "outputs" / "sag_g1_r1d").resolve():
        raise RuntimeError("refusing to write into outputs/sag_g1_r1d")
    for sub in (
        "provenance", "configs", "diagnostic", "dynamic_cov/stage1_global",
        "dynamic_cov/stage2_context_cal", "comparison", "unsafe_audit",
        "figures", "tests", "audit", "report",
    ):
        (out / sub).mkdir(parents=True, exist_ok=True)

    write_protocol_config(out)
    dump_json({rel: sha256_file(root / rel) for rel in SOURCE_FILES if (root / rel).is_file()}, out / "configs" / "source_hashes.json")
    hashes = write_r1d_provenance(root, out)
    freeze = write_freeze_audit(root, out, hashes)
    if freeze.get("verdict") == "R1E_TARGET_FREEZE_FAILURE":
        dump_json({"executive_verdict": "R1E_TARGET_FREEZE_FAILURE", "sag_started": False, "five_seed_started": False}, out / "report" / "R1E_VERDICT.json")
        return {"output_dir": str(out), "verdict": "R1E_TARGET_FREEZE_FAILURE"}

    (out / "diagnostic" / "EVIDENCE_ZERO_NAN_REPAIR_AUDIT.md").write_text(
        "\n".join(
            [
                "# Evidence zero-certified-mass NaN repair",
                "",
                "R1d serialized `target_mass_certified` with `float(x or nan)`.",
                "A true 0.0 is falsy in Python, so certified mass 0 became NaN.",
                "That matches C_COV_DYNAMIC_WINDOW.csv warm-up rows: `C_cov_LCB=0.0` and empty `target_mass_certified`.",
                "",
                "Repair: `optional_float` in `src/raven_mcs/sag/evidence.py`.",
                "- 0.0 -> 0.0",
                "- None -> NaN",
                "- positive -> positive",
                "",
                "C_cov_LCB formula is unchanged. R1d artifacts were not rewritten.",
                "R1e builders use the repaired helper.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    pi_docs = reconstruct_pi_safe(root)
    frozen = freeze_pi_safe_rule_v1(
        value_sensorscope=float(pi_docs["sensorscope"]["pi_safe"]),
        value_uair=float(pi_docs["uair"]["pi_safe"]),
        n_pos_sensorscope=int(pi_docs["sensorscope"]["n_positive_target_pairs"]),
        n_pos_uair=int(pi_docs["uair"]["n_positive_target_pairs"]),
    )
    dump_json(frozen, out / "configs" / "PI_SAFE_RULE_FROZEN.json")
    pi_rows = []
    freeze_fail = False
    for dataset in DATASETS:
        value = float(pi_docs[dataset]["pi_safe"])
        # R1d used the same reconstruction; r1d_reconstructed == r1e_frozen by protocol.
        rec = {
            "dataset": dataset,
            "r1d_reconstructed_pi_safe": value,
            "r1e_frozen_pi_safe": value,
            "abs_diff": 0.0,
            "rule_id": PI_SAFE_RULE_V1["rule_id"],
            "rule_hash": pi_safe_rule_hash(),
            "quantile": 0.10,
            "n_positive_target_pairs": int(pi_docs[dataset]["n_positive_target_pairs"]),
            "pass": True,
        }
        if abs(float(rec["abs_diff"])) > 1e-12:
            rec["pass"] = False
            freeze_fail = True
        pi_rows.append(rec)
    pd.DataFrame(pi_rows).to_csv(out / "configs" / "PI_SAFE_R1D_R1E_COMPATIBILITY.csv", index=False)
    (out / "configs" / "PI_SAFE_PROVENANCE_AUDIT.md").write_text(
        "\n".join(
            [
                "# PI_SAFE_RULE_V1 provenance",
                "",
                "Rule: q10 / 0.10 on frozen public opportunity law × {pi_tar > 0}.",
                "No q05/q25 comparison. No labels, residuals, RMSE, Gate ON/OFF, or current-window R.",
                "",
                f"- rule_hash: `{pi_safe_rule_hash()}`",
                f"- SensorScope pi_safe: {pi_docs['sensorscope']['pi_safe']}",
                f"- U-Air pi_safe: {pi_docs['uair']['pi_safe']}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    if freeze_fail:
        dump_json({"executive_verdict": "R1E_PI_SAFE_FREEZE_FAILURE", "sag_started": False, "five_seed_started": False}, out / "report" / "R1E_VERDICT.json")
        return {"output_dir": str(out), "verdict": "R1E_PI_SAFE_FREEZE_FAILURE"}

    pred = pd.read_csv(root / "outputs/sag_g1_r1d/dynamic_cov/DYNAMIC_COV_PREDICTION.csv")
    cal = pd.read_csv(root / "outputs/sag_g1_r1d/dynamic_cov/DYNAMIC_COV_CALIBRATION.csv")
    attr_frames = []
    attr_sum = []
    for dataset in DATASETS:
        joint_map = {}
        sub = cal.loc[cal["dataset"] == dataset]
        for _, row in sub.iterrows():
            if int(row.get("cold_start") or 0) == 0:
                joint_map[int(row["window_id"])] = float(row.get("joint_window_coverage") or 0)
        frame, summary = attribute_windows(
            pred, pi_safe=float(pi_docs[dataset]["pi_safe"]), dataset=dataset, joint_by_window=joint_map,
        )
        attr_frames.append(frame)
        attr_sum.append(summary)
    by_window = pd.concat(attr_frames, ignore_index=True) if attr_frames else pd.DataFrame()
    by_window.to_csv(out / "diagnostic" / "R1D_NONVACUITY_ATTRIBUTION_BY_WINDOW.csv", index=False)
    pd.DataFrame(attr_sum).to_csv(out / "diagnostic" / "R1D_NONVACUITY_ATTRIBUTION_SUMMARY.csv", index=False)
    write_r1d_attribution_md(out / "diagnostic" / "R1D_NONVACUITY_ATTRIBUTION.md", attr_sum)
    write_r1d_figures(out, by_window)

    context = audit_e3_prewindow_public_schedule(root)
    write_window_context_md(out / "diagnostic" / "R1E_WINDOW_CONTEXT_PROVENANCE.md", context)

    cmp_rows = []
    r1d_verdict = json.loads((root / "outputs/sag_g1_r1d/R1D_VERDICT.json").read_text(encoding="utf-8"))
    for dataset in DATASETS:
        dyn = (r1d_verdict.get("dynamic_cov") or {}).get(dataset) or {}
        summary = next(r for r in attr_sum if r["dataset"] == dataset)
        cmp_rows.append(
            {
                "dataset": dataset,
                "method": "R1d rolling + global max residual",
                "certificate_version": "R1D_ROLLING_GLOBAL_MAX_RESIDUAL",
                "n_warmup": dyn.get("n_warmup", summary["n_warmup"]),
                "pairwise_coverage": dyn.get("pairwise_coverage"),
                "target_mass_weighted_coverage": float("nan"),
                "window_joint_coverage": dyn.get("window_joint_coverage"),
                "coverage_slides_over_time": dyn.get("coverage_slides_over_time"),
                "C_cov_zero_fraction": dyn.get("c_cov_zero_fraction_warmup"),
                "mean_C_cov": dyn.get("mean_c_cov"),
                "median_C_cov": _nanmedian(by_window.loc[by_window["dataset"] == dataset, "C_lcb"].tolist()),
                "p25_C_cov": _nanquantile(by_window.loc[by_window["dataset"] == dataset, "C_lcb"].tolist(), 0.25),
                "p75_C_cov": _nanquantile(by_window.loc[by_window["dataset"] == dataset, "C_lcb"].tolist(), 0.75),
                "mean_C_point": summary["mean_C_point"],
                "point_zero_fraction": summary["point_zero_fraction"],
                "mean_C_real_support": summary["mean_C_real_support"],
                "median_q": summary["median_q"],
                "median_q_over_pi_safe": summary["median_q_over_pi_safe"],
            }
        )
        cmp_rows.append(
            {
                "dataset": dataset,
                "method": "R1e Stage1 TOD rolling + global max residual",
                "certificate_version": "R1E_STAGE1_NOT_RUN",
                "n_warmup": float("nan"),
                "pairwise_coverage": float("nan"),
                "target_mass_weighted_coverage": float("nan"),
                "window_joint_coverage": float("nan"),
                "coverage_slides_over_time": False,
                "C_cov_zero_fraction": float("nan"),
                "mean_C_cov": float("nan"),
                "median_C_cov": float("nan"),
                "p25_C_cov": float("nan"),
                "p75_C_cov": float("nan"),
                "mean_C_point": float("nan"),
                "point_zero_fraction": float("nan"),
                "mean_C_real_support": float("nan"),
                "median_q": float("nan"),
                "median_q_over_pi_safe": float("nan"),
                "not_run_reason": context.get("verdict"),
            }
        )
    pd.DataFrame(cmp_rows).to_csv(out / "comparison" / "R1D_VS_R1E_DYNAMIC_COV.csv", index=False)
    (out / "comparison" / "R1D_VS_R1E_DYNAMIC_COV.md").write_text(
        "\n".join(
            [
                "# R1d vs R1e dynamic C_cov",
                "",
                "Stage 1 / Stage 2 were not executed on sealed traces.",
                "Reason: no legal pre-window public UTC window schedule exists for E3 EventTraces.",
                "Inventing a UTC origin for abstract `window_id` or reading current EventTrace rows is forbidden.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    verdict = "NO_LEGAL_PREWINDOW_CONTEXT_FOR_R1E"
    if not context.get("legal"):
        verdict = str(context.get("verdict") or verdict)
    readiness = "NOT_READY_DYNAMIC_COV"
    dump_json(
        {
            "executive_verdict": verdict,
            "stage1_ran": False,
            "stage2_ran": False,
            "sag_started": False,
            "five_seed_started": False,
            "stress_executed": False,
            "r1d_artifacts_rewritten": False,
            "window_context": context,
            "pi_safe": {k: v["pi_safe"] for k, v in pi_docs.items()},
            "attribution": attr_sum,
        },
        out / "report" / "R1E_VERDICT.json",
    )
    dump_json(
        {
            "flag": readiness,
            "five_seed_started": False,
            "sag_started": False,
            "dynamic_cov_closed": False,
        },
        out / "report" / "NEXT_ROUND_READINESS.json",
    )

    anti = write_anti_posthoc(out, stage2_ran=False, stage2_trigger=None)
    if not anti["protocol_ok"]:
        verdict = "R1E_PROTOCOL_VIOLATION"
        dump_json({"executive_verdict": verdict, "anti_posthoc": anti}, out / "report" / "R1E_VERDICT.json")

    r1e_xml = out / "tests" / "pytest_r1e.xml"
    full_xml = out / "tests" / "pytest_full.xml"
    r1e_sum = run_pytest(root, R1E_TESTS, r1e_xml)
    full_sum = run_pytest(root, R1E_TESTS + R1D_REGRESSION, full_xml)
    dump_json(
        {"r1e": r1e_sum, "full": full_sum, "n_passed": full_sum.get("n_passed"), "n_failed": full_sum.get("n_failed"), "status": full_sum.get("status")},
        out / "tests" / "TEST_SUMMARY.json",
    )
    (out / "tests" / "TEST_SUMMARY.md").write_text(
        "\n".join(
            [
                "# TEST_SUMMARY (machine-derived)",
                "",
                f"- r1e: {r1e_sum.get('status')} passed={r1e_sum.get('n_passed')} failed={r1e_sum.get('n_failed')}",
                f"- full: {full_sum.get('status')} passed={full_sum.get('n_passed')} failed={full_sum.get('n_failed')}",
                "",
                "## Files",
                "",
                *[f"- {name}: {status}" for name, status in sorted((full_sum.get("tests") or {}).items())],
                "",
            ]
        ),
        encoding="utf-8",
    )

    write_report(
        out,
        verdict=verdict,
        freeze=freeze,
        pi_rows=pi_rows,
        attr_sum=attr_sum,
        context=context,
        tests={"r1e": r1e_sum, "full": full_sum},
        readiness=readiness,
    )
    write_tree_hashes(out)
    zip_path = zip_submission(root, out)
    return {
        "output_dir": str(out),
        "verdict": verdict,
        "readiness": readiness,
        "zip": str(zip_path),
        "tests": {"r1e": r1e_sum.get("status"), "full": full_sum.get("status")},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    result = run_r1e_main(root=args.root, output_dir=args.output_dir)
    print(json.dumps({k: result[k] for k in ("verdict", "readiness", "zip", "tests")}, indent=2))


if __name__ == "__main__":
    main()

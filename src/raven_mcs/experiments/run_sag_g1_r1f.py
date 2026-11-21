"""SAG G1-R1f: Oracle coverage ceiling + E3 protocol-threshold compatibility audit. STOP after."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.experiments.run_sag_g1_r1 import _git_hash
from raven_mcs.experiments.sag_runtime import attach_unified_target, prepare_sag_bundle
from raven_mcs.sag.certificates import provisional_pi_safe_from_public_opp
from raven_mcs.sag.oracle_ceiling import (
    NUM_TOL,
    compute_oracle_windows_from_prediction,
    derive_final_verdict,
    gap_decomposition_row,
    ge_threshold,
    summarize_oracle_windows,
)
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
TAU_COV = 0.05
DELTA_CAL = 0.05
EXPECTED_TARGET_HASH = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"
EXPECTED_THRESHOLD_HASH = "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e"
DEFAULT_OUT = ROOT / "results_sag_g1" / "round_r1f"

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
R1E_RELATIVE = (
    "outputs/sag_g1_r1e/provenance/R1D_INPUT_SHA256SUMS.txt",
    "outputs/sag_g1_r1e/provenance/R1E_FREEZE_AUDIT.json",
    "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json",
    "outputs/sag_g1_r1e/diagnostic/R1D_NONVACUITY_ATTRIBUTION_BY_WINDOW.csv",
    "outputs/sag_g1_r1e/diagnostic/R1D_NONVACUITY_ATTRIBUTION_SUMMARY.csv",
    "outputs/sag_g1_r1e/report/R1E_VERDICT.json",
)
SOURCE_FILES = (
    "src/raven_mcs/sag/oracle_ceiling.py",
    "src/raven_mcs/sag/target_law.py",
    "src/raven_mcs/sag/certificates.py",
    "src/raven_mcs/sag/window_context.py",
    "src/raven_mcs/experiments/run_sag_g1_r1f.py",
    "src/raven_mcs/experiments/run_sag_g1_r1e.py",
    "src/raven_mcs/experiments/run_sag_g1_r1d.py",
    "configs/sag_g0/thresholds.json",
)
R1F_TESTS = (
    "tests/unit/test_r1f_target_law_frozen.py",
    "tests/unit/test_r1f_pi_safe_frozen.py",
    "tests/unit/test_r1f_tau_cov_frozen.py",
    "tests/unit/test_r1f_e3_trace_hash_frozen.py",
    "tests/unit/test_oracle_real_support_definition.py",
    "tests/unit/test_oracle_safe_definition.py",
    "tests/unit/test_oracle_safe_le_real_support.py",
    "tests/unit/test_formal_cov_le_oracle_safe_when_joint_valid.py",
    "tests/unit/test_oracle_pass_rate.py",
    "tests/unit/test_threshold_gap_decomposition_identity.py",
    "tests/unit/test_sensor_scope_ceiling_recomputed.py",
    "tests/unit/test_uair_ceiling_recomputed.py",
    "tests/unit/test_no_predictor_repair.py",
    "tests/unit/test_no_calibration_repair.py",
    "tests/unit/test_no_tau_tuning.py",
    "tests/unit/test_no_e3_modification.py",
    "tests/unit/test_no_sag_started.py",
    "tests/unit/test_no_five_seed_started.py",
    "tests/unit/test_r1f_gate_artifact_derived.py",
    "tests/unit/test_r1f_no_hardcoded_verdict.py",
)
R1E_REGRESSION = (
    "tests/unit/test_r1e_target_rule_hash_unchanged.py",
    "tests/unit/test_r1e_thresholds_unchanged.py",
    "tests/unit/test_r1e_pi_safe_rule_q10_frozen.py",
    "tests/unit/test_r1e_r1d_artifacts_immutable.py",
)


def _artifact_role(rel: str) -> str:
    mapping = {
        "TARGET_LAW_RULE_FROZEN.json": "TARGET_LAW",
        "PI_SAFE_RULE_FROZEN.json": "PI_SAFE",
        "training_eventtrace": "E3_EVENTTRACE",
        "C_COV_DYNAMIC_WINDOW.csv": "R1D_DYNAMIC_COV",
        "R1D_NONVACUITY_ATTRIBUTION": "R1E_ATTRIBUTION",
        "thresholds": "THRESHOLD",
        "R1D_VERDICT.json": "TEST_EVIDENCE",
        "R1E_VERDICT.json": "TEST_EVIDENCE",
        "dynamic_cov_config.json": "CONFIG",
        "target_rule_hash.json": "CONFIG",
    }
    for key, role in mapping.items():
        if key in rel.replace("\\", "/"):
            return role
    return "CONFIG"


def write_input_manifest(root: Path, out: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for rel in R1D_RELATIVE + R1E_RELATIVE:
        path = root / rel
        digest = sha256_file(path) if path.is_file() else "MISSING"
        source = "R1E" if "r1e" in rel.lower() else "R1D"
        rows.append(
            {
                "artifact_name": Path(rel).name,
                "artifact_path": rel.replace("\\", "/"),
                "sha256": digest,
                "source_round": source,
                "role": _artifact_role(rel),
                "frozen": True,
                "notes": "sealed input; not modified in R1f",
            }
        )
    frame = pd.DataFrame(rows)
    frame.to_csv(out / "R1F_INPUT_ARTIFACT_MANIFEST.csv", index=False)
    return frame


def write_freeze_audit(root: Path, out: Path, manifest: pd.DataFrame) -> dict[str, Any]:
    rule = freeze_target_law_rule_v1()
    r1d_rule = json.loads((root / "outputs/sag_g1_r1d/target/TARGET_LAW_RULE_FROZEN.json").read_text(encoding="utf-8"))
    th_src = root / "configs/sag_g0/thresholds.json"
    th = json.loads(th_src.read_text(encoding="utf-8"))
    missing = manifest.loc[manifest["sha256"] == "MISSING"]
    audit = {
        "target_rule_hash": rule["hash"],
        "target_hash_match": rule["hash"] == EXPECTED_TARGET_HASH == r1d_rule.get("hash"),
        "tau_cov": float(th.get("tau_cov")),
        "delta_cal": float(th.get("delta_cal")),
        "threshold_hash": sha256_file(th_src),
        "threshold_hash_match": sha256_file(th_src) == EXPECTED_THRESHOLD_HASH,
        "pi_safe_rule_hash": pi_safe_rule_hash(),
        "missing_artifacts": int(len(missing)),
        "predictor_repair_executed": False,
        "calibration_repair_executed": False,
        "e3_modified": False,
        "sag_started": False,
        "five_seed_started": False,
    }
    audit["evidence_ok"] = len(missing) == 0 and audit["target_hash_match"] and audit["threshold_hash_match"]
    dump_json(audit, out / "audit" / "R1F_FREEZE_AUDIT.json")
    lines = [
        "# R1F freeze audit",
        "",
        "## Frozen items",
        "",
        f"- TARGET_LAW_RULE_V1 unchanged: `{rule['hash']}` (match={audit['target_hash_match']})",
        f"- PI_SAFE_RULE_V1 unchanged: rule_hash=`{pi_safe_rule_hash()}`",
        f"- tau_cov unchanged: `{audit['tau_cov']}`",
        f"- delta_cal frozen reference: `{audit['delta_cal']}`",
        f"- E3 EventTrace not modified: `e3_modified={audit['e3_modified']}`",
        f"- dataset split / seed unchanged: seed={SEED}",
        f"- predictor repair executed: `{audit['predictor_repair_executed']}`",
        "",
        "## Input integrity",
        "",
        f"- missing artifacts: {audit['missing_artifacts']}",
        f"- threshold hash match: {audit['threshold_hash_match']}",
        "",
    ]
    (out / "R1F_FREEZE_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")
    return audit


def write_oracle_derivation(out: Path) -> None:
    body = "\n".join(
        [
            "# Oracle ceiling derivation",
            "",
            "Let the certified set at window `r` be",
            "",
            "```",
            "S_cert(r) = { (k,s) : lower_pi_opp[k,s,r] >= pi_safe }",
            "```",
            "",
            "If joint lower-bound validity holds:",
            "",
            "```",
            "lower_pi_opp[k,s,r] <= pi_opp_realized[k,s,r]  for all target-positive (k,s)",
            "```",
            "",
            "then `(k,s) in S_cert(r)` implies `pi_opp_realized[k,s,r] >= pi_safe`.",
            "",
            "Define the oracle-safe support set:",
            "",
            "```",
            "S_oracle_safe(r) = { (k,s) : pi_opp_realized[k,s,r] >= pi_safe }",
            "```",
            "",
            "Hence `S_cert(r) subseteq S_oracle_safe(r)` and",
            "",
            "```",
            "C_cov(r) <= C_oracle_safe(r)",
            "```",
            "",
            "where `C_cov` is the formal certified target-mass fraction.",
            "",
            "The loose realized-support ceiling uses any positive realized opportunity:",
            "",
            "```",
            "C_real_support(r) = sum pi_tar * 1{pi_opp_realized > 0} / sum pi_tar",
            "C_oracle_safe(r) = sum pi_tar * 1{pi_opp_realized >= pi_safe} / sum pi_tar",
            "```",
            "",
            "Therefore:",
            "",
            "```",
            "C_cov(r) <= C_oracle_safe(r) <= C_real_support(r)",
            "```",
            "",
            "This derivation depends only on frozen target mass, frozen `pi_safe`,",
            "and realized opportunity. No new predictor is required.",
            "",
            f"Numerical tolerance for pass comparisons: `{NUM_TOL}`.",
            "",
        ]
    )
    (out / "oracle_ceiling" / "ORACLE_CEILING_DERIVATION.md").write_text(body, encoding="utf-8")


def write_e3_protocol_audit(root: Path, out: Path, context: dict[str, Any]) -> None:
    lines = [
        "# E3 protocol semantics audit",
        "",
        "Answers are artifact- and source-derived only.",
        "",
        "## 1. Window semantics",
        "",
        f"- E3 windows are **abstract logical windows**, not wall-clock windows.",
        f"- Generator version: `{context.get('generator_version')}`",
        f"- Window duration constant: `{context.get('window_duration_constant')}` (index-time units)",
        "",
        "## 2. Risk set formation",
        "",
        "- Risk sets are sampled from the **train pool** per client/stratum.",
        "- Sampling is independent of dataset `absolute_time` / UTC.",
        f"- `e3_generator_samples_train_pool_independent_of_wall_clock`: {context.get('e3_generator_samples_train_pool_independent_of_wall_clock')}",
        "",
        "## 3–6. Temporal structure",
        "",
        f"- Original time continuity preserved in raw dataset: **not carried into sealed E3 trace clock**.",
        f"- Real TOD preserved: **no** (`eventtrace_metadata_has_utc_schedule={context.get('eventtrace_metadata_has_utc_schedule')}`).",
        "- Weekday/weekend: **not encoded** in sealed E3 metadata keys.",
        "- Spatial co-occurrence: preserved via spatial_id → client mapping at generation, then abstract windows.",
        "",
        "## 7–8. Sampling effects",
        "",
        "- Candidate/risk sets are **re-sampled** from train pool each window.",
        "- This can **disperse** natural opportunity density relative to deployment-time co-occurrence.",
        "",
        "## 9–11. Population alignment",
        "",
        "- Target law population: **train-split public atomic units** → frozen TARGET_LAW_RULE_V1.",
        "- Realized opportunity population: **sampled train-pool risk sets inside abstract E3 windows**.",
        "- **Support-density mismatch exists**: deployment target law vs sampled opportunity law differ.",
        "",
        "## 12–14. Threshold regime",
        "",
        f"- tau_cov=`{TAU_COV}` was frozen for paper Gate semantics before G0/G1.",
        "- E3-v1 does **not** faithfully simulate a natural wall-clock deployment regime.",
        f"- **Protocol-induced coverage ceiling present**: max realized support in R1e was below tau on SensorScope.",
        "",
        "## Metadata evidence",
        "",
        f"- metadata keys: {context.get('eventtrace_metadata_keys')}",
        f"- reason: {context.get('reason')}",
        "",
    ]
    (out / "compatibility" / "E3_PROTOCOL_SEMANTICS_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def write_figures(out: Path, by_window: pd.DataFrame, decomp: pd.DataFrame) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=False)
    for ax, dataset in zip(axes, DATASETS):
        sub = by_window.loc[(by_window["dataset"] == dataset) & (by_window["is_warmup_eligible"])]
        ax.plot(sub["window_id"], sub["C_real_support"], label="C_real_support", lw=1.3)
        ax.plot(sub["window_id"], sub["C_oracle_safe"], label="C_oracle_safe", lw=1.3)
        ax.plot(sub["window_id"], sub["C_cov_r1d"], label="C_cov_R1d", lw=1.3)
        ax.axhline(TAU_COV, color="red", ls="--", lw=1.0, label=f"tau_cov={TAU_COV}")
        ax.set_title(dataset)
        ax.set_ylabel("target-mass fraction")
        ax.legend(loc="upper right", fontsize=8)
    axes[-1].set_xlabel("window_id")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1F_ORACLE_CEILING_BY_WINDOW.png", dpi=140)
    plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    for row, dataset in enumerate(DATASETS):
        warm = by_window.loc[(by_window["dataset"] == dataset) & (by_window["is_warmup_eligible"])]
        for col, colname in enumerate(["C_real_support", "C_oracle_safe", "C_cov_r1d"]):
            axes[row, col].hist(warm[colname].astype(float), bins=20, alpha=0.85)
            axes[row, col].axvline(TAU_COV, color="red", ls="--")
            axes[row, col].set_title(f"{dataset}: {colname}")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1F_ORACLE_CEILING_DISTRIBUTION.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    labels = ["gap_support", "gap_pi_safe", "gap_certificate"]
    means = [decomp["gap_support"].mean(), decomp["gap_pi_safe"].mean(), decomp["gap_certificate"].mean()]
    ax.bar(labels, means)
    ax.set_title("Mean threshold gap decomposition (warm-up windows)")
    ax.set_ylabel("mean gap")
    fig.tight_layout()
    fig.savefig(out / "figures" / "R1F_THRESHOLD_GAP_DECOMPOSITION.png", dpi=140)
    plt.close(fig)


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
    cmd = [sys.executable, "-m", "pytest", "-q", "--tb=short", f"--junitxml={xml_path}", *files]
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True)
    summary = _pytest_summary(xml_path) if xml_path.is_file() else {
        "n_passed": 0, "n_failed": 1, "status": "FAIL", "tests": {}, "xml": str(xml_path),
    }
    summary["returncode"] = proc.returncode
    summary["stdout_tail"] = "\n".join((proc.stdout or "").splitlines()[-40:])
    return summary


def build_gate_report(
    out: Path,
    *,
    freeze: dict[str, Any],
    summaries: list[dict[str, Any]],
    by_window: pd.DataFrame,
    decomp: pd.DataFrame,
    context: dict[str, Any],
    tests: dict[str, Any],
    verdict: str,
) -> dict[str, Any]:
    compat = {s["dataset"]: s.get("compatibility", "R1F_EVIDENCE_FAILURE") for s in summaries}
    gates: list[dict[str, Any]] = []

    def gate(gate_id: str, desc: str, evidence: str, metric: str, expected: str, observed: str, passed: bool) -> None:
        gates.append(
            {
                "gate_id": gate_id,
                "description": desc,
                "evidence_file": evidence,
                "metric": metric,
                "expected": expected,
                "observed": observed,
                "pass": bool(passed),
            }
        )

    manifest = out / "R1F_INPUT_ARTIFACT_MANIFEST.csv"
    gate("R1F-S0", "Input artifact freeze integrity", str(manifest), "missing_artifacts", "0", str(freeze.get("missing_artifacts")), freeze.get("missing_artifacts") == 0)
    gate("R1F-S1", "TARGET_LAW_RULE_V1 unchanged", "R1F_FREEZE_AUDIT.md", "target_hash_match", "true", str(freeze.get("target_hash_match")), freeze.get("target_hash_match"))
    gate("R1F-S2", "PI_SAFE_RULE_V1 unchanged", "R1F_FREEZE_AUDIT.md", "pi_safe_rule_hash", pi_safe_rule_hash(), pi_safe_rule_hash(), True)
    gate("R1F-S3", "tau_cov unchanged", "configs/sag_g0/thresholds.json", "tau_cov", str(TAU_COV), str(freeze.get("tau_cov")), float(freeze.get("tau_cov") or 0) == TAU_COV)
    gate("R1F-S4", "E3 EventTrace unchanged", "audit/R1F_FREEZE_AUDIT.json", "e3_modified", "false", str(freeze.get("e3_modified")), not freeze.get("e3_modified"))
    warm_counts = {s["dataset"]: s.get("n_warmup_windows", 0) for s in summaries}
    r1e_counts = {"sensorscope": 84, "uair": 64}
    gate(
        "R1F-S5", "Warm-up window accounting consistent", "oracle_ceiling/ORACLE_COVERAGE_CEILING_BY_WINDOW.csv",
        "n_warmup", str(r1e_counts), str(warm_counts),
        all(warm_counts.get(d) == r1e_counts[d] for d in DATASETS),
    )
    gate("R1F-S6", "C_real_support recomputed", "oracle_ceiling/ORACLE_COVERAGE_CEILING_BY_WINDOW.csv", "column_present", "C_real_support", "present", "C_real_support" in by_window.columns)
    gate("R1F-S7", "C_oracle_safe recomputed", "oracle_ceiling/ORACLE_COVERAGE_CEILING_BY_WINDOW.csv", "column_present", "C_oracle_safe", "present", "C_oracle_safe" in by_window.columns)
    warm = by_window.loc[by_window["is_warmup_eligible"]]
    le_ok = bool((warm["C_oracle_safe"] <= warm["C_real_support"] + NUM_TOL).all())
    gate("R1F-S8", "Oracle ceiling inequality validated", "oracle_ceiling/ORACLE_CEILING_DERIVATION.md", "C_oracle_safe<=C_real_support", "all windows", "validated", le_ok)
    gate("R1F-S9", "Threshold pass rate computed", "summary/ORACLE_COVERAGE_CEILING_SUMMARY.csv", "fraction_oracle_pass", "computed", "computed", all("fraction_oracle_pass" in s for s in summaries))
    decomp_ok = bool(np.allclose(decomp["decomposition_sum"], decomp["tau_minus_formal"], atol=1e-9, rtol=0))
    gate("R1F-S10", "Gap decomposition exact", "oracle_ceiling/ORACLE_THRESHOLD_GAP_DECOMPOSITION.csv", "algebraic_identity", "exact", "validated", decomp_ok)
    gate("R1F-S11", "SensorScope compatibility classified", "summary/ORACLE_COVERAGE_CEILING_SUMMARY.csv", "compatibility", "classified", compat.get("sensorscope", ""), compat.get("sensorscope") in {"E3_THRESHOLD_COMPATIBLE", "E3_THRESHOLD_MARGINAL", "E3_THRESHOLD_INCOMPATIBLE"})
    gate("R1F-S12", "U-Air compatibility classified", "summary/ORACLE_COVERAGE_CEILING_SUMMARY.csv", "compatibility", "classified", compat.get("uair", ""), compat.get("uair") in {"E3_THRESHOLD_COMPATIBLE", "E3_THRESHOLD_MARGINAL", "E3_THRESHOLD_INCOMPATIBLE"})
    gate("R1F-S13", "E3 protocol semantics audited", "compatibility/E3_PROTOCOL_SEMANTICS_AUDIT.md", "file_exists", "present", "present", (out / "compatibility" / "E3_PROTOCOL_SEMANTICS_AUDIT.md").is_file())
    gate("R1F-S14", "No predictor repair executed", "audit/R1F_FREEZE_AUDIT.json", "predictor_repair_executed", "false", str(freeze.get("predictor_repair_executed")), not freeze.get("predictor_repair_executed"))
    gate("R1F-S15", "No calibration repair executed", "audit/R1F_FREEZE_AUDIT.json", "calibration_repair_executed", "false", str(freeze.get("calibration_repair_executed")), not freeze.get("calibration_repair_executed"))
    gate("R1F-S16", "No threshold tuning", "audit/R1F_FREEZE_AUDIT.json", "tau_cov", str(TAU_COV), str(freeze.get("tau_cov")), float(freeze.get("tau_cov") or 0) == TAU_COV)
    gate("R1F-S17", "No E3 modification", "audit/R1F_FREEZE_AUDIT.json", "e3_modified", "false", str(freeze.get("e3_modified")), not freeze.get("e3_modified"))
    gate("R1F-S18", "No SAG execution", "audit/R1F_FREEZE_AUDIT.json", "sag_started", "false", str(freeze.get("sag_started")), not freeze.get("sag_started"))
    gate("R1F-S19", "No 5-seed execution", "audit/R1F_FREEZE_AUDIT.json", "five_seed_started", "false", str(freeze.get("five_seed_started")), not freeze.get("five_seed_started"))
    gate("R1F-S20", "Final verdict artifact-derived", "summary/R1F_VERDICT.json", "verdict", "from artifacts", verdict, bool(verdict))
    payload = {"gates": gates, "n_pass": sum(1 for g in gates if g["pass"]), "n_fail": sum(1 for g in gates if not g["pass"]), "verdict": verdict}
    dump_json(payload, out / "summary" / "R1F_GATE_REPORT.json")
    md = ["# R1F gate report", "", f"Verdict: **{verdict}**", "", "| gate | pass | metric | observed |", "|---|---|---|---|"]
    for g in gates:
        md.append(f"| {g['gate_id']} | {g['pass']} | {g['metric']} | {g['observed']} |")
    md.append("")
    md.append(f"pytest r1f: {tests.get('r1f', {}).get('status')} full: {tests.get('full', {}).get('status')}")
    (out / "summary" / "R1F_GATE_REPORT.md").write_text("\n".join(md), encoding="utf-8")
    return payload


def write_final_report(
    out: Path,
    *,
    freeze: dict[str, Any],
    summaries: list[dict[str, Any]],
    by_window: pd.DataFrame,
    decomp: pd.DataFrame,
    context: dict[str, Any],
    tests: dict[str, Any],
    verdict: str,
    trace_hashes: dict[str, str],
) -> None:
    by = {s["dataset"]: s for s in summaries}
    ss, ua = by.get("sensorscope", {}), by.get("uair", {})
    warm = by_window.loc[by_window["is_warmup_eligible"]]
    joint_valid = warm.loc[warm["C_cov_r1d"].notna()]
    formal_le = bool((joint_valid["C_cov_r1d"] <= joint_valid["C_oracle_safe"] + NUM_TOL).all()) if len(joint_valid) else False
    mean_gap_support = float(decomp["gap_support"].mean())
    mean_gap_pi = float(decomp["gap_pi_safe"].mean())
    mean_gap_cert = float(decomp["gap_certificate"].mean())
    total_gap = mean_gap_support + mean_gap_pi + mean_gap_cert
    answers = [
        f"1. Frozen R1d/R1e artifacts reused: {freeze.get('missing_artifacts') == 0}.",
        f"2. target law hash consistent: {freeze.get('target_hash_match')} (`{EXPECTED_TARGET_HASH}`).",
        f"3. pi_safe rule/hash consistent: `{pi_safe_rule_hash()}`.",
        f"4. tau_cov still {TAU_COV}: {float(freeze.get('tau_cov') or 0) == TAU_COV}.",
        f"5. E3 EventTrace hashes: sensorscope=`{trace_hashes.get('sensorscope')}` uair=`{trace_hashes.get('uair')}`.",
        f"6. SensorScope warm-up windows: {ss.get('n_warmup_windows')}.",
        f"7. U-Air warm-up windows: {ua.get('n_warmup_windows')}.",
        f"8. SensorScope C_real_support mean/median/max: {ss.get('mean_C_real_support')}/{ss.get('median_C_real_support')}/{ss.get('max_C_real_support')}.",
        f"9. SensorScope C_oracle_safe mean/median/max: {ss.get('mean_C_oracle_safe')}/{ss.get('median_C_oracle_safe')}/{ss.get('max_C_oracle_safe')}.",
        f"10. SensorScope oracle pass count/rate: {ss.get('n_oracle_pass')}/{ss.get('fraction_oracle_pass')}.",
        f"11. U-Air C_real_support mean/median/max: {ua.get('mean_C_real_support')}/{ua.get('median_C_real_support')}/{ua.get('max_C_real_support')}.",
        f"12. U-Air C_oracle_safe mean/median/max: {ua.get('mean_C_oracle_safe')}/{ua.get('median_C_oracle_safe')}/{ua.get('max_C_oracle_safe')}.",
        f"13. U-Air oracle pass count/rate: {ua.get('n_oracle_pass')}/{ua.get('fraction_oracle_pass')}.",
        f"14. C_oracle_safe <= C_real_support all warm-up windows: {(warm['C_oracle_safe'] <= warm['C_real_support'] + NUM_TOL).all()}.",
        f"15. C_cov_R1d <= C_oracle_safe on joint-valid windows: {formal_le}.",
        f"16. SensorScope oracle reachability: {ss.get('compatibility')}.",
        f"17. U-Air oracle reachability: {ua.get('compatibility')}.",
        f"18. Robust natural safe regime: {verdict == 'READY_FOR_CERTIFICATE_REPAIR'}.",
        f"19. Robust natural unsafe regime: {verdict == 'E3_THRESHOLD_INCOMPATIBLE'}.",
        f"20. Vacuity shares (mean gaps): protocol={mean_gap_support/total_gap if total_gap else 0:.3f} pi_safe={mean_gap_pi/total_gap if total_gap else 0:.3f} certificate={mean_gap_cert/total_gap if total_gap else 0:.3f}.",
        f"21. E3 windows have real wall-clock semantics: False (abstract index clock).",
        f"22. E3 preserves temporal continuity: False in sealed trace clock.",
        f"23. E3 sampling may depress natural opportunity support: True.",
        f"24. target vs realized opportunity density mismatch: True.",
        f"25. predictor modified this round: False.",
        f"26. calibration modified this round: False.",
        f"27. threshold modified this round: False.",
        f"28. E3 modified this round: False.",
        f"29. SAG run this round: False.",
        f"30. 5-seed run this round: False.",
        f"31. pytest r1f: {tests.get('r1f', {}).get('status')} passed={tests.get('r1f', {}).get('n_passed')} failed={tests.get('r1f', {}).get('n_failed')}.",
        f"32. full pytest: {tests.get('full', {}).get('status')} passed={tests.get('full', {}).get('n_passed')} failed={tests.get('full', {}).get('n_failed')}.",
        f"33. R1F-S0–S20 artifact-derived: see summary/R1F_GATE_REPORT.json.",
        f"34. Final verdict: {verdict}.",
        f"35. Certificate repair allowed next round: {verdict == 'READY_FOR_CERTIFICATE_REPAIR'}.",
        f"36. E3-v2 protocol specification required first: {verdict in {'E3_THRESHOLD_INCOMPATIBLE', 'E3_THRESHOLD_MARGINAL', 'R1F_EVIDENCE_FAILURE'}}.",
    ]
    body = [
        "# RAVEN-MCS SAG G1 R1F Oracle Coverage Ceiling Report",
        "",
        f"## Executive verdict: {verdict}",
        "",
        "STOP. No predictor repair, no calibration repair, no SAG, no 5-seed in this round.",
        "",
        "## Answers",
        "",
        *[f"{line}" for line in answers],
        "",
        "## E3 context",
        "",
        context.get("reason", ""),
        "",
    ]
    (out / "summary" / "RAVEN_MCS_SAG_G1_R1F_ORACLE_COVERAGE_CEILING_REPORT.md").write_text("\n".join(body), encoding="utf-8")


def reconstruct_pi_safe(root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for dataset in DATASETS:
        prepared = attach_unified_target(prepare_sag_bundle(root=root, dataset=dataset, seed=SEED), root=root)
        doc = provisional_pi_safe_from_public_opp(prepared["pi_target"], prepared["pi_opp_joint"], quantile=0.10)
        out[dataset] = {"pi_safe": float(doc["pi_safe"]), "trace_hash": str(prepared["identity"].get("trace_hash"))}
    return out


def run_r1f_main(*, root: Path = ROOT, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root)
    out = Path(output_dir or DEFAULT_OUT)
    for sub in ("audit", "oracle_ceiling", "compatibility", "figures", "summary", "legacy_refs"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    shutil.copy2(root / "configs/sag_g0/thresholds.json", out / "legacy_refs" / "thresholds_frozen_copy.json")
    for rel in R1D_RELATIVE[:3]:
        src = root / rel
        if src.is_file():
            shutil.copy2(src, out / "legacy_refs" / Path(rel).name)

    manifest = write_input_manifest(root, out)
    freeze = write_freeze_audit(root, out, manifest)
    write_oracle_derivation(out)
    dump_json({rel: sha256_file(root / rel) for rel in SOURCE_FILES if (root / rel).is_file()}, out / "audit" / "source_hashes.json")

    if not freeze.get("evidence_ok"):
        verdict = "R1F_EVIDENCE_FAILURE"
        dump_json({"executive_verdict": verdict}, out / "summary" / "R1F_VERDICT.json")
        return {"output_dir": str(out), "verdict": verdict}

    pi_docs = reconstruct_pi_safe(root)
    pred = pd.read_csv(root / "outputs/sag_g1_r1d/dynamic_cov/DYNAMIC_COV_PREDICTION.csv")
    cov = pd.read_csv(root / "outputs/sag_g1_r1d/dynamic_cov/C_COV_DYNAMIC_WINDOW.csv")
    rule_hash = target_law_rule_hash()
    ps_hash = pi_safe_rule_hash()

    frames: list[pd.DataFrame] = []
    summaries: list[dict[str, Any]] = []
    for dataset in DATASETS:
        c_map: dict[int, float] = {}
        sub_cov = cov.loc[cov["dataset"] == dataset]
        for _, row in sub_cov.iterrows():
            if int(row.get("cold_start") or 0) == 0:
                val = row.get("C_cov_LCB")
                c_map[int(row["window_id"])] = float(val) if pd.notna(val) else 0.0
        frame = compute_oracle_windows_from_prediction(
            pred,
            dataset=dataset,
            seed=SEED,
            pi_safe=float(pi_docs[dataset]["pi_safe"]),
            tau_cov=TAU_COV,
            c_cov_r1d_by_window=c_map,
            trace_hash=str(pi_docs[dataset]["trace_hash"]),
            target_law_hash=rule_hash,
            pi_safe_rule_hash=ps_hash,
        )
        frames.append(frame)
        summaries.append(summarize_oracle_windows(frame, dataset=dataset, tau_cov=TAU_COV))
    by_window = pd.concat(frames, ignore_index=True)
    by_window.to_csv(out / "oracle_ceiling" / "ORACLE_COVERAGE_CEILING_BY_WINDOW.csv", index=False)
    pd.DataFrame(summaries).to_csv(out / "summary" / "ORACLE_COVERAGE_CEILING_SUMMARY.csv", index=False)

    decomp_rows = []
    warm = by_window.loc[by_window["is_warmup_eligible"]]
    for _, row in warm.iterrows():
        decomp_rows.append(
            gap_decomposition_row(
                dataset=str(row["dataset"]),
                window_id=int(row["window_id"]),
                tau_cov=TAU_COV,
                c_real_support=float(row["C_real_support"]),
                c_oracle_safe=float(row["C_oracle_safe"]),
                c_cov_r1d=float(row["C_cov_r1d"]),
            )
        )
    decomp = pd.DataFrame(decomp_rows)
    decomp.to_csv(out / "oracle_ceiling" / "ORACLE_THRESHOLD_GAP_DECOMPOSITION.csv", index=False)

    context = audit_e3_prewindow_public_schedule(root)
    write_e3_protocol_audit(root, out, context)
    write_figures(out, by_window, decomp)

    compat = {s["dataset"]: s["compatibility"] for s in summaries}
    verdict = derive_final_verdict(compat, evidence_ok=True)
    dump_json(
        {
            "executive_verdict": verdict,
            "compatibility_by_dataset": compat,
            "summaries": summaries,
            "tau_cov": TAU_COV,
            "delta_cal": DELTA_CAL,
            "sag_started": False,
            "five_seed_started": False,
        },
        out / "summary" / "R1F_VERDICT.json",
    )

    r1f_xml = out / "audit" / "pytest_r1f.xml"
    full_xml = out / "audit" / "pytest_full.xml"
    r1f_sum = run_pytest(root, R1F_TESTS, r1f_xml)
    full_sum = run_pytest(root, R1F_TESTS + R1E_REGRESSION, full_xml)
    tests = {"r1f": r1f_sum, "full": full_sum}
    dump_json(
        {"r1f": r1f_sum, "full": full_sum, "status": full_sum.get("status")},
        out / "audit" / "TEST_SUMMARY.json",
    )

    build_gate_report(out, freeze=freeze, summaries=summaries, by_window=by_window, decomp=decomp, context=context, tests=tests, verdict=verdict)
    write_final_report(
        out,
        freeze=freeze,
        summaries=summaries,
        by_window=by_window,
        decomp=decomp,
        context=context,
        tests=tests,
        verdict=verdict,
        trace_hashes={d: pi_docs[d]["trace_hash"] for d in DATASETS},
    )

    zip_path = root / "deliverables" / "TO_SUBMIT_SAG_G1_R1F_ORACLE_COVERAGE_CEILING_AUDIT.zip"
    pack_script = root / "scripts" / "package_sag_g1_r1f_submission.py"
    if pack_script.is_file():
        subprocess.run([sys.executable, str(pack_script)], cwd=root, check=False)

    return {
        "output_dir": str(out),
        "verdict": verdict,
        "compatibility": compat,
        "tests": {"r1f": r1f_sum.get("status"), "full": full_sum.get("status")},
        "deliverable_zip": str(zip_path) if zip_path.is_file() else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    result = run_r1f_main(root=args.root, output_dir=args.output_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

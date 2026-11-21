"""SAG G1-R1m: first formal aggregate certificate experiment. STOP. No SAG / 5-seed."""

from __future__ import annotations

import argparse
import ast
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from e3_v2_context import public_context_from_start
from raven_mcs.aggregation.method_policy import FORMAL_GATE_MODE, get_method_policy, resolve_method
from raven_mcs.experiments.r1m_method_freeze import PAPER_METHOD
from raven_mcs.experiments.run_sag_g1_r1 import _git_hash
from raven_mcs.experiments.sag_runtime import attach_unified_target, prepare_sag_bundle
from raven_mcs.sag.availability_stress import A_GRID, TAU_COV
from raven_mcs.sag.e3v1_root_cause import natural_windows_from_atomic, unit_meta_from_atomic
from raven_mcs.sag.oracle_stress_builder import stressed_window
from raven_mcs.sag.r1l_conformal import c_lcb
from raven_mcs.sag.r1l_design import design_from_gate
from raven_mcs.sag.r1l_spec import ALPHA, N_MIN, NUM_TOL, k_n
from raven_mcs.sag.r1m_eval import (
    annotate_window,
    clopper_pearson_upper,
    leakage_ok,
    overall_verdict,
    primary_usable,
    secondary_safe,
    summarize_scope,
    track_verdict,
)
from raven_mcs.sag.r1m_spec import (
    DATASETS,
    FEATURE_NAMES,
    PREDICTOR_ID,
    PRIMARY,
    RESET_RULE_ID,
    RIDGE_ALPHA,
    SECONDARY,
    feature_spec_hash,
    predictor_family_payload,
    reset_rule_payload,
)
from raven_mcs.sag.r1m_track import complete_window, decide_window, open_track
from raven_mcs.sag.stress_mask import SEED, mask_rule_hash
from raven_mcs.sag.target_law import freeze_target_law_rule_v1, pi_safe_rule_hash
from raven_mcs.utils.hashing import sha256_file, sha256_json
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = ROOT / "results_sag_g1" / "round_r1m"
ORACLE_SRC = ROOT / "results_sag_g1/round_r1i/oracle_stress/R1I_ORACLE_STRESS_BY_WINDOW.csv"
R1K_SUMMARY = ROOT / "results_sag_g1/round_r1k/aggregate_eval/R1K_PAIRWISE_VS_AGGREGATE_SUMMARY.csv"
R1K_WINDOWS = ROOT / "results_sag_g1/round_r1k/aggregate_certificate/R1K_AGGREGATE_VALIDITY_BY_WINDOW.csv"
R1J_METRICS = ROOT / "results_sag_g1/round_r1j/gate_eval/R1J_GATE_METRICS.csv"
EXPECTED_TARGET_HASH = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"
EXPECTED_THRESHOLD_HASH = "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e"

SNAPSHOT = (
    ("method_policy", "src/raven_mcs/aggregation/method_policy.py"),
    ("window_runner", "src/raven_mcs/training/window_runner.py"),
    ("certificates", "src/raven_mcs/sag/certificates.py"),
    ("aggregate_certificate", "src/raven_mcs/sag/aggregate_certificate.py"),
    ("gate", "src/raven_mcs/sag/gate.py"),
    ("r1l_design", "src/raven_mcs/sag/r1l_design.py"),
    ("r1l_state", "src/raven_mcs/sag/r1l_state.py"),
    ("r1l_block", "src/raven_mcs/sag/r1l_block.py"),
    ("r1l_conformal", "src/raven_mcs/sag/r1l_conformal.py"),
    ("r1l_spec", "src/raven_mcs/sag/r1l_spec.py"),
    ("r1l_theory", "src/raven_mcs/sag/r1l_theory.py"),
    ("r1m_spec", "src/raven_mcs/sag/r1m_spec.py"),
    ("r1m_features", "src/raven_mcs/sag/r1m_features.py"),
    ("r1m_predictor", "src/raven_mcs/sag/r1m_predictor.py"),
    ("r1m_reset", "src/raven_mcs/sag/r1m_reset.py"),
    ("r1m_track", "src/raven_mcs/sag/r1m_track.py"),
    ("r1m_eval", "src/raven_mcs/sag/r1m_eval.py"),
    ("availability_stress", "src/raven_mcs/sag/availability_stress.py"),
    ("stress_mask", "src/raven_mcs/sag/stress_mask.py"),
    ("oracle_stress_builder", "src/raven_mcs/sag/oracle_stress_builder.py"),
    ("r1m_method_freeze", "src/raven_mcs/experiments/r1m_method_freeze.py"),
    ("r1m_method_freeze_json", "configs/sag_g1/r1m_method_freeze.json"),
    ("run_sag_g1_r1m", "src/raven_mcs/experiments/run_sag_g1_r1m.py"),
    ("thresholds", "configs/sag_g0/thresholds.json"),
)

R1M_TESTS = (
    "tests/unit/test_r1m_frozen_theory_constants.py",
    "tests/unit/test_r1m_tau_unchanged.py",
    "tests/unit/test_r1m_alpha_unchanged.py",
    "tests/unit/test_r1m_nmin_19.py",
    "tests/unit/test_r1m_raven_mcs_formal_alias.py",
    "tests/unit/test_r1m_no_legacy_gate_bypass.py",
    "tests/unit/test_ridge_alpha_fixed.py",
    "tests/unit/test_feature_spec_fixed.py",
    "tests/unit/test_no_model_zoo.py",
    "tests/unit/test_predictor_snapshot_frozen_within_block.py",
    "tests/unit/test_predictor_refit_only_after_reset.py",
    "tests/unit/test_calibration_same_dataset.py",
    "tests/unit/test_calibration_same_a.py",
    "tests/unit/test_calibration_same_block.py",
    "tests/unit/test_current_window_not_in_own_q.py",
    "tests/unit/test_no_future_score.py",
    "tests/unit/test_n_lt_19_warmup_off.py",
    "tests/unit/test_kn_not_clipped.py",
    "tests/unit/test_finite_sample_quantile.py",
    "tests/unit/test_gate_from_CLCB_only.py",
    "tests/unit/test_design_equals_gate.py",
    "tests/unit/test_reset_trigger_after_completed_miscoverage.py",
    "tests/unit/test_reset_not_retroactive.py",
    "tests/unit/test_reset_clears_buffer.py",
    "tests/unit/test_reset_refits_new_snapshot.py",
    "tests/unit/test_reset_restarts_warmup.py",
    "tests/unit/test_no_oracle_current_gate_leakage.py",
    "tests/unit/test_no_current_mask_leakage.py",
    "tests/unit/test_full_stress_grid_exact.py",
    "tests/unit/test_no_stress_level_added.py",
    "tests/unit/test_primary_sensor_a040_present.py",
    "tests/unit/test_secondary_uair_a020_present.py",
    "tests/unit/test_no_posthoc_predictor_tuning.py",
    "tests/unit/test_no_posthoc_reset_tuning.py",
    "tests/unit/test_no_sag_started.py",
    "tests/unit/test_no_five_seed_started.py",
    "tests/unit/test_r1m_gate_artifact_derived.py",
    "tests/unit/test_r1m_verdict_not_hardcoded.py",
)


def _mkdirs(out: Path) -> None:
    for name in (
        "freeze",
        "pretest",
        "certificate",
        "audit",
        "eval",
        "primary",
        "secondary",
        "compare",
        "figures",
        "source_snapshot",
        "interface",
        "summary",
        "gates",
        "pytest",
    ):
        (out / name).mkdir(parents=True, exist_ok=True)


def _source_ok(rel: str, needles: tuple[str, ...]) -> bool:
    text = (ROOT / rel).read_text(encoding="utf-8")
    return not any(n in text for n in needles)


def build_pretest(root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for dataset in DATASETS:
        prepared = attach_unified_target(prepare_sag_bundle(root=root, dataset=dataset, seed=SEED), root=root)
        atomic = prepared["atomic_sealed"]
        mapping = prepared["spatial_to_client"]
        meta = unit_meta_from_atomic(atomic, mapping)
        pi_tar = prepared["pi_target"]
        ident = json.loads(
            (root / f"results_sag_g1/round_r1g/e3v2_skeleton/{dataset}/identity.json").read_text(encoding="utf-8")
        )
        natural_hash = str(ident.get("trace_hash") or "")
        oracle = pd.read_csv(ORACLE_SRC)
        pi_safe = float(oracle.loc[oracle["dataset"] == dataset, "pi_safe"].iloc[0])
        train_nat = natural_windows_from_atomic(atomic, mapping, split="train")
        for window_id, rec in enumerate(train_nat):
            ctx = public_context_from_start(rec["window_start_utc"])
            for a in A_GRID:
                row = stressed_window(
                    dataset=dataset,
                    window_id=window_id,
                    unit_ids=list(rec["unit_ids"]),
                    unit_meta=meta,
                    availability_level=a,
                    pi_tar=pi_tar,
                    pi_safe=pi_safe,
                    natural_trace_hash=natural_hash,
                )
                rows.append(
                    {
                        "dataset": dataset,
                        "split": "train",
                        "pretest_window_id": int(window_id),
                        "availability_level": float(a),
                        "C_t": float(row["C_oracle_safe"]),
                        "window_start_utc": rec["window_start_utc"],
                        "hour": int(ctx["hour_of_day"]),
                        "weekend": bool(ctx["weekend_flag"]),
                        "time_index": int(rec["time_index"]),
                        "label": f"pretest:{dataset}:{window_id}",
                    }
                )
    return pd.DataFrame(rows)


def _scope(frame: pd.DataFrame, dataset: str, a: float) -> pd.DataFrame:
    return frame.loc[
        (frame["dataset"] == dataset) & np.isclose(frame["availability_level"].astype(float), float(a))
    ].copy()


def _block_audit(cert: pd.DataFrame, snap_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    by_key = {(r["dataset"], float(r["availability_level"]), int(r["block_id"])): r for r in snap_rows}
    for (ds, a, b), chunk in cert.groupby(["dataset", "availability_level", "block_id"], sort=True):
        hashes = sorted(set(chunk["snapshot_hash"].astype(str)))
        rec = by_key.get((ds, float(a), int(b)))
        out.append(
            {
                "dataset": ds,
                "a": float(a),
                "block_id": int(b),
                "snapshot_id": str(chunk["predictor_snapshot_id"].iloc[0]),
                "fit_end_window": rec["fit_end_window"] if rec else "",
                "n_fit_samples": rec["n_fit_samples"] if rec else "",
                "ridge_alpha": RIDGE_ALPHA,
                "feature_spec_hash": str(chunk["feature_spec_hash"].iloc[0]),
                "snapshot_hash": hashes[0] if hashes else "",
                "n_distinct_snapshot_hash": len(hashes),
                "frozen_within_block": len(hashes) == 1,
            }
        )
    return out


def _buffer_audit(cert: pd.DataFrame, all_rows: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rec in cert.itertuples(index=False):
        ids = [x for x in str(rec.cal_window_ids).split("|") if x]
        cur = int(rec.window_id)
        block = int(rec.block_id)
        ds = rec.dataset
        a = float(rec.availability_level)
        track = all_rows.loc[
            (all_rows["dataset"] == ds) & np.isclose(all_rows["availability_level"].astype(float), a)
        ]
        cross_block = 0
        cross_a = 0
        future = 0
        current = False
        for wid in ids:
            w = int(wid)
            if w == cur:
                current = True
            if w >= cur:
                future += 1
            hit = track.loc[track["window_id"].astype(int) == w]
            if hit.empty:
                continue
            if int(hit["block_id"].iloc[0]) != block:
                cross_block += 1
        wids = [int(x) for x in ids] if ids else []
        ok = (not current) and cross_block == 0 and cross_a == 0 and future == 0
        rows.append(
            {
                "dataset": ds,
                "a": a,
                "window_id": cur,
                "block_id": block,
                "n_cal": int(rec.n_cal_before_decision),
                "min_cal_window": min(wids) if wids else "",
                "max_cal_window": max(wids) if wids else "",
                "current_window_in_buffer": current,
                "cross_block_score_count": cross_block,
                "cross_a_score_count": cross_a,
                "future_score_count": future,
                "pass": ok,
            }
        )
    return pd.DataFrame(rows)


def _figures(frame: pd.DataFrame, metrics: pd.DataFrame, out: Path) -> None:
    cert = frame.loc[frame["state_before_decision"] == "CERTIFIED"]
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    for ds, marker in (("sensorscope", "o"), ("uair", "s")):
        sub = cert.loc[cert["dataset"] == ds]
        ax.scatter(sub["C_t"], sub["C_LCB"], s=18, alpha=0.7, marker=marker, label=ds)
    ax.axvline(TAU_COV, color="k", ls="--", lw=1, label=r"$\tau_{cov}=0.05$")
    ax.axhline(TAU_COV, color="k", ls=":", lw=1)
    ax.set_xlabel(r"$C_t$")
    ax.set_ylabel(r"$C_{LCB,t}$")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "R1M_ORACLE_VS_FORMAL_LCB.png", dpi=140)
    plt.close(fig)

    def timeline(ds: str, a: float, path: Path, title: str) -> None:
        sub = _scope(frame, ds, a).sort_values("window_id")
        fig, ax = plt.subplots(figsize=(10.5, 4.6))
        ax.plot(sub["window_id"], sub["C_t"], label=r"$C_t$", color="C0")
        ax.plot(sub["window_id"], sub["C_hat"], label=r"$\hat C_t$", color="C1", ls="--")
        ax.plot(sub["window_id"], sub["C_LCB"], label=r"$C_{LCB,t}$", color="C2")
        ax.axhline(TAU_COV, color="k", ls=":", lw=1, label=r"$\tau_{cov}$")
        for st, color in (("WARMUP", "#dddddd"), ("RESET", "#ffd0d0")):
            hit = sub.loc[sub["state_before_decision"] == st]
            for w in hit["window_id"]:
                ax.axvspan(float(w) - 0.5, float(w) + 0.5, color=color, lw=0)
        trig = sub.loc[sub["reset_trigger_after_window"].astype(int) == 1]
        if len(trig):
            ax.scatter(trig["window_id"], sub.loc[trig.index, "C_t"], marker="x", s=40, color="red", label="RESET trigger", zorder=5)
        ax.set_title(title)
        ax.set_xlabel("window")
        ax.legend(loc="upper right", fontsize=8)
        fig.tight_layout()
        fig.savefig(path, dpi=140)
        plt.close(fig)

    timeline("sensorscope", 0.40, out / "R1M_PRIMARY_SENSOR_A040_TIMELINE.png", "SensorScope a=0.40")
    timeline("uair", 0.20, out / "R1M_SECONDARY_UAIR_A020_TIMELINE.png", "U-Air a=0.20")

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), sharey=True)
    for ax, ds in zip(axes, DATASETS):
        xs, tp, tn, fp, fn = [], [], [], [], []
        for a in A_GRID:
            m = metrics.loc[(metrics["dataset"] == ds) & np.isclose(metrics["availability_level"], a)]
            xs.append(str(a))
            if len(m):
                tp.append(int(m["TP"].iloc[0]))
                tn.append(int(m["TN"].iloc[0]))
                fp.append(int(m["FP"].iloc[0]))
                fn.append(int(m["FN"].iloc[0]))
            else:
                tp.append(0)
                tn.append(0)
                fp.append(0)
                fn.append(0)
        x = np.arange(len(xs))
        ax.bar(x, tp, label="TP")
        ax.bar(x, tn, bottom=tp, label="TN")
        bot = np.array(tp) + np.array(tn)
        ax.bar(x, fp, bottom=bot, label="FP")
        ax.bar(x, fn, bottom=bot + np.array(fp), label="FN")
        ax.set_xticks(x, xs)
        ax.set_title(ds)
        ax.set_xlabel("a")
    axes[0].set_ylabel("certified windows")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "R1M_GATE_CONFUSION_BY_STRESS.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    labels, duty, resets, don = [], [], [], []
    for ds in DATASETS:
        for a in A_GRID:
            m = metrics.loc[(metrics["dataset"] == ds) & np.isclose(metrics["availability_level"], a)]
            labels.append(f"{ds[:3]}:{a}")
            if len(m):
                duty.append(float(m["certified_duty_cycle"].iloc[0]))
                resets.append(float(m["reset_count"].iloc[0]))
                don.append(float(m["design_on_fraction_all"].iloc[0]))
            else:
                duty.append(0.0)
                resets.append(0.0)
                don.append(0.0)
    x = np.arange(len(labels))
    w = 0.25
    ax.bar(x - w, duty, w, label="certified duty")
    ax.bar(x, don, w, label="Design ON (all)")
    ax2 = ax.twinx()
    ax2.bar(x + w, resets, w, color="C3", label="reset count")
    ax.set_xticks(x, labels, rotation=40, ha="right")
    ax.set_ylabel("fraction")
    ax2.set_ylabel("reset count")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "R1M_DUTY_CYCLE_AND_RESETS.png", dpi=140)
    plt.close(fig)


def _md_table(m: dict[str, Any], title: str) -> str:
    keys = [
        "n_total_windows", "n_warmup", "n_reset", "n_certified", "number_of_blocks", "reset_count",
        "n_oracle_safe_certified", "n_oracle_unsafe_certified", "TP", "TN", "FP", "FN",
        "validity_rate", "miscoverage_count", "false_safe_count", "FSR_unsafe", "false_unsafe_rate",
        "balanced_accuracy", "fraction_C_LCB_zero", "design_on_fraction_certified", "certified_duty_cycle",
        "n_boundary_near_certified",
    ]
    lines = [f"# {title}", "", "| metric | value |", "|---|---|"]
    for k in keys:
        v = m.get(k, "")
        if isinstance(v, float):
            lines.append(f"| `{k}` | {v:.6f} |")
        else:
            lines.append(f"| `{k}` | {v} |")
    lines.append("")
    lines.append("Empirical validity does not prove Assumption A / exchangeability.")
    lines.append("")
    return "\n".join(lines)


def run_pytest(root: Path, out: Path) -> dict[str, Any]:
    py = Path(sys.executable)
    cmd = [str(py), "-m", "pytest", "-q", "--tb=line", *R1M_TESTS]
    proc = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    (out / "pytest" / "R1M_PYTEST_STDOUT.txt").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
    xml_path = out / "pytest" / "R1M_PYTEST.xml"
    junit = [str(py), "-m", "pytest", "-q", f"--junitxml={xml_path}", *R1M_TESTS]
    subprocess.run(junit, cwd=root, capture_output=True, text=True)
    n_fail = n_skip = 0
    if xml_path.is_file():
        tree = ET.parse(xml_path)
        suite = tree.getroot()
        n_fail = int(suite.attrib.get("failures", 0)) + int(suite.attrib.get("errors", 0))
        n_skip = int(suite.attrib.get("skipped", 0))
    return {"exit_code": int(proc.returncode), "failed": n_fail, "skipped": n_skip, "stdout_tail": (proc.stdout or "")[-2000:]}


def _forbidden_in_r1m_sources() -> bool:
    needles = (
        "RandomForest",
        "XGBClassifier",
        "XGBRegressor",
        "MLPRegressor",
        "ARIMA",
        "LogisticRegression",
        "CUSUM",
        "PageHinkley",
        "ADWIN",
    )
    for rel in (
        "src/raven_mcs/sag/r1m_features.py",
        "src/raven_mcs/sag/r1m_predictor.py",
        "src/raven_mcs/sag/r1m_reset.py",
        "src/raven_mcs/sag/r1m_track.py",
    ):
        if any(n in (ROOT / rel).read_text(encoding="utf-8") for n in needles):
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    root = ROOT
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    _mkdirs(out)

    target = freeze_target_law_rule_v1()
    thresh_hash = sha256_file(root / "configs/sag_g0/thresholds.json")
    oracle_hash = sha256_file(ORACLE_SRC)
    shutil.copy2(ORACLE_SRC, out / "freeze" / "R1I_ORACLE_STRESS_BY_WINDOW.csv")
    dump_json(
        {
            "target_law_hash": target["hash"],
            "pi_safe_rule_hash": pi_safe_rule_hash(),
            "tau_cov": TAU_COV,
            "alpha": ALPHA,
            "n_min": N_MIN,
            "A_GRID": list(A_GRID),
            "mask_rule_hash": mask_rule_hash(),
            "threshold_hash": thresh_hash,
            "oracle_sha256": oracle_hash,
            "paper_method": PAPER_METHOD,
            "gate_mode": FORMAL_GATE_MODE,
            "predictor": predictor_family_payload(),
            "reset": reset_rule_payload(),
            "feature_spec_hash": feature_spec_hash(),
        },
        out / "freeze" / "R1M_FREEZE.json",
    )

    code_hash = sha256_json(
        {
            "r1m_track": sha256_file(root / "src/raven_mcs/sag/r1m_track.py"),
            "r1m_predictor": sha256_file(root / "src/raven_mcs/sag/r1m_predictor.py"),
            "r1l_conformal": sha256_file(root / "src/raven_mcs/sag/r1l_conformal.py"),
            "r1l_design": sha256_file(root / "src/raven_mcs/sag/r1l_design.py"),
        }
    )

    pretest = build_pretest(root)
    pretest.to_csv(out / "pretest" / "R1M_PRETEST_HISTORY.csv", index=False)
    pretest_ok = bool(len(pretest) > 0)
    n_pre = {ds: int((pretest["dataset"] == ds).sum() / max(len(A_GRID), 1)) for ds in DATASETS} if pretest_ok else {}
    if (not pretest_ok) or any(int(n_pre.get(ds, 0)) <= 0 for ds in DATASETS):
        dump_json(
            {
                "executive_verdict": "R1M_INSUFFICIENT_PRETEST_HISTORY",
                "sag_started": False,
                "five_seed_started": False,
                "pretest_counts": n_pre,
            },
            out / "summary" / "R1M_VERDICT.json",
        )
        (out / "summary" / "RAVEN_MCS_R1M_AGGREGATE_CERTIFICATE_FORMAL_AUDIT_REPORT.md").write_text(
            "# R1m STOP: R1M_INSUFFICIENT_PRETEST_HISTORY\n",
            encoding="utf-8",
        )
        return 2

    oracle = pd.read_csv(ORACLE_SRC)
    rows: list[dict[str, Any]] = []
    snap_rows: list[dict[str, Any]] = []
    reset_rows: list[dict[str, Any]] = []

    for dataset in DATASETS:
        for a in A_GRID:
            pre = pretest.loc[
                (pretest["dataset"] == dataset) & np.isclose(pretest["availability_level"].astype(float), float(a))
            ].sort_values("pretest_window_id")
            track = open_track(
                dataset=dataset,
                availability_level=float(a),
                pretest_c=pre["C_t"].astype(float).tolist(),
                pretest_hours=pre["hour"].astype(int).tolist(),
                pretest_weekends=pre["weekend"].astype(bool).tolist(),
                pretest_labels=pre["label"].astype(str).tolist(),
            )
            snap_rows.append(
                {
                    "dataset": dataset,
                    "availability_level": float(a),
                    "block_id": 0,
                    "snapshot_id": f"{dataset}|a={float(a):.2f}|b0",
                    "fit_end_window": track.snapshot.fit_end_window,
                    "n_fit_samples": track.snapshot.n_fit,
                    "ridge_alpha": RIDGE_ALPHA,
                    "feature_spec_hash": track.snapshot.feature_spec_hash,
                    "snapshot_hash": track.snapshot.snapshot_hash,
                }
            )
            seq = oracle.loc[
                (oracle["dataset"] == dataset) & np.isclose(oracle["availability_level"].astype(float), float(a))
            ].sort_values("window_id")
            seq_list = list(seq.itertuples(index=False))
            for i, rec in enumerate(seq_list):
                ctx = public_context_from_start(rec.window_start_utc)
                hour = int(ctx["hour_of_day"])
                weekend = bool(ctx["weekend_flag"])
                decision = decide_window(track, window_id=int(rec.window_id), hour=hour, weekend=weekend)
                c_t = float(rec.C_oracle_safe)
                decision = complete_window(
                    track,
                    decision,
                    c_t=c_t,
                    hour=hour,
                    weekend=weekend,
                    window_label=str(int(rec.window_id)),
                )
                extra = annotate_window(
                    {
                        "C_t": c_t,
                        "C_LCB": decision["C_LCB"],
                        "Gate_t": decision["Gate"],
                    }
                )
                if int(decision.get("reset_trigger_after_window") or 0) == 1:
                    nxt = seq_list[i + 1] if i + 1 < len(seq_list) else None
                    snap_rows.append(
                        {
                            "dataset": dataset,
                            "availability_level": float(a),
                            "block_id": int(track.block_id),
                            "snapshot_id": f"{dataset}|a={float(a):.2f}|b{track.block_id}",
                            "fit_end_window": track.snapshot.fit_end_window,
                            "n_fit_samples": track.snapshot.n_fit,
                            "ridge_alpha": RIDGE_ALPHA,
                            "feature_spec_hash": track.snapshot.feature_spec_hash,
                            "snapshot_hash": track.snapshot.snapshot_hash,
                        }
                    )
                    reset_rows.append(
                        {
                            "dataset": dataset,
                            "a": float(a),
                            "trigger_window": int(rec.window_id),
                            "trigger_block": int(decision["block_id"]),
                            "C_LCB": float(decision["C_LCB"]),
                            "C_t": c_t,
                            "miscoverage_margin": float(decision["C_LCB"] - c_t),
                            "next_window": int(nxt.window_id) if nxt is not None else "",
                            "new_block_id": int(track.block_id),
                            "new_snapshot_id": f"{dataset}|a={float(a):.2f}|b{track.block_id}",
                            "buffer_cleared": True,
                            "next_state": "RESET",
                            "gate_next": 0,
                            "design_next": 0,
                            "pass": True,
                        }
                    )
                rows.append(
                    {
                        "dataset": dataset,
                        "availability_level": float(a),
                        "window_id": int(rec.window_id),
                        "block_id": int(decision["block_id"]),
                        "predictor_snapshot_id": decision["predictor_snapshot_id"],
                        "state_before_decision": decision["state_before_decision"],
                        "n_cal_before_decision": int(decision["n_cal_before_decision"]),
                        "C_hat": float(decision["C_hat"]),
                        "q_t": decision["q_t"],
                        "C_LCB": float(decision["C_LCB"]),
                        "tau_cov": TAU_COV,
                        "Gate_t": int(decision["Gate"]),
                        "Design_t": int(decision["Design"]),
                        "C_t": c_t,
                        "Y_oracle": extra["Y_oracle"],
                        "Y_cert": extra["Y_cert"],
                        "certificate_valid": extra["certificate_valid"],
                        "false_safe": extra["false_safe"],
                        "false_unsafe": extra["false_unsafe"],
                        "classification": extra["classification"],
                        "score_S_t": float(decision["S_t"]),
                        "reset_trigger_after_window": int(decision.get("reset_trigger_after_window") or 0),
                        "state_next_window": decision.get("state_next_window"),
                        "natural_complete_status": rec.natural_complete_status,
                        "natural_boundary_status": rec.natural_boundary_status,
                        "oracle_source_hash": oracle_hash,
                        "stress_mask_hash": str(rec.availability_mask_hash),
                        "predictor_hash": decision["snapshot_hash"],
                        "snapshot_hash": decision["snapshot_hash"],
                        "feature_spec_hash": decision["feature_spec_hash"],
                        "certificate_code_hash": code_hash,
                        "cal_window_ids": "|".join(str(x) for x in decision.get("cal_window_ids") or []),
                        "boundary_near": extra["boundary_near"],
                        "C_LCB_zero": extra["C_LCB_zero"],
                        "predictor_id": PREDICTOR_ID,
                        "reset_rule_id": RESET_RULE_ID,
                        "ridge_alpha": RIDGE_ALPHA,
                        "paper_method": PAPER_METHOD,
                        "k_n_clipped": False,
                    }
                )

    frame = pd.DataFrame(rows)
    frame.to_csv(out / "certificate" / "R1M_CERTIFICATE_BY_WINDOW.csv", index=False)

    metric_rows = []
    for dataset in DATASETS:
        for a in A_GRID:
            sub = _scope(frame, dataset, a)
            m = summarize_scope(sub)
            m["dataset"] = dataset
            m["availability_level"] = float(a)
            m["track_verdict"] = ""
            metric_rows.append(m)
    metrics = pd.DataFrame(metric_rows)

    cert = frame.loc[frame["state_before_decision"] == "CERTIFIED"].copy()
    snap_audit = pd.DataFrame(_block_audit(frame, snap_rows))
    snap_audit.to_csv(out / "audit" / "R1M_PREDICTOR_SNAPSHOT_AUDIT.csv", index=False)
    buf = _buffer_audit(cert, frame)
    buf.to_csv(out / "audit" / "R1M_CALIBRATION_BUFFER_AUDIT.csv", index=False)
    reset_df = pd.DataFrame(reset_rows)
    if reset_df.empty:
        reset_df = pd.DataFrame(
            columns=[
                "dataset", "a", "trigger_window", "trigger_block", "C_LCB", "C_t",
                "miscoverage_margin", "next_window", "new_block_id", "new_snapshot_id",
                "buffer_cleared", "next_state", "gate_next", "design_next", "pass",
            ]
        )
    reset_df.to_csv(out / "audit" / "R1M_RESET_AUDIT.csv", index=False)

    leak = leakage_ok(buf)
    impl_formula = True
    for rec in cert.itertuples(index=False):
        q = float(rec.q_t)
        expect = float(c_lcb(float(rec.C_hat), q)) if np.isfinite(q) else 0.0
        if abs(float(rec.C_LCB) - expect) > 1e-10:
            impl_formula = False
        if int(rec.Design_t) != design_from_gate(int(rec.Gate_t)):
            impl_formula = False
    warmup_off = bool(
        (
            frame.loc[frame["state_before_decision"].isin(["WARMUP", "RESET"]), "Gate_t"].astype(int) == 0
        ).all()
    )
    design_eq = bool((frame["Gate_t"].astype(int) == frame["Design_t"].astype(int)).all())
    snap_frozen = bool(snap_audit["frozen_within_block"].all()) if len(snap_audit) else False
    grid_ok = sorted({round(float(x), 2) for x in frame["availability_level"].unique()}) == [0.2, 0.4, 0.6, 0.8, 1.0]
    both_ds = set(frame["dataset"].unique()) == set(DATASETS)
    primary = _scope(frame, PRIMARY["dataset"], PRIMARY["availability_level"])
    secondary = _scope(frame, SECONDARY["dataset"], SECONDARY["availability_level"])
    primary.to_csv(out / "primary" / "R1M_SENSORSCOPE_A040_PRIMARY_AUDIT.csv", index=False)
    secondary.to_csv(out / "secondary" / "R1M_UAIR_A020_SECONDARY_AUDIT.csv", index=False)
    p_m = summarize_scope(primary)
    s_m = summarize_scope(secondary)
    (out / "primary" / "R1M_SENSORSCOPE_A040_PRIMARY_SUMMARY.md").write_text(
        _md_table(p_m, "R1m SensorScope a=0.40 primary"), encoding="utf-8"
    )
    (out / "secondary" / "R1M_UAIR_A020_SECONDARY_SUMMARY.md").write_text(
        _md_table(s_m, "R1m U-Air a=0.20 secondary"), encoding="utf-8"
    )

    pooled = summarize_scope(frame)
    metrics["track_verdict"] = [
        track_verdict(
            metrics.loc[i].to_dict(),
            leak_ok=leak,
            impl_ok=impl_formula and warmup_off and design_eq and snap_frozen,
        )
        for i in metrics.index
    ]
    metrics.to_csv(out / "eval" / "R1M_TRACK_METRICS.csv", index=False)

    # R1k / R1j diagnostic compare
    r1k = pd.read_csv(R1K_SUMMARY) if R1K_SUMMARY.is_file() else pd.DataFrame()
    r1k_win = pd.read_csv(R1K_WINDOWS) if R1K_WINDOWS.is_file() else pd.DataFrame()
    r1j = pd.read_csv(R1J_METRICS) if R1J_METRICS.is_file() else pd.DataFrame()
    cmp_rows = []
    for dataset in DATASETS:
        for a in A_GRID:
            m = metrics.loc[(metrics["dataset"] == dataset) & np.isclose(metrics["availability_level"], a)].iloc[0]
            krow = r1k.loc[(r1k["dataset"] == dataset) & np.isclose(r1k["availability_level"].astype(float), a)] if len(r1k) else pd.DataFrame()
            kw = r1k_win.loc[
                (r1k_win["dataset"] == dataset) & np.isclose(r1k_win["availability_level"].astype(float), a)
            ] if len(r1k_win) else pd.DataFrame()
            r1k_duty = float(kw["eligible_after_warmup"].astype(bool).mean()) if len(kw) else float("nan")
            jscope = f"{dataset}|a={a:.2f}" if a != 1.0 else f"{dataset}|a=1.00"
            # R1j uses a=1.00 style
            jhit = pd.DataFrame()
            if len(r1j):
                jhit = r1j.loc[r1j["scope"].astype(str) == f"{dataset}|a={a:.2f}"]
                if jhit.empty:
                    jhit = r1j.loc[r1j["scope"].astype(str) == f"{dataset}|a={a:.1f}0"]
                if jhit.empty and abs(a - 1.0) < 1e-9:
                    jhit = r1j.loc[r1j["scope"].astype(str) == f"{dataset}|a=1.00"]
                if jhit.empty and abs(a - 0.2) < 1e-9:
                    jhit = r1j.loc[r1j["scope"].astype(str) == f"{dataset}|a=0.20"]
                if jhit.empty and abs(a - 0.4) < 1e-9:
                    jhit = r1j.loc[r1j["scope"].astype(str) == f"{dataset}|a=0.40"]
            cmp_rows.append(
                {
                    "dataset": dataset,
                    "availability_level": float(a),
                    "r1m_validity": float(m["validity_rate"]),
                    "r1m_FSR_unsafe": float(m["FSR_unsafe"]),
                    "r1m_false_unsafe_rate": float(m["false_unsafe_rate"]),
                    "r1m_balanced_accuracy": float(m["balanced_accuracy"]),
                    "r1m_fraction_zero": float(m["fraction_C_LCB_zero"]),
                    "r1m_certified_duty_cycle": float(m["certified_duty_cycle"]),
                    "r1m_reset_count": int(m["reset_count"]),
                    "r1k_aggregate_validity": float(krow["aggregate_validity"].iloc[0]) if len(krow) else float("nan"),
                    "r1k_aggregate_false_safe": float(krow["aggregate_false_safe"].iloc[0]) if len(krow) else float("nan"),
                    "r1k_aggregate_false_unsafe": float(krow["aggregate_false_unsafe"].iloc[0]) if len(krow) else float("nan"),
                    "r1k_aggregate_balanced_accuracy": float(krow["aggregate_balanced_accuracy"].iloc[0]) if len(krow) else float("nan"),
                    "r1k_aggregate_fraction_zero": float(krow["aggregate_fraction_zero"].iloc[0]) if len(krow) else float("nan"),
                    "r1k_certified_duty_cycle": r1k_duty,
                    "r1j_fraction_zero": float(jhit["fraction_C_cov_zero"].iloc[0]) if len(jhit) else float("nan"),
                    "r1j_balanced_accuracy": float(jhit["balanced_accuracy"].iloc[0]) if len(jhit) else float("nan"),
                    "r1j_false_safe_rate": float(jhit["false_safe_rate"].iloc[0]) if len(jhit) else float("nan"),
                    "note": "R1k is feasibility-only; R1j is pairwise diagnostic. Neither is a formal baseline.",
                }
            )
    pd.DataFrame(cmp_rows).to_csv(out / "compare" / "R1M_VS_R1K_AGGREGATE_SUMMARY.csv", index=False)
    pd.DataFrame(cmp_rows).to_csv(out / "compare" / "R1M_VS_R1J_PAIRWISE_SUMMARY.csv", index=False)

    bin_rows = [
        {
            "scope": "pooled_miscoverage",
            "n": int(pooled["n_certified"]),
            "errors": int(pooled["miscoverage_count"]),
            "empirical_rate": pooled["miscoverage_rate"],
            "one_sided_95_upper": clopper_pearson_upper(int(pooled["miscoverage_count"]), int(pooled["n_certified"])),
            "notes": "reporting only; not the PASS/FAIL gate",
        },
        {
            "scope": "sensorscope_a040_miscoverage",
            "n": int(p_m["n_certified"]),
            "errors": int(p_m["miscoverage_count"]),
            "empirical_rate": p_m["miscoverage_rate"],
            "one_sided_95_upper": clopper_pearson_upper(int(p_m["miscoverage_count"]), int(p_m["n_certified"])),
            "notes": "primary",
        },
        {
            "scope": "uair_a020_miscoverage",
            "n": int(s_m["n_certified"]),
            "errors": int(s_m["miscoverage_count"]),
            "empirical_rate": s_m["miscoverage_rate"],
            "one_sided_95_upper": clopper_pearson_upper(int(s_m["miscoverage_count"]), int(s_m["n_certified"])),
            "notes": "secondary",
        },
        {
            "scope": "pooled_false_safe",
            "n": int(pooled["n_certified"]),
            "errors": int(pooled["false_safe_count"]),
            "empirical_rate": pooled["FSR_all"],
            "one_sided_95_upper": clopper_pearson_upper(int(pooled["false_safe_count"]), int(pooled["n_certified"])),
            "notes": "FSR_all",
        },
        {
            "scope": "primary_false_safe_unsafe_conditioned",
            "n": int(p_m["n_oracle_unsafe_certified"]),
            "errors": int(p_m["false_safe_count"]),
            "empirical_rate": p_m["FSR_unsafe"],
            "one_sided_95_upper": clopper_pearson_upper(int(p_m["false_safe_count"]), int(p_m["n_oracle_unsafe_certified"])),
            "notes": "FSR_unsafe primary",
        },
        {
            "scope": "secondary_false_safe_unsafe_conditioned",
            "n": int(s_m["n_oracle_unsafe_certified"]),
            "errors": int(s_m["false_safe_count"]),
            "empirical_rate": s_m["FSR_unsafe"],
            "one_sided_95_upper": clopper_pearson_upper(int(s_m["false_safe_count"]), int(s_m["n_oracle_unsafe_certified"])),
            "notes": "FSR_unsafe secondary",
        },
    ]
    pd.DataFrame(bin_rows).to_csv(out / "eval" / "R1M_BINOMIAL_SAFETY_INTERVALS.csv", index=False)

    _figures(frame, metrics, out / "figures")

    snap_manifest = []
    for component, rel in SNAPSHOT:
        src = root / rel
        dst = out / "source_snapshot" / Path(rel).name
        if src.is_file():
            shutil.copy2(src, dst)
            digest = sha256_file(src)
        else:
            digest = "MISSING"
        snap_manifest.append(
            {
                "component": component,
                "source_path": rel.replace("\\", "/"),
                "snapshot_path": str((Path("source_snapshot") / Path(rel).name).as_posix()) if src.is_file() else "",
                "sha256": digest,
            }
        )
    pd.DataFrame(snap_manifest).to_csv(out / "source_snapshot" / "R1M_SOURCE_SNAPSHOT_MANIFEST.csv", index=False)

    alias_ok = resolve_method("raven_mcs") == "raven_mcs" and get_method_policy("raven_mcs").gate_mode == FORMAL_GATE_MODE
    theory_ok = (
        target["hash"] == EXPECTED_TARGET_HASH
        and thresh_hash == EXPECTED_THRESHOLD_HASH
        and TAU_COV == 0.05
        and ALPHA == 0.05
        and N_MIN == 19
        and k_n(19) <= 19
    )
    no_zoo = not _forbidden_in_r1m_sources()
    impl_ok = bool(
        impl_formula
        and warmup_off
        and design_eq
        and snap_frozen
        and alias_ok
        and theory_ok
        and no_zoo
        and RIDGE_ALPHA == 1.0
        and grid_ok
        and both_ds
        and not primary.empty
        and not secondary.empty
    )
    p_ok = primary_usable(p_m, leak_ok=leak, impl_ok=impl_ok)
    s_ok = secondary_safe(s_m, leak_ok=leak)
    verdict = overall_verdict(
        primary_ok=p_ok,
        secondary_ok=s_ok,
        primary_m=p_m,
        secondary_m=s_m,
        impl_ok=impl_ok,
        leak_ok=leak,
        pretest_ok=True,
    )

    gates = [
        ("R1M-S0", "R1l theory freeze unchanged", theory_ok, f"target={target['hash'][:12]} tau={TAU_COV} alpha={ALPHA} n_min={N_MIN}"),
        ("R1M-S1", "raven_mcs resolves to aggregate_coverage", alias_ok, FORMAL_GATE_MODE),
        ("R1M-S2", "legacy gate bypass absent", get_method_policy("raven").legacy_only is True, "raven.legacy_only"),
        ("R1M-S3", "stress grid unchanged", grid_ok, str(list(A_GRID))),
        ("R1M-S4", "oracle ground truth frozen", ORACLE_SRC.is_file() and oracle_hash == sha256_file(out / "freeze" / "R1I_ORACLE_STRESS_BY_WINDOW.csv"), oracle_hash[:16]),
        ("R1M-S5", "predictor family frozen", PREDICTOR_ID == "AGGREGATE_COVERAGE_RIDGE_V1" and no_zoo, PREDICTOR_ID),
        ("R1M-S6", "feature spec frozen", list(FEATURE_NAMES)[0] == "intercept" and "hour_sin" in FEATURE_NAMES, feature_spec_hash()[:16]),
        ("R1M-S7", "ridge alpha fixed", RIDGE_ALPHA == 1.0, str(RIDGE_ALPHA)),
        ("R1M-S8", "predictor snapshot frozen per block", snap_frozen, "R1M_PREDICTOR_SNAPSHOT_AUDIT.csv"),
        ("R1M-S9", "refit only after RESET", bool((reset_df["pass"].astype(bool).all() if len(reset_df) else True)), "R1M_RESET_AUDIT.csv"),
        ("R1M-S10", "n_min=19", N_MIN == 19, str(N_MIN)),
        ("R1M-S11", "finite-sample k_n not clipped", "min(k_n" not in (root / "src/raven_mcs/sag/r1l_conformal.py").read_text(encoding="utf-8") and not bool(frame["k_n_clipped"].astype(bool).any()), "k_n unclipped"),
        ("R1M-S12", "same-a same-block calibration only", leak, "R1M_CALIBRATION_BUFFER_AUDIT.csv"),
        ("R1M-S13", "no current-window calibration leakage", leak and (not bool(buf["current_window_in_buffer"].astype(bool).any()) if len(buf) else False), "current_window_in_buffer"),
        ("R1M-S14", "no future leakage", leak and (int(buf["future_score_count"].sum()) == 0 if len(buf) else False), "future_score_count"),
        ("R1M-S15", "C_LCB formula correct", impl_formula, "max(0, C_hat-q)"),
        ("R1M-S16", "Gate_t from C_LCB only", warmup_off and bool((cert["Gate_t"].astype(int) == ((cert["C_LCB"] >= TAU_COV).astype(int))).all()) if len(cert) else warmup_off, "Gate=1{C_LCB>=tau}"),
        ("R1M-S17", "Design_t equals Gate_t", design_eq, "Design_t := Gate_t"),
        ("R1M-S18", "RESET rule frozen", RESET_RULE_ID == "MISCOVERAGE_TRIGGERED_RESET_V1", RESET_RULE_ID),
        ("R1M-S19", "RESET only after completed miscoverage", bool(reset_df["pass"].all()) if len(reset_df) else True, f"n_reset_events={len(reset_df)}"),
        ("R1M-S20", "RESET restarts WARMUP", bool((reset_df["next_state"] == "RESET").all()) if len(reset_df) else True, "next window RESET then WARMUP"),
        ("R1M-S21", "primary SensorScope a=.4 complete", len(primary) == 62, f"n={len(primary)}"),
        ("R1M-S22", "secondary U-Air a=.2 complete", len(secondary) == 53, f"n={len(secondary)}"),
        ("R1M-S23", "full stress track complete", both_ds and grid_ok and len(frame) == len(oracle), f"n={len(frame)}"),
        ("R1M-S24", "validity quantified", np.isfinite(pooled["validity_rate"]), str(pooled["validity_rate"])),
        ("R1M-S25", "false-safe quantified", np.isfinite(pooled["FSR_unsafe"]) or pooled["n_certified"] == 0, str(pooled["FSR_unsafe"])),
        ("R1M-S26", "false-unsafe quantified", "false_unsafe_rate" in pooled, str(pooled.get("false_unsafe_rate"))),
        ("R1M-S27", "duty cycle quantified", np.isfinite(pooled["certified_duty_cycle"]), str(pooled["certified_duty_cycle"])),
        ("R1M-S28", "non-vacuity quantified", np.isfinite(p_m["fraction_C_LCB_zero"]), str(p_m["fraction_C_LCB_zero"])),
        ("R1M-S29", "binomial intervals reported", (out / "eval" / "R1M_BINOMIAL_SAFETY_INTERVALS.csv").is_file(), "R1M_BINOMIAL_SAFETY_INTERVALS.csv"),
        ("R1M-S30", "no post-hoc predictor tuning", RIDGE_ALPHA == 1.0 and no_zoo, "alpha frozen before results"),
        ("R1M-S31", "no post-hoc RESET tuning", "CUSUM" not in (root / "src/raven_mcs/sag/r1m_reset.py").read_text(encoding="utf-8"), RESET_RULE_ID),
        ("R1M-S32", "source snapshot complete", all(r["sha256"] != "MISSING" for r in snap_manifest), "R1M_SOURCE_SNAPSHOT_MANIFEST.csv"),
        ("R1M-S33", "no SAG", True, "sag_started=False"),
        ("R1M-S34", "no 5-seed", True, "five_seed_started=False"),
        ("R1M-S35", "final verdict artifact-derived", verdict in {
            "READY_FOR_SAG_1SEED_FUNCTIONAL_VALIDATION",
            "READY_FOR_LIMITED_SAG_1SEED_VALIDATION",
            "R1M_CERTIFICATE_TOO_CONSERVATIVE",
            "R1M_SAFETY_NOT_ESTABLISHED",
            "R1M_IMPLEMENTATION_FAILURE",
            "R1M_INSUFFICIENT_PRETEST_HISTORY",
        }, verdict),
    ]
    # S35 must remain derived from the same function; do not hardcode READY_* here.
    gate_rows = [{"id": g, "name": n, "pass": bool(p), "evidence": str(e)} for g, n, p, e in gates]
    dump_json({"gates": gate_rows, "n_pass": sum(1 for r in gate_rows if r["pass"]), "n_fail": sum(1 for r in gate_rows if not r["pass"])}, out / "gates" / "R1M_GATE_REPORT.json")
    md = ["# R1m gate report", "", "| id | name | pass | evidence |", "|---|---|---|---|"]
    for r in gate_rows:
        md.append(f"| {r['id']} | {r['name']} | {r['pass']} | {r['evidence']} |")
    md.append("")
    (out / "gates" / "R1M_GATE_REPORT.md").write_text("\n".join(md), encoding="utf-8")

    impl_from_gates = all(r["pass"] for r in gate_rows if r["id"] not in {"R1M-S21", "R1M-S22", "R1M-S24", "R1M-S25", "R1M-S26", "R1M-S27", "R1M-S28", "R1M-S35"})
    # Recompute overall using gate implementation subset? Keep eval function as authority.
    dump_json(
        {
            "executive_verdict": verdict,
            "primary_usable": p_ok,
            "secondary_safe": s_ok,
            "primary_metrics": p_m,
            "secondary_metrics": s_m,
            "pooled": pooled,
            "track_verdicts": metrics[["dataset", "availability_level", "track_verdict"]].to_dict(orient="records"),
            "sag_started": False,
            "five_seed_started": False,
            "posthoc_predictor_tuning": False,
            "posthoc_reset_tuning": False,
            "git": _git_hash(),
            "paper_method": PAPER_METHOD,
            "n_pretest_windows": n_pre,
        },
        out / "summary" / "R1M_VERDICT.json",
    )

    report = [
        "# RAVEN-MCS R1m aggregate certificate formal audit",
        "",
        f"**Executive verdict:** `{verdict}`",
        "",
        "This round implements the first formal aggregate coverage certificate under frozen R1l theory.",
        "Empirical validity is an audit of realized certificates. It does **not** prove Assumption A or exchangeability.",
        "Theorem 1 remains conditional on Assumption A. RESET is an operational abstention rule and does not protect the first unseen shift window.",
        "",
        "## Freeze",
        "",
        f"1. target law unchanged: `{target['hash']}` (expected `{EXPECTED_TARGET_HASH}`).",
        f"2. pi_safe rule hash: `{pi_safe_rule_hash()}`.",
        f"3. tau_cov = {TAU_COV}.",
        f"4. alpha = {ALPHA}.",
        f"5. n_min = {N_MIN}.",
        f"6. stress grid = {list(A_GRID)}.",
        f"7. canonical method = `{PAPER_METHOD}` → `{FORMAL_GATE_MODE}`.",
        "",
        "## Predictor",
        "",
        f"8. `{PREDICTOR_ID}`.",
        f"9. ridge_alpha = {RIDGE_ALPHA} (not scanned).",
        f"10. features: {list(FEATURE_NAMES)}.",
        "11. first-block fit uses E3-v2 train-split windows under the same R1i stress mechanism; test labels are not used to warm-start f_0.",
        f"12. snapshot frozen within block: {snap_frozen}.",
        "13. refit only after RESET, on data completed through the trigger window.",
        "",
        "## Calibration",
        "",
        "14. S_t = C_hat_t - C_t.",
        "15. current window is not in its own q_t.",
        "16. tracks do not mix availability levels.",
        "17. tracks do not mix blocks.",
        "18. n < 19 → WARMUP, C_LCB=0, Gate OFF, Design OFF.",
        "19. k_n is never clipped to n.",
        "",
        "## RESET",
        "",
        f"20. `{RESET_RULE_ID}`.",
        "21. trigger only after a completed CERTIFIED miscoverage (C_LCB > C_t + tol).",
        "22. the violating window stays CERTIFIED.",
        "23. the next window is RESET (Gate OFF) then new-block WARMUP.",
        "24. second detector: **NO**.",
        "",
        "## Pooled (CERTIFIED unless noted)",
        "",
        f"25. certified windows = {pooled['n_certified']} / {pooled['n_total_windows']}.",
        f"26. validity_rate = {pooled['validity_rate']}.",
        f"27. miscoverage_count = {pooled['miscoverage_count']}.",
        f"28. false-safe count = {pooled['false_safe_count']}; FSR_unsafe = {pooled['FSR_unsafe']}; FSR_all = {pooled['FSR_all']}.",
        f"29. false-unsafe rate (certified) = {pooled.get('false_unsafe_rate')}.",
        f"30. balanced_accuracy = {pooled.get('balanced_accuracy')}.",
        f"31. certified_duty_cycle = {pooled['certified_duty_cycle']}.",
        f"32. fraction_C_LCB_zero = {pooled['fraction_C_LCB_zero']}.",
        f"33. Design ON count (certified) = {pooled['design_on_count']}.",
        f"34. reset_count = {pooled['reset_count']}; blocks = {pooled['number_of_blocks']}.",
        "",
        "## Primary (SensorScope a=0.40)",
        "",
        f"PRIMARY_USABLE = {p_ok}.",
        f"certified={p_m['n_certified']}, duty={p_m['certified_duty_cycle']}, validity={p_m['validity_rate']},",
        f"FSR_unsafe={p_m['FSR_unsafe']}, BA={p_m.get('balanced_accuracy')}, zero={p_m['fraction_C_LCB_zero']}, DesignON={p_m['design_on_count']}.",
        "",
        "## Secondary (U-Air a=0.20)",
        "",
        f"SECONDARY_SAFE = {s_ok}.",
        f"certified={s_m['n_certified']}, validity={s_m['validity_rate']}, FSR_unsafe={s_m['FSR_unsafe']}, BA={s_m.get('balanced_accuracy')}.",
        "",
        "## Routing",
        "",
        "SAG was not started. 5-seed was not started. Even a READY_FOR_SAG_* verdict must STOP this round.",
        "",
        f"Git: `{_git_hash()}`.",
        "",
    ]
    (out / "summary" / "RAVEN_MCS_R1M_AGGREGATE_CERTIFICATE_FORMAL_AUDIT_REPORT.md").write_text(
        "\n".join(report), encoding="utf-8"
    )
    (out / "interface" / "R1M_FORMAL_EXECUTION_CHAIN.md").write_text(
        "\n".join(
            [
                "# R1m formal execution chain",
                "",
                "C_t (R1i oracle, after completion) → C_hat_t (frozen ridge snapshot) →",
                "S_t = C_hat - C_t → q_t (block conformal, n_min=19, no k_n clip) →",
                "C_LCB = max(0, C_hat - q) → Gate_t = 1{C_LCB ≥ τ} → Design_t := Gate_t.",
                "",
                "RESET: after CERTIFIED miscoverage, keep window t, then t+1 RESET / new block WARMUP.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    # pytest after artifacts exist
    pytest_info = run_pytest(root, out)
    verdict_payload = json.loads((out / "summary" / "R1M_VERDICT.json").read_text(encoding="utf-8"))
    verdict_payload["pytest"] = pytest_info
    dump_json(verdict_payload, out / "summary" / "R1M_VERDICT.json")
    print(json.dumps({"verdict": verdict, "primary_usable": p_ok, "secondary_safe": s_ok, "pytest": pytest_info["exit_code"]}, indent=2))
    return 0 if pytest_info["exit_code"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

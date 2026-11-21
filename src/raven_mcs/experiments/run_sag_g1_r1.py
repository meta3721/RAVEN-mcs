"""SAG G1-R1 1-seed certificate repair diagnostic. Does not start 5-seed."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e3.delta_cs_rho.delta_cs_v6 import accumulate_delta_cs_v6
from raven_mcs.e3.real_runner.runner import _mu_weights_for_test, _predict
from raven_mcs.experiments.run_sag_g0 import _flatten_log, _load_thresholds
from raven_mcs.experiments.run_sag_g1 import _cover, _require_g0_full_pass, _worst_group_rmse
from raven_mcs.experiments.sag_runtime import METHODS, prepare_sag_bundle
from raven_mcs.metrics.accuracy import mae_mu, rmse_mu
from raven_mcs.metrics.distribution import delta_group
from raven_mcs.sag.certificates import (
    FrozenSagThresholds,
    provisional_pi_safe_from_public_opp,
)
from raven_mcs.sag.counterfactual_audit import metrics_from_raw_states
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
R1_DATASETS = ("sensorscope", "uair")
R1_SEEDS = (30001,)
LOCAL_STEPS = 2
EPS = 1e-12


def _git_hash() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
        ).strip()
    except Exception:
        return "UNKNOWN"


def _pct(arr: list[float], q: float) -> float:
    xs = [float(x) for x in arr if x is not None and np.isfinite(float(x))]
    if not xs:
        return float("nan")
    return float(np.quantile(np.asarray(xs, dtype=np.float64), q))


def _summarize(arr: list[float]) -> dict[str, float]:
    xs = [float(x) for x in arr if x is not None and np.isfinite(float(x))]
    if not xs:
        return {"n": 0, "mean": float("nan"), "median": float("nan"), "p90": float("nan"), "p95": float("nan"), "max": float("nan")}
    a = np.asarray(xs, dtype=np.float64)
    return {
        "n": int(a.size),
        "mean": float(a.mean()),
        "median": float(np.median(a)),
        "p90": float(np.quantile(a, 0.90)),
        "p95": float(np.quantile(a, 0.95)),
        "max": float(a.max()),
    }


def _run_one(*, prepared: dict[str, Any], method: str, thresholds: FrozenSagThresholds, pi_safe: float):
    from raven_mcs.aggregation.method_policy import get_method_policy
    from raven_mcs.training.window_runner import build_full_runner

    policy = get_method_policy(method)
    runner = build_full_runner(
        prepared["trace"],
        prepared["dataset"],
        method=method,
        n_groups=int(prepared["n_groups"]),
        model_seed=int(prepared["trace"].metadata.seed),
        local_steps=LOCAL_STEPS,
        target_mu=prepared["target_mu"],
        pi_target=prepared["pi_target"],
        s_max=int(prepared["trace"].metadata.s_max),
        device="cpu",
        use_coarse_time_groups=False,
        pi_opp_joint=prepared["pi_opp_joint"],
    )
    runner.sag_thresholds = FrozenSagThresholds(
        **{**thresholds.as_dict(), "n_groups": int(prepared["n_groups"])}
    )
    runner.sag_pi_safe = float(pi_safe)
    window_metrics = runner.run()
    return runner, list(runner.sag_window_logs), window_metrics


def _diag(row: dict[str, Any]) -> dict[str, Any]:
    d = row.get("certificate_diagnostics")
    if isinstance(d, dict):
        return d
    return {}


def run_r1_main(*, root: Path = ROOT, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root)
    g0 = _require_g0_full_pass(root)
    out = Path(output_dir or (root / "outputs" / "sag_g1_r1"))
    for sub in ("audit", "coverage", "safety_bound", "diagnostic", "configs", "tests"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    thresholds = _load_thresholds()
    shutil.copy2(root / "configs/sag_g0/thresholds.json", out / "configs" / "thresholds_frozen_copy.json")

    gate_rows: list[dict[str, Any]] = []
    method_rows: list[dict[str, Any]] = []
    cov_repair_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    btot_rows: list[dict[str, Any]] = []
    bm_rows: list[dict[str, Any]] = []
    tightness_rows: list[dict[str, Any]] = []
    recompute_rows: list[dict[str, Any]] = []
    raw_lines: list[str] = []
    pi_safe_docs: dict[str, Any] = {}
    unit_payload = {"synthetic_cases": "see tests/unit/test_counterfactual_metrics_independent.py"}

    for dataset in R1_DATASETS:
        for seed in R1_SEEDS:
            prepared = prepare_sag_bundle(root=root, dataset=dataset, seed=int(seed))
            pi_doc = provisional_pi_safe_from_public_opp(
                prepared["pi_target"], prepared["pi_opp_joint"], quantile=0.10,
            )
            pi_safe_docs[dataset] = pi_doc
            pi_safe = float(pi_doc["pi_safe"])
            sag_logs = None
            sag_runner = None
            for method in METHODS:
                runner, logs, window_metrics = _run_one(
                    prepared=prepared, method=method, thresholds=thresholds, pi_safe=pi_safe,
                )
                pred = _predict(runner, prepared["dataset"], split="test")
                mu_w = _mu_weights_for_test(pred, np.asarray(prepared["target_mu"]))
                rmse = float(rmse_mu(pred["y_pred"], pred["y_true"], mu_w)) if len(mu_w) else float("nan")
                mae = float(mae_mu(pred["y_pred"], pred["y_true"], mu_w)) if len(mu_w) else float("nan")
                worst = _worst_group_rmse(pred, mu_w)
                try:
                    d_g = float(delta_group(runner.omega_bar(), np.asarray(prepared["target_mu"])))
                except Exception:
                    d_g = float("nan")
                _, pair_summary = accumulate_delta_cs_v6(
                    window_metrics=window_metrics,
                    diagnostics=list(runner.diagnostics),
                    atomic=prepared["atomic_sealed"],
                    spatial_to_client=prepared["spatial_to_client"],
                    dataset=dataset,
                    seed=int(seed),
                    scenario="complete_aligned",
                    method=method,
                    eventtrace_hash=str(prepared["identity"].get("trace_hash")),
                    stratum_map_hash=None,
                    target_mass_hash=prepared["target_artifact_sha256"],
                    method_source_hash=None,
                )
                on = [r for r in logs if int(r.get("G_r", 0)) == 1]
                off = [r for r in logs if int(r.get("G_r", 0)) == 0]
                method_rows.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "method": method,
                    "RMSE_mu": rmse,
                    "MAE_mu": mae,
                    "WorstGroupRMSE": worst,
                    "Delta_group": d_g,
                    "Delta_cs": pair_summary.get("Delta_c_s"),
                    "Gate_ON_rate": (len(on) / len(logs)) if logs else 0.0,
                    "n_windows": len(logs),
                    "n_ON": len(on),
                    "n_OFF": len(off),
                })
                for row in logs:
                    flat = _flatten_log(row, dataset=dataset, seed=int(seed), method=method)
                    diag = _diag(row)
                    feat = row.get("gate_features") or {}
                    flat.update({
                        "C_cov_LCB": feat.get("C_cov_LCB"),
                        "C_ret_LCB": feat.get("C_ret_LCB"),
                        "C_ESS_LCB": feat.get("C_ESS_LCB"),
                        "C_clip_UCB": feat.get("C_clip_UCB"),
                        "delta_A_UCB": feat.get("delta_A_UCB"),
                        "B_tot_UCB": feat.get("B_tot_UCB"),
                        "old_realized_C_cov": row.get("old_realized_C_cov", row.get("realized_C_cov")),
                        "B_M_cf": row.get("B_M_cf"),
                        "service_diff_l1": row.get("service_diff_l1", row.get("service_diff")),
                        "service_diff_l2": row.get("service_diff_l2"),
                    })
                    for key in (
                        "B_M_pre", "B_Q", "Delta_beta_UCB", "Delta_M_UCB", "Delta_V_UCB",
                        "term_beta", "term_M", "term_V", "D_alpha_UCB",
                        "service_direct_M_term", "service_alpha_term", "B_srv_UCB",
                        "active_set_term", "cal_failure_term", "target_mass_certified",
                        "number_target_positive_pairs", "pi_safe", "B_M_bound_rule",
                    ):
                        if key in diag:
                            flat[key] = diag[key]
                    gate_rows.append(flat)
                if method == "raven_sag":
                    sag_logs = logs
                    sag_runner = runner

            assert sag_logs is not None and sag_runner is not None
            for raw in sag_runner.sag_raw_states:
                rec = {"dataset": dataset, "seed": int(seed), **raw}
                raw_lines.append(json.dumps(rec, ensure_ascii=False))
                try:
                    mets = metrics_from_raw_states(
                        beta_d=np.asarray(raw["beta_D"]),
                        beta_0=np.asarray(raw["beta_0"]),
                        m_d=np.asarray(raw["M_D"]),
                        m_0=np.asarray(raw["M_0"]),
                        v_d=np.diag(np.asarray(raw["V_D_diag"])),
                        v_0=np.diag(np.asarray(raw["V_0_diag"])),
                        alpha_d=np.asarray(raw["alpha_D"]),
                        alpha_0=np.asarray(raw["alpha_0"]),
                    )
                except Exception as exc:
                    mets = {"error": str(exc)}
                logged = next(
                    (r for r in sag_logs if int(r.get("window_id")) == int(raw["window_id"])),
                    {},
                )
                recompute_rows.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "window_id": raw.get("window_id"),
                    "A_D_size": logged.get("A_D_size"),
                    "A_0_size": logged.get("A_0_size"),
                    "Delta_beta_logged": logged.get("Delta_beta"),
                    "Delta_beta_recomputed": mets.get("Delta_beta"),
                    "Delta_M_logged": logged.get("Delta_M"),
                    "Delta_M_recomputed": mets.get("Delta_M"),
                    "Delta_V_logged": logged.get("Delta_V"),
                    "Delta_V_recomputed": mets.get("Delta_V"),
                    "service_diff_logged": logged.get("service_diff"),
                    "service_diff_l1_recomputed": mets.get("service_diff_l1"),
                    "service_diff_l2_recomputed": mets.get("service_diff_l2"),
                })

            for row in sag_logs:
                feat = row.get("gate_features") or {}
                diag = _diag(row)
                cov_repair_rows.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "window_id": row.get("window_id"),
                    "G_r": row.get("G_r"),
                    "fallback_reason": row.get("fallback_reason"),
                    "pi_safe": diag.get("pi_safe", pi_safe),
                    "number_target_positive_pairs": diag.get("number_target_positive_pairs"),
                    "target_mass_certified": diag.get("target_mass_certified"),
                    "C_cov_LCB": feat.get("C_cov_LCB"),
                    "old_realized_C_cov": row.get("old_realized_C_cov", row.get("realized_C_cov")),
                    "cold_start": feat.get("cold_start"),
                })
                for fail in (diag.get("top_failures") or [])[:3]:
                    pair_rows.append({
                        "dataset": dataset,
                        "seed": int(seed),
                        "window_id": row.get("window_id"),
                        "client": fail.get("client"),
                        "stratum": fail.get("stratum"),
                        "pi_tar": fail.get("pi_tar"),
                        "pi_hat_opp": fail.get("pi_hat_opp"),
                        "lower_pi_opp": fail.get("lower_pi_opp"),
                    })
                btot_rows.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "window_id": row.get("window_id"),
                    "B_M_pre": diag.get("B_M_pre"),
                    "B_Q": diag.get("B_Q"),
                    "Delta_beta_UCB": feat.get("Delta_beta_UCB", diag.get("Delta_beta_UCB")),
                    "Delta_M_UCB": feat.get("Delta_M_UCB", diag.get("Delta_M_UCB")),
                    "Delta_V_UCB": feat.get("Delta_V_UCB", diag.get("Delta_V_UCB")),
                    "term_beta": diag.get("term_beta"),
                    "term_M": diag.get("term_M"),
                    "term_V": diag.get("term_V"),
                    "D_alpha_UCB": diag.get("D_alpha_UCB"),
                    "service_direct_M_term": diag.get("service_direct_M_term"),
                    "service_alpha_term": diag.get("service_alpha_term"),
                    "B_srv_UCB": feat.get("B_srv_UCB", diag.get("B_srv_UCB")),
                    "active_set_term": diag.get("active_set_term"),
                    "cal_failure_term": diag.get("cal_failure_term"),
                    "B_tot_UCB": feat.get("B_tot_UCB"),
                    "B_M_cf": row.get("B_M_cf"),
                    "service_diff_l1": row.get("service_diff_l1", row.get("service_diff")),
                    "cold_start": feat.get("cold_start"),
                })
                b_m_pre = diag.get("B_M_pre")
                b_m_cf = row.get("B_M_cf")
                b_srv = feat.get("B_srv_UCB", diag.get("B_srv_UCB"))
                b_tot = feat.get("B_tot_UCB")
                s_l1 = row.get("service_diff_l1", row.get("service_diff"))
                try:
                    ratio_bm = float(b_m_pre) / max(float(b_m_cf), EPS)
                except (TypeError, ValueError):
                    ratio_bm = float("nan")
                try:
                    ratio_srv = float(b_srv) / max(abs(float(s_l1)), EPS)
                except (TypeError, ValueError):
                    ratio_srv = float("nan")
                try:
                    ratio_tot = float(b_tot) / max(abs(float(s_l1)), EPS)
                except (TypeError, ValueError):
                    ratio_tot = float("nan")
                bm_rows.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "window_id": row.get("window_id"),
                    "B_M_pre": b_m_pre,
                    "B_M_cf": b_m_cf,
                    "ratio_BM": ratio_bm,
                    "ratio_Bsrv": ratio_srv,
                    "ratio_Btot": ratio_tot,
                    "B_M_bound_rule": diag.get("B_M_bound_rule"),
                    "common_nonempty": int(
                        int(row.get("both_empty") or 0) == 0
                        and int(row.get("active_set_mismatch") or 0) == 0
                        and row.get("Delta_beta") is not None
                    ),
                })
                if (
                    int(row.get("both_empty") or 0) == 0
                    and int(row.get("active_set_mismatch") or 0) == 0
                    and row.get("Delta_beta") is not None
                ):
                    for name, actual_key, bound_key in (
                        ("beta", "Delta_beta", "Delta_beta_UCB"),
                        ("M", "Delta_M", "Delta_M_UCB"),
                        ("V", "Delta_V", "Delta_V_UCB"),
                    ):
                        actual = row.get(actual_key)
                        bound = feat.get(bound_key)
                        covered = _cover(actual, bound)
                        try:
                            width = float(bound) - float(actual)
                            ratio = (
                                float(bound) / float(actual)
                                if actual is not None and abs(float(actual)) > EPS
                                else float("nan")
                            )
                            actual_zero = abs(float(actual)) <= EPS
                            ucb_zero = abs(float(bound)) <= EPS
                        except (TypeError, ValueError):
                            width = float("nan")
                            ratio = float("nan")
                            actual_zero = False
                            ucb_zero = False
                        tightness_rows.append({
                            "dataset": dataset,
                            "seed": int(seed),
                            "window_id": row.get("window_id"),
                            "metric": name,
                            "actual": actual,
                            "ucb": bound,
                            "covered": covered,
                            "width": width,
                            "ucb_over_actual": ratio,
                            "actual_zero": int(actual_zero),
                            "ucb_zero": int(ucb_zero),
                        })

    pd.DataFrame(gate_rows).to_csv(out / "diagnostic" / "R1_GATE_WINDOW_LOG.csv", index=False)
    pd.DataFrame(method_rows).to_csv(out / "diagnostic" / "R1_METHOD_DIAGNOSTIC.csv", index=False)
    pd.DataFrame(cov_repair_rows).to_csv(out / "coverage" / "C_COV_REPAIR_WINDOW.csv", index=False)
    pd.DataFrame(pair_rows).to_csv(out / "coverage" / "C_COV_PAIR_DIAGNOSTIC.csv", index=False)
    pd.DataFrame(btot_rows).to_csv(out / "safety_bound" / "B_TOT_DECOMPOSITION.csv", index=False)
    pd.DataFrame(bm_rows).to_csv(out / "safety_bound" / "BM_BOUND_AUDIT.csv", index=False)
    pd.DataFrame(tightness_rows).to_csv(out / "safety_bound" / "CERTIFICATE_TIGHTNESS.csv", index=False)
    pd.DataFrame(recompute_rows).to_csv(out / "audit" / "COUNTERFACTUAL_METRIC_RECOMPUTE.csv", index=False)
    (out / "audit" / "COUNTERFACTUAL_RAW_STATE.jsonl").write_text(
        "\n".join(raw_lines) + ("\n" if raw_lines else ""),
        encoding="utf-8",
    )
    dump_json(unit_payload, out / "audit" / "COUNTERFACTUAL_METRIC_UNIT_TEST.json")
    dump_json(pi_safe_docs, out / "configs" / "pi_safe_provenance.json")

    coverage_rows = []
    for dataset in R1_DATASETS:
        sub = [r for r in tightness_rows if r["dataset"] == dataset]
        rec: dict[str, Any] = {"dataset": dataset, "seed": 30001, "coverage_target": 0.95}
        joint_ok: list[int] = []
        by_win: dict[Any, dict[str, Any]] = {}
        for row in sub:
            by_win.setdefault(row["window_id"], {})[row["metric"]] = row
        for win, mets in by_win.items():
            if set(mets) >= {"beta", "M", "V"}:
                flags = [mets[m].get("covered") for m in ("beta", "M", "V")]
                if all(f is not None for f in flags):
                    joint_ok.append(int(all(float(f) > 0.5 for f in flags)))
        rec["n_common_nonempty"] = len(by_win)
        rec["coverage_joint"] = float(np.mean(joint_ok)) if joint_ok else float("nan")
        for metric in ("beta", "M", "V"):
            rows_m = [r for r in sub if r["metric"] == metric]
            covers = [float(r["covered"]) for r in rows_m if r["covered"] is not None]
            widths = [float(r["width"]) for r in rows_m if np.isfinite(float(r["width"]))]
            ratios = [float(r["ucb_over_actual"]) for r in rows_m if np.isfinite(float(r.get("ucb_over_actual", math.nan)))]
            rec[f"coverage_{metric}"] = float(np.mean(covers)) if covers else float("nan")
            rec[f"mean_width_{metric}"] = float(np.mean(widths)) if widths else float("nan")
            rec[f"median_width_{metric}"] = float(np.median(widths)) if widths else float("nan")
            rec[f"p90_width_{metric}"] = _pct(widths, 0.90)
            rec[f"p95_width_{metric}"] = _pct(widths, 0.95)
            rec[f"mean_ucb_over_actual_{metric}"] = float(np.mean(ratios)) if ratios else float("nan")
            rec[f"exact_zero_rate_{metric}"] = float(np.mean([r["actual_zero"] for r in rows_m])) if rows_m else float("nan")
            rec[f"ucb_zero_rate_{metric}"] = float(np.mean([r["ucb_zero"] for r in rows_m])) if rows_m else float("nan")
        coverage_rows.append(rec)
    pd.DataFrame(coverage_rows).to_csv(out / "diagnostic" / "R1_CERTIFICATE_COVERAGE.csv", index=False)

    config = {
        "mode": "g1_r1_1seed",
        "datasets": list(R1_DATASETS),
        "seeds": list(R1_SEEDS),
        "methods": list(METHODS),
        "local_steps": LOCAL_STEPS,
        "git_commit": _git_hash(),
        "g0_config_hash": g0.get("config", {}).get("config_hash"),
        "threshold_hash": sha256_file(root / "configs/sag_g0/thresholds.json"),
        "tau_unchanged": True,
        "coverage_target": 0.95,
        "pi_safe": pi_safe_docs,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(config, out / "configs" / "config_r1.json")
    verdict = write_r1_repair_report(out)
    return {"output_dir": str(out), "config": config, "verdict": verdict}


def _pass_rate(frame: pd.DataFrame, col: str, pred) -> float:
    if frame.empty:
        return float("nan")
    flags = [pred(v) for v in frame[col].tolist()]
    flags = [f for f in flags if f is not None]
    return float(np.mean(flags)) if flags else float("nan")


def write_r1_repair_report(out: Path) -> dict[str, Any]:
    out = Path(out)
    recon = pd.read_csv(out / "audit" / "COUNTERFACTUAL_METRIC_RECOMPUTE.csv")
    cov = pd.read_csv(out / "coverage" / "C_COV_REPAIR_WINDOW.csv")
    btot = pd.read_csv(out / "safety_bound" / "B_TOT_DECOMPOSITION.csv")
    bm = pd.read_csv(out / "safety_bound" / "BM_BOUND_AUDIT.csv")
    tight = pd.read_csv(out / "safety_bound" / "CERTIFICATE_TIGHTNESS.csv")
    gate = pd.read_csv(out / "diagnostic" / "R1_GATE_WINDOW_LOG.csv")
    cover = pd.read_csv(out / "diagnostic" / "R1_CERTIFICATE_COVERAGE.csv")
    methods = pd.read_csv(out / "diagnostic" / "R1_METHOD_DIAGNOSTIC.csv")
    pi_doc = json.loads((out / "configs" / "pi_safe_provenance.json").read_text(encoding="utf-8"))

    def close(a, b) -> bool:
        try:
            return abs(float(a) - float(b)) <= 1e-8 * (1.0 + abs(float(a)))
        except (TypeError, ValueError):
            return pd.isna(a) and pd.isna(b)

    recon_ok = True
    if not recon.empty:
        for _, row in recon.iterrows():
            for a, b in (
                ("Delta_beta_logged", "Delta_beta_recomputed"),
                ("Delta_M_logged", "Delta_M_recomputed"),
                ("Delta_V_logged", "Delta_V_recomputed"),
                ("service_diff_logged", "service_diff_l1_recomputed"),
            ):
                if not close(row.get(a), row.get(b)):
                    recon_ok = False
                    break

    sag = gate[gate["method"] == "raven_sag"].copy() if "method" in gate.columns else gate
    equal_old = False
    if not sag.empty and "C_cov_LCB" in sag.columns and "old_realized_C_cov" in sag.columns:
        sub = sag.dropna(subset=["C_cov_LCB", "old_realized_C_cov"])
        if not sub.empty:
            diffs = (sub["C_cov_LCB"] - sub["old_realized_C_cov"]).abs()
            equal_old = bool((diffs < 1e-12).mean() > 0.8)

    ss = sag[sag["dataset"] == "sensorscope"] if "dataset" in sag.columns else sag
    ua = sag[sag["dataset"] == "uair"] if "dataset" in sag.columns else sag

    def gate_stats(frame: pd.DataFrame) -> dict[str, Any]:
        warm = frame[frame.get("cold_start").fillna(False) != True] if "cold_start" in frame.columns else frame
        on = frame[frame["G_r"] == 1] if "G_r" in frame.columns else frame.iloc[0:0]
        reasons = frame["fallback_reason"].fillna("ON").value_counts(dropna=False).to_dict() if "fallback_reason" in frame.columns else {}
        def ge(col, t):
            if col not in frame.columns or frame.empty:
                return float("nan")
            xs = pd.to_numeric(frame[col], errors="coerce")
            xs = xs[np.isfinite(xs)]
            return float((xs >= t).mean()) if len(xs) else float("nan")
        def le(col, t):
            if col not in frame.columns or frame.empty:
                return float("nan")
            xs = pd.to_numeric(frame[col], errors="coerce")
            xs = xs[np.isfinite(xs)]
            return float((xs <= t).mean()) if len(xs) else float("nan")
        return {
            "n": int(len(frame)),
            "on": int(len(on)),
            "on_rate": float(len(on) / len(frame)) if len(frame) else 0.0,
            "C_cov": ge("C_cov_LCB", 0.05),
            "C_ret": ge("C_ret_LCB", 0.05),
            "C_ESS": ge("C_ESS_LCB", 1.0),
            "C_clip": le("C_clip_UCB", 0.95),
            "delta_A": le("delta_A_UCB", 0.35),
            "B_tot": le("B_tot_UCB", 4.0),
            "reasons": {str(k): int(v) for k, v in reasons.items()},
            "n_warm": int(len(warm)),
        }

    ss_s = gate_stats(ss)
    ua_s = gate_stats(ua)

    def btot_summary(frame: pd.DataFrame) -> dict[str, Any]:
        cols = [
            "B_M_pre", "B_M_cf", "Delta_beta_UCB", "Delta_M_UCB", "Delta_V_UCB",
            "D_alpha_UCB", "B_srv_UCB", "active_set_term", "cal_failure_term", "B_tot_UCB",
        ]
        out_s: dict[str, Any] = {}
        for col in cols:
            src = frame
            if col == "B_M_cf":
                src = bm[bm["dataset"] == frame["dataset"].iloc[0]] if not frame.empty and "dataset" in frame.columns else bm
            if col not in src.columns:
                continue
            out_s[col] = _summarize(pd.to_numeric(src[col], errors="coerce").tolist())
        return out_s

    ss_btot = btot_summary(btot[btot["dataset"] == "sensorscope"] if "dataset" in btot.columns else btot)
    ua_btot = btot_summary(btot[btot["dataset"] == "uair"] if "dataset" in btot.columns else btot)

    bm_legal = "NO_LEGAL_TIGHTER_BM_BOUND_FOUND"
    if not bm.empty and "B_M_bound_rule" in bm.columns:
        bm_legal = str(bm["B_M_bound_rule"].dropna().iloc[0])

    ss_on = ss_s["on"]
    btot_high = True
    if ss_btot.get("B_tot_UCB", {}).get("median") is not None:
        btot_high = float(ss_btot["B_tot_UCB"].get("median", 99)) > 4.0

    if not recon_ok:
        verdict = "IMPLEMENTATION_BUG_FOUND"
    elif equal_old:
        verdict = "NEEDS_MORE_CERTIFICATE_REPAIR"
    elif ss_on == 0 and btot_high:
        verdict = "STRUCTURAL_CERTIFICATE_TOO_CONSERVATIVE"
    elif ss_on > 0:
        verdict = "READY_FOR_G1_R2_5SEED"
    else:
        verdict = "NEEDS_MORE_CERTIFICATE_REPAIR"

    payload = {
        "executive_verdict": verdict,
        "counterfactual_recompute_matches_log": recon_ok,
        "c_cov_equals_old_realized_coverage": equal_old,
        "sensorscope_gate": ss_s,
        "uair_gate": ua_s,
        "bm_bound_rule": bm_legal,
        "pi_safe": pi_doc,
    }
    dump_json(payload, out / "R1_VERDICT.json")

    def fmt_sum(d: dict[str, Any], key: str) -> str:
        s = d.get(key) or {}
        return (
            f"median={s.get('median', float('nan')):.4g}, "
            f"p95={s.get('p95', float('nan')):.4g}"
        )

    lines = [
        "# 1. Executive Verdict",
        "",
        verdict,
        "",
        "R1 1-seed diagnostic only. Frozen tau_* unchanged. Not a 5-seed result.",
        "",
        "# 2. Counterfactual Metric Audit",
        "",
        "Old G1 logs set `service_diff = Delta_M` (0.5 L1 of the mix vector) and",
        "used lagged S² as V for both modes, so Delta_V was identically 0.",
        "R1 recomputes Δβ=||β^D−β^0||_2, ΔM=||M^D−M^0||_2 (operator),",
        "ΔV=||V^D−V^0||_2 with v_k=S²/max(n_eff,1)+v_floor, and",
        "service_diff_l1=||M^D α^D − M^0 α^0||_1 via P2.",
        "",
        f"Raw-state recompute matches logged metrics: **{recon_ok}**.",
        f"Old G1 certificate tables are void for Δ/service (BUG_CONFIRMED on the previous logger).",
        "See `audit/COUNTERFACTUAL_RAW_STATE.jsonl` and `COUNTERFACTUAL_METRIC_RECOMPUTE.csv`.",
        "",
        "# 3. C_cov Repair",
        "",
        "C_cov_LCB = sum π^tar(k,s) 1{lower_π_opp(k,s) ≥ π_safe}.",
        "lower_π_opp = empirical-Bernstein LCB on completed-window opportunity masses (F_{r-} only).",
        f"π_safe provenance: `{pi_doc}`.",
        f"C_cov still equal to old realized-R coverage in ≥80% windows: **{equal_old}**.",
        "",
        "# 4. B_tot Decomposition",
        "",
        f"B_M_pre rule: `{bm_legal}` (sqrt of pre-window EventTrace client roster).",
        "B_M_cf is post-window oracle only and is not a Gate input.",
        "",
        "## SensorScope",
        f"- B_M_pre: {fmt_sum(ss_btot, 'B_M_pre')}",
        f"- B_M_cf: {fmt_sum(ss_btot, 'B_M_cf')}",
        f"- Δ UCBs β/M/V: {fmt_sum(ss_btot, 'Delta_beta_UCB')} / {fmt_sum(ss_btot, 'Delta_M_UCB')} / {fmt_sum(ss_btot, 'Delta_V_UCB')}",
        f"- D_alpha: {fmt_sum(ss_btot, 'D_alpha_UCB')}",
        f"- B_srv: {fmt_sum(ss_btot, 'B_srv_UCB')}",
        f"- 2 δ_A: {fmt_sum(ss_btot, 'active_set_term')}",
        f"- 2 δ_cal: {fmt_sum(ss_btot, 'cal_failure_term')}",
        f"- B_tot: {fmt_sum(ss_btot, 'B_tot_UCB')}",
        "",
        "## U-Air",
        f"- B_M_pre: {fmt_sum(ua_btot, 'B_M_pre')}",
        f"- B_M_cf: {fmt_sum(ua_btot, 'B_M_cf')}",
        f"- Δ UCBs β/M/V: {fmt_sum(ua_btot, 'Delta_beta_UCB')} / {fmt_sum(ua_btot, 'Delta_M_UCB')} / {fmt_sum(ua_btot, 'Delta_V_UCB')}",
        f"- D_alpha: {fmt_sum(ua_btot, 'D_alpha_UCB')}",
        f"- B_srv: {fmt_sum(ua_btot, 'B_srv_UCB')}",
        f"- 2 δ_A: {fmt_sum(ua_btot, 'active_set_term')}",
        f"- 2 δ_cal: {fmt_sum(ua_btot, 'cal_failure_term')}",
        f"- B_tot: {fmt_sum(ua_btot, 'B_tot_UCB')}",
        "",
        "# 5. Certificate Coverage",
        "",
        "Formal target = 0.95. Domain = common nonempty A^D=A^0 only.",
        cover.to_string(index=False),
        "",
        "# 6. One-Seed Gate Diagnostic",
        "",
        "## SensorScope seed 30001",
        json.dumps(ss_s, indent=2),
        "",
        "## U-Air seed 30001",
        json.dumps(ua_s, indent=2),
        "",
        "# 7. Scientific Interpretation",
        "",
        f"SensorScope legal ON windows: {ss_s['on']} / {ss_s['n']}.",
        f"U-Air legal ON windows: {ua_s['on']} / {ua_s['n']}.",
        f"U-Air delta_A pass rate (≤0.35): {ua_s['delta_A']}.",
        "",
        "# 8. Next Decision",
        "",
    ]
    if verdict == "READY_FOR_G1_R2_5SEED":
        lines.append("May enter 5-seed G1-R2. This run did **not** start 5-seed.")
    elif verdict == "STRUCTURAL_CERTIFICATE_TOO_CONSERVATIVE":
        lines.append("Main blocker: legal B_tot remains far above tau_safe=4 after correct C_cov/metrics.")
        lines.append("Do not start 5-seed. Needs theory/method judgment, not tau hacking.")
    elif verdict == "IMPLEMENTATION_BUG_FOUND":
        lines.append("Main blocker: logged vs recomputed metrics still disagree.")
    else:
        lines.append("Main blocker: certificate semantics or calibration still not diagnostic-ready.")
    lines.append("")
    lines.append("Method ranking (not the R1 objective):")
    lines.append(methods.to_string(index=False))
    (out / "R1_REPAIR_REPORT.md").write_text("\n".join(str(x) for x in lines) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    run_r1_main(root=args.root, output_dir=args.output_dir)


if __name__ == "__main__":
    main()

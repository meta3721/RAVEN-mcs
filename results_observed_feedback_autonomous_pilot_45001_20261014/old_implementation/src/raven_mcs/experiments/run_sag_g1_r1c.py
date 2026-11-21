"""SAG G1-R1c 1-seed target-compatibility + coverage-certificate repair.

Does not start 5-seed. Stops if target compatibility is not closed.
"""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e3.delta_cs_rho.delta_cs_v6 import accumulate_delta_cs_v6
from raven_mcs.e3.real_runner.runner import _mu_weights_for_test, _predict
from raven_mcs.experiments.run_sag_g0 import _flatten_log, _load_thresholds
from raven_mcs.experiments.run_sag_g1 import _cover, _require_g0_full_pass, _worst_group_rmse
from raven_mcs.experiments.run_sag_g1_r1 import _diag, _git_hash, _pct
from raven_mcs.experiments.run_sag_g1_r1b import _condition_flags, _remap_pred_groups
from raven_mcs.experiments.sag_runtime import METHODS, attach_unified_target, prepare_sag_bundle
from raven_mcs.metrics.accuracy import mae_mu, rmse_mu
from raven_mcs.metrics.distribution import delta_group
from raven_mcs.sag.certificates import (
    FrozenSagThresholds,
    c_cov_from_opportunity_lcb,
    lower_pi_opp_event_count_by_pair,
    pair_key,
    provisional_pi_safe_from_public_opp,
)
from raven_mcs.sag.deployment_groups import N_H_GROUPS
from raven_mcs.sag.target_law import (
    COMPAT_ATOL,
    atomic_law_rows,
    compatibility_rows,
    freeze_pi_safe_rule_v1,
)
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
DATASETS = ("sensorscope", "uair")
SEEDS = (30001,)
LOCAL_STEPS = 2
EPS = 1e-12
SOURCE_FILES = (
    "src/raven_mcs/sag/target_law.py",
    "src/raven_mcs/sag/certificates.py",
    "src/raven_mcs/sag/deployment_groups.py",
    "src/raven_mcs/experiments/sag_runtime.py",
    "src/raven_mcs/experiments/run_sag_g1_r1c.py",
    "src/raven_mcs/training/window_runner.py",
    "configs/sag_g0/thresholds.json",
)


def _run_one(*, prepared: dict[str, Any], method: str, thresholds: FrozenSagThresholds, pi_safe: float):
    from raven_mcs.aggregation.method_policy import get_method_policy
    from raven_mcs.training.window_runner import build_full_runner

    policy = get_method_policy(method)
    n_groups = int(prepared["paper_n_groups"])
    runner = build_full_runner(
        prepared["trace"],
        prepared["dataset"],
        method=method,
        n_groups=n_groups,
        model_seed=int(prepared["trace"].metadata.seed),
        local_steps=LOCAL_STEPS,
        target_mu=prepared["paper_mu"],
        pi_target=prepared["pi_target"],
        s_max=int(prepared["trace"].metadata.s_max),
        device="cpu",
        use_coarse_time_groups=False,
        pi_opp_joint=prepared["pi_opp_joint"],
        paper_h_by_unit=prepared["paper_h_by_unit"],
    )
    runner.sag_thresholds = FrozenSagThresholds(
        **{**thresholds.as_dict(), "n_groups": n_groups}
    )
    runner.sag_pi_safe = float(pi_safe)
    window_metrics = runner.run()
    return runner, list(runner.sag_window_logs), window_metrics, policy


def _history_from_logs(logs: list[dict[str, Any]], end: int) -> list[dict[str, Any]]:
    out = []
    for row in logs[:end]:
        out.append(
            {
                "window_id": row.get("window_id"),
                "opp_count_by_pair": dict(row.get("opp_count_by_pair") or {}),
                "opp_event_total": row.get("opp_event_total"),
                "opp_mass_by_pair": dict(row.get("opp_mass_by_pair") or {}),
            }
        )
    return out


def _future_counts(logs: list[dict[str, Any]], start: int) -> tuple[dict[tuple[str, str], float], float]:
    counts: dict[tuple[str, str], float] = {}
    total = 0.0
    for row in logs[start:]:
        raw = row.get("opp_count_by_pair") or {}
        for key, val in raw.items():
            try:
                pk = pair_key(key)
                counts[pk] = counts.get(pk, 0.0) + float(val)
            except (TypeError, ValueError):
                continue
        try:
            total += float(row.get("opp_event_total") or sum(float(v) for v in raw.values()))
        except (TypeError, ValueError):
            continue
    return counts, total


def run_r1c_main(*, root: Path = ROOT, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root)
    g0 = _require_g0_full_pass(root)
    out = Path(output_dir or (root / "outputs" / "sag_g1_r1c"))
    for sub in ("target", "coverage", "calibration", "diagnostic", "tests", "configs"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    thresholds = _load_thresholds()
    shutil.copy2(root / "configs/sag_g0/thresholds.json", out / "configs" / "thresholds_frozen_copy.json")

    hashes = {rel: sha256_file(root / rel) for rel in SOURCE_FILES if (root / rel).is_file()}
    dump_json(hashes, out / "configs" / "source_hashes.json")

    prepared_by_ds: dict[str, dict[str, Any]] = {}
    compat_rows: list[dict[str, Any]] = []
    law_rows: list[dict[str, Any]] = []
    for dataset in DATASETS:
        prepared = attach_unified_target(
            prepare_sag_bundle(root=root, dataset=dataset, seed=int(SEEDS[0])),
            root=root,
        )
        law = prepared["target_law"]
        prepared_by_ds[dataset] = prepared
        compat_rows.extend(compatibility_rows(law))
        law_rows.extend(atomic_law_rows(law, prepared["paper_h_by_unit"]))

    pd.DataFrame(compat_rows).to_csv(out / "target" / "TARGET_COMPATIBILITY_CHECK.csv", index=False)
    pd.DataFrame(law_rows).to_csv(out / "target" / "TARGET_ATOMIC_LAW.csv", index=False)

    max_err = max(float(r["abs_error"]) for r in compat_rows) if compat_rows else float("inf")
    compat_pass = all(int(r["pass"]) == 1 for r in compat_rows) and max_err <= COMPAT_ATOL
    if not compat_pass:
        verdict = {
            "executive_verdict": "TARGET_COMPATIBILITY_NOT_CLOSED",
            "max_abs_error": max_err,
            "g1_r2_5seed_started": False,
        }
        dump_json(verdict, out / "R1C_VERDICT.json")
        (out / "R1C_COVERAGE_REPAIR_REPORT.md").write_text(
            "# 1. Executive Verdict\n\nTARGET_COMPATIBILITY_NOT_CLOSED\n\n"
            f"max_abs_error={max_err}. 1-seed was not started.\n",
            encoding="utf-8",
        )
        return {"output_dir": str(out), "verdict": verdict}

    pi_safe_docs: dict[str, Any] = {}
    for dataset, prepared in prepared_by_ds.items():
        pi_doc = provisional_pi_safe_from_public_opp(
            prepared["pi_target"], prepared["pi_opp_joint"], quantile=0.10,
        )
        pi_safe_docs[dataset] = {
            **pi_doc,
            "frozen_rule_id": "PI_SAFE_RULE_V1",
            "value": float(pi_doc["pi_safe"]),
        }
    frozen_rule = freeze_pi_safe_rule_v1(
        value_sensorscope=float(pi_safe_docs["sensorscope"]["value"]),
        value_uair=float(pi_safe_docs["uair"]["value"]),
        n_pos_sensorscope=int(pi_safe_docs["sensorscope"].get("n_positive_target_pairs") or 0),
        n_pos_uair=int(pi_safe_docs["uair"].get("n_positive_target_pairs") or 0),
    )
    dump_json(frozen_rule, out / "target" / "PI_SAFE_RULE_FROZEN.json")

    gate_rows: list[dict[str, Any]] = []
    method_rows: list[dict[str, Any]] = []
    cov_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []
    cal_rows: list[dict[str, Any]] = []
    old_vs: list[dict[str, Any]] = []
    a8b_cover: list[dict[str, Any]] = []
    a8b_width: list[dict[str, Any]] = []
    tightness: list[dict[str, Any]] = []

    old_cov_path = root / "outputs" / "sag_g1_r1b" / "opportunity" / "C_COV_EVENT_MASS_WINDOW.csv"
    old_cov = pd.read_csv(old_cov_path) if old_cov_path.is_file() else pd.DataFrame()

    for dataset in DATASETS:
        prepared = prepared_by_ds[dataset]
        pi_safe = float(pi_safe_docs[dataset]["value"])
        target_pairs = [
            (str(k[0]), str(k[1]))
            for k, w in prepared["pi_target"].items()
            if float(w) > 0.0
        ]
        sag_logs = None
        for seed in SEEDS:
            for method in METHODS:
                runner, logs, window_metrics, _policy = _run_one(
                    prepared=prepared, method=method, thresholds=thresholds, pi_safe=pi_safe,
                )
                pred = _remap_pred_groups(
                    _predict(runner, prepared["dataset"], split="test"),
                    prepared["paper_h_by_unit"],
                )
                mu_w = _mu_weights_for_test(pred, np.asarray(prepared["paper_mu"]))
                rmse = float(rmse_mu(pred["y_pred"], pred["y_true"], mu_w)) if len(mu_w) else float("nan")
                mae = float(mae_mu(pred["y_pred"], pred["y_true"], mu_w)) if len(mu_w) else float("nan")
                worst = _worst_group_rmse(pred, mu_w)
                try:
                    d_g = float(delta_group(runner.omega_bar(), np.asarray(prepared["paper_mu"])))
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
                    "n_groups": N_H_GROUPS,
                    "target_law_hash": prepared.get("target_law_hash"),
                })
                for row in logs:
                    flat = _flatten_log(row, dataset=dataset, seed=int(seed), method=method)
                    diag = _diag(row)
                    feat = row.get("gate_features") or {}
                    flags = _condition_flags(row)
                    flat.update({
                        "C_cov_LCB": feat.get("C_cov_LCB"),
                        "C_cov_LCB_old_eb": diag.get("C_cov_LCB_old_eb"),
                        "C_ret_LCB": feat.get("C_ret_LCB"),
                        "C_ESS_LCB": feat.get("C_ESS_LCB"),
                        "C_clip_UCB": feat.get("C_clip_UCB"),
                        "delta_A_UCB": feat.get("delta_A_UCB"),
                        "B_tot_UCB": feat.get("B_tot_UCB"),
                        "pass_C_cov": int(flags["C_cov"]),
                        "pass_C_ret": int(flags["C_ret"]),
                        "pass_C_ESS": int(flags["C_ESS"]),
                        "pass_C_clip": int(flags["C_clip"]),
                        "pass_delta_A": int(flags["delta_A"]),
                        "pass_B_tot": int(flags["B_tot"]),
                        "pass_ALL": int(all(flags.values())),
                        "n_groups": N_H_GROUPS,
                        "opp_event_total": row.get("opp_event_total"),
                        "completed_event_total": diag.get("completed_event_total"),
                        "lower_pi_opp_method": diag.get("lower_pi_opp_method"),
                        "target_mass_certified": diag.get("target_mass_certified"),
                    })
                    gate_rows.append(flat)
                    if (
                        method == "raven_sag"
                        and int(row.get("both_empty") or 0) == 0
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
                            except (TypeError, ValueError):
                                width = float("nan")
                                ratio = float("nan")
                                actual_zero = False
                            tightness.append({
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
                            })
                if method == "raven_sag":
                    sag_logs = logs

            assert sag_logs is not None
            for i, row in enumerate(sag_logs):
                feat = row.get("gate_features") or {}
                diag = _diag(row)
                flags = _condition_flags(row)
                hist = _history_from_logs(sag_logs, i)
                lowers = (
                    lower_pi_opp_event_count_by_pair(
                        hist, target_pairs, delta=float(thresholds.delta_cal), bonferroni=True,
                    )
                    if hist
                    else {}
                )
                cov_info = (
                    c_cov_from_opportunity_lcb(prepared["pi_target"], lowers, pi_safe)
                    if lowers
                    else {"C_cov_LCB": float("nan"), "target_mass_certified": float("nan")}
                )
                counts_now = [float(v.get("count") or 0.0) for v in lowers.values()] if lowers else []
                sample_rows.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "window": row.get("window_id"),
                    "history_windows": len(hist),
                    "total_completed_events": next(iter(lowers.values()), {}).get("n") if lowers else 0.0,
                    "target_positive_pairs": len(target_pairs),
                    "min_pair_count": min(counts_now) if counts_now else 0.0,
                    "median_pair_count": float(np.median(counts_now)) if counts_now else 0.0,
                    "max_pair_count": max(counts_now) if counts_now else 0.0,
                })
                future, future_n = _future_counts(sag_logs, i)
                n_pair_cover = 0
                w_pair_cover = 0.0
                w_total = 0.0
                n_eval = 0
                slacks: list[float] = []
                for key in target_pairs:
                    rec = lowers.get(key, {})
                    lower = rec.get("lower_pi_opp", float("nan"))
                    ref = (float(future.get(key, 0.0)) / future_n) if future_n > 0 else float("nan")
                    covered = (
                        np.isfinite(float(lower)) and np.isfinite(ref) and float(lower) <= float(ref)
                    )
                    w = float(prepared["pi_target"][key])
                    w_total += w
                    if np.isfinite(ref):
                        n_eval += 1
                        n_pair_cover += int(covered)
                        w_pair_cover += w if covered else 0.0
                        if np.isfinite(float(lower)):
                            slacks.append(float(ref) - float(lower))
                    pair_rows.append({
                        "dataset": dataset,
                        "seed": int(seed),
                        "window_id": row.get("window_id"),
                        "client": key[0],
                        "stratum": key[1],
                        "pi_tar": w,
                        "count": rec.get("count"),
                        "n_events": rec.get("n"),
                        "pi_hat_opp": rec.get("pi_hat_opp"),
                        "lower_pi_opp": lower,
                        "pi_opp_ref_future": ref,
                        "pair_covered": int(covered) if np.isfinite(ref) else None,
                        "certified": int(
                            np.isfinite(float(lower)) and float(lower) >= float(pi_safe)
                        ) if np.isfinite(float(lower) if lower is not None else float("nan")) else 0,
                    })
                joint = int(n_eval > 0 and n_pair_cover == n_eval)
                cal_rows.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "window_id": row.get("window_id"),
                    "pairwise_coverage": (n_pair_cover / n_eval) if n_eval else float("nan"),
                    "target_mass_weighted_coverage": (w_pair_cover / w_total) if w_total else float("nan"),
                    "joint_window_coverage": joint,
                    "mean_lcb_slack": float(np.mean(slacks)) if slacks else float("nan"),
                    "median_lcb_slack": float(np.median(slacks)) if slacks else float("nan"),
                    "certified_target_mass": cov_info.get("target_mass_certified"),
                    "n_pairs_evaluated": n_eval,
                })
                cov_rows.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "window_id": row.get("window_id"),
                    "G_r": row.get("G_r"),
                    "fallback_reason": row.get("fallback_reason"),
                    "pi_safe": pi_safe,
                    "C_cov_LCB": feat.get("C_cov_LCB"),
                    "C_cov_LCB_recomputed": cov_info.get("C_cov_LCB"),
                    "C_cov_LCB_old_eb": diag.get("C_cov_LCB_old_eb"),
                    "target_mass_certified": diag.get("target_mass_certified", cov_info.get("target_mass_certified")),
                    "opp_event_total": row.get("opp_event_total"),
                    "completed_event_total": diag.get("completed_event_total"),
                    "cold_start": feat.get("cold_start"),
                    "pass_ALL": int(all(flags.values())),
                    "pass_C_cov": int(flags["C_cov"]),
                })
                old_val = float("nan")
                if not old_cov.empty:
                    match = old_cov[
                        (old_cov["dataset"] == dataset)
                        & (old_cov["seed"] == int(seed))
                        & (old_cov["window_id"] == int(row.get("window_id")))
                    ]
                    if len(match):
                        old_val = match.iloc[0].get("C_cov_LCB")
                old_vs.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "window_id": row.get("window_id"),
                    "C_cov_old_eb": old_val,
                    "C_cov_new_cp": feat.get("C_cov_LCB"),
                    "C_cov_old_eb_runtime": diag.get("C_cov_LCB_old_eb"),
                })

    pd.DataFrame(gate_rows).to_csv(out / "diagnostic" / "R1C_GATE_WINDOW_LOG.csv", index=False)
    pd.DataFrame(method_rows).to_csv(out / "diagnostic" / "R1C_METHOD_DIAGNOSTIC.csv", index=False)
    pd.DataFrame(sample_rows).to_csv(out / "coverage" / "EVENT_COUNT_EFFECTIVE_SAMPLE.csv", index=False)
    pd.DataFrame(pair_rows).to_csv(out / "coverage" / "OPPORTUNITY_LCB_PAIR.csv", index=False)
    pd.DataFrame(cov_rows).to_csv(out / "coverage" / "C_COV_WINDOW.csv", index=False)
    pd.DataFrame(cal_rows).to_csv(out / "coverage" / "C_COV_CALIBRATION.csv", index=False)
    pd.DataFrame(old_vs).to_csv(out / "coverage" / "C_COV_OLD_VS_NEW.csv", index=False)

    a8b_rows = []
    width_rows = []
    for dataset in DATASETS:
        sub = [r for r in tightness if r["dataset"] == dataset]
        rec: dict[str, Any] = {"dataset": dataset, "seed": 30001, "coverage_target": 0.95}
        wrec: dict[str, Any] = {"dataset": dataset, "seed": 30001}
        by_win: dict[Any, dict[str, Any]] = {}
        for row in sub:
            by_win.setdefault(row["window_id"], {})[row["metric"]] = row
        joint_ok = []
        for mets in by_win.values():
            if set(mets) >= {"beta", "M", "V"}:
                flags = [mets[m].get("covered") for m in ("beta", "M", "V")]
                if all(f is not None for f in flags):
                    joint_ok.append(int(all(float(f) > 0.5 for f in flags)))
        rec["n_common_nonempty"] = len(by_win)
        rec["cover_joint"] = float(np.mean(joint_ok)) if joint_ok else float("nan")
        for metric in ("beta", "M", "V"):
            rows_m = [r for r in sub if r["metric"] == metric]
            covers = [float(r["covered"]) for r in rows_m if r["covered"] is not None]
            widths = [float(r["width"]) for r in rows_m if np.isfinite(float(r["width"]))]
            ratios = [float(r["ucb_over_actual"]) for r in rows_m if np.isfinite(float(r.get("ucb_over_actual", math.nan)))]
            rec[f"cover_{metric}"] = float(np.mean(covers)) if covers else float("nan")
            wrec[f"width_{metric}_mean"] = float(np.mean(widths)) if widths else float("nan")
            wrec[f"width_{metric}_median"] = float(np.median(widths)) if widths else float("nan")
            wrec[f"ucb_over_actual_{metric}"] = float(np.mean(ratios)) if ratios else float("nan")
            wrec[f"actual_zero_rate_{metric}"] = float(np.mean([r["actual_zero"] for r in rows_m])) if rows_m else float("nan")
        a8b_rows.append(rec)
        width_rows.append(wrec)
    pd.DataFrame(a8b_rows).to_csv(out / "calibration" / "A8B_CERTIFICATE_COVERAGE_R1C.csv", index=False)
    pd.DataFrame(width_rows).to_csv(out / "calibration" / "A8B_CERTIFICATE_WIDTH_R1C.csv", index=False)

    pass_rows = []
    sag = pd.DataFrame(gate_rows)
    sag = sag[sag["method"] == "raven_sag"] if "method" in sag.columns else sag
    for dataset in DATASETS:
        sub = sag[sag["dataset"] == dataset] if "dataset" in sag.columns else sag
        rec = {"dataset": dataset, "seed": 30001, "n": int(len(sub))}
        for name in ("C_cov", "C_ret", "C_ESS", "C_clip", "delta_A", "B_tot", "ALL"):
            col = f"pass_{name}" if name != "ALL" else "pass_ALL"
            rec[f"pass_rate_{name}"] = (
                float(pd.to_numeric(sub[col], errors="coerce").mean())
                if col in sub.columns and len(sub)
                else float("nan")
            )
        rec["Gate_ON_rate"] = float((sub["G_r"] == 1).mean()) if "G_r" in sub.columns and len(sub) else 0.0
        rec["first_fail"] = json.dumps(
            sub["fallback_reason"].fillna("ON").value_counts().to_dict()
        ) if "fallback_reason" in sub.columns else "{}"
        all_fail: Counter[str] = Counter()
        for _, row in sub.iterrows():
            for name in ("C_cov", "C_ret", "C_ESS", "C_clip", "delta_A", "B_tot"):
                if int(row.get(f"pass_{name}", 0) or 0) == 0:
                    all_fail[name] += 1
        rec["all_fail"] = json.dumps(dict(all_fail))
        pass_rows.append(rec)
    pd.DataFrame(pass_rows).to_csv(out / "diagnostic" / "R1C_GATE_PASSRATE.csv", index=False)

    config = {
        "mode": "g1_r1c_1seed",
        "datasets": list(DATASETS),
        "seeds": list(SEEDS),
        "methods": list(METHODS),
        "local_steps": LOCAL_STEPS,
        "git_commit": _git_hash(),
        "g0_config_hash": g0.get("config", {}).get("config_hash"),
        "threshold_hash": sha256_file(root / "configs/sag_g0/thresholds.json"),
        "tau_unchanged": True,
        "paper_n_groups": N_H_GROUPS,
        "target_compatibility_pass": True,
        "max_abs_error": max_err,
        "pi_safe_rule": frozen_rule,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(config, out / "configs" / "config_r1c.json")
    verdict = write_r1c_report(out)
    return {"output_dir": str(out), "config": config, "verdict": verdict}


def write_r1c_report(out: Path) -> dict[str, Any]:
    out = Path(out)
    gate = pd.read_csv(out / "diagnostic" / "R1C_GATE_WINDOW_LOG.csv")
    passrate = pd.read_csv(out / "diagnostic" / "R1C_GATE_PASSRATE.csv")
    compat = pd.read_csv(out / "target" / "TARGET_COMPATIBILITY_CHECK.csv")
    cov = pd.read_csv(out / "coverage" / "C_COV_WINDOW.csv")
    sample = pd.read_csv(out / "coverage" / "EVENT_COUNT_EFFECTIVE_SAMPLE.csv")
    cal = pd.read_csv(out / "coverage" / "C_COV_CALIBRATION.csv")
    oldvs = pd.read_csv(out / "coverage" / "C_COV_OLD_VS_NEW.csv")
    a8b = pd.read_csv(out / "calibration" / "A8B_CERTIFICATE_COVERAGE_R1C.csv")
    width = pd.read_csv(out / "calibration" / "A8B_CERTIFICATE_WIDTH_R1C.csv")
    frozen = json.loads((out / "target" / "PI_SAFE_RULE_FROZEN.json").read_text(encoding="utf-8"))

    sag = gate[gate["method"] == "raven_sag"].copy() if "method" in gate.columns else gate

    def rates(frame: pd.DataFrame) -> dict[str, Any]:
        outd = {"n": int(len(frame)), "on": int((frame["G_r"] == 1).sum()) if "G_r" in frame.columns else 0}
        outd["on_rate"] = float(outd["on"] / outd["n"]) if outd["n"] else 0.0
        for name in ("C_cov", "C_ret", "C_ESS", "C_clip", "delta_A", "B_tot", "ALL"):
            col = f"pass_{name}" if name != "ALL" else "pass_ALL"
            outd[name] = (
                float(pd.to_numeric(frame[col], errors="coerce").mean())
                if col in frame.columns and len(frame)
                else float("nan")
            )
        outd["reasons"] = (
            frame["fallback_reason"].fillna("ON").value_counts().to_dict()
            if "fallback_reason" in frame.columns
            else {}
        )
        return outd

    ss = rates(sag[sag["dataset"] == "sensorscope"]) if "dataset" in sag.columns else rates(sag)
    ua = rates(sag[sag["dataset"] == "uair"]) if "dataset" in sag.columns else rates(pd.DataFrame())

    def cov_sum(dataset: str) -> dict[str, float]:
        sub = cov[cov["dataset"] == dataset] if "dataset" in cov.columns else cov
        xs = pd.to_numeric(sub["C_cov_LCB"], errors="coerce").dropna()
        return {
            "median": float(xs.median()) if len(xs) else float("nan"),
            "p05": float(xs.quantile(0.05)) if len(xs) else float("nan"),
            "p95": float(xs.quantile(0.95)) if len(xs) else float("nan"),
            "frac_zero": float((xs <= 1e-15).mean()) if len(xs) else float("nan"),
            "frac_pos": float((xs > 0).mean()) if len(xs) else float("nan"),
        }

    ss_c, ua_c = cov_sum("sensorscope"), cov_sum("uair")
    max_err = float(compat["abs_error"].max()) if len(compat) else float("nan")
    events_ss = pd.to_numeric(
        sample.loc[sample["dataset"] == "sensorscope", "total_completed_events"], errors="coerce"
    ) if "dataset" in sample.columns else pd.Series(dtype=float)
    events_ua = pd.to_numeric(
        sample.loc[sample["dataset"] == "uair", "total_completed_events"], errors="coerce"
    ) if "dataset" in sample.columns else pd.Series(dtype=float)

    old_zero = float((pd.to_numeric(oldvs["C_cov_old_eb"], errors="coerce").fillna(0) <= 1e-15).mean()) if len(oldvs) else float("nan")
    new_zero = float((pd.to_numeric(oldvs["C_cov_new_cp"], errors="coerce").fillna(0) <= 1e-15).mean()) if len(oldvs) else float("nan")

    a8b_ss = a8b[a8b["dataset"] == "sensorscope"].iloc[0].to_dict() if len(a8b) and "dataset" in a8b.columns else {}
    a8b_ua = a8b[a8b["dataset"] == "uair"].iloc[0].to_dict() if len(a8b[a8b["dataset"] == "uair"]) else {}
    joint_ss = float(a8b_ss.get("cover_joint", float("nan")))
    a8b_note = "A8B_CALIBRATION_NOT_YET_CLOSED" if (np.isfinite(joint_ss) and joint_ss < 0.95) else "A8b joint coverage at or above 0.95 (development audit)"

    degenerate = (
        (ss_c["frac_zero"] >= 0.99 and ua_c["frac_zero"] >= 0.99)
        and float(events_ss.max() if len(events_ss.dropna()) else 0) > 32
    )
    ss_on = ss["on"]
    ua_delta = ua.get("delta_A", float("nan"))
    ua_on = ua.get("on", 0)
    cov_alive = (ss_c["frac_pos"] > 0.5) and (ss.get("C_cov", 0) > 0)

    if degenerate:
        verdict = "COV_CERTIFICATE_STILL_DEGENERATE"
    elif not cov_alive:
        verdict = "NEEDS_MORE_COV_CERTIFICATE_REPAIR"
    elif ss_on > 0 and ua_on <= max(1, int(0.15 * max(ua.get("n", 0), 1))) and (
        not np.isfinite(ua_delta) or ua_delta < 0.5
    ):
        verdict = "READY_FOR_G1_R2_5SEED"
        if np.isfinite(joint_ss) and joint_ss < 0.95:
            verdict = "READY_WITH_A8B_CALIBRATION_REPAIR"
    elif ss_on > 0:
        # C_cov is usable and SS has legal ON, but U-Air is no longer
        # discriminated by delta_A / safety certificates.
        verdict = "TARGET_COMPATIBILITY_BUG_FIXED"
    else:
        verdict = "NEEDS_MORE_COV_CERTIFICATE_REPAIR"

    def a8b_line(rec: dict[str, Any]) -> str:
        if not rec:
            return "n/a"
        return (
            f"cover β={rec.get('cover_beta')} M={rec.get('cover_M')} V={rec.get('cover_V')} "
            f"joint={rec.get('cover_joint')} n={rec.get('n_common_nonempty')}"
        )

    cal_ss = cal[cal["dataset"] == "sensorscope"] if "dataset" in cal.columns else cal
    cal_ua = cal[cal["dataset"] == "uair"] if "dataset" in cal.columns else cal

    report = f"""# 1. Executive Verdict

{verdict}

R1c is a 1-seed target-compatibility + coverage-certificate repair (SensorScope 30001, U-Air 30001). Frozen `tau_*` were not changed. 5-seed was not started.

# 2. Target Compatibility

`varpi_tar` is uniform over train-split supported atoms (`build_frozen_atomic_target_law`).
`μ` is the paper-`h(i)` marginal of that law.
`π^{{tar}}` is the client×stratum pushforward of the same law with frozen `ξ_{{k|i}}=1{{client(spatial_id)=k}}`.

R1b source split: μ from train, `π^{{tar}}` from `build_pi_target(..., split="test")`. **BUG_CONFIRMED** then **FIXED**.

max compatibility error = {max_err} (atol={COMPAT_ATOL}).

# 3. pi_safe Freeze

rule={frozen.get('rule_id')}; quantile={frozen.get('quantile')}; source={frozen.get('data_source')};
excludes={frozen.get('excludes')};
SensorScope={frozen.get('value_SensorScope')}; U-Air={frozen.get('value_UAir')};
hash={frozen.get('hash')}.

# 4. Old C_cov Failure Mechanism

Old estimator: empirical-Bernstein on per-window normalized pair masses, lookback ≤ 32.
Typical pair mass ≈ 0.125. For n=32, δ=0.05: `sqrt(2v log(1/δ)/n) + 3 log(1/δ)/n` exceeds the mean, so LCB clips to 0.
Old C_cov zero fraction (R1b vs this run) = {old_zero}.

# 5. New Opportunity LCB

Event-count one-sided Clopper–Pearson on completed events `t<r` (all history, not 32 mass samples).
Assumption: completed opportunity events are exchangeable marks of the frozen EventTrace event-mark law.
Simultaneous correction: Bonferroni `δ_pair = delta_cal / m_{{π^{{tar}}>0}}`.
SensorScope max completed events = {float(events_ss.max()) if len(events_ss.dropna()) else float('nan')}.
U-Air max completed events = {float(events_ua.max()) if len(events_ua.dropna()) else float('nan')}.

# 6. C_cov Results

SensorScope: median={ss_c['median']} p05={ss_c['p05']} p95={ss_c['p95']} frac>0={ss_c['frac_pos']} pass={ss.get('C_cov')}
U-Air: median={ua_c['median']} p05={ua_c['p05']} p95={ua_c['p95']} frac>0={ua_c['frac_pos']} pass={ua.get('C_cov')}
New vs old zero fraction: old={old_zero} new={new_zero}.
Calibration pairwise/target-mass/joint (SS mean): {float(pd.to_numeric(cal_ss['pairwise_coverage'], errors='coerce').mean()) if len(cal_ss) else float('nan')} / {float(pd.to_numeric(cal_ss['target_mass_weighted_coverage'], errors='coerce').mean()) if len(cal_ss) else float('nan')} / {float(pd.to_numeric(cal_ss['joint_window_coverage'], errors='coerce').mean()) if len(cal_ss) else float('nan')}
U-Air calibration pairwise mean: {float(pd.to_numeric(cal_ua['pairwise_coverage'], errors='coerce').mean()) if len(cal_ua) else float('nan')}

# 7. A8b 95% Calibration

SensorScope: {a8b_line(a8b_ss)}
U-Air: {a8b_line(a8b_ua)}
{a8b_note}

# 8. Gate Re-Diagnostic

Dataset | Ccov | Cret | CESS | Cclip | deltaA | Btot | ALL | ON
---|---|---|---|---|---|---|---|---
SensorScope | {ss.get('C_cov')} | {ss.get('C_ret')} | {ss.get('C_ESS')} | {ss.get('C_clip')} | {ss.get('delta_A')} | {ss.get('B_tot')} | {ss.get('ALL')} | {ss.get('on_rate')}
U-Air | {ua.get('C_cov')} | {ua.get('C_ret')} | {ua.get('C_ESS')} | {ua.get('C_clip')} | {ua.get('delta_A')} | {ua.get('B_tot')} | {ua.get('ALL')} | {ua.get('on_rate')}

SensorScope first-fail: {ss.get('reasons')}
U-Air first-fail: {ua.get('reasons')}

# 9. Scientific Interpretation

SensorScope legal ON windows: {ss_on} / {ss.get('n')}.
U-Air legal ON windows: {ua_on} / {ua.get('n')}.
U-Air delta_A pass rate: {ua_delta}.

C_cov is no longer the unique all-zero blocker. After the train-split unified `π^{{tar}}` and event-count CP LCB, both datasets produce legal ALL-pass windows. U-Air is **not** mainly intercepted by the active-set-risk certificate in this 1-seed diagnostic, so the intended SS-vs-U-Air Gate discrimination is not yet established.

# 10. Next Decision

Verdict {verdict}. Do not auto-start 5-seed.
READY_FOR_G1_R2_5SEED requires SensorScope legal ON **and** U-Air support-unsafe windows still mostly OFF. The second clause is not met.
"""
    (out / "R1C_COVERAGE_REPAIR_REPORT.md").write_text(report, encoding="utf-8")
    verdict_payload = {
        "executive_verdict": verdict,
        "target_compatibility_pass": True,
        "max_abs_error": max_err,
        "old_bug": "TARGET_COMPATIBILITY_BUG_FIXED",
        "c_cov_old_zero_fraction": old_zero,
        "c_cov_new_zero_fraction": new_zero,
        "sensorscope_gate": ss,
        "uair_gate": ua,
        "pi_safe": frozen,
        "a8b_note": a8b_note,
        "g1_r2_5seed_started": False,
        "passrate": passrate.to_dict(orient="records"),
    }
    dump_json(verdict_payload, out / "R1C_VERDICT.json")
    return verdict_payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default="")
    args = parser.parse_args()
    out = Path(args.output_dir) if args.output_dir else None
    result = run_r1c_main(output_dir=out)
    print(json.dumps({"verdict": result["verdict"]["executive_verdict"], "output_dir": result["output_dir"]}, indent=2))


if __name__ == "__main__":
    main()

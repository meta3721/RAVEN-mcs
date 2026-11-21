"""SAG G1-R1d target-semantics freeze + dynamic C_cov audit. No 5-seed."""

from __future__ import annotations

import argparse
import json
import math
import shutil
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
    pair_key,
    provisional_pi_safe_from_public_opp,
)
from raven_mcs.sag.deployment_groups import N_H_GROUPS
from raven_mcs.sag.dynamic_cov import (
    coverage_flags,
    dynamic_lower_pi_opp,
    extract_window_opp_masses,
)
from raven_mcs.sag.target_law import (
    COMPAT_ATOL,
    compare_target_laws,
    compatibility_rows,
    freeze_target_law_rule_v1,
)
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
DATASETS = ("sensorscope", "uair")
SEEDS = (30001,)
LOCAL_STEPS = 2
EPS = 1e-12
ROLLING_L = 8
SOURCE_FILES = (
    "src/raven_mcs/sag/target_law.py",
    "src/raven_mcs/sag/dynamic_cov.py",
    "src/raven_mcs/sag/certificates.py",
    "src/raven_mcs/experiments/sag_runtime.py",
    "src/raven_mcs/experiments/run_sag_g1_r1d.py",
    "configs/sag_g0/thresholds.json",
)


def _run_one(
    *,
    prepared: dict[str, Any],
    method: str,
    thresholds: FrozenSagThresholds,
    pi_safe: float,
    cov_mode: str,
):
    from raven_mcs.aggregation.method_policy import get_method_policy
    from raven_mcs.training.window_runner import build_full_runner

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
    runner.sag_thresholds = FrozenSagThresholds(**{**thresholds.as_dict(), "n_groups": n_groups})
    runner.sag_pi_safe = float(pi_safe)
    runner.sag_cov_mode = str(cov_mode)
    runner.sag_rolling_L = ROLLING_L
    window_metrics = runner.run()
    return runner, list(runner.sag_window_logs), window_metrics, get_method_policy(method)


def _offline_dynamic_cov(
    opp_rows: list[dict[str, Any]],
    pi_target: dict[tuple[str, str], float],
    pi_safe: float,
    delta_cal: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    pairs = [(str(k[0]), str(k[1])) for k, w in pi_target.items() if float(w) > 0.0]
    pred_rows: list[dict[str, Any]] = []
    cal_rows: list[dict[str, Any]] = []
    time_rows: list[dict[str, Any]] = []
    warmup_joint: list[int] = []
    warmup_pair: list[float] = []
    c_cov_vals: list[float] = []
    for i, row in enumerate(opp_rows):
        hist = opp_rows[:i]
        dyn = dynamic_lower_pi_opp(
            hist, pairs, lookback=ROLLING_L, delta=delta_cal, min_calib=ROLLING_L,
        )
        realized = {}
        raw = row.get("opp_mass_by_pair") or {}
        for key, val in raw.items():
            try:
                realized[pair_key(key)] = float(val)
            except (TypeError, ValueError):
                continue
        cov_info = (
            c_cov_from_opportunity_lcb(pi_target, dyn["lowers"], pi_safe)
            if not dyn["cold_start"]
            else {"C_cov_LCB": float("nan"), "target_mass_certified": float("nan")}
        )
        flags = coverage_flags(dyn["lowers"], realized, pi_target)
        from raven_mcs.sag.evidence import optional_float

        certified = optional_float(cov_info.get("target_mass_certified"))
        realized_support = float(
            sum(realized.get(k, 0.0) for k in pairs)
        )
        rec = {
            "window_id": row.get("window_id"),
            "history_windows": i,
            "cold_start": int(dyn["cold_start"]),
            "n_calib": dyn.get("n_calib"),
            "q_max_residual": dyn.get("q"),
            "C_cov_LCB": cov_info.get("C_cov_LCB"),
            "target_mass_certified": certified,
            "realized_target_support_mass": realized_support,
            **flags,
        }
        cal_rows.append(rec)
        time_rows.append(rec)
        if not dyn["cold_start"]:
            warmup_joint.append(int(flags["joint_window_coverage"]))
            warmup_pair.append(float(flags["pairwise_coverage"]))
            if np.isfinite(float(cov_info.get("C_cov_LCB", float("nan")))):
                c_cov_vals.append(float(cov_info["C_cov_LCB"]))
        for key in pairs:
            rec_l = dyn["lowers"].get(key, {})
            pred_rows.append({
                "window_id": row.get("window_id"),
                "client": key[0],
                "stratum": key[1],
                "pi_tar": float(pi_target[key]),
                "pi_hat_opp": rec_l.get("pi_hat_opp"),
                "lower_pi_opp": rec_l.get("lower_pi_opp"),
                "pi_opp_realized": realized.get(key, 0.0),
                "q_max_residual": dyn.get("q"),
                "cold_start": int(dyn["cold_start"]),
            })
    n_w = len(warmup_joint)
    first = warmup_pair[: max(n_w // 3, 1)] if warmup_pair else []
    last = warmup_pair[-max(n_w // 3, 1):] if warmup_pair else []
    joint = float(np.mean(warmup_joint)) if warmup_joint else float("nan")
    pair = float(np.mean(warmup_pair)) if warmup_pair else float("nan")
    slide = (
        (float(np.mean(last)) + 1e-12) < (float(np.mean(first)) - 0.10)
        if first and last and n_w >= 12
        else False
    )
    c_zero = float(np.mean([v <= 1e-15 for v in c_cov_vals])) if c_cov_vals else float("nan")
    status = "CALIBRATED"
    if (not warmup_joint) or (np.isfinite(joint) and joint < 0.90) or slide:
        status = "DYNAMIC_COV_NOT_CALIBRATED"
    elif np.isfinite(c_zero) and c_zero >= 0.90 and np.isfinite(joint) and joint >= 0.90:
        status = "DYNAMIC_COV_TOO_CONSERVATIVE"
    summary = {
        "status": status,
        "n_warmup": n_w,
        "window_joint_coverage": joint,
        "pairwise_coverage": pair,
        "coverage_slides_over_time": slide,
        "c_cov_zero_fraction_warmup": c_zero,
        "mean_c_cov": float(np.mean(c_cov_vals)) if c_cov_vals else float("nan"),
    }
    return pred_rows, cal_rows, time_rows, summary


def run_r1d_main(*, root: Path = ROOT, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root)
    g0 = _require_g0_full_pass(root)
    out = Path(output_dir or (root / "outputs" / "sag_g1_r1d"))
    for sub in ("target", "dynamic_cov", "unsafe_audit", "a8b", "diagnostic", "tests", "configs"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    thresholds = _load_thresholds()
    shutil.copy2(root / "configs/sag_g0/thresholds.json", out / "configs" / "thresholds_frozen_copy.json")
    dump_json({rel: sha256_file(root / rel) for rel in SOURCE_FILES if (root / rel).is_file()}, out / "configs" / "source_hashes.json")
    rule = freeze_target_law_rule_v1()
    dump_json(rule, out / "target" / "TARGET_LAW_RULE_FROZEN.json")
    dump_json({"rule_hash": rule["hash"], "rule_id": rule["rule_id"]}, out / "configs" / "target_rule_hash.json")
    dump_json(
        {
            "cov_mode": "dynamic_max_residual",
            "predictor": "rolling_mean",
            "lookback_L": ROLLING_L,
            "calibration": "window_max_residual_conformal",
            "delta": float(thresholds.delta_cal),
            "min_calib": ROLLING_L,
        },
        out / "configs" / "dynamic_cov_config.json",
    )

    prepared_by: dict[str, dict[str, Any]] = {}
    compat_rows: list[dict[str, Any]] = []
    cmp_rows: list[dict[str, Any]] = []
    pi_safe_docs: dict[str, Any] = {}
    for dataset in DATASETS:
        prepared = attach_unified_target(
            prepare_sag_bundle(root=root, dataset=dataset, seed=int(SEEDS[0])),
            root=root,
        )
        law = prepared["target_law"]
        if not law.compatibility["passed"]:
            verdict = {
                "executive_verdict": "TARGET_SEMANTICS_NOT_FROZEN",
                "reason": "compatibility failed after V1 freeze",
                "max_abs_error": law.compatibility["max_abs_error"],
                "g1_r2_5seed_started": False,
            }
            dump_json(verdict, out / "R1D_VERDICT.json")
            (out / "R1D_TARGET_DYNAMIC_COV_REPORT.md").write_text(
                f"# 1. Executive Verdict\n\nTARGET_SEMANTICS_NOT_FROZEN\n\nmax_abs_error={law.compatibility['max_abs_error']}\n",
                encoding="utf-8",
            )
            return {"output_dir": str(out), "verdict": verdict}
        prepared_by[dataset] = prepared
        compat_rows.extend(compatibility_rows(law))
        cmp_rows.append(compare_target_laws(prepared["target_law_r1c"], law, prepared["pi_opp_joint"]))
        pi_doc = provisional_pi_safe_from_public_opp(
            prepared["pi_target"], prepared["pi_opp_joint"], quantile=0.10,
        )
        pi_safe_docs[dataset] = float(pi_doc["pi_safe"])
    pd.DataFrame(compat_rows).to_csv(out / "target" / "TARGET_COMPATIBILITY_R1D.csv", index=False)
    pd.DataFrame(cmp_rows).to_csv(out / "target" / "TARGET_LAW_R1C_VS_R1D.csv", index=False)

    realized_rows: list[dict[str, Any]] = []
    pred_all: list[dict[str, Any]] = []
    cal_all: list[dict[str, Any]] = []
    time_all: list[dict[str, Any]] = []
    cov_win: list[dict[str, Any]] = []
    dyn_status: dict[str, Any] = {}
    for dataset, prepared in prepared_by.items():
        opp = extract_window_opp_masses(
            trace_events=prepared["trace"].events,
            dataset=prepared["dataset"],
            n_windows=int(prepared["trace"].metadata.num_windows),
            paper_h_by_unit=prepared["paper_h_by_unit"],
        )
        for row in opp:
            for key, n_evt in (row.get("opp_count_by_pair") or {}).items():
                client, stratum = pair_key(key)
                realized_rows.append({
                    "dataset": dataset,
                    "seed": 30001,
                    "window_id": row["window_id"],
                    "client": client,
                    "stratum": stratum,
                    "N_opp": n_evt,
                    "pi_opp_realized": (row.get("opp_mass_by_pair") or {}).get(key),
                })
        pred, cal, trows, summary = _offline_dynamic_cov(
            opp, prepared["pi_target"], pi_safe_docs[dataset], float(thresholds.delta_cal),
        )
        dyn_status[dataset] = summary
        for row in pred:
            pred_all.append({"dataset": dataset, "seed": 30001, **row})
        for row in cal:
            cal_all.append({"dataset": dataset, "seed": 30001, **row})
            cov_win.append({"dataset": dataset, "seed": 30001, **row})
        for row in trows:
            time_all.append({"dataset": dataset, "seed": 30001, **row})

    pd.DataFrame(realized_rows).to_csv(out / "dynamic_cov" / "CURRENT_WINDOW_OPP_REALIZED.csv", index=False)
    pd.DataFrame(pred_all).to_csv(out / "dynamic_cov" / "DYNAMIC_COV_PREDICTION.csv", index=False)
    pd.DataFrame(cal_all).to_csv(out / "dynamic_cov" / "DYNAMIC_COV_CALIBRATION.csv", index=False)
    pd.DataFrame(time_all).to_csv(out / "dynamic_cov" / "DYNAMIC_COV_COVERAGE_BY_TIME.csv", index=False)
    pd.DataFrame(cov_win).to_csv(out / "dynamic_cov" / "C_COV_DYNAMIC_WINDOW.csv", index=False)

    not_cal = any(s["status"] == "DYNAMIC_COV_NOT_CALIBRATED" for s in dyn_status.values())
    too_cons = any(s["status"] == "DYNAMIC_COV_TOO_CONSERVATIVE" for s in dyn_status.values())
    if not_cal or too_cons:
        verdict_name = "DYNAMIC_COV_NOT_CALIBRATED" if not_cal else "DYNAMIC_COV_TOO_CONSERVATIVE"
        payload = {
            "executive_verdict": verdict_name,
            "target_rule": rule,
            "dynamic_cov": dyn_status,
            "g1_r2_5seed_started": False,
            "sag_ran": False,
        }
        dump_json(payload, out / "R1D_VERDICT.json")
        write_r1d_report(out, sag_ran=False)
        return {"output_dir": str(out), "verdict": payload}

    # Calibration passed: Always-D vs No-D unsafe reaudit, then maybe SAG.
    method_rows: list[dict[str, Any]] = []
    gate_rows: list[dict[str, Any]] = []
    unsafe_rows: list[dict[str, Any]] = []
    tightness: list[dict[str, Any]] = []
    run_methods = ("raven", "raven_wo_design")
    sag_allowed = False
    uair_unsafe = False
    for dataset, prepared in prepared_by.items():
        pi_safe = pi_safe_docs[dataset]
        by_method: dict[str, dict[str, Any]] = {}
        for method in run_methods:
            runner, logs, window_metrics, _ = _run_one(
                prepared=prepared, method=method, thresholds=thresholds,
                pi_safe=pi_safe, cov_mode="dynamic_max_residual",
            )
            pred = _remap_pred_groups(
                _predict(runner, prepared["dataset"], split="test"),
                prepared["paper_h_by_unit"],
            )
            mu_w = _mu_weights_for_test(pred, np.asarray(prepared["paper_mu"]))
            rmse = float(rmse_mu(pred["y_pred"], pred["y_true"], mu_w)) if len(mu_w) else float("nan")
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
                seed=30001,
                scenario="complete_aligned",
                method=method,
                eventtrace_hash=str(prepared["identity"].get("trace_hash")),
                stratum_map_hash=None,
                target_mass_hash=prepared["target_artifact_sha256"],
                method_source_hash=None,
            )
            mismatch = [float(r.get("active_set_mismatch") or 0) for r in logs]
            ess = [float((r.get("gate_features") or {}).get("C_ESS_LCB") or float("nan")) for r in logs]
            clip = [float((r.get("gate_features") or {}).get("C_clip_UCB") or float("nan")) for r in logs]
            rec = {
                "dataset": dataset,
                "method": method,
                "RMSE_mu": rmse,
                "WorstGroupRMSE": worst,
                "Delta_group": d_g,
                "Delta_cs": pair_summary.get("Delta_c_s"),
                "active_set_mismatch_rate": float(np.mean(mismatch)) if mismatch else float("nan"),
                "n_windows": len(logs),
            }
            method_rows.append(rec)
            by_method[method] = rec
            for row in logs:
                flat = _flatten_log(row, dataset=dataset, seed=30001, method=method)
                feat = row.get("gate_features") or {}
                flags = _condition_flags(row)
                flat.update({
                    "C_cov_LCB": feat.get("C_cov_LCB"),
                    "pass_ALL": int(all(flags.values())),
                    "active_set_mismatch": row.get("active_set_mismatch"),
                })
                gate_rows.append(flat)
                if method == "raven" and int(row.get("both_empty") or 0) == 0 and int(row.get("active_set_mismatch") or 0) == 0:
                    for name, actual_key, bound_key in (
                        ("beta", "Delta_beta", "Delta_beta_UCB"),
                        ("M", "Delta_M", "Delta_M_UCB"),
                        ("V", "Delta_V", "Delta_V_UCB"),
                    ):
                        actual = row.get(actual_key)
                        bound = feat.get(bound_key)
                        tightness.append({
                            "dataset": dataset,
                            "window_id": row.get("window_id"),
                            "metric": name,
                            "actual": actual,
                            "ucb": bound,
                            "covered": _cover(actual, bound),
                            "width": (
                                float(bound) - float(actual)
                                if actual is not None and bound is not None
                                else float("nan")
                            ),
                        })
        d_on = by_method["raven"]
        d_off = by_method["raven_wo_design"]
        a_high = float(d_on["active_set_mismatch_rate"] or 0) >= 0.25
        pred_harm = (
            np.isfinite(d_on["RMSE_mu"]) and np.isfinite(d_off["RMSE_mu"])
            and float(d_on["RMSE_mu"]) > float(d_off["RMSE_mu"]) + 1e-6
        )
        group_harm = (
            np.isfinite(d_on["Delta_group"]) and np.isfinite(d_off["Delta_group"])
            and float(d_on["Delta_group"]) > float(d_off["Delta_group"]) + 1e-6
        )
        unsafe = bool(a_high or pred_harm or group_harm)
        if dataset == "uair":
            uair_unsafe = unsafe
        unsafe_rows.append({
            "dataset": dataset,
            "active_set_mismatch_rate_AlwaysD": d_on["active_set_mismatch_rate"],
            "RMSE_AlwaysD": d_on["RMSE_mu"],
            "RMSE_NoD": d_off["RMSE_mu"],
            "WorstGroupRMSE_AlwaysD": d_on["WorstGroupRMSE"],
            "WorstGroupRMSE_NoD": d_off["WorstGroupRMSE"],
            "Delta_group_AlwaysD": d_on["Delta_group"],
            "Delta_group_NoD": d_off["Delta_group"],
            "Delta_cs_AlwaysD": d_on["Delta_cs"],
            "Delta_cs_NoD": d_off["Delta_cs"],
            "criterion_A_mismatch_high": int(a_high),
            "criterion_B_prediction_harm": int(pred_harm),
            "criterion_C_group_alignment_harm": int(group_harm),
            "unsafe_candidate": int(unsafe),
        })

    pd.DataFrame(unsafe_rows).to_csv(out / "unsafe_audit" / "UAIR_UNSAFE_REAUDIT.csv", index=False)
    _write_a8b(out, tightness)
    _write_natural_blocks(out, cal_all, prepared_by)

    if not uair_unsafe:
        (out / "unsafe_audit" / "PRE_REGISTERED_SUPPORT_STRESS_PLAN.md").write_text(
            """# Pre-registered support-stress plan (not executed)

Main line: opportunity-support thinning on sealed EventTrace.

- Keep TARGET_LAW_RULE_V1 and frozen tau_*.
- Thin current-window opportunity events independently of Y / residuals / RMSE.
- Freeze a single thinning level before running.
- Do not sweep multiple stress levels in this development round.
- Do not execute in R1d.
""",
            encoding="utf-8",
        )

    sag_ran = False
    if uair_unsafe or any(int(r["unsafe_candidate"]) for r in unsafe_rows):
        sag_allowed = True
    # Instruction: SAG only if legal safe/unsafe contrast exists.
    if sag_allowed:
        for dataset, prepared in prepared_by.items():
            runner, logs, window_metrics, _ = _run_one(
                prepared=prepared, method="raven_sag", thresholds=thresholds,
                pi_safe=pi_safe_docs[dataset], cov_mode="dynamic_max_residual",
            )
            sag_ran = True
            pred = _remap_pred_groups(
                _predict(runner, prepared["dataset"], split="test"),
                prepared["paper_h_by_unit"],
            )
            mu_w = _mu_weights_for_test(pred, np.asarray(prepared["paper_mu"]))
            rmse = float(rmse_mu(pred["y_pred"], pred["y_true"], mu_w)) if len(mu_w) else float("nan")
            worst = _worst_group_rmse(pred, mu_w)
            on = [r for r in logs if int(r.get("G_r", 0)) == 1]
            method_rows.append({
                "dataset": dataset,
                "method": "raven_sag",
                "RMSE_mu": rmse,
                "WorstGroupRMSE": worst,
                "Gate_ON_rate": (len(on) / len(logs)) if logs else 0.0,
                "n_ON": len(on),
                "n_windows": len(logs),
            })
            for row in logs:
                flat = _flatten_log(row, dataset=dataset, seed=30001, method="raven_sag")
                feat = row.get("gate_features") or {}
                flags = _condition_flags(row)
                flat.update({
                    "C_cov_LCB": feat.get("C_cov_LCB"),
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
                })
                gate_rows.append(flat)

    pd.DataFrame(method_rows).to_csv(out / "diagnostic" / "R1D_METHOD_DIAGNOSTIC.csv", index=False)
    if gate_rows:
        pd.DataFrame(gate_rows).to_csv(out / "diagnostic" / "R1D_GATE_WINDOW_LOG.csv", index=False)
        _write_passrate(out, gate_rows)

    dump_json(
        {
            "mode": "g1_r1d_1seed",
            "git_commit": _git_hash(),
            "g0_config_hash": g0.get("config", {}).get("config_hash"),
            "threshold_hash": sha256_file(root / "configs/sag_g0/thresholds.json"),
            "tau_unchanged": True,
            "target_rule": rule,
            "pi_safe": pi_safe_docs,
            "dynamic_cov": dyn_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        out / "configs" / "config_r1d.json",
    )
    verdict = write_r1d_report(out, sag_ran=sag_ran, uair_unsafe=uair_unsafe)
    return {"output_dir": str(out), "verdict": verdict}


def _write_passrate(out: Path, gate_rows: list[dict[str, Any]]) -> None:
    sag = pd.DataFrame(gate_rows)
    sag = sag[sag["method"] == "raven_sag"] if "method" in sag.columns else sag
    rows = []
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
        rec["Gate_ON_rate"] = float((sub["G_r"] == 1).mean()) if "G_r" in sub.columns and len(sub) else float("nan")
        rec["first_fail"] = json.dumps(
            sub["fallback_reason"].fillna("ON").value_counts().to_dict()
        ) if "fallback_reason" in sub.columns and len(sub) else "{}"
        rows.append(rec)
    pd.DataFrame(rows).to_csv(out / "diagnostic" / "R1D_GATE_PASSRATE.csv", index=False)


def _write_a8b(out: Path, tightness: list[dict[str, Any]]) -> None:
    rows = []
    widths = []
    for dataset in DATASETS:
        sub = [r for r in tightness if r["dataset"] == dataset]
        rec: dict[str, Any] = {"dataset": dataset, "coverage_target": 0.95}
        wrec: dict[str, Any] = {"dataset": dataset}
        by_win: dict[Any, dict[str, Any]] = {}
        for row in sub:
            by_win.setdefault(row["window_id"], {})[row["metric"]] = row
        joint = []
        for mets in by_win.values():
            if set(mets) >= {"beta", "M", "V"}:
                flags = [mets[m].get("covered") for m in ("beta", "M", "V")]
                if all(f is not None for f in flags):
                    joint.append(int(all(float(f) > 0.5 for f in flags)))
        rec["n_common_nonempty"] = len(by_win)
        rec["cover_joint"] = float(np.mean(joint)) if joint else float("nan")
        for metric in ("beta", "M", "V"):
            rows_m = [r for r in sub if r["metric"] == metric]
            covers = [float(r["covered"]) for r in rows_m if r["covered"] is not None]
            wds = [float(r["width"]) for r in rows_m if np.isfinite(float(r.get("width", math.nan)))]
            rec[f"cover_{metric}"] = float(np.mean(covers)) if covers else float("nan")
            wrec[f"width_{metric}_mean"] = float(np.mean(wds)) if wds else float("nan")
        rows.append(rec)
        widths.append(wrec)
    pd.DataFrame(rows).to_csv(out / "a8b" / "A8B_COVERAGE_R1D.csv", index=False)
    pd.DataFrame(widths).to_csv(out / "a8b" / "A8B_WIDTH_R1D.csv", index=False)


def _write_natural_blocks(
    out: Path,
    cal_all: list[dict[str, Any]],
    prepared_by: dict[str, dict[str, Any]],
) -> None:
    cal = pd.DataFrame(cal_all)
    rows = []
    if cal.empty:
        pd.DataFrame(rows).to_csv(out / "unsafe_audit" / "NATURAL_UNSAFE_BLOCK_CANDIDATES.csv", index=False)
        return
    for dataset in DATASETS:
        sub = cal[cal["dataset"] == dataset].copy() if "dataset" in cal.columns else cal
        if sub.empty:
            continue
        n = len(sub)
        block = max(8, n // 5)
        for b, start in enumerate(range(0, n, block)):
            chunk = sub.iloc[start:start + block]
            if chunk.empty:
                continue
            overlap = pd.to_numeric(chunk.get("realized_target_support_mass"), errors="coerce")
            c_cov = pd.to_numeric(chunk.get("C_cov_LCB"), errors="coerce")
            rows.append({
                "dataset": dataset,
                "block_id": f"{dataset}_w{int(chunk['window_id'].min())}-{int(chunk['window_id'].max())}",
                "time_range": f"{int(chunk['window_id'].min())}-{int(chunk['window_id'].max())}",
                "target_support_mass": float(c_cov.mean()) if c_cov.notna().any() else float("nan"),
                "opportunity_support_mass": float(overlap.mean()) if overlap.notna().any() else float("nan"),
                "overlap": float(overlap.mean()) if overlap.notna().any() else float("nan"),
                "active_set_mismatch": float("nan"),
                "ESS": float("nan"),
                "clipping": float("nan"),
                "performance_based_selection": 0,
            })
    pd.DataFrame(rows).to_csv(out / "unsafe_audit" / "NATURAL_UNSAFE_BLOCK_CANDIDATES.csv", index=False)


def write_r1d_report(out: Path, *, sag_ran: bool = False, uair_unsafe: bool | None = None) -> dict[str, Any]:
    out = Path(out)
    rule = json.loads((out / "target" / "TARGET_LAW_RULE_FROZEN.json").read_text(encoding="utf-8"))
    compat = pd.read_csv(out / "target" / "TARGET_COMPATIBILITY_R1D.csv")
    cmp = pd.read_csv(out / "target" / "TARGET_LAW_R1C_VS_R1D.csv")
    cal = pd.read_csv(out / "dynamic_cov" / "DYNAMIC_COV_CALIBRATION.csv")
    cfg = json.loads((out / "configs" / "dynamic_cov_config.json").read_text(encoding="utf-8"))
    max_err = float(compat["abs_error"].max()) if len(compat) else float("nan")

    def cov_sum(dataset: str) -> dict[str, float]:
        sub = cal[cal["dataset"] == dataset] if "dataset" in cal.columns else cal
        warm = sub[pd.to_numeric(sub.get("cold_start"), errors="coerce").fillna(1) == 0]
        return {
            "pairwise": float(pd.to_numeric(warm["pairwise_coverage"], errors="coerce").mean()) if len(warm) else float("nan"),
            "mass": float(pd.to_numeric(warm["target_mass_weighted_coverage"], errors="coerce").mean()) if len(warm) else float("nan"),
            "joint": float(pd.to_numeric(warm["joint_window_coverage"], errors="coerce").mean()) if len(warm) else float("nan"),
            "c_cov": float(pd.to_numeric(warm["C_cov_LCB"], errors="coerce").mean()) if len(warm) else float("nan"),
            "n_warm": int(len(warm)),
        }

    ss_c, ua_c = cov_sum("sensorscope"), cov_sum("uair")
    existing = {}
    vpath = out / "R1D_VERDICT.json"
    if vpath.is_file():
        existing = json.loads(vpath.read_text(encoding="utf-8"))
    dyn = existing.get("dynamic_cov") or {}
    status_ss = (dyn.get("sensorscope") or {}).get("status", "")
    status_ua = (dyn.get("uair") or {}).get("status", "")

    unsafe_path = out / "unsafe_audit" / "UAIR_UNSAFE_REAUDIT.csv"
    unsafe = pd.read_csv(unsafe_path) if unsafe_path.is_file() else pd.DataFrame()
    ua_row: dict[str, Any] = {}
    ss_row: dict[str, Any] = {}
    if not unsafe.empty and "dataset" in unsafe.columns:
        ua_hit = unsafe[unsafe["dataset"] == "uair"]
        ss_hit = unsafe[unsafe["dataset"] == "sensorscope"]
        if len(ua_hit):
            ua_row = ua_hit.iloc[0].to_dict()
        if len(ss_hit):
            ss_row = ss_hit.iloc[0].to_dict()

    passrate_path = out / "diagnostic" / "R1D_GATE_PASSRATE.csv"
    passrate = pd.read_csv(passrate_path) if passrate_path.is_file() else pd.DataFrame()
    a8b_path = out / "a8b" / "A8B_COVERAGE_R1D.csv"
    a8b = pd.read_csv(a8b_path) if a8b_path.is_file() else pd.DataFrame()
    joint_ss = float(a8b.loc[a8b["dataset"] == "sensorscope", "cover_joint"].iloc[0]) if len(a8b) and "dataset" in a8b.columns else float("nan")
    a8b_note = "A8B_NOT_FINAL_CLOSED" if (not np.isfinite(joint_ss) or joint_ss < 0.95) else "A8b joint at or above 0.95 (development)"

    if existing.get("executive_verdict") in {
        "DYNAMIC_COV_NOT_CALIBRATED",
        "DYNAMIC_COV_TOO_CONSERVATIVE",
        "TARGET_SEMANTICS_NOT_FROZEN",
    }:
        verdict = existing["executive_verdict"]
    elif ua_row and int(ua_row.get("unsafe_candidate") or 0) == 0:
        verdict = "U_AIR_NO_LONGER_UNSAFE_UNDER_CORRECT_TARGET"
    elif sag_ran:
        verdict = "NEED_NATURAL_UNSAFE_BLOCK_AUDIT"
    else:
        verdict = "NEED_NATURAL_UNSAFE_BLOCK_AUDIT"

    gate_table = "SAG was not run."
    if len(passrate):
        lines = ["Dataset | Ccov | Cret | CESS | Cclip | deltaA | Btot | ALL | ON", "---|---|---|---|---|---|---|---|---"]
        for _, r in passrate.iterrows():
            lines.append(
                f"{r['dataset']} | {r.get('pass_rate_C_cov')} | {r.get('pass_rate_C_ret')} | "
                f"{r.get('pass_rate_C_ESS')} | {r.get('pass_rate_C_clip')} | {r.get('pass_rate_delta_A')} | "
                f"{r.get('pass_rate_B_tot')} | {r.get('pass_rate_ALL')} | {r.get('Gate_ON_RATE', r.get('Gate_ON_rate'))}"
            )
        gate_table = "\n".join(lines)

    report = f"""# 1. Executive Verdict

{verdict}

R1d is a 1-seed target-semantics + dynamic C_cov audit. Frozen `tau_*` were not changed. 5-seed was not started.

# 2. Target Semantics

Deployment population: public evaluation/deployment-supported atoms (test split, `support_flag`).
`μ_g` is frozen train-split TOD occupancy (manuscript). Atomic `ϖ_i = μ_{{h(i)}} / n_{{I_dep,h(i)}}`.
`π^{{tar}}` is the client×stratum pushforward of the same `ϖ` with frozen station→client `ξ`.
Test outcomes are not used. max compatibility error = {max_err} (atol={COMPAT_ATOL}).

R1c vs R1d is a semantic comparison only (`TARGET_LAW_R1C_VS_R1D.csv`).

# 3. Dynamic Opportunity Model

Predictor: rolling mean of last L={ROLLING_L} completed window masses.
Bound: window max-residual conformal quantile, `δ={cfg.get('delta')}`.
Features are F_{{r-}} only (see DYNAMIC_COV_FEATURE_AUDIT.md). Current R is not a Gate input.

# 4. Dynamic C_cov Calibration

SensorScope warmup n={ss_c['n_warm']}: pairwise={ss_c['pairwise']} mass={ss_c['mass']} joint={ss_c['joint']} mean C_cov={ss_c['c_cov']} status={status_ss}
U-Air warmup n={ua_c['n_warm']}: pairwise={ua_c['pairwise']} mass={ua_c['mass']} joint={ua_c['joint']} mean C_cov={ua_c['c_cov']} status={status_ua}

# 5. U-Air Re-Audit

{json.dumps(ua_row, default=str) if ua_row else 'Not run (dynamic C_cov did not pass calibration, or methods not started).'}
SensorScope Always-D vs No-D: {json.dumps(ss_row, default=str) if ss_row else 'n/a'}

# 6. Gate Diagnostic

{gate_table}

# 7. A8b Status

{a8b.to_string(index=False) if len(a8b) else 'not computed'}
{a8b_note}

# 8. Scientific Interpretation

R1c pooled CP made both datasets Always-ON because it certified a static law, not P_r^{{opp}}.
R1d asks whether current-window support risk is predictable from F_{{r-}} under the frozen deployment population.
Old U-Air reversal is not treated as a verified fact under TARGET_LAW_RULE_V1.

# 9. Next Decision

Verdict {verdict}. Do not auto-start 5-seed.
"""
    (out / "R1D_TARGET_DYNAMIC_COV_REPORT.md").write_text(report, encoding="utf-8")
    payload = {
        "executive_verdict": verdict,
        "target_rule": rule,
        "max_abs_error": max_err,
        "dynamic_cov": dyn or {"sensorscope": ss_c, "uair": ua_c},
        "uair_unsafe_candidate": bool(uair_unsafe) if uair_unsafe is not None else (
            int(ua_row.get("unsafe_candidate") or 0) == 1 if ua_row else None
        ),
        "sag_ran": sag_ran,
        "a8b_note": a8b_note,
        "g1_r2_5seed_started": False,
        "r1c_vs_r1d": cmp.to_dict(orient="records"),
    }
    dump_json(payload, out / "R1D_VERDICT.json")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default="")
    args = parser.parse_args()
    result = run_r1d_main(output_dir=Path(args.output_dir) if args.output_dir else None)
    print(json.dumps({"verdict": result["verdict"]["executive_verdict"], "output_dir": result["output_dir"]}, indent=2))


if __name__ == "__main__":
    main()

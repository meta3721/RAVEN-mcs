"""SAG G1-R1b 1-seed semantic alignment re-diagnostic. Does not start 5-seed."""

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
from raven_mcs.experiments.sag_runtime import METHODS, attach_paper_h, prepare_sag_bundle
from raven_mcs.metrics.accuracy import mae_mu, rmse_mu
from raven_mcs.metrics.distribution import delta_group
from raven_mcs.sag.certificates import FrozenSagThresholds, pair_key, provisional_pi_safe_from_public_opp
from raven_mcs.sag.counterfactual_audit import metrics_from_raw_states
from raven_mcs.sag.deployment_groups import N_H_GROUPS
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
DATASETS = ("sensorscope", "uair")
SEEDS = (30001,)
LOCAL_STEPS = 2
EPS = 1e-12
CONDITIONS = (
    ("C_cov_LCB", 0.05, "ge"),
    ("C_ret_LCB", 0.05, "ge"),
    ("C_ESS_LCB", 1.0, "ge"),
    ("C_clip_UCB", 0.95, "le"),
    ("delta_A_UCB", 0.35, "le"),
    ("B_tot_UCB", 4.0, "le"),
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


def _remap_pred_groups(pred: dict[str, Any], h_by_unit: dict[str, int]) -> dict[str, Any]:
    groups = np.asarray(
        [int(h_by_unit[str(uid)]) for uid in pred["unit_ids"]],
        dtype=int,
    )
    out = dict(pred)
    out["groups_fine"] = np.asarray(pred["groups"])
    out["groups"] = groups
    return out


def _condition_flags(row: dict[str, Any]) -> dict[str, bool]:
    passed = row.get("gate_passed") or {}
    if isinstance(passed, dict) and passed:
        return {
            "C_cov": bool(passed.get("C_cov_LCB", False)),
            "C_ret": bool(passed.get("C_ret_LCB", False)),
            "C_ESS": bool(passed.get("C_ESS_LCB", False)),
            "C_clip": bool(passed.get("C_clip_UCB", False)),
            "delta_A": bool(passed.get("delta_A_UCB", False)),
            "B_tot": bool(passed.get("B_tot_UCB", False)),
        }
    feat = row.get("gate_features") or {}
    flags = {}
    for col, thresh, side in CONDITIONS:
        try:
            val = float(feat.get(col))
            flags[{
                "C_cov_LCB": "C_cov",
                "C_ret_LCB": "C_ret",
                "C_ESS_LCB": "C_ESS",
                "C_clip_UCB": "C_clip",
                "delta_A_UCB": "delta_A",
                "B_tot_UCB": "B_tot",
            }[col]] = (val >= thresh) if side == "ge" else (val <= thresh)
        except (TypeError, ValueError):
            flags[{
                "C_cov_LCB": "C_cov",
                "C_ret_LCB": "C_ret",
                "C_ESS_LCB": "C_ESS",
                "C_clip_UCB": "C_clip",
                "delta_A_UCB": "delta_A",
                "B_tot_UCB": "B_tot",
            }[col]] = False
    return flags


def run_r1b_main(*, root: Path = ROOT, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root)
    g0 = _require_g0_full_pass(root)
    out = Path(output_dir or (root / "outputs" / "sag_g1_r1b"))
    for sub in (
        "audit",
        "opportunity",
        "safety",
        "diagnostic",
        "configs/deployment_group_map",
        "tests",
    ):
        (out / sub).mkdir(parents=True, exist_ok=True)

    thresholds = _load_thresholds()
    shutil.copy2(root / "configs/sag_g0/thresholds.json", out / "configs" / "thresholds_frozen_copy.json")

    gate_rows: list[dict[str, Any]] = []
    method_rows: list[dict[str, Any]] = []
    cov_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    count_rows: list[dict[str, Any]] = []
    mass_rows: list[dict[str, Any]] = []
    btot_rows: list[dict[str, Any]] = []
    old_vs: list[dict[str, Any]] = []
    recompute_rows: list[dict[str, Any]] = []
    ess_rows: list[dict[str, Any]] = []
    map_comp: list[dict[str, Any]] = []
    pi_safe_docs: dict[str, Any] = {}
    raw_lines: list[str] = []

    old_gate_path = root / "outputs" / "sag_g1_r1" / "diagnostic" / "R1_GATE_WINDOW_LOG.csv"
    old_gate = pd.read_csv(old_gate_path) if old_gate_path.is_file() else pd.DataFrame()

    for dataset in DATASETS:
        for seed in SEEDS:
            prepared = attach_paper_h(
                prepare_sag_bundle(root=root, dataset=dataset, seed=int(seed)),
                root=root,
            )
            src_map = root / prepared["paper_h"]["path"]
            shutil.copy2(src_map, out / "configs" / "deployment_group_map" / src_map.name)
            map_comp.append({
                "dataset": dataset,
                "G_size_old": int(prepared["n_groups_runtime_fine"]),
                "G_size_new": int(prepared["paper_n_groups"]),
                "source_old": "E3 spatial×time n_groups_runtime",
                "source_new": prepared["paper_h"]["source"],
                "map_hash": prepared["paper_h"]["map_hash"],
                "mu_new": json.dumps(prepared["paper_h"]["mu"]),
                "uses_labels": False,
                "uses_test": False,
            })
            pi_doc = provisional_pi_safe_from_public_opp(
                prepared["pi_target"], prepared["pi_opp_joint"], quantile=0.10,
            )
            pi_safe_docs[dataset] = {
                "rule": "q10 of public pi_opp_joint on {pi_tar>0} pairs (R1 provisional, not reselected)",
                "source": pi_doc["source"],
                "fitted_on": "public_pi_opp_joint × pi_target support; no labels, no test Y, no ON/OFF",
                "uses_labels": False,
                "uses_test": False,
                "value": float(pi_doc["pi_safe"]),
                "status": "PROVISIONAL_REQUIRES_LATER_FREEZE",
                "candidates": pi_doc.get("candidates"),
                "n_positive_target_pairs": pi_doc.get("n_positive_target_pairs"),
            }
            pi_safe = float(pi_doc["pi_safe"])
            sag_logs = None
            sag_runner = None
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
                    "WorstGroup_space": "paper_h_4_utc_tod",
                    "Delta_group": d_g,
                    "Delta_cs": pair_summary.get("Delta_c_s"),
                    "Gate_ON_rate": (len(on) / len(logs)) if logs else 0.0,
                    "n_windows": len(logs),
                    "n_ON": len(on),
                    "n_OFF": len(off),
                    "n_groups": N_H_GROUPS,
                })
                for row in logs:
                    flat = _flatten_log(row, dataset=dataset, seed=int(seed), method=method)
                    diag = _diag(row)
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
                        "n_groups": N_H_GROUPS,
                        "old_realized_C_cov": row.get("old_realized_C_cov", row.get("realized_C_cov")),
                        "B_srv_UCB": feat.get("B_srv_UCB", diag.get("B_srv_UCB")),
                        "service_diff_l1": row.get("service_diff_l1", row.get("service_diff")),
                        "opp_event_total": row.get("opp_event_total"),
                    })
                    for key in (
                        "B_M_pre", "B_Q", "Delta_beta_UCB", "Delta_M_UCB", "Delta_V_UCB",
                        "D_alpha_UCB", "B_srv_UCB", "active_set_term", "cal_failure_term",
                        "target_mass_certified", "number_target_positive_pairs", "pi_safe",
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
                raw_lines.append(json.dumps(rec, ensure_ascii=False, default=str))
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
                    "n_groups": int(np.asarray(raw.get("M_D")).shape[0]) if raw.get("M_D") is not None else None,
                    "Delta_beta_logged": logged.get("Delta_beta"),
                    "Delta_beta_recomputed": mets.get("Delta_beta"),
                    "Delta_M_logged": logged.get("Delta_M"),
                    "Delta_M_recomputed": mets.get("Delta_M"),
                    "Delta_V_logged": logged.get("Delta_V"),
                    "Delta_V_recomputed": mets.get("Delta_V"),
                    "service_diff_logged": logged.get("service_diff"),
                    "service_diff_l1_recomputed": mets.get("service_diff_l1"),
                })
                for item in raw.get("ess_clients") or []:
                    ess_rows.append({
                        "dataset": dataset,
                        "seed": int(seed),
                        "window": raw.get("window_id"),
                        **item,
                    })

            for row in sag_logs:
                feat = row.get("gate_features") or {}
                diag = _diag(row)
                flags = _condition_flags(row)
                cov_rows.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "window_id": row.get("window_id"),
                    "G_r": row.get("G_r"),
                    "fallback_reason": row.get("fallback_reason"),
                    "pi_safe": diag.get("pi_safe", pi_safe),
                    "C_cov_LCB": feat.get("C_cov_LCB"),
                    "old_realized_C_cov": row.get("old_realized_C_cov", row.get("realized_C_cov")),
                    "target_mass_certified": diag.get("target_mass_certified"),
                    "opp_event_total": row.get("opp_event_total"),
                    "cold_start": feat.get("cold_start"),
                    "pass_ALL": int(all(flags.values())),
                })
                counts = row.get("opp_count_by_pair") or {}
                masses = row.get("opp_mass_by_pair") or {}
                for key, n_evt in counts.items():
                    client, stratum = pair_key(key)
                    count_rows.append({
                        "dataset": dataset,
                        "seed": int(seed),
                        "window_id": row.get("window_id"),
                        "client": client,
                        "stratum": stratum,
                        "N_opp": n_evt,
                    })
                    mass_rows.append({
                        "dataset": dataset,
                        "seed": int(seed),
                        "window_id": row.get("window_id"),
                        "client": client,
                        "stratum": stratum,
                        "N_opp": n_evt,
                        "pi_hat_opp_window": masses.get(key),
                        "pi_tar": prepared["pi_target"].get((client, stratum), 0.0),
                    })
                for fail in (diag.get("top_failures") or [])[:10]:
                    pair_rows.append({
                        "dataset": dataset,
                        "seed": int(seed),
                        "window_id": row.get("window_id"),
                        "client": fail.get("client"),
                        "stratum": fail.get("stratum"),
                        "pi_tar": fail.get("pi_tar"),
                        "pi_hat_opp": fail.get("pi_hat_opp"),
                        "lower_pi_opp": fail.get("lower_pi_opp"),
                        "certified": int(float(fail.get("lower_pi_opp") or 0) >= float(pi_safe)),
                    })
                btot_rows.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "window_id": row.get("window_id"),
                    "n_groups": N_H_GROUPS,
                    "B_M_pre": diag.get("B_M_pre"),
                    "Delta_beta_UCB": feat.get("Delta_beta_UCB", diag.get("Delta_beta_UCB")),
                    "Delta_M_UCB": feat.get("Delta_M_UCB", diag.get("Delta_M_UCB")),
                    "Delta_V_UCB": feat.get("Delta_V_UCB", diag.get("Delta_V_UCB")),
                    "D_alpha_UCB": diag.get("D_alpha_UCB"),
                    "B_srv_UCB": feat.get("B_srv_UCB", diag.get("B_srv_UCB")),
                    "active_set_term": diag.get("active_set_term"),
                    "cal_failure_term": diag.get("cal_failure_term"),
                    "B_tot_UCB": feat.get("B_tot_UCB"),
                    "delta_A_UCB": feat.get("delta_A_UCB"),
                    "cold_start": feat.get("cold_start"),
                })
                old_match = old_gate
                if not old_gate.empty:
                    old_match = old_gate[
                        (old_gate["dataset"] == dataset)
                        & (old_gate["seed"] == int(seed))
                        & (old_gate["method"] == "raven_sag")
                        & (old_gate["window_id"] == int(row.get("window_id")))
                    ]
                old_row = old_match.iloc[0].to_dict() if len(old_match) else {}
                b_old = old_row.get("B_tot_UCB")
                b_new = feat.get("B_tot_UCB")
                srv_old = old_row.get("B_srv_UCB")
                srv_new = feat.get("B_srv_UCB", diag.get("B_srv_UCB"))
                old_vs.append({
                    "dataset": dataset,
                    "seed": int(seed),
                    "window": row.get("window_id"),
                    "G_size_old": int(prepared["n_groups_runtime_fine"]),
                    "G_size_new": N_H_GROUPS,
                    "B_srv_old": srv_old,
                    "B_srv_new": srv_new,
                    "B_tot_old": b_old,
                    "B_tot_new": b_new,
                    "delta_A_UCB": feat.get("delta_A_UCB"),
                    "tau_safe": 4.0,
                    "pass_Btot_old": (
                        int(float(b_old) <= 4.0)
                        if b_old is not None and np.isfinite(float(b_old))
                        else None
                    ),
                    "pass_Btot_new": (
                        int(float(b_new) <= 4.0)
                        if b_new is not None and np.isfinite(float(b_new))
                        else None
                    ),
                })

    pd.DataFrame(gate_rows).to_csv(out / "diagnostic" / "R1B_GATE_WINDOW_LOG.csv", index=False)
    pd.DataFrame(method_rows).to_csv(out / "diagnostic" / "R1B_METHOD_DIAGNOSTIC.csv", index=False)
    pd.DataFrame(cov_rows).to_csv(out / "opportunity" / "C_COV_EVENT_MASS_WINDOW.csv", index=False)
    pd.DataFrame(pair_rows).to_csv(out / "opportunity" / "C_COV_PAIR_DIAGNOSTIC.csv", index=False)
    pd.DataFrame(count_rows).to_csv(out / "opportunity" / "OPPORTUNITY_EVENT_COUNT_WINDOW.csv", index=False)
    pd.DataFrame(mass_rows).to_csv(out / "opportunity" / "OPPORTUNITY_EVENT_MASS_WINDOW.csv", index=False)
    pd.DataFrame(btot_rows).to_csv(out / "safety" / "B_TOT_DECOMPOSITION_R1B.csv", index=False)
    pd.DataFrame(old_vs).to_csv(out / "safety" / "B_TOT_OLD_VS_R1B.csv", index=False)
    pd.DataFrame(recompute_rows).to_csv(out / "audit" / "COUNTERFACTUAL_METRIC_REGRESSION.csv", index=False)
    pd.DataFrame(ess_rows).to_csv(out / "audit" / "ESS_VARIANCE_COUNTERFACTUAL_AUDIT.csv", index=False)
    pd.DataFrame(map_comp).to_csv(out / "audit" / "GROUP_MAPPING_COMPARISON.csv", index=False)
    (out / "audit" / "COUNTERFACTUAL_RAW_STATE.jsonl").write_text(
        "\n".join(raw_lines) + ("\n" if raw_lines else ""), encoding="utf-8",
    )

    pi_out = {
        "rule": "q10 of public pi_opp_joint on {pi_tar>0} (R1 provisional reused)",
        "source": "provisional_pi_safe_from_public_opp",
        "fitted_on": "public opportunity joint × target-positive pairs",
        "uses_labels": False,
        "uses_test": False,
        "value_SensorScope": pi_safe_docs["sensorscope"]["value"],
        "value_UAir": pi_safe_docs["uair"]["value"],
        "status": "PROVISIONAL_REQUIRES_LATER_FREEZE",
        "per_dataset": pi_safe_docs,
    }
    dump_json(pi_out, out / "opportunity" / "PI_SAFE_PROVENANCE.json")

    pass_rows = []
    sag = pd.DataFrame(gate_rows)
    sag = sag[sag["method"] == "raven_sag"] if "method" in sag.columns else sag
    for dataset in DATASETS:
        sub = sag[sag["dataset"] == dataset] if "dataset" in sag.columns else sag
        rec = {"dataset": dataset, "seed": 30001, "n": int(len(sub))}
        for name in ("C_cov", "C_ret", "C_ESS", "C_clip", "delta_A", "B_tot", "ALL"):
            col = f"pass_{name}" if name != "ALL" else "pass_ALL"
            if col in sub.columns and len(sub):
                rec[f"pass_rate_{name}"] = float(pd.to_numeric(sub[col], errors="coerce").mean())
            else:
                rec[f"pass_rate_{name}"] = float("nan")
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
    pd.DataFrame(pass_rows).to_csv(out / "diagnostic" / "R1B_GATE_PASSRATE.csv", index=False)

    config = {
        "mode": "g1_r1b_1seed",
        "datasets": list(DATASETS),
        "seeds": list(SEEDS),
        "methods": list(METHODS),
        "local_steps": LOCAL_STEPS,
        "git_commit": _git_hash(),
        "g0_config_hash": g0.get("config", {}).get("config_hash"),
        "threshold_hash": sha256_file(root / "configs/sag_g0/thresholds.json"),
        "tau_unchanged": True,
        "paper_n_groups": N_H_GROUPS,
        "pi_safe": pi_out,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(config, out / "configs" / "config_r1b.json")
    verdict = write_r1b_report(out)
    return {"output_dir": str(out), "config": config, "verdict": verdict}


def write_r1b_report(out: Path) -> dict[str, Any]:
    out = Path(out)
    gate = pd.read_csv(out / "diagnostic" / "R1B_GATE_WINDOW_LOG.csv")
    methods = pd.read_csv(out / "diagnostic" / "R1B_METHOD_DIAGNOSTIC.csv")
    passrate = pd.read_csv(out / "diagnostic" / "R1B_GATE_PASSRATE.csv")
    btot = pd.read_csv(out / "safety" / "B_TOT_DECOMPOSITION_R1B.csv")
    oldvs = pd.read_csv(out / "safety" / "B_TOT_OLD_VS_R1B.csv")
    ess = pd.read_csv(out / "audit" / "ESS_VARIANCE_COUNTERFACTUAL_AUDIT.csv")
    recon = pd.read_csv(out / "audit" / "COUNTERFACTUAL_METRIC_REGRESSION.csv")
    mmap = pd.read_csv(out / "audit" / "GROUP_MAPPING_COMPARISON.csv")
    cov = pd.read_csv(out / "opportunity" / "C_COV_EVENT_MASS_WINDOW.csv")
    masses = pd.read_csv(out / "opportunity" / "OPPORTUNITY_EVENT_MASS_WINDOW.csv")
    pi_doc = json.loads((out / "opportunity" / "PI_SAFE_PROVENANCE.json").read_text(encoding="utf-8"))

    sag = gate[gate["method"] == "raven_sag"].copy() if "method" in gate.columns else gate
    ss = sag[sag["dataset"] == "sensorscope"] if "dataset" in sag.columns else sag
    ua = sag[sag["dataset"] == "uair"] if "dataset" in sag.columns else sag

    def rates(frame: pd.DataFrame) -> dict[str, Any]:
        outd = {"n": int(len(frame)), "on": int((frame["G_r"] == 1).sum()) if "G_r" in frame.columns else 0}
        outd["on_rate"] = float(outd["on"] / outd["n"]) if outd["n"] else 0.0
        for name in ("C_cov", "C_ret", "C_ESS", "C_clip", "delta_A", "B_tot", "ALL"):
            col = f"pass_{name}" if name != "ALL" else "pass_ALL"
            outd[name] = float(pd.to_numeric(frame[col], errors="coerce").mean()) if col in frame.columns and len(frame) else float("nan")
        outd["reasons"] = frame["fallback_reason"].fillna("ON").value_counts().to_dict() if "fallback_reason" in frame.columns else {}
        return outd

    ss_s, ua_s = rates(ss), rates(ua)
    recon_ok = True
    if not recon.empty:
        for _, row in recon.iterrows():
            for a, b in (
                ("Delta_beta_logged", "Delta_beta_recomputed"),
                ("Delta_M_logged", "Delta_M_recomputed"),
                ("Delta_V_logged", "Delta_V_recomputed"),
            ):
                try:
                    if abs(float(row[a]) - float(row[b])) > 1e-6:
                        recon_ok = False
                except (TypeError, ValueError):
                    if pd.notna(row.get(a)) or pd.notna(row.get(b)):
                        recon_ok = False

    zeta0 = float((ess["zeta_std"] == 0).mean()) if len(ess) and "zeta_std" in ess.columns else float("nan")
    neff_eq = float((ess["abs_neff_diff"] <= 1e-12).mean()) if len(ess) and "abs_neff_diff" in ess.columns else float("nan")
    dv0 = float((pd.to_numeric(sag["Delta_V"], errors="coerce").fillna(0).abs() <= 1e-12).mean()) if "Delta_V" in sag.columns and len(sag) else float("nan")

    example = ""
    if not masses.empty:
        pick = masses[(masses["dataset"] == "sensorscope") & (masses["window_id"] == masses["window_id"].min())]
        top = pick.sort_values("N_opp", ascending=False).head(10)
        example = top.to_string(index=False)

    ss_on = ss_s["on"]
    ua_delta = ua_s.get("delta_A", float("nan"))
    btot_ss = pd.to_numeric(btot[btot["dataset"] == "sensorscope"]["B_tot_UCB"], errors="coerce") if "dataset" in btot.columns else pd.Series(dtype=float)
    med_btot_ss = float(btot_ss.median()) if len(btot_ss.dropna()) else float("nan")

    h_ok = bool((mmap["G_size_new"] == 4).all()) if len(mmap) else False
    mass_not_uniform = True
    if not masses.empty:
        # A window with two pairs should not be 0.5/0.5 if counts differ.
        grouped = masses.groupby(["dataset", "window_id"])
        for _, g in grouped:
            if len(g) >= 2 and g["N_opp"].nunique() > 1:
                if abs(float(g["pi_hat_opp_window"].iloc[0]) - 1.0 / len(g)) < 1e-12:
                    mass_not_uniform = False
                    break

    if not h_ok:
        verdict = "H_MAPPING_NOT_FROZEN"
    elif not recon_ok:
        verdict = "NEEDS_MORE_SEMANTIC_REPAIR"
    elif ss_on > 0 and ua_delta < 0.5:
        verdict = "READY_FOR_G1_R2_5SEED"
    elif ss_on == 0 and med_btot_ss > 4.0:
        verdict = "STRUCTURAL_CERTIFICATE_TOO_CONSERVATIVE_CONFIRMED"
    elif ss_on == 0:
        verdict = "STRUCTURAL_CERTIFICATE_TOO_CONSERVATIVE_CONFIRMED"
    else:
        verdict = "NEEDS_MORE_SEMANTIC_REPAIR"

    def bsum(frame: pd.DataFrame) -> str:
        if frame.empty:
            return "n/a"
        cols = ["Delta_beta_UCB", "Delta_M_UCB", "Delta_V_UCB", "B_srv_UCB", "active_set_term", "cal_failure_term", "B_tot_UCB"]
        lines = []
        for col in cols:
            if col not in frame.columns:
                continue
            xs = pd.to_numeric(frame[col], errors="coerce").dropna()
            if xs.empty:
                continue
            lines.append(f"  {col}: median={xs.median():.4g} p95={xs.quantile(0.95):.4g}")
        return "\n".join(lines)

    report = f"""# 1. Executive Verdict

{verdict}

R1b is a 1-seed semantic alignment diagnostic (SensorScope 30001, U-Air 30001). Frozen `tau_*` were not changed. 5-seed was not started.

# 2. Deployment-Group Mapping Audit

Paper `h(i)` is the four UTC time-of-day deployment groups (H1:00–06 … H4:18–24), train-split mass, no test labels. `s(i)` remains the sealed opportunity stratum.

SensorScope |G| new = 4 (old runtime {int(mmap.loc[mmap['dataset']=='sensorscope','G_size_old'].iloc[0]) if len(mmap) else 'NA'}).
U-Air |G| new = 4 (old runtime {int(mmap.loc[mmap['dataset']=='uair','G_size_old'].iloc[0]) if len(mmap) else 'NA'}).

220/144 came from E3 spatial×time `n_groups_runtime` with `use_coarse_time_groups=False`. That is not paper `h(i)`. R1b uses `RepeatableTimeOfDayMapper` on public `absolute_time`.

μ / M / Δ_group now live in this 4-block space. WorstGroupRMSE in this diagnostic uses the same paper `h(i)` (G2 definition). `Δ_{{c-s}}` still uses `s(i)`.

# 3. Opportunity-Event Mass Repair

Old R1 `window_opportunity_masses` unique-pair-uniformized completed-window pairs. New code counts opportunity events (risk-set units) then normalizes. Unique-pair uniform is isolated as `pair_presence_distribution` and is not a Gate input.

Concrete SensorScope window (first window present in the mass table), top-10 (k,s) by event count:

```
{example}
```

# 4. C_cov

C_cov is target-mass weighted EB LCB on lagged completed-window event-mass `π^opp`. Current R is not an input to `compute_certificates`.

pi_safe rule: {pi_doc.get('rule')}; status={pi_doc.get('status')}; SS={pi_doc.get('value_SensorScope')}; U-Air={pi_doc.get('value_UAir')}. Not reselected from ON/OFF.

SensorScope C_cov pass rate = {ss_s.get('C_cov')}
U-Air C_cov pass rate = {ua_s.get('C_cov')}

# 5. ESS / Delta_V Audit

fraction(zeta_std==0) = {zeta0}
fraction(n_eff_D==n_eff_0) = {neff_eq}
fraction(|Delta_V|≈0 on logged windows) = {dv0}

If within-client ζ is constant on observed records, Hájek n_eff invariance is the expected mechanism, not a copy bug.

Counterfactual metric regression match: {recon_ok}

# 6. B_tot Recalculation

|G_new|=4. Formula unchanged: B_srv = √|G|(ΔM_UCB + B_M_pre D_α_UCB).

SensorScope:
{bsum(btot[btot['dataset']=='sensorscope']) if 'dataset' in btot.columns else 'n/a'}

U-Air:
{bsum(btot[btot['dataset']=='uair']) if 'dataset' in btot.columns else 'n/a'}

Old vs new comparison is in `safety/B_TOT_OLD_VS_R1B.csv`.

# 7. Gate Re-Diagnostic

## SensorScope 30001
pass rates: cov={ss_s.get('C_cov')} ret={ss_s.get('C_ret')} ESS={ss_s.get('C_ESS')} clip={ss_s.get('C_clip')} delta_A={ss_s.get('delta_A')} B_tot={ss_s.get('B_tot')} ALL={ss_s.get('ALL')}
ON = {ss_s.get('on')} / {ss_s.get('n')} ({ss_s.get('on_rate')})
first-fail: {ss_s.get('reasons')}

## U-Air 30001
pass rates: cov={ua_s.get('C_cov')} ret={ua_s.get('C_ret')} ESS={ua_s.get('C_ESS')} clip={ua_s.get('C_clip')} delta_A={ua_s.get('delta_A')} B_tot={ua_s.get('B_tot')} ALL={ua_s.get('ALL')}
ON = {ua_s.get('on')} / {ua_s.get('n')} ({ua_s.get('on_rate')})
first-fail: {ua_s.get('reasons')}

# 8. Scientific Boundary

SensorScope legal ON windows: {ss_on}.
U-Air delta_A pass rate: {ua_delta} (support-risk certificate should remain discriminative).

# 9. Next Decision

Verdict {verdict}. Do not auto-start 5-seed. Unique blocker, if still 0 ON, is the first-fail distribution above plus B_tot vs tau_safe=4.
"""
    (out / "R1B_SEMANTIC_REPAIR_REPORT.md").write_text(report, encoding="utf-8")
    verdict_payload = {
        "executive_verdict": verdict,
        "h_mapping_aligned": h_ok,
        "event_mass_not_unique_pair": mass_not_uniform,
        "counterfactual_recompute_matches_log": recon_ok,
        "sensorscope_gate": ss_s,
        "uair_gate": ua_s,
        "pi_safe": pi_doc,
        "g1_r2_5seed_started": False,
    }
    dump_json(verdict_payload, out / "R1B_VERDICT.json")
    return verdict_payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default="")
    args = parser.parse_args()
    out = Path(args.output_dir) if args.output_dir else None
    result = run_r1b_main(output_dir=out)
    print(json.dumps({"verdict": result["verdict"]["executive_verdict"], "output_dir": result["output_dir"]}, indent=2))


if __name__ == "__main__":
    main()

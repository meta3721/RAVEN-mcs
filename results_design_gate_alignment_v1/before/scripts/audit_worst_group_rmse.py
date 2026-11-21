#!/usr/bin/env python3
"""B1/B2 deployment-consequence follow-up (no retraining).

B1: reload checkpoints/final.pt, recompute test-set:
  - worst-group RMSE among deployment groups h(i) with n >= MIN_GROUP_N
  - p90 group RMSE (robust companion to the max)
  - high-mu group RMSE (units in groups with mu_g >= median)
  - high-mu pair RMSE (units in client x stratum pairs with pi_tar >= median)
Does NOT use Tail_RMSE as a worst-group substitute.

B2: association between Delta_c_s and RMSE_mu from stored final_metrics
    (and from recomputed RMSE_mu as a sanity check).

Does not touch sealed formal E3 artifacts except reading them.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import torch

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
from raven_mcs.e3.delta_cs_rho.delta_cs_v6 import (
    build_pi_tar_client_stratum,
    client_stratum_id,
)
from raven_mcs.e3.formal.constants import FORMAL_SEEDS
from raven_mcs.e3.formal.stats import holm, paired_summary, summarize_vector
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt
from raven_mcs.e3.target_pair.target_wiring import production_target_bundle
from raven_mcs.metrics.accuracy import rmse_mu
from raven_mcs.models.features import extract_features

MIN_GROUP_N = 5
DATASETS = ("sensorscope", "uair")
SCENARIOS = ("complete_aligned", "drifting")
METHODS = (
    "fedavg_window",
    "fedau_window",
    "obsuse_window",
    "twostage_hajek",
    "raven",
)
DISPLAY = {
    "fedavg_window": "FedAvg-Window",
    "fedau_window": "FedAU-Window",
    "obsuse_window": "ObsUse-Window",
    "twostage_hajek": "TwoStage-Hajek",
    "raven": "RAVEN-MCS",
}
OUT_DIR = _ROOT / "_paper_work" / "worst_group_results"
B1_METRICS = (
    "worst_group_rmse",
    "p90_group_rmse",
    "high_mu_group_rmse",
    "high_mu_pair_rmse",
)


def run_dir(scenario: str, dataset: str, method: str, seed: int) -> Path:
    if scenario == "drifting":
        root = _ROOT / "artifacts" / "e3_drifting_r1" / "runs"
    elif method == "fedau_window":
        root = _ROOT / "artifacts" / "e3_fedau_window_r1" / "runs"
    elif method == "obsuse_window":
        root = _ROOT / "artifacts" / "e3_obsuse_window_r1" / "runs"
    else:
        root = _ROOT / "artifacts" / "e3_formal_runs_r1" / "runs"
    return root / dataset / method / f"seed{seed}"


def _abs_hours(series: pd.Series) -> np.ndarray:
    out = []
    for ts in series.tolist():
        if hasattr(ts, "timestamp"):
            out.append(float(ts.timestamp()) / 3600.0)
        else:
            out.append(float(ts))
    return np.asarray(out, dtype=np.float64)


def build_eval_pack(dataset_name: str) -> dict:
    ds = load_paper_dataset(_ROOT, dataset_name)
    spatial_to_client = load_spatial_to_client(_ROOT, dataset_name)
    bundle = production_target_bundle(
        root=_ROOT, dataset_name=dataset_name, dataset=ds
    )
    mu = np.asarray(bundle["mu"], dtype=np.float64)
    test = ds.atomic_df[ds.atomic_df["split"] == "test"].copy()
    if test.empty:
        raise RuntimeError(f"empty test split: {dataset_name}")
    g2i = ds._target_group_str_to_int
    groups = np.asarray(
        [int(g2i.get(str(g), 0)) for g in test["target_group"].tolist()],
        dtype=int,
    )
    spatial_ids = [str(s) for s in test["spatial_id"].tolist()]
    time_indices = [int(t) for t in test["time_index"].tolist()]
    hours = _abs_hours(test["absolute_time"])
    total_slots = int(ds.atomic_df["time_index"].max()) + 1
    sp_idx, hour_t, wday_t, trend_t = extract_features(
        spatial_ids,
        hours.tolist(),
        time_indices,
        {str(k): int(v) for k, v in ds._spatial_to_idx.items()},
        total_slots,
    )
    y_true = test["target_value"].to_numpy(dtype=np.float64)
    unit_ids = [str(u) for u in test["unit_id"].tolist()]
    strata = [str(s) for s in test["opportunity_stratum"].tolist()]
    clients = [spatial_to_client.get(sid, "UNK") for sid in spatial_ids]
    pair_ids = [
        client_stratum_id(c, s) for c, s in zip(clients, strata)
    ]
    pi_tar = build_pi_tar_client_stratum(
        ds.atomic_df.copy(), spatial_to_client, split="test"
    )
    pair_mu = np.asarray([float(pi_tar.get(p, 0.0)) for p in pair_ids], dtype=np.float64)
    # mu weights identical to runner._mu_weights_for_test
    counts: dict[int, int] = {}
    for g in groups.tolist():
        counts[int(g)] = counts.get(int(g), 0) + 1
    w = np.zeros(len(groups), dtype=np.float64)
    for i, g in enumerate(groups.tolist()):
        g = int(g)
        mg = float(mu[g]) if g < len(mu) else 0.0
        w[i] = mg / max(counts[g], 1)
    s = float(w.sum())
    w = w / s if s > 0 else np.full(len(w), 1.0 / len(w))
    group_mu = mu[np.clip(groups, 0, len(mu) - 1)]
    present = np.unique(groups)
    present_mu = np.asarray([float(mu[g]) if g < len(mu) else 0.0 for g in present])
    med_g = float(np.median(present_mu[present_mu > 0])) if np.any(present_mu > 0) else 0.0
    high_g_mask = group_mu >= med_g
    pos_pair = pair_mu[pair_mu > 0]
    med_p = float(np.median(pos_pair)) if len(pos_pair) else 0.0
    high_p_mask = pair_mu >= med_p
    return {
        "dataset": ds,
        "num_spatial": int(ds.num_spatial),
        "features": (sp_idx, hour_t, wday_t, trend_t),
        "y_true": y_true,
        "groups": groups,
        "mu_w": w,
        "group_mu": group_mu,
        "high_g_mask": high_g_mask,
        "high_p_mask": high_p_mask,
        "unit_ids": unit_ids,
        "n_test": int(len(y_true)),
        "n_groups_test": int(len(present)),
        "median_group_mu": med_g,
        "median_pair_mu": med_p,
        "n_high_g": int(high_g_mask.sum()),
        "n_high_p": int(high_p_mask.sum()),
    }


def _wrmse(y_true: np.ndarray, y_pred: np.ndarray, mask: np.ndarray, mu_w: np.ndarray) -> float:
    if not np.any(mask):
        return float("nan")
    ww = mu_w[mask].copy()
    s = float(ww.sum())
    if s <= 0:
        ww = np.full(int(mask.sum()), 1.0 / int(mask.sum()))
    else:
        ww = ww / s
    err = y_true[mask] - y_pred[mask]
    return float(np.sqrt(np.sum(ww * err * err)))


def group_rmses(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    groups: np.ndarray,
    min_n: int,
) -> np.ndarray:
    vals = []
    for g in np.unique(groups):
        mask = groups == g
        n = int(mask.sum())
        if n < min_n:
            continue
        err = y_true[mask] - y_pred[mask]
        vals.append(float(np.sqrt(np.mean(err * err))))
    return np.asarray(vals, dtype=np.float64)


def predict_pack(ckpt: Path, pack: dict) -> np.ndarray:
    model = CommonNDMF_from_ckpt(ckpt, pack["num_spatial"])
    sp_idx, hour_t, wday_t, trend_t = pack["features"]
    model.eval()
    with torch.no_grad():
        pred = model(sp_idx, hour_t, wday_t, trend_t).cpu().numpy().reshape(-1)
    return np.asarray(pred, dtype=np.float64)


def collect_b1(packs: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for scenario in SCENARIOS:
        for dataset in DATASETS:
            pack = packs[dataset]
            for method in METHODS:
                for seed in FORMAL_SEEDS:
                    d = run_dir(scenario, dataset, method, seed)
                    ckpt = d / "checkpoints" / "final.pt"
                    stored = d / "final_metrics.json"
                    rec = {
                        "dataset": dataset,
                        "scenario": scenario,
                        "method": method,
                        "seed": int(seed),
                        "status": "OK",
                    }
                    if stored.is_file():
                        payload = json.loads(stored.read_text(encoding="utf-8"))
                        rec["RMSE_mu_stored"] = payload.get("RMSE_mu")
                        rec["Delta_c_s"] = payload.get("Delta_c_s")
                        rec["Delta_group"] = payload.get("Delta_group")
                        rec["Tail_RMSE_stored"] = payload.get("Tail_RMSE")
                    else:
                        rec["RMSE_mu_stored"] = None
                        rec["Delta_c_s"] = None
                        rec["Delta_group"] = None
                        rec["Tail_RMSE_stored"] = None
                    if not ckpt.is_file():
                        rec["status"] = "MISSING_CKPT"
                        rows.append(rec)
                        continue
                    y_pred = predict_pack(ckpt, pack)
                    y_true = pack["y_true"]
                    rec["RMSE_mu_recomputed"] = float(
                        rmse_mu(y_pred, y_true, pack["mu_w"])
                    )
                    stored_v = rec["RMSE_mu_stored"]
                    rec["rmse_mu_abs_diff"] = (
                        abs(float(rec["RMSE_mu_recomputed"]) - float(stored_v))
                        if stored_v is not None
                        else None
                    )
                    grmse = group_rmses(y_true, y_pred, pack["groups"], MIN_GROUP_N)
                    rec["n_groups_eval"] = int(len(grmse))
                    rec["worst_group_rmse"] = (
                        float(np.max(grmse)) if len(grmse) else None
                    )
                    rec["p90_group_rmse"] = (
                        float(np.quantile(grmse, 0.90)) if len(grmse) else None
                    )
                    rec["median_group_rmse"] = (
                        float(np.median(grmse)) if len(grmse) else None
                    )
                    rec["high_mu_group_rmse"] = _wrmse(
                        y_true, y_pred, pack["high_g_mask"], pack["mu_w"]
                    )
                    rec["high_mu_pair_rmse"] = _wrmse(
                        y_true, y_pred, pack["high_p_mask"], pack["mu_w"]
                    )
                    rows.append(rec)
    return pd.DataFrame(rows)


def _seed_map(frame: pd.DataFrame, dataset: str, scenario: str, method: str, metric: str) -> dict[int, float]:
    sub = frame[
        (frame["dataset"] == dataset)
        & (frame["scenario"] == scenario)
        & (frame["method"] == method)
        & (frame["status"] == "OK")
    ]
    out: dict[int, float] = {}
    for row in sub.itertuples(index=False):
        val = getattr(row, metric, None)
        if val is None or (isinstance(val, float) and not math.isfinite(val)):
            continue
        out[int(row.seed)] = float(val)
    return out


def stats_tables(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    holm_rows = []
    comparisons = (
        ("raven", "fedau_window", "raven_vs_fedau"),
        ("raven", "obsuse_window", "raven_vs_obsuse"),
        ("raven", "fedavg_window", "raven_vs_fedavg"),
        ("raven", "twostage_hajek", "raven_vs_twostage"),
    )
    specified = {"raven_vs_fedau", "raven_vs_fedavg"}
    for dataset in DATASETS:
        for scenario in SCENARIOS:
            for method in METHODS:
                sub = frame[
                    (frame["dataset"] == dataset)
                    & (frame["scenario"] == scenario)
                    & (frame["method"] == method)
                    & (frame["status"] == "OK")
                ]
                for metric in B1_METRICS + ("RMSE_mu_recomputed", "rmse_mu_abs_diff"):
                    vals = [float(v) for v in sub[metric].tolist() if pd.notna(v)]
                    summary_rows.append(
                        {
                            "dataset": dataset,
                            "scenario": scenario,
                            "method": method,
                            "metric": metric,
                            **summarize_vector(vals),
                        }
                    )
            for metric in B1_METRICS:
                packed: dict[str, dict] = {}
                family: dict[str, float] = {}
                for left, right, name in comparisons:
                    a = _seed_map(frame, dataset, scenario, left, metric)
                    b = _seed_map(frame, dataset, scenario, right, metric)
                    if len(set(a) & set(b)) < 2:
                        packed[name] = {
                            "n": len(set(a) & set(b)),
                            "p_raw": None,
                            "test_status": "INSUFFICIENT",
                        }
                        continue
                    summary = paired_summary(a, b)
                    packed[name] = summary
                    family[name] = float(summary["p_raw"])
                adjusted = holm(family) if family else {}
                for name, summary in packed.items():
                    mean_diff = summary.get("mean_diff_raven_minus_baseline")
                    p_h = adjusted.get(name)
                    holm_rows.append(
                        {
                            "dataset": dataset,
                            "scenario": scenario,
                            "metric": metric,
                            "comparison": name,
                            "holm_family": f"{dataset}:{scenario}:{metric}:4comparisons",
                            "family_role": "specified" if name in specified else "diagnostic",
                            "n": summary.get("n"),
                            "mean_diff_left_minus_right": mean_diff,
                            "effect_size": summary.get("effect_size"),
                            "wins": summary.get("wins"),
                            "ties": summary.get("ties"),
                            "losses": summary.get("losses"),
                            "p_raw": summary.get("p_raw"),
                            "p_holm": p_h,
                            "test_status": summary.get("test_status"),
                            "raven_lower_holm": (
                                False
                                if p_h is None or mean_diff is None
                                else float(p_h) < 0.05 and float(mean_diff) < 0
                            ),
                            "baseline_lower_holm": (
                                False
                                if p_h is None or mean_diff is None
                                else float(p_h) < 0.05 and float(mean_diff) > 0
                            ),
                        }
                    )
    return pd.DataFrame(summary_rows), pd.DataFrame(holm_rows)


def _corr(x: np.ndarray, y: np.ndarray) -> dict:
    if len(x) < 3:
        return {
            "n": int(len(x)),
            "spearman_rho": None,
            "spearman_p": None,
            "pearson_r": None,
            "pearson_p": None,
        }
    from scipy.stats import pearsonr, spearmanr

    sp = spearmanr(x, y)
    pr = pearsonr(x, y)
    return {
        "n": int(len(x)),
        "spearman_rho": float(sp.statistic),
        "spearman_p": float(sp.pvalue),
        "pearson_r": float(pr.statistic),
        "pearson_p": float(pr.pvalue),
    }


def association_table(frame: pd.DataFrame) -> pd.DataFrame:
    """B2: does worse Delta_c-s go with worse RMSE_mu?"""
    rows = []
    ok = frame[
        (frame["status"] == "OK")
        & frame["Delta_c_s"].notna()
        & frame["RMSE_mu_stored"].notna()
    ]
    for dataset in DATASETS:
        for scenario in SCENARIOS:
            sub = ok[(ok["dataset"] == dataset) & (ok["scenario"] == scenario)]
            rows.append(
                {
                    "dataset": dataset,
                    "scenario": scenario,
                    "kind": "pooled_method_seed",
                    "x": "Delta_c_s",
                    "y": "RMSE_mu_stored",
                    **_corr(
                        sub["Delta_c_s"].to_numpy(dtype=float),
                        sub["RMSE_mu_stored"].to_numpy(dtype=float),
                    ),
                }
            )
            # within-seed Spearman across 5 methods, then mean
            seed_rhos = []
            seed_ps = []
            for seed in FORMAL_SEEDS:
                one = sub[sub["seed"] == seed]
                if len(one) < 4:
                    continue
                c = _corr(
                    one["Delta_c_s"].to_numpy(dtype=float),
                    one["RMSE_mu_stored"].to_numpy(dtype=float),
                )
                if c["spearman_rho"] is not None:
                    seed_rhos.append(c["spearman_rho"])
                    seed_ps.append(c["spearman_p"])
            rows.append(
                {
                    "dataset": dataset,
                    "scenario": scenario,
                    "kind": "mean_within_seed_across_methods",
                    "x": "Delta_c_s",
                    "y": "RMSE_mu_stored",
                    "n": len(seed_rhos),
                    "spearman_rho": float(np.mean(seed_rhos)) if seed_rhos else None,
                    "spearman_p": None,
                    "pearson_r": float(np.median(seed_rhos)) if seed_rhos else None,
                    "pearson_p": float(np.std(seed_rhos, ddof=1)) if len(seed_rhos) > 1 else None,
                    "note": "pearson_r=median within-seed Spearman; pearson_p=std of those Spearmans",
                }
            )
            # method means (5 points)
            means = (
                sub.groupby("method")[["Delta_c_s", "RMSE_mu_stored"]]
                .mean()
                .reset_index()
            )
            rows.append(
                {
                    "dataset": dataset,
                    "scenario": scenario,
                    "kind": "method_means_n5",
                    "x": "Delta_c_s",
                    "y": "RMSE_mu_stored",
                    **_corr(
                        means["Delta_c_s"].to_numpy(dtype=float),
                        means["RMSE_mu_stored"].to_numpy(dtype=float),
                    ),
                }
            )
            # paired vs FedAvg: structural gap vs prediction gap
            fed = sub[sub["method"] == "fedavg_window"][
                ["seed", "Delta_c_s", "RMSE_mu_stored"]
            ].rename(
                columns={"Delta_c_s": "d_base", "RMSE_mu_stored": "r_base"}
            )
            for method in METHODS:
                if method == "fedavg_window":
                    continue
                oth = sub[sub["method"] == method][
                    ["seed", "Delta_c_s", "RMSE_mu_stored"]
                ]
                mrg = oth.merge(fed, on="seed")
                dx = mrg["Delta_c_s"] - mrg["d_base"]
                dy = mrg["RMSE_mu_stored"] - mrg["r_base"]
                rows.append(
                    {
                        "dataset": dataset,
                        "scenario": scenario,
                        "kind": f"paired_gap_vs_fedavg:{method}",
                        "x": "Delta_c_s_minus_fedavg",
                        "y": "RMSE_mu_minus_fedavg",
                        **_corr(dx.to_numpy(dtype=float), dy.to_numpy(dtype=float)),
                    }
                )
    return pd.DataFrame(rows)


def _fmt_p(p) -> str:
    if p is None or (isinstance(p, float) and not math.isfinite(p)):
        return "NA"
    p = float(p)
    if p < 1e-4:
        return f"{p:.3e}"
    return f"{p:.4f}"


def write_conclusion(
    holm_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    assoc_df: pd.DataFrame,
    seed_df: pd.DataFrame,
    packs: dict[str, dict],
) -> str:
    lines = []
    lines.append("B1/B2 deployment follow-up (checkpoints + stored metrics, 20 seeds).")
    lines.append(
        f"B1 worst-group RMSE: unweighted RMSE per h(i) group with n>={MIN_GROUP_N}; "
        "high-mu group/pair RMSE uses runner mu-weights on the high-mass subset."
    )
    lines.append("Tail_RMSE is stored only as a sanity column and is NOT used as worst-group.")
    lines.append("")
    # sanity
    diffs = seed_df.loc[seed_df["status"] == "OK", "rmse_mu_abs_diff"].dropna()
    lines.append("SANITY (recomputed RMSE_mu vs stored):")
    if len(diffs):
        lines.append(
            f"- n={len(diffs)}, max_abs_diff={float(diffs.max()):.6g}, "
            f"median={float(diffs.median()):.6g}"
        )
        if float(diffs.max()) > 1e-4:
            lines.append("- WARNING: checkpoint reload does not match stored RMSE_mu.")
        else:
            lines.append("- OK: checkpoint reload matches stored RMSE_mu.")
    lines.append("")
    for ds, pack in packs.items():
        lines.append(
            f"- {ds} test: n={pack['n_test']}, groups={pack['n_groups_test']}, "
            f"high_mu_group_units={pack['n_high_g']}, high_mu_pair_units={pack['n_high_p']}"
        )
    lines.append("")
    lines.append("B1 paired Wilcoxon+Holm (lower better):")
    raven_better = 0
    raven_worse = 0
    n_core = 0
    core = holm_df[holm_df["metric"] == "worst_group_rmse"]
    for dataset in DATASETS:
        for scenario in SCENARIOS:
            for cmp_name, label in (
                ("raven_vs_fedau", "FedAU"),
                ("raven_vs_fedavg", "FedAvg"),
                ("raven_vs_obsuse", "ObsUse"),
                ("raven_vs_twostage", "TwoStage"),
            ):
                row = core[
                    (core["dataset"] == dataset)
                    & (core["scenario"] == scenario)
                    & (core["comparison"] == cmp_name)
                ]
                if row.empty:
                    continue
                r = row.iloc[0]
                n_core += 1
                if bool(r["raven_lower_holm"]):
                    raven_better += 1
                    tag = "Holm-sig RAVEN lower"
                elif bool(r["baseline_lower_holm"]):
                    raven_worse += 1
                    tag = "Holm-sig baseline lower"
                else:
                    md = float(r["mean_diff_left_minus_right"])
                    tag = (
                        "RAVEN numerically lower, not Holm-sig"
                        if md < 0
                        else "RAVEN numerically higher, not Holm-sig"
                    )
                lines.append(
                    f"- {dataset} {scenario} worst_group vs {label}: {tag}, "
                    f"mean_diff={float(r['mean_diff_left_minus_right']):.4f}, "
                    f"wins={r['wins']}/ties={r['ties']}/losses={r['losses']}, "
                    f"p_holm={_fmt_p(r['p_holm'])}"
                )
    lines.append("")
    lines.append("B1 means (worst_group_rmse):")
    sub = summary_df[summary_df["metric"] == "worst_group_rmse"]
    for dataset in DATASETS:
        for scenario in SCENARIOS:
            bits = []
            for method in METHODS:
                row = sub[
                    (sub["dataset"] == dataset)
                    & (sub["scenario"] == scenario)
                    & (sub["method"] == method)
                ]
                if row.empty or row.iloc[0]["mean"] is None:
                    bits.append(f"{DISPLAY[method]}=NA")
                else:
                    rr = row.iloc[0]
                    bits.append(
                        f"{DISPLAY[method]}={float(rr['mean']):.4f}+/-{float(rr['std']):.4f}"
                    )
            lines.append(f"- {dataset} {scenario}: " + "; ".join(bits))
    lines.append("")
    lines.append("B2 association (worse Delta_c-s with worse RMSE_mu would be rho>0):")
    for dataset in DATASETS:
        for scenario in SCENARIOS:
            for kind in (
                "pooled_method_seed",
                "mean_within_seed_across_methods",
                "method_means_n5",
            ):
                row = assoc_df[
                    (assoc_df["dataset"] == dataset)
                    & (assoc_df["scenario"] == scenario)
                    & (assoc_df["kind"] == kind)
                ]
                if row.empty:
                    continue
                r = row.iloc[0]
                lines.append(
                    f"- {dataset} {scenario} {kind}: Spearman={r['spearman_rho'] if r['spearman_rho'] is None else round(float(r['spearman_rho']), 4)} "
                    f"p={_fmt_p(r['spearman_p'])} n={r['n']}"
                )
    lines.append("")
    lines.append("Author verdict (honest):")
    if raven_better == n_core and n_core > 0:
        lines.append(
            "- B1 SUPPORTS a worst-group prediction gain vs FedAU/FedAvg/ObsUse/TwoStage."
        )
        b1 = "SUPPORT"
    elif raven_better > 0 and raven_worse == 0:
        lines.append(
            f"- B1 PARTIAL: Holm RAVEN-lower on {raven_better}/{n_core} worst-group comparisons; none favor the baseline."
        )
        b1 = "PARTIAL"
    else:
        lines.append(
            f"- B1 NOT SUPPORTED as a uniform worst-group gain: RAVEN-lower {raven_better}/{n_core}, "
            f"baseline-lower {raven_worse}/{n_core}."
        )
        b1 = "NOT_SUPPORTED"
    # B2: look at pooled complete_aligned
    pos = 0
    neg = 0
    pooled = assoc_df[assoc_df["kind"] == "pooled_method_seed"]
    for _, r in pooled.iterrows():
        rho = r["spearman_rho"]
        p = r["spearman_p"]
        if rho is None or p is None:
            continue
        if float(p) < 0.05 and float(rho) > 0:
            pos += 1
        elif float(p) < 0.05 and float(rho) < 0:
            neg += 1
    if pos > 0 and neg == 0:
        lines.append(
            f"- B2 PARTIAL/SUPPORT: {pos}/{len(pooled)} pooled dataset-scenario Spearman "
            "values are significantly positive (worse structure with worse RMSE)."
        )
        b2 = "SUPPORT" if pos == len(pooled) else "PARTIAL"
    elif pos == 0:
        lines.append(
            "- B2 NOT SUPPORTED: pooled Spearman is not a significant positive "
            "structure-to-prediction link."
        )
        b2 = "NOT_SUPPORTED"
    else:
        lines.append(
            f"- B2 MIXED: significant positive in {pos}, significant negative in {neg} "
            "pooled dataset-scenario blocks."
        )
        b2 = "MIXED"
    lines.append(f"- VERDICT_B1={b1}")
    lines.append(f"- VERDICT_B2={b2}")
    lines.append(
        "- Paper backfill only if B1 SUPPORT/PARTIAL with a real effect size, "
        "or B2 SUPPORT. Do not use Tail_RMSE. Do not claim coverage gains."
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    packs = {ds: build_eval_pack(ds) for ds in DATASETS}
    meta = {
        ds: {
            k: packs[ds][k]
            for k in (
                "n_test",
                "n_groups_test",
                "median_group_mu",
                "median_pair_mu",
                "n_high_g",
                "n_high_p",
                "num_spatial",
            )
        }
        for ds in DATASETS
    }
    (OUT_DIR / "eval_pack_meta.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8"
    )
    print("eval packs", json.dumps(meta, indent=2))
    seed_df = collect_b1(packs)
    seed_df.to_csv(OUT_DIR / "per_seed.csv", index=False)
    summary_df, holm_df = stats_tables(seed_df)
    summary_df.to_csv(OUT_DIR / "summary.csv", index=False)
    holm_df.to_csv(OUT_DIR / "holm.csv", index=False)
    assoc_df = association_table(seed_df)
    assoc_df.to_csv(OUT_DIR / "association.csv", index=False)
    text = write_conclusion(holm_df, summary_df, assoc_df, seed_df, packs)
    (OUT_DIR / "conclusion.txt").write_text(text, encoding="utf-8")
    print(text)
    print(f"wrote {OUT_DIR}")
    print(f"rows={len(seed_df)} missing={int((seed_df.status!='OK').sum())}")


if __name__ == "__main__":
    main()

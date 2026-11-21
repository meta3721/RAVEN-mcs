"""G2: 4-block worst-group + Path B gated vs adapted baselines. No new training."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TAB = OUT / "tables"
VAL_SEEDS = list(range(30001, 30011))
TEST_SEEDS = list(range(30011, 30021))
ALL_SEEDS = VAL_SEEDS + TEST_SEEDS
DATASETS = ("sensorscope", "uair")
GATED = {"sensorscope": "raven", "uair": "raven_wo_design"}
METHODS = (
    "raven",
    "raven_wo_design",
    "fedavg_window",
    "fedau_window",
    "obsuse_window",
    "twostage_hajek",
    "local_hajek",
)
STRONG = ("fedau_window", "obsuse_window", "twostage_hajek")
NI = 0.5


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _run_dir(dataset: str, method: str, seed: int) -> Path:
    if method == "raven_wo_design":
        return ROOT / "artifacts" / "e4_core_mechanism_ablation_r1" / "runs" / dataset / method / f"seed{seed}"
    if method == "fedau_window":
        return ROOT / "artifacts" / "e3_fedau_window_r1" / "runs" / dataset / method / f"seed{seed}"
    if method == "obsuse_window":
        return ROOT / "artifacts" / "e3_obsuse_window_r1" / "runs" / dataset / method / f"seed{seed}"
    return ROOT / "artifacts" / "e3_formal_runs_r1" / "runs" / dataset / method / f"seed{seed}"


def _pct(new: float, ref: float) -> float:
    if ref is None or not np.isfinite(ref) or abs(float(ref)) < 1e-15:
        return float("nan")
    return 100.0 * (float(new) - float(ref)) / float(ref)


def build_pack(dataset_name: str) -> dict:
    from raven_mcs.data.target import RepeatableTimeOfDayMapper
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
    from raven_mcs.e3.target_pair.target_wiring import production_target_bundle
    from raven_mcs.models.features import extract_features

    ds = load_paper_dataset(ROOT, dataset_name)
    spatial_to_client = load_spatial_to_client(ROOT, dataset_name)
    bundle = production_target_bundle(root=ROOT, dataset_name=dataset_name, dataset=ds)
    mu = np.asarray(bundle["mu"], dtype=np.float64)
    test = ds.atomic_df[ds.atomic_df["split"] == "test"].copy()
    g2i = ds._target_group_str_to_int
    fine = np.asarray([int(g2i.get(str(g), 0)) for g in test["target_group"].tolist()], dtype=int)
    blocks = RepeatableTimeOfDayMapper().map(test).to_numpy(dtype=int)
    hours = []
    for ts in test["absolute_time"].tolist():
        hours.append(float(ts.timestamp()) / 3600.0 if hasattr(ts, "timestamp") else float(ts))
    hours = np.asarray(hours, dtype=np.float64)
    spatial_ids = [str(s) for s in test["spatial_id"].tolist()]
    time_indices = [int(t) for t in test["time_index"].tolist()]
    total_slots = int(ds.atomic_df["time_index"].max()) + 1
    feats = extract_features(
        spatial_ids,
        hours.tolist(),
        time_indices,
        {str(k): int(v) for k, v in ds._spatial_to_idx.items()},
        total_slots,
    )
    y_true = test["target_value"].to_numpy(dtype=np.float64)
    counts: dict[int, int] = {}
    for g in fine.tolist():
        counts[int(g)] = counts.get(int(g), 0) + 1
    w = np.zeros(len(fine), dtype=np.float64)
    for i, g in enumerate(fine.tolist()):
        mg = float(mu[g]) if g < len(mu) else 0.0
        w[i] = mg / max(counts[int(g)], 1)
    s = float(w.sum())
    w = w / s if s > 0 else np.full(len(w), 1.0 / max(len(w), 1))
    return {
        "num_spatial": int(ds.num_spatial),
        "features": feats,
        "y_true": y_true,
        "blocks": blocks,
        "mu_w": w,
        "n_test": int(len(y_true)),
        "block_counts": {int(g): int((blocks == g).sum()) for g in range(4)},
    }


def _wrmse(y_true, y_pred, mask, mu_w) -> float:
    if not np.any(mask):
        return float("nan")
    ww = mu_w[mask].copy()
    s = float(ww.sum())
    ww = ww / s if s > 0 else np.full(int(mask.sum()), 1.0 / int(mask.sum()))
    err = y_true[mask] - y_pred[mask]
    return float(np.sqrt(np.sum(ww * err * err)))


def predict(ckpt: Path, pack: dict) -> np.ndarray:
    from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt

    model = CommonNDMF_from_ckpt(ckpt, pack["num_spatial"])
    sp_idx, hour_t, wday_t, trend_t = pack["features"]
    model.eval()
    with torch.no_grad():
        pred = model(sp_idx, hour_t, wday_t, trend_t).cpu().numpy().reshape(-1)
    return np.asarray(pred, dtype=np.float64)


def collect(packs: dict[str, dict]) -> pd.DataFrame:
    from raven_mcs.metrics.accuracy import rmse_mu

    rows = []
    for dataset in DATASETS:
        pack = packs[dataset]
        for method in METHODS:
            for seed in ALL_SEEDS:
                d = _run_dir(dataset, method, seed)
                ckpt = d / "checkpoints" / "final.pt"
                rec = {
                    "dataset": dataset,
                    "method": method,
                    "seed": seed,
                    "status": "OK",
                    "gated_role": method == GATED[dataset],
                }
                stored = d / "final_metrics.json"
                if stored.is_file():
                    met = _load_json(stored)
                    rec["RMSE_mu_stored"] = met.get("RMSE_mu")
                    rec["Delta_group"] = met.get("Delta_group")
                    rec["Delta_c_s"] = met.get("Delta_c_s")
                if not ckpt.is_file():
                    rec["status"] = "MISSING_CKPT"
                    rows.append(rec)
                    continue
                y_pred = predict(ckpt, pack)
                y_true = pack["y_true"]
                rec["RMSE_mu"] = float(rmse_mu(y_pred, y_true, pack["mu_w"]))
                block_vals = []
                for g in range(4):
                    rmse_g = _wrmse(y_true, y_pred, pack["blocks"] == g, pack["mu_w"])
                    rec[f"RMSE_block{g}"] = rmse_g
                    if np.isfinite(rmse_g):
                        block_vals.append(rmse_g)
                rec["WorstGroupRMSE"] = float(np.max(block_vals)) if block_vals else float("nan")
                rec["group_dispersion"] = (
                    float(np.max(block_vals) - np.min(block_vals)) if block_vals else float("nan")
                )
                rows.append(rec)
    return pd.DataFrame(rows)


def add_gated(frame: pd.DataFrame) -> pd.DataFrame:
    extra = []
    for dataset, method in GATED.items():
        sub = frame[(frame.dataset == dataset) & (frame.method == method) & (frame.status == "OK")]
        for rec in sub.to_dict("records"):
            rec = dict(rec)
            rec["method"] = "raven_gated"
            rec["gated_role"] = True
            extra.append(rec)
    return pd.concat([frame, pd.DataFrame(extra)], ignore_index=True)


def _mean_ci(vals: np.ndarray) -> tuple[float, float, float]:
    vals = np.asarray(vals, dtype=np.float64)
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return float("nan"), float("nan"), float("nan")
    mean = float(vals.mean())
    se = float(vals.std(ddof=1) / np.sqrt(vals.size)) if vals.size > 1 else 0.0
    return mean, mean - 1.96 * se, mean + 1.96 * se


def paired_table(frame: pd.DataFrame, seeds: list[int], split: str) -> pd.DataFrame:
    from raven_mcs.e3.formal.stats import holm, wilcoxon_signed_rank_two_sided

    rows = []
    for dataset in DATASETS:
        g = frame[
            (frame.dataset == dataset)
            & (frame.method == "raven_gated")
            & (frame.seed.isin(seeds))
            & (frame.status == "OK")
        ].set_index("seed")
        raw_p = {}
        tmp = []
        for base in STRONG + ("fedavg_window",):
            b = frame[
                (frame.dataset == dataset)
                & (frame.method == base)
                & (frame.seed.isin(seeds))
                & (frame.status == "OK")
            ].set_index("seed")
            common = sorted(set(g.index) & set(b.index))
            diffs = [
                float(g.loc[s, "WorstGroupRMSE"] - b.loc[s, "WorstGroupRMSE"]) for s in common
            ]
            pcts = [
                _pct(float(g.loc[s, "WorstGroupRMSE"]), float(b.loc[s, "WorstGroupRMSE"]))
                for s in common
            ]
            p, stat = wilcoxon_signed_rank_two_sided(diffs)
            raw_p[base] = p
            mean_pct, lo, hi = _mean_ci(np.asarray(pcts))
            tmp.append(
                {
                    "split": split,
                    "dataset": dataset,
                    "baseline": base,
                    "n": len(common),
                    "gated_mean": float(g.loc[common, "WorstGroupRMSE"].mean()),
                    "base_mean": float(b.loc[common, "WorstGroupRMSE"].mean()),
                    "mean_pct_gated_minus_base": mean_pct,
                    "pct_ci95_low": lo,
                    "pct_ci95_high": hi,
                    "p_raw": p,
                    "test": stat,
                    "ni_pass": bool(mean_pct <= NI) if base in ("fedau_window", "obsuse_window") else None,
                }
            )
        adj = holm({k: raw_p[k] for k in ("fedau_window", "obsuse_window") if k in raw_p})
        for row in tmp:
            if row["baseline"] in adj:
                row["p_holm"] = adj[row["baseline"]]
            rows.append(row)
    return pd.DataFrame(rows)


def val_gate(paired_val: pd.DataFrame, frame: pd.DataFrame) -> dict:
    checks = []
    for dataset in DATASETS:
        n_ok = int(
            (
                (frame.dataset == dataset)
                & (frame.method == "raven_gated")
                & (frame.seed.isin(VAL_SEEDS))
                & (frame.status == "OK")
                & np.isfinite(frame.WorstGroupRMSE)
            ).sum()
        )
        checks.append(
            {
                "rule": f"{dataset}_gated_finite_val",
                "n": n_ok,
                "pass": n_ok == len(VAL_SEEDS),
            }
        )
        for base in ("fedau_window", "obsuse_window"):
            sub = paired_val[(paired_val.dataset == dataset) & (paired_val.baseline == base)]
            if sub.empty:
                checks.append({"rule": f"{dataset}_vs_{base}", "pass": False})
                continue
            row = sub.iloc[0]
            checks.append(
                {
                    "rule": f"{dataset}_vs_{base}_ni",
                    "mean_pct": float(row["mean_pct_gated_minus_base"]),
                    "pass": bool(row["ni_pass"]),
                }
            )
    return {
        "verdict": "G2_VAL_NONINFERIOR" if all(c["pass"] for c in checks) else "G2_VAL_NI_FAILS",
        "checks": checks,
    }


def degeneracy(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dataset in DATASETS:
        for split, seeds in (("val", VAL_SEEDS), ("test", TEST_SEEDS)):
            a = frame[
                (frame.dataset == dataset)
                & (frame.method == "local_hajek")
                & (frame.seed.isin(seeds))
                & (frame.status == "OK")
            ]
            b = frame[
                (frame.dataset == dataset)
                & (frame.method == "fedavg_window")
                & (frame.seed.isin(seeds))
                & (frame.status == "OK")
            ]
            if a.empty or b.empty:
                continue
            m = a.merge(b, on="seed", suffixes=("_lh", "_fa"))
            rel = [
                _pct(float(r.RMSE_mu_lh), float(r.RMSE_mu_fa)) for r in m.itertuples(index=False)
            ]
            rows.append(
                {
                    "split": split,
                    "dataset": dataset,
                    "mean_rmse_local_hajek_vs_fedavg_pct": float(np.nanmean(rel)),
                    "demote": bool(abs(float(np.nanmean(rel))) < 0.5),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    packs = {}
    meta = {}
    for dataset in DATASETS:
        print("pack", dataset, flush=True)
        packs[dataset] = build_pack(dataset)
        meta[dataset] = {
            "n_test": packs[dataset]["n_test"],
            "block_counts": packs[dataset]["block_counts"],
        }
    (OUT / "eval_pack_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("collect checkpoints", flush=True)
    raw = collect(packs)
    frame = add_gated(raw)
    frame.to_csv(TAB / "per_seed.csv", index=False)
    paired_val = paired_table(frame, VAL_SEEDS, "val")
    paired_test = paired_table(frame, TEST_SEEDS, "test")
    paired = pd.concat([paired_val, paired_test], ignore_index=True)
    paired.to_csv(TAB / "paired_worstgroup.csv", index=False)
    deg = degeneracy(frame)
    deg.to_csv(TAB / "local_hajek_degeneracy.csv", index=False)
    gate = val_gate(paired_val, frame)
    gate["local_hajek"] = deg.to_dict("records")
    (OUT / "VAL_GATE.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")
    print(json.dumps(gate, indent=2))
    print(paired.to_string(index=False))


if __name__ == "__main__":
    main()

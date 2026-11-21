#!/usr/bin/env python3
"""Part I driver for the estimand-gate round: arrival-weighted validation vs
deployment-target model selection.

Instruction (read-only copy): raven-mcs-estimand-gate-execution-prompt.md
  sha256 ffb4bde64af8b6c4d6c647bc0d8b90e2191b945946e1cedc76e47dc08f1d189d
Contract: CCFA-Skills/ccf-experiment-designer.  Protocol, not publication prose.

Outputs (only): results_estimand_selection/round_v1/
  INVENTORY.json  (written by .rb_work/estimand_inventory_write.py, I-P0)
  WEIGHTS.csv
  THETA_SCORED.csv
  tables/RISK_ROWS.csv, tables/SELECTION.csv, tables/SELECTION_SUMMARY.csv
  SELECTION_DECISION.json

Stage `p0`  : WEIGHTS.csv only, written before any score exists.
Stage `p1`  : checkpoint scoring + reproduction check + tables + labels.

No training.  src/, the manuscript, artifacts/ and every other results_* are untouched.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import torch
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "results_estimand_selection" / "round_v1"
TABLES = OUT / "tables"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
E4 = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"
TRACES = ROOT / "artifacts/e3_formal_runs_r1/eventtraces"

SEEDS = list(range(30001, 30021))
DATASETS = ("sensorscope", "uair")
M_MAIN = ["fedavg_window", "fedasync_window", "flamf_timealign_adapted", "local_hajek",
          "twostage_hajek", "inst_cal", "debt_cal", "raven"]
M_EXTRA = ["raven_wo_design"]
M = M_MAIN + M_EXTRA                      # order fixed by I-2; also the tie-break order
DELTA = 0.005                             # margin of I-H1 = 0.5 %, same as II-H2
BOOT_SEED = 20261007
BOOT_DRAWS = 10000
Z_POWER = stats.norm.ppf(0.975) + stats.norm.ppf(0.80)


# ------------------------------------------------------------------ shared plumbing
def dump_json(obj, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_context(dataset: str) -> dict:
    """Everything shared by all runs of one dataset."""
    from raven_mcs.data.processed_dataset import ProcessedDataset  # noqa: F401
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
    from raven_mcs.e3.real_runner.runner import _predict
    from raven_mcs.models.common_ndmf import deterministic_common_ndmf
    from raven_mcs.e3.target_pair.target_wiring import production_target_bundle
    from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum

    ds = load_paper_dataset(ROOT, dataset)
    mapping = load_spatial_to_client(ROOT, dataset)
    sealed, _meta = apply_sealed_opportunity_stratum(ds.atomic_df, dataset=dataset, root=ROOT)
    bundle = production_target_bundle(root=ROOT, dataset_name=dataset, dataset=ds)
    mu = np.asarray(bundle["mu"], dtype=np.float64)
    gids = list(bundle["group_id_by_index"])
    str_to_int = {str(k): int(v) for k, v in ds._target_group_str_to_int.items()}
    for name in gids:
        if str(name) not in str_to_int:
            raise RuntimeError("group %r missing from the dataset group map" % (name,))
    unit_group = dict(zip(sealed["unit_id"].astype(str),
                          [str(g) for g in sealed["target_group"]]))
    unit_split = dict(zip(sealed["unit_id"].astype(str), sealed["split"].astype(str)))
    return {"dataset": dataset, "ds": ds, "sealed": sealed, "mapping": mapping,
            "mu": mu, "gids": gids, "str_to_int": str_to_int,
            "unit_group": unit_group, "unit_split": unit_split,
            "predict": _predict, "factory": deterministic_common_ndmf,
            "artifact": str(bundle["artifact_path"]), "artifact_sha": bundle["artifact_sha256"]}


def group_index_vector(ctx: dict) -> np.ndarray:
    """gid name -> index in the frozen mu order."""
    return {str(g): i for i, g in enumerate(ctx["gids"])}


# --------------------------------------------------------------------- I-P0: weights
def build_pi_arr(ctx: dict, variant: str) -> tuple[np.ndarray, dict]:
    """Group share of delivered risk units on non-test splits of the frozen trace.

    variant 'U'  : units of events with U = 1
    variant 'R'  : every risk-set unit of every event (the R = 1 sensitivity of I-2)
    """
    dataset = ctx["dataset"]
    idx = group_index_vector(ctx)
    counts = np.zeros(len(ctx["gids"]), dtype=np.float64)
    n_units = 0
    n_test_dropped = 0
    n_unmapped = 0
    for seed in SEEDS:
        ev = pd.read_parquet(TRACES / dataset / ("seed%d" % seed) /
                             "training_eventtrace/events.parquet")
        for row in ev.itertuples(index=False):
            if variant == "U" and int(row.U) != 1:
                continue
            raw = row.risk_set_unit_ids
            ids = json.loads(raw) if isinstance(raw, str) else list(raw)
            for uid_raw in ids:
                uid = str(uid_raw)
                if ctx["unit_split"].get(uid) == "test":
                    n_test_dropped += 1
                    continue
                g = ctx["unit_group"].get(uid)
                if g is None or g not in idx:
                    n_unmapped += 1
                    continue
                counts[idx[g]] += 1.0
                n_units += 1
    if n_units == 0:
        raise RuntimeError("empty arrival frame for %s/%s" % (dataset, variant))
    meta = {"n_units": n_units, "n_test_units_dropped": n_test_dropped,
            "n_unmapped": n_unmapped}
    return counts / n_units, meta


def stage_p0() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    meta_all = {}
    for dataset in DATASETS:
        ctx = load_context(dataset)
        pi_u, meta_u = build_pi_arr(ctx, "U")
        pi_r, meta_r = build_pi_arr(ctx, "R")
        tv = 0.5 * float(np.abs(pi_u - ctx["mu"]).sum())
        l1 = float(np.abs(pi_u - ctx["mu"]).sum())
        tv_r = 0.5 * float(np.abs(pi_r - ctx["mu"]).sum())
        l1_r = float(np.abs(pi_r - ctx["mu"]).sum())
        meta_all[dataset] = {"pi_arr": meta_u, "pi_arr_R": meta_r,
                             "tv_arr_mu": tv, "l1_arr_mu": l1,
                             "tv_arrR_mu": tv_r, "l1_arrR_mu": l1_r,
                             "n_groups": len(ctx["gids"]),
                             "mu_artifact": ctx["artifact"],
                             "mu_artifact_sha256": ctx["artifact_sha"]}
        for i, name in enumerate(ctx["gids"]):
            rows.append({"dataset": dataset, "group_index": i, "group_id": name,
                         "mu": float(ctx["mu"][i]), "pi_arr": float(pi_u[i]),
                         "pi_arr_R": float(pi_r[i])})
        print("%-12s groups=%d  TV(pi_arr,mu)=%.6f  L1=%.6f  TV(pi_arr^R,mu)=%.6f  L1^R=%.6f"
              % (dataset, len(ctx["gids"]), tv, l1, tv_r, l1_r))
    with (OUT / "WEIGHTS.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["dataset", "group_index", "group_id", "mu",
                                           "pi_arr", "pi_arr_R"])
        w.writeheader()
        w.writerows(rows)
    dump_json({"created_utc": datetime.now(timezone.utc).isoformat(),
               "written_before_any_score": True,
               "datasets": meta_all,
               "instruction_sha256":
                   "ffb4bde64af8b6c4d6c647bc0d8b90e2191b945946e1cedc76e47dc08f1d189d"},
              OUT / "WEIGHTS_META.json")
    print("wrote", OUT / "WEIGHTS.csv", "| sha256", sha256_file(OUT / "WEIGHTS.csv")[:16])


def read_weights() -> dict[str, dict[str, np.ndarray]]:
    df = pd.read_csv(OUT / "WEIGHTS.csv")
    out = {}
    for ds, g in df.groupby("dataset"):
        out[ds] = {"mu": g["mu"].to_numpy(float), "pi_arr": g["pi_arr"].to_numpy(float),
                   "pi_arr_R": g["pi_arr_R"].to_numpy(float),
                   "group_id": g["group_id"].astype(str).tolist()}
    return out


# ------------------------------------------------------------------- I-P1: scoring
def score_run(ctx: dict, method: str, seed: int) -> dict:
    """Per-group test MSE from the saved checkpoint (the construction of evidence_headroom.py)."""
    base = (E3 if method in M_MAIN else E4) / ctx["dataset"] / method / ("seed%d" % seed)
    ckpt = torch.load(base / "checkpoints/final.pt", map_location="cpu", weights_only=False)
    state = ckpt["state_dict"] if isinstance(ckpt, dict) and "state_dict" in ckpt else ckpt
    model = ctx["factory"](ctx["ds"].num_spatial, seed=seed)
    model.load_state_dict(state)
    model.eval()

    class _M:
        pass

    holder = _M()
    holder.model = model
    pred = ctx["predict"](holder, ctx["ds"], split="test")
    groups = pred["groups"]
    mse_by_int = {}
    for g in sorted(set(int(x) for x in groups.tolist())):
        m = groups == g
        mse_by_int[g] = float(np.mean((pred["y_true"][m] - pred["y_pred"][m]) ** 2))
    mse = np.zeros(len(ctx["gids"]), dtype=np.float64)
    for i, name in enumerate(ctx["gids"]):
        mse[i] = mse_by_int[ctx["str_to_int"][str(name)]]
    if not np.any(mse > 0):
        raise RuntimeError("degenerate group MSE for %s/%s/seed%d" % (ctx["dataset"], method, seed))
    wm = json.loads((base / "window_metrics.json").read_text(encoding="utf-8"))
    stored = json.loads((base / "final_metrics.json").read_text(encoding="utf-8"))
    return {"mse": mse, "last_window_active": bool(wm[-1]["active"]),
            "stored_RMSE_mu": float(stored["RMSE_mu"]), "run_dir": str(base),
            "theta_hash": hashlib.sha256(
                json.dumps({k: float(v.abs().sum()) for k, v in state.items()},
                           sort_keys=True).encode()).hexdigest()[:16]}


def weighted_risk(mse: np.ndarray, w: np.ndarray) -> float:
    return float(np.sqrt(np.sum(np.asarray(w, dtype=np.float64) * mse)))


def kendall_tau(a: np.ndarray, b: np.ndarray) -> float:
    return float(stats.kendalltau(a, b).statistic)


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (float(max(0.0, c - h)), float(min(1.0, c + h)))


def boot_mean_ci(values: np.ndarray, rng_label: str) -> tuple[float, float]:
    """Seed bootstrap over the 20 seeds: resample seeds (with all their methods)."""
    rng = np.random.default_rng(BOOT_SEED)
    n = len(values)
    draws = np.empty(BOOT_DRAWS, dtype=np.float64)
    for i in range(BOOT_DRAWS):
        pick = rng.integers(0, n, size=n)
        draws[i] = float(np.mean(values[pick]))
    return (float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5)))


def label_regret(mean_reg: float, lo: float, hi: float) -> str:
    if lo > DELTA:
        return "open"
    if hi < DELTA:
        return "null"
    return "inconclusive"


def stage_p1(methods: list[str] | None = None, max_seeds: int | None = None) -> None:
    methods = methods or M
    seeds = SEEDS if max_seeds is None else SEEDS[:max_seeds]
    W = read_weights()
    TABLES.mkdir(parents=True, exist_ok=True)

    risk_rows: list[dict] = []
    theta_scored: list[dict] = []
    repro: list[dict] = []
    for dataset in DATASETS:
        ctx = load_context(dataset)
        w = W[dataset]
        for method in methods:
            for seed in seeds:
                s = score_run(ctx, method, seed)
                r_mu = weighted_risk(s["mse"], w["mu"])
                r_arr = weighted_risk(s["mse"], w["pi_arr"])
                r_arrR = weighted_risk(s["mse"], w["pi_arr_R"])
                stored = s["stored_RMSE_mu"]
                row = {
                    "dataset": dataset, "method": method, "seed": seed,
                    "R_mu": r_mu, "R_arr": r_arr, "R_arr_R": r_arrR,
                    "b": (r_arr - r_mu) / r_mu,
                    "b_R": (r_arrR - r_mu) / r_mu,
                    "stored_RMSE_mu": stored,
                    "rel_diff_vs_stored": abs(r_mu - stored) / abs(stored) if stored else None,
                    "last_window_active": s["last_window_active"],
                    "theta_scored": (not s["last_window_active"]),
                    "run_dir": s["run_dir"].replace(str(ROOT) + "\\", "").replace("\\", "/"),
                }
                risk_rows.append(row)
                if not s["last_window_active"]:
                    theta_scored.append({k: row[k] for k in
                                         ("dataset", "method", "seed", "R_mu", "stored_RMSE_mu",
                                          "rel_diff_vs_stored", "run_dir")})
                repro.append({"dataset": dataset, "method": method, "seed": seed,
                              "last_window_active": s["last_window_active"],
                              "rel_diff_vs_stored": row["rel_diff_vs_stored"],
                              "pass_1e-8": (row["rel_diff_vs_stored"] is not None
                                            and row["rel_diff_vs_stored"] <= 1e-8)})
            print("  scored %-12s %-26s seeds %d" % (dataset, method, len(seeds)), flush=True)

    with (OUT / "tables" / "RISK_ROWS.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(risk_rows[0].keys()))
        wr.writeheader()
        wr.writerows(risk_rows)
    with (OUT / "THETA_SCORED.csv").open("w", newline="", encoding="utf-8") as fh:
        if theta_scored:
            wr = csv.DictWriter(fh, fieldnames=list(theta_scored[0].keys()))
            wr.writeheader()
            wr.writerows(theta_scored)
        else:
            fh.write("dataset,method,seed,R_mu,stored_RMSE_mu,rel_diff_vs_stored,run_dir\n")
    with (OUT / "tables" / "REPRODUCTION.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(repro[0].keys()))
        wr.writeheader()
        wr.writerows(repro)

    misses = [r for r in repro if not r["pass_1e-8"] and r["last_window_active"]]
    print("\nreproduction check: %d rows, %d active-window misses (tol 1e-8 relative), "
          "%d theta-scored cell(s)" % (len(repro), len(misses), len(theta_scored)))
    for m in misses[:20]:
        print("   MISS %-12s %-26s seed%d rel=%.3e"
              % (m["dataset"], m["method"], m["seed"], m["rel_diff_vs_stored"]))
    dump_json({"n_rows": len(repro), "n_active_misses": len(misses),
               "n_theta_scored": len(theta_scored),
               "tol": 1e-8, "misses": misses},
              OUT / "REPRODUCTION_CHECK.json")
    if misses:
        raise SystemExit("STOP: reproduction miss outside the theta rule (I-2)")


def stage_summary(exclude_nodesign: bool = False) -> None:
    """I-3/I-4: selection decisions, labels, descriptive readouts, MDE."""
    df = pd.read_csv(OUT / "tables" / "RISK_ROWS.csv")
    methods = [m for m in M if not (exclude_nodesign and m == "raven_wo_design")]
    W = read_weights()
    sel_rows: list[dict] = []
    for dataset in DATASETS:
        sub = df[df.dataset == dataset]
        present = set(sub.method.unique())
        # The scored table always holds the full set; a sensitivity that drops a method
        # from the decision still reads every scored row.
        if not set(methods).issubset(present):
            raise SystemExit("INCOMPLETE: %s scored %s, missing %s"
                             % (dataset, sorted(present), sorted(set(methods) - present)))
        for seed in sorted(sub.seed.unique()):
            cell = sub[sub.seed == seed]
            if not set(methods).issubset(set(cell.method)):
                raise SystemExit("INCOMPLETE: %s seed%d has methods %s"
                                 % (dataset, seed, sorted(cell.method)))
            rec: dict = {"dataset": dataset, "seed": int(seed)}
            for variant, col in (("arr", "R_arr"), ("arrR", "R_arr_R")):
                a = cell.set_index("method")[col].reindex(methods).to_numpy(float)
                b = cell.set_index("method")["R_mu"].reindex(methods).to_numpy(float)
                m_arr = methods[int(np.argmin(a))]
                m_mu = methods[int(np.argmin(b))]
                rec["m_arr_" + variant] = m_arr
                rec["m_mu_" + variant] = m_mu
                rec["d_" + variant] = int(m_arr != m_mu)
                r_mu_mu = float(b[methods.index(m_mu)])
                rec["reg_" + variant] = float((b[methods.index(m_arr)] - r_mu_mu) / r_mu_mu)
                rec["tau_" + variant] = kendall_tau(a, b)
            sel_rows.append(rec)

        arr = np.array([r["reg_arr"] for r in sel_rows if r["dataset"] == dataset], float)
        d = np.array([r["d_arr"] for r in sel_rows if r["dataset"] == dataset], float)
        tau = np.array([r["tau_arr"] for r in sel_rows if r["dataset"] == dataset], float)
        lo, hi = boot_mean_ci(arr, dataset)
        mean_reg = float(arr.mean())
        lab = label_regret(mean_reg, lo, hi)
        k = int(d.sum())
        n = int(d.size)
        dbar = k / n
        wlo, whi = wilson(k, n)
        if dbar in (0.0, 1.0):
            lab = "saturated"
        mde = float(Z_POWER * arr.std(ddof=1) / np.sqrt(n))
        # If every seed yields the same regret (e.g. the same argmin under both criteria),
        # the seed sd is 0 and the MDE collapses to 0.  Report that as a degenerate
        # resolution and never divide by it.
        degenerate = bool(arr.std(ddof=1) == 0.0)
        # sign-flip rates on method pairs
        pairs = [(methods[i], methods[j]) for i in range(len(methods))
                 for j in range(i + 1, len(methods))]
        flips = tot = flips_big = tot_big = 0
        for seed in sorted(sub.seed.unique()):
            cell = sub[sub.seed == seed].set_index("method")
            for a_m, b_m in pairs:
                da = float(cell.loc[a_m, "R_arr"] - cell.loc[b_m, "R_arr"])
                dm = float(cell.loc[a_m, "R_mu"] - cell.loc[b_m, "R_mu"])
                if da == 0 or dm == 0:
                    continue
                tot += 1
                flips += int(np.sign(da) != np.sign(dm))
                if abs(dm) / float(cell.loc[b_m, "R_mu"]) > DELTA:
                    tot_big += 1
                    flips_big += int(np.sign(da) != np.sign(dm))
        b_rows = sub.set_index(["method", "seed"])
        method_b = {}
        for m in methods:
            v = b_rows.loc[m]["b"].to_numpy(float)
            half = float(stats.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v)))
            method_b[m] = {"mean_b": float(v.mean()), "ci_lo": float(v.mean() - half),
                           "ci_hi": float(v.mean() + half)}
        summary = {
            "dataset": dataset, "n_seeds": n, "n_methods": len(methods),
            "mean_reg": mean_reg, "reg_ci_lo": lo, "reg_ci_hi": hi,
            "label": lab, "delta": DELTA, "mde_80pct": mde, "reg_seed_sd": float(arr.std(ddof=1)),
            "reg_degenerate_all_seeds_equal": degenerate,
            "headroom_vs_mde": (None if degenerate else mean_reg / mde),
            "disagreement_rate": dbar, "disagreement_wilson_lo": wlo,
            "disagreement_wilson_hi": whi, "base_rate_non_degenerate": 0.0 < dbar < 1.0,
            "median_tau": float(np.median(tau)), "mean_tau": float(tau.mean()),
            "sign_flip_rate": flips / tot if tot else None, "sign_flip_n": tot,
            "sign_flip_rate_big_delta": flips_big / tot_big if tot_big else None,
            "sign_flip_n_big_delta": tot_big,
            "mean_reg_arrR": float(np.mean([r["reg_arrR"] for r in sel_rows
                                            if r["dataset"] == dataset])),
            "disagreement_rate_arrR": float(np.mean([r["d_arrR"] for r in sel_rows
                                                     if r["dataset"] == dataset])),
            "median_tau_arrR": float(np.median([r["tau_arrR"] for r in sel_rows
                                                if r["dataset"] == dataset])),
            "methods": methods,
            "method_b": method_b,
        }
        summaries.append(summary)

    with (OUT / "tables" / "SELECTION.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(sel_rows[0].keys()))
        wr.writeheader()
        wr.writerows(sel_rows)
    flat = []
    for s in summaries:
        row = {k: v for k, v in s.items() if k not in ("method_b", "methods")}
        flat.append(row)
    with (OUT / "tables" / "SELECTION_SUMMARY.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(flat[0].keys()))
        wr.writeheader()
        wr.writerows(flat)
    decision = {"created_utc": datetime.now(timezone.utc).isoformat(),
                "instruction": "raven-mcs-estimand-gate-execution-prompt.md",
                "excluded_raven_wo_design": exclude_nodesign,
                "delta": DELTA, "bootstrap": {"draws": BOOT_DRAWS, "seed": BOOT_SEED,
                                              "type": "seed percentile 95%"},
                "summaries": summaries}
    dump_json(decision, OUT / "SELECTION_DECISION.json")
    for s in summaries:
        print("%-12s mean_reg=%+.5f [%+.5f, %+.5f]  label=%-12s dbar=%.3f [%.3f, %.3f]  "
              "MDE=%.5f  tau=%.3f  m_arr=%s  m_mu=%s"
              % (s["dataset"], s["mean_reg"], s["reg_ci_lo"], s["reg_ci_hi"], s["label"],
                 s["disagreement_rate"], s["disagreement_wilson_lo"],
                 s["disagreement_wilson_hi"], s["mde_80pct"], s["median_tau"],
                 sel_rows[0]["m_arr_arr"], sel_rows[0]["m_mu_arr"]))


summaries: list[dict] = []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["p0", "p1", "summary"])
    ap.add_argument("--methods", nargs="*", default=None)
    ap.add_argument("--max-seeds", type=int, default=None)
    ap.add_argument("--exclude-nodesign", action="store_true")
    args = ap.parse_args()
    if args.stage == "p0":
        stage_p0()
    elif args.stage == "p1":
        stage_p1(methods=args.methods, max_seeds=args.max_seeds)
    elif args.stage == "summary":
        stage_summary(exclude_nodesign=args.exclude_nodesign)
    else:
        raise SystemExit("unknown stage %s" % args.stage)


if __name__ == "__main__":
    main()

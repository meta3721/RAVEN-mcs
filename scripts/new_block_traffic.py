"""S0 driver for the NSW-Traffic new-block round (read-only, no training).

Instruction (read-only copy): raven-mcs-new-block-traffic-execution-prompt.md
  sha256 25f580aa4e2824daa931addab39eadee67319a24fc89c11ce7f2cf9aa552bb36
Contract: CCFA-Skills/ccf-experiment-designer.

Outputs (only): results_new_block_traffic/round_v1/
  TRACE_FAMILIES.json   S0-a
  S0_TABLE.csv          S0-b/c/d per family and seed
  S0_VERDICT.json       family choice and go/no-go

Stage `probe` is a read-only reconnaissance of the traffic target structure (no output
files) used to confirm the bundle's group order before S0 is written.
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

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

OUT = ROOT / "results_new_block_traffic" / "round_v1"
E3_TRACES = ROOT / "artifacts/e3_formal_runs_r1/eventtraces/traffic"
E2_TRACES = ROOT / "artifacts/e2_traffic_formal_runs_r1/eventtraces"
E3_RUNS = ROOT / "artifacts/e3_formal_runs_r1/runs/traffic"

SEEDS_ALL = list(range(30001, 30021))
SCREEN_SEEDS = list(range(30001, 30006))
S1_SEEDS = list(range(30001, 30004))
TV_BAR = 0.10
LE2_SHARE_BAR = 0.25
INSTRUCTION_SHA = "25f580aa4e2824daa931addab39eadee67319a24fc89c11ce7f2cf9aa552bb36"


def dump_json(obj, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def entropy(w: np.ndarray) -> float:
    w = np.asarray(w, dtype=float)
    w = w[w > 0]
    w = w / w.sum()
    return float(-np.sum(w * np.log(w)))


# --------------------------------------------------------------- traffic target
def load_traffic():
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset
    from raven_mcs.e3.target_pair.target_wiring import production_target_bundle

    ds = load_paper_dataset(ROOT, "traffic")
    bundle = production_target_bundle(root=ROOT, dataset_name="traffic", dataset=ds)
    mu = np.asarray(bundle["mu"], dtype=np.float64)
    gids = list(bundle["group_id_by_index"])
    return ds, mu, gids, bundle


def probe() -> None:
    ds, mu, gids, bundle = load_traffic()
    atomic = ds.atomic_df
    print("num_groups       :", ds.num_groups)
    print("num_spatial      :", ds.num_spatial)
    print("bundle n_groups  :", bundle["n_groups_runtime"], bundle["n_groups_frozen"])
    print("len(mu)          :", len(mu), " sum:", mu.sum())
    print("gids[:4]         :", gids[:4], " ... gids[-2:]:", gids[-2:])
    print("atomic rows      :", len(atomic), " splits:", atomic["split"].value_counts().to_dict())
    print("target_group nunique:", atomic["target_group"].nunique())
    print("target_group sample :", atomic["target_group"].astype(str).unique()[:5])
    print("has _target_group_str_to_int:", hasattr(ds, "_target_group_str_to_int"))
    if hasattr(ds, "_target_group_str_to_int"):
        m = ds._target_group_str_to_int
        print("  map size:", len(m), " sample:", list(m.items())[:3])
    print("opportunity_stratum nunique:", atomic["opportunity_stratum"].nunique())
    print("opportunity_stratum sample :", atomic["opportunity_stratum"].astype(str).unique()[:3])
    test = atomic.loc[atomic["split"].astype(str) == "test"]
    print("test rows        :", len(test))
    counts = test["target_group"].astype(str).value_counts().to_numpy(float)
    order = np.sort(counts)[::-1]
    hn = float(np.log(len(order)))
    print("group share of test units: top1=%.4f%% top5=%.4f%% H/Hmax=%.4f  n_groups=%d"
          % (100 * order[0] / order.sum(), 100 * order[:5].sum() / order.sum(),
             entropy(order) / hn, len(order)))
    ev = pd.read_parquet(E3_TRACES / "seed30001/training_eventtrace/events.parquet")
    print("e3 trace seed30001 rows:", len(ev), " cols:", sorted(ev.columns)[:8])
    print("  window_id range:", int(ev.window_id.min()), int(ev.window_id.max()))
    print("  client_id sample:", ev.client_id.astype(str).unique()[:4])
    print("  U value counts:", ev.U.value_counts().to_dict())


# ------------------------------------------------------------------ S0-a families
def eventtrace_paths(family: str, seed: int) -> pathlib.Path:
    if family == "e3_complete_aligned":
        return E3_TRACES / ("seed%d" % seed) / "training_eventtrace/events.parquet"
    return E2_TRACES / ("%d" % seed) / family / "training_eventtrace/events.parquet"


def enumerate_families() -> dict:
    e2_conditions = sorted(p.name for p in (E2_TRACES / "30001").iterdir() if p.is_dir())
    families = ["e3_complete_aligned"] + e2_conditions
    out = {"created_utc": now(), "instruction_sha256": INSTRUCTION_SHA,
           "roots": {"e3": str(E3_TRACES.relative_to(ROOT)).replace("\\", "/"),
                     "e2": str(E2_TRACES.relative_to(ROOT)).replace("\\", "/")},
           "families": {}}
    for fam in families:
        seeds = [s for s in SEEDS_ALL if eventtrace_paths(fam, s).is_file()]
        per_seed = {}
        for s in seeds:
            p = eventtrace_paths(fam, s)
            per_seed[str(s)] = {"path": str(p.relative_to(ROOT)).replace("\\", "/"),
                                "bytes": p.stat().st_size, "sha256": sha256_file(p)}
        missing = [s for s in SEEDS_ALL if s not in seeds]
        combined = hashlib.sha256(
            json.dumps({k: v["sha256"] for k, v in sorted(per_seed.items())},
                       sort_keys=True).encode()).hexdigest()
        out["families"][fam] = {
            "n_seeds": len(seeds), "seeds": seeds, "missing_seeds": missing,
            "covers_30001_30020": len(missing) == 0,
            "family_content_sha256": combined, "per_seed": per_seed,
        }
    return out


# ------------------------------------------------------------------- S0-b and S0-c
def family_measurements(family: str, seeds: list[int], mu: np.ndarray, gids: list[str],
                        unit_group: dict, unit_split: dict) -> list[dict]:
    idx = {str(g): i for i, g in enumerate(gids)}
    rows = []
    for seed in seeds:
        ev = pd.read_parquet(eventtrace_paths(family, seed))
        counts = np.zeros(len(gids), dtype=np.float64)
        n_units = n_test_dropped = n_unmapped = 0
        # S0-c: per-window count of distinct clients delivering >= 1 U=1 unit
        per_window: dict[int, set] = {}
        for row in ev.itertuples(index=False):
            if int(row.U) != 1:
                continue
            cid = str(row.client_id)
            raw = row.risk_set_unit_ids
            ids = json.loads(raw) if isinstance(raw, str) else list(raw)
            got_any = False
            for uid_raw in ids:
                uid = str(uid_raw)
                if unit_split.get(uid) == "test":
                    n_test_dropped += 1
                    continue
                g = unit_group.get(uid)
                if g is None or str(g) not in idx:
                    n_unmapped += 1
                    continue
                counts[idx[str(g)]] += 1.0
                n_units += 1
                got_any = True
            if got_any:
                per_window.setdefault(int(row.window_id), set()).add(cid)
        if n_units == 0:
            raise RuntimeError("empty arrival frame %s seed%d" % (family, seed))
        pi = counts / n_units
        tv = 0.5 * float(np.abs(pi - mu).sum())
        l1 = float(np.abs(pi - mu).sum())
        wc = np.array([len(v) for v in per_window.values()], dtype=float)
        rows.append({
            "family": family, "seed": seed,
            "n_delivered_test_dropped": n_test_dropped, "n_unmapped": n_unmapped,
            "n_delivered_units": n_units,
            "TV_pi_arr_mu": tv, "L1_pi_arr_mu": l1,
            "pi_arr_top1_share": float(pi.max()),
            "pi_arr_top5_share": float(np.sort(pi)[::-1][:5].sum()),
            "mu_top1_share": float(mu.max()),
            "mu_top5_share": float(np.sort(mu)[::-1][:5].sum()),
            "mu_1_minus_H_over_Hmax": 1.0 - entropy(mu) / float(np.log(len(mu))),
            "n_windows_with_delivery": int(len(wc)),
            "mean_clients_per_window": float(wc.mean()) if wc.size else None,
            "share_windows_le2": float((wc <= 2).mean()) if wc.size else None,
            "max_clients_per_window": float(wc.max()) if wc.size else None,
        })
    return rows


# ------------------------------------------------------------------------- S0-d
def error_heterogeneity(ds, mu: np.ndarray, gids: list[str], arm: str, seed: int) -> dict:
    import torch
    from raven_mcs.e3.real_runner.runner import _predict
    from raven_mcs.models.common_ndmf import deterministic_common_ndmf

    run = E3_RUNS / arm / ("seed%d" % seed)
    obj = torch.load(run / "checkpoints/final.pt", map_location="cpu", weights_only=False)
    state = obj["state_dict"] if isinstance(obj, dict) and "state_dict" in obj else obj
    model = deterministic_common_ndmf(ds.num_spatial, seed=seed)
    model.load_state_dict(state)
    model.eval()

    class _H:
        pass

    holder = _H()
    holder.model = model
    pred = _predict(holder, ds, split="test")
    groups = pred["groups"]

    class _I:
        "per-group mean squared error keyed by the integer group id"
    mse_by_int = {}
    for g in sorted(set(int(x) for x in groups.tolist())):
        m = groups == g
        mse_by_int[g] = float(np.mean((pred["y_true"][m] - pred["y_pred"][m]) ** 2))
    # the traffic dataset exposes no str->int map (the e3 class keeps spatial×time h), so
    # index the frozen mu by the integer group id it carries
    if hasattr(ds, "_target_group_str_to_int"):
        s2i = {str(k): int(v) for k, v in ds._target_group_str_to_int.items()}
        mse = np.array([mse_by_int[s2i[str(g)]] for g in gids], dtype=float)
    else:
        ints = sorted(mse_by_int)
        if len(ints) != len(mu):
            raise RuntimeError("group-count mismatch: %d mse groups vs %d mu entries"
                               % (len(ints), len(mu)))
        mse = np.array([mse_by_int[i] for i in ints], dtype=float)
    w_tar = mu / mu.sum()
    w_uni = np.ones_like(mu) / len(mu)
    r_tar = float(np.sqrt(np.sum(w_tar * mse)))
    r_uni = float(np.sqrt(np.sum(w_uni * mse)))
    r_best = float(np.sqrt(mse.min()))
    r_worst = float(np.sqrt(mse.max()))
    stored = json.loads((run / "final_metrics.json").read_text(encoding="utf-8"))["RMSE_mu"]
    return {"arm": arm, "seed": seed, "RMSE_mu_tar": r_tar, "stored_RMSE_mu": float(stored),
            "rel_diff_vs_stored": abs(r_tar - float(stored)) / abs(float(stored)),
            "RMSE_mu_uniform": r_uni, "RMSE_group_best": r_best, "RMSE_group_worst": r_worst,
            "spread_worst_over_best": r_worst / r_best,
            "uniform_minus_target_pct": 100.0 * (r_uni - r_tar) / r_tar,
            "n_groups": int(len(mu))}


def stage_s0() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ds, mu, gids, bundle = load_traffic()
    atomic = ds.atomic_df
    unit_group = dict(zip(atomic["unit_id"].astype(str), atomic["target_group"].astype(str)))
    unit_split = dict(zip(atomic["unit_id"].astype(str), atomic["split"].astype(str)))

    fams = enumerate_families()
    dump_json(fams, OUT / "TRACE_FAMILIES.json")
    print("families:")
    for name, f in fams["families"].items():
        print("  %-28s seeds %2d  covers 30001-30020: %s"
              % (name, f["n_seeds"], f["covers_30001_30020"]))

    rows = []
    for name, f in fams["families"].items():
        if not f["covers_30001_30020"]:
            continue
        rows.extend(family_measurements(name, SCREEN_SEEDS, mu, gids, unit_group, unit_split))
    df = pd.DataFrame(rows)

    for seed in (30001, 30002):
        for arm in ("central_all", "central_delivered"):
            h = error_heterogeneity(ds, mu, gids, arm, seed)
            print("  S0-d %-18s seed%d RMSE_tar=%.5f (stored %.5f, rel %.2e) uniform=%.5f "
                  "best=%.5f worst=%.5f spread=%.3f"
                  % (arm, seed, h["RMSE_mu_tar"], h["stored_RMSE_mu"], h["rel_diff_vs_stored"],
                     h["RMSE_mu_uniform"], h["RMSE_group_best"], h["RMSE_group_worst"],
                     h["spread_worst_over_best"]))
            rows.append({"family": "e3_complete_aligned", "seed": seed,
                         "heterogeneity_arm": arm,
                         **{k: v for k, v in h.items()}})
    pd.DataFrame(rows).to_csv(OUT / "S0_TABLE.csv", index=False)

    # ---- family selection rule (fixed in §2, applied verbatim)
    elig = []
    for name in fams["families"]:
        sub = df[df.family == name]
        if sub.empty:
            continue
        mean_tv = float(sub["TV_pi_arr_mu"].mean())
        le2 = float(sub["share_windows_le2"].mean())
        elig.append({"family": name, "mean_tv": mean_tv, "mean_share_le2": le2,
                     "n_screen_seeds": int(len(sub)),
                     "passes_le2_bar": le2 < LE2_SHARE_BAR, "passes_tv_bar": mean_tv >= TV_BAR})
    cands = [e for e in elig if e["passes_le2_bar"]]
    chosen = max(cands, key=lambda e: e["mean_tv"]) if cands else None
    verdict = {"created_utc": now(), "instruction_sha256": INSTRUCTION_SHA,
               "tv_bar": TV_BAR, "le2_share_bar": LE2_SHARE_BAR,
               "screen_seeds": SCREEN_SEEDS, "eligibility": elig,
               "chosen_family": chosen["family"] if chosen else None,
               "chosen_mean_tv": chosen["mean_tv"] if chosen else None}
    if chosen is None or chosen["mean_tv"] < TV_BAR:
        verdict["go"] = False
        verdict["failed"] = "N2"
        verdict["reason"] = ("no family with S0-c <=2 share < 25 % reaches mean TV >= 0.10"
                             if chosen is None else
                             "best admissible family has mean TV %.6f < %.2f"
                             % (chosen["mean_tv"], TV_BAR))
    else:
        verdict["go"] = True
        verdict["needs_central_delivered_on_chosen_family"] = (
            chosen["family"] != "e3_complete_aligned")
    dump_json(verdict, OUT / "S0_VERDICT.json")
    print("\nS0 verdict: go = %s  chosen = %s  mean TV = %s"
          % (verdict["go"], verdict.get("chosen_family"),
             verdict.get("chosen_mean_tv")))
    for e in elig:
        print("  %-28s meanTV=%.4f  <=2 share=%.3f  TV>=0.10:%s  le2<0.25:%s"
              % (e["family"], e["mean_tv"], e["mean_share_le2"], e["passes_tv_bar"],
                 e["passes_le2_bar"]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["probe", "s0"])
    args = ap.parse_args()
    if args.stage == "probe":
        probe()
    else:
        stage_s0()


if __name__ == "__main__":
    main()

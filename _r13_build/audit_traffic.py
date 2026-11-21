"""Read-only numeric audit of the NSW-Traffic claims (main.tex lines 2210-2215).

Computes:
  A) S0-c statistic: mean active clients per window from the raw eventtraces
     (replicating scripts/new_block_traffic.py::family_measurements verbatim,
     plus pooled / unit-weighted alternatives) and from the run-side
     window_metrics.json roll-ups.
  B) Frozen federated arm RMSE_mu means over 20 seeds and the spread among the
     four federated arms under three denominators.
  C) S1 ladder: per-level means, ratio_to_c, and ratio-1 percentages against the
     e3 central_delivered mean on the S1 seeds.
No writes outside _r13_build.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
ROUND = ROOT / "results_new_block_traffic" / "round_v1"
E3_TRACES = ROOT / "artifacts/e3_formal_runs_r1/eventtraces/traffic"
E2_RUNS = ROOT / "artifacts/e2_traffic_formal_runs_r1/runs"
E3_RUNS = ROOT / "artifacts/e3_formal_runs_r1/runs/traffic"
S1_RUNS = ROUND / "runs/s1/fedavg_window"

SEEDS20 = list(range(30001, 30021))
SCREEN5 = list(range(30001, 30006))
S1_SEEDS = [30001, 30002, 30003]


def jload(p: pathlib.Path):
    return json.loads(p.read_text(encoding="utf-8"))


print("=" * 72)
print("PART A0 - eventtrace files present")
for s in SEEDS20:
    p = E3_TRACES / ("seed%d" % s) / "training_eventtrace/events.parquet"
    if s <= 30006 or not p.is_file():
        print("  seed%d exists=%s" % (s, p.is_file()))

# ---------------------------------------------------------------- dataset maps
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

ok_ds = False
try:
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset
    from raven_mcs.e3.target_pair.target_wiring import production_target_bundle

    ds = load_paper_dataset(ROOT, "traffic")
    atomic = ds.atomic_df
    bundle = production_target_bundle(root=ROOT, dataset_name="traffic", dataset=ds)
    mu = np.asarray(bundle["mu"], dtype=np.float64)
    gids = [str(g) for g in bundle["group_id_by_index"]]
    unit_group = dict(zip(atomic["unit_id"].astype(str), atomic["target_group"].astype(str)))
    unit_split = dict(zip(atomic["unit_id"].astype(str), atomic["split"].astype(str)))
    ok_ds = True
    print("dataset loaded: n_groups=%d  atomic_rows=%d" % (len(gids), len(atomic)))
except Exception as exc:  # noqa: BLE001
    print("DATASET LOAD FAILED:", type(exc).__name__, exc)

# --------------------------------------------------------- A1 trace-side S0-c
def trace_measure(family: str, seeds: list[int]) -> pd.DataFrame:
    """Verbatim replica of new_block_traffic.family_measurements, plus extras."""
    idx = {g: i for i, g in enumerate(gids)}
    rows = []
    for seed in seeds:
        ev = pd.read_parquet(E3_TRACES / ("seed%d" % seed) / "training_eventtrace/events.parquet")
        counts = np.zeros(len(gids), dtype=np.float64)
        n_units = n_test_dropped = n_unmapped = 0
        per_window: dict[int, set] = {}
        units_per_window: dict[int, int] = {}
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
                units_per_window[int(row.window_id)] = units_per_window.get(
                    int(row.window_id), 0) + 1
            if got_any:
                per_window.setdefault(int(row.window_id), set()).add(cid)
        pi = counts / n_units
        tv = 0.5 * float(np.abs(pi - mu).sum())
        wc = np.array([len(v) for v in per_window.values()], dtype=float)
        uc = np.array([units_per_window[k] for k in per_window], dtype=float)
        rows.append({
            "family": family, "seed": seed,
            "n_delivered_units": n_units,
            "n_test_dropped": n_test_dropped, "n_unmapped": n_unmapped,
            "TV_pi_arr_mu": tv,
            "n_windows_with_delivery": int(len(wc)),
            "sum_clients_over_windows": float(wc.sum()),
            "mean_clients_per_window": float(wc.mean()) if wc.size else None,
            "share_windows_le2": float((wc <= 2).mean()) if wc.size else None,
            "max_clients_per_window": float(wc.max()) if wc.size else None,
            "unit_weighted_mean_clients": (float((wc * uc).sum() / uc.sum())
                                           if uc.sum() else None),
        })
    return pd.DataFrame(rows)


if ok_ds:
    print("=" * 72)
    print("PART A1 - trace-side per-seed (screen seeds 30001-30005, e3_complete_aligned)")
    tr5 = trace_measure("e3_complete_aligned", SCREEN5)
    cols = ["seed", "n_windows_with_delivery", "mean_clients_per_window",
            "share_windows_le2", "max_clients_per_window", "sum_clients_over_windows",
            "unit_weighted_mean_clients", "TV_pi_arr_mu"]
    print(tr5[cols].to_string(index=False))
    print("  MEAN OF PER-SEED MEANS (what S0_REPORT prints) = %.6f"
          % tr5["mean_clients_per_window"].mean())
    print("  POOLED mean over all windows                = %.6f"
          % (tr5["sum_clients_over_windows"].sum() / tr5["n_windows_with_delivery"].sum()))
    print("  total windows (5 seeds)                     = %d"
          % tr5["n_windows_with_delivery"].sum())
    print("  MEAN OF PER-SEED <=2 shares (S0_REPORT)      = %.6f"
          % tr5["share_windows_le2"].mean())
    print("  POOLED <=2 share                            = %.6f"
          % (float((tr5["share_windows_le2"] * tr5["n_windows_with_delivery"]).sum())
             / tr5["n_windows_with_delivery"].sum()))
    uw = float((tr5["unit_weighted_mean_clients"]
                * tr5["n_windows_with_delivery"]).sum()
               / tr5["n_windows_with_delivery"].sum())
    print("  unit-weighted mean clients/window           = %.6f" % uw)

    print("=" * 72)
    print("PART A2 - trace-side over ALL 20 seeds (seeds 30001-30020)")
    tr20 = trace_measure("e3_complete_aligned", SEEDS20)
    print(tr20[cols].to_string(index=False))
    print("  MEAN OF PER-SEED MEANS (20 seeds) = %.6f"
          % tr20["mean_clients_per_window"].mean())
    print("  POOLED mean over all windows      = %.6f"
          % (tr20["sum_clients_over_windows"].sum() / tr20["n_windows_with_delivery"].sum()))
    print("  total windows (20 seeds)          = %d"
          % tr20["n_windows_with_delivery"].sum())
    print("  MEAN OF PER-SEED <=2 shares       = %.6f"
          % tr20["share_windows_le2"].mean())
    tr5.to_csv(ROOT / "_r13_build/out_trace5.csv", index=False)
    tr20.to_csv(ROOT / "_r13_build/out_trace20.csv", index=False)

    # ---- compare against S0_TABLE.csv as written
    s0 = pd.read_csv(ROUND / "S0_TABLE.csv")
    sub = s0[(s0.family == "e3_complete_aligned") & (s0.seed.isin(SCREEN5))]
    sub = sub[sub.mean_clients_per_window.notna()]
    m = sub.merge(tr5, on="seed", suffixes=("_table", "_recomp"))
    print("  max |table - recomputed| mean_clients_per_window = %.3e"
          % float(np.abs(m.mean_clients_per_window_table
                         - m.mean_clients_per_window_recomp).max()))
    print("  max |table - recomputed| share_windows_le2       = %.3e"
          % float(np.abs(m.share_windows_le2_table - m.share_windows_le2_recomp).max()))
    print("  max |table - recomputed| TV_pi_arr_mu            = %.3e"
          % float(np.abs(m.TV_pi_arr_mu_table - m.TV_pi_arr_mu_recomp).max()))

# --------------------------------------------------------- A3 run-side roll-up
print("=" * 72)
print("PART A3 - run-side window_metrics.json roll-ups (mean a_r_size over active windows)")
for arm in ("debt_cal", "inst_cal", "local_hajek", "raven_simoracle", "central_all",
            "central_delivered"):
    per_seed = []
    for s in SEEDS20:
        p = E3_RUNS / arm / ("seed%d" % s) / "window_metrics.json"
        if not p.is_file():
            continue
        wm = jload(p)
        act = [w for w in wm if w.get("active")]
        sizes = np.array([float(w["a_r_size"]) for w in act], dtype=float)
        pairs = np.array([len(w["active_clients"]) for w in act], dtype=float)
        per_seed.append({"seed": s, "n_active_windows": len(act),
                         "mean_ar": float(sizes.mean()), "share_le2": float((sizes <= 2).mean()),
                         "max_ar": float(sizes.max()),
                         "mean_len_active_clients": float(pairs.mean()),
                         "ar_eq_len": bool(np.all(sizes == pairs))})
    if not per_seed:
        print("  %-18s no window_metrics.json found" % arm)
        continue
    d = pd.DataFrame(per_seed)
    pooled_n = d.n_active_windows.sum()
    print("  %-18s seeds=%2d  n_active(pooled)=%5d  mean_of_seed_means=%.4f  "
          "pooled_mean=%.4f  mean_share_le2=%.5f  max=%g  ar==len(active_clients)=%s"
          % (arm, len(d), pooled_n, d.mean_ar.mean(),
             float((d.mean_ar * d.n_active_windows).sum() / pooled_n),
             d.share_le2.mean(), d.max_ar.max(), bool(d.ar_eq_len.all())))
    d.to_csv(ROOT / ("_r13_build/out_runside_%s.csv" % arm), index=False)

print("  --- run-side for the fresh S1 runs (federated fedavg_window, ls5/10/20, 3 seeds) ---")
for ls in (5, 10, 20):
    per_seed = []
    for s in S1_SEEDS:
        p = S1_RUNS / ("ls%d" % ls) / ("seed%d" % s) / "window_metrics.json"
        wm = jload(p)
        act = [w for w in wm if w.get("active")]
        sizes = np.array([float(w["a_r_size"]) for w in act], dtype=float)
        per_seed.append((len(act), float(sizes.mean()), float((sizes <= 2).mean()),
                         float(sizes.max())))
    d = pd.DataFrame(per_seed, columns=["n_active", "mean_ar", "share_le2", "max_ar"])
    print("  ls=%-3d  n_active=%s  mean_of_seed_means=%.4f  pooled=%.4f  share_le2_mean=%.5f"
          % (ls, list(d.n_active), d.mean_ar.mean(),
             float((d.mean_ar * d.n_active).sum() / d.n_active.sum()), d.share_le2.mean()))

# ------------------------------------------------------ B: frozen arm RMSE_mu
print("=" * 72)
print("PART B - frozen e3 arms, RMSE_mu per-seed-pooled means over 20 seeds")
arm_seed = {}
for arm in ("central_all", "central_delivered", "debt_cal", "inst_cal", "local_hajek",
            "raven_simoracle"):
    vals = {}
    for s in SEEDS20:
        p = E3_RUNS / arm / ("seed%d" % s) / "final_metrics.json"
        if p.is_file():
            vals[s] = float(jload(p)["RMSE_mu"])
    arm_seed[arm] = vals
    a = np.array(list(vals.values()))
    print("  %-18s n=%2d  mean=%.9f  sd=%.9f  min=%.6f  max=%.6f"
          % (arm, len(a), a.mean(), a.std(ddof=1), a.min(), a.max()))

fed4 = ["debt_cal", "inst_cal", "local_hajek", "raven_simoracle"]
means4 = {a: float(np.mean(list(arm_seed[a].values()))) for a in fed4}
print("  four federated members (name -> mean RMSE_mu):")
for a in fed4:
    print("    %-18s %.9f" % (a, means4[a]))
mx, mn = max(means4.values()), min(means4.values())
mean4 = float(np.mean(list(means4.values())))
cen = float(np.mean(list(arm_seed["central_delivered"].values())))
print("  max-min (absolute)                = %.9f" % (mx - mn))
print("  spread / mean(4 members)          = %.9e = %.6f %%" % ((mx - mn) / mean4,
                                                                 100 * (mx - mn) / mean4))
print("  spread / min(4 members)           = %.6f %%" % (100 * (mx - mn) / mn))
print("  spread / max(4 members)           = %.6f %%" % (100 * (mx - mn) / mx))
print("  spread / central_delivered(20sd)  = %.6f %%" % (100 * (mx - mn) / cen))
print("  central_delivered 20-seed mean    = %.9f" % cen)
print("  per-seed values:")
for a in fed4:
    print("    %-18s %s" % (a, " ".join("%.6f" % arm_seed[a][s] for s in sorted(arm_seed[a]))))

# ------------------------------------------------------------------ C: ladder
print("=" * 72)
print("PART C - S1 ladder recomputation")
c_s1 = float(np.mean([float(jload(E3_RUNS / "central_delivered" / ("seed%d" % s)
                                 / "final_metrics.json")["RMSE_mu"]) for s in S1_SEEDS]))
print("  c = mean central_delivered RMSE_mu on seeds 30001-30003 (e3 frozen) = %.12f" % c_s1)
print("  per-seed central_delivered: %s"
      % ["%.9f" % float(jload(E3_RUNS / "central_delivered" / ("seed%d" % s)
                              / "final_metrics.json")["RMSE_mu"]) for s in S1_SEEDS])
print("  1.01*c = %.12f" % (1.01 * c_s1))

rows = []
for ls in (2, 5, 10, 20):
    srcs, vals = [], {}
    for s in S1_SEEDS:
        if ls == 2:
            p = E2_RUNS / ("%d" % s) / "complete_aligned" / "fedavg_window" / "final_metrics.json"
            src = "sealed_e2"
        else:
            p = S1_RUNS / ("ls%d" % ls) / ("seed%d" % s) / "final_metrics.json"
            src = "fresh_e3"
        v = float(jload(p)["RMSE_mu"])
        vals[s] = v
        srcs.append(src)
    mean_v = float(np.mean(list(vals.values())))
    rows.append({"local_steps": ls, "n": len(vals), "mean": mean_v,
                 "min": min(vals.values()), "max": max(vals.values()),
                 "ratio_to_c": mean_v / c_s1,
                 "pct_above_c": 100 * (mean_v / c_s1 - 1),
                 "source": srcs[0],
                 "ratio_to_c_20seed_central": mean_v / cen,
                 "pct_above_c_20seed_central": 100 * (mean_v / cen - 1),
                 "qualifies_1p01c": bool(mean_v <= 1.01 * c_s1)})
    print("  ls=%-3d src=%-10s per-seed=%s" % (ls, srcs[0],
                                               ["%.9f" % vals[s] for s in S1_SEEDS]))
lad = pd.DataFrame(rows)
print(lad.to_string(index=False))
print("  range of pct_above_c over the 4 rungs = %.6f %% .. %.6f %%"
      % (lad.pct_above_c.min(), lad.pct_above_c.max()))
print("  range of ratio_to_c over the 4 rungs = %.9f .. %.9f"
      % (lad.ratio_to_c.min(), lad.ratio_to_c.max()))
base2 = float(lad.loc[lad.local_steps == 2, "mean"].iloc[0])
best = lad.loc[lad["mean"].idxmin()]
print("  best level: ls=%d mean=%.9f ; (level2-best)/level2 = %.6f %% (fallback needs >= 1 %%)"
      % (best.local_steps, best["mean"], 100 * (base2 - best["mean"]) / base2))
lad.to_csv(ROOT / "_r13_build/out_ladder.csv", index=False)

# compare to S1_LADDER.csv as written
sl = pd.read_csv(ROUND / "S1_LADDER.csv")
print("  S1_LADDER.csv as written:")
print(sl.to_string(index=False))
mm = sl.merge(lad, on="local_steps", suffixes=("_csv", "_recomp"))
print("  max |csv - recomputed| mean_RMSE_mu = %.3e"
      % float(np.abs(mm.mean_RMSE_mu - mm["mean"]).max()))
print("  max |csv - recomputed| ratio_to_c   = %.3e"
      % float(np.abs(mm.ratio_to_c_csv - mm.ratio_to_c_recomp).max()))

# ---------------------------------------------------------------- config check
print("=" * 72)
print("PART D - run config_snapshot local_steps vs directory level (carry-over check)")
for ls in (5, 10, 20):
    for s in S1_SEEDS:
        p = S1_RUNS / ("ls%d" % ls) / ("seed%d" % s) / "config_snapshot.json"
        cfg = jload(p)
        keys = {k: cfg[k] for k in cfg if "local" in k.lower() or "step" in k.lower()
                or "eventtrace" in k.lower() or "trace" in k.lower()}
        print("  ls=%-3d seed%d  %s" % (ls, s, keys))

"""TE2 step 3 (primary cell): 80 runs at kappa = 5 under the injected concentrated target.

Frozen server step (driver mode 'off'), frozen protocol, no src/ edit.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_traffic_e2/round_v1"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "tables").mkdir(parents=True, exist_ok=True)
DRV = OUT / "driver"
sys.path.insert(0, str(DRV))
sys.path.insert(0, str(ROOT / "src"))

import s1p_driver as D  # noqa: E402

ARMS = ["local_hajek", "inst_cal", "debt_cal", "raven_simoracle"]
CONTROL = "local_hajek"
SEEDS = list(range(30001, 30021))
TAG = {a: f"K5_{a}" for a in ARMS}
BOOT_DRAWS, BOOT_SEED = 10000, 20261007

pre = json.loads((OUT / "TE2_FROZEN_PREREG.json").read_text(encoding="utf-8"))
art = json.loads((OUT / "TE2_TARGET_ARTIFACT_KAPPA5.json").read_text(encoding="utf-8"))
D.TARGET_ARTIFACT = art
print(f"target artifact injected: kappa={pre['target_artifact']['kappa']} "
      f"priority={pre['target_artifact']['priority_region']} sha={art['_artifact_sha256'][:16]}", flush=True)

# ---- 1. the 80 runs ----
for arm in ARMS:
    for seed in SEEDS:
        D.run_one("traffic", arm, seed, 2, TAG[arm], "off")
print("all 80 cells attempted", flush=True)

# ---- 2. post-processing: validation error under the concentrated target, K_r, finiteness ----
from raven_mcs.data.target import GroupMapper, TargetBuilder  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test  # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import align_mu_to_dataset, freeze_fixture_target  # noqa: E402
from raven_mcs.e3.stratum_seal.traffic_regions import load_frozen_traffic_station_regions  # noqa: E402

ds = load_paper_dataset(ROOT, "traffic")
station_to_region, _ = load_frozen_traffic_station_regions(ROOT)
code_station = {str(c): sorted(set(s["spatial_id"].astype(str)))[0]
                for c, s in ds.atomic_df.groupby("target_group", observed=True)}

# validation-split concentrated weights, same region multipliers
a2 = ds.atomic_df.copy()
a2["target_group_main"] = pd.Categorical(a2["target_group"]).codes
vb = TargetBuilder(group_mapper=GroupMapper("target_group_main")).build(a2, split="validation")
n_g = int(a2["target_group_main"].max()) + 1
vmu = np.asarray([float(vb.group_mass.get(str(g), 0.0)) for g in range(n_g)])
vreg = {c: station_to_region.get(code_station.get(str(c), "")) for c in range(n_g)}
vw = np.array([pre["target_artifact"]["kappa"] if vreg[c] == pre["target_artifact"]["priority_region"]
               else 1.0 for c in range(n_g)])
vmu5 = vmu * vw
vmu5 = vmu5 / vmu5.sum()
print(f"validation concentrated weights: n={n_g} sum={vmu5.sum():.6f}", flush=True)


def val_score(ck: pathlib.Path) -> float:
    class _Shim:
        pass
    shim = _Shim()
    shim.model = CommonNDMF_from_ckpt(ck, ds.num_spatial)
    pred = _predict(shim, ds, split="validation")
    w = np.asarray(_mu_weights_for_test(pred, vmu5), dtype=np.float64)
    if len(w) == 0:
        return float("nan")
    w = w / w.sum()
    return float(np.sqrt(np.sum(w * (np.asarray(pred["y_pred"], dtype=np.float64)
                                    - np.asarray(pred["y_true"], dtype=np.float64)) ** 2)))


def nonfinite(d: pathlib.Path) -> int:
    import torch
    bad = 0

    def walk(o, depth=0):
        nonlocal bad
        if depth > 8:
            return
        if isinstance(o, dict):
            for v in o.values():
                walk(v, depth + 1)
        elif isinstance(o, list):
            for v in o[:20000]:
                walk(v, depth + 1)
        elif isinstance(o, float) and not math.isfinite(o):
            bad += 1

    for p in sorted(d.rglob("*.json")):
        try:
            walk(json.loads(p.read_text(encoding="utf-8")))
        except Exception:  # noqa: BLE001
            pass
    ck = d / "checkpoints/final.pt"
    if ck.is_file():
        obj = torch.load(ck, map_location="cpu", weights_only=False)
        th = obj["state_dict"] if isinstance(obj, dict) and "state_dict" in obj else obj
        bad += sum(0 if bool(torch.isfinite(v).all()) else 1 for v in th.values())
    return bad


rows = []
for arm in ARMS:
    for seed in SEEDS:
        d = D.RUNS / TAG[arm] / "traffic" / arm / f"seed{seed}"
        fm_p = d / "final_metrics.json"
        if not fm_p.is_file():
            rows.append({"arm": arm, "seed": seed, "missing": True})
            continue
        fm = json.loads(fm_p.read_text(encoding="utf-8"))
        cfg = json.loads((d / "config_snapshot.json").read_text(encoding="utf-8"))
        kr = D.kr_le3_share(d)
        rows.append({"arm": arm, "seed": seed, "missing": False,
                     "test_RMSE_mu": fm.get("RMSE_mu"),
                     "WorstGroupRMSE": fm.get("WorstGroupRMSE"),
                     "Tail_RMSE": fm.get("Tail_RMSE"),
                     "Delta_group": fm.get("Delta_group"),
                     "Delta_c_s": fm.get("Delta_c_s"),
                     "val_RMSE_mu_concentrated": val_score(d / "checkpoints/final.pt"),
                     "kr_le3_share": kr["share_kr_le3"], "n_active": kr["n_active"],
                     "nonfinite": nonfinite(d),
                     "target_artifact_path": cfg.get("target_artifact_path"),
                     "target_artifact_sha256": cfg.get("target_artifact_sha256")})
        print(f"  scored {arm} seed{seed} test={rows[-1]['test_RMSE_mu']} "
              f"val={rows[-1]['val_RMSE_mu_concentrated']:.6f}", flush=True)

with (OUT / "tables/TE2_MAIN.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

# ---- 3. the contrast ----
from scipy.stats import t as tdist

get = {(r["arm"], r["seed"]): r for r in rows if not r.get("missing")}
ctrl = {s: get[(CONTROL, s)]["test_RMSE_mu"] for s in SEEDS if (CONTROL, s) in get}
n = len(ctrl)
t_lo, t_hi = float(tdist.ppf(0.975, n - 1)), float(tdist.ppf(0.80, n - 1))
bar = 0.02 * float(np.mean(list(ctrl.values())))
contrasts = {}
for arm in ARMS:
    if arm == CONTROL:
        continue
    Ds = np.asarray([ctrl[s] - get[(arm, s)]["test_RMSE_mu"] for s in SEEDS if (arm, s) in get
                     and s in ctrl])
    if len(Ds) < 3:
        contrasts[arm] = {"verdict": "insufficient pairs", "n": len(Ds)}
        continue
    nn = len(Ds)
    sd = float(Ds.std(ddof=1))
    mde = (float(tdist.ppf(0.975, nn - 1)) + float(tdist.ppf(0.80, nn - 1))) * sd / math.sqrt(nn)
    rng = np.random.default_rng(BOOT_SEED)
    boot = np.asarray([float(np.mean(rng.choice(Ds, size=nn, replace=True))) for _ in range(BOOT_DRAWS)])
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
    mean = float(Ds.mean())
    cond = {"interval_entirely_favourable": lo > 0,
            "mean_exceeds_own_MDE80": abs(mean) > mde,
            "effect_ge_2pct_of_control": abs(mean) >= bar}
    contrasts[arm] = {"n": nn, "mean_D": mean, "sd_D": sd, "MDE80": mde,
                      "boot_lo": lo, "boot_hi": hi, "control_mean": float(np.mean(list(ctrl.values()))),
                      "conditions": cond, "separated": all(cond.values())}
    print(f"  {CONTROL} - {arm:<16} D={mean:+.6f} sd={sd:.6f} MDE80={mde:.6f} CI=[{lo:+.5f},{hi:+.5f}] "
          f"2%bar={bar:.6f} separated={all(cond.values())}", flush=True)

verdict = {"round": "TE2", "step": 3, "kappa": pre["target_artifact"]["kappa"],
           "priority_region": pre["target_artifact"]["priority_region"],
           "n_pairs": n, "bar_2pct_of_control": bar, "contrasts": contrasts,
           "artifact_injection_verified": sorted({r["target_artifact_path"] for r in rows
                                                  if not r.get("missing")}),
           "artifact_sha_seen": sorted({r["target_artifact_sha256"] for r in rows
                                        if not r.get("missing")}),
           "kr_le3_share_mean": float(np.mean([r["kr_le3_share"] for r in rows if not r.get("missing")])),
           "created_utc": datetime.now(timezone.utc).isoformat()}
(OUT / "TE2_VERDICT.json").write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")
print("\ninjection recorded in config snapshots:", verdict["artifact_injection_verified"])
print("verdict file written")

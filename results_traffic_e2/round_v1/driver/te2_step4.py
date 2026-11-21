"""TE2 alternate step 4: the ceiling ladder. Two settings (kappa=10, single-region limit) x 2 arms
(local_hajek control, raven_simoracle oracle) x 20 seeds = 80 runs, plus the kappa=1 rung from the
frozen tree and the kappa=5 rung from step 3.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_traffic_e2/round_v1"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "tables").mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(OUT / "driver"))
sys.path.insert(0, str(ROOT / "src"))
import s1p_driver as D  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.target_pair.target_wiring import align_mu_to_dataset, freeze_fixture_target  # noqa: E402
from raven_mcs.e3.stratum_seal.traffic_regions import load_frozen_traffic_station_regions  # noqa: E402
from scipy.stats import t as tdist  # noqa: E402

ARMS = ["local_hajek", "raven_simoracle"]
CONTROL, ORACLE = "local_hajek", "raven_simoracle"
SEEDS = list(range(30001, 30021))
PRIO = "region1"
BOOT_DRAWS, BOOT_SEED = 10000, 20261007
FROZEN_TREE = ROOT / "artifacts/e3_formal_runs_r1/runs/traffic"

ds = load_paper_dataset(ROOT, "traffic")
atomic = ds.atomic_df
station_to_region, _ = load_frozen_traffic_station_regions(ROOT)
code_station = {str(c): sorted(set(s["spatial_id"].astype(str)))[0]
                for c, s in atomic.groupby("target_group", observed=True)}
art0 = freeze_fixture_target(atomic, dataset="traffic")
mu0, gids, _ = align_mu_to_dataset(ds, art0)
region_of = {str(g): station_to_region.get(code_station[str(g)]) for g in gids}
print(f"base artifact: {len(gids)} groups, prio={PRIO}, "
      f"prio groups={sum(1 for g in gids if region_of[str(g)] == PRIO)}", flush=True)


def make_artifact(kappa: float | None) -> tuple[dict, dict]:
    """kappa=None means the single-region limit (weight 1 on the priority region, 0 elsewhere)."""
    w = np.array([(1.0 if region_of[str(g)] == PRIO else 0.0) if kappa is None
                  else (kappa if region_of[str(g)] == PRIO else 1.0) for g in gids])
    m = np.asarray(mu0, dtype=float) * w
    m = m / m.sum()
    a = dict(art0)
    a["mu"] = {str(g): float(m[i]) for i, g in enumerate(gids)}
    a["_artifact_path"] = "inline_fixture_freeze(step4)"
    mm, gg, _ = align_mu_to_dataset(ds, a)
    assert list(gg) == list(gids) and np.allclose(np.asarray(mm, float), m, atol=1e-12)
    share = {r: float(sum(m[i] for i, g in enumerate(gids) if region_of[str(g)] == r))
             for r in sorted({"region0", "region1", "region2", "region3"})}
    a["_artifact_sha256"] = hashlib.sha256(
        json.dumps(a["mu"], sort_keys=True, default=str).encode()).hexdigest()
    return a, share


SETTINGS = []
for name, kappa, tag in (("kappa10", 10.0, "K10"), ("single_region", None, "KLIM")):
    a, share = make_artifact(kappa)
    SETTINGS.append({"name": name, "kappa": kappa, "tag": tag, "artifact": a,
                     "top1": max(share.values()), "region_share": share})
    print(f"  {name:<14} top-1 share = {max(share.values()):.4f}  masses = "
          f"{ {k: round(v, 4) for k, v in share.items()} }", flush=True)

# ---- smoke: can the exact single-region target load and run? ----
limit = SETTINGS[1]
D.TARGET_ARTIFACT = limit["artifact"]
fallback = None
try:
    d = D.run_one("traffic", CONTROL, 30001, 2, limit["tag"] + "_smoke", "off", force=True)
    fm = json.loads((d / "final_metrics.json").read_text(encoding="utf-8"))
    ok = fm.get("RMSE_mu") is not None and math.isfinite(float(fm["RMSE_mu"]))
    print(f"  smoke on the exact single-region target: RMSE_mu={fm.get('RMSE_mu')} finite={ok}", flush=True)
    if not ok:
        raise RuntimeError("non-finite metric")
except Exception as exc:  # noqa: BLE001
    fallback = f"{type(exc).__name__}: {exc}"
    print(f"  smoke FAILED on the exact single-region target -> {fallback}", flush=True)
    print("  falling back to kappa=100 (top-1 ~0.97) and recording the deviation", flush=True)
    a100, share100 = make_artifact(100.0)
    SETTINGS[1] = {"name": "near_single_region_kappa100", "kappa": 100.0, "tag": "K100",
                   "artifact": a100, "top1": max(share100.values()), "region_share": share100}
    print(f"  kappa=100 top-1 share = {max(share100.values()):.4f}", flush=True)

# ---- the 80 runs ----
for st in SETTINGS:
    D.TARGET_ARTIFACT = st["artifact"]
    for arm in ARMS:
        for s in SEEDS:
            D.run_one("traffic", arm, s, 2, f"{st['tag']}_{arm}", "off")
print("all 80 cells attempted", flush=True)

# ---- scores ----
def cell(tag, arm, s):
    p = D.RUNS / f"{tag}_{arm}" / "traffic" / arm / f"seed{s}" / "final_metrics.json"
    if not p.is_file():
        return None
    fm = json.loads(p.read_text(encoding="utf-8"))
    cfg = json.loads((p.parent / "config_snapshot.json").read_text(encoding="utf-8"))
    kr = D.kr_le3_share(p.parent)
    return {"tag": tag, "arm": arm, "seed": s, "test_RMSE_mu": fm.get("RMSE_mu"),
            "WorstGroupRMSE": fm.get("WorstGroupRMSE"), "Delta_group": fm.get("Delta_group"),
            "kr_le3_share": kr["share_kr_le3"], "n_active": kr["n_active"],
            "artifact_sha": cfg.get("target_artifact_sha256")}


rows = []
for st in SETTINGS:
    for arm in ARMS:
        for s in SEEDS:
            r = cell(st["tag"], arm, s)
            if r:
                r["setting"] = st["name"]
                r["top1_share"] = st["top1"]
                rows.append(r)
with (OUT / "tables/TE2_STEP4_MAIN.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"scored {len(rows)} cells", flush=True)

# ---- the ceiling ladder ----
def gap(pairs, label):
    Dv = np.asarray(pairs, dtype=float)
    n = len(Dv)
    sd = float(Dv.std(ddof=1))
    mde = (float(tdist.ppf(0.975, n - 1)) + float(tdist.ppf(0.80, n - 1))) * sd / math.sqrt(n)
    rng = np.random.default_rng(BOOT_SEED)
    boot = np.asarray([float(np.mean(rng.choice(Dv, size=n, replace=True))) for _ in range(BOOT_DRAWS)])
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
    return {"rung": label, "n": n, "mean_gap": float(Dv.mean()), "sd": sd, "MDE80": mde,
            "boot_lo": lo, "boot_hi": hi,
            "pct_of_control": None, "interval_excludes_zero": bool(lo > 0 or hi < 0)}


ladder = []
# kappa = 1 from the frozen uniform-target runs
g1 = []
for s in SEEDS:
    a = FROZEN_TREE / CONTROL / f"seed{s}" / "final_metrics.json"
    b = FROZEN_TREE / ORACLE / f"seed{s}" / "final_metrics.json"
    if a.is_file() and b.is_file():
        g1.append(json.loads(a.read_text())["RMSE_mu"] - json.loads(b.read_text())["RMSE_mu"])
r1 = gap(g1, "kappa=1 (frozen uniform target, existing runs)")
r1["control_mean"] = float(np.mean([json.loads((FROZEN_TREE / CONTROL / f"seed{s}" /
                                                 "final_metrics.json").read_text())["RMSE_mu"]
                                    for s in SEEDS]))
ladder.append(r1)
# kappa = 5 from step 3
g5 = []
ctl5 = [r for r in csv.DictReader((OUT / "tables/TE2_MAIN.csv").open(encoding="utf-8"))]
for s in SEEDS:
    a = [r for r in ctl5 if r["arm"] == CONTROL and int(r["seed"]) == s]
    b = [r for r in ctl5 if r["arm"] == ORACLE and int(r["seed"]) == s]
    if a and b:
        g5.append(float(a[0]["test_RMSE_mu"]) - float(b[0]["test_RMSE_mu"]))
r5 = gap(g5, "kappa=5 (step 3, target top-1 0.6322)")
r5["control_mean"] = float(np.mean([float(r["test_RMSE_mu"]) for r in ctl5 if r["arm"] == CONTROL]))
ladder.append(r5)
for st in SETTINGS:
    sel = [r for r in rows if r["setting"] == st["name"]]
    ctl = {r["seed"]: r["test_RMSE_mu"] for r in sel if r["arm"] == CONTROL}
    orc = {r["seed"]: r["test_RMSE_mu"] for r in sel if r["arm"] == ORACLE}
    g = [ctl[s] - orc[s] for s in sorted(set(ctl) & set(orc))]
    r = gap(g, f"{st['name']} (target top-1 {st['top1']:.4f})")
    r["control_mean"] = float(np.mean(list(ctl.values())))
    r["kr_le3_share_mean"] = float(np.mean([x["kr_le3_share"] for x in sel]))
    ladder.append(r)
for r in ladder:
    if r.get("control_mean"):
        r["pct_of_control"] = 100 * r["mean_gap"] / r["control_mean"]
    print(f"  {r['rung']:<48} gap={r['mean_gap']:+.6f} ({r.get('pct_of_control') or 0:+.4f} %) "
          f"sd={r['sd']:.6f} MDE80={r['MDE80']:.6f} CI=[{r['boot_lo']:+.5f},{r['boot_hi']:+.5f}]",
          flush=True)

verdict = {"round": "TE2", "step": "4 (alternate: ceiling ladder)",
           "arms": {"control": CONTROL, "oracle": ORACLE},
           "settings": [{"name": s["name"], "kappa": s["kappa"], "top1": s["top1"],
                         "region_share": s["region_share"], "tag": s["tag"]} for s in SETTINGS],
           "single_region_fallback": fallback,
           "ceiling_ladder": ladder,
           "artifact_shas_recorded_by_runner": sorted({r["artifact_sha"] for r in rows if r.get("artifact_sha")}),
           "created_utc": datetime.now(timezone.utc).isoformat()}
(OUT / "TE2_STEP4_VERDICT.json").write_text(json.dumps(verdict, indent=2, sort_keys=True, default=str),
                                            encoding="utf-8")
print("\nverdict written; single-region fallback:", fallback)

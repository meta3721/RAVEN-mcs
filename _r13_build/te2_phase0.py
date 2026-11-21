"""TE2 Phase 0 — the power gate. Re-scoring only, no training.

Builds the primary-cell concentrated target (kappa = 5 on the priority region), scores the stored
checkpoints of the 20 frozen seeds under it, and computes the paired sd and MDE80.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_traffic_e2/round_v1"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.data.target import GroupMapper, TargetBuilder  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test  # noqa: E402
from raven_mcs.e3.stratum_seal.traffic_regions import load_frozen_traffic_station_regions  # noqa: E402

KAPPA = 5.0
ARMS = ("local_hajek", "inst_cal", "debt_cal", "raven_simoracle")
CONTROL = "local_hajek"

ds = load_paper_dataset(ROOT, "traffic")
atomic = ds.atomic_df
codes = pd.Categorical(atomic["target_group"]).codes
atomic = atomic.assign(_code=codes)
n_groups = int(codes.max()) + 1
station_to_region, region_meta = load_frozen_traffic_station_regions(ROOT)

# code -> station -> region
code_station, code_region, multi = {}, {}, []
for c, sub in atomic.groupby("_code"):
    st = set(sub["spatial_id"].astype(str))
    if len(st) != 1:
        multi.append((int(c), sorted(st)[:4]))
    sid = sorted(st)[0]
    code_station[int(c)] = sid
    code_region[int(c)] = station_to_region.get(sid)
print(f"groups={n_groups}  regions={region_meta['region_count']}  "
      f"groups spanning >1 station: {len(multi)} {multi[:3]}")

tgt = TargetBuilder(group_mapper=GroupMapper("target_group_main")) if False else None
a = atomic.copy()
a["target_group_main"] = a["_code"]
built = TargetBuilder(group_mapper=GroupMapper("target_group_main")).build(a, split="test")
mass1 = np.asarray([float(built.group_mass.get(str(g), 0.0)) for g in range(n_groups)])
mass1 = mass1 / mass1.sum()
print(f"frozen (kappa=1) group mass: sum={mass1.sum():.6f} n_nonzero={(mass1 > 0).sum()}")

regions = sorted({r for r in code_region.values() if r})
region_mass1 = {r: float(sum(mass1[c] for c in range(n_groups) if code_region.get(c) == r))
                for r in regions}
print("frozen region target mass:", {k: round(v, 6) for k, v in region_mass1.items()})
PRIORITY = max(region_mass1, key=region_mass1.get)
print(f"-> priority region by the pre-declared rule (largest frozen target mass): {PRIORITY}")

w = np.array([KAPPA if code_region.get(c) == PRIORITY else 1.0 for c in range(n_groups)])
mass5 = mass1 * w
mass5 = mass5 / mass5.sum()
region_mass5 = {r: float(sum(mass5[c] for c in range(n_groups) if code_region.get(c) == r))
                for r in regions}
print("\nprimary cell (kappa = 5) region mass:",
      {k: f"{v:.4f}" for k, v in sorted(region_mass5.items(), key=lambda kv: -kv[1])})
print(f"  realised top-1 region share = {max(region_mass5.values()):.4f}  (design table assumed 0.6250)")
p5 = mass5[mass5 > 0]
print(f"  effective groups = {float(np.exp(-(p5*np.log(p5)).sum())):.2f} of {n_groups}")

mass_sha = hashlib.sha256(mass5.tobytes()).hexdigest()
print(f"  concentrated weight vector sha256 = {mass_sha}")


def score(ck: pathlib.Path, mu: np.ndarray) -> float:
    class _Shim:
        pass
    shim = _Shim()
    shim.model = CommonNDMF_from_ckpt(ck, ds.num_spatial)
    pred = _predict(shim, ds, split="test")
    wv = np.asarray(_mu_weights_for_test(pred, mu), dtype=np.float64)
    if len(wv) == 0:
        return float("nan")
    wv = wv / wv.sum()
    yp = np.asarray(pred["y_pred"], dtype=np.float64)
    yt = np.asarray(pred["y_true"], dtype=np.float64)
    return float(np.sqrt(np.sum(wv * (yp - yt) ** 2)))


TREE = ROOT / "artifacts/e3_formal_runs_r1/runs/traffic"
seeds = sorted(int(p.name[4:]) for p in (TREE / "local_hajek").glob("seed*"))
print(f"\nseeds available: {len(seeds)}  {seeds[0]}..{seeds[-1]}")

rows = {}
for arm in ARMS:
    vals, vals1 = [], []
    for s in seeds:
        ck = TREE / arm / f"seed{s}" / "checkpoints/final.pt"
        if not ck.is_file():
            print(f"  MISSING {arm} seed{s}")
            continue
        vals.append(score(ck, mass5))
        vals1.append(score(ck, mass1))
    rows[arm] = {"concentrated": vals, "frozen_uniform": vals1}
    print(f"  {arm:<17} concentrated RMSE_mu mean={np.mean(vals):.6f}  "
          f"(frozen target mean={np.mean(vals1):.6f})  n={len(vals)}")

from scipy.stats import t as tdist

n = len(rows[CONTROL]["concentrated"])
t_lo, t_hi = float(tdist.ppf(0.975, n - 1)), float(tdist.ppf(0.80, n - 1))
ctrl = np.asarray(rows[CONTROL]["concentrated"])
bar = 0.02 * float(ctrl.mean())
print(f"\n=== power gate: n={n}, t=({t_lo:.6f}, {t_hi:.6f}), "
      f"2 % of the control's concentrated error = {bar:.6f} ===")
summary = {}
for arm in ARMS:
    if arm == CONTROL:
        continue
    tr = np.asarray(rows[arm]["concentrated"])
    D = ctrl - tr
    sd = float(D.std(ddof=1))
    mde = (t_lo + t_hi) * sd / np.sqrt(n)
    rng = np.random.default_rng(20261007)
    boot = np.asarray([float(np.mean(rng.choice(D, size=n, replace=True))) for _ in range(10000)])
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
    summary[arm] = {"mean_D": float(D.mean()), "sd_D": sd, "MDE80": mde,
                    "boot_lo": lo, "boot_hi": hi, "mean_treatment": float(tr.mean()),
                    "passes": bool(mde <= bar)}
    print(f"  {CONTROL} - {arm:<17} D={D.mean():+.6f} sd={sd:.6f} MDE80={mde:.6f} "
          f"CI=[{lo:+.5f},{hi:+.5f}]  <= 2%bar? {mde <= bar}")

verdict = "CONTINUE" if all(v["passes"] for v in summary.values()) else "STOP"
print(f"\nPHASE 0 VERDICT: {verdict}")

json.dump({"phase": "TE2 Phase 0 power gate", "kappa": KAPPA, "priority_region": PRIORITY,
           "region_mass_frozen": region_mass1, "region_mass_kappa5": region_mass5,
           "mass_sha256": mass_sha, "n_seeds": n, "seeds": seeds,
           "bar_2pct_of_control": bar, "control_mean_concentrated": float(ctrl.mean()),
           "arms": {a: {"concentrated_per_seed": rows[a]["concentrated"],
                        "frozen_target_mean": float(np.mean(rows[a]["frozen_uniform"]))} for a in ARMS},
           "paired_vs_control": summary, "verdict": verdict},
          open(OUT / "TE2_PHASE0.json", "w", encoding="utf-8"), indent=2, sort_keys=True)
print("wrote", (OUT / "TE2_PHASE0.json").relative_to(ROOT).as_posix())

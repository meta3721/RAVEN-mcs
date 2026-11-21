"""Does ANY of the paper's other evidence trees contain arms with skill, or is the degeneracy general?

Walks the candidate trees, derives (dataset, arm, seed) from each checkpoint path, and scores it
through the repository's own prediction path against the best constant predictor under the same
mu weights.  Read-only.
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test  # noqa: E402
from raven_mcs.metrics.accuracy import rmse_mu  # noqa: E402

N_GROUPS = {"sensorscope": 220, "uair": 144, "traffic": 172}
TREES = ["results_h_headroom", "results_h_response_shift", "results_gate_dose",
         "results_w1_ladder", "results_int_r", "results_active_set_repair"]
MAX_PER_ARM = 2  # bound the work


def test_mu(dataset, n_groups: int) -> np.ndarray:
    atomic = dataset.atomic_df.copy()
    if n_groups == 4:
        atomic["target_group_main"] = RepeatableTimeOfDayMapper().map(atomic)
    else:
        atomic["target_group_main"] = pd.Categorical(atomic["target_group"]).codes
    tgt = TargetBuilder(group_mapper=GroupMapper("target_group_main")).build(atomic, split="test")
    return np.asarray([float(tgt.group_mass.get(str(g), 0.0)) for g in range(n_groups)], dtype=np.float64)


class _Shim:
    pass


cache: dict[str, tuple] = {}
for b in ("sensorscope", "uair", "traffic"):
    ds = load_paper_dataset(ROOT, b)
    cache[b] = (ds, test_mu(ds, N_GROUPS[b]))
print("datasets loaded\n")

rows = []
seen = defaultdict(int)
for tree in TREES:
    base = ROOT / tree
    if not base.is_dir():
        continue
    for ck in sorted(base.rglob("final.pt")):
        parts = ck.relative_to(base).parts
        block = next((p for p in parts if p in N_GROUPS), None)
        if block is None:
            continue
        sd_i = next((i for i, p in enumerate(parts) if p.startswith("seed")), None)
        if sd_i is None:
            continue
        seed = parts[sd_i]
        arm = parts[sd_i - 1] if sd_i >= 1 else "?"
        key = (tree, block, arm)
        if seen[key] >= MAX_PER_ARM:
            continue
        seen[key] += 1
        ds, mu = cache[block]
        try:
            shim = _Shim()
            shim.model = CommonNDMF_from_ckpt(ck, ds.num_spatial)
            pred = _predict(shim, ds, split="test")
            yp = np.asarray(pred["y_pred"], dtype=np.float64)
            yt = np.asarray(pred["y_true"], dtype=np.float64)
            w = _mu_weights_for_test(pred, mu)
            if len(w) == 0:
                continue
            w = np.asarray(w, dtype=np.float64)
            w = w / w.sum()
            ybar = float(np.sum(w * yt))
            r_const = float(np.sqrt(np.sum(w * (yt - ybar) ** 2)))
            r_model = rmse_mu(yp, yt, w)
            sd_pred = float(np.sqrt(np.sum(w * (yp - float(np.sum(w * yp))) ** 2)))
            yc, pc = yt - ybar, yp - float(np.sum(w * yp))
            den = float(np.sqrt(np.sum(w * pc**2) * np.sum(w * yc**2)))
            corr = float(np.sum(w * pc * yc) / den) if den > 0 else float("nan")
            rows.append(dict(tree=tree, block=block, arm=arm, seed=seed, RMSE_mu=r_model,
                             best_const=r_const, sd_pred=sd_pred, corr=corr,
                             vs_const_pct=100 * (r_model / r_const - 1)))
        except Exception as exc:  # noqa: BLE001
            rows.append(dict(tree=tree, block=block, arm=arm, seed=seed, error=f"{type(exc).__name__}"))

ok = [r for r in rows if "vs_const_pct" in r]
print(f"scored {len(ok)} checkpoints ({len(rows)-len(ok)} failed/missing weights)\n")
agg = defaultdict(list)
for r in ok:
    agg[(r["tree"], r["block"])].append(r)
print(f"{'tree':<34}{'block':<13}{'n':>4}{'better-than-const':>19}{'best vs_const':>15}{'worst vs_const':>16}{'max|corr|':>11}")
for (tree, block), v in sorted(agg.items()):
    n_beat = sum(1 for r in v if r["vs_const_pct"] < 0)
    print(f"{tree:<34}{block:<13}{len(v):>4}{n_beat:>10}/{len(v):<8}"
          f"{min(r['vs_const_pct'] for r in v):>+14.1f}%{max(r['vs_const_pct'] for r in v):>+15.1f}%"
          f"{max(abs(r['corr']) for r in v):>11.3f}")
print()
print("=== the arms that decide the ceiling: fedavg_window and raven_simoracle ===")
for (tree, block), v in sorted(agg.items()):
    sel = [r for r in v if r["arm"] in ("fedavg_window", "raven_simoracle")]
    if not sel:
        continue
    for r in sel:
        print(f"  {tree:<30}{block:<12}{r['arm']:<18}{r['seed']:<9}"
              f"RMSE_mu={r['RMSE_mu']:9.4f} const={r['best_const']:8.4f} "
              f"sd_pred={r['sd_pred']:7.4f} corr={r['corr']:+.3f} vs_const={r['vs_const_pct']:+8.1f}%")
p = ROOT / "results_server_optimizer/round_v1/PAPER_TREES_VS_CONSTANT.json"
p.write_text(json.dumps(rows, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
print("\nwrote", p)

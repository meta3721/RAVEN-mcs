"""Screen our four datasets for the two conditions a structural projection needs:
target-mass concentration at the aggregation level, and slack in eq:Cr (K_r > 3 windows).
"""
from __future__ import annotations

import glob
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "results_traffic_e1/round_v1/driver"))
from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client  # noqa: E402


def concentration(mass: np.ndarray) -> dict:
    m = np.asarray(mass, dtype=float)
    tot = m.sum()
    if tot <= 0:
        return {}
    p = m / tot
    p = p[p > 0]
    h = float(-(p * np.log(p)).sum())
    n = len(m)
    return {"n_groups": int(n), "top1_share": float(p.max()), "top2_share": float(np.sort(p)[-2:].sum()),
            "effective_groups": float(np.exp(h)), "effective_over_n": float(np.exp(h) / n),
            "groups_for_50pct": int(np.searchsorted(np.cumsum(np.sort(p)[::-1]), 0.5) + 1)}


print(f"{'dataset':<14}{'mapping':<12}{'n_groups':>9}{'top1':>8}{'top2':>8}{'eff.grps':>10}"
      f"{'eff/n':>8}{'grp@50%':>9}")
rows = {}
for name in ("sensorscope", "uair", "traffic", "tdrive_speed"):
    try:
        ds = load_paper_dataset(ROOT, name)
    except Exception as exc:  # noqa: BLE001
        print(f"{name:<14}LOAD FAILED: {type(exc).__name__}: {exc}")
        continue
    atomic = ds.atomic_df
    full_card = int(atomic["target_group"].nunique())
    tod = RepeatableTimeOfDayMapper().map(atomic)
    for label, codes, ng in (("full", pd.Categorical(atomic["target_group"]).codes, full_card),
                             ("4 UTC blocks", tod, int(pd.Series(tod).nunique()))):
        a = atomic.copy()
        a["target_group_main"] = codes
        tgt = TargetBuilder(group_mapper=GroupMapper("target_group_main")).build(a, split="test")
        mass = np.asarray([float(tgt.group_mass.get(str(g), 0.0)) for g in range(ng)])
        c = concentration(mass)
        rows[f"{name}|{label}"] = c
        print(f"{name:<14}{label:<12}{c['n_groups']:>9}{c['top1_share']:>8.4f}{c['top2_share']:>8.4f}"
              f"{c['effective_groups']:>10.1f}{c['effective_over_n']:>8.3f}{c['groups_for_50pct']:>9}")
    try:
        s2c = load_spatial_to_client(ROOT, name)
        print(f"{'':<14}n_clients = {len(set(s2c.values()))}, n_spatial = {ds.num_spatial}, "
              f"n_atomic = {len(atomic)}")
    except Exception as exc:  # noqa: BLE001
        print(f"{'':<14}(client mapping unavailable: {type(exc).__name__})")

print("\n=== eq:Cr slack: K_r = active clients per active window, from frozen window_metrics.json ===")
pats = {
    "sensorscope": "artifacts/e3_formal_runs_r1/runs/sensorscope/*/seed30001/window_metrics.json",
    "uair": "artifacts/e3_formal_runs_r1/runs/uair/*/seed30001/window_metrics.json",
    "traffic": "artifacts/e3_formal_runs_r1/runs/traffic/*/seed30001/window_metrics.json",
    "tdrive_speed": "artifacts/**/tdrive*/**/seed30001/window_metrics.json",
}
slack = {}
for name, pat in pats.items():
    hits = sorted(glob.glob(str(ROOT / pat), recursive=True))
    if not hits:
        print(f"  {name:<14} no window_metrics.json found for this pattern")
        continue
    p = pathlib.Path(hits[0])
    rowsj = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(rowsj, dict):
        rowsj = rowsj.get("windows", rowsj.get("rows", []))
    act = [r for r in rowsj if r.get("active")]
    field = "active_clients" if act and "active_clients" in act[0] else None
    if field is None:
        print(f"  {name:<14} no active_clients field; keys={sorted(act[0].keys()) if act else None}")
        continue
    vals = []
    for r in act:
        v = r[field]
        vals.append(float(len(v)) if isinstance(v, (list, tuple, dict)) else float(v))
    kr = np.asarray(vals, dtype=float)
    le3 = float(np.mean(kr <= 3))
    slack[name] = {"n_active": int(len(kr)), "share_kr_le3": le3, "share_kr_gt3": 1 - le3,
                   "median_kr": float(np.median(kr)), "max_kr": float(kr.max()),
                   "source": p.relative_to(ROOT).as_posix()}
    print(f"  {name:<14} n_active={len(kr):<6} K_r<=3 share={le3:.4f}  K_r>3 share={1-le3:.4f}  "
          f"median K_r={np.median(kr):.0f}  max={kr.max():.0f}   [{p.name} in {p.parent.parent.name}]")

out = {"concentration": rows, "slack": slack,
       "note": "concentration is the test-split deployment target mass per group; slack is the share of "
               "active windows with K_r > 3, where eq:Cr does not force uniform weights"}
(ROOT / "results_text_repairs/round_v1/BLOCK_SCREEN.json").write_text(
    json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print("\nwrote results_text_repairs/round_v1/BLOCK_SCREEN.json")

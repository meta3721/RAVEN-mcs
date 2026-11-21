"""Is each frozen artifact set internally consistent?

Recomputes the runner's own _theta_hash (window_runner.py L253-L261) from the saved checkpoint and
compares it with the last theta_hash_after logged in that run's window_metrics.json.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import torch

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")


def theta_hash(theta: dict) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(theta.items()):
        array = value.detach().cpu().contiguous().numpy()
        digest.update(name.encode("utf-8"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(str(array.shape).encode("ascii"))
        digest.update(array.tobytes())
    return digest.hexdigest()


def load_theta(p: pathlib.Path) -> dict:
    obj = torch.load(p, map_location="cpu", weights_only=False)
    return obj["state_dict"] if isinstance(obj, dict) and "state_dict" in obj else obj


def check(label: str, ckpt: pathlib.Path, wm: pathlib.Path, fm: pathlib.Path | None) -> dict:
    if not ckpt.is_file() or not wm.is_file():
        print(f"  {label}: missing ckpt or window_metrics")
        return {}
    h_ck = theta_hash(load_theta(ckpt))
    rows = json.loads(wm.read_text(encoding="utf-8"))
    last_after = rows[-1].get("theta_hash_after")
    last_before = rows[-1].get("theta_hash_before")
    first_before = rows[0].get("theta_hash_before")
    n_active = sum(1 for r in rows if r.get("active"))
    fm_rmse = None
    if fm is not None and fm.is_file():
        fm_rmse = json.loads(fm.read_text(encoding="utf-8")).get("RMSE_mu")
    ok = (h_ck == last_after)
    print(f"  {label}")
    print(f"     checkpoint _theta_hash          = {h_ck[:24]}")
    print(f"     last theta_hash_after in wm     = {str(last_after)[:24]}   MATCH={ok}")
    print(f"     first theta_hash_before in wm   = {str(first_before)[:24]}")
    print(f"     last  theta_hash_before in wm   = {str(last_before)[:24]}")
    print(f"     active windows={n_active}   final_metrics RMSE_mu={fm_rmse!r}")
    return {"match": ok, "ckpt_hash": h_ck, "last_after": last_after, "n_active": n_active, "rmse": fm_rmse}


print("=== frozen artifacts ===")
frozen = {}
for blk in ("sensorscope", "uair"):
    for arm in ("fedavg_window", "raven"):
        d = ROOT / "artifacts/e3_formal_runs_r1/runs" / blk / arm / "seed30001"
        frozen[(blk, arm)] = check(f"frozen {blk}/{arm}",
                                   d / "checkpoints" / "final.pt",
                                   d / "window_metrics.json",
                                   d / "final_metrics.json")

print()
print("=== this round's re-runs ===")
rerun = {}
for blk in ("sensorscope", "uair"):
    for arm in ("fedavg_window", "raven"):
        d = ROOT / "results_server_optimizer/round_v1/runs/g0_baseline" / blk / arm / "seed30001"
        rerun[(blk, arm)] = check(f"rerun  {blk}/{arm}",
                                  d / "checkpoints" / "final.pt",
                                  d / "window_metrics.json",
                                  d / "final_metrics.json")

print()
print("=== verdict ===")
for key in frozen:
    f, r = frozen[key], rerun.get(key, {})
    print(f"  {key[0]:<12} {key[1]:<15} frozen_internally_consistent={f.get('match')} "
          f"rerun_internally_consistent={r.get('match')} "
          f"rmse frozen={f.get('rmse')!r} rerun={r.get('rmse')!r}")

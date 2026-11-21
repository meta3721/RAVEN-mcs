"""TE1 pre-flight, read-only. Checks the prompt's own STOP condition, the guard behaviour on the
confirm seeds, the exemption in force, and previews the G-const value."""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
S1P = ROOT / "results_server_optimizer/round_v1"
NEW = ROOT / "results_traffic_e1"
sys.path.insert(0, str(ROOT / "src"))

print("=== 1. prompt section 2 STOP check: any seed30006..seed30020 under the S1' tree? ===")
hits = [p for p in S1P.rglob("seed300*") if p.is_dir() and 30006 <= int(p.name[4:]) <= 30020]
print("   matches:", len(hits), [str(p.relative_to(ROOT)) for p in hits[:5]])
print("   ->", "STOP" if hits else "clear, may proceed")

print("\n=== 2. does results_traffic_e1 already exist? ===")
print("   exists:", NEW.exists(), "| driver target exists:", (NEW / "round_v1/driver").exists())

print("\n=== 3. guard behaviour on a CONFIRM seed (traffic, complete_aligned, seed 30006) ===")
from raven_mcs.e3.protocol_closure.reuse_guard import (  # noqa: E402
    assert_schedulable_e3_run, is_reused_e2_traffic_block, E2_TRAFFIC_REUSED_METHODS, FORMAL_SEEDS)
from raven_mcs.e3.canary.traffic_reuse_guard import assert_canary_schedulable  # noqa: E402

print("   sealed methods      :", E2_TRAFFIC_REUSED_METHODS)
print("   formal seed range   :", FORMAL_SEEDS[0], "-", FORMAL_SEEDS[-1])
for arm in ("fedavg_window", "raven_simoracle"):
    print(f"   is_reused_e2_traffic_block(seed 30006, {arm}) =",
          is_reused_e2_traffic_block(dataset="traffic", scenario="complete_aligned", seed=30006,
                                     method=arm))
    for label, kw in (("default", {}), ("exempt", {"allow_reused_traffic_rerun": True})):
        try:
            assert_schedulable_e3_run(dataset="traffic", scenario="complete_aligned", seed=30006,
                                      method=arm, **kw)
            print(f"     {arm:<17} {label:<8} -> NO_RAISE")
        except Exception as e:
            print(f"     {arm:<17} {label:<8} -> {type(e).__name__}")
    try:
        assert_canary_schedulable(dataset="traffic", method=arm, seed=31001)
        print(f"     {arm:<17} canary   -> NO_RAISE")
    except Exception as e:
        print(f"     {arm:<17} canary   -> {type(e).__name__}")

print("\n=== 4. does the S1' driver carry the exemption, and where does it write? ===")
drv = S1P / "driver/s1p_driver.py"
src = drv.read_text(encoding="utf-8")
for probe in ("TRAFFIC_REUSE_EXEMPTION", "allow_reused_traffic_rerun", "results_server_optimizer"):
    print(f"   {probe!r}: {src.count(probe)} occurrence(s)")
for i, ln in enumerate(src.splitlines(), 1):
    if ln.startswith("OUT =") or ln.startswith("RUNS =") or ln.startswith("TAG") or ln.startswith("ROOT ="):
        print(f"   L{i}: {ln}")

print("\n=== 5. G-const preview: validation-path weighted constant (NOT frozen yet) ===")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder  # noqa: E402
from raven_mcs.e3.canary.dataset_load import load_paper_dataset  # noqa: E402
from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test  # noqa: E402

ds = load_paper_dataset(ROOT, "traffic")
atomic = ds.atomic_df.copy()
atomic["target_group_main"] = pd.Categorical(atomic["target_group"]).codes
tgt = TargetBuilder(group_mapper=GroupMapper("target_group_main")).build(atomic, split="validation")
mu = np.asarray([float(tgt.group_mass.get(str(g), 0.0)) for g in range(172)], dtype=np.float64)


class _Shim:
    pass


ck = S1P / "runs/C_raven_simoracle/traffic/raven_simoracle/seed30001/checkpoints/final.pt"
shim = _Shim()
shim.model = CommonNDMF_from_ckpt(ck, ds.num_spatial)
pred = _predict(shim, ds, split="validation")
w = np.asarray(_mu_weights_for_test(pred, mu), dtype=np.float64)
w = w / w.sum()
y = np.asarray(pred["y_true"], dtype=np.float64)
ybar = float(np.sum(w * y))
c_val = float(np.sqrt(np.sum(w * (y - ybar) ** 2)))
import hashlib  # noqa: E402
print(f"   n = {len(y)}  weighted mean = {ybar:.8f}  c_val = {c_val:.8f}")
print(f"   weight vector sha256 = {hashlib.sha256(w.tobytes()).hexdigest()}")
print(f"   divergence ceiling 2*c_val = {2 * c_val:.6f}")
print(f"   prompt's unweighted check  : sd 0.99457 / mean 0.00878")
print(f"   S1' oracle seed30005 validation RMSE_mu = 1.125605 -> passes 2*c_val: "
      f"{1.125605 < 2 * c_val}")

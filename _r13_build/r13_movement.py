"""R1.3 adversarial audit - does MOVEMENT.csv agree with the checkpoints on disk,
and where do the report's 'mean movement' numbers come from?

ASCII only.
"""
import csv, json, math, pathlib, hashlib
import numpy as np
import torch, sys

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.models.common_ndmf import deterministic_common_ndmf

OUT = ROOT / "results_server_optimizer" / "round_v1"
RUNS = OUT / "runs"
FROZEN = ROOT / "artifacts/e3_formal_runs_r1/runs"
SEEDS = [30001, 30002, 30003, 30004, 30005]
BLOCKS = ("sensorscope", "uair", "traffic")


def rel_move(ckpt, seed):
    obj = torch.load(ckpt, map_location="cpu", weights_only=False)
    th = obj["state_dict"] if isinstance(obj, dict) and "state_dict" in obj else obj
    init = deterministic_common_ndmf(int(th["spatial.weight"].shape[0]), seed=seed).state_dict()
    d2 = sum(float(((th[k].double() - init[k].double()) ** 2).sum()) for k in th)
    i2 = sum(float((init[k].double() ** 2).sum()) for k in th)
    return math.sqrt(d2) / math.sqrt(i2)


mv = list(csv.DictReader((OUT / "tables" / "MOVEMENT.csv").open(encoding="utf-8")))
print("MOVEMENT.csv rows:", len(mv))
print("arms in MOVEMENT.csv:", sorted({r["arm"] for r in mv}))
print("configs in MOVEMENT.csv:", sorted({r["config"] for r in mv}))
print("blocks in MOVEMENT.csv:", sorted({r["block"] for r in mv}))
print()
print("### movement: MOVEMENT.csv vs checkpoint on disk vs report table")
for b in BLOCKS:
    for eta in ("0.001", "0.003", "0.01"):
        rows = [r for r in mv if r["block"] == b and r["arm"] == "fedavg_window" and r["config"] == "eta_s=%s" % eta]
        if not rows:
            print("  %-11s eta=%-6s NO ROWS in MOVEMENT.csv" % (b, eta))
            continue
        csv_mean = float(np.mean([float(r["overall_rel_movement"]) for r in rows]))
        recomputed = []
        for s in SEEDS:
            ck = RUNS / ("A_eta%g" % float(eta)) / b / "fedavg_window" / ("seed%d" % s) / "checkpoints/final.pt"
            if ck.is_file():
                recomputed.append(rel_move(ck, s))
        rec_mean = float(np.mean(recomputed)) if recomputed else float("nan")
        print("  %-11s eta=%-6s MOVEMENT.csv mean=%.6f (n=%d)  checkpoint recompute mean=%.6f (n=%d)  ratio=%.4f"
              % (b, eta, csv_mean, len(rows), rec_mean, len(recomputed), rec_mean / csv_mean))
    # frozen rows must come from the frozen tree
    frows = [r for r in mv if r["block"] == b and r["config"] == "frozen_SGD"]
    print("  %-11s frozen_SGD rows: %s" % (b, sorted({r["arm"] for r in frows}) or "NONE"))
    for r in frows:
        ck = FROZEN / b / r["arm"] / ("seed%d" % int(r["seed"])) / "checkpoints/final.pt"
        if ck.is_file():
            got = rel_move(ck, int(r["seed"]))
            print("     %-16s seed%s csv=%.6f frozen_recompute=%.6f  match=%s"
                  % (r["arm"], r["seed"], float(r["overall_rel_movement"]), got,
                     abs(got - float(r["overall_rel_movement"])) < 1e-9))

print()
print("### per-seed agreement MOVEMENT.csv vs checkpoint")
for r in mv:
    s = int(r["seed"])
    b = r["block"]
    eta = r["config"].split("=")[1]
    ck = RUNS / ("A_eta%g" % float(eta)) / b / r["arm"] / ("seed%d" % s) / "checkpoints/final.pt"
    if not ck.is_file():
        continue
    got = rel_move(ck, s)
    d = abs(got - float(r["overall_rel_movement"]))
    if d > 1e-9:
        print("  MISMATCH %-11s %-14s eta=%-6s seed%d  csv=%.9f  disk=%.9f  rel=%.4f"
              % (b, r["arm"], eta, s, float(r["overall_rel_movement"]), got, got / float(r["overall_rel_movement"])))

print()
print("### frozen (SGD server step) movement, for the 0.26/0.40/0.28 baseline claim")
for b, arm in (("sensorscope", "fedavg_window"), ("sensorscope", "raven"), ("sensorscope", "local_hajek"),
               ("uair", "fedavg_window"), ("uair", "raven"), ("uair", "local_hajek"),
               ("traffic", "local_hajek"), ("traffic", "raven_simoracle")):
    vals = []
    for s in (30001, 30002, 30003):
        ck = FROZEN / b / arm / ("seed%d" % s) / "checkpoints/final.pt"
        if ck.is_file():
            vals.append(rel_move(ck, s))
    if vals:
        print("  %-11s %-16s mean over 30001-3 = %.6f   (%.4f %%)"
              % (b, arm, float(np.mean(vals)), 100 * float(np.mean(vals))))
    else:
        print("  %-11s %-16s no checkpoints" % (b, arm))

print()
print("### eta=0.01 traffic: is the selection-eligible cell the same object as the reported one?")
for s in SEEDS:
    ck = RUNS / "A_eta0.01" / "traffic" / "fedavg_window" / ("seed%d" % s) / "checkpoints/final.pt"
    if ck.is_file():
        print("  seed%d exists  rel_move=%.6f" % (s, rel_move(ck, s)))

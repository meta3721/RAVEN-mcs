"""R1.3 adversarial audit - claim 2 detail: frozen server-step movement baselines,
the 7-70x multiplier arithmetic, and 'mostly through the output bias head.8.bias'.

ASCII only.
"""
import math, pathlib, sys, json
import numpy as np
import torch

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.models.common_ndmf import deterministic_common_ndmf

FROZEN = ROOT / "artifacts/e3_formal_runs_r1/runs"
RUNS = ROOT / "results_server_optimizer/round_v1/runs"
SEEDS3 = [30001, 30002, 30003]
SEEDS5 = [30001, 30002, 30003, 30004, 30005]


def per_tensor(ckpt, seed):
    obj = torch.load(ckpt, map_location="cpu", weights_only=False)
    th = obj["state_dict"] if isinstance(obj, dict) and "state_dict" in obj else obj
    init = deterministic_common_ndmf(int(th["spatial.weight"].shape[0]), seed=seed).state_dict()
    d2 = {k: float(((th[k].double() - init[k].double()) ** 2).sum()) for k in th}
    i2 = {k: float((init[k].double() ** 2).sum()) for k in th}
    return d2, i2


def rel(d2, i2):
    return math.sqrt(sum(d2.values())) / math.sqrt(sum(i2.values()))


print("### frozen server-step movement baselines (report section 1 recomputation)")
base = {}
for b, arm in (("sensorscope", "fedavg_window"), ("sensorscope", "raven"), ("sensorscope", "local_hajek"),
               ("uair", "fedavg_window"), ("uair", "raven"), ("uair", "local_hajek"),
               ("traffic", "local_hajek"), ("traffic", "debt_cal")):
    vals, vals5 = [], []
    for s in SEEDS5:
        ck = FROZEN / b / arm / ("seed%d" % s) / "checkpoints/final.pt"
        if ck.is_file():
            d2, i2 = per_tensor(ck, s)
            vals5.append(rel(d2, i2))
            if s in SEEDS3:
                vals.append(rel(d2, i2))
    if vals5:
        base[(b, arm)] = (float(np.mean(vals)), float(np.mean(vals5)))
        print("  %-11s %-16s mean seeds30001-3 = %.6f %%   mean seeds30001-5 = %.6f %%"
              % (b, arm, 100 * np.mean(vals), 100 * np.mean(vals5)))

print()
print("### the 7-70x multiplier arithmetic")
for b, arm in (("sensorscope", "fedavg_window"), ("uair", "fedavg_window"), ("traffic", "local_hajek")):
    tag = {"sensorscope": "A_eta0.01", "uair": "A_eta0.003", "traffic": "A_eta0.003"}[b]
    mv = []
    for s in SEEDS5:
        ck = RUNS / tag / b / "fedavg_window" / ("seed%d" % s) / "checkpoints/final.pt"
        if ck.is_file():
            d2, i2 = per_tensor(ck, s)
            mv.append(rel(d2, i2))
    new = float(np.mean(mv))
    frozen3 = base[(b, arm)][0]
    frozen5 = base[(b, arm)][1]
    print("  %-11s new(eta*)=%.6f %%  frozen(3seed)=%.6f %% ratio=%.2fx   frozen(5seed)=%.6f %% ratio=%.2fx"
          % (b, 100 * new, 100 * frozen3, new / frozen3, 100 * frozen5, new / frozen5))

print()
print("### 'mostly through the output bias head.8.bias': decomposition of the frozen movement")
for b, arm in (("sensorscope", "fedavg_window"), ("uair", "fedavg_window"), ("traffic", "local_hajek")):
    rows = []
    for s in SEEDS3:
        ck = FROZEN / b / arm / ("seed%d" % s) / "checkpoints/final.pt"
        d2, i2 = per_tensor(ck, s)
        tot = sum(d2.values())
        rows.append((s, d2, i2, tot))
    agg = {}
    for s, d2, i2, tot in rows:
        for k in d2:
            agg.setdefault(k, []).append(d2[k] / tot)
    ranked = sorted(agg.items(), key=lambda kv: -np.mean(kv[1]))
    print("  %-11s %-16s top-5 share of squared movement:" % (b, arm))
    for k, v in ranked[:5]:
        print("       %-16s %.4f  (mean over 3 seeds)" % (k, float(np.mean(v))))

print()
print("### eta=0.01 traffic (eligible but not selected): relative movement and test score")
for s in SEEDS5:
    ck = RUNS / "A_eta0.01" / "traffic" / "fedavg_window" / ("seed%d" % s) / "checkpoints/final.pt"
    fm = RUNS / "A_eta0.01" / "traffic" / "fedavg_window" / ("seed%d" % s) / "final_metrics.json"
    if ck.is_file():
        d2, i2 = per_tensor(ck, s)
        print("  seed%d exists rel_move=%.6f test_RMSE_mu=%s" % (s, rel(d2, i2),
              json.loads(fm.read_text())["RMSE_mu"] if fm.is_file() else "n/a"))

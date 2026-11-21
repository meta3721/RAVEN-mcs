"""R1.3 adversarial audit - objections (b) continued, (d), (e).

Checks:
 E1  split composition / unit-level independence / target-mass recipe.
 E2  which kernels / optimizer each arm used (drives the central-vs-fed comparison).
 E3  movement numbers, re-derived from the counters the driver itself logged.
 E4  window counts, active windows, seeds actually present, K_r share reproduction.
 E5  file mtimes -> vintages; carried-over cells; mixed vintages.
ASCII only.
"""
import json, math, pathlib, hashlib, datetime, csv
import numpy as np
import torch

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_server_optimizer" / "round_v1"
RUNS = OUT / "runs"
FROZEN = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs"
BUILD = ROOT / "_r13_build"
SEEDS = [30001, 30002, 30003, 30004, 30005]
BLOCKS = ("sensorscope", "uair", "traffic")

def walk_metric_files(tag, block, arm, seed):
    d = RUNS / tag / block / arm / ("seed%d" % seed)
    return d

print("### E1  atomic split composition and target-mass recipe")
for b in BLOCKS:
    for src, label in ((ROOT / "data/processed" / b / "atomic_units.parquet", "data/processed"),
                       (ROOT / "artifacts/e3_multidataset_real_runner_canary_r1/_traffic_e3_staging/atomic_units.parquet", "traffic staging")):
        if not src.is_file():
            continue
        if b != "traffic" and label != "data/processed":
            continue
        print(" %-11s %-16s sha256=%s" % (b, label, hashlib.sha256(src.read_bytes()).hexdigest()))

print()
print("### E2  whose kernel/optimizer produced each number")
print(" central_delivered / central_all  -> artifacts/e3_formal_runs_r1 (central_real.py, torch.optim.Adam)")
cr = ROOT / "src/raven_mcs/e3/real_runner/central_real.py"
lines = cr.read_text(encoding="utf-8").splitlines()
for i, ln in enumerate(lines, 1):
    if "Adam" in ln or "optim." in ln or "SGD" in ln:
        print("   central_real.py:%d  %s" % (i, ln.strip()))
wr = ROOT / "src/raven_mcs/training/window_runner.py"
wl = wr.read_text(encoding="utf-8").splitlines()
print("   window_runner.py:1150-1170 (hand-rolled server step):")
for i in range(1149, 1170):
    print("     %d  %s" % (i + 1, wl[i]))
cl = ROOT / "src/raven_mcs/training/client.py"
cll = cl.read_text(encoding="utf-8").splitlines()
print("   client.py:100-110 (client normalisation):")
for i in range(99, 110):
    print("     %d  %s" % (i + 1, cll[i]))

print()
print("### E3  movement, re-derived from the driver's own logged counters")
rows = []
for b in BLOCKS:
    eta_star = {"sensorscope": 0.01, "uair": 0.003, "traffic": 0.003}[b]
    tag = "A_eta%g" % eta_star
    for s in SEEDS:
        p = RUNS / tag / b / "fedavg_window" / ("seed%d" % s) / "SERVER_OPT_META.json"
        if not p.is_file():
            continue
        m = json.loads(p.read_text())
        f = m.get("diag_last") or []
        g = m.get("diag_first") or []
        rows.append((b, s, m.get("server_opt"), m.get("n_windows_optimizer_applied"),
                     g[0].get("g_norm") if g else None, f[0].get("g_norm") if f else None,
                     f[0].get("m_norm") if f else None))
for r in rows:
    print("  %-11s seed%d opt=%s n_applied=%s g_norm(first,last)=(%.5f, %.5f) m_norm_last=%.5f"
          % (r[0], r[1], r[2], r[3], r[4] or float("nan"), r[5] or float("nan"), r[6] or float("nan")))

print()
print("### E4  windows / active / seeds / K_r share")
csh = json.loads((OUT / "S1P_STAGE_C_H.json").read_text())
for b in BLOCKS:
    eta_star = csh["H"][b]["eta_s_star"]
    tag = "A_eta%g" % eta_star
    seen = []
    for s in SEEDS:
        d = RUNS / tag / b / "fedavg_window" / ("seed%d" % s)
        rows_ = json.loads((d / "window_metrics.json").read_text())
        act = [r for r in rows_ if r.get("active")]
        ar = [int(r.get("a_r_size") or 0) for r in act]
        seen.append((s, len(rows_), len(act), float(np.mean(ar)) if ar else None,
                     sum(1 for x in ar if x <= 3) / len(ar) if ar else None))
    ks = [x[4] for x in seen if x[4] is not None]
    print("  %-11s per-seed (n_rows, n_active, mean a_r, share K_r<=3):" % b)
    for x in seen:
        print("      seed%d rows=%d active=%d mean_a_r=%.3f kr<=3=%.6f" % (x[0], x[1], x[2], x[3], x[4]))
    pooled = float(np.mean(ks))
    rec = csh["H"][b]["kr_le3_under_new_config"]
    print("      pooled mean of per-seed shares=%.16f  recorded share=%.16f  n_active recorded=%s  match=%s"
          % (pooled, rec["share_kr_le3"], rec["n_active"], abs(pooled - rec["share_kr_le3"]) < 1e-12))
    print("      recorded applied over ONE cell only (driver uses the first grid row's run_dir) -> it is a per-seed share, not a pooled one")

print()
print("### E5  vintages / carried-over cells")
def mt(p):
    try:
        return datetime.datetime.utcfromtimestamp(p.stat().st_mtime).isoformat()
    except Exception:
        return None
for p in (OUT / "S1P_FROZEN_CONFIG.json", OUT / "S1P_STAGE_C_H.json", OUT / "S1P_REPORT.md",
          OUT / "driver/s1p_driver.py", OUT / "driver/stageA_traffic2_stderr.log",
          OUT / "driver/stageC_stderr.log", OUT / "S1P_BLOCKED.md"):
    print("  %-45s mtime=%s" % (p.relative_to(ROOT), mt(p)))
print("  per-tag run mtimes:")
for tag in ("A_eta0.001", "A_eta0.003", "A_eta0.01", "C_raven", "C_raven_simoracle",
            "g0_baseline", "g0_identity", "g0t_off", "g0t_sgd", "g2_det_a", "g2_det_b"):
    ts = []
    for p in sorted((RUNS / tag).rglob("SERVER_OPT_META.json")):
        ts.append((mt(p), str(p.relative_to(RUNS)).replace("\\", "/")))
    if ts:
        print("   %-16s n=%2d  first=%s  last=%s" % (tag, len(ts), ts[0][0], ts[-1][0]))
print("  src mtimes:")
for p in (ROOT / "src/raven_mcs/e3/protocol_closure/reuse_guard.py",
          ROOT / "src/raven_mcs/training/window_runner.py",
          ROOT / "src/raven_mcs/e3/real_runner/runner.py"):
    print("   %-60s mtime=%s sha=%s" % (p.relative_to(ROOT), mt(p), hashlib.sha256(p.read_bytes()).hexdigest()[:16]))

print()
print("### E6  SERVER_OPT_META records each run's own eta_s / mode")
from collections import Counter
c = Counter()
for b in BLOCKS:
    for tag in sorted(RUNS.glob("*/%s/*/seed30001" % b)):
        m = json.loads((tag / "SERVER_OPT_META.json").read_text())
        c[(str(tag.relative_to(RUNS)).split("\\")[0], str(m.get("server_opt")))] += 1
for k in sorted(c):
    print("  ", k, c[k])

print()
print("### E7  movement: reconstruct init and compare, plus self-consistency with logged counters")
import sys
sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.models.common_ndmf import deterministic_common_ndmf
for b in BLOCKS:
    eta_star = csh["H"][b]["eta_s_star"]
    tag = "A_eta%g" % eta_star
    for s in (30001,):
        ck = RUNS / tag / b / "fedavg_window" / ("seed%d" % s) / "checkpoints" / "final.pt"
        obj = torch.load(ck, map_location="cpu", weights_only=False)
        th = obj["state_dict"] if "state_dict" in obj else obj
        init = deterministic_common_ndmf(int(th["spatial.weight"].shape[0]), seed=s).state_dict()
        d2 = sum(float(((th[k].double() - init[k].double()) ** 2).sum()) for k in th)
        i2 = sum(float((init[k].double() ** 2).sum()) for k in th)
        print("  %-11s seed%d rel_move_by_reconstruction=%.6f" % (b, s, math.sqrt(d2) / math.sqrt(i2)))

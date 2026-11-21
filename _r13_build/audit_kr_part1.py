"""READ-ONLY recomputation, part 1: K_r counts and the K_r <= 3 share.

K_r is derived as len(window_metrics.json[k]['active_clients']) for entries with
'active' == True.  Also cross-checked against window_metrics.json['a_r_size'] and
against the independent trace-based REACHABILITY_WINDOWS.parquet (n_active).
Writes nothing.
"""
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
E4 = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"
SEEDS = list(range(30001, 30021))


def suite(arm):
    return E3 if arm == "raven" else E4


def collect(dataset, arm):
    base = suite(arm) / dataset / arm
    rows = []
    missing = []
    for s in SEEDS:
        p = base / ("seed%d" % s) / "window_metrics.json"
        if not p.is_file():
            missing.append(s)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for w in d:
            act = bool(w.get("active"))
            k = len(w["active_clients"]) if act else 0
            rows.append({"dataset": dataset, "arm": arm, "seed": s,
                         "window_id": w["window_id"], "active": act, "K_r": k,
                         "a_r_size": w.get("a_r_size"),
                         "n_alpha": len(w.get("alpha", []))})
    return pd.DataFrame(rows), missing


print("=" * 100)
print("A) every (suite, dataset, arm) that has window_metrics.json, 20 seeds each")
for tag, base in (("E3", E3), ("E4", E4)):
    for ds in ("sensorscope", "uair", "traffic"):
        d = base / ds
        if not d.is_dir():
            continue
        for arm in sorted(p.name for p in d.iterdir() if p.is_dir()):
            df, miss = collect(ds, arm)
            if df.empty:
                continue
            act = df[df.active]
            print("  %s %-12s %-22s n_windows=%5d n_active=%5d K<=3=%5d share=%.4f (%.2f%%) "
                  "Kmax=%2d Kmean=%.3f infeasible_n_active=%d missing_seeds=%s"
                  % (tag, ds, arm, len(df), len(act), int((act.K_r <= 3).sum()),
                     100 * float((act.K_r <= 3).mean()), float((act.K_r <= 3).mean()) * 100,
                     int(act.K_r.max()), float(act.K_r.mean()),
                     int((df[~df.active].K_r != 0).sum()), miss))

CASES = [
    ("D", "sensorscope", "raven", 0.786, 1877),
    ("E", "uair", "raven", 0.902, 1402),
    ("F", "uair", "raven_wo_design", 0.790, 1515),
    ("F2", "sensorscope", "raven_wo_design", None, None),
]

print()
print("=" * 100)
print("B) the three manuscript cases, exact counts")
for tag, ds, arm, ms_share, ms_n in CASES:
    df, miss = collect(ds, arm)
    act = df[df.active]
    n = len(act)
    k3 = int((act.K_r <= 3).sum())
    share = k3 / n
    print("-" * 100)
    print("  %s  suite=%s dataset=%s arm=%s"
          % (tag, "E3" if arm == "raven" else "E4", ds, arm))
    print("     n_active_windows        = %d   (manuscript denominator %s)"
          % (n, ms_n))
    print("     n_active with K_r <= 3  = %d" % k3)
    print("     share                   = %.6f  = %.4f %%  (manuscript %s)"
          % (share, 100 * share, ms_share))
    if ms_share is not None:
        print("     manuscript share x its denominator = %.3f  -> nearest int %d"
              % (ms_share * ms_n, round(ms_share * ms_n)))
        print("     shifted-round check: 0.7855-0.7865 * %d in [%d, %d] -> raw %d %s"
              % (ms_n, int(np.floor(0.7855 * ms_n)), int(np.ceil(0.7865 * ms_n)), k3,
                 "IN RANGE" if 0.7855 * ms_n <= k3 <= 0.7865 * ms_n else "OUT OF RANGE"))
    print("     K_r distribution: %s"
          % dict(sorted(act.K_r.value_counts().to_dict().items())))
    print("     a_r_size == K_r on all rows: %s"
          % bool((act.a_r_size == act.K_r).all()))
    print("     len(alpha) == K_r on all rows: %s"
          % bool((act.n_alpha == act.K_r).all()))
    print("     inactive windows with nonzero active_clients: %d"
          % int((df[~df.active].K_r != 0).sum()))
    # alternative denominators
    print("     ALT all windows (active+inactive) denominator = %d share=%.6f"
          % (len(df), float((df.K_r <= 3).mean())))
    print("     ALT per-seed share (mean of 20 seed-level shares) = %.6f"
          % float(act.groupby("seed").K_r.apply(lambda v: float((v <= 3).mean())).mean()))
    print("     per-seed n_active : %s"
          % list(act.groupby("seed").size().values))
    print("     per-seed n_(K<=3) : %s"
          % list(act.groupby("seed").K_r.apply(lambda v: int((v <= 3).sum())).values))
    if miss:
        print("     MISSING SEEDS: %s" % miss)

print()
print("=" * 100)
print("C) cross-check against the independent trace-based artifact")
rw = ROOT / ".rb_work/evidence_headroom/REACHABILITY_WINDOWS.parquet"
if rw.is_file():
    w = pd.read_parquet(rw)
    for ds in ("sensorscope", "uair"):
        g = w[w.dataset == ds]
        na = g[g.n_active > 0]
        print("  %-12s trace rows=%d  n_active_windows=%d  n_active(K<=3)=%d share=%.6f"
              % (ds, len(g), len(na), int((na.n_active <= 3).sum()),
                 float((na.n_active <= 3).mean())))
    # row-level agreement with window_metrics for the two uair arms
    for ds, arm in (("sensorscope", "raven"), ("uair", "raven"), ("uair", "raven_wo_design")):
        df, _ = collect(ds, arm)
        m = df.merge(w[(w.dataset == ds)][["seed", "window_id", "n_active"]],
                     on=["seed", "window_id"], how="left")
        bad = m[(m.active) & (m.K_r != m.n_active)]
        print("  row-level K_r(window_metrics) vs n_active(trace) for %s/%s: mismatches=%d / %d"
              % (ds, arm, len(bad), len(m)))
        if len(bad):
            print("    first mismatches:\n%s" % bad.head(8).to_string(index=False))
    # also the reverse: trace-active but runner-inactive
    for ds, arm in (("sensorscope", "raven"), ("uair", "raven"), ("uair", "raven_wo_design")):
        df, _ = collect(ds, arm)
        m = df.merge(w[(w.dataset == ds)][["seed", "window_id", "n_active"]],
                     on=["seed", "window_id"], how="left")
        print("  %s/%s: runner-active & trace-zero = %d ; runner-inactive & trace-active = %d"
              % (ds, arm, int(((m.active) & (m.n_active == 0)).sum()),
                 int(((~m.active) & (m.n_active > 0)).sum())))
else:
    print("  REACHABILITY_WINDOWS.parquet not found")

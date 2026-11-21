"""READ-ONLY: is K_r derivable from the trace alone?  Per-arm diff structure."""
import json
import pathlib
from collections import Counter

import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
E4 = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"
SEEDS = list(range(30001, 30021))
w = pd.read_parquet(ROOT / ".rb_work/evidence_headroom/REACHABILITY_WINDOWS.parquet")


def collect(dataset, arm):
    base = (E3 if arm == "raven" else E4) / dataset / arm
    rows = []
    for s in SEEDS:
        p = base / ("seed%d" % s) / "window_metrics.json"
        if not p.is_file():
            continue
        for x in json.loads(p.read_text(encoding="utf-8")):
            rows.append({"dataset": dataset, "seed": s, "window_id": x["window_id"],
                         "active": bool(x.get("active")),
                         "K_r": len(x["active_clients"]) if x.get("active") else 0,
                         "clients": set(x["active_clients"])})
    return pd.DataFrame(rows)


for ds, arm in (("uair", "raven"), ("uair", "raven_wo_design"), ("sensorscope", "raven")):
    d = collect(ds, arm)
    m = d.merge(w[w.dataset == ds][["seed", "window_id", "n_active"]],
                on=["seed", "window_id"], how="left")
    print("=" * 90)
    print("%s / %s   rows=%d" % (ds, arm, len(m)))
    act = m[m.active]
    print("  active rows=%d ; (trace - K_r) counts on active rows: %s"
          % (len(act), dict(sorted(Counter((act.n_active - act.K_r).tolist()).items()))))
    inactive = m[~m.active]
    print("  inactive rows=%d ; trace n_active counts: %s"
          % (len(inactive), dict(sorted(Counter(inactive.n_active.tolist()).items()))))
    # K_r<=3 share if K_r were read off the trace instead
    share_trace = float((act.n_active <= 3).mean())
    print("  K_r<=3 share using runner K_r = %.6f ; using trace n_active = %.6f"
          % (float((act.K_r <= 3).mean()), share_trace))
    # which client is dropped?  compare sets for the +1 rows
    sub = act[(act.n_active - act.K_r) == 1]
    if len(sub):
        print("  rows where the runner has exactly one fewer client than the trace: %d" % len(sub))
    print("  a_r_size column present: %s" % ("a_r_size" in json.loads(
        ((E3 if arm == "raven" else E4) / ds / arm / "seed30001" / "window_metrics.json")
        .read_text(encoding="utf-8"))[0]))

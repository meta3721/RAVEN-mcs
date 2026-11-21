"""F-1 design input: is the opportunity stratum nested inside the target group?

If every risk unit of a stratum carries the same target group, then no
stratum-level (or group-level) propensity can vary *within* a stratum, and the
only way to build within-stratum selection is a unit-level covariate such as
time_index.

Read-only over the frozen E3 EventTraces plus runtime accounting.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

TR = Path("artifacts/e3_formal_runs_r1/eventtraces")
RUNS = Path("artifacts/e3_formal_runs_r1/runs")


def find_events():
    hits = sorted(TR.rglob("events.parquet"))
    print(f"events.parquet files under {TR}: {len(hits)}")
    for h in hits[:4]:
        print("   ", h)
    return hits


def check_nesting(path: Path) -> None:
    df = pd.read_parquet(path, columns=[
        "window_id", "client_id", "risk_set_unit_ids",
        "opportunity_features", "target_groups",
    ])
    bad = 0
    pairs = 0
    seen = defaultdict(set)
    for r in df.itertuples(index=False):
        feats = r.opportunity_features
        if isinstance(feats, str):
            feats = json.loads(feats)
        stratum = (feats or {}).get("opportunity_stratum", "?")
        groups = r.target_groups
        if isinstance(groups, str):
            groups = json.loads(groups)
        if groups is None:
            continue
        if isinstance(groups, dict):
            vals = {str(v) for v in groups.values()}
        else:
            vals = {str(v) for v in groups}
        pairs += 1
        seen[stratum] |= vals
        if len(vals) > 1:
            bad += 1
    multi = sum(1 for v in seen.values() if len(v) > 1)
    print(f"  {path.parent.parent.name}/{path.parent.name}: client-windows={pairs}, "
          f"with >1 target group={bad}, distinct strata={len(seen)}, "
          f"strata spanning >1 group={multi}")
    examples = list(seen.items())[:3]
    for s, g in examples:
        print(f"     stratum {s!r} -> groups {sorted(g)}")


def runtime_accounting() -> None:
    tot = 0.0
    per = {}
    for f in RUNS.rglob("final_metrics.json"):
        payload = json.loads(f.read_text(encoding="utf-8"))
        sec = float(payload.get("runtime_seconds") or 0.0)
        method = f.parent.parent.name
        dataset = f.parent.parent.parent.name
        per[(dataset, method)] = per.get((dataset, method), 0.0) + sec
        tot += sec
    print(f"\npublished E3 formal runs: total {tot/3600.0:.2f} h over {len(list(RUNS.rglob('final_metrics.json')))} runs")
    for (ds, m), sec in sorted(per.items()):
        print(f"   {ds:<12}{m:<26}{sec/60.0:8.1f} min total")


hits = find_events()
if hits:
    check_nesting(hits[0])
runtime_accounting()

"""F-1 design input: is the opportunity stratum nested inside the target group?

If every risk unit of a stratum carries the same target group, then no
stratum-level or group-level propensity can vary *within* a stratum, and the
only way to build within-stratum selection is a unit-level covariate.

Read-only.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd

TR = Path("artifacts/e3_formal_runs_r1/eventtraces")
RUNS = Path("artifacts/e3_formal_runs_r1/runs")
PROC = Path("data/processed")


def load_units(dataset: str) -> dict[str, dict]:
    f = PROC / dataset / "atomic_units.parquet"
    if not f.is_file():
        print(f"  missing {f}")
        return {}
    df = pd.read_parquet(f)
    print(f"  {f}: columns={list(df.columns)}")
    out = {}
    for r in df.itertuples(index=False):
        d = r._asdict()
        out[str(d["unit_id"])] = d
    return out


def check(dataset: str, seed: str) -> None:
    units = load_units(dataset)
    f = TR / dataset / seed / "training_eventtrace" / "events.parquet"
    df = pd.read_parquet(f, columns=[
        "window_id", "client_id", "risk_set_unit_ids", "opportunity_features",
    ])
    stratum_groups = defaultdict(set)
    bad = 0
    for r in df.itertuples(index=False):
        feats = r.opportunity_features
        if isinstance(feats, str):
            feats = json.loads(feats)
        stratum = str((feats or {}).get("opportunity_stratum", "?"))
        ids = r.risk_set_unit_ids
        if isinstance(ids, str):
            ids = json.loads(ids)
        groups = {str(units[str(u)]["target_group"]) for u in (ids or []) if str(u) in units}
        if len(groups) > 1:
            bad += 1
        stratum_groups[stratum] |= groups
    multi = sum(1 for v in stratum_groups.values() if len(v) > 1)
    print(f"  {dataset}/{seed}: client-windows={len(df)}, risk sets spanning >1 group={bad}")
    print(f"      distinct strata={len(stratum_groups)}, strata spanning >1 group={multi}")
    sp = defaultdict(set)
    for s in stratum_groups:
        sp[s.rsplit("::", 1)[0]].add(s)
    print(f"      distinct (spatial::block) parents={len(sp)}; "
          f"strata per parent: {sorted({len(v) for v in sp.values()})}")
    for s, g in list(stratum_groups.items())[:3]:
        print(f"      e.g. stratum {s!r} -> groups {sorted(g)}")


def runtime_accounting() -> None:
    files = list(RUNS.rglob("final_metrics.json"))
    tot = 0.0
    per = defaultdict(float)
    for f in files:
        payload = json.loads(f.read_text(encoding="utf-8"))
        sec = float(payload.get("runtime_seconds") or 0.0)
        per[(f.parent.parent.parent.name, f.parent.parent.name)] += sec
        tot += sec
    print(f"\npublished E3 formal runs: {tot/3600.0:.2f} h over {len(files)} runs")
    for (ds, m), sec in sorted(per.items()):
        print(f"   {ds:<12}{m:<26}{sec/60.0:8.1f} min")


check("sensorscope", "seed30001")
check("uair", "seed30001")
runtime_accounting()

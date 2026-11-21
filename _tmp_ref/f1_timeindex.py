import pandas as pd
from collections import defaultdict
for ds in ("sensorscope","uair"):
    df = pd.read_parquet(f"data/processed/{ds}/atomic_units.parquet",
                         columns=["unit_id","time_index","target_group","opportunity_stratum","split","target_value"])
    tr = df[df["split"].astype(str)=="train"]
    g = defaultdict(set)
    for r in tr.itertuples(index=False):
        g[r.opportunity_stratum].add(int(r.time_index))
    counts = sorted({len(v) for v in g.values()})
    print(f"{ds}: train units={len(tr)} strata={len(g)} distinct time_index per stratum: min={counts[0]} max={counts[-1]} histogram={ {c: sum(1 for v in g.values() if len(v)==c) for c in counts} }")
    # per stratum unit count
    n = defaultdict(int)
    for r in tr.itertuples(index=False):
        n[r.opportunity_stratum]+=1
    nc = sorted(set(n.values()))
    print(f"   units per stratum histogram: {{ {', '.join(f'{c}:{sum(1 for v in n.values() if v==c)}' for c in nc[:12])} }}")

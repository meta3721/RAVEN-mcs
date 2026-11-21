import pathlib, json, numpy as np
ROOT = pathlib.Path(".")
for ds, exp in (("uair", (70.10, 63, 75)), ("sensorscope", (93.85, 88, 98))):
    base = ROOT/"artifacts/e3_formal_runs_r1/runs"/ds
    per = []
    for d in sorted(base.iterdir()):
        if not d.is_dir(): continue
        for sd in sorted(d.glob("seed*")):
            wm = sd/"window_metrics.json"
            if not wm.is_file(): continue
            recs = json.loads(wm.read_text(encoding="utf-8"))
            per.append(sum(1 for w in recs if w.get("active")))
    a = np.array(per, dtype=float)
    print(f"{ds:<12} runs={len(a):<4} mean={a.mean():.4f} (table {exp[0]})  min={int(a.min())} max={int(a.max())} (table {exp[1]}-{exp[2]})  windows_per_run={len(recs)}")

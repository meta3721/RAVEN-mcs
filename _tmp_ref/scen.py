import csv, pathlib, collections
p = pathlib.Path("artifacts/e2_traffic_formal_runs_r1")
if not p.exists(): p = pathlib.Path("artifacts/e2_traffic_formal_runs_r1/formal_results.csv").parent
f = None
for c in p.rglob("formal_results.csv"):
    f = c; break
print("results file:", f)
if f:
    rows = list(csv.DictReader(open(f, newline="", encoding="utf-8")))
    print("rows:", len(rows), "| cols:", list(rows[0].keys())[:10])
    print("scenarios:", sorted({r.get("scenario","?") for r in rows}))
    print("methods  :", sorted({r.get("method","?") for r in rows}))
else:
    print("formal_results.csv not found; listing:", [str(x.relative_to(p)) for x in list(p.rglob("*"))[:10]])

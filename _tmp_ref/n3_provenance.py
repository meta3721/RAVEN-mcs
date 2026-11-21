import json, pathlib, csv, hashlib
ROOT = pathlib.Path(".")
def rd(p): return [r for r in csv.DictReader(open(p, newline="", encoding="utf-8"))]
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()[:12]

A = ROOT/"RAVEN_MCS_PUBLIC_REPRO_R1"/"tables"/"TABLE_II_WORSTGROUP_PER_SEED.csv"
B = ROOT/"post_review"/"P0_ni_artifact"/"tables"/"TABLE_II_WORSTGROUP_PER_SEED.csv"
print("repro CSV sha", sha(A), "len", A.stat().st_size, "| P0 CSV sha", sha(B), "len", B.stat().st_size, "| identical:", sha(A)==sha(B))

src = ROOT/"manuscript_evidence_closure_r1"/"01_table_sources"/"TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv"
print("\n=== manuscript declared source:", src.name, "exists", src.exists())
if src.exists():
    r = rd(src); print("cols:", list(r[0].keys()))
    for row in r:
        if row.get("dataset","").lower()=="uair":
            print("  ", {k:v for k,v in row.items() if k.lower() in ("dataset","method","rmse_mu","rmse","worstgroup","worstgroup_rmse","seeds","n_seeds")})
meta = src.with_suffix(".csv.meta.json")
if meta.exists():
    m = json.loads(meta.read_text(encoding="utf-8"))
    print("  meta keys:", list(m.keys())[:14])
    print("  meta:", json.dumps({k:v for k,v in m.items() if not isinstance(v,(list,dict))}, ensure_ascii=False)[:600])

print("\n=== per-method: repro CSV mean vs E3 tree mean (uair) ===")
csvrows = [r for r in rd(A) if r["dataset"]=="uair"]
methods = sorted({r["method"] for r in csvrows})
print(f"{'method':<18} {'csvmean':>10} {'treemean':>10} {'rel%':>9}  nseeddiff  worst_seed_diff")
for m in methods:
    c = {int(r["seed"]): float(r["RMSE_mu"]) for r in csvrows if r["method"]==m}
    d = ROOT/"artifacts"/"e3_formal_runs_r1"/"runs"/"uair"/m
    t = {}
    if d.exists():
        for sd in d.glob("seed*"):
            f = sd/"final_metrics.json"
            if f.exists(): t[int(sd.name.replace("seed",""))] = float(json.loads(f.read_text(encoding="utf-8"))["RMSE_mu"])
    common = sorted(set(c)&set(t))
    if not common: print(f"{m:<18} {'-':>10} {'-':>10}  (no tree dir)"); continue
    diffs = {s: (c[s]-t[s])/t[s]*100 for s in common}
    bad = {s:v for s,v in diffs.items() if abs(v)>1e-6}
    cm = sum(c[s] for s in common)/len(common); tm = sum(t[s] for s in common)/len(common)
    ws = max(bad.items(), key=lambda kv: abs(kv[1])) if bad else (None,0.0)
    print(f"{m:<18} {cm:>10.6f} {tm:>10.6f} {(cm-tm)/tm*100:>9.4f}  {len(bad):>9}  {ws[0]}={ws[1]:+.4f}%" if bad else
          f"{m:<18} {cm:>10.6f} {tm:>10.6f} {(cm-tm)/tm*100:>9.4f}  {0:>9}  -")

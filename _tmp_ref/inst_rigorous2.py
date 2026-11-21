import csv, json, pathlib, statistics as st
E3 = pathlib.Path("artifacts/e3_formal_runs_r1/runs/uair")
E4 = pathlib.Path("artifacts/e4_core_mechanism_ablation_r1/runs/uair")
S = list(range(30001, 30021))
def vec(d, k):
    out=[]
    for s in S:
        f = d/f"seed{s}"/"final_metrics.json"
        if not f.is_file(): return None
        v = json.loads(f.read_text(encoding="utf-8")).get(k)
        if not isinstance(v,(int,float)): return None
        out.append(float(v))
    return out
rows = [r for r in csv.DictReader(open("RAVEN_MCS_PUBLIC_REPRO_R1/tables/E4_ABLATION_RELATIVE_CHANGE.csv", newline="", encoding="utf-8"))
        if r["dataset"]=="U-Air" and r["component"]=="Inst" and r["metric"]=="Delta_group"]
rows.sort(key=lambda r: int(r["seed"]))
csv_full = [float(r["full_RAVEN"]) for r in rows]
csv_ab   = [float(r["ablation"]) for r in rows]
raven = vec(E3/"raven", "Delta_group")
print("1) does the CSV's full_RAVEN column equal the E3 tree's `raven` per seed?")
d = max(abs(x-y) for x,y in zip(csv_full, raven))
print(f"   max|diff| = {d:.3e}  ->  {'EXACT per-seed match' if d==0 else 'differs'}")
print()
print("2) which stored U-Air arm equals the CSV's Inst ablation column, per seed?")
best=[]
for base in (E3, E4):
    for dd in sorted(base.iterdir()):
        if not dd.is_dir(): continue
        v = vec(dd, "Delta_group")
        if v is None: continue
        best.append((max(abs(x-y) for x,y in zip(v, csv_ab)), f"{base.parent.name.split('_')[0]}/{dd.name}"))
best.sort()
for dd, n in best[:5]:
    tag = "  <-- EXACT" if dd == 0 else ""
    print(f"   {n:<34} max|diff| = {dd:.6f}{tag}")
print()
print("3) the paper's own units (ratio-of-means over the 20-seed column means)")
def rom(v): return (st.mean(v)/st.mean(raven) - 1)*100
print(f"   Table IV line 1955 (Inst, Delta_group) prints        -0.089")
print(f"   from the CSV columns  : {rom(csv_ab):+.4f}%   <- reproduces the table")
print(f"   from E4 raven_wo_inst : {rom(vec(E4/'raven_wo_inst','Delta_group')):+.4f}%")
print(f"   from E3 twostage_hajek: {rom(vec(E3/'twostage_hajek','Delta_group')):+.4f}%")

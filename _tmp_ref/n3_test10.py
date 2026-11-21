import json, pathlib, csv
ROOT = pathlib.Path(".")
repro = [r for r in csv.DictReader(open(ROOT/"RAVEN_MCS_PUBLIC_REPRO_R1"/"tables"/"TABLE_II_WORSTGROUP_PER_SEED.csv", newline="", encoding="utf-8")) if r["dataset"]=="uair"]
TEST = set(range(30011,30021))
def rmap(m, key="RMSE_mu"):
    return {int(r["seed"]): float(r[key]) for r in repro if r["method"]==m}
def tmap(m, key="RMSE_mu"):
    d = ROOT/"artifacts"/"e3_formal_runs_r1"/"runs"/"uair"/m; out={}
    if d.exists():
        for sd in d.glob("seed*"):
            f=sd/"final_metrics.json"
            if f.exists(): out[int(sd.name.replace("seed",""))]=float(json.loads(f.read_text(encoding="utf-8"))[key])
    return out
def mean(d, sel=None):
    v=[x for s,x in d.items() if sel is None or s in sel]; return sum(v)/len(v) if v else float("nan")

print("=== uair TEST10 (30011-30020) vs ALL20, RMSE_mu ===")
print(f"{'method':<18} {'src':<8} {'TEST10':>10} {'ALL20':>10}")
M = ["fedavg_window","local_hajek","twostage_hajek","raven","raven_wo_design","fedau_window","obsuse_window"]
for m in M:
    r = rmap(m); t = tmap(m)
    print(f"{m:<18} {'repro':<8} {mean(r,TEST):>10.6f} {mean(r):>10.6f}")
    if t: print(f"{'':<18} {'tree':<8} {mean(t,TEST):>10.6f} {mean(t):>10.6f}")

print("\n=== the paper's TEST claims, recomputed on each source ===")
ND  = "raven_wo_design"
for base in ("fedavg_window","twostage_hajek"):
    for src,fn in (("repro",rmap),("tree",tmap)):
        a=fn(ND); b=fn(base)
        if not a or not b: print(f"  NoDesign vs {base:<16} [{src}] : unavailable ({'NoDesign absent from tree' if not a else 'base absent'})"); continue
        for lab,sel in (("TEST10",TEST),("ALL20",None)):
            va,vb=mean(a,sel),mean(b,sel)
            print(f"  NoDesign vs {base:<16} [{src}] {lab:<6} : {va:.6f} vs {vb:.6f}  ->  {(va-vb)/vb*100:+.3f}%")
print("\n=== Design-on (raven) vs baselines, tree only ===")
for base in ("fedavg_window","twostage_hajek"):
    a=tmap("raven"); b=tmap(base)
    for lab,sel in (("TEST10",TEST),("ALL20",None)):
        print(f"  raven vs {base:<16} [tree]  {lab:<6} : {mean(a,sel):.6f} vs {mean(b,sel):.6f}  ->  {(mean(a,sel)-mean(b,sel))/mean(b,sel)*100:+.3f}%")

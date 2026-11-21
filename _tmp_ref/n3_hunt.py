import json, pathlib, csv, itertools
ROOT = pathlib.Path(".")
repro = [r for r in csv.DictReader(open(ROOT/"RAVEN_MCS_PUBLIC_REPRO_R1"/"tables"/"TABLE_II_WORSTGROUP_PER_SEED.csv", newline="", encoding="utf-8")) if r["dataset"]=="uair"]
def rmap(m,k): return {int(r["seed"]): float(r[k]) for r in repro if r["method"]==m}
def tmap(m,k):
    d = ROOT/"artifacts"/"e3_formal_runs_r1"/"runs"/"uair"/m; out={}
    for sd in d.glob("seed*"):
        f=sd/"final_metrics.json"
        if f.exists():
            j=json.loads(f.read_text(encoding="utf-8"))
            if k in j and isinstance(j[k],(int,float)): out[int(sd.name.replace("seed",""))]=float(j[k])
    return out
WINDOWS = {"TEST10": set(range(30011,30021)), "ALL20": None, "TEST6": set(range(30015,30021)), "FIRST10": set(range(30001,30011))}
TARGETS = (-9.11, -6.17)
hits=[]
for metric in ("RMSE_mu","WorstGroupRMSE"):
    for ref in ("fedavg_window","twostage_hajek","raven","local_hajek","fedau_window","obsuse_window"):
        for src,fn in (("repro",rmap),("tree",tmap)):
            nd = fn("raven_wo_design",metric); b = fn(ref,metric)
            if not nd or not b: continue
            for wname, sel in WINDOWS.items():
                ks = sorted(s for s in nd if s in b and (sel is None or s in sel))
                if len(ks) < 3: continue
                vals = {
                  "ratio": (sum(nd[s] for s in ks)/len(ks))/(sum(b[s] for s in ks)/len(ks)) - 1,
                  "paired": sum((nd[s]-b[s])/b[s] for s in ks)/len(ks),
                }
                for agg,v in vals.items():
                    for t in TARGETS:
                        if abs(v*100 - t) < 0.35:
                            hits.append((abs(v*100-t), metric, ref, src, wname, agg, v*100))
hits.sort()
print("=== near-misses for -9.11% and -6.17% ===")
if not hits: print("   NONE within 0.35pp under any metric/reference/source/window/aggregation")
for h in hits[:14]: print(f"   |{h[0]:.3f}| {h[1]:<15} vs {h[2]:<16} [{h[3]:<5}] {h[4]:<7} {h[5]:<6} = {h[6]:+.3f}%")


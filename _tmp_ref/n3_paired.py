import json, pathlib, csv
ROOT = pathlib.Path(".")
repro = [r for r in csv.DictReader(open(ROOT/"RAVEN_MCS_PUBLIC_REPRO_R1"/"tables"/"TABLE_II_WORSTGROUP_PER_SEED.csv", newline="", encoding="utf-8")) if r["dataset"]=="uair"]
TEST = set(range(30011,30021))
def rmap(m): return {int(r["seed"]): float(r["RMSE_mu"]) for r in repro if r["method"]==m}
def tmap(m):
    d = ROOT/"artifacts"/"e3_formal_runs_r1"/"runs"/"uair"/m; out={}
    for sd in d.glob("seed*"):
        f=sd/"final_metrics.json"
        if f.exists(): out[int(sd.name.replace("seed",""))]=float(json.loads(f.read_text(encoding="utf-8"))["RMSE_mu"])
    return out
nd = rmap("raven_wo_design")
print(f"{'comparison':<34} {'window':<7} {'ratio-of-means':>15} {'paired-mean':>13}")
for bname, b in (("fedavg(tree)", tmap("fedavg_window")), ("fedavg(repro)", rmap("fedavg_window")),
                 ("twostage(tree)", tmap("twostage_hajek")), ("twostage(repro)", rmap("twostage_hajek")),
                 ("fedau(repro)", rmap("fedau_window")), ("obsuse(repro)", rmap("obsuse_window"))):
    for lab, sel in (("TEST10", TEST), ("ALL20", None)):
        ks = sorted(s for s in nd if s in b and (sel is None or s in sel))
        if not ks: continue
        rm = (sum(nd[s] for s in ks)/len(ks)) / (sum(b[s] for s in ks)/len(ks)) - 1
        pm = sum((nd[s]-b[s])/b[s] for s in ks)/len(ks)
        print(f"  NoDesign vs {bname:<21} {lab:<7} {rm*100:>14.3f}% {pm*100:>12.3f}%")

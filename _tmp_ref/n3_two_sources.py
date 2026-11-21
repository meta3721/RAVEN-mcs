import json, pathlib, csv
ROOT = pathlib.Path(".")
per_seed = ROOT/"RAVEN_MCS_PUBLIC_REPRO_R1"/"tables"/"TABLE_II_WORSTGROUP_PER_SEED.csv"
rows = [r for r in csv.DictReader(open(per_seed, newline="", encoding="utf-8")) if r["dataset"]=="uair"]
print("CSV uair methods:", sorted({r["method"] for r in rows}))
csv_fa = {int(r["seed"]): float(r["RMSE_mu"]) for r in rows if r["method"]=="fedavg_window"}
tree = {}
for d in sorted((ROOT/"artifacts"/"e3_formal_runs_r1"/"runs"/"uair"/"fedavg_window").glob("seed*")):
    fm = json.loads((d/"final_metrics.json").read_text(encoding="utf-8"))
    tree[int(d.name.replace("seed",""))] = float(fm["RMSE_mu"])
print(f"{'seed':>6} {'CSV(pubrepro)':>14} {'E3tree':>14} {'diff':>12} {'rel%':>9}")
diffs=[]
for s in sorted(set(csv_fa)&set(tree)):
    a,b = csv_fa[s], tree[s]; d=a-b; diffs.append(abs(d)/b*100)
    print(f"{s:>6} {a:>14.6f} {b:>14.6f} {d:>12.6f} {d/b*100:>9.4f}")
print()
print("n csv =", len(csv_fa), " n tree =", len(tree), " common =", len(diffs))
print("CSV  mean = %.6f" % (sum(csv_fa.values())/len(csv_fa)))
print("E3   mean = %.6f" % (sum(tree.values())/len(tree)))
print("max rel%% = %.4f  median rel%% = %.4f  n_exact(<=1e-9) = %d" % (max(diffs), sorted(diffs)[len(diffs)//2], sum(1 for d in diffs if d<=1e-9)))

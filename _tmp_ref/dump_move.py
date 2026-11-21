import json, pathlib, pandas as pd
ROOT = pathlib.Path("."); O = ROOT/"results_active_set_repair/round_v1"
E3 = ROOT/"artifacts/e3_formal_runs_r1/runs/uair"
rows=[]
for m in ("fedavg_window","fedasync_window","flamf_timealign_adapted","debt_cal"):
    old = [json.loads((E3/m/f"seed{s}"/"final_metrics.json").read_text(encoding="utf-8"))["RMSE_mu"] for s in range(30001,30021)]
    new = [json.loads((O/"repair/C0_frozen/uair"/m/f"seed{s}"/"final_metrics.json").read_text(encoding="utf-8"))["RMSE_mu"] for s in range(30001,30021)]
    om, nm = sum(old)/20, sum(new)/20
    rows.append({"method": m, "old_contaminated": round(om,6), "new_licensed": round(nm,6),
                 "abs": round(nm-om,6), "rel_pct": round((nm-om)/om*100,4)})
df = pd.DataFrame(rows)
print("=== cell movement, all four rebuilt U-Air no-Design rows (20 seeds) ===")
print(df.to_string(index=False))
print()
print("=== E3 P2 coverage per run (licensed set) vs published ===")
pr = pd.read_csv(O/"P2_COVERAGE_PER_RUN.csv")
print(pr.groupby("method")["active_windows"].agg(["count","mean","min","max"]).round(3).to_string())
print()
print("published: runs=180 mean=70.10 range=63-75")

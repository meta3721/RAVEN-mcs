import csv, json, pathlib, statistics as st
E3 = pathlib.Path("artifacts/e3_formal_runs_r1/runs"); E4 = pathlib.Path("artifacts/e4_core_mechanism_ablation_r1/runs")
S = list(range(30001,30021))
def mean(ds, arm, k):
    d = pathlib.Path(E4 if (E4/ds/arm).exists() else E3)/ds/arm
    if not d.exists(): return None
    v=[]
    for s in S:
        f=d/f"seed{s}"/"final_metrics.json"
        if not f.is_file(): return None
        x=json.loads(f.read_text(encoding="utf-8")).get(k)
        if not isinstance(x,(int,float)): return None
        v.append(float(x))
    return st.mean(v), st.stdev(v)
print("=== bundle TABLE_E4_CORE_ABLATION.csv vs the trees ===")
rows = list(csv.DictReader(open("RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_E4_CORE_ABLATION.csv", newline="", encoding="utf-8")))
for r in rows:
    ds = r["dataset"].lower().replace("-","")
    cfg = r["configuration"]
    arm = {"RAVEN-Design":"raven","RAVEN-NoDesign":"raven_wo_design","RAVEN-w/o-Inst":"raven_wo_inst",
           "RAVEN-w/o-Obs":"raven_wo_obs","RAVEN-w/o-Use":"raven_wo_use","RAVEN-w/o-Debt":"raven_wo_debt",
           "RAVEN-Full":"raven"}.get(cfg, cfg.replace("-","_").lower())
    m = mean(ds, arm, "Delta_group")
    if m is None:
        print(f"  {r['dataset']:<12} {cfg:<18} bundle d_g={float(r['Delta_group_mean']):.6f}   (no tree arm '{arm}')")
    else:
        b=float(r["Delta_group_mean"]); ok = "AGREE" if abs(b-m[0])<5e-4 else "*** DIFF ***"
        print(f"  {r['dataset']:<12} {cfg:<18} bundle d_g={b:.6f}   tree {arm:<16} {m[0]:.6f}   {ok}")

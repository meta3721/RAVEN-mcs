import json, pathlib, csv
ROOT = pathlib.Path(".")
sealed = {r["method"]: r for r in csv.DictReader(open(ROOT/"manuscript_evidence_closure_r1"/"01_table_sources"/"TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv", newline="", encoding="utf-8")) if r["dataset"]=="U-Air"}
repro  = [r for r in csv.DictReader(open(ROOT/"RAVEN_MCS_PUBLIC_REPRO_R1"/"tables"/"TABLE_II_WORSTGROUP_PER_SEED.csv", newline="", encoding="utf-8")) if r["dataset"]=="uair"]

def tree_means(method):
    d = ROOT/"artifacts"/"e3_formal_runs_r1"/"runs"/"uair"/method
    acc = {}
    seeds=[]
    if not d.exists(): return None, 0
    for sd in sorted(d.glob("seed*")):
        f = sd/"final_metrics.json"
        if not f.exists(): continue
        j = json.loads(f.read_text(encoding="utf-8")); seeds.append(int(sd.name.replace("seed","")))
        for k,v in j.items():
            if isinstance(v,(int,float)) and not isinstance(v,bool): acc.setdefault(k,[]).append(float(v))
    return {k: sum(v)/len(v) for k,v in acc.items()}, len(seeds)

PRINTED = {"RMSE_mu":1.1882, "WorstGroupRMSE":1.2596, "Delta_group":1.1218, "Delta_c_s":1.2621}
SEL = {"RMSE_mu":20.631670048948354, "Tail_RMSE":20.78101674317128, "Delta_group":1.1217615790653563, "Delta_c_s":1.2621315859838975}
for m in ("fedavg_window","twostage_hajek","raven","local_hajek"):
    tm, n = tree_means(m)
    print(f"\n### {m}  (tree n={n})")
    if tm is None: print("   no tree dir"); continue
    for k in ("RMSE_mu","Tail_RMSE","WorstGroupRMSE","Delta_group","Delta_c_s","MAE_mu","RMSE_rho"):
        if k in tm: print(f"   tree mean {k:<16} = {tm[k]:.6f}")
    print("   -- printed Table III (paper) --")
    for k,v in PRINTED.items():
        if k in tm: print(f"      {k:<16} printed={v:<10} tree={tm[k]:.4f}  diff={v-tm[k]:+.4f}  {'MATCH' if abs(v-tm[k])<=5e-5 else 'DIFF'}")
    print("   -- sealed FINAL source --")
    s = sealed.get({"fedavg_window":"FedAvg-Window","twostage_hajek":"TwoStage-Hajek","raven":"RAVEN-MCS","local_hajek":"Local-Hajek"}[m])
    if s:
        for k,sc in (("RMSE_mu","RMSE_mu_mean"),("Tail_RMSE","Tail_RMSE_mean"),("Delta_group","Delta_group_mean"),("Delta_c_s","Delta_c_s_mean")):
            sv=float(s[sc]); tv=tm.get(k)
            print(f"      {k:<16} sealed={sv:<20.10f} tree={tv if tv is None else round(tv,6)}  ratio={sv/tv if tv else float('nan'):.4f}")

print("\n### repro CSV WorstGroupRMSE mean (uair)")
for m in ("fedavg_window","twostage_hajek","raven","local_hajek","fedau_window","obsuse_window","raven_wo_design"):
    v=[float(r["WorstGroupRMSE"]) for r in repro if r["method"]==m]
    rm=[float(r["RMSE_mu"]) for r in repro if r["method"]==m]
    if v: print(f"   {m:<18} WG mean={sum(v)/len(v):.6f}  RMSE_mu mean={sum(rm)/len(rm):.6f}  n={len(v)}")


import json, pathlib
ROOT = pathlib.Path(".")
def vec(tree, ds, m, key):
    d = ROOT/tree/ds/m
    return [json.loads((d/f"seed{s}"/"final_metrics.json").read_text(encoding="utf-8"))[key] for s in range(30001,30021)]
E3="artifacts/e3_formal_runs_r1/runs"; E4="artifacts/e4_core_mechanism_ablation_r1/runs"
pairs = [("raven_wo_inst",E4,"twostage_hajek",E3), ("inst_cal",E3,"raven_wo_debt",E4),
         ("raven",E3,"raven_wo_obs",E4), ("raven",E3,"raven_wo_use",E4),
         ("raven",E3,"raven_wo_debt",E4), ("debt_cal",E3,"raven_wo_debt",E4)]
for a,ta,b,tb in pairs:
    print(f"--- {a} [{ta.split('/')[1]}]  vs  {b} [{tb.split('/')[1]}]")
    for key in ("RMSE_mu","Delta_group","Delta_c_s"):
        va, vb = vec(ta,"uair",a,key), vec(tb,"uair",b,key)
        d = max(abs(x-y) for x,y in zip(va,vb))
        same = "IDENTICAL per seed" if d == 0.0 else f"max|d|={d:.3e}"
        print(f"      {key:<12} {sum(va)/20:.12f}  {sum(vb)/20:.12f}   {same}")

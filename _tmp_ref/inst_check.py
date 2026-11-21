import csv, json, pathlib, statistics as st
rows = [r for r in csv.DictReader(open("RAVEN_MCS_PUBLIC_REPRO_R1/tables/E4_ABLATION_RELATIVE_CHANGE.csv", newline="", encoding="utf-8"))
        if r["dataset"]=="U-Air" and r["component"]=="Inst" and r["metric"]=="Delta_group"]
rows.sort(key=lambda r: int(r["seed"]))
print("=== bundle CSV: U-Air / RAVEN-w/o-Inst / Delta_group ===")
for r in rows[:6]:
    print(f"  seed{r['seed']}  full_RAVEN={float(r['full_RAVEN']):.6f}  ablation={float(r['ablation']):.6f}  rel={float(r['relative_change_percent']):+.4f}%")
print(f"  means: full={st.mean(float(r['full_RAVEN']) for r in rows):.6f}  ablation={st.mean(float(r['ablation']) for r in rows):.6f}")
E3 = pathlib.Path("artifacts/e3_formal_runs_r1/runs/uair"); E4 = pathlib.Path("artifacts/e4_core_mechanism_ablation_r1/runs/uair")
def mean(d, k="Delta_group"):
    v=[json.loads((d/f"seed{s}"/"final_metrics.json").read_text(encoding="utf-8"))[k] for s in range(30001,30021)]
    return sum(v)/len(v)
print()
print("=== trees ===")
print(f"  E3 raven          Delta_group mean = {mean(E3/'raven'):.6f}")
print(f"  E4 raven_wo_inst  Delta_group mean = {mean(E4/'raven_wo_inst'):.6f}   (rel vs raven: {(mean(E4/'raven_wo_inst')/mean(E3/'raven')-1)*100:+.4f}%)")
print(f"  E3 inst_cal       Delta_group mean = {mean(E3/'inst_cal'):.6f}")
print(f"  E4 raven_wo_debt  Delta_group mean = {mean(E4/'raven_wo_debt'):.6f}")

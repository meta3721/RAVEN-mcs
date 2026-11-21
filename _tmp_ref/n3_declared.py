import json, pathlib, csv
ROOT = pathlib.Path(".")
src = ROOT/"manuscript_evidence_closure_r1"/"01_table_sources"/"TABLE_II_E3_MAIN_EFFECTIVENESS_FINAL.csv"
rows = list(csv.DictReader(open(src, newline="", encoding="utf-8")))
print("datasets:", sorted({r["dataset"] for r in rows}))
print(f"\n{'dataset':<12} {'method':<18} {'n':>4} {'RMSE_mu_display':>16} {'RMSE_mu_mean':>13} {'Delta_group_display':>20} {'Delta_c_s_display':>18}")
for r in rows:
    print(f"{r['dataset']:<12} {r['method']:<18} {r['n']:>4} {r['RMSE_mu_display']:>16} {float(r['RMSE_mu_mean']):>13.6f} {r['Delta_group_display']:>20} {r['Delta_c_s_display']:>18}")

print("\n=== declared-source uair FedAvg vs the two frozen batches ===")
CSV = ROOT/"RAVEN_MCS_PUBLIC_REPRO_R1"/"tables"/"TABLE_II_WORSTGROUP_PER_SEED.csv"
c = [r for r in csv.DictReader(open(CSV, newline="", encoding="utf-8")) if r["dataset"]=="uair"]
for m in ("fedavg_window","local_hajek","raven","twostage_hajek"):
    d = {int(r["seed"]): float(r["RMSE_mu"]) for r in c if r["method"]==m}
    print(f"  repro CSV {m:<16} mean={sum(d.values())/len(d):.6f}")
print("\n  declared source rows for uair are listed above; compare the RMSE_mu_mean column.")

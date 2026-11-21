import csv, pathlib
b = list(csv.DictReader(open("RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv", newline="", encoding="utf-8")))
e = list(csv.DictReader(open("results_active_set_repair/round_v1/E2_UAIR_CELLS.csv", newline="", encoding="utf-8")))
e = [r for r in e if r["status"]=="OK"]
for m in ("fedavg_window","fedasync_window","debt_cal"):
    bm = [float(r["RMSE_mu"]) for r in b if r["dataset"]=="uair" and r["method"]==m]
    em = [float(r["RMSE_mu_std"]) for r in e if r["method"]==m]
    print(f"  {m:<20} bundle mean={sum(bm)/len(bm):.6f} (n={len(bm)})   rebuilt mean={sum(em)/len(em):.6f} (n={len(em)})")

import csv, pathlib
O = pathlib.Path("results_active_set_repair/round_v1")
e2 = {r["method"]: r for r in csv.DictReader(open(O/"E2_UAIR_SUMMARY.csv", newline="", encoding="utf-8"))}
cols = ["RMSE_mu_std_mean","RMSE_mu_std_std","WorstGroupRMSE_std_mean","WorstGroupRMSE_std_std",
        "Delta_group_mean","Delta_group_std","Delta_c_s_mean","Delta_c_s_std"]
print("=== values for the replacement cells (20 seeds, mean / std; 4 dp as the tables print) ===")
for m in ("fedavg_window","fedasync_window","flamf_timealign_adapted","debt_cal"):
    r = e2[m]
    print(f"{m:<24} " + "  ".join(f"{float(r[c]):.4f}" for c in cols))
print()
print("=== per-seed worst-case for block RMSEs (tab:app_block_rmse needs 4 blocks + WG) ===")
cells = [r for r in csv.DictReader(open(O/"E2_UAIR_CELLS.csv", newline="", encoding="utf-8")) if r["status"]=="OK"]
for m in ("fedavg_window",):
    rs = [r for r in cells if r["method"]==m]
    for b in range(4):
        v = [float(r[f"RMSE_block{b}_std"]) for r in rs]
        print(f"  {m} block{b}: mean={sum(v)/len(v):.4f} std={(sum((x-sum(v)/len(v))**2 for x in v)/(len(v)-1))**0.5:.4f}")
    wg = [float(r["WorstGroupRMSE_std"]) for r in rs]
    print(f"  {m} WG:      mean={sum(wg)/len(wg):.4f} std={(sum((x-sum(wg)/len(wg))**2 for x in wg)/(len(wg)-1))**0.5:.4f}")

import pandas as pd, pathlib
O = pathlib.Path("results_active_set_repair/round_v1")
pd.set_option("display.width", 250)
e2 = pd.read_csv(O/"E2_UAIR_SUMMARY.csv")
print("=== R1: no-Design family on the licensed set (20 seeds) ===")
cols = ["method","RMSE_mu_std_mean","RMSE_mu_std_std","RMSE_mu_phys_mean","WorstGroupRMSE_std_mean",
        "WorstGroupRMSE_std_std","Delta_group_mean","Delta_c_s_mean"]
order = ["fedavg_window","fedasync_window","flamf_timealign_adapted","debt_cal",
         "fedau_window","obsuse_window","raven_wo_design"]
e2["o"] = e2["method"].map({m:i for i,m in enumerate(order)})
print(e2.dropna(subset=["o"]).sort_values("o")[cols].round(6).to_string(index=False))
print()
p = pd.read_csv(O/"PAIRED_STATS.csv")
print("=== R2: RAVEN-NoDesign minus comparator, paired relative ===")
for met in ("RMSE_mu_std","WorstGroupRMSE_std","Delta_group","Delta_c_s"):
    sub = p[["comparator","slice","n",f"{met}_rel_mean",f"{met}_rel_lo",f"{met}_rel_hi",f"{met}_wins",f"{met}_holm"]].copy()
    sub.columns = ["comparator","slice","n","rel_mean","lo","hi","wins","holm_p"]
    print(f"--- {met}")
    print(sub.round(6).to_string(index=False))

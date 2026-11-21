"""Append FedAU-Window rows from the per-seed result CSV into the two figure CSVs."""
import pandas as pd
from pathlib import Path

BASE = Path(r"D:\Cursor\raven.mcs\_paper_work")
per_seed = pd.read_csv(BASE / "fedau_window_results" / "e3_fedau_window_per_seed.csv")
fedau = per_seed[per_seed["method"] == "fedau_window"].copy()
fedau["dataset"] = fedau["dataset"].map({"sensorscope": "SensorScope", "uair": "U-Air"})
fedau["method"] = "FedAU-Window"
fedau["seed"] = fedau["seed"].astype(int)

# Structural figure CSV
struct_path = BASE / "figure_data" / "FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv"
struct = pd.read_csv(struct_path)
rows = fedau[["dataset", "method", "seed", "Delta_group", "Delta_c_s"]].copy()
rows["Delta_group_status"] = "VALID"
rows["Delta_c_s_status"] = "VALID"
rows["comparison_class"] = "SCI_COMPARABLE_MAIN"
rows = rows[["dataset", "method", "seed", "Delta_group", "Delta_group_status",
             "Delta_c_s", "Delta_c_s_status", "comparison_class"]]
struct = pd.concat([struct, rows], ignore_index=True)
struct.to_csv(struct_path, index=False)

# Prediction figure CSV (MAE_mu / RMSE_rho are unused by fig4; leave blank)
pred_path = BASE / "figure_data" / "FIG_E3_E3_PREDICTION_RISK.csv"
pred = pd.read_csv(pred_path)
prows = fedau[["dataset", "method", "seed", "RMSE_mu", "Tail_RMSE"]].copy()
prows["MAE_mu"] = ""
prows["RMSE_rho"] = ""
prows["comparison_class"] = "SCI_COMPARABLE_MAIN"
prows = prows[["dataset", "method", "seed", "RMSE_mu", "MAE_mu", "Tail_RMSE",
               "RMSE_rho", "comparison_class"]]
pred = pd.concat([pred, prows], ignore_index=True)
pred.to_csv(pred_path, index=False)

print(f"appended {len(rows)} structural rows and {len(prows)} prediction rows for FedAU-Window")

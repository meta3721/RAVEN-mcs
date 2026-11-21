"""Append ObsUse-Window rows into fig3/fig4 CSVs if missing."""
from pathlib import Path
import pandas as pd

BASE = Path(r"D:\Cursor\raven.mcs\_paper_work")
per_seed = pd.read_csv(BASE / "obsuse_window_results" / "e3_obsuse_window_per_seed.csv")
obs = per_seed[per_seed["method"] == "obsuse_window"].copy()
obs["dataset"] = obs["dataset"].map({"sensorscope": "SensorScope", "uair": "U-Air"})
obs["method"] = "ObsUse-Window"
obs["seed"] = obs["seed"].astype(int)

struct_path = BASE / "figure_data" / "FIG_E2_E3_STRUCTURAL_ALIGNMENT.csv"
struct = pd.read_csv(struct_path)
struct = struct[struct["method"] != "ObsUse-Window"]
rows = obs[["dataset", "method", "seed", "Delta_group", "Delta_c_s"]].copy()
rows["Delta_group_status"] = "VALID"
rows["Delta_c_s_status"] = "VALID"
rows["comparison_class"] = "SCI_COMPARABLE_MAIN"
rows = rows[["dataset", "method", "seed", "Delta_group", "Delta_group_status",
             "Delta_c_s", "Delta_c_s_status", "comparison_class"]]
struct = pd.concat([struct, rows], ignore_index=True)
struct.to_csv(struct_path, index=False)

pred_path = BASE / "figure_data" / "FIG_E3_E3_PREDICTION_RISK.csv"
pred = pd.read_csv(pred_path)
pred = pred[pred["method"] != "ObsUse-Window"]
prows = obs[["dataset", "method", "seed", "RMSE_mu", "Tail_RMSE"]].copy()
prows["MAE_mu"] = ""
prows["RMSE_rho"] = ""
prows["comparison_class"] = "SCI_COMPARABLE_MAIN"
prows = prows[["dataset", "method", "seed", "RMSE_mu", "MAE_mu", "Tail_RMSE",
               "RMSE_rho", "comparison_class"]]
pred = pd.concat([pred, prows], ignore_index=True)
pred.to_csv(pred_path, index=False)
print(f"appended {len(rows)} structural and {len(prows)} prediction rows for ObsUse-Window")

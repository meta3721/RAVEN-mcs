"""Complete the two remaining section-7 outputs: tables/MOVEMENT.csv and tables/STAGE_C_H.csv."""
import csv
import json
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_server_optimizer" / "round_v1"

# ---- MOVEMENT.csv: per-run movement under the new config, plus the frozen SGD reference ----
val = list(csv.DictReader((OUT / "tables" / "STAGE_A_VALIDATION.csv").open(encoding="utf-8")))
mov = []
for r in val:
    if r["blocked"] == "True":
        mov.append({"block": r["block"], "arm": r["arm"], "config": "eta_s=%s" % r["eta_s"],
                    "seed": r["seed"], "blocked": True, "overall_rel_movement": "",
                    "head_0_weight_rel": "", "head_8_bias_rel": "", "spatial_weight_rel": ""})
        continue
    mov.append({"block": r["block"], "arm": r["arm"], "config": "eta_s=%s" % r["eta_s"],
                "seed": r["seed"], "blocked": False,
                "overall_rel_movement": r.get("overall_rel_movement", ""),
                "head_0_weight_rel": r.get("head_0_weight_rel", ""),
                "head_8_bias_rel": r.get("head_8_bias_rel", ""),
                "spatial_weight_rel": r.get("spatial_weight_rel", "")})
pf = json.loads((OUT / "PREFLIGHT_SECTION0.json").read_text(encoding="utf-8"))
for r in pf["records"]:
    mov.append({"block": r["dataset"], "arm": r["arm"], "config": "frozen_SGD", "seed": r["seed"],
                "blocked": False, "overall_rel_movement": r["overall_rel_movement"],
                "head_0_weight_rel": r["tensors"]["head.0.weight"]["rel"],
                "head_8_bias_rel": r["tensors"]["head.8.bias"]["rel"],
                "spatial_weight_rel": r["tensors"]["spatial.weight"]["rel"]})
with (OUT / "tables" / "MOVEMENT.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["block", "arm", "config", "seed", "blocked",
                                      "overall_rel_movement", "head_0_weight_rel",
                                      "head_8_bias_rel", "spatial_weight_rel"])
    w.writeheader()
    w.writerows(mov)
print("wrote MOVEMENT.csv with", len(mov), "rows")

# ---- STAGE_C_H.csv: the H summary ----
cv = json.loads((OUT / "S1P_STAGE_C_H.json").read_text(encoding="utf-8"))
rows = []
for b, v in cv["H"].items():
    if v.get("verdict") == "not_run":
        rows.append({"block": b, "verdict": v["verdict"], "reason": v.get("reason", ""),
                     "eta_s_star": "", "n_paired_seeds": 0, "mean_H": "", "boot_lo": "", "boot_hi": "",
                     "paired_sd": "", "MDE80_n5": "", "cond_mean_ge_1pct": "", "cond_lcb_gt_0.5pct": "",
                     "cond_mde_lt_half_H": "", "share_kr_le3": "",
                     "kr_excluded_from_GO": "", "fedavg_test_mean": "", "simoracle_test_mean": ""})
        continue
    kr = v["kr_clause"]
    fed = [float(x) for x in v["fedavg_test_RMSE_mu"].values()]
    sim = [float(x) for x in v["raven_simoracle_test_RMSE_mu"].values()]
    rows.append({"block": b, "verdict": v["verdict"], "reason": "", "eta_s_star": v["eta_s_star"],
                 "n_paired_seeds": v["n_paired_seeds"], "mean_H": v["mean_H"],
                 "boot_lo": v["boot_lo"], "boot_hi": v["boot_hi"], "paired_sd": v["paired_sd"],
                 "MDE80_n5": v["MDE80_n5"], "cond_mean_ge_1pct": v["cond_mean_ge_1pct"],
                 "cond_lcb_gt_0.5pct": v["cond_lcb_gt_0.5pct"],
                 "cond_mde_lt_half_H": v["cond_mde_lt_half_H"],
                 "share_kr_le3": kr["share_kr_le3"], "kr_excluded_from_GO": kr["excluded_from_GO"],
                 "fedavg_test_mean": sum(fed) / len(fed), "simoracle_test_mean": sum(sim) / len(sim)})
with (OUT / "tables" / "STAGE_C_H.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("wrote STAGE_C_H.csv with", len(rows), "rows")

# ---- STAGE_B_GRID.csv is required only "if run"; record explicitly that it was not ----
(OUT / "tables" / "STAGE_B_GRID.csv").write_text(
    "block,arm,R,seed,status\n# Stage B not run: section 5 applies it only to blocks not PASS at "
    "Stage A; SensorScope and U-Air both PASS and NSW-Traffic is BLOCKED before any run\n",
    encoding="utf-8")
print("wrote STAGE_B_GRID.csv (not-run marker)")

"""Emit GATES_V51.csv from the A1'/A2'/A3' outputs (columns: observed, tolerance, tolerance_source, pass)."""
from __future__ import annotations

import json
import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results_w1_ladder/round_v5_1"
g = json.loads((OUT / "A1P_ORACLE_GATES.json").read_text(encoding="utf-8"))
a2 = json.loads((OUT / "A2P_SUMMARY.json").read_text(encoding="utf-8"))
imp = pd.read_csv(OUT / "A1P_IMPL.csv")

rows = []


def add(gate, observed, tolerance, source, ok, scope):
    rows.append({"gate": gate, "scope": scope, "observed": observed,
                 "tolerance": tolerance, "tolerance_source": source,
                 "pass": bool(ok)})


# --- A1' gates
add("B-G1", g["B-G1"]["observed"], 0, g["B-G1"]["tolerance_source"], g["B-G1"]["pass"],
    "120 runs: 3 arms x 2 datasets x 20 seeds")
add("G-self", g["G-self_AM1"]["observed_alpha_linf"], 1e-8, g["G-self_AM1"]["tolerance_source"],
    bool(g["G-self_AM1"]["observed_alpha_linf"] <= 1e-8), "120 runs")
add("G-self", g["G-self_AM1"]["observed_endpoint_err"], 1e-12,
    g["G-self_AM1"]["tolerance_source"], bool(g["G-self_AM1"]["observed_endpoint_err"] <= 1e-12),
    "120 runs (max over |d_group|, |d_c-s|)")
add("O-G0", g["O-G0"]["observed_primal"], g["O-G0"]["tolerance_primal"],
    g["O-G0"]["tolerance_source"], bool(g["O-G0"]["observed_primal"] <= g["O-G0"]["tolerance_primal"]),
    "80 runs / %d windows" % g["O-G0"]["n_windows"])
add("O-G0", g["O-G0"]["observed_stationarity"], g["O-G0"]["tolerance_stationarity"],
    g["O-G0"]["tolerance_source"],
    bool(g["O-G0"]["observed_stationarity"] <= g["O-G0"]["tolerance_stationarity"]),
    "80 runs / %d windows" % g["O-G0"]["n_windows"])
add("O-G0", g["O-G0"]["observed_cs"], g["O-G0"]["tolerance_cs"],
    g["O-G0"]["tolerance_source"], bool(g["O-G0"]["observed_cs"] <= g["O-G0"]["tolerance_cs"]),
    "80 runs / %d windows" % g["O-G0"]["n_windows"])
add("O-G0", g["O-G0_sample"]["max_primal"], g["O-G0_sample"]["tolerance_primal"] if "tolerance_primal" in g["O-G0_sample"] else 1e-13,
    g["O-G0"]["tolerance_source"],
    bool(g["O-G0_sample"]["max_primal"] <= 1e-13), "200-window sample")
add("O-G0", g["O-G0_sample"]["max_stationarity"], 1e-12, g["O-G0"]["tolerance_source"],
    bool(g["O-G0_sample"]["max_stationarity"] <= 1e-12), "200-window sample")
add("O-G1", g["O-G1"]["observed_max_obj_gap"], g["O-G1"]["tolerance"],
    g["O-G1"]["tolerance_source"], g["O-G1"]["pass"], "200 random windows")
add("O-G2", g["O-G2"]["observed"], g["O-G2"]["tolerance"], g["O-G2"]["tolerance_source"],
    g["O-G2"]["pass"], "K = 1..64 uniform control")
add("O-gate", max(float(imp.eps_impl_group.max()), float(imp.eps_impl_cs.max())),
    g["O-gate"]["threshold_eps_impl"], g["O-gate"]["tolerance_source"],
    False, "all 160 measured runs (2 arms x 2 datasets x 20 seeds x 2 endpoints)")
for cell, d in g["O-gate"]["per_cell"].items():
    add("O-gate", d["max_eps_impl"], g["O-gate"]["threshold_eps_impl"],
        g["O-gate"]["tolerance_source"], d["verdict"] == "certified", cell)

# --- A2' gates
gg = a2["gates"]
add("G0-a", gg["AM3_G0a"]["observed_max_d_rmse"], gg["AM3_G0a"]["tolerance"],
    "AM-3: checkpoint/theta re-score equals final_metrics.json on non-trigger rows",
    gg["AM3_G0a"]["pass"], "222 non-trigger rows (RMSE_mu)")
add("G0-a", gg["AM3_G0a"]["observed_max_d_head"], gg["AM3_G0a"]["tolerance"],
    "AM-3 (Head_RMSE)", gg["AM3_G0a"]["pass"], "222 non-trigger rows")
add("G0-a", gg["AM3_G0a"]["observed_max_d_tail"], gg["AM3_G0a"]["tolerance"],
    "AM-3 (Tail_RMSE)", gg["AM3_G0a"]["pass"], "222 non-trigger rows")
add("G0-b", gg["AM3_G0b"]["observed_max_rel_tableII"], gg["AM3_G0b"]["tolerance_rel"],
    "AM-3: theta re-score vs TABLE_II_WORSTGROUP_PER_SEED.csv per seed (relative)",
    gg["AM3_G0b"]["pass"], "18 trigger rows, trigger confirmed in each own window_metrics.json")
add("G0-b", gg["AM3_G0b"]["unlisted_trigger_rows"], 0,
    "AM-3: any trigger outside the pre-fixed set stops A2'",
    gg["AM3_G0b"]["unlisted_trigger_rows"] == 0, "all 240 runs swept")
add("G0-b", gg["AM3_G0b"]["listed_without_trigger"], 0,
    "AM-3: any listed row lacking the trigger stops A2'",
    gg["AM3_G0b"]["listed_without_trigger"] == 0, "18 listed rows")
add("G0-c", gg["AM3_G0c"]["observed_max_rel"], gg["AM3_G0c"]["tolerance_rel"],
    "AM-4: stored WorstGroupRMSE of the frozen arms reproduced within 1e-8 relative",
    gg["AM3_G0c"]["pass"], "80 rows (fedavg_window, raven x 2 datasets x 20 seeds)")

pd.DataFrame(rows).to_csv(OUT / "GATES_V51.csv", index=False)
print(pd.DataFrame(rows)[["gate", "scope", "observed", "tolerance", "pass"]].to_string(index=False))

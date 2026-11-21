"""Emit GATES_V51A.csv for round v5.1a (columns: gate, scope, observed, tolerance,
tolerance_source, pass) from O_GATES_RERUN.json and the A1'/evidence artefacts.
"""
from __future__ import annotations

import json
import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results_w1_ladder/round_v5_1a"
g = json.loads((OUT / "O_GATES_RERUN.json").read_text(encoding="utf-8"))
ev = json.loads((OUT / "ORACLE_EVIDENCE.json").read_text(encoding="utf-8"))
imp = pd.read_csv(OUT / "A1P_IMPL_RERUN.csv")

rows = []


def add(gate, scope, observed, tolerance, source, ok):
    rows.append({"gate": gate, "scope": scope, "observed": observed, "tolerance": tolerance,
                 "tolerance_source": source, "pass": bool(ok)})


# ---- gates kept from v5.1 (unchanged tolerances) --------------------------------------
add("B-G1", "120 runs: 3 arms x 2 datasets x 20 seeds", g["B-G1"]["observed"], 0,
    g["B-G1"]["tolerance_source"], g["B-G1"]["pass"])
add("G-self", "120 runs (alpha L-inf vs final_metrics)", g["G-self_AM1"]["observed_alpha_linf"],
    1e-8, g["G-self_AM1"]["tolerance_source"],
    bool(g["G-self_AM1"]["observed_alpha_linf"] <= 1e-8))
add("G-self", "120 runs (max over |d_group|, |d_c-s|)", g["G-self_AM1"]["observed_endpoint_err"],
    1e-12, g["G-self_AM1"]["tolerance_source"],
    bool(g["G-self_AM1"]["observed_endpoint_err"] <= 1e-12))

# ---- O-G0 -----------------------------------------------------------------------------
og0 = g["O-G0"]
scope = "80 runs / %d windows (2 arms x 2 datasets x 20 seeds)" % og0["n_windows"]
add("O-G0", scope + " / primal", og0["observed_primal"], og0["tolerance_primal"],
    og0["tolerance_source"], bool(og0["observed_primal"] <= og0["tolerance_primal"]))
add("O-G0", scope + " / stationarity", og0["observed_stationarity"], og0["tolerance_stationarity"],
    og0["tolerance_source"],
    bool(og0["observed_stationarity"] <= og0["tolerance_stationarity"]))
add("O-G0", scope + " / complementary slackness", og0["observed_cs"], og0["tolerance_cs"],
    og0["tolerance_source"], bool(og0["observed_cs"] <= og0["tolerance_cs"]))

# ---- O-G1 -----------------------------------------------------------------------------
og1 = g["O-G1"]
add("O-G1", "%d sampled windows (fresh CVXPY CLARABEL, projected back onto C_r)"
    % og1["n_windows"], og1["observed_max_gap"], og1["tolerance"], og1["tolerance_source"],
    og1["pass"])

# ---- O-G2 -----------------------------------------------------------------------------
og2 = g["O-G2"]
add("O-G2", "K = 1..64 uniform control", og2["observed"], og2["tolerance"],
    og2["tolerance_source"], og2["pass"])

# ---- debt algebra self-check ----------------------------------------------------------
sa = g["self_check_debt_algebra"]
add("O-debt-algebra", "identity residual on a real window", sa["identity_abs_error"], 1e-12,
    "AM-6: the debt oracle equals the minimiser of -Q^T M a + (1/(2k))||a - beta||^2 on C_r",
    bool(sa["identity_abs_error"] <= 1e-12))
add("O-debt-algebra", "best feasible perturbation improvement (%d sampled)"
    % sa["n_feasible_perturbations"], sa["best_improvement"], 0.0,
    "no feasible point may beat the oracle point", bool(sa["perturbation_not_better_1e-12"]))

# ---- independent optimality evidence --------------------------------------------------
bf = ev["brute_force_small_K"]
add("O-evid-brute", "small-K brute force, %d cases (K = 2..5)" % bf["n_cases"],
    bf["worst_objective_gap_oracle_minus_grid"], 1e-14,
    "AM-6 evidence: oracle objective <= dense (lam, tau) grid minimum over feasible points + 1e-14",
    bf["pass_objective_1e-14"])
add("O-evid-brute", "small-K brute force, worst ||alpha_oracle - alpha_grid||_inf",
    bf["worst_alpha_linf_oracle_vs_grid"], 1e-12,
    "AM-6 evidence: point agreement with the refined grid solution", 
    bool(bf["worst_alpha_linf_oracle_vs_grid"] <= 1e-12))
pb = ev["perturbation"]
add("O-evid-perturb", "perturbation test, %d windows" % pb["n_windows"], pb["worst_improvement"],
    1e-12, "AM-6 evidence: no sampled feasible perturbation lowers the objective by > 1e-12",
    pb["pass_1e-12"])
db = ev["dual_bound"]
add("O-evid-dual", "Fenchel duality gap, %d windows" % db["n_windows"], db["worst_gap"], 1e-12,
    "AM-6 evidence: f(x) - d(grad f(x)) <= 1e-12", db["pass_1e-12"])

# ---- O-gate ---------------------------------------------------------------------------
og = g["O-gate"]
add("O-gate", "all 160 measured runs (max over eps_impl_group, eps_impl_cs)", og["observed"],
    og["threshold_eps_impl"], og["tolerance_source"], og["pass"])
for cell, d in og["per_cell"].items():
    add("O-gate", cell, d["max_eps_impl"], og["threshold_eps_impl"], og["tolerance_source"],
        d["verdict"] == "certified")

# ---- structural re-check --------------------------------------------------------------
st = g["A1P_STRUCT"]
add("A1-STRUCT", "20 recomputed v4 rows (Delta_group, Delta_c-s)", st["max_abs_d_pp"], None,
    "AM-6: same contrasts / bootstrap / Holm families as v4; reported, not gated",
    True)
add("A1-STRUCT", "verdict changes vs round v4", st["verdict_changes"], 0,
    "AM-6: a verdict change is reported, not smoothed over", st["verdict_changes"] == 0)

df = pd.DataFrame(rows)
df.to_csv(OUT / "GATES_V51A.csv", index=False)
print(df[["gate", "scope", "observed", "tolerance", "pass"]].to_string(index=False))

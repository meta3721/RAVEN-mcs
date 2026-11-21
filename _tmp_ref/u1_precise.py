"""Precise U1 values for the write-up."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv("results_h_headroom/round_u1/tables/H_summary.csv")
u = df[df.dataset == "uair"].sort_values("condition")
hdr = ("condition", "H_nodesign", "ci_lo", "ci_hi", "sd_pp", "MDE_pp",
       "cost", "cost_lo", "cost_hi")
print(("{:<18}" + "{:>12}" * 8).format(*hdr))
for r in u.itertuples():
    sd = (r.H_nodesign_RMSE_mu_ci_hi - r.H_nodesign_RMSE_mu) * np.sqrt(r.n) / stats.t.ppf(0.975, r.n - 1)
    se = sd / np.sqrt(r.n)
    mde = (stats.t.ppf(0.975, r.n - 1) + stats.t.ppf(0.8, r.n - 1)) * se
    print(("{:<18}" + "{:>11.4f}%" + "{:>9.4f}%" * 2 + "{:>8.3f}" * 2 + "{:>8.3f}%" * 3).format(
        r.condition, 100 * r.H_nodesign_RMSE_mu,
        100 * r.H_nodesign_RMSE_mu_ci_lo, 100 * r.H_nodesign_RMSE_mu_ci_hi,
        100 * sd, 100 * mde, 100 * r.design_support_cost_RMSE_mu,
        100 * r.design_support_cost_RMSE_mu_ci_lo, 100 * r.design_support_cost_RMSE_mu_ci_hi))

print()
print("max |H| over six conditions : %.4f%%" % (100 * u.H_nodesign_RMSE_mu.abs().max()))
print("max H upper CI bound        : %.4f%%" % (100 * u.H_nodesign_RMSE_mu_ci_hi.max()))
print("min support-cost CI lower   : %.4f%%" % (100 * u.design_support_cost_RMSE_mu_ci_lo.min()))
print("all |H| < band floor 0.30%%  :", bool((u.H_nodesign_RMSE_mu.abs() < 0.003).all()))
print("all go False                :", bool((~u.go).all()))
print("MDE range                   : %.3f%% - %.3f%%" % (
    100 * min((u.H_nodesign_RMSE_mu_ci_hi - u.H_nodesign_RMSE_mu).abs() * np.sqrt(u.n) / stats.t.ppf(0.975, u.n - 1) / np.sqrt(u.n)
              * (stats.t.ppf(0.975, u.n - 1) + stats.t.ppf(0.8, u.n - 1))),
    100 * max((u.H_nodesign_RMSE_mu_ci_hi - u.H_nodesign_RMSE_mu).abs() * np.sqrt(u.n) / stats.t.ppf(0.975, u.n - 1) / np.sqrt(u.n)
              * (stats.t.ppf(0.975, u.n - 1) + stats.t.ppf(0.8, u.n - 1)))))

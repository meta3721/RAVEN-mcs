# 1. Executive Verdict

DYNAMIC_COV_TOO_CONSERVATIVE

R1d is a 1-seed target-semantics + dynamic C_cov audit. Frozen `tau_*` were not changed. 5-seed was not started.

# 2. Target Semantics

Deployment population: public evaluation/deployment-supported atoms (test split, `support_flag`).
`μ_g` is frozen train-split TOD occupancy (manuscript). Atomic `ϖ_i = μ_{h(i)} / n_{I_dep,h(i)}`.
`π^{tar}` is the client×stratum pushforward of the same `ϖ` with frozen station→client `ξ`.
Test outcomes are not used. max compatibility error = 1.0547118733938987e-14 (atol=1e-10).

R1c vs R1d is a semantic comparison only (`TARGET_LAW_R1C_VS_R1D.csv`).

# 3. Dynamic Opportunity Model

Predictor: rolling mean of last L=8 completed window masses.
Bound: window max-residual conformal quantile, `δ=0.05`.
Features are F_{r-} only (see DYNAMIC_COV_FEATURE_AUDIT.md). Current R is not a Gate input.

# 4. Dynamic C_cov Calibration

SensorScope warmup n=84: pairwise=0.9999458874458875 mass=0.9999282357571128 joint=0.9761904761904762 mean C_cov=7.176424288723571e-05 status=DYNAMIC_COV_TOO_CONSERVATIVE
U-Air warmup n=64: pairwise=1.0 mass=1.0 joint=1.0 mean C_cov=0.0 status=DYNAMIC_COV_TOO_CONSERVATIVE

# 5. U-Air Re-Audit

Not run (dynamic C_cov did not pass calibration, or methods not started).
SensorScope Always-D vs No-D: n/a

# 6. Gate Diagnostic

SAG was not run.

# 7. A8b Status

not computed
A8B_NOT_FINAL_CLOSED

# 8. Scientific Interpretation

R1c pooled CP made both datasets Always-ON because it certified a static law, not P_r^{opp}.
R1d asks whether current-window support risk is predictable from F_{r-} under the frozen deployment population.
Old U-Air reversal is not treated as a verified fact under TARGET_LAW_RULE_V1.

# 9. Next Decision

Verdict DYNAMIC_COV_TOO_CONSERVATIVE. Do not auto-start 5-seed.

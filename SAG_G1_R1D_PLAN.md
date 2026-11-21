# SAG G1-R1d Plan

Authority: Spec v1.2 → PostAudit III–VI → this R1d instruction.
Frozen `tau_*` unchanged. No 5-seed. New writes: `outputs/sag_g1_r1d/`.

## R1d-A — freeze unique deployment target

Evidence uniquely supports a reconciliation of PostAudit `I_dep` and manuscript `μ`:

- Scientific population: public **evaluation/deployment** atoms (test split, `support_flag`, public covariates only).
- Group masses `μ_g`: frozen **train-split** TOD occupancy (TABLE I / Section III seal; no test labels).
- Atomic law on `I_dep`: `ϖ_i = μ_{h(i)} / |{j∈I_dep: h(j)=h(i)}|`.
- `π_{k,s}` from the same `ϖ` with frozen `ξ_{k|i}=1{client(spatial_id)=k}`.

Rejected:

- Candidate A (R1c train-uniform): makes target = training support by construction; contradicts PostAudit deployment population and test-side `R_μ`.
- Candidate C: no external SS/U-Air deployment measure exists.

Not selected by Gate ON/OFF or RMSE.

## R1d-B/C — current-window C_cov

Replace all-history pooled CP. Predictor: rolling mean of last `L=lookback_min` completed window masses. Bound: window **max-residual** conformal quantile of `R_t = max_{π^{tar}>0}(π̂_t − π^{realized}_t)` from strictly prior windows. Fail-closed if calibration history `< L`. Current R never enters Gate.

If post-warmup window-joint coverage `< 0.90` or coverage slides over time: `DYNAMIC_COV_NOT_CALIBRATED`, no SAG.

## R1d-E/F

Always-D vs No-D 1-seed only after calibration. If U-Air is no longer unsafe, do not force OFF; emit natural-block candidates / pre-registered stress plan. SAG 1-seed only if a legal safe/unsafe contrast exists.

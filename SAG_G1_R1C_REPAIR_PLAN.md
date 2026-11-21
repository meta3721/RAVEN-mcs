# SAG G1-R1c Coverage Certificate Repair Plan

Authority: Spec v1.2 → PostAudit III–VI → R1/R1b → this R1c instruction.
Frozen `tau_*` unchanged. Same paper `h(i)` map. No 5-seed. New writes: `outputs/sag_g1_r1c/`.

## R1c-A — target compatibility

**Confirmed source split (see `outputs/sag_g1_r1c/target/TARGET_SOURCE_AUDIT.md`)**

- Paper `μ`: `deployment_groups.build_paper_h_payload` → train-split uniform then `h(i)` marginal.
- Gate `π^{tar}`: `sag_runtime.prepare_sag_bundle` → `build_pi_target(..., split="test")`.
- These are two atomic laws. Mark `TARGET_COMPATIBILITY_BUG_CONFIRMED`, then fix.

**Fix:** one frozen train-split atomic law `varpi_i^{tar}` (public metadata only). Derive

- `μ_g = ∑_{i:h(i)=g} ϖ_i`
- `π_{k,s}^{tar} = ∑_{i:s(i)=s} ξ_{k|i} ϖ_i` with frozen `ξ_{k|i}=1{client(spatial_id)=k}`

Group bridge via `s →` atoms `→ h(i)` varpi weights. Require max abs error ≤ 1e-10. If unclosed: STOP (no 1-seed).

## R1c-B — freeze `π_safe` rule

No earlier frozen rule exists. Freeze R1/R1b q10 protocol as `PI_SAFE_RULE_V1`. Do not retune q from ON/OFF.

## R1c-C — event-count Clopper–Pearson LCB

Replace window-mass empirical-Bernstein (n≤32, mass≈0.125 → LCB=0) as the **main** C_cov certifier.

Use completed-window event counts `t<r` (all history, not 32 mass samples).
`lower_π_opp` = one-sided Clopper–Pearson on `x=C_{k,s}`, `n=C^{tot}` with Bonferroni `δ/m_{+}` (`δ=delta_cal=0.05`).
`C_cov` formula unchanged. Assumption: completed opportunity events are treated as exchangeable multinomial marks of the frozen event-mark law (EventTrace risk-set units). If that is untenable we would switch to block calibration; current sealed traces use fixed per-window event counts, so count-based CP is the preferred route.

## R1c-D / E

Recompute A8b 95% coverage/width (do not inflate). Then 1-seed SS/U-Air 30001 only. Then zip to `deliverables/`.

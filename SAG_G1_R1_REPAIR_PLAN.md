# SAG G1-R1 Certificate Repair Plan

Status: **implementation plan for R1-A–E only.**  
Authority: Spec v1.2 → PostAudit III–VI → `RAVEN_MCS_Cursor_SAG_G1_R1_Certificate_Repair_Instruction_v1.0.txt`.  
Frozen `tau_*` / `tau_safe=4.0` are not changed. No 5-seed / E1–E5 / T-Drive.

Do not overwrite `outputs/sag_g0/` or `outputs/sag_g1/`. New writes go to `outputs/sag_g1_r1/`.

---

## 0. Already-confirmed facts (do not “explain away”)

- G0 PASS; timing / B_r / A_r / EventTrace stay as-is.
- G1 ON = 0/900 because `C_cov` was current-window R-coverage (~0.018–0.028).
- `B_tot_UCB` is far above `tau_safe=4` even if `C_cov` is fixed.
- Formal coverage target is **95%** (`delta_cal=0.05`), not the old 0.90 floor.

---

## 1. R1-A — counterfactual metric source

**Files**

- `src/raven_mcs/sag/counterfactual_audit.py`
  - replace `_l1_half` as the Δ definition
  - add `metrics_from_raw_states()`
  - `audit_design_vs_nodesign()`: build real `M` (G×K compositions), reconstruct `V` from lagged `S²` and mode-specific `n_eff`, solve P2 for `α^D, α^0`
- `src/raven_mcs/training/window_runner.py`
  - pass `v_floor`, `mu`, lagged `debt`, per-client staleness, P2 lambdas into the audit
  - dump first 10 common-nonempty raw states on the diagnostic seed
- `tests/unit/test_counterfactual_metrics_independent.py` (Cases A–D)

**Current bugs (to confirm with synthetic tests + raw states)**

1. `service_diff = float(delta_m)` — **aliases service to Δ_M**. Spec: `s = Mα`, `service_diff_l1 = ||s^D−s^0||_1`.
2. `Δ_β` / `Δ_M` use `0.5‖·‖_1` on `β` and on the **mix vector** `Mβ`, not `‖β^D−β^0‖_2` and operator `‖M^D−M^0‖_2`.
3. `V` is the lagged `S²` vector, identical for D and 0 → `Δ_V ≡ 0`. PostAudit: `v_k = S²_{k,r-} / max(n_eff,1) + v_floor`.

If logged G1 metrics disagree with the recompute: **BUG_CONFIRMED**, old G1 certificate tables are void (files kept, not deleted).

---

## 2. R1-B — `C_cov` semantic repair

**Files**

- `src/raven_mcs/sag/certificates.py`
  - `C_cov_LCB = ∑_{k,s} π^tar(k,s) 1{lower_π_opp(k,s,r) ≥ π_safe}`
  - `lower_π_opp`: empirical-Bernstein LCB on **completed-window** pair masses only
- `src/raven_mcs/sag/sag_state.py` — store per-completed-window `opp_mass_by_pair` (not current R)
- `src/raven_mcs/training/window_runner.py` — after window close, record pair masses from that window’s R; Gate for window r uses only history `< r`
- `configs/sag_g1_r1/pi_safe_provenance.json` — **not** written into frozen `thresholds.json`
- tests: `test_c_cov_semantics.py`, `test_c_cov_target_mass.py`, `test_pi_safe_config.py`

**π_safe:** not in Spec/PostAudit/thresholds. Provisional = 10th percentile of **public** `π_opp_joint` on `{π^tar>0}` pairs. Mark `PI_SAFE_REQUIRES_FREEZE_DECISION`. Candidates q05/q10/q25 logged; ON rate is not a selection criterion.

---

## 3. R1-C — `B_tot` decomposition + legal `B_M`

**Files**

- `src/raven_mcs/sag/certificates.py`
  - full T3/T4 pieces: `D_α_UCB`, `B_srv = √|G|(Δ_M_UCB + B_M_pre D_α_UCB)`, `B_tot = B_srv + 2δ_A + 2δ_cal`
  - `B_Q = ‖Q_{r-}‖_2` (current debt at Gate time)
  - `B_M_pre = √K` with `K` = pre-window known client roster (dataset clients)
- `src/raven_mcs/training/window_runner.py` — log decomposition; post-window `B_M_cf = max(‖M^D‖_2,‖M^0‖_2)` **diagnostic only**
- tests: `test_Btot_decomposition.py`, `test_BM_predictability.py`

If no assertable client–group support mask: `NO_LEGAL_TIGHTER_BM_BOUND_FOUND` (do not use realized `|A_r|` or empirical percentiles).

---

## 4. R1-D — 95% coverage + width

**Files**

- `certificates.py`: conformal/order-statistic UCB `k = ceil((n+1)q)` instead of `np.quantile` (no arbitrary multiplier)
- `src/raven_mcs/experiments/run_sag_g1_r1.py`: `width = UCB − actual`; `actual=0` tallied separately; domain = `A^D=A^0≠∅` only
- tests: `test_certificate_coverage_domain.py`, `test_certificate_width.py`

---

## 5. R1-E — 1-seed diagnostic then STOP

**New** `src/raven_mcs/experiments/run_sag_g1_r1.py`  
Seeds: SensorScope 30001, U-Air 30001. Methods: Always-D / No-D / SAG. Same sealed EventTraces.

Outputs under `outputs/sag_g1_r1/` as specified in the R1 instruction §11.  
Verdict ∈ {READY_FOR_G1_R2_5SEED, NEEDS_MORE_CERTIFICATE_REPAIR, STRUCTURAL_CERTIFICATE_TOO_CONSERVATIVE, IMPLEMENTATION_BUG_FOUND}.  
Do **not** auto-start 5-seed.

---

## 6. Execution order

1. This plan.
2. R1-A + synthetic tests (must PASS before certificate rewrite is trusted).
3. C_cov + C_cov tests.
4. B_tot decomposition + legal B_M check.
5. 95% width logging.
6. All unit tests.
7. 1-seed diagnostic.
8. `R1_REPAIR_REPORT.md` and STOP.

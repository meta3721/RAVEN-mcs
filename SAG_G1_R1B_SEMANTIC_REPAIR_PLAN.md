# SAG G1-R1b Semantic Alignment Repair Plan

Status: implementation plan for R1b-A–C + 1-seed re-diagnostic only.  
Authority: Spec v1.2 → PostAudit III–VI → R1 instruction → R1b instruction.  
Frozen `tau_*` unchanged. No 5-seed / E1–E5 / T-Drive. Do not overwrite `outputs/sag_g0/`, `outputs/sag_g1/`, `outputs/sag_g1_r1/`.

## 0. Mapping decision (must precede any M/μ rewrite)

Paper / sealed manuscript semantics already unique-freeze SensorScope and U-Air `h(i)`:

- four UTC time-of-day groups H1:00–06, H2:06–12, H3:12–18, H4:18–24
- train-split mass, no test labels
- `h(i) ≠ s(i)`; forbidden to write `h(i)` as spatial × time

Code that produced `|G|=220/144` used E3 frozen **spatial×time** `target_group` (`n_groups_runtime`) with `use_coarse_time_groups=False`. That is **not** paper `h(i)`.

This is **not** `H_MAPPING_NOT_FROZEN`. R1b will implement the paper 4-block map via `RepeatableTimeOfDayMapper` on public `absolute_time`.

## 1. R1b-A — unified deployment-group space

**Files**

- `src/raven_mcs/sag/deployment_groups.py` (new freeze/load)
- `configs/deployment_group_map/SensorScope_h_map.json`
- `configs/deployment_group_map/UAir_h_map.json`
- `src/raven_mcs/data/window_dataset.py` — optional `h_by_unit` lookup
- `src/raven_mcs/training/window_runner.py` — `num_groups=4`, `mu` length 4, `M` columns from `h(i)`
- `src/raven_mcs/experiments/sag_runtime.py` — attach paper-h bundle; keep E3 pair/`s(i)` wiring
- tests: `test_group_mapping_consistency.py`, `test_group_mapping_frozen.py`

Do **not** change E3 `production_target_bundle` (spatial×time pair domain stays for `π^{tar}_{k,s}` / `s(i)`).

WorstGroupRMSE: G2/paper already uses the 4-block map. Old SAG G1 used fine `target_group`. R1b diagnostic WorstGroupRMSE / `Δ_group` / `RMSE_μ` weights switch to paper `h(i)` and this is reported.

## 2. R1b-B — opportunity-event mass

**Files**

- `src/raven_mcs/sag/certificates.py`
  - `window_opportunity_masses` = count/mass then normalize
  - isolate unique-pair uniform as `pair_presence_distribution` (not a Gate input)
- `window_runner._window_opp_mass_map` — pass all risk-set (k,s) events, not unique keys
- tests: `test_opportunity_event_mass.py`, `test_c_cov_no_current_R_leakage.py`, `test_c_cov_target_mass_weighted.py`

`π_safe`: reuse R1 provisional q10-on-public-`π_opp_joint` rule. Do not re-select from ON/OFF.

## 3. R1b-C — ΔV / ESS

Extend counterfactual raw state with per-client `zeta_std` / `n_eff_D` / `n_eff_0` on observed records. Write `ESS_VARIANCE_COUNTERFACTUAL_AUDIT.csv`. Repair V reconstruction only if `zeta_std>0` but `n_eff` is wrongly equal.

## 4. 1-seed

`python -m raven_mcs.experiments.run_sag_g1_r1b`  
SensorScope 30001, U-Air 30001, sealed EventTrace, methods Always-D / No-D / SAG. Then STOP.

# 1. Executive Verdict

STRUCTURAL_CERTIFICATE_TOO_CONSERVATIVE_CONFIRMED

R1b is a 1-seed semantic-alignment diagnostic (SensorScope 30001, U-Air 30001). Frozen `tau_*` were not changed. 5-seed was not started.

`h(i)` is now the paper 4-block UTC map. Opportunity mass is event-count mass. Counterfactual Δ metrics recompute. SensorScope still has **0 legal ON windows**. The remaining unique first-fail is **`C_cov_LCB`**, not `B_tot`.

# 2. Deployment-Group Mapping Audit

Paper `h(i)` is the application-level deployment group: four UTC time-of-day blocks H1:00–06, H2:06–12, H3:12–18, H4:18–24. `μ` is train-split supported atomic mass, no test labels. `s(i)` is the sealed opportunity stratum (`spatial_id × time block × weekday`) and is **not** `h(i)`.

| dataset | old `|G|` (E3 spatial×time runtime) | new `|G|` (paper `h(i)`) |
|---|---:|---:|
| SensorScope | 220 | **4** |
| U-Air | 144 | **4** |

220/144 appeared because G0/G1/R1 passed `n_groups_runtime` from the frozen spatial×time target artifact and `use_coarse_time_groups=False`. That encoding is the E3 pair-domain `target_group`, which the sealed manuscript **forbids** as SensorScope/U-Air `h(i)`.

R1b freezes `configs/deployment_group_map/SensorScope_h_map.json` and `UAir_h_map.json` via `RepeatableTimeOfDayMapper` on public `absolute_time`. Train/val/test share the same unit map. Labels and current-window data are not used.

`μ`, `M_r`, `ω_r=M_r α_r`, `Δ_group`, Theorem-4 `|G|`, and `B_srv=√|G|(…)` all use this 4-block space. R1b WorstGroupRMSE uses the same paper `h(i)` as G2. `Δ_{c-s}` remains on `s(i)`.

# 3. Opportunity-Event Mass Repair

Old R1 `window_opportunity_masses` unique-pair-uniformized completed-window pairs (`1/#unique_pairs`). That logic is now isolated as `pair_presence_distribution` and **does not enter C_cov**.

New code: `N^{opp}_{k,s,t}` = count of opportunity events (risk-set units) with `(k,s(i)=s)`; `π^{opp}=N/∑N` when `∑N>0`. Unit test: 20 vs 1 events → 20/21 vs 1/21, not 1/2.

On these sealed EventTraces every recorded pair has `N_opp=4` (regular risk-set size), so **this particular data** makes event-mass coincide with unique-pair uniform. That is a trace fact, not leftover unique-pair code. The implementation is still count-based.

Example SensorScope window 0, all pairs (8 pairs × 4 events):

| client | stratum | event count | π̂_opp window | π^tar |
|---|---|---:|---:|---:|
| client-000 | s93::block0::weekend | 4 | 0.125 | 0.00176 |
| client-001 | s106::block0::weekday | 4 | 0.125 | 0.00352 |
| client-002 | s36::block1::weekend | 4 | 0.125 | 0.00176 |
| client-003 | s33::block0::weekday | 4 | 0.125 | 0.00352 |
| client-004 | s94::block0::weekday | 4 | 0.125 | 0.00352 |
| client-005 | s25::block0::weekend | 4 | 0.125 | 0.00176 |
| client-006 | s19::block0::weekday | 4 | 0.125 | 0.00352 |
| client-007 | s84::block0::weekend | 4 | 0.125 | 0.00176 |

None of these window-0 pairs is certified (`lower_π_opp` history is empty / cold).

# 4. C_cov

`C_cov_LCB(r)=∑ π^tar(k,s) 1{lower_π_opp(k,s,r) ≥ π_safe}`. Input history is completed-window event-mass `π^opp`. Current R is not passed into `compute_certificates`.

`π_safe` reuses the R1 provisional rule (q10 of public `π_opp_joint` on `{π^tar>0}`). Not reselected from ON/OFF. Status: **PROVISIONAL_REQUIRES_LATER_FREEZE**. SensorScope 6.33e-4; U-Air 1.39e-3.

Pass rate: SensorScope **0**; U-Air **0**. Recorded first-fail after cold start remains `OFF_LOW_COVERAGE`.

# 5. ESS / Delta_V Audit

`within_client_zeta_std = 0` on **all** dumped observed records (fraction 1.0). Design is a common multiplicative factor on the client/window, not a within-client reweighting of records.

`n_eff_D = n_eff_0` on 92% of ESS rows. The other 8% are U-Air rows with `ζ^D ≡ 0` on the observed records, so Design mass and `n_eff_D` collapse to 0 while No-Design `n_eff_0` equals the observation count. That is the ζ=0 mechanism, not an unexplained Hajek bug.

`ΔV ≈ 0` on logged common-nonempty windows follows from equal `n_eff` when ζ is a positive common factor, plus lagged `S²` shared across modes. Raw-state recompute matches the new logs.

# 6. B_tot Recalculation

Formula unchanged. `|G|` is now 4, so `√|G|` is 2 instead of ≈14.8.

| piece | SS median | SS p95 | U-Air median | U-Air p95 |
|---|---:|---:|---:|---:|
| Δβ_UCB | 0.415 | 0.661 | 0.474 | 0.577 |
| ΔM_UCB | 0 | 0 | 0 | 0 |
| ΔV_UCB | ~0 | ~0 | ~0 | ~0 |
| B_srv | 2.35 | 3.74 | 2.68 | 3.26 |
| 2 δ_A | 0.063 | 0.34 | 1.48 | 2.00 |
| 2 δ_cal | 0.10 | 0.10 | 0.10 | 0.10 |
| B_tot | **2.51** | **3.90** | **4.26** | 5.36 |

Old vs new SensorScope `B_tot` median: **17.55 → 2.51**. Old pass rate 0; new pass rate 1.0 on windows with a finite bound (gate table 0.92 includes 8 cold-start fails). U-Air `B_tot` still often exceeds `τ_safe=4` because `2δ_A` is large; `δ_A` already blocks U-Air independently.

# 7. Gate Re-Diagnostic

Frozen: `τ_cov=0.05`, `τ_ret=0.05`, `τ_ESS=1`, `τ_clip=0.95`, `τ_A=0.35`, `τ_safe=4`.

## SensorScope 30001 (100 windows)

| certificate | pass rate |
|---|---:|
| C_cov | **0.00** |
| C_ret | 0.92 |
| C_ESS | 0.92 |
| C_clip | 0.92 |
| δ_A | 0.92 |
| B_tot | 0.92 |
| ALL | **0.00** |

ON = **0 / 100**. First-fail: 8 `OFF_COLD_START`, 92 `OFF_LOW_COVERAGE`. All-fail: C_cov fails every window; other certificates fail only the 8 cold-start windows.

## U-Air 30001 (80 windows)

| certificate | pass rate |
|---|---:|
| C_cov | **0.00** |
| C_ret | 0.90 |
| C_ESS | 0.90 |
| C_clip | 0.90 |
| δ_A | **0.00** |
| B_tot | 0.125 |
| ALL | **0.00** |

ON = **0 / 80**. First-fail: 8 cold start, 72 `OFF_LOW_COVERAGE`. All-fail: C_cov 80, δ_A 80, B_tot 70. Support-unsafe U-Air is still separated by `δ_A`.

SAG ≡ No-Design on RMSE / WorstGroup / Δ (ON rate 0). Always-D still uses `G=1` every window.

# 8. Scientific Boundary

SensorScope compatible regime: **no legal ON window** after aligning `h(i)` and event-mass `C_cov`. `B_tot` is no longer the SensorScope blocker. `δ_A` still passes after cold start.

U-Air support-unsafe regime: `δ_A_UCB` pass rate 0, so the active-set certificate still closes unsafe windows even if coverage were later to pass.

# 9. Next Decision

Do **not** start 5-seed G1-R2.

The R1 hypothesis “`B_tot` stays ≫ `τ_safe=4` after a legal `|G|`” is **false on SensorScope**. After paper `h(i)` (`|G|=4`), SensorScope `B_tot` median 2.51 < 4.

Unique remaining blocker at frozen thresholds: **`C_cov_LCB=0`**. Pair-level empirical-Bernstein LCBs on lagged opportunity masses still do not certify `π^tar` mass ≥ `τ_cov=0.05`. That is not a group-mapping bug and not unique-pair uniformization.

`π_safe` still requires an explicit freeze. Do not lower `τ_cov` / `τ_safe` / `τ_A` to manufacture ON.

# SAG G0/G1 Report

# 1. Executive Verdict
REPAIR

G0 implementation audit passed. G1 5-seed shows SAG is **identically No-Design** (Gate never ON). Certificates are too conservative on the current `C_cov` operationalization. Do **not** expand to 10 seeds, E1–E5, or T-Drive.

# 2. G0 Implementation Audit
G0 full verdict: **PASS** (SensorScope + U-Air, seeds 30001–30003, sealed E3 EventTraces).

| Check | Result |
|---|---|
| timing correct? | PASS |
| p_obs frozen before O? | PASS |
| q_use frozen before U? | PASS |
| B_r / A_r correct? | PASS |
| shared EventTrace? | PASS |
| no dataset-name Gate? | PASS |
| no forbidden Gate feature? | PASS |
| counterfactual audit valid? | PASS |
| No-Design ζ̃=1 with IPW/P2/V/staleness/Debt on? | PASS |

Smoke archive: `outputs/sag_g0/logs/smoke_pass/`.

# 3. Gate Behavior

SAG mean ON rate: **0.000** (900 SAG windows; 0 ON).

SAG fallback counts (G1 window log):

| dataset | OFF_COLD_START | OFF_LOW_COVERAGE | ON |
|---|---:|---:|---:|
| SensorScope | 40 | 460 | 0 |
| U-Air | 40 | 360 | 0 |

Always-Design false-enable (oracle-unsafe = `active_set_mismatch==1` among G=1 windows):

- SensorScope: **0.00** (Always-D mismatch rate 0)
- U-Air: **0.46–0.59** (Always-D mismatch ≈ 0.46–0.59)

SAG false-enable: **0.00** because it never enables. That is safety-by-never-ON, not a useful Gate.

Comparison A (Always-D vs No-D) **reproduces the old boundary**: SensorScope Design is structurally a bit better and prediction-similar; U-Air Always-D raises RMSE and WorstGroupRMSE and damages the active set. Negative U-Air Design result is retained.

# 4. Certificate Calibration

Joint coverage of (Δβ, ΔM, ΔV) on common nonempty A^D=A^0, using F_{r-} 95% rolling quantiles:

- SensorScope seeds: 0.89–0.94
- U-Air seeds: 0.76–0.97 (seed 30003 = 0.76)

Mean joint coverage is below the 0.90 development floor used in the G1 verdict script (target remains 95% before unseen test). Bound widths were not logged (NaN) because UCB fields were read from `gate_features` after flatten in some rows; coverage indicators themselves were computed from raw logs.

Dominant OFF cause is **not** B_tot: it is `C_cov_LCB < τ_cov`. Current realized `C_cov` is “fraction of all π^tar>0 client–stratum pairs that appear in this window’s R”. That is far below 0.05 in almost every window, so the Gate stays fail-closed after cold start.

This is a certificate-definition / calibration REPAIR, not a threshold hack. Do not lower τ_cov just to force ON.

# 5. Prediction Safety

SAG ≡ No-Design on every seed (bit-identical RMSE / WorstGroupRMSE).

- mean relative RMSE harm vs No-D: **0.000** (budget 0.5%)
- mean relative WorstGroup harm vs No-D: **0.000**

Prediction no-harm holds only because SAG never used Design.

# 6. Structural Utility

- mean `gain_group` (No-D − SAG) = **0**
- mean `gain_cs` = **0**
- `NAG_NOT_AVAILABLE_IN_G1` (no legal feasible oracle in this pass)

On SensorScope, Always-D has a small structural edge vs No-D (e.g. seed 30001 Δ_group 0.998 vs 1.006). SAG did not capture it.

# 7. Failure Analysis

1. **Almost-always OFF.** After 8-window cold start, every remaining window is `OFF_LOW_COVERAGE`.
2. **U-Air is the mismatch environment.** Always-D active-set mismatch ≈ 50%. SAG avoided those windows by never turning ON, including on SensorScope-compatible windows.
3. **C_cov is over-strict as implemented.** Window-level hit rate of the full target support is not a usable positivity LCB. Repair should use a lagged opportunity-probability LCB on S_tar, not “did every target pair appear this window?”
4. Joint Δ coverage is close to 90% on SensorScope and unstable on U-Air; quantile UCBs need a held-out calibration pass before any unseen test.
5. P2 CLARABEL inaccuracy warnings occurred (same as E3); they did not fail G0.

# 8. Go/Repair/Stop Decision

| Gate | Result | Note |
|---|---|---|
| Gate-1 Predictability | PASS | G0 full PASS |
| Gate-2 Certificate | FAIL | joint coverage < 0.90; C_cov unusable |
| Gate-3 Safety | PASS | SAG false-enable < Always-D (0 vs 0.26 mean) |
| Gate-4 Prediction | PASS | harm 0.0 vs No-D |
| Gate-5 Utility | FAIL | ON rate 0; structural gain 0; degenerates to Always-No-Design |

**Decision: REPAIR**

Do not retune τ after seeing G1. Next work (only if you confirm): repair `C_cov` to an F_{r-}-measurable opportunity-probability LCB on S_tar, freeze one coverage target, then rerun G0 smoke/full + G1 5-seed. Do not start 10-seed or E1–E5.

# 9. Files Produced

G0:

- `outputs/sag_g0/G0_IMPLEMENTATION_AUDIT.md`
- `outputs/sag_g0/G0_ASSERTION_SUMMARY.json`
- `outputs/sag_g0/G0_WINDOW_TRACE.csv`
- `outputs/sag_g0/G0_GATE_FEATURE_AUDIT.csv`
- `outputs/sag_g0/G0_EVENTTRACE_HASH_CHECK.csv`
- `outputs/sag_g0/G0_B_A_SET_AUDIT.csv`
- `outputs/sag_g0/G0_COUNTERFACTUAL_AUDIT.csv`
- `outputs/sag_g0/configs/`
- `outputs/sag_g0/logs/smoke_pass/`

G1:

- `outputs/sag_g1/SAG_G0_G1_REPORT.md`
- `outputs/sag_g1/G1_VERDICT.json`
- `outputs/sag_g1/G1_METHOD_SUMMARY.csv`
- `outputs/sag_g1/G1_GATE_WINDOW_LOG.csv`
- `outputs/sag_g1/G1_CERTIFICATE_COVERAGE.csv`
- `outputs/sag_g1/G1_PREDICTION_SAFETY.csv`
- `outputs/sag_g1/G1_STRUCTURAL_GAIN.csv`
- `outputs/sag_g1/configs/config_g1_5seed.json`

# Executable instruction: A1 (gatekeeping + non-inferiority) and C1 (City Scanner deletion mechanism)

```text
Mode: design + one execution prompt. This file starts no run.
Contract: CCFA-Skills/ccf-experiment-designer. Protocol, not publication prose.
Inputs: results_c1_cityscanner/round_v1/ (frozen CS runs, CS_TRAIN_SETUP.json, CS_PHI_DECISION.json),
        results_nodesign_supplement/round_v1/ (CS raven_wo_design), results_exogenous_target/round_v1/ (MAPS_KEY_LEVEL.csv),
        results_w1_ladder/round_v4/ + round_v5/ (SS/U-Air Part B, θ-canonical rule), scripts/run_nodesign_supplement.py (CS driver).
Output: results_gatekeeping/round_v1/ only.
Part A (A1 descriptive) is read-only. Part B (C1 training) needs the phrase "授权 C1 训练". Part C (SS/U-Air confirmatory) is not in this round.
Forbidden: editing src/, the manuscript, any existing results directory, tdrive_protocol_seal_r1/, artifacts/;
           X1; PATH_A NO2; full build(); git commit/push; choosing maps, margins, seeds or contrasts after seeing any C1 RMSE.
```

## 0 Why this design (facts read on 2026-10-03, CS frozen + Design-off runs, 10 seeds)

| contrast (RMSE_μ, relative) | mean | median | SD | seeds where the first arm is lower |
|---|---|---|---|---|
| `raven − fedavg_window` | +5.59 % | **+0.27 %** | 13.4 % | 5/10 |
| `raven − raven_wo_design` | +2.45 % | **−0.22 %** | 13.0 % | 7/10 |

- The "+5.6 % Design cost" on City Scanner is mostly **one seed**: seed 32005 has `raven` 0.4092 vs `fedavg_window` 0.2938 (+39 %).
- `Δ_group` drops from 0.148–0.244 (FedAvg) to 0.045–0.121 (RAVEN) on every seed. The structural gain is large and uniform across seeds.
- The training-time map is `build_pi_target(split="test")` at key level (1164 keys). Its zero-mass keys remove **14.35 %** of delivered units. The exogenous maps M1/M2 would remove about 1 %.
- Only 10 CS event traces exist and no trace generator is in the repo. Replicates can therefore only be added as **model seeds on fixed traces**, and inference must cluster by trace.

What follows from this:
- The CS question is mechanistic: is the prediction cost caused by deleting delivered units, and is it a single-trace event?
- An n = 10 mean test cannot answer it. The design uses a matched no-deletion arm, robust estimators, and replicate model seeds.
- A1 supplies the inferential frame: structure first, prediction as non-inferiority.

## 1 Part A — A1 gatekeeping, descriptive on existing data (read-only)

### A1.0 The hierarchy (written into PREREG.md before anything else; it is also the confirmatory rule for Part B)

Use one chain per (dataset, method-arm) against `fedavg_window`, with a fixed sequence at the full α = 0.05:
- **H1 (structure):** Δ_group(arm) < Δ_group(fedavg_window), tested with a paired Wilcoxon.
- **H2 (prediction, non-inferiority):** RMSE_μ(arm)/RMSE_μ(fedavg_window) − 1 < δ.
  - Decision statistic: the Hodges–Lehmann estimate of the paired relative difference and the upper bound of its one-sided 95 % CI (Wilcoxon-inverted, or the trace-cluster bootstrap in Part B).
- **H3 (prediction, superiority):** the same CI excludes 0 from below. H3 is only tested if H2 passes.

Each later hypothesis is tested only if the previous one is rejected. Across chains within one dataset, use Holm (graphical Bretz–Maurer–Brannath–Posch form: chain weights equal; α propagates to the remaining chains once a chain is completed). Datasets are not pooled.

Margins:
- δ = 0.5 % for SensorScope and U-Air (unchanged from v5).
- δ_CS = 2 %. It is declared now, and its power is reported in A1.2. Justification: the CS paired SD is 13 %, so with n = 10 a 0.5 % margin is untestable. The margin must be set before C1, and it is not revisited.

### A1.1 Descriptive application (post hoc, labelled as such)

Apply the hierarchy to the existing data. Arms are `raven` and `proj_beta` (SS/U-Air) and `raven` (CS). Use θ-canonical U-Air values (round_v5.1 rule) and 20 seeds; CS has 10 seeds.

Output `A1_DESCRIPTIVE.csv`: `ds, arm, H1_p, H1_reject, H2_hl, H2_ub95, H2_reject, H3_reject, power_H2_at_delta, label = "post hoc descriptive"`.

These rows **must never be cited as confirmatory**. They show what the frame reads on data that already exist.

### A1.2 Power table

For each dataset, use the observed paired SD to compute the power of H2 at δ (and at δ_CS for CS) with the n actually available. For CS, also compute it with n = 10 traces × r model seeds, r ∈ {1, 3, 5}, under the trace-cluster bootstrap, with the within-trace variance estimated from Part B's B0 step.

The table states plainly whether CS H2 is testable at all.

## 2 Part B — C1: the City Scanner deletion mechanism (training, gated)

### B0 Reproduction and variance probe

- **B0-a (driver reproduction).** Build a new driver `scripts/c1_deletion_driver.py`. It imports `build_setup` and `train_one` from `scripts/run_nodesign_supplement.py` and only replaces `setup["pi_target"]` per arm. It must reproduce frozen `raven` seed 32001 bit-exactly (RMSE_μ, WorstGroupRMSE, Δ_group, Δ_c-s ≤ 1e-12) and `raven_wo_design` seed 32001 from `results_nodesign_supplement`. A failure stops everything.
- **B0-b (seed-32005 probe).** On trace 32005 only, train `raven` and `raven_wo_design` with model seeds {32005 (original), 132005, 232005, 332005, 432005}.
  - Report whether the +39 % reproduces across model seeds (trace-driven) or appears only at the original model seed (training instability).
  - This is a diagnostic, not an endpoint, and it does not change any later rule.

### B1 Arms (all at the frozen μ = test region share, same s_max, windows and λ as the frozen CS runs)

| arm | key-level π^tar used for ζ | deleted delivered share (expected) | what it isolates |
|---|---|---|---|
| `fedavg_window` | — | 0 | comparator (frozen; reused) |
| `raven_wo_design` | ζ ≡ 1 | 0 | no tilt, no deletion (reused) |
| `raven_ctrl` | control `build_pi_target(test)` | 14.35 % | frozen RAVEN (reused) |
| **`raven_ctrl_floor`** | control map, every zero key set to π_floor = the smallest positive control key mass, renormalized | 0 | **same tilt, no deletion**: the mechanism arm |
| **`raven_M1mu`** | M1 (ACS) rescaled within region so its region marginals equal μ | ≈ 1.0 % | exogenous support, same region target |
| **`raven_M2mu`** | M2 (311) rescaled the same way | ≈ 1.0 % | same, temporal shape |

Rules for the maps:
- Region-matching (`*mu`) keeps μ, P2 and the debt target identical across arms. Only within-region shape and support change.
- The maps are built from `MAPS_KEY_LEVEL.csv`.
- The driver must cover every risk-set key; a missing key is a hard error, not a zero.
- Log per arm: the realized deleted share ρ per seed (delivered units with ζ = 0, recomputed from the trace exactly as `exogenous_target_cityscanner.py` does), the key count, and the map sha256.

Replicates: 10 traces (32001–32010) × r model seeds.
- r = 1 uses the original model seed, which makes the reused arms valid.
- If the user authorizes more, set r = 3 with model seeds {s, s+100000, s+200000}; the reused arms then also need the extra model seeds.
- r is fixed in PREREG before B1 starts and cannot be raised afterwards.

New runs: 3 arms × 10 × r (+ 2 reused arms × 10 × (r − 1)). At r = 1 that is 30 runs, about 40 s each (≈ 20 min). At r = 3 it is 130 runs (≈ 1.5 h).

### B2 Endpoints and hypotheses (preregistered; one primary)

**Primary (mechanism):** H_mech: RMSE_μ(`raven_ctrl`) > RMSE_μ(`raven_ctrl_floor`).
- Estimand: Hodges–Lehmann paired relative difference, with a trace-cluster bootstrap CI (10 000 resamples, seed 20261003) and a two-sided Wilcoxon on trace-level means.
- Single primary test, so no multiplicity adjustment.
- Reading:
  - CI above 0: deletion causes a prediction cost.
  - CI inside ±δ_CS: no detectable deletion cost.
  - Otherwise: inconclusive.

**Structural guardrail (must be reported next to the primary):** Δ_group and Δ_c-s of `raven_ctrl_floor` vs `raven_ctrl`. If removing deletion also removes most of the structural gain, report it as a trade-off, measured as the share of the FedAvg→RAVEN Δ_group gain retained.

**Secondary (Holm within this family):**
- `raven_M1mu − raven_ctrl`
- `raven_M2mu − raven_ctrl`
- `raven_ctrl_floor − raven_wo_design` (the cost of the tilt alone)
- dose-response: per-(arm, trace) RMSE_μ vs. realized ρ, trace-cluster bootstrap slope

**Confirmatory A1 chains on the new arms:** run the hierarchy H1 → H2 (δ_CS) → H3 for `raven_ctrl_floor`, `raven_M1mu` and `raven_M2mu` vs. `fedavg_window`, using the graphical α split of A1.0. These are the only confirmatory prediction statements this round can produce.

Also report: WorstGroupRMSE and the per-region RMSE (R0–R3) for every arm, the per-seed table with seed 32005 marked, and every estimate recomputed without trace 32005. The exclusion analysis is a declared sensitivity analysis, never the primary.

### B3 Decision rules (written before B1)

| outcome | what may be written later (paper paused) |
|---|---|
| H_mech CI > 0 and the floor retains ≥ 50 % of the Δ_group gain | "On City Scanner the prediction cost is caused by deleting delivered units whose keys carry no evaluation-derived mass; a floored map keeps X % of the structural gain without that cost." |
| H_mech inside ±δ_CS | "Deleting 14 % of delivered units has no detectable prediction cost at n = …; the Design cost reported earlier is not a deletion effect." The seed-32005 probe then decides how that row is described. |
| H_mech inconclusive | Report the CI and power. No mechanism claim. Do not add traces or model seeds. |
| B0-b shows the +39 % only at the original model seed | That seed's contribution is described as a training-instability outlier, with the probe as evidence; the primary is still computed on all traces. |

## 3 Part C (not this round) — SS/U-Air confirmatory A1

The A1 chains can only become confirmatory on SS/U-Air with new, independent replicates. No new event traces exist and no generator is in the repo. Model-seed replicates on the existing 20 traces are the only option, and they inherit the same traces as the descriptive analysis, so they are not independent of it.

This is flagged here and **not designed further until the user decides** whether a trace generator should be rebuilt.

## 4 Outputs

`PREREG.md` (+ sha256 in `MANIFEST.sha256` before any computation), `A1_DESCRIPTIVE.csv`, `A1_POWER.csv`, `B0_REPRO.json`, `B0_SEED32005_PROBE.csv`, `C1_MAPS.json` (map hashes, key counts, π_floor, realized ρ per arm × trace), `C1_RUNS.csv` (per run), `C1_PRIMARY.json`, `C1_SECONDARY.csv`, `C1_A1_CHAINS.csv`, `C1_SENSITIVITY_NO32005.csv`, `EXECUTION_REPORT.md`, `ERRATA_FOR_PAPER.md` (items only; no manuscript edits).

## 5 Result templates (placeholders only)

`C1_RUNS.csv`: `arm, trace_seed, model_seed, rho_realized, RMSE_mu, WorstGroupRMSE, WG_R0..R3, Delta_group, Delta_c_s, runtime_s, map_sha256`

`C1_PRIMARY.json`: `{hl_rel_diff, ci95_lo, ci95_hi, wilcoxon_p, n_traces, r, reading, dgroup_gain_retained_share}`

`C1_A1_CHAINS.csv`: `arm, H1_p, H1_reject, H2_hl, H2_ub95, delta_CS, H2_reject, H3_reject, alpha_allocated`

No-fabrication status: all cells TBD. The only numbers above are the §0 readings of frozen artefacts.

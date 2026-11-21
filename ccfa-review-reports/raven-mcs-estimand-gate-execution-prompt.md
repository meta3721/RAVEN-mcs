# Executable instruction: (I) does arrival-weighted validation pick the wrong model? (II) does ρ predict the cost of Design?

```text
Mode: design + execution prompt.
Contract: CCFA-Skills/ccf-experiment-designer. Protocol, not publication prose.
Why this round exists: E1 (raven-mcs-tmc-review.md L107, L218) asks for one pre-registered
endpoint whose headroom exceeds its detectable effect AND a decision quantity whose base rate
is not saturated. results_evidence_axis/round_v1 shows that the aggregation weights cannot
supply that on SensorScope or U-Air: 51.4 % / 69.0 % of active windows have |A_r| ≤ 2, so
under α_max = 0.5 the weights are fixed by the constraint, and within a fixed active set oracle
weights move RMSE_μ by −0.27 % / −0.22 %. This round therefore changes the claim, not the
method:
  Part I  — the estimand matters for a decision a deployer actually makes (model selection),
            measured on stored checkpoints;
  Part II — the cost of the alignment factor (Design) is predicted, before training, by the
            structural statistic ρ, measured by a dose of ρ.
Neither part claims that alignment improves prediction.
Outputs: results_estimand_selection/round_v1/ (Part I), results_gate_dose/round_v2/ (Part II).
Drivers: new scripts/estimand_selection.py; scripts/gate_dose.py extended with a round_v2
         entry point (round_v1 code path and outputs unchanged). Do not edit src/.
Forbidden: editing src/, the manuscript, artifacts/, results_gate_dose/round_v1/, any other
           existing results_* directory; changing the method set, seeds, masks, endpoints,
           estimators, bootstrap seed, thresholds or decision rules after any Part I number or
           any Part II training run exists; pooling datasets for a decision; git commit/push.
Part I needs no training and runs on the request "执行第一部分".
Part II training starts only after the user writes "授权门控剂量". Its gate (II-§3) is part of
that authorization; if the gate fails, nothing else in Part II runs.
```

## 0 What is already measured (read from the named files)

- Within a fixed active set, oracle reweighting moves U-Air `RMSE_μ` by −0.27 % [−0.80, +0.26] (narrow support) and −0.22 % [−0.72, +0.28] (wide support), 20 seeds (`results_h_headroom/round_v3`).
- Active windows with `|A_r| ≤ 2` in frozen `raven`, seeds 30001–30020: SensorScope 51.4 % of 1877, U-Air 69.0 % of 1402 (measured 2026-10-07 from `window_metrics.json`).
- Per-group error heterogeneity on frozen checkpoints: single-group-weighted `RMSE_μ` relative to target-weighted is −12.1 % … +12.1 % (SensorScope), −71.5 % … +45.6 % (U-Air) (`.rb_work/evidence_headroom/HEADROOM.csv`).
- Four-block `TV(π^opp, μ)`: SensorScope 0.192, U-Air 0.278, T-Drive 0.142 (`main.tex` L1688–1689). The manuscript's RQ1 test of risk non-interchangeability is on NSW-Traffic and "is not a method-ranking test" (L1682).
- Design removal on U-Air: `RMSE_μ` −6.885 %, `Δ_group` −6.943 %, `Δ_c-s` +4.990 % (`tab:e4_ablation`). On SensorScope the Design-on/off gap in `RMSE_μ` is +0.005 % (`CONCENTRATION_COUNTERFACTUAL.csv`, C = 0).
- Gate input: SensorScope `ρ = 0`, U-Air `ρ = 0.35443037974683544` (train-atom frame, `results_gate_dose/round_v1/RHO.csv`).
- `raven_wo_design` reproduces its frozen artifacts bit-exactly in the current tree. Frozen `raven` does not: `|ΔRMSE_μ|` 4.20e-7 (SensorScope) and 3.78e-10 (U-Air), and `|Δθ|` 3.09e-7 / 1.49e-8. The cause is runner drift since `b01db69` (22 files changed, including the P2 CVXPY path). Within one environment, two runs are bit-identical (`results_gate_dose/round_v1/P0_REPORT.md` §5).
- Frozen-θ replay reproduces `RMSE_μ` and `Tail_RMSE` exactly on runs whose last window is active. Three runs have an inactive last window: `uair/raven` 30007, 30016, 30018 (`P0_REPORT.md` §4).

---

# Part I — arrival-weighted validation versus deployment-target selection

## I-1 Question

A deployer who validates on arriving data scores each candidate model with the arrival-weighted risk. The deployment risk is target-weighted. Does choosing by the first lead to a measurably worse choice under the second, and how often?

## I-2 Locked inputs

**Datasets.** SensorScope and U-Air, seeds 30001–30020. NSW-Traffic is descriptive only, and only if the P0 inventory finds all of the following for every method and seed: a group target, checkpoints and EventTraces. It never enters a decision.

**Candidate set M (9 deployable configurations), fixed now.**
- From `artifacts/e3_formal_runs_r1/runs/<ds>/<m>/seed<seed>/checkpoints/final.pt`: `fedavg_window`, `fedasync_window`, `flamf_timealign_adapted`, `local_hajek`, `twostage_hajek`, `inst_cal`, `debt_cal`, `raven`.
- From `artifacts/e4_core_mechanism_ablation_r1/runs/<ds>/raven_wo_design/seed<seed>/checkpoints/final.pt`: `raven_wo_design`.
- Excluded, because they are not deployable federated configurations: `raven_simoracle`, `central_all`, `central_delivered`.

A missing checkpoint makes the run `INCOMPLETE`. It is not replaced.

**Per-group test error.** For each (dataset, method, seed), load the checkpoint into the production runner, predict the frozen test split, and compute `MSE_g` for every target group `g`. Use the same group index as the frozen `μ`, and the same construction as `.rb_work/evidence_headroom.py`.

Reproduction check: `sqrt(Σ_g μ_g MSE_g)` must equal the stored `final_metrics.json` `RMSE_mu` to ≤ 1e-8 relative. This applies to every run whose last window is active. For a run whose last window is inactive, the checkpoint score is canonical: score it from the checkpoint and list it in `THETA_SCORED.csv`. Any other miss stops Part I.

**Two weight vectors over groups.**
- `μ`: the frozen deployment target, read from the run's target bundle.
- `π_arr`, per (dataset, seed): the group share of delivered `U = 1` risk units on non-test splits of the frozen EventTrace `artifacts/e3_formal_runs_r1/eventtraces/<ds>/seed<seed>/`. Units map to groups by the same unit→group map as the test split. This is the weighting under which a validation set drawn from arrivals estimates risk, assuming the error is stationary within each group.
- Sensitivity variant `π_arr^R`: the same, over all `R = 1` opportunity units regardless of `U`.

Write `WEIGHTS.csv` before any score is computed. It holds `μ`, `π_arr` and `π_arr^R` per dataset and seed, and `TV(π_arr, μ)` and `‖π_arr − μ‖₁` at group level.

## I-3 Endpoints (fixed now)

For each (dataset, seed, method):

```text
R_μ   = sqrt(Σ_g μ_g     MSE_g)        deployment-target risk (the paper's RMSE_μ)
R_arr = sqrt(Σ_g π_arr,g MSE_g)        arrival-weighted validation risk
b     = (R_arr − R_μ) / R_μ            misreport
```

Per (dataset, seed), the selection decision:

```text
m_arr = argmin_{m∈M} R_arr(m)          what arrival validation picks
m_μ   = argmin_{m∈M} R_μ(m)            what the deployment target would pick
d     = 1[m_arr ≠ m_μ]                 disagreement
reg   = (R_μ(m_arr) − R_μ(m_μ)) / R_μ(m_μ)    selection regret, ≥ 0
τ     = Kendall τ between the R_arr and R_μ rankings of M
```

Ties in `argmin` are broken by the order of M as listed in I-2. That order is fixed now.

## I-4 Hypotheses and labels (per dataset, never pooled)

**I-H1 (primary, decision).** The interval is a seed bootstrap: resample the 20 seeds, 10 000 draws, `numpy.random.default_rng(20261007)`, percentile 95 %. Margin `δ = 0.5 %`, the margin of II-H2.

| label | condition |
|---|---|
| `open` | CI lower bound of mean `reg` > `δ` |
| `null` | CI upper bound of mean `reg` < `δ` |
| `inconclusive` | otherwise |

**Base-rate condition (E1).** Report the disagreement rate `d̄` with a Wilson 95 % interval.
- If `d̄ = 0` or `d̄ = 1`, I-H1 is labelled `saturated` regardless of `reg`.
- If `0 < d̄ < 1`, the decision base rate is non-degenerate, and that fact is recorded next to the label.

**Descriptive, no decision.**
- Per method: mean `b` with Student-t 95 % interval.
- Pairwise sign-flip rate: the share of (method pair, seed) for which `sign(ΔR_arr) ≠ sign(ΔR_μ)`, overall and restricted to pairs with `|ΔR_μ| > δ`.
- Median `τ`.
- Which method `m_arr` and `m_μ` pick, as a count table.
- All of the above under `π_arr^R`.
- All of the above with `raven_wo_design` removed from M.

**Detectable effect.** Report the paired MDE (80 % power, two-sided 5 %, n = 20) of `reg` from its seed standard deviation. Report it next to `δ`, so the E1 headroom statement can be read directly: headroom is mean `reg`, and the detectable size is the MDE.

## I-5 What Part I licenses

- **`open` on a dataset.** The paper may state, on that block, that selecting a model by arrival-weighted validation costs `reg` (with CI) on the deployment-target risk, and that it disagrees with target-weighted selection in `d̄` of seeds. That is an empirical consequence of the non-interchangeability already proved. It is a statement about the estimand, not about RAVEN's weights.
- **`null`.** Arrival-weighted validation is a usable proxy for selection on that block, at margin δ. This goes into limitations, next to RQ1.
- **`saturated` or `inconclusive`.** Reported as measured. Nothing is added to the claims.

## I-6 Part I outputs

`results_estimand_selection/round_v1/`:
- `INVENTORY.json`: the method × seed checkpoint table and the NSW-Traffic eligibility verdict.
- `WEIGHTS.csv`.
- `tables/RISK_ROWS.csv`: one row per (dataset, method, seed), with `R_μ`, `R_arr`, `R_arr^R`, `b`, `theta_scored` and the stored `RMSE_mu`.
- `tables/SELECTION.csv`: one row per (dataset, seed), with `m_arr`, `m_μ`, `d`, `reg` and `τ`, under both arrival variants.
- `tables/SELECTION_SUMMARY.csv` and `SELECTION_DECISION.json`: the labels, `d̄` with its interval, the MDE and `δ`.

---

# Part II — dose of ρ against the cost of Design (gate law), with a same-tree reference

## II-1 What changes from `raven-mcs-gate-dose-execution-prompt.md` (round_v1)

Round v1 stopped after P0 and has no result. Round v2 keeps every v1 rule except the three listed here.

1. **Reference at m = 0.**
   - `raven`: the `m = 0` cells are fresh runs in the current tree (20 seeds × 2 datasets), not the stored artifacts. Every `raven` cell then comes from one code version. The stored `raven` artifacts appear only in the drift check of II-3.
   - `raven_wo_design`: the `m = 0` cells are the stored artifacts, after the II-3 bit-exact check.
2. **A decision endpoint (II-H3)** is added, because E1 also requires a non-saturated decision quantity.
3. **Output** goes to `results_gate_dose/round_v2/`. Round v1's files are read-only inputs.

**Unchanged and reused as locked inputs** (verify the content hashes before any run; a mismatch stops the round):
- `results_gate_dose/round_v1/MASKS.json` (content `6b456bd378e92ead…`): nested masks and levels. SensorScope `m ∈ {0, 0.10, 0.25, 0.40}`, U-Air `m ∈ {0, 0.10, 0.20}`.
- `TARGET_WIRING.json` (content `b9de9d9b7d7e7823…`): consumers T1–T3, with the value-equality assertion at ≤ 1e-12.
- `RHO.csv` (file `302cd48c779e9a2a…`): the train-atom ρ frame.
- `scripts/gate_dose.py::CONFIRMED`: items 2–4.

**Arms and configuration** are unchanged: `raven` and `raven_wo_design`, `local_steps = 2`, seeds 30001–30020, frozen EventTraces.

## II-2 Run count

| block | runs |
|---|---:|
| II-3 G1 determinism repeat: `raven`, m = 0, seed 30001, once more per dataset | 2 |
| II-3 G2: `raven_wo_design`, m = 0, seeds 30001–30002, both datasets | 4 |
| `raven`, m = 0, 20 seeds × 2 datasets (G3 is read off these) | 40 |
| dose cells: SensorScope 3 levels + U-Air 2 levels, × 20 seeds × 2 arms | 200 |
| **total** | **246** |

## II-3 Gate (a failure writes `GATE.json` with `"pass": false`, a JSON boolean, and stops Part II)

- **G1, determinism.** `raven`, m = 0, seed 30001, run twice per dataset in the same environment. θ must be bit-equal and the four endpoints must have `|Δ| = 0`.
- **G2, off-arm reproduction.** `raven_wo_design`, m = 0, seeds 30001–30002. Compared with the stored artifacts: `RMSE_μ`, `Δ_group`, `Δ_c-s` each `|Δ| ≤ 1e-9`, and `active_clients` identical on every window.
- **G3, on-arm drift bound.** All 40 fresh `raven` m = 0 runs, compared with the stored artifacts:
  - `active_clients` identical on every window;
  - `|ΔRMSE_μ| / RMSE_μ ≤ 1e-6`;
  - `|ΔΔ_group| / Δ_group ≤ 1e-6` and `|ΔΔ_c-s| / Δ_c-s ≤ 1e-6`.

  The bound is fixed now. It is four orders of magnitude below δ = 0.5 % and above the measured drift (5.3e-8 relative on SensorScope). G3 checks that the code drift is negligible against the effects tested. It does not make the stored artifacts the reference.

There is no waiver list and no second rule.

## II-4 Scoring, estimand, H1 and H2

Unchanged from round_v1 §3–§4:
- the θ re-scoring rule, with `CONFIRMED` item 4;
- the paired `r_e = (M_e(raven) − M_e(raven_wo_design)) / M_e(raven_wo_design)`;
- **H1**: OLS slope of `r_RMSE` on realized ρ, seed-cluster bootstrap, 10 000 draws, `default_rng(20261007)`. SensorScope is primary and U-Air is the replication. `gate_law = supported` if and only if SensorScope is `open` and U-Air is not `harm`;
- **H2**: non-inferiority of Design on at SensorScope m = 0, upper bound < +0.5 %, tested only if H1 supports;
- `ρ*` reported only when H1 is `open`.

## II-5 II-H3 (decision): does the pre-outcome gate choose the better setting?

**Policies**, evaluated per (dataset, level, seed) cell:
- `gate`: eq:design_gate, `D = on ⇔ ρ = 0`, using realized ρ.
- `always_on`.
- `always_off`.

**Ex-post optimum** under two weight vectors fixed now:
- `w_pred`: `RMSE_μ` only.
- `w_eq`: the four endpoints of eq:design_switch, `w_e = 1/4` each, relative to the Design-on value.

The regret of a policy is `Ĵ(policy choice) − min_D Ĵ(D)`. For `w_pred`, that is the relative `RMSE_μ` excess.

**Test, SensorScope only.** On U-Air every level has ρ > 0, so `gate` is the same policy as `always_off`; U-Air is reported descriptively. The intervals are seed-cluster bootstrap, as in H1.
- **Primary (`w_pred`).** `gate_decision = open` if and only if the mean regret difference has CI upper bound < 0 against both:
  - `regret(gate) − regret(always_on)`;
  - `regret(gate) − regret(always_off)`.
- `null` if either difference has a CI that contains 0. `harm` if either difference has CI lower bound > 0.
- `w_eq` is secondary, same rule, reported next to the primary.

**Base rate.** Report the share of SensorScope cells where `off` is optimal under each weight vector, with a Wilson interval. If it is 0 or 1, label II-H3 `saturated`. Report the same share per level, so the reader sees where the optimum switches.

## II-6 What Part II licenses

- **`gate_law = supported`.** The paper may state that a structural statistic computed before training predicts the sign and size of the prediction cost of Design, with the slope and its CI.
- **`gate_decision = open`** in addition. The gate is a decision rule that beats both fixed settings on held-out doses. Those doses were not used to place the switch point, which was fitted on U-Air.
- **SensorScope `null`.** The gate stays "a decision chart fitted to this U-Air ablation row" (L2050–2051), as written.
- **`harm`.** Reported in limitations.

## II-7 Part II outputs

`results_gate_dose/round_v2/`:
- `INPUT_HASHES.json`;
- `GATE.json`;
- `THETA_SCORED.csv`;
- `tables/DOSE_CELLS.csv`, `DOSE_SUMMARY.csv` and `DOSE_SLOPES.csv`, with the round_v1 §6 schemas;
- `tables/GATE_POLICY.csv`: per cell, ρ, the choices of the three policies, the optimum and regret under both weight vectors;
- `DOSE_DECISION.json`: gate pass, H1 labels, `gate_law`, H2, H3 labels, base rates, `ρ*`.

---

## III Joint reading (fixed now, so the story cannot be chosen after the numbers)

| Part I (SensorScope / U-Air) | Part II | contribution statement the results license |
|---|---|---|
| `open` on ≥ 1 | `supported` | Lead with the estimand: arrival-weighted validation selects the wrong model at a measured regret. Then the gate: the alignment factor's prediction cost is predicted by ρ. This is the E1 repair candidate. |
| `open` on ≥ 1 | not `supported` | Lead with the estimand. The gate stays a U-Air rule. |
| `null` / `saturated` / `inconclusive` on both | `supported` | Lead with the gate law, together with the E2 repair: a contribution statement that leads with the projection and the Design factor. |
| `null` / `saturated` / `inconclusive` on both | not `supported` | Neither claim. Fall back to writing up the bound (`results_evidence_axis/round_v1`, option C1), after the four corrections listed in that review. |

No manuscript edit follows from this file. A writing pass is a separate request.

## IV Execution order

| Priority | Step | Cost | Stop condition |
|---|---|---|---|
| I-P0 | `INVENTORY.json`, `WEIGHTS.csv` | none | missing checkpoint or trace in M × seeds |
| I-P1 | checkpoint scoring, reproduction check, Part I tables and labels | 360 inferences, no training | a reproduction miss outside the θ rule |
| II-P0 | verify round_v1 input hashes | none | hash mismatch |
| II-P1 | G1, G2, the 40 `raven` m = 0 runs, then G3 | 46 trains | any gate check fails |
| II-P2 | 200 dose cells | 200 trains | a θ re-score check fails, or a run is missing |
| II-P3 | tables, H1, H2 if licensed, H3, `DOSE_DECISION.json` | none | `INCOMPLETE` if any cell is missing |

Part I and Part II are independent. Part I may run first and alone.

## V Known limits, stated before the run

- `R_arr` uses per-group test error under arrival weights. It models a validation set whose group mix follows arrivals and whose within-group error equals the test error. It is not a separately held-out arrival sample.
- M is limited to the frozen configurations. No retuning per selection criterion.
- Part II carries round_v1 §8: a level changes ρ and the target together, the masks are random rather than structured, and City Scanner is excluded.
- T-Drive (ρ = 47.4 %) has no Design-on/off pair in `artifacts/`, so it is not a point on the dose line.

## VI No-fabrication status

Every value in I-3 to I-6 and II-3 to II-7 is `TBD` until the drivers write it. Section 0 is read from the named files. No result is claimed here.

Next owner after both decision files exist: report the labels and the row of III that applies. `ccf-paper-writer` only on a later request.

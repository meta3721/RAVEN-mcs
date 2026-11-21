# Executable instruction: a block on which alignment can be tested — NSW-Traffic screen, then confirm

```text
Mode: design + execution prompt.
Contract: CCFA-Skills/ccf-experiment-designer. Protocol, not publication prose.
Why this round exists: every Evidence-axis route on SensorScope and U-Air is now measured and
closed (weights, estimand selection, gate law, gate decision, exceedance decision). The
rounds share one cause: the endpoint was run before anyone checked that the block could move
it. This round reverses the order. It fixes four necessary conditions, measures them on a
block that already meets the one SensorScope/U-Air fail hardest, and spends confirmation
seeds only if all four hold.
Output: results_new_block_traffic/round_v1/ only.
Driver: new scripts/new_block_traffic.py. Do not edit src/.
Forbidden: editing src/, the manuscript, artifacts/, any existing results_* directory;
           regenerating or creating EventTraces; using seeds 30006–30020 before the S2 verdict
           is written; changing a threshold, ladder level, endpoint, arm, seed split or
           decision rule after any number of the stage it governs exists; selecting the
           training budget with any arm other than fedavg_window; git commit/push.
Authorization: S0 needs none (no training). S1 + S2 start after "授权交通筛查".
F starts only after S2 writes GO and the user writes "授权交通确认".
```

## 0 Necessary conditions and what is already measured

A weighting rule can buy measurable accuracy only if all four hold on the block:

| | condition | SensorScope / U-Air | NSW-Traffic (frozen `e3_formal_runs_r1`, `complete_aligned`, `local_steps = 2`) |
|---|---|---|---|
| N1 | weights have freedom: most active windows have `\|A_r\| ≥ 3` | **fails**: 51.4 % / 69.0 % of windows have `\|A_r\| ≤ 2` | **holds**: 6.8 % `≤ 2`, mean `\|A_r\|` 12.08 (1990 windows, `debt_cal`) |
| N2 | arrival and target laws differ at group level | holds (four-block TV 0.192 / 0.278) | **unmeasured** |
| N3 | the federated learner is off its floor | holds | **fails**: every federated arm `RMSE_μ` = 1.00348–1.00349 (n = 20). `central_delivered` 0.97543 (−2.9 %), `central_all` 0.95383 (−5.2 %) |
| N4 | group errors respond to the training mix: oracle headroom `H` | **fails**: `H` −0.27 % to −0.68 % at every condition, including target tilt (C1, C2) and low capacity (C3) (`results_h_headroom/round_v3`) | **unmeasured** |

Reading of N3: `central_delivered` trains on the same delivered data as the federated arms and is 2.9 % better. The gap is therefore optimisation budget, not information. Reading of N4 on U-Air: the C1–C3 levers acted through weights on a block where N1 fails, so their nulls do not show that those levers are inert where weights are free.

NSW-Traffic facts: 172 groups, 20 frozen EventTraces (seeds 30001–30020) under `artifacts/e3_formal_runs_r1/eventtraces/traffic/`, and two-stage-selection trace families under `artifacts/e2_traffic_formal_runs_r1/eventtraces/` used by RQ1. Frozen e3 arms on this block: `central_all`, `central_delivered`, `debt_cal`, `inst_cal`, `local_hajek`, `raven_simoracle`. There is no frozen `raven` or `fedavg_window` here.

## 1 Seed split (fixed now)

- **Screen seeds:** 30001–30005 (S1 uses 30001–30003).
- **Confirm seeds:** 30006–30020, n = 15. No stage before F may read, train on, or score these seeds.

## 2 S0 — read-only measurements (no training)

**S0-a, trace family.** Enumerate every pre-existing NSW-Traffic EventTrace family that has seeds 30001–30020. That is the e3 `complete_aligned` family plus each e2 selection condition. Write `TRACE_FAMILIES.json` with paths, seed coverage and hashes.

**S0-b, N2.** Per family and per screen seed, compute the group-level arrival law `π_arr`: the group shares of delivered `U = 1` non-test risk units. Compute `TV(π_arr, μ)` with the frozen 172-group `μ`. Also report top-1 and top-5 shares and `1 − H/H_max` of `μ`.

**S0-c, N1.** For every family: the per-window count of clients delivering at least one `U = 1` unit. Report the share of windows with count ≤ 2 and the mean count. This is trace-only, without the method's activity rule. The frozen-run figure in §0 is the cross-check for the e3 family.

**S0-d, error heterogeneity.** On the frozen `central_all` and `central_delivered` checkpoints, compute per-group test RMSE. Report the spread (worst/best) and the gap between target-weighted and uniform-weighted RMSE. These are evaluation-layer numbers only. They bound nothing about training.

**Family selection rule (fixed now).** Use the family with the largest mean `TV(π_arr, μ)` over the screen seeds, among families with S0-c `≤ 2` share below 25 %. If no family has mean TV ≥ 0.10, write `S0_VERDICT.json` with `"go": false, "failed": "N2"` and stop. The bar 0.10 sits between the paper's 0.05 floor and the 0.142–0.278 measured on the other blocks. If the chosen family is not the e3 family, S1 also trains `central_delivered` on it (seeds 30001–30003).

## 3 S1 — learnability ladder (N3), `fedavg_window` only

Budget ladder: `local_steps ∈ {2, 5, 10, 20}`. Everything else is the frozen configuration. Seeds 30001–30003. Selection uses `fedavg_window` alone, so no arm comparison enters the choice.

Let `c` be the mean `RMSE_μ` of `central_delivered` on the chosen family and the same seeds. The selected budget `L*` is the smallest level whose mean `fedavg_window` `RMSE_μ` is ≤ `1.01 · c`. If no level qualifies:
- if the best level is at least 1 % below level 2, `L*` is the best level, recorded as `"L_star_reason": "best_not_within_1pct"`;
- otherwise write `"go": false, "failed": "N3"` and stop.

`L*` then applies to **every** arm in S2 and F. Runs: 12 (plus 3 if `central_delivered` is needed).

## 4 S2 — headroom and decision screen (N4), seeds 30001–30005, budget `L*`

**Arms:**
- `fedavg_window`;
- `raven_simoracle` (oracle weights inside the same active set, the round_v3 construction);
- `central_delivered` (reference only).

If the chosen family has `ρ > 0` (train-atom frame, `scripts/gate_dose.py` semantics), also run `raven_simoracle_nodesign`. Design follows eq:design_gate in F. Runs: 15, or 20 with the extra arm.

**Headroom.**

```text
H = (RMSE_μ(fedavg_window) − RMSE_μ(raven_simoracle)) / RMSE_μ(fedavg_window), per seed.
```

- **GO-H** iff mean `H` ≥ 1.0 % **and** the one-sided 95 % Student-t lower bound (n = 5) is > 0.5 %.
- **Power check (fixed now).** Projected confirm-stage MDE: `MDE80 = (t_{0.975,14} + t_{0.80,14}) · sd(H) / √15`. GO-H additionally requires `MDE80 < 0.5 · mean H`.

**Decision quantity (fixed now).**
- Threshold `τ` = the 0.90 quantile of the training-split target values on the chosen family.
- A unit is an exceedance iff `y > τ`. The alert is `ŷ > τ`.
- Endpoint: `F1_μ`, the F1 of alerts with each test unit weighted by `μ` of its group divided by the group's test count.

**GO-D** iff all three hold:
- the μ-weighted base rate of exceedance on the test split lies in [0.05, 0.30];
- both `fedavg_window` and `raven_simoracle` have μ-weighted recall in (0.02, 0.98) on every screen seed;
- mean `F1_μ(simoracle) − F1_μ(fedavg)` is > 0.

This is the non-saturation condition that the U-Air exceedance endpoint failed (NEW-r12-1).

**Verdict.** `S2_VERDICT.json` has `"go": true` iff GO-H and GO-D. Otherwise it has `"go": false` and lists which of `H`, `power`, `base_rate`, `recall` or `F1_direction` failed. Either way, S2 ends the screen; nothing is retuned.

## 5 F — confirmation (only after GO and "授权交通确认"), seeds 30006–30020, budget `L*`

**Arms (fixed now):**
- `fedavg_window` (primary comparator);
- `raven`, with Design per eq:design_gate on the chosen family;
- `local_hajek`, `debt_cal`, `inst_cal`, `twostage_hajek` (secondary comparators);
- `raven_simoracle` (ceiling);
- `central_delivered` (reference).

Runs: 8 × 15 = 120.

**Primary (F-H1, prediction).** The paired relative gain is `g = (RMSE_μ(fedavg_window) − RMSE_μ(raven)) / RMSE_μ(fedavg_window)`.
- `open` iff the two-sided 95 % Student-t lower bound (n = 15) is > 0.5 %;
- `harm` iff the upper bound is < 0;
- otherwise `null`.

**Co-primary (F-H2, decision).** Paired `ΔF1_μ = F1_μ(raven) − F1_μ(fedavg_window)`.
- `open` iff the 95 % lower bound is > 0;
- the same base-rate and recall checks as GO-D, on the confirm seeds. If they fail, the label is `saturated`.

**Multiplicity.** Holm over {F-H1, F-H2}. The E1 repair claim needs both to be `open` after Holm.

**Descriptive, no decision:**
- `raven` versus each secondary comparator;
- the fraction of the oracle headroom recovered, `g / H`, on the confirm seeds;
- `Δ_group`, `Δ_c-s` and `Tail_RMSE` for every arm;
- `|A_r|` distribution of `raven`, and P2 weight dispersion per window.

## 6 What each outcome licenses

- **S0 or S1 NO-GO.** NSW-Traffic cannot test the claim either. The reason is reported (N2 or N3). No F seed is used.
- **S2 NO-GO.**
  - If `H` fails, oracle weights cannot buy accuracy even where the weights are free and the learner trains. That is the strongest negative the paper can report, and it belongs in limitations.
  - If only GO-D fails, a prediction-only F is **not** licensed by this file, because E1 requires both.
- **F both `open`.** On NSW-Traffic at budget `L*`, the deployment-target-aligned aggregation lowers `RMSE_μ` by `g` against window FedAvg and raises the target-weighted alert F1, on held-out seeds, against a measured oracle ceiling. This is the E1 repair candidate. The paper must also state that the block uses a Complete-aligned control for `O` and `U`, and that its training budget differs from the other blocks.
- **F otherwise.** Reported as measured. No claim beyond the label.

No manuscript edit follows from this file.

## 7 Outputs

`results_new_block_traffic/round_v1/`:
- `TRACE_FAMILIES.json`, `S0_TABLE.csv`, `S0_VERDICT.json`;
- `S1_LADDER.csv`, `S1_VERDICT.json` (with `L*` and its reason);
- `S2_CELLS.csv`, `S2_VERDICT.json`;
- after F: `F_CELLS.csv`, `F_SUMMARY.csv`, `F_DECISION.json`;
- `MANIFEST.sha256`, written before each stage's first run, covering this file's sha256, the family choice and `L*`.

## 8 Execution order and stops

| step | cost | stop |
|---|---|---|
| S0 | none | no family with TV ≥ 0.10 and `≤ 2` share < 25 % |
| S1 | 12–15 trains | no admissible `L*` |
| S2 | 15–20 trains | GO-H or GO-D fails |
| F | 120 trains | a run is missing (`INCOMPLETE`), or a θ re-score check fails under the round_v1 §3 rule |

Record the wall time of the first S1 run. If it projects F beyond 24 h on this machine, write that into `S2_VERDICT.json` before asking for the F authorization.

## 9 Known limits, stated before the run

- On NSW-Traffic, `O` and `U` are Complete-aligned controls, and opportunity shift comes from the selected trace family. This is a controlled block, not an end-to-end mobile deployment.
- `L*` is chosen on screen seeds with one arm. The S2 headroom is measured on the same screen seeds at that budget. F uses disjoint seeds, so neither choice is re-used as evidence.
- `τ` is a training-split quantile. It is not a regulatory threshold for this quantity.
- One block. A positive F does not transfer to SensorScope or U-Air, where N1 fails by measurement.

## 10 No-fabrication status

Every S0–F value is `TBD` until the driver writes it. Section 0 is read from frozen artifacts or from the measurements made on 2026-10-07 (`|A_r|` counts and the NSW-Traffic `RMSE_μ` table). No result is claimed here.

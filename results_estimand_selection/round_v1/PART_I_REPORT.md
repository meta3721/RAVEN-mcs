# Part I — arrival-weighted validation versus deployment-target selection

Round: `results_estimand_selection/round_v1/`
Instruction: `raven-mcs-estimand-gate-execution-prompt.md`, sha256 `ffb4bde6…`, 18 510 B
Contract: `CCFA-Skills/ccf-experiment-designer` (protocol, not publication prose).
Executed 2026-10-07. **No training.** `src/`, the manuscript, `artifacts/` and every other
`results_*` untouched. Driver: `scripts/estimand_selection.py`.

## 1 Gate and reproduction

**I-P0 inventory.** The 9-configuration set `M` is complete for both datasets: every method ×
seed 30001–30020 holds `checkpoints/final.pt`, `final_metrics.json` and `window_metrics.json`
(20/20). No run is `INCOMPLETE`; none was replaced.

**NSW-Traffic: excluded, with the full reason recorded** (`INVENTORY.json → nsw_traffic`).
Two roots were searched:

| root | exists | contents |
| --- | --- | --- |
| `artifacts/e3_formal_runs_r1/runs/traffic` | yes | `central_all`, `central_delivered`, `debt_cal`, `inst_cal`, `local_hajek`, `raven_simoracle` |
| `artifacts/e3_formal_runs_r1/eventtraces/traffic` | yes | `seed30001`–`seed30020` |

Of the 9 configurations of `M`, **3 are present and in `M`** (`debt_cal`, `inst_cal`,
`local_hajek`); **6 are missing**: `fedavg_window`, `fedasync_window`,
`flamf_timealign_adapted`, `twostage_hajek`, `raven`, `raven_wo_design`. Accounting:
9 = 3 + 6, and the 3 further directories that do exist are the non-deployable configurations
I-2 excludes. `eligible: false`, verdict `EXCLUDED_FROM_M`. **No substitute source was used**:
not the RQ1 five-method NSW experiment, not NSW runs under any other directory, and no
reduced-method ranking for this dataset only. SensorScope and U-Air proceed as locked.

**Reproduction check.** `sqrt(Σ_g μ_g MSE_g)` against the stored `RMSE_mu` for all 360
(dataset, method, seed) cells: **360/360 within 1e-8 relative**, and in fact within 5e-15.
**No active-window miss**, so Part I did not stop.

**θ-scored cells: 24** (`THETA_SCORED.csv`). All are `uair` seeds **30007, 30016, 30018** —
the three traces whose final window is inactive — across all 8 `E3` methods.
`raven_wo_design` has no inactive final window. Their stored `RMSE_mu` is the in-memory
mirror value and moves by **1.3–5.1 %** when the saved checkpoint is scored; the checkpoint
value is canonical here, per I-2, and `RISK_ROWS.csv` carries both the stored and the
scored value for every cell. This is consistent with the round_v1 finding and is wider than
the 3 cells listed there because that note covered only the `raven` arm.

## 2 Weights (`WEIGHTS.csv`, written before any score)

Written first, in a separate stage, so no number below could influence it.
**Content hash `cd1aa6d3b6c01b90…`.**

| dataset | groups | TV(π_arr, μ) | ‖π_arr − μ‖₁ | TV(π_arr^R, μ) | ‖π_arr^R − μ‖₁ |
| --- | ---: | ---: | ---: | ---: | ---: |
| SensorScope | 220 | **0.354784** | 0.709569 | 0.252594 | 0.505188 |
| U-Air | 144 | **0.425505** | 0.851011 | 0.287168 | 0.574337 |

The arrival mix and the deployment target are very far apart at group level — much further
than the four-block `TV(π^opp, μ)` of 0.192 / 0.278 the manuscript reports (`main.tex`
L1688–1689), because this statistic is at stratum×group level rather than four blocks.

## 3 Misreport: the arrival-weighted risk is a biased estimate of deployment risk

`b = (R_arr − R_μ)/R_μ` per method, mean over 20 seeds with Student-t 95 % intervals:

| dataset | b across the 9 methods | spread | interpretation |
| --- | --- | ---: | --- |
| SensorScope | **−0.0411 to −0.0412** | 0.0001 | arrival validation **understates** risk by ≈4.1 %, for every method |
| U-Air | **+0.0027 to +0.0062** | 0.0035 | arrival validation **overstates** risk by ≈0.3–0.6 %, for every method |

So the estimand gap is real and large on SensorScope: a deployer who reads
`R_arr ≈ 7.61` is reading a number that is 4.1 % below the deployment risk they will pay.
The bias is nearly a constant, not a per-method correction.

## 4 Decision: the misreport does **not** reach the selection

| quantity | SensorScope | U-Air |
| --- | ---: | ---: |
| `m_arr` (arrival validation picks) | `twostage_hajek` | `twostage_hajek` |
| `m_μ` (deployment target picks) | `twostage_hajek` | `twostage_hajek` |
| disagreement rate `d̄` | **0.000**, Wilson [0.000, 0.161] | **0.000**, Wilson [0.000, 0.161] |
| mean regret `reg` | **0.000000**, CI [0.000000, 0.000000] | **0.000000**, CI [0.000000, 0.000000] |
| Kendall τ (R_arr vs R_μ rankings) | median **1.000**, mean 0.9943 | median **1.000**, mean 1.0000 |
| sign-flip rate over method pairs | 0.0029 (n = 700) | 0.0000 (n = 700) |
| sign-flip, restricted to \|ΔR_μ\| > δ = 0.5 % | **0.0000** (n = 10) | **0.0000** (n = 417) |
| label (I-H1) | **`saturated`** | **`saturated`** |

Both datasets are labelled **`saturated`** by the base-rate condition, because `d̄ = 0`:
arrival-weighted validation never picks a different model than the deployment target does,
in any of the 20 seeds. The regret is therefore identically zero and its seed bootstrap has
no width (the MDE collapses to 0 — reported as degenerate, not divided by).

**Sensitivity.** Under `π_arr^R` (all `R = 1` opportunity units instead of delivered `U = 1`):
mean regret 0, disagreement 0, median τ 1.000, both datasets. Under `M` without
`raven_wo_design`: same (`SELECTION_no_nodesign.csv`, `SELECTION_DECISION_no_nodesign.json`).

## 5 Reading

The arrival-weighted risk is a **bad estimate of the level** and a **perfect guide to the
order**. On SensorScope the misreport is −4.1 % — a deployer validating on arrivals would
understate their deployment risk by more than four points, on every candidate — yet the
ranking is preserved exactly, so the model they choose is the model the deployment target
would choose, and the regret is 0.000000 with an upper CI bound of 0.000000, far inside the
δ = 0.5 % margin.

This is the honest form of the E1 answer for Part I: **the decision base rate is degenerate
(`d̄ = 0`), so the decision quantity is saturated**, and the estimand gap does not convert
into a selection cost through this route. Per I-5, a `saturated` label adds nothing to the
claims; the misreport numbers (§3) stand as descriptive readouts of `b`.

The mechanism is visible in §3: the misreport is a near-constant because the arrival mix and
the target differ mostly in how they weight *groups*, while the candidate models' per-group
errors move together. Only the level of the reported risk changes, not the ordering.

## 6 Limits, stated before the run and confirmed after

* `R_arr` uses per-group **test** error under arrival weights; it is not a separately held-out
  arrival sample (I-5, first bullet).
* `M` is the frozen configuration set. No retuning per criterion.
* `d̄ = 0` on both blocks means the primary hypothesis is decided by the base-rate condition,
  not by the regret interval. The Wilson upper bound of 0.161 says the data are also
  consistent with a disagreement rate as high as 16 %, so the statement is "no disagreement
  observed in 20 seeds", not "no disagreement possible".
* 24 cells are θ-scored; the primary analysis includes them, and §3/§4 are unaffected by
  removing them because the same `twostage_hajek` wins either way.

## 7 Outputs

`INVENTORY.json` (`cc50a11fa4083739…`), `WEIGHTS.csv` (`cd1aa6d3b6c01b90…`),
`WEIGHTS_META.json`, `THETA_SCORED.csv`, `REPRODUCTION_CHECK.json`,
`tables/RISK_ROWS.csv` (360 rows), `tables/REPRODUCTION.csv`, `tables/SELECTION.csv`,
`tables/SELECTION_no_nodesign.csv`, `tables/SELECTION_SUMMARY.csv`,
`SELECTION_DECISION.json`, `SELECTION_DECISION_no_nodesign.json`.

## 8 What Part I licenses

Nothing positive, per I-5 and the Part III table: `null`/`saturated` on both datasets means
the estimand route does not supply the E1 repair. If Part II is also not `supported`, Part III
row 4 applies: fall back to writing the bound (`results_evidence_axis/round_v1`, option C1),
after the corrections listed in that round's review. Part II needs its own authorization
(`授权门控剂量`); it has not been started.

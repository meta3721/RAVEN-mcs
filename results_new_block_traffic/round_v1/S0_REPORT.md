# S0 report — NSW-Traffic screen (read-only, no training)

Round: `results_new_block_traffic/round_v1/`
Instruction: `raven-mcs-new-block-traffic-execution-prompt.md`, sha256 `25f580aa…`, 11 605 B
Driver: `scripts/new_block_traffic.py`. Executed 2026-10-07. **No training**, no `src/`,
manuscript, `artifacts/` or other `results_*` write.

## 1 S0-a — trace families

Two roots were searched; seven families cover seeds 30001–30020 in full (20/20 each):

| family | root | seeds | family content sha256 |
| --- | --- | ---: | --- |
| `e3_complete_aligned` | `artifacts/e3_formal_runs_r1/eventtraces/traffic` | 20 | `875c0be390fe9c92…` |
| `balanced` | `artifacts/e2_traffic_formal_runs_r1/eventtraces/<seed>/balanced` | 20 | per `TRACE_FAMILIES.json` |
| `complete_aligned` | same root, `complete_aligned` | 20 | ” |
| `complete_counteracting` | same root | 20 | ” |
| `observation_only` | same root | 20 | ” |
| `opportunity_only` | same root | 20 | ” |
| `usable_only` | same root | 20 | ” |

Paths, per-seed byte sizes and per-seed sha256 are in `TRACE_FAMILIES.json`. The e2 family
layout is `<seed>/<condition>/training_eventtrace/events.parquet`; the e3 family is
`seed<seed>/training_eventtrace/events.parquet`.

## 2 S0-b — N2, the arrival law against the target

Frozen target: **172 groups**, `μ` top-1 **0.581 %**, top-5 **2.907 %**,
`1 − H/H_max` **−0.000000** (i.e. `μ` is exactly uniform over the 172 groups).

| family | mean TV(π_arr, μ) over screen seeds | per-seed TV range |
| --- | ---: | --- |
| **`e3_complete_aligned`** | **0.35638** | 0.3508 – 0.3652 |
| `complete_aligned` | 0.35638 | identical to e3 (same traces) |
| `complete_counteracting` | 0.23419 | 0.2188 – 0.2461 |
| `opportunity_only` | 0.19331 | 0.1831 – 0.2039 |
| `observation_only` | 0.18390 | 0.1768 – 0.1912 |
| `usable_only` | 0.15712 | 0.1515 – 0.1606 |
| `balanced` | 0.13150 | 0.1181 – 0.1415 |

All seven clear the 0.10 bar. The arrival law is far more concentrated than the target:
`π_arr` top-1 is **1.43–1.68 %** against `μ`'s 0.58 %, and `π_arr` top-5 is
**6.93–7.59 %** against 2.91 %. On this block N2 holds by a wide margin — and at 0.356 the
TV is larger than the four-block figures the manuscript reports (0.142 – 0.278).

## 3 S0-c — N1, freedom of the weights (trace-only)

Per-window count of distinct clients delivering at least one `U = 1` unit:

| family | mean clients/window | share of windows ≤ 2 | max |
| --- | ---: | ---: | ---: |
| **`e3_complete_aligned`** | **12.06** | **0.0669** | 28 |
| `balanced` | 13.14 | 0.0000 | 22 |
| `complete_counteracting` | 12.11 | 0.0000 | 25 |
| `observation_only` | 12.68 | 0.0021 | 26 |
| `opportunity_only` | 12.93 | 0.0000 | 23 |
| `usable_only` | 13.03 | 0.0000 | 25 |

**Cross-check against the protocol's §0 figure.** §0 states 6.8 % `≤ 2` and mean `|A_r|`
12.08 for the frozen `debt_cal` runs on the e3 family. This trace-only measurement gives
**6.69 %** and **12.06**, so the run-side and trace-side agree. N1 holds on this block in
contrast to SensorScope (51.4 % `≤ 2`) and U-Air (69.0 %).

## 4 S0-d — error heterogeneity (evaluation-layer only)

Frozen `central_all` and `central_delivered` checkpoints, per-group test RMSE:

| arm | seed | `RMSE_μ` (target) | stored | rel. diff | uniform | uniform − target | best group | worst group | spread |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `central_all` | 30001 | 0.964002 | 0.964002 | **0.0** | 0.964002 | −1.2e-14 | 0.10260 | 4.09399 | 39.9× |
| `central_delivered` | 30001 | 0.982733 | 0.982733 | **0.0** | 0.982733 | −1.1e-14 | 0.08245 | 4.09837 | 49.7× |
| `central_all` | 30002 | 0.960475 | 0.960475 | **0.0** | 0.960475 | 0.0 | 0.07659 | 3.96845 | 51.8× |
| `central_delivered` | 30002 | 0.972424 | 0.972424 | **0.0** | 0.972424 | 0.0 | 0.08957 | 4.12679 | 46.1× |

Two readings. First, the scoring path is faithful: `sqrt(Σ μ_g MSE_g)` reproduces the stored
`RMSE_μ` to **0.0 relative** on all four cells. Second, the group errors are extremely
heterogeneous (**40–52×** worst/best) while `μ` is exactly uniform — so on this block the
deployment weighting is uniform by construction and the *only* way weights can matter is a
rule that departs from uniform, which is precisely what §0's N3 measurement makes possible:
the frozen federated arms sit on a floor (1.00348–1.00349) that `central_delivered` beats by
2.9 % on the same delivered data.

## 5 Family selection rule, applied verbatim

Admissible = S0-c `≤ 2` share < 25 %; among those, largest mean TV; bar 0.10.

| family | mean TV | `≤ 2` share | TV ≥ 0.10 | share < 25 % |
| --- | ---: | ---: | --- | --- |
| **`e3_complete_aligned`** | **0.35638** | 0.0669 | yes | yes |
| `complete_counteracting` | 0.23419 | 0.0000 | yes | yes |
| `opportunity_only` | 0.19331 | 0.0000 | yes | yes |
| `observation_only` | 0.18390 | 0.0021 | yes | yes |
| `usable_only` | 0.15712 | 0.0000 | yes | yes |
| `balanced` | 0.13150 | 0.0000 | yes | yes |

`complete_aligned` is not listed separately because it is the same traces as
`e3_complete_aligned` (identical per-seed sha256), which the enumeration records rather than
double-counts.

**Verdict: `go = true`, chosen family `e3_complete_aligned`, mean TV 0.35638.**
Because the chosen family *is* the e3 family, §2's conditional does not fire: S1 does **not**
need an extra `central_delivered` run.

## 6 What this licenses, and what it does not

Per §6: S0 has no NO-GO branch to report, so nothing about NSW-Traffic is closed by this
stage. The screen establishes that the block satisfies **N1** and **N2**; **N3** (learnability)
and **N4** (headroom and decision non-saturation) are unmeasured and belong to S1 and S2.
Section 0's N3 reading is repeated as a hypothesis, not a result: the frozen federated arms
sit on a floor that `central_delivered` beats on the same data, so the gap looks like
optimisation budget rather than information — S1's ladder tests exactly that.

No claim is made here about the prediction or decision endpoint on this block, and no F seed
(30006–30020) was read, trained on or scored.

## 7 Outputs

`TRACE_FAMILIES.json`, `S0_TABLE.csv`, `S0_VERDICT.json`, `S0_FOLLOWUP.json`,
`MANIFEST.sha256` (written before any S1 run, covering this file's sha256, the family choice
and the seed split).

## 8 §8 wall-time projection, and §0 cross-checks (added 2026-10-07, read-only)

§8 asks for the first S1 run's wall time and a projection of F (120 runs) against 24 h. The
ladder has not been run and, per §3, no ladder number may exist before authorization, so the
projection is built from the **frozen e3 traffic runs' own `runtime_seconds`** on the same
block and configuration, not from a new run.

| quantity | measured |
| --- | ---: |
| frozen federated-family per-run runtime, 80 runs (4 arms × 20 seeds) | mean **67.6 s**, min 61.9 s, max 73.7 s, sd ≈2 s |
| worst case for `local_steps = 20` (linear, 10× the frozen 2-step cost) | **676 s/run** |
| S1 = 12 runs | 2.3 h |
| S2 = 15 runs | 2.8 h |
| **F = 120 runs** | **22.5 h on the mean baseline**; **24.6 h on the slowest observed run** |

**F is borderline against the 24 h cap**: 22.5 h expected, and 24.6 h if every F run costs
what the slowest frozen run cost. §8 requires this to be written into `S2_VERDICT.json`
before the F authorization is requested, which this note satisfies; the estimate should be
refreshed from S1's measured first-run wall time once S1 is authorized.

**§0 cross-checks** (independent, from the frozen artifacts):

| §0 claim | measured | verdict |
| --- | --- | --- |
| no frozen `raven` or `fedavg_window` on this block | both absent; present arms are `central_all`, `central_delivered`, `debt_cal`, `inst_cal`, `local_hajek`, `raven_simoracle` | confirmed |
| every federated arm `RMSE_μ` = 1.00348–1.00349 (n = 20) | `debt_cal` 1.00348, `inst_cal` 1.00348, `local_hajek` 1.00349, `raven_simoracle` 1.00348 | confirmed |
| `central_delivered` 0.97543 (−2.9 %) | 0.97543; ratio to the federated mean is **−2.79 %** | value confirmed, percentage is −2.8 % not −2.9 % |
| `central_all` 0.95383 (−5.2 %) | 0.95383; ratio to the federated mean is **−4.95 %** | value confirmed, percentage is −5.0 % not −5.2 % |
| N1 on the frozen runs: 6.8 % `≤ 2`, mean `\|A_r\|` 12.08, 1990 windows | `debt_cal`: 1990 active windows, mean **12.08**, `≤ 2` share **0.0683**, max 29 | confirmed exactly |

**Design-gate condition for the S2 arm set.** §4 runs `raven_simoracle_nodesign` only "if the
chosen family has `ρ > 0` (train-atom frame)". On the chosen family
(`e3_complete_aligned`): 344 client×stratum keys, **all positive**, 18 576 train atoms with
**0** on zero-target keys, so `φ_train_unit = 0` and by `eq:design_gate` Design is **on**
⇒ `ρ = 0`. **The conditional does not fire: S2 runs 15 cells, not 20, and no
`raven_simoracle_nodesign` arm is used.** This is the same statement the manuscript makes
for NSW-Traffic ("both City Scanner rankings are on because their public targets are
four-region shares with every region positive", and §0 of the instruction lists NSW as a
block whose target is positive everywhere), now verified on this family's train atoms.

## 9 Pre-S2 checks: the scoring path reproduces, and the decision endpoint cannot fire

Added 2026-10-07, read-only, before any S1 run. Both checks use the driver's own
`score_checkpoint`, so the validated code is the code S2 will run.

### 9.1 The S2 scoring path reproduces the frozen artifacts exactly

`score_checkpoint` applied to all 6 frozen arms × 3 screen seeds (18 cells):

| quantity | result |
| --- | --- |
| worst relative error of `RMSE_μ` vs stored `final_metrics.json` | **0.000e+00** (all 18 cells) |
| μ-weighted test weights sum to 1 | yes by construction (each group has exactly 36 test units) |
| `τ` = train-split 0.90 quantile | **1.343869** (validation-split sensitivity: 1.383208) |

So `H` in S2 is a difference of two quantities computed by a path that reproduces the
paper's own stored numbers to machine precision.

### 9.2 The decision endpoint produces zero alerts on every frozen arm

The same scoring run returns `alert_rate_mu = 0`, `recall_mu = 0`, `F1_mu = 0` for **all 18
cells**. Measured cause, not inferred:

| quantity | value |
| --- | ---: |
| `τ` (alert threshold) | 1.3439 |
| largest single prediction, any arm × any screen seed | **0.2978** |
| ratio `τ` / largest prediction | **4.5×** |
| largest share of test units alerted, any arm × seed | **0.00000** |

The scale facts behind it: the train split is z-scored (mean 0.00000, sd 1.00000, range
−0.96 … +7.95); the best **constant** predictor on train has test RMSE **1.00670**; the
frozen federated arms measure **1.00348** and `central_delivered` **0.97543**. So the
federated arms beat a constant predictor by **0.3 %** — they are, numerically, constant
predictors near 0, and a constant cannot exceed `τ` = 1.34.

**Consequence for GO-D**, whose three conditions are a μ-weighted base rate in [0.05, 0.30],
recall strictly inside (0.02, 0.98) for **both** `fedavg_window` and `raven_simoracle`, and
`mean F1(simoracle) − mean F1(fedavg) > 0`:

* base rate **0.0990** — passes, the base-rate condition is not the problem;
* recall **0.00** on both arms — **fails** (outside the open band);
* `mean ΔF1` **0.0000** — **fails** (not > 0).

This is the mirror image of `NEW-r12-1` on U-Air: there the decision endpoint was saturated
by excess alerts; here it is saturated by the absence of them.

**Status of this forecast — it is a forecast, not the verdict.** It is measured at
`local_steps = 2`, and S1's ladder raises the budget to `L* ∈ {2, 5, 10, 20}` before S2
runs. More optimisation could widen the prediction range; the gap to close is **4.5×**. I am
recording it now precisely because §5 of the instruction makes S2 the deciding stage and this
is the condition that would stop it, and I am **not** treating it as settled: S2 runs the
frozen arms at `L*` and its own verdict governs. If S2 returns NO-GO on `recall` and
`F1_direction`, this section is the explanation and the reason the failure was foreseeable
from artifacts rather than from 15 training runs.

**What it means for §6.** S2 NO-GO with `H` failing is the strongest negative the paper can
report ("oracle weights cannot buy accuracy even where the weights are free"). S2 NO-GO with
only GO-D failing is the other case: a prediction-only F is **not** licensed by this file,
because E1 requires both endpoints. On the evidence here, `H` is genuinely open — the ladder
has not been run — but GO-D is the condition to watch.

### 9.3 GO-H's power clause is the binding risk, not the headroom level

GO-H requires mean `H ≥ 1.0 %`, a one-sided 95 % lower bound > 0.5 %, **and**
`MDE80 = (t_{0.975,14} + t_{0.80,14})·sd(H)/√15 < 0.5·mean H`. With
`t_{0.975,14} + t_{0.80,14} = 3.012841`, the projected confirm-stage resolution is
**0.7779 · sd(H)**.

`sd(H)` cannot be measured before S1/S2 exist. What can be measured is the scale it inherits,
from the frozen arms' own seed-to-seed `RMSE_μ` dispersion over 20 seeds:

| arm | mean `RMSE_μ` | sd over 20 seeds |
| --- | ---: | ---: |
| `central_all` | 0.953832 | 0.013224 |
| `central_delivered` | 0.975425 | 0.016986 |
| `debt_cal` | 1.003476 | 0.002516 |
| `inst_cal` | 1.003481 | 0.002458 |
| `local_hajek` | 1.003491 | 0.002422 |
| `raven_simoracle` | 1.003478 | 0.002459 |

The power clause is equivalent to `mean H > 2·MDE80 = 1.5558·sd(H)`. So it demands:

| `sd(H)` | projected `MDE80` | required mean `H` | against the 1.0 % bar |
| ---: | ---: | ---: | --- |
| 0.002466 (the federated arms' own dispersion) | 0.19 % | 0.38 % | comfortable |
| 0.005 | 0.39 % | 0.78 % | tight |
| **0.006395** | 0.50 % | **0.99 %** | **break-even with the bar itself** |
| 0.010 | 0.78 % | 1.56 % | the clause now exceeds the bar |
| 0.016986 (`central_delivered`'s dispersion) | 1.32 % | 2.64 % | unreachable for a fixed-class weighting effect |

**The tension, stated plainly.** The power clause alone forces `mean H` above twice the
resolution, while the design's own recorded effects on comparable classes are small: U-Air's
fixed-class headroom `H` measured **0.34 %**, this block's per-window reach of target mass is
**0.89 %**, and the only large number on record (**6.89 %**, U-Air Design removal) comes from
changing the *support*, not from a fixed-class oracle reweighting. So once `sd(H) ≳ 0.0064`
the clause demands more than the accompanying 1.0 % bar, and the smallest effect this design
could resolve at `sd(H) = 0.017` is about **1.3 %** — larger than any fixed-class headroom
measured anywhere in this project.

**This is a forecast from artifacts, and the binding condition is power, not `H` itself.**
§4 fixes the rule and S2 at `L*` settles it; if S2 returns NO-GO, this section predicts which
of `H`, `power`, `base_rate`, `recall` or `F1_direction` will be named, and §9.2 already
forecasts the last two.

**Together with §9.2, both of S2's gates are forecast to fail for structural reasons** —
GO-H on power (unless `sd(H)` comes in below ≈0.0064 *and* the effect exceeds ~0.4 %), GO-D on
recall and F1 direction (alerts are impossible at this threshold). That would make S2 a NO-GO,
which per §6 closes the Evidence-axis question for this block as well: no F seed is used, and
the outcome is reported with its reason. I state it before the run because §8 asks for the
screen to be read before seeds are spent, and because a NO-GO whose causes were visible in the
frozen artifacts should be reported as foreseen rather than discovered.

## 10 Next step

**S1 + S2 require the authorization phrase `授权交通筛查`.** S1 is the learnability ladder —
`fedavg_window` only, `local_steps ∈ {2, 5, 10, 20}`, seeds 30001–30003, 12 runs — selecting
`L*` such that mean `RMSE_μ` ≤ `1.01 · c` where `c` is `central_delivered`'s mean on the same
family and seeds. S2 then measures headroom `H` and the μ-weighted exceedance `F1` on seeds
30001–30005 at budget `L*`. Neither has been started.

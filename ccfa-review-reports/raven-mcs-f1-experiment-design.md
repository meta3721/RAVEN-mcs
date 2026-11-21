# F-1 experiment design — does the constructed selection regime cap the gain?

```text
Mode: design, then executed. Sections 0-4 and 6-8 are the design; 5.3, 5.4 and 9 are results.
Venue / paper type: IEEE TMC journal article, method + evidence paper
Target of the test: record §3 T8, hypothesis H-A, and §3 T8 F-1
Inputs: ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md (§2 L6–L9, §3 T1–T8, D-6);
        artifacts/e3_formal_runs_r1/** (560 published runs, 20 paired seeds);
        artifacts/e3_f1_score_dependent_r1/**, artifacts/e3_f1_theta1_r1/** (160 new cells);
        data/processed/{sensorscope,uair}/atomic_units.parquet;
        src/raven_mcs/e3/real_runner/generator_r3.py;
        src/raven_mcs/training/window_runner.py; src/raven_mcs/aggregation/method_policy.py
Status: DESIGN AND EXECUTED, 2026-09-24. Verdict: H-A is refuted (§5.4). Every number marked
        "measured" comes from the artifact named next to it; the two arms and the driver are named
        in §5.4. No file under artifacts/e3_formal_runs_r1/ was written.
```

---

## 0. F-1 as recorded cannot be run as written

The record says: *"Give `p_obs` a unit-level, score-dependent term while holding the marginal rate
fixed. The E2 generator already implements exactly this (`logits = intercept + d_p·κ_p·s`) … port
it into the E3 runner."*

Porting it literally does nothing, for a structural reason established below: **in E3 the
opportunity stratum is nested inside the target group**, and E3's `tail_score` analogue *is* the
UTC block (`_stratum_is_tail(stratum, {2, 3})`, `semantic_alignment/complete_aligned_r2.py:44`).
A block-indexed score is therefore constant on every stratum, so a "score-dependent" `p_obs` built
from it is exactly the current construction with a different name. The manipulation would change
the label of the propensity, not its geometry.

This section is the main product of this design pass. The rest of the file specifies the
manipulation that does change the geometry.

---

## 1. Verified constraints the design has to respect

All rows below were read from the repository in this pass, not assumed.

| # | fact | value | source |
|:--|:---|:---|:---|
| C1 | opportunity stratum is nested inside the target group | `h(i) = s93::block0`, `s(i) = s93::block0::weekend` | `delta_cs_rho/stratum.py:21-24`; `semantic_alignment/target_semantics.py:71` |
| C2 | no risk set spans two groups | **0 of 800** SensorScope, **0 of 640** U-Air client-windows | `eventtraces/{dataset}/seed30001/training_eventtrace/events.parquet` × `atomic_units.parquet` |
| C3 | no stratum spans two groups | **0 of 312** SensorScope, **0 of 232** U-Air strata (one seed each) | same |
| C4 | a group is covered by one or two strata (weekday / weekend) | 189 parents with 1–2 strata (SS), 132 (U-Air) | same |
| C5 | the true observation propensity is two-valued and block-level | `p_obs_true ∈ {0.1925, 0.35}` over 28 800 audit rows | record L6; `artifacts/a5_a6_audit/audit_records.csv` |
| C6 | both design factors are stratum-constant in truth | `π^opp_s` and `π^tar_s` are functions of the block and of the group only | `generator_r3.py:33-40`; C1 |
| C7 | the frozen propensity model has only stratum-level features | `bias`, `hour_block`, `planned_workload_pre` | `propensity/observation.py:39-43`; `window_runner.py:319-339, 698-706` |
| C8 | a per-unit covariate that varies inside a stratum exists and is dense | `time_index`: 12–36 distinct values per stratum | `data/processed/*/atomic_units.parquet` |
| C9 | `q^use` is per client-window, never per unit | 1105 distinct values on `[0, 0.9815]`; 0 client-windows with two values | record L7 |
| C10 | `RAVEN-SimOracle` flips **both** propensities, not just `q` | `uses_oracle_propensity` gates `rec.oracle_q` (`window_runner.py:426-430`) **and** `p_obs_true_by_unit` (`:707-727`) | `aggregation/method_policy.py:161-172` |
| C11 | no oracle-`p`-only arm exists | one flag covers both sites | C10 |
| C12 | the published family costs 3.54 h for 560 runs | SensorScope ≈ 0.45 min per method-seed, U-Air ≈ 0.26 | summed `runtime_seconds` in `runs/*/*/final_metrics.json` |

### 1.1 What C1–C7 mean for the correction

Within one client-window every risk unit belongs to one stratum, every stratum has exactly one
group, and `π^opp`, `π^tar` and `p̂` all depend on the stratum only through quantities that the
block and the group already determine. So the stage-1 weight

```text
a_s = min{a_max, ζ̂_s / max(p̂_s, p_min)},   ζ̂_s = π^tar_{g(s)} / π^opp_s
```

takes **at most four distinct values per client-window, one per UTC block**, and the model's three
features span exactly that dependence. The correction therefore estimates a four-parameter object
whose functional form the model can track, and it can express nothing below the stratum. That is
the sharpest available statement of H-A: the correction problem is not merely easy, it is
low-dimensional *and* correctly specified, and no within-stratum component exists to be recovered.

The one honest qualification: the truth is a two-level step in the block index and the model is a
smooth monotone function of the same index, so the fit is functional-form-approximate rather than
exact. The residual is curvature error over four block values with three free parameters, not a
missing covariate.

### 1.2 A correction to the record that this pass found

C10 means **`RAVEN-SimOracle` is a joint oracle** (true `p` *and* true `q`). Record §3 T3 reads its
`+0.008%` / `−0.030%` as *"replacing the estimated `q` by the true `q`"* and concludes that "the
layer the paper devotes most of its machinery to estimating is close to irrelevant". The measured
contrast is real and reproduces to within 0.002 percentage points (this pass, paired over the same
20 seeds: `+0.008%` SensorScope, `−0.028%` U-Air), but the **attribution to `q` alone is
unsupported**: the null could be carried by `p`, by `q`, or by both. T3's conclusion (root defect 3
stands) is unaffected and in fact strengthened; its wording is not. Proposed record change, pending
the user's decision:

```text
T3 — the plug-in propensity pair is not the bottleneck.  Replacing *both* estimated propensities
by their true values (RAVEN-SimOracle: uses_oracle_propensity gates the q map at
window_runner.py:426-430 and the atomic p map at :707-727) changes RMSE_mu by +0.008% and -0.028%.
No arm in the repository separates the p and q components; F-1 adds one.
```

---

## 2. What the manipulation must break

Three factors determine `a_s`: `π^tar_{g(s)}`, `π^opp_s`, and `p_s`. C1 removes `π^tar` from the
list of usable levers, because the target is defined on the group and the stratum cannot move
inside a group. That leaves two, and each breaks a different branch:

| arm | lever | breaks | models the |
|:---|:---|:---|:---|
| **F-1-O** (primary) | `p_obs` depends on `time_index` inside the stratum | the observation model, and assumption A1's within-stratum exchangeability | device / connectivity / duty-cycle heterogeneity |
| **F-1-R** (secondary) | `π^opp` depends on the day type inside the group | the design-ratio branch, which the main tables currently assume away by A1 | real mobility that is not block-periodic |

F-1-O is primary because it is minimal (one generator argument, no new opportunity machinery),
because C8 shows the covariate is dense, and because it is the only arm that can move `a` below the
stratum, which is where C7 says the model is blind.

---

## 3. Manipulation specification

### 3.1 F-1-O: within-stratum observation propensity

For each risk unit `i` in stratum `s`, with `b = block(s)`:

```text
z_i = tercile rank of time_index inside s          (z_i in {-1, 0, +1}, balanced within s)
p_obs(i) = clip( sigmoid( beta_0(b) + theta_O * z_i ), p_gen_min, p_gen_max )      p_gen_min = 0.05
beta_0(b) solved by bisection on the block pool:
        mean over train units of block b of p_obs(i) = r_b
        r_b = 0.1925 for b in {2,3}, 0.35 otherwise          (the published values)
```

- The bisection reuses the E2 apparatus as an algorithm: `solve_observation_intercept` and
  `compute_observation_probabilities` (`e2/generators.py:101-184`), with the mean taken over the
  block pool instead of over the E2 atom mass. Nothing else from E2 is imported.
- **The marginal is preserved by construction, per block.** Realized observed counts will still
  differ from the published trace; that is a property of the manipulation, not a defect, and is
  reported per arm (threat T1 below).
- `theta_O ∈ {0.5, 1.0, 1.5}` with **`theta_O = 1.0` pre-registered as primary**, matching the
  frozen E2 profile `PROFILE-S2` (`kappa_p = 1.0`, `configs/e2_numeric/strength_profile_registry.yaml`).
  The sweep is reported as a dose-response, and the decision uses `theta_O = 1.0` only.
- Expected effect on the propensity range: with the terciles balanced, `theta_O = 1.0` and block
  rate `0.1925` put the three terciles near `0.35 / 0.16 / 0.07` (solved from
  `sigmoid(beta_0 + z)` with `beta_0` matched to the block mean). The `p_gen_min = 0.05` clip
  therefore does not bind, but the low tercile sits only `1.3×` above it, so the A5 row
  `min p^obs ≥ p_min` is re-audited and reported for every dose rather than assumed.
- Everything else is frozen: the opportunity law, the target map, the splits, `q^use` and the whole
  arrival process, `s_max`, the risk-set size `min(4, |support|)`, and the seeds 30001–30020.

### 3.2 F-1-R: within-group opportunity tilt (secondary)

For each client, add a day-type term to the block score and solve `gamma` so that the client's
expected observed mass is unchanged:

```text
score_s(gamma) = exp( -theta_align * 1{b(s) in {2,3}} + gamma * 1{weekend(s)} )
pi^opp(gamma)  = normalize over the client's strata
gamma solved s.t.  sum_s pi^opp_s(gamma) * p_s  =  sum_s pi^opp_s(0) * p_s
```

`theta_align = 1.25` stays at its published value. `gamma` is reported, not pre-set. This arm is
secondary because it needs a new normalisation path and because its `gamma` is data-dependent; it
is run only if F-1-O returns a null and the question "was the design-ratio branch ever stressed?"
still needs an answer.

---

## 4. Arms and method matrix

Every cell uses the frozen seeds 30001–30020, the frozen splits, the frozen target maps and the
published training configuration.

| arm | trace | methods | status |
|:---|:---|:---|:---|
| **N** (published) | `e3_formal_runs_r1/eventtraces/**` | raven, twostage_hajek, fedavg_window, local_hajek, raven_simoracle | **reuse; no new run** |
| **N + oracle-p** | same trace | `raven_oracle_p` (new) | new run, 1 cell |
| **S** (F-1-O, `theta_O = 1.0`) | new traces | raven, `raven_oracle_p`, twostage_hajek, fedavg_window, local_hajek | new runs, 5 cells |
| **S dose** (`theta_O = 0.5`, `1.5`) | new traces | raven, `raven_oracle_p` | new runs, 2 cells, diagnostic only |
| **R** (F-1-R) | new traces | raven, `raven_oracle_p`, twostage_hajek, fedavg_window, local_hajek | conditional on an S null |

### 4.1 The one code change F-1 requires

`uses_oracle_propensity` gates two independent sites (C10, C11). Split it:

```text
MethodPolicy:  uses_oracle_p: bool = False      # window_runner.py:707-727  (atomic p_obs_true_by_unit)
               uses_oracle_q: bool = False      # window_runner.py:426-430  (rec.oracle_q)
               uses_oracle_propensity -> kept as a read-only property returning uses_oracle_p or uses_oracle_q,
                                          only so existing call sites keep working until both are migrated
POLICY_MAP:    "raven_simoracle": both True                     (unchanged behaviour)
               "raven_oracle_p":  uses_oracle_p=True, uses_oracle_q=False, otherwise identical to raven_mcs
```

`raven_oracle_p` is a diagnostic arm, not a paper method: it appears in no manuscript table.

### 4.2 Baselines and why these

- `twostage_hajek` is `_normalize(β̂)` (`aggregation/methods.py:314-320`): the published reference
  with P2 off, sharing RAVEN's exact `β̂`. It is the only baseline that isolates the correction from
  P2 and debt, which is what F-1 is about.
- `fedavg_window` and `local_hajek` are the two uncorrected families the paper already reports.
- `raven_oracle_p` is the headroom probe and has no published counterpart.

---

## 5. Endpoints and pre-registered decision rules

Decision endpoints, in order. Holm is applied within the family {E1, E2} × {SensorScope, U-Air} at
`α = 0.05`; nothing else enters the family.

**E1 (primary) — headroom of the observation correction, within the S trace.**
`Δ_oracle = RMSE_μ(raven) − RMSE_μ(raven_oracle_p)`, paired per seed, same trace for both arms.

| outcome | reading |
|:---|:---|
| `Δ_oracle > 0.5%` | the harder regime *did* create recoverable mass error: H-A supported, and the next question is whether any estimable model captures it |
| `|Δ_oracle| ≤ 0.5%` | even an exact propensity buys nothing under a within-stratum, label-correlated selection law: H-A's "the construction is the cause" reading is **refuted**, and H-B (endpoint insensitivity) is what remains |

**E2 (secondary, the criterion as recorded) — does RAVEN's lead over baselines grow?**
`[RMSE_μ(raven) − RMSE_μ(baseline)]_S − [RMSE_μ(raven) − RMSE_μ(baseline)]_N`, paired by seed, for
`baseline ∈ {twostage_hajek, fedavg_window, local_hajek}`.

| outcome | reading |
|:---|:---|
| any baseline shows a ≥ 0.5% *improvement in RAVEN's favour* | the as-published construction was suppressing a real advantage |
| all stay ≤ 0.5% | the record's stated refutation of H-A |

**E3 (diagnostic, never decisive).** `Δ_group`, `Δ_c-s`, `clip_rate_stage1`, realized observed-unit
counts per arm, and the re-run A5/A6 audit rows (`min p^obs`, `min q^use` on active support).

### 5.1 Measured power — 20 seeds are enough

Paired statistics over the 20 published seeds (`runs/*/*/final_metrics.json`, `RMSE_mu`). MDE is
the two-sided 80 %-power minimum detectable effect at `n = 20`; `base` is the second method's mean.

| dataset | pair | mean diff | paired sd | MDE | MDE as % of base |
|:---|:---|---:|---:|---:|---:|
| SensorScope | raven − raven_simoracle | +0.008 % | 0.0056 | 0.0035 | **0.044 %** |
| U-Air | raven − raven_simoracle | −0.028 % | 0.0032 | 0.0020 | **0.166 %** |
| SensorScope | raven − twostage_hajek | +0.090 % | 0.0195 | 0.0122 | 0.154 % |
| U-Air | raven − twostage_hajek | −2.043 % | 0.0175 | 0.0109 | 0.900 % |
| SensorScope | raven − fedavg_window | −0.011 % | 0.0079 | 0.0049 | 0.062 % |
| U-Air | raven − fedavg_window | +0.242 % | 0.0120 | 0.0075 | 0.631 % |

The 0.5 % threshold sits 3–11× above the MDE of the primary contrast, so F-1 is not power-limited:
a null on E1 would be a null, not an underpowered test. Two caveats to carry into the analysis:
the MDEs are estimated on the published trace, and the S trace will pair the two oracle arms on the
*same* trace (so the tight pairing is preserved) while cross-trace comparisons in E2 pair only by
seed. The observed paired sd must be reported for every F-1 contrast; if it exceeds twice the
table above, increase seeds rather than reinterpret the decision.

### 5.2 Ceilings that bound the possible outcome

Measured on the published traces, so any F-1 effect is read against them:

| reference | SensorScope | U-Air |
|:---|---:|---:|
| raven | 7.9380 | 1.1911 |
| central_delivered (delivered data, no correction) | 7.9291 (−0.11 %) | 1.1782 (−1.08 %) |
| central_all (all observations, no delivery restriction) | 7.6004 (−4.25 %) | 1.0556 (−11.4 %) |

The reweighting family can at most approach `central_delivered`; the 4.25 % / 11.4 % gap to
`central_all` is the undelivered-sample ceiling (record T2) and is unreachable by any weighting.
This is why **U-Air is the sensitive block and SensorScope the insensitive one, and they are never
pooled.** Under F-1 the delivered set changes, so these ceilings are sensitivity guidance for the
pre-registration, not fixed bounds; each S arm recomputes its own `central_delivered` row.

---

### 5.3 Stage A result — the measured ceiling map (executed 2026-09-24)

Before implementing anything, the ceiling was read off the existing frozen artifacts: the `raven`
cell (`artifacts/e3_formal_runs_r1/runs`) against the E4 one-factor ablations
(`artifacts/e4_core_mechanism_ablation_r1/runs`), paired on the 20 formal seeds. `delta%` is
(ablated − reference) / reference; `sig` is |mean| / standard error of the paired difference.

**Anchor correction (found 2026-09-24, after this section was first written).** `raven` is not the
paper's method on U-Air. It is `_RAVEN_CORE` with `gate_mode="always_on"`, so its design ratio always
applies, and no φ is computed anywhere in the E3 runner path. Table III reports `RAVEN-NoDesign`
U-Air = **1.1131** as the table method and labels `raven`'s **1.1911** as `RAVEN-Design (forced)`
(`main.tex` 1754–1757, 1821–1822); 1.1131 is exactly `runs/uair/raven_wo_design`. The SensorScope
anchor is correct (`RAVEN-Design` = `raven` = 7.9380). So the U-Air column below is a **forced-Design
factorial**, and the one row that looks like an opportunity is not one: see the withdrawal note after
the table.

**SensorScope** (full RAVEN `RMSE_μ` = 7.9380)

| module changed | `RMSE_μ` | `Δ_group` | `Tail_RMSE` | sig |
|:---|---:|---:|---:|---:|
| remove design (ζ̂ + Gate) | +0.005% | +1.237% | +0.005% | 0.3 / 9.2 |
| remove observation IPW | +0.012% | +0.096% | +0.011% | 2.5 / 2.9 |
| remove usable IPW | +0.012% | +0.026% | +0.012% | 2.5 / 0.8 |
| **remove Inst (P2 group term)** | **−0.090%** | +2.110% | −0.085% | 1.6 / 7.7 |
| remove debt | +0.000% | +0.014% | +0.000% | 0.1 / 13.8 |
| oracle p + q | −0.008% | +0.200% | −0.008% | 0.5 / 1.5 |

**U-Air** (full RAVEN `RMSE_μ` = 1.1911)

| module changed | `RMSE_μ` | `Δ_group` | `Tail_RMSE` | sig |
|:---|---:|---:|---:|---:|
| **remove design (ζ̂ + Gate)** | **−6.553%** | **−6.943%** | **−6.875%** | 10.0 / 12.7 |
| remove observation IPW | −0.010% | +0.123% | −0.010% | 1.0 / 6.3 |
| remove usable IPW | +0.024% | +0.014% | +0.025% | 1.1 / 0.5 |
| remove Inst (P2 group term) | +2.086% | +2.494% | +2.176% | 6.4 / 6.4 |
| remove debt | +0.001% | +0.004% | +0.001% | 0.7 / 8.1 |
| oracle p + q | +0.028% | −0.017% | +0.030% | 0.5 / 0.3 |

Reference ceilings from the same artifacts, against the `raven` cell: the reachable-by-any-weighting
bound (`Central-Delivered`) is `−0.112%` (SensorScope, sd 0.082) and `−1.100%` (U-Air, sd 0.122); the
undelivered-sample bound (`Central-All`) is `−4.442%` and `−12.841%`, and no weighting reaches it.
The U-Air figures inherit the anchor caveat and are corrected in item 3 below.

**What this says about where the ceiling is.**

1. On SensorScope **every module is worth at most 0.09%**, and the only non-trivial one (Inst) is
   worth a *negative* amount: removing it helps. This anchor is correct.
2. On U-Air **the one large number is not headroom.** The −6.553% "remove design" row is the φ-based
   branch assignment the paper already makes: Table III deploys `RAVEN-NoDesign` (1.1131) on U-Air
   and reports the forced-Design row (1.1911) beside it as a diagnostic. Presented as "deletion buys
   6.55%" it was wrong, and the claim is withdrawn.
3. Re-anchored to the deployed method, the U-Air reference bounds also flip: `Central-Delivered`
   (1.1782) is **5.85% worse** than the table method, not 1.10% better, and `Central-All` (1.0556) is
   5.17% better and unreachable by reweighting. On U-Air the deployed method already beats
   uncorrected central training and every federal baseline in the tree (1.1882–1.2160).
4. The entire propensity family (observation IPW, usable IPW, exact p and q) moves `RMSE_μ` by
   **at most 0.03%** on either dataset, in either direction. `RAVEN-SimOracle` is worth 0.008% and
   −0.028%; removing the observation weighting outright is worth 0.012% and −0.010%. This is the
   bound F-1 was designed to test, and on U-Air it is a statement about the forced-Design base
   because the E4 tree carries no design-removed module factorial.
5. U-Air `remove Inst` reproduces `twostage_hajek` to four decimals (both 1.2160) inside the forced
   factorial, so on U-Air the whole RAVEN-versus-`β̂` difference is the P2 group term, and the same
   term has the opposite sign on SensorScope.

**Consequence for F-1.** The manipulation F-1-O applies changes the *difficulty* of the observation
weighting. Item 4 bounds what the observation weighting can be worth on these endpoints even when
it is exact or absent: ≤0.03%. The most favourable reading of F-1-O is therefore that a harder
construction lets the correction recover at most the difference between a *misspecified* and an
*exact* propensity on an endpoint that item 4 shows is nearly weight-blind. The pre-registered null
on E1 is the expected outcome, and H-A would be refuted at the cost of the runs. And the route the
work does *not* open is the one this section originally pointed at: on U-Air the design branch is
already removed by the paper's own rule, so there is no 6.55% sitting on the table.

These Stage A numbers duplicate Table IV's Design-removal and Inst rows; they are consolidated here
with σ and with all five modules in one place.

### 5.4 Stage B result — E1 executed, and H-A is refuted

Executed 2026-09-24. 160 new runs: two arms × {`raven`, `raven_oracle_p`} × {SensorScope, U-Air} ×
20 paired seeds. Arm N (`θ_O = 0`) reuses the published traces; arm S is the F-1-O trace at
`θ_O = 1.0`. Everything else frozen: seeds 30001–30020, splits, target maps, opportunity law,
risk-set size, stage-2 usable process, training configuration.

**Harness reproduction (gate, passed exactly).** Arm N `raven` reproduces the published `raven`:
`RMSE_μ` 7.937989 vs 7.937989 (SensorScope) and 1.191114 vs 1.191114 (U-Air), i.e. **0.0000%** on
both datasets. The new execution path is the published path.

**Manipulation integrity (gate, passed).** `θ_O = 1.0` preserves the per-block marginal to machine
precision: the pool-weighted mean of `p` equals 0.350000 and 0.192500 on all eight block cells with
`|Δ| ≤ 5.6e-17`. It moves the propensity *inside* the stratum: 2.76–2.83 distinct `p` per stratum
(maximum 3) against exactly 1 for the published construction. Minimum `p` is 0.0671, above
`p_min = 0.05`. `clip_rate_stage1` does not rise (SensorScope 0.000421 → 0.000234; U-Air 0.025958 →
0.022612) and `ESS` moves by ≤1.8%, so the test is not measuring a clip or a sample-size collapse.

**E1 (primary).** `Δ_oracle` = `RMSE_μ(raven) − RMSE_μ(raven_oracle_p)`, paired, same trace.

| dataset | arm | `Δ_oracle` | paired sd | MDE | σ |
|:---|---:|---:|---:|---:|---:|
| SensorScope | N (`raven` = the table method) | −0.005% | 0.0011 | 0.009% | 1.7 |
| SensorScope | S (`θ_O = 1.0`) | **+0.104%** | 0.0079 | 0.062% | **4.7** |
| U-Air | N (`raven` = forced Design, not the table method) | +0.017% | 0.0004 | 0.020% | 2.3 |
| U-Air | S (`θ_O = 1.0`) | **−0.251%** | 0.0065 | 0.342% | **2.1** |

`Tail_RMSE` tracks `RMSE_μ` to two decimals in every row (SS −0.005%, +0.100%; U-Air +0.017%,
−0.262%). `Δ_group` is not significant on either dataset (−0.150% at 1.7 σ, −0.095% at 1.6 σ).

**Anchor caveat on the U-Air rows.** Both arms ran the `raven` policy. On SensorScope that *is* the
paper's table method (`RAVEN-Design`). On U-Air it is not: Table III's U-Air method is
`RAVEN-NoDesign` = 1.1131 = `runs/uair/raven_wo_design`, while `raven` = 1.1911 is the row the paper
labels `RAVEN-Design (forced)`. The U-Air `Δ_oracle` figures therefore describe the forced-Design
configuration, not the deployed one. The verdict is untouched, because `Δ_oracle` is a within-trace
contrast between two policies that differ only in the propensity map, but the U-Air number must not
be quoted as a property of the paper's U-Air method. Re-anchoring it needs a
`raven_wo_design_oracle_p` policy and a further 40 cells; that is not run.

**Verdict, by the pre-registered rule.** The rule was: `|Δ_oracle| ≤ 0.5%` refutes H-A. Both
datasets and both predictive endpoints fall inside that bound, the larger of the two at 0.251%, and
on U-Air the sign is negative. **H-A is refuted.** The constructed block-level regime is not what
caps the gain at the paper's own 0.5% threshold: even a deliberately harder, within-stratum,
label-correlated selection law leaves an exact observation propensity worth 0.10% on SensorScope,
and on U-Air the exact propensity is *worse* than the estimated one by 0.25%.

**What the manipulation did establish.** Between the two arms the value of an exact propensity rose
15–21× (SensorScope 0.005% → 0.104%, U-Air 0.017% → 0.251%). H-A's mechanism is real: the published
construction does suppress propensity headroom. It suppresses a quantity whose scale, after a 20×
amplification, still sits below the threshold that matters. Direction confirmed, magnitude refuted.

**T3 is now decomposed rather than asserted.** Under the published construction the observation
member alone is worth −0.005% (SensorScope) and +0.017% (U-Air) on `RMSE_μ`; the joint oracle is
+0.008% and −0.028%, so the usable member accounts for roughly +0.013% and −0.045%. Neither member
is the bottleneck.

**Not run, and why that is safe.** E2 needs uncorrected baselines on the S trace (120 further runs)
and the dose sweep needs `θ_O ∈ {0.5, 1.5}` (80 runs). The design's own stop rule applies: E1 is
decisive, so the sweep is not run for completeness. E2 remains available, and its absence does not
touch the verdict, which is an E1 statement.

Artifacts: `artifacts/e3_f1_score_dependent_r1/` (arm N) and `artifacts/e3_f1_theta1_r1/` (arm S);
driver `scripts/run_e3_f1.py`; readout `_tmp_ref/f1_readout.py`; generator validation
`_tmp_ref/f1_generator_check.py`. No file under `artifacts/e3_formal_runs_r1/` was written.

---

## 6. Implementation checklist

| # | item | file |
|:--|:---|:---|
| 1 | generator with the `theta_O` argument, the `time_index` tercile and the per-block bisection; new `GENERATOR_VERSION` | `e3/real_runner/generator_r3_score.py` (new) |
| 2 | keep writing `p_obs_true_by_unit` and `atomic_p_obs_true.parquet`; the oracle-p arm reads them | same |
| 3 | split `uses_oracle_propensity` into `uses_oracle_p` / `uses_oracle_q`; add `raven_oracle_p` | `aggregation/method_policy.py`; `training/window_runner.py:426-430, 707-727` |
| 4 | freeze `theta_O`, the tercile rule, `p_gen_min/p_gen_max`, the bisection tolerance and the block rates | `configs/frozen/e3_f1_score_dependent/*.yaml` (new) |
| 5 | new artifact root; **no write to `artifacts/e3_formal_runs_r1/`** | `artifacts/e3_f1_score_dependent_r1/` (new) |
| 6 | run driver reusing the published config snapshot and seeds; assert the config diff against `E3_main_complete.yaml` is exactly the new arm | `scripts/run_e3_f1.py` (new) |
| 7 | pre-flight checks before any headline run: realized block marginals equal the published ones to tolerance; `min p^obs ≥ p_min`; A6 rows re-audited; `clip_rate_stage1` no higher than published; the harness reproduces `raven = 7.9380 / 1.1911` on the N trace | `tools/` |
| 8 | confirm which design-ratio form the arm exercises (`zeta_hat_stratum` general form at `window_runner.py:317` vs the A1 simplification at `main.tex:1496-1499`); record it, because F-1-O makes A1 false by construction | read-only check |

---

## 7. Cost and execution order

Measured unit costs from the published family (C12): SensorScope ≈ 0.45 min per method-seed,
U-Air ≈ 0.26 min per method-seed.

| stage | cells | runs | estimate |
|:---|:---|---:|---:|
| pre-flight (1 seed, both datasets) | 7 | 14 | ≈ 5 min |
| N + oracle-p | 1 | 40 | ≈ 14 min |
| S (`theta_O = 1.0`) | 5 | 200 | ≈ 71 min |
| S dose (`theta_O = 0.5`, `1.5`) | 2 | 80 | ≈ 28 min |
| R (conditional) | 5 | 200 | ≈ 71 min |
| **total, with R** | | **534** | **≈ 3.2 h** |
| **total, without R** | | **334** | **≈ 2.0 h** |

Order: pre-flight → N + oracle-p (must reproduce the published numbers, otherwise the harness is
suspect) → S at the primary dose → E1 read → then decide on the dose sweep and R. Stop after E1 if
E1 is decisive; do not run the sweep for completeness.

---

## 8. Threats to validity

| # | threat | mitigation, or why it does not invalidate the test |
|:--|:---|:---|
| T1 | the S trace delivers a different observed set, so the arms no longer share data with the published table | E1 is *within* the S trace (both arms see identical data); E2 is reported per arm with delivered counts, and the S arm's own `central_delivered` row is recomputed |
| T2 | positivity: the manipulation lowers the minimum propensity | the per-block bisection holds the marginal and the clip is inactive at `theta_O = 1.0`; the A5 row `min p^obs ≥ p_min = 0.05` is re-audited and reported |
| T3 | the `a_max = 40` ceiling or the `p_min = 0.05` floor could bind and truncate the correction, turning the test into a clip test | `clip_rate_stage1` is compared against its published value; a rise means the arm is measuring the clip, and the dose is reduced |
| T4 | the oracle-p arm is new code | it reuses the existing SimOracle injection path, which already raises if `p_obs_true_by_unit` is missing; a unit test asserts the injected vector equals the generator's, and the pre-flight asserts `raven_oracle_p` differs from `raven` by more than zero on at least one seed |
| T5 | scope: F-1 moves only the `O` axis | `R` stays always-on and `q^use` unchanged, so a null bounds the `O` component of H-A only. The `R`/design axis is what F-1-R addresses |
| T6 | block asymmetry | U-Air and SensorScope are never pooled; the pre-registration names U-Air as the sensitive block on the basis of the measured ceilings in §5.2 |
| T7 | multiplicity | the Holm family is exactly {E1, E2} × {2 datasets} = 4 tests, fixed before the run; the dose sweep and E3 rows are exploratory and labelled as such |
| T8 | the new trace is a new protocol block, and the paper's tables must not silently absorb it | the arm is reported in the record only. If F-1 is later written into the manuscript it enters as a new subsection with its own caption, and the P0 scoping sentence of §VII-A.2 is re-checked against it |

---

## 9. Result tables

Filled from executed runs. `TBD` marks a cell that was deliberately not run.

**Table F-1a — headroom of the observation correction (E1).**

| dataset | trace | `RMSE_μ` raven (plug-in p) | `RMSE_μ` raven (exact p) | `Δ_oracle` | paired sd | MDE | σ | n |
|:---|:---|---:|---:|---:|---:|---:|---:|---:|
| SensorScope | published (θ = 0) | 7.9380 | 7.9384 | −0.005% | 0.0011 | 0.009% | 1.7 | 20 |
| SensorScope | F-1-O (θ = 1.0) | 7.9809 | 7.9726 | **+0.104%** | 0.0079 | 0.062% | **4.7** | 20 |
| U-Air | published (θ = 0) | 1.1911 | 1.1909 | +0.017% | 0.0004 | 0.020% | 2.3 | 20 |
| U-Air | F-1-O (θ = 1.0) | 1.1880 | 1.1910 | **−0.251%** | 0.0065 | 0.342% | **2.1** | 20 |

For reference, the *joint* oracle (`raven_simoracle`, exact p **and** q) is +0.008% on SensorScope
and −0.028% on U-Air against the same plug-in cells, which places the usable member's share at about
+0.013% and −0.045%.

**Table F-1b — does RAVEN's lead move (E2)? Not run.** Uncorked baselines on the S trace would be
120 further runs; the design's stop rule applies because E1 is decisive.

**Table F-1c — manipulation integrity (gate).**

| dataset | θ | per-block marginal of `p` vs published | distinct `p` per stratum | `min p` | `clip_rate_stage1` (N → S) | `ESS` (N → S) |
|:---|:---|---:|---:|---:|---|---|
| SensorScope | 1.0 | 0.350000 / 0.192500, `|Δ| ≤ 5.6e-17` | 2.76 mean, 3 max (published: 1) | 0.0671 | 0.000421 → 0.000234 | 1.672 → 1.667 |
| U-Air | 1.0 | 0.350000 / 0.192500, `|Δ| ≤ 5.6e-17` | 2.83 mean, 3 max (published: 1) | 0.0671 | 0.025958 → 0.022612 | 1.680 → 1.649 |

The hairline threshold in the endpoint comparison is a hairline here: `max{|p_min|}` is 0.0671
against `p_min = 0.05`, so A5's positivity clause survives the manipulation with a 1.34× margin.

---

## 10. What F-1 cannot settle

- It cannot raise the ceiling: if the endpoint is insensitive to the composition (record T4: P2
  moves `α` by L1 0.337 with `RMSE_μ` flat), no propensity manipulation will produce a large
  `RMSE_μ` effect, and F-1 would return a null that supports H-B rather than refuting H-A.
- It says nothing about the `R`/design axis unless F-1-R is run, and nothing about `q^use`, which
  C9 shows has no unit-level component to stress.
- It is a simulation study on constructed selection. A positive E1 would show that the *published*
  regime hides headroom; it would not show that real selection has that shape.
- It does not touch the target-provenance defect (record §1); `RMSE_μ` remains evaluation-derived
  in every F-1 arm.

---

## 11. Missing values and no-fabrication status

Executed 2026-09-24. Sections 5.3, 5.4 and 9 report measured values from runs that exist:
`artifacts/e3_f1_score_dependent_r1/` (arm N) and `artifacts/e3_f1_theta1_r1/` (arm S), 160 cells
over 20 paired seeds, read out by `_tmp_ref/f1_readout.py`. Every number quoted from the published
evidence base stays attributed to `artifacts/e3_formal_runs_r1/`. The only cells reported as `TBD`
are E2 and the θ sweep, and section 5.4 states why they were not run. The `raven_oracle_p` policy,
the generator, the driver and the trace guard now exist; the run-level detail is in
`f1_run_status.jsonl` under each arm.

Next CCFA owner: `ccf-visual-composer` only if F-1 enters the manuscript as a table →
`ccf-paper-writer` for that
prose. The record entry for F-1 should be updated to point here and to carry §0 and §1.2.

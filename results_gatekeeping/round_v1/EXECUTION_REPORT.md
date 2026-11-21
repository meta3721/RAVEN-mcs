# EXECUTION_REPORT — A1 gatekeeping (Part A only)

Round directory: `results_gatekeeping/round_v1/`
Executable protocol: `PROTOCOL.md` — byte-identical copy of the execution prompt, 11 336 bytes,
sha256 `916b55766f24b4b5685e59418fe2140ad1e74e2c178ed0f75ba375c7feb8324e`, verified equal to
the source attachment after copying.
Preregistration: `PREREG.md`. Its sha256 **as first written, before any computation**, is
`c30ea27366df3217008aa26796c553d5d908c31b71b072728cd657e9f43e76d8`; both that hash and the
operating protocol's are in `MANIFEST.sha256`, written first.

### 0.1 Registration history (declared)

`PREREG.md` was amended twice **after** it was hashed but **before any A1 value was
computed, read or reported** (times t1), and the timeline section itself was added at t2.
Both amendments are recorded in `PREREG.md` §0 and in the `REGISTRATION TIMELINE` block of
`MANIFEST.sha256`:

* **(a)** the H2/H3 upper/lower bound was changed from a basic bootstrap percentile to the
  **Wilcoxon-inverted distribution-free bound expressed as explicit Walsh order statistics**
  — the estimator family the protocol itself names for A1 — with the bootstrap and the
  normal approximation demoted to reported secondaries. This came from re-reading the
  protocol text and from internal consistency checks on the inversion.
* **(b)** the City Scanner within-trace variance scenarios were restated as the admissible
  range `S0`/`S1`/`S2` with `σ_W` defined precisely as the within-trace paired-difference SD
  (the quantity Part B's B0-b would measure). This came from noticing that the only
  available pilot contrast measures an arm difference on shared traces, not a model-seed
  replicate.

**No decision-relevant element was changed at any point**: the H1 → H2 → H3 sequence,
δ = 0.5 % for SensorScope and U-Air, δ_CS = 2 %, the graphical-Holm rule within (never
across) datasets, the arm list, the seed/trace sets, the "post hoc descriptive" labelling,
the `B = 10 000` / `seed = 20261003` bootstrap settings and the no-32005 sensitivity rule
are exactly as the protocol states them, and they are identical at t0, t1 and t2. The
amendment changed how a preregistered bound is computed and named, not what is tested, at
which margin, on which data. A file cannot contain the hash of its own final bytes, so the
executed (t2) hash of `PREREG.md` is recorded in `MANIFEST.sha256` and
`A1_PROVENANCE.json`, not inside `PREREG.md` itself.

Discipline: `CCFA-Skills/ccf-experiment-designer`. Every cell below is produced by
`A1_ANALYSIS.py` from read-only inputs (input sha256 in `A1_PROVENANCE.json`). Nothing is
imputed; no quantity was substituted for another.

**Round executed: A1.0 → A1.1 → A1.2 → report. No training was run. Part B was not started.**

---

## 0 Scope actually executed, and what was not

| protocol item | status in this round | reason |
|---|---|---|
| §1 A1.0 preregistration | **done** — `PREREG.md` + `MANIFEST.sha256` before computing | required |
| §1 A1.1 descriptive hierarchy | **done** — `A1_DESCRIPTIVE.csv` (+ `A1_DESCRIPTIVE_DETAIL.csv`) | required |
| §1 A1.2 power table | **done** — `A1_POWER.csv` | required |
| §1 sensitivity rule (no trace 32005) | **done** — `A1_SENSITIVITY_NO32005.csv` | required |
| §2 Part B (B0-a, B0-b, B1, B2, B3) | **NOT RUN** | the exact authorization phrase `授权 C1 训练` was not given |
| §3 Part C | **not in this round** | out of scope by the prompt |
| §4 outputs `B0_REPRO.json`, `B0_SEED32005_PROBE.csv`, `C1_MAPS.json`, `C1_RUNS.csv`, `C1_PRIMARY.json`, `C1_SECONDARY.csv`, `C1_A1_CHAINS.csv`, `C1_SENSITIVITY_NO32005.csv` | **NOT PRODUCED** | they are Part-B artefacts; Part B was not authorized |

No file was created or modified outside `results_gatekeeping/round_v1/`. `src/`, the
manuscripts, every pre-existing results directory, `tdrive_protocol_seal_r1/` and
`artifacts/` were read-only throughout. X1, PATH_A NO2, full `build()` and git were not
touched. No `scripts/c1_deletion_driver.py` was created.

## 1 A1.0 — the preregistered hierarchy and margins, quoted verbatim

From `PREREG.md` §3 (fixed at full α = 0.05, one chain per `(dataset, arm)` against
`fedavg_window`, each later hypothesis tested only if the previous one is rejected):

> 1. **H1 (structure).** `Delta_group(arm) < Delta_group(fedavg_window)`.
>    Statistic: paired Wilcoxon signed-rank test on `T_s` (one-sided,
>    `alternative = "less"`, i.e. `median(T) < 0`), n = 20 (SensorScope, U-Air) / n = 10
>    (City Scanner).
> 2. **H2 (prediction, non-inferiority).** `RMSE_mu(arm)/RMSE_mu(fedavg_window) − 1 < δ`.
>    Decision statistic: the **Hodges–Lehmann (HL) estimate** `θ̂ = median over all pair
>    averages (d_i + d_j)/2` of the paired relative differences, plus the **upper bound of
>    its one-sided 95 % confidence interval** `U`. … **Reject H2 iff `U_wilcox < δ`**
> 3. **H3 (prediction, superiority).** The same estimator family excludes 0 from below:
>    **H3 tested only if H2 was rejected in the same chain** … **H3 rejected iff
>    `L_wilcox > 0`**.

α across chains (from `PREREG.md` §3, verbatim):

> Chains are the `(dataset, arm)` pairs. Within one dataset the chains form one
> **Bretz–Maurer–Brannath–Posch graphical family** with *equal initial weights*
> `w = 1/K` (`K` = number of chains in that dataset: 2 for SensorScope, 2 for U-Air,
> 1 for City Scanner) and the **Holm transition matrix** `g_ij = 1/(K−1)` for `i ≠ j`,
> `g_ii = 0`. A chain that completes (all hypotheses tested) releases its weight to the
> remaining chains; a chain whose *current* hypothesis is not rejected is stopped and its
> weight is propagated. … **Datasets are never pooled**; City Scanner is a family of size 1.

Margins (from `PREREG.md` §4, verbatim):

> | dataset | margin | status |
> |---|---|---|
> | SensorScope | δ = 0.5 % | unchanged from v5 |
> | U-Air | δ = 0.5 % | unchanged from v5 |
> | City Scanner | **δ_CS = 2 %** | declared in this file **before** any A1 number; justified by the 13 % paired SD at n = 10; **never revisited** |

Sensitivity rule (from `PREREG.md` §6, verbatim):

> **Every estimate in this round is recomputed with trace/model seed 32005 excluded** …
> **The exclusion is a sensitivity analysis and is never primary.**

### 1.1 Realised α allocation (graphical Holm, per dataset, never pooled)

| dataset | chain order executed | step | α allocated | p | rejected |
|---|---|---|---|---|---|
| SensorScope | `raven` | H1 | 0.0250 | 9.537e-07 | yes |
| SensorScope | `proj_beta` | H1 | 0.0500 | 9.537e-07 | yes |
| SensorScope | `proj_beta` | H2 | 0.0500 | 1.286e-56 | yes |
| SensorScope | `raven` | H2 | 0.0500 | 1.225e-119 | yes |
| SensorScope | `raven` | H3 | 0.0500 | 0.7392 | no |
| SensorScope | `proj_beta` | H3 | 0.0500 | 0.7848 | no |
| U-Air | `raven` | H1 | 0.0250 | 9.537e-07 | yes |
| U-Air | `proj_beta` | H1 | 0.0500 | 9.537e-07 | yes |
| U-Air | `raven` | H2 | 0.0500 | 0.0930 | no |
| U-Air | `raven` | H3 | 0.0500 | 0.1744 | no |
| U-Air | `proj_beta` | H2 | 0.0500 | 0.2403 | no |
| U-Air | `proj_beta` | H3 | 0.0500 | 0.0664 | no |
| City Scanner | `raven` | H1 | 0.0500 | 9.766e-04 | yes |
| City Scanner | `raven` | H2 | 0.0500 | 0.5191 | no |
| City Scanner | `raven` | H3 | 0.0500 | 0.2158 | no |

Holm propagation is visible: a chain that rejects hands its weight to the other chain
(e.g. U-Air `raven` H1 first at 0.0250, then `proj_beta` H1 at 0.0500, and `raven` H2 back
at 0.0500). All α levels are ≥ 8 × 10⁻⁷, far above the p-value resolution floor, so no
chain failed *because of* the split. `H3_reject` is `False` for the two SensorScope chains
because their HL point estimates are negative; those chains are "non-inferior but not
demonstrably superior", exactly what the frame is built to say.

### 1.2 Estimator validation, and reproduction of the protocol's own §0 readings

The preregistered Wilcoxon inversion was verified two independent ways (numbers in
`A1_PROVENANCE.json`):

* **Agreement with the exact signed-rank tests** on the same data, for all 5 chains:
  `U_wilcox < δ` ⟺ `p(one-sided "less" on d − δ) < 0.05` — 5/5 agree;
  `L_wilcox > 0` ⟺ `p(one-sided "greater" on d) < 0.05` — 5/5 agree.
* **Simulated coverage** (`verify_inversion`, 20 000 replications, seed 4242, normal data
  at a known shift): two-sided 90 % coverage 0.9027 (n = 20) / 0.8962 (n = 10); one-sided
  lower 0.9502 / 0.9462; one-sided upper 0.9526 / 0.9500. Targets 0.90 / 0.95.

During development the inversion helper was written wrongly twice (a doubled Walsh-average
vectorisation, then a wrong order-statistic index). Both defects were caught **before**
any A1 value was reported, by exactly the two checks above, and neither defect ever
entered a written output. `PREREG.md` names the estimator form (`L = W_norm[c_lo]`,
`U = W_norm[c_hi]`, exact null CDF) so the convention cannot drift.

The City Scanner row of protocol §0 was independently reproduced from the frozen tables
before any A1 statistic was read:

| quantity (protocol §0) | protocol | computed here | agrees |
|---|---|---|---|
| `raven − fedavg_window` relative mean | +5.59 % | +5.589 % | yes |
| median | +0.27 % | +0.270 % | yes |
| SD | 13.4 % | 13.42 % | yes |
| seeds where `raven` is lower | 5/10 | 5/10 | yes |
| seed 32005 ratio (`raven`/`fedavg_window`) | +39 % | +39.2 % | yes |
| `raven − raven_wo_design` relative mean | +2.45 % | +2.368 % | approximately |
| median / SD / seeds lower | −0.22 % / 13.0 % / 7/10 | −0.625 % / 12.99 % / 8/10 | **no** — convention differs |

The last row is filed as errata item **E-A1-13**: the `raven − raven_wo_design` summary in
protocol §0 does not reproduce under the per-trace ratio convention used here (the
absolute per-trace values are bit-identical to the frozen table, 200/200 cells). No
conclusion of this round depends on that row.

## 2 A1.1 — descriptive application (post hoc)

**Every row of `A1_DESCRIPTIVE.csv` carries `label = "post hoc descriptive"` and these rows
must never be cited as confirmatory evidence.** They show what the fixed frame reads on
data that already existed when the frame was written. The exclusion of trace 32005 is a
declared sensitivity analysis, never primary.

| dataset | arm | H1 p | H1 reject | H2 HL | H2 ub95 | δ | H2 reject | H3 reject | power (θ=0) |
|---|---|---|---|---|---|---|---|---|---|
| SensorScope | `raven` | 9.537e-07 † | yes | −0.000131 | +0.000241 | 0.5 % | yes | no | 1.000 |
| SensorScope | `proj_beta` | 9.537e-07 † | yes | −0.000273 | +0.000305 | 0.5 % | yes | no | 1.000 |
| U-Air | `raven` | 9.537e-07 † | yes | +0.001937 | +0.005430 | 0.5 % | **no** | not tested | 0.697 |
| U-Air | `proj_beta` | 9.537e-07 † | yes | +0.003318 | +0.007676 | 0.5 % | **no** | not tested | 0.674 |
| City Scanner | `raven` | 9.766e-04 | yes | +0.022029 | +0.148204 | 2 % (δ_CS) | **no** | not tested | 0.120 |

† = at the exact signed-rank resolution floor `2^-20 = 9.537e-07`; the value means
`p ≤ 9.5e-07`, not a measured magnitude below it (errata item E-A1-6).

Reading, stated plainly:

* **Structure (H1) is replicated on every chain and both datasets.** On City Scanner all
  10/10 traces improve `Δ_group` under `raven` (p = 9.77e-04, its own floor for n = 10,
  `2^-10`); `Δ_group` falls from 0.148–0.244 (`fedavg_window`) to 0.045–0.121 (`raven`).
* **Prediction (H2) holds on SensorScope and fails on U-Air and City Scanner.**
  SensorScope's HL relative difference is *negative* for both arms (the arm is marginally
  better in the median), and both one-sided 95 % upper bounds sit below δ = 0.5 %.
  U-Air's upper bound is 1.09 × δ (`raven`) and 1.54 × δ (`proj_beta`) — it *fails* on
  the margin, but it fails narrowly, and the A1.2 power column says the test had the
  power to detect it (MDE₈₀ = −0.076 % < 0).
* **City Scanner fails H2 by a wide margin**: HL +2.20 %, upper bound +14.8 %, versus
  δ_CS = 2 %. The mean +5.59 % and median +0.27 % of protocol §0 reproduce exactly
  (checked: mean +5.589 %, median +0.270 %, SD 13.42 %, 5/10 seeds lower, seed-32005
  ratio +39.2 %). The failure is driven by the upper tail, i.e. by the same single-trace
  behaviour protocol §0 describes.

**H3 (superiority) is never reached in this round**: it is gated on H2, and H2 was
rejected only for SensorScope, where the HL point estimates are negative and the lower
bound therefore cannot be > 0. The `H3_reject` cell reads `not tested (H2 not rejected)`
for the three chains that stop at H2.

### 2.1 Declared sensitivity: recomputed without trace 32005

| dataset | arm | n | rel mean | rel median | rel SD | H1 p | HL | ub95 | δ | H2 reject |
|---|---|---|---|---|---|---|---|---|---|---|
| SensorScope | `raven` | 20 | not applicable — unit 32005 does not occur on this dataset | | | | | | | |
| SensorScope | `proj_beta` | 20 | not applicable | | | | | | | |
| U-Air | `raven` | 20 | not applicable | | | | | | | |
| U-Air | `proj_beta` | 20 | not applicable | | | | | | | |
| City Scanner | `raven` | 9 | +1.849 % | −0.052 % | 6.74 % | 1.953e-03 | +0.005913 | +0.024546 | 2 % | **no** |

Dropping trace 32005 halves the City Scanner paired SD (13.42 % → 6.74 %) and takes the
median relative difference to ≈ 0 (−0.05 %), but **still does not reject H2**: the
one-sided 95 % upper bound is +2.45 % > 2 %. This is exactly why the exclusion is
registered as sensitivity only, and it is consistent with the A1.2 verdict below.
The exclusion is not applicable on SensorScope/U-Air because seed 32005 is a City Scanner
trace id; those four rows are recorded with `excluded_unit = not applicable` rather than
silently dropped from the file.

## 3 A1.2 — power

`A1_POWER.csv` holds the full grid: every `(dataset, arm)`, margins δ, `θ ∈ {0, δ/2, δ}`,
`r ∈ {1, 3, 5}` for City Scanner, with the normal-approximation power, the two-sided-`t`
variant, `MDE₈₀` and the trace-cluster bootstrap power. Headline rows at `θ = 0`, `r = 1`
unless stated:

| dataset | arm | n | paired SD | SE | power(θ=0) | MDE₈₀ | δ | H2 testable? |
|---|---|---|---|---|---|---|---|---|
| SensorScope | `raven` | 20 | 0.0988 % | 0.0221 % | 1.000 | +0.445 % | 0.5 % | **yes** |
| SensorScope | `proj_beta` | 20 | 0.1491 % | 0.0333 % | 1.000 | +0.417 % | 0.5 % | **yes** |
| U-Air | `raven` | 20 | 1.0356 % | 0.2316 % | 0.697 | **−0.076 %** | 0.5 % | **yes (0.70 < 0.80, but MDE₈₀ < 0)** |
| U-Air | `proj_beta` | 20 | 1.0665 % | 0.2385 % | 0.674 | **−0.093 %** | 0.5 % | **yes (0.67 < 0.80, but MDE₈₀ < 0)** |
| City Scanner | `raven` | 10 | 13.424 % | 4.245 % | **0.120** | +8.56 % | 2 % | **NO** |

The preregistered testability rule was `power(θ = 0) ≥ 0.80`. Under it, SensorScope is
testable and **U-Air's two chains land just under the rule at 0.697 / 0.674**, which is
reported as it falls rather than rounded to a verdict; their `MDE₈₀` is below zero, so the
margin δ = 0.5 % is inside their 80 %-power range and the observed H2 failures there are
informative rather than artefacts of low power. This near-miss is an errata item
(E-A1-7) precisely because the rule's `≥ 0.80` threshold is a convention, not a
measurement.

### 3.1 City Scanner: the proxy, and the testability verdict

**B0 does not exist** — Part B was not authorized — so the within-trace variance that
protocol §1.2 asks for cannot be measured. The script says so in every affected cell
(`proxy_flag = proxy`, plus a `proxy_status` string). The best available proxy is the
`raven_wo_design` vs `raven` contrast
(`results_nodesign_supplement/round_v1/tables/cityscanner_seed_rows.csv`): the two arms
share the same 10 traces and the same model seeds and differ only in their π^tar support,
so the trace effect cancels in the contrast and its scatter estimates the within-trace
scale. Its value is **0.0980** (mean of the contrast −1.20 % across the 10 traces).

Under the preregistered two-component model `σ_total² = σ_B² + σ_W²` (σ_total = 0.1342 at
r = 1), the admissible range is reported rather than one number:

| scenario | σ_W | σ_B | power(θ=0) r=1 | r=3 | r=5 | bootstrap r=1 / r=3 / r=5 | MDE₈₀ at r=5 |
|---|---|---|---|---|---|---|---|
| `S0_sigmaW_zero` (floor: extra seeds buy nothing) | 0 | 0.1342 | 0.120 | 0.120 | 0.120 | 0.142 / 0.142 / 0.142 | +8.56 % |
| `S1_neutral` (σ_W = σ_B) | 0.0949 | 0.0949 | 0.120 | 0.143 | 0.150 | 0.142 / 0.165 / 0.173 | +6.18 % |
| `S2_pilot_within_trace` (proxy 0.0980, optimistic) | 0.0980 | 0.0918 | 0.120 | 0.145 | 0.153 | 0.142 / 0.168 / 0.176 | +5.99 % |

**Verdict, stated plainly: City Scanner H2 is NOT testable at δ_CS = 2 % with the traces
that exist.** The maximum power reached anywhere in the admissible range is **0.153**
(normal approximation, r = 5, most optimistic σ_W; the trace-cluster bootstrap Monte-Carlo
puts the same cell at **0.176**), i.e. at best about one chance in six of detecting
non-inferiority even if the arm were exactly as good as `fedavg_window`. Quintupling the
number of model seeds moves the answer from 0.120 to at most 0.176, because the binding
term is the *between-trace* variance, which no number of model seeds on the same 10 traces
can reduce. The minimum effect the rule can detect at 80 % power is +8.6 % (S0, any r) to
+6.0 % (S2, r = 5) relative RMSE_μ, i.e. 3–4 × the declared margin.

Consequences that follow directly and are not softened:

1. A City Scanner H2 non-rejection in Part B would carry almost no information — it would
   be the expected outcome under both H2 true and H2 false.
2. No `r` and no margin change in this round fixes it; the only fix is more independent
   **event traces**, and no trace generator exists in the repo (protocol §0, §3).
3. δ_CS = 2 % remains the declared margin and is not revisited, per §A1.0. Reporting that
   the test cannot reach it is not the same as redefining it.

## 4 Part B (C1 training) — not run, and why

**Part B was not run because the exact authorization phrase `授权 C1 训练` was not given in
this session.** No training of any kind was performed: no call to `train_one`, no
`build_full_runner`, no `build()`, no checkpoint written, no arm trained at any `r`,
including the `r = 1` "cheap" case. `scripts/c1_deletion_driver.py` was not created.
`scripts/run_nodesign_supplement.py` was read (read-only) to understand the driver
precedent, and no other repo path outside the round directory was written.

What Part B would require, if authorized (protocol §2, for the user's decision — this is
an outline, not a design performed here):

* **B0-a reproduction gate.** A new driver `scripts/c1_deletion_driver.py` importing
  `build_setup` / `train_one` from `scripts/run_nodesign_supplement.py`, replacing only
  `setup["pi_target"]` per arm, must reproduce frozen `raven` seed 32001 and
  `raven_wo_design` seed 32001 to ≤ 1e-12 on `RMSE_μ`, `WorstGroupRMSE`, `Δ_group`,
  `Δ_c-s`. A failure stops everything.
* **B0-b seed-32005 probe.** On trace 32005 only, `raven` and `raven_wo_design` under
  model seeds {32005, 132005, 232005, 332005, 432005}, to separate a trace-driven effect
  from training instability. B0-b is also the only measurement that would replace the
  A1.2 proxy of §3.1 with a real `σ_W`.
* **B1 arms** (6): `fedavg_window` and `raven_wo_design` reused when `r = 1`; new
  `raven_ctrl` (`build_pi_target(test)`, 14.35 % deleted share), `raven_ctrl_floor`
  (zero keys set to the smallest positive control mass, renormalised), `raven_M1mu` and
  `raven_M2mu` (ACS / 311 maps from `MAPS_KEY_LEVEL.csv`, region-rescaled). Maps cover
  every risk-set key; a missing key is a hard error; map sha256, key counts, π_floor and
  per-(arm, trace) realized ρ are logged.
* **Cost.** `r = 1` → 30 new runs ≈ 40 s each ≈ 20 min; `r = 3` → 130 runs ≈ 1.5 h. `r`
  must be fixed in `PREREG` before B1 and cannot be raised afterwards.
* **Endpoint.** Primary H_mech: `RMSE_μ(raven_ctrl) > RMSE_μ(raven_ctrl_floor)`, HL paired
  relative difference with trace-cluster bootstrap CI (10 000 resamples, seed 20261003)
  and a two-sided Wilcoxon on trace-level means. Structural guardrail: Δ_group and Δ_c-s
  of `raven_ctrl_floor` vs `raven_ctrl`, plus the retained share of the FedAvg→RAVEN
  Δ_group gain. Secondary Holm family: `M1mu − ctrl`, `M2mu − ctrl`,
  `ctrl_floor − wo_design`, dose-response of `RMSE_μ` on realized ρ.
* **Confirmatory A1 chains** for `raven_ctrl_floor`, `raven_M1mu`, `raven_M2mu` vs
  `fedavg_window` with the graphical α split of this round.
* **Prerequisite the A1.2 verdict imposes.** The confirmatory H2 chains above are exactly
  the tests §3.1 shows are unreachable at n = 10 traces. Authorizing Part B therefore
  buys the *mechanism* answer (H_mech, which is a comparison between two new arms on the
  same traces and is not the same power problem) but cannot buy a confirmatory
  non-inferiority statement at δ_CS = 2 %. If a confirmatory H2 statement is wanted, the
  trace generator question of protocol §3 must be decided first.
* **Decision rules** already fixed in protocol §B3 (paper paused) apply unchanged.

## 5 Files produced in this round

| file | what it is |
|---|---|
| `PROTOCOL.md` | byte-identical copy of the execution prompt (sha256 in `MANIFEST.sha256`) |
| `PREREG.md` | the preregistration, hashed before any computation |
| `MANIFEST.sha256` | sha256 of `PROTOCOL.md` and `PREREG.md`, written first |
| `A1_ANALYSIS.py` | the analysis script (reads only the listed inputs; writes only here) |
| `A1_DESCRIPTIVE.csv` | A1.1, one row per `(dataset, arm)`, every row `post hoc descriptive` |
| `A1_DESCRIPTIVE_DETAIL.csv` | the same chains with SE, all three CI variants, α allocation, consistency checks |
| `A1_POWER.csv` | A1.2 power grid, proxy rows labelled |
| `A1_SENSITIVITY_NO32005.csv` | the declared sensitivity recomputation |
| `A1_PROVENANCE.json` | input sha256 (11 files), bootstrap settings, α history, SS0 reproduction check, estimator validation |
| `EXECUTION_REPORT.md` | this file |
| `ERRATA_FOR_PAPER.md` | 13 items (E-A1-1 … E-A1-13); no manuscript was edited |

Relevant input sha256 (full list in `MANIFEST.sha256` and `A1_PROVENANCE.json`):

| input | sha256 (first 16) |
|---|---|
| `results_w1_ladder/round_v5_1/TRADEOFF_V51.csv` (θ-canonical SS/U-Air) | `a66eb2e46c874c1c` |
| `results_c1_cityscanner/round_v1/tables/CS_E3.csv` (frozen CS) | `8cbb81134ab2822b` |
| `results_nodesign_supplement/round_v1/tables/cityscanner_seed_rows.csv` | `037220d32bb1fe11` |
| `results_w1_ladder/round_v4/TRADEOFF.csv` (v4 cross-check only) | `6b2c10c04b649c92` |
| `results_exogenous_target/round_v1/MAPS_KEY_LEVEL.csv` (Part B prep, not used in A1) | `b9e3ed9c4e4f7690` |

## 6 No-fabrication statement

Every number in this report and in the four CSVs is computed by `A1_ANALYSIS.py` from the
read-only inputs whose sha256 are recorded in `A1_PROVENANCE.json`. No cell is imputed,
extrapolated or replaced by a different quantity; the one place where a required quantity
does not exist (the City Scanner within-trace variance, because B0 was not run) is filled
with an explicitly labelled proxy and an admissible range, never with a single invented
number. No `TBD` cell was needed in `A1_DESCRIPTIVE.csv` or `A1_POWER.csv`: every column
in those two files is computable from the frozen inputs. Where a number is at a
resolution floor or fails a preregistered threshold, it is reported as such (§2, §3).
No margin, arm, contrast, seed set, endpoint or α was changed after seeing a result, and
no Part-B or Part-C artefact was produced.

---
---

# EXECUTION_REPORT — Part B (C1 delivery-deletion mechanism), r = 3

Appended after Part A. **Nothing above this line was edited.** Part A's text is reproduced
unmodified; `PREREG.md` was extended append-only by `AMENDMENT 1`, and `MANIFEST.sha256`
was extended by an appended block.

## B.0 Authorization, registration, and what was locked when

| item | value |
|---|---|
| user authorization (verbatim, received through the delegating agent) | `授权C1训练，r=3` |
| replication | **r = 3**, model seeds `{s, s+100000, s+200000}` |
| `PREREG.md` before the amendment (Part A as executed) | sha256 `1e1816cd3431a1c49c92f2806ab83b981b4392d216906af1323425c819f7719e` |
| `PREREG.md` including AMENDMENT 1 (t3) | sha256 `d44558d959c70d08c045940128cbf0df85a1a6d60e5eaf42a67520030c07ffe7` |
| `PROTOCOL.md` (unchanged) | sha256 `916b55766f24b4b5685e59418fe2140ad1e74e2c178ed0f75ba375c7feb8324e` |
| registration order | AMENDMENT 1 was written and its hash appended to `MANIFEST.sha256` **before the first training run of any kind** (B0-a included). At that moment no City Scanner run existed under any new arm or extra model seed, so no C1 `RMSE_μ` existed. |

Locked in AMENDMENT 1 before any run: the arm list, the map construction and the map key
universe, the π_floor rule, δ_CS = 2 %, the primary `H_mech` estimand and its percentile
trace-cluster bootstrap (`B = 10000`, `seed = 20261003`), the structural guardrail formula,
the secondary Holm family, the K = 3 graphical-α A1 chains, the no-32005 sensitivity rule
and all four B3 decision rows.

Machinery: `scripts/c1_deletion_driver.py` imports `build_setup` and `train_one` from
`scripts/run_nodesign_supplement.py` and replaces **only** `setup["pi_target"]` per arm
(plus, at the extra model seeds, an output-root redirect into this round directory and a
directory junction presenting trace `s` under the name `seed{s+100000·j}` — both are path
redirections only; the training path is intact, which is what B0-a proves).

## B.1 B0-a — driver reproduction (hard gate): **PASS**

`B0_REPRO.json`. Both frozen seed-32001 rows were reproduced **bit-exactly** (max |Δ| = 0.0
on every endpoint, not merely ≤ 1e-12), with matching `eventtrace_hash`:

| arm | endpoint | frozen | rerun | \|Δ\| |
|---|---|---|---|---|
| `raven_ctrl` (= frozen `raven`) | `RMSE_mu` | 0.3640887382754061 | 0.3640887382754061 | 0.0 |
| | `WorstGroupRMSE` | 0.38698378721310384 | 0.38698378721310384 | 0.0 |
| | `Delta_group` | 0.05490366930013694 | 0.05490366930013694 | 0.0 |
| | `Delta_c_s` | 0.6032874844741689 | 0.6032874844741689 | 0.0 |
| `raven_wo_design` | `RMSE_mu` | 0.36722021263758886 | 0.36722021263758886 | 0.0 |
| | `WorstGroupRMSE` | 0.3946359257625973 | 0.3946359257625973 | 0.0 |
| | `Delta_group` | 0.07089974367065534 | 0.07089974367065534 | 0.0 |
| | `Delta_c_s` | 0.8021415247948038 | 0.8021415247948038 | 0.0 |

The gate therefore licensed B0-b and B1. A configuration check run alongside it (also
`B0_REPRO__b0a_t1.json`) showed that forcing `torch.set_num_threads(1)` breaks bit-exactness
(max |Δ| 4.2e-8 on `Delta_group`, 4.0e-10 on `RMSE_mu`); **all Part B runs therefore use the
default thread configuration of the frozen runs** (see E-B-1).

## B.2 B0-b — seed-32005 probe: the +39 % is **trace-driven**, not a single-seed instability

`B0_SEED32005_PROBE.csv`, `B0_SEED32005_PROBE.json`. Trace 32005 only, both arms, five
model seeds (the original 32005 plus four replicates):

| model seed | `raven_ctrl` `RMSE_mu` | `raven_wo_design` `RMSE_mu` | ratio − 1 |
|---|---|---|---|
| 32005 (original) | 0.409160 | 0.295501 | **+38.46 %** |
| 132005 | 0.404394 | 0.314149 | **+28.73 %** |
| 232005 | 0.412830 | 0.331715 | **+24.45 %** |
| 332005 | 0.366847 | 0.270868 | **+35.43 %** |
| 432005 | 0.418853 | 0.320264 | **+30.78 %** |

Mean +31.57 %, SD 5.52 pp; 5/5 seeds ≥ +20 %, 0/5 ≥ +39 %.

All eight replicate rows were trained by the B0-b stage itself (the probe ran **before** B1;
`C1_EXECUTION_LOG.md` records eight `B0-b … created` lines at 09:13:57–09:14:40 UTC), and the
`source` column of `B0_SEED32005_PROBE.csv` marks them `trained_B0b_stage`, with the two
original-seed rows marked `frozen`. B1 later reused the four rows that fall on its r = 3
grid (`s+100000`, `s+200000`) rather than re-training them.

**Verdict: trace-driven.** Every replicate model seed reproduces a large positive gap on
trace 32005, so the +39 % is a property of this event trace, not of one model seed. The B3
row "B0-b shows the +39 % only at the original model seed" therefore **does not trigger**:
no training-instability-outlier language is licensed, and the primary is computed on all 10
traces (as registered either way).

## B.3 Maps, realized deletion ρ, and key coverage (`C1_MAPS.json`)

π_floor = smallest positive control key mass = **4.784688995215311e-04** (> 480 × the
ζ denominator floor π_min = 1e-6, so floored keys receive strictly positive ζ).

| arm | map | keys | positive / zero | π^tar region marginals = μ? | realized ρ (mean) | ρ range over traces | map sha256 (16) |
|---|---|---|---|---|---|---|---|
| `fedavg_window` | control (unused, Design off) | 1164 | 352 / 812 | yes | **0** (by construction) | 0 | `783ca56b209c09ee` |
| `raven_wo_design` | control (unused, Design off) | 1164 | 352 / 812 | yes | **0** (by construction) | 0 | `783ca56b209c09ee` |
| `raven_ctrl` | control = `build_pi_target(test)` | 1164 | 352 / 812 | yes (≤ 1e-12) | **0.143450** | 0.1296 – 0.1553 | `783ca56b209c09ee` |
| `raven_ctrl_floor` | control, zeros → π_floor, renormalized | 1164 | 1164 / 0 | no (see below) | **0.000000** | 0 | `86a3f8d048ba44ba` |
| `raven_M1mu` | M1 (ACS) rescaled within region to μ | 1164 | 1094 / 70 | yes (≤ 1e-15) | **0.010077** | 0.0067 – 0.0144 | `f40b0f0374a0fb3c` |
| `raven_M2mu` | M2 (NYC 311) rescaled the same way | 1164 | 1131 / 33 | yes (≤ 1e-15) | **0.009848** | 0.0043 – 0.0150 | `58ec1cd429a2cd37` |

* **Hard coverage:** the union of every `(client, stratum)` key appearing in any risk set of
  any of the 10 traces is **959 keys** (identical to `n_pi_opp_keys`). All four maps contain
  all 959; `n_missing = 0` for every arm, so the "missing key is a hard error" rule never
  fired.
* **Control map cross-check:** the control map equals the `pi_control` column of
  `MAPS_KEY_LEVEL.csv` on all 1164 shared keys (max |Δ| = 9.8e-17), and its region marginals
  equal μ exactly — the frozen π^tar is region-matched to μ by construction.
* **M-map key universe (registered):** M1/M2 were placed on the control map's 1164-key
  support, not on the raw 3568-row cross product of `MAPS_KEY_LEVEL.csv`. On the raw cross
  product, phantom `(cell, stratum)` combinations carry mass and the real support's region
  marginals would deviate from μ by up to **7.03 pp** (M1) / 5.82 pp (M2); that rejected
  variant's numbers are stored in `C1_MAPS.json` (`map_meta`).
* **ρ definition:** share of delivered units (events with `U = 1` on non-test splits, 29 189
  rows in total) whose key carries π^tar = 0, recomputed exactly as
  `scripts/exogenous_target_cityscanner.py` does. The pooled control value 0.14345
  reproduces the frozen 14.35 %. For the two Design-off arms the *realized* ρ is 0 because ζ
  is not applied; the share the control *map* would delete is reported separately in
  `C1_MAPS.json` as a structural reference and is never used as their ρ.

## B.4 B1 runs

180 rows in `C1_RUNS.csv` = 6 arms × 10 traces × 3 model seeds, of which **150 were newly
trained** and 30 are reused frozen rows (model seed `s`). Zero failures; `C1_FAILURES/` is
empty. Executed as 6 concurrent shards, 25 runs each, `09:14:59 → 09:36:22 UTC`
(**21.4 min wall clock**); 157 new training runs in total (including B0-a, B0-b and the
thread-configuration check), 7 802 s ≈ **2.17 h of aggregate compute**.

Registered deviation from the protocol's run-count estimate: 150 new runs, not ≈130. The
protocol's arm table marks **three** reused arms (`fedavg_window`, `raven_wo_design`,
`raven_ctrl`) while its count charges extra seeds for two; all three reused arms received
the extra seeds so that the primary contrast is balanced at r = 3. This was fixed in
AMENDMENT 1 **before** the first run.

## B.5 B2 — primary `H_mech` and structural guardrail (`C1_PRIMARY.json`)

Contrast: `d_t = RMSE_μ(raven_ctrl,t)/RMSE_μ(raven_ctrl_floor,t) − 1`, trace-level means over
r = 3 model seeds; positive ⇒ deletion costs prediction accuracy.

| trace | `RMSE_μ` ctrl | `RMSE_μ` floor | `d_t` |
|---|---|---|---|
| 32001 | 0.37758 | 0.33816 | +11.66 % |
| 32002 | 0.41606 | 0.41621 | −0.04 % |
| 32003 | 0.19395 | 0.19775 | −1.92 % |
| 32004 | 0.19687 | 0.19687 | −0.002 % |
| **32005** | **0.40879** | **0.31480** | **+29.86 %** |
| 32006 | 0.16901 | 0.17195 | −1.71 % |
| 32007 | 0.16322 | 0.16505 | −1.11 % |
| 32008 | 0.18357 | 0.19366 | −5.21 % |
| 32009 | 0.25314 | 0.24818 | +2.00 % |
| 32010 | 0.19916 | 0.19926 | −0.05 % |

| quantity | value |
|---|---|
| HL paired relative difference | **−0.000192** (−0.019 %) |
| percentile trace-cluster bootstrap CI (B = 10 000, seed 20261003) | **[−0.018930, +0.122754]** |
| basic (reflection) CI (secondary) | [−0.123138, +0.018546] |
| Wilcoxon-inverted bounds `[L, U]` (secondary) | [−0.016079, +0.116558] |
| two-sided paired Wilcoxon on the 10 trace-level means | p = **0.9219** |
| traces where ctrl is worse | 3 / 10 |
| **reading (mechanical)** | **inconclusive** |

The reading is **identical under all three interval types** (percentile, basic,
Wilcoxon-inverted): none is wholly above 0 and none lies inside ±δ_CS, so the registered
mechanical reading is "inconclusive" however the interval is formed. The CI is dominated by
trace heterogeneity: 7 of 10 traces show the floored arm at or slightly *worse* than the
deletion arm, while trace 32005 alone contributes +29.9 %.

**Structural guardrail (reported next to the primary).**

| quantity | `fedavg_window` | `raven_ctrl` | `raven_ctrl_floor` |
|---|---|---|---|
| mean `Δ_group` (‖ω̂ − μ‖₁, lower better) | 0.195335 | 0.070644 | **0.068224** |
| mean `Δ_c-s` (vs the arm's own π^tar) | 0.812260 | 0.567578 | 0.789248 |

`Δ_group(floor) − Δ_group(ctrl) = −0.002420` (the floored arm is slightly *better*, not
worse). Share of the FedAvg→RAVEN `Δ_group` gain retained by the floor arm:
`(0.195335 − 0.068224)/(0.195335 − 0.070644)` = **1.0194 (101.9 %)** — far above the 50 %
threshold of the B3 rule. Per-trace shares range 0.871 – 1.328.

Caveat, stated plainly: `Δ_c-s` is computed against **each arm's own** π^tar, so the
ctrl-vs-floor `Δ_c-s` values are not like-for-like: the floor arm's realized delivery sits
further from its (all-positive, π_floor-flattened) target (0.789) than the control arm's
delivery sits from its (812-zero, spike-shaped) target (0.568). The floor arm also loses the
`Δ_c-s` reduction that deletion produced; that is a trade-off, reported, not a decision.

**Power (required by B3 for the inconclusive row; post hoc diagnostic, no decision input).**
sd(`d_t`) = 10.30 %, SE = 3.26 %, n = 10 traces, r = 3 ⇒ power of the H2-style
non-inferiority rule at δ_CS = 2 % and θ = 0 is **0.151**, `MDE_80 = −6.10 %`: by the A1 §5
testability rule this round is **not testable** at δ_CS for this contrast (power < 0.80).
The percentile CI width is 14.2 pp. Without trace 32005 the sd falls to 4.66 % and the power
rises to 0.361 — still below 0.80.

## B.6 B2 — secondary family, Holm within the family (m = 4) (`C1_SECONDARY.csv`)

All contrasts are `RMSE_μ(first)/RMSE_μ(second) − 1` at trace level. Holm step-down,
α = 0.05, thresholds 0.0125 / 0.0167 / 0.025 / 0.05.

| member | HL | percentile CI | p | Holm rank | threshold | reject |
|---|---|---|---|---|---|---|
| `raven_M2mu − raven_ctrl` | +0.015229 | [−0.059178, +0.044883] | 0.4922 | 1 | 0.0125 | no |
| dose-response slope (6 arms, `RMSE_μ` on realized ρ) | slope **+0.044061** | [−0.069302, +0.200960] | 0.541 (bootstrap) | 2 | 0.0167 | no |
| `raven_ctrl_floor − raven_wo_design` | +0.000645 | [−0.005718, +0.006399] | 0.6250 | 3 | 0.025 | no |
| `raven_M1mu − raven_ctrl` | +0.002215 | [−0.085358, +0.031195] | 0.9219 | 4 | 0.05 | no |
| *(declared variant, not a Holm member)* slope, RAVEN-Design arms only | +0.024002 | [−0.091087, +0.178799] | 0.7494 | — | — | — |

**No member of the secondary family is rejected.** Two of them are nevertheless informative
and are reported as such (descriptive, not decisions): the cost of the tilt alone
(`raven_ctrl_floor − raven_wo_design`) is +0.06 % with a CI of ±0.6 pp, i.e. the RAVEN
machinery with no deletion is statistically indistinguishable from the no-design arm; and
the dose-response slope is positive but its CI comfortably contains 0 and its point estimate
flips sign (−0.005) when trace 32005 is removed, so no dose-response claim is supported.

## B.7 B2 — confirmatory A1 chains (the only confirmatory prediction statements of this round) (`C1_A1_CHAINS.csv`)

`H1 → H2(δ_CS = 2 %) → H3` vs `fedavg_window`, trace-level means at r = 3, graphical
Bretz–Maurer–Brannath–Posch α split with K = 3 chains (equal initial weights 1/3, Holm
transitions 1/2). The α machinery and the Wilcoxon-inverted bounds were verified identical
to `A1_ANALYSIS.py` on the same data (`C1_ANALYSIS_PROVENANCE.json`, all three checks
`true`).

| arm | H1 p | H1 reject | H2 HL | H2 `U_wilcox` (95 %) | δ_CS | H2 reject | H3 | α(H1) |
|---|---|---|---|---|---|---|---|---|
| `raven_ctrl_floor` | 0.000977 | **yes** | +0.003695 | +0.038329 | 0.02 | **no** | not tested | 0.0375 |
| `raven_M1mu` | 0.000977 | **yes** | +0.007048 | +0.041392 | 0.02 | **no** | not tested | 0.0167 |
| `raven_M2mu` | 0.000977 | **yes** | +0.022632 | +0.081481 | 0.02 | **no** | not tested | 0.0250 |

* **H1 (structure) is confirmed for all three new arms**: `Δ_group` is lower than
  `fedavg_window` on 10/10 traces (p at the n = 10 resolution floor 9.77e-04).
* **H2 (prediction, non-inferiority at δ_CS = 2 %) is not established for any of them**: the
  whole one-sided 95 % interval lies above +2 % for all three (3.83 %, 4.14 %, 8.15 %).
  H3 is therefore not tested anywhere and no superiority statement is made.
* The rule-based and the A1-implementation readings of `H2_reject` agree (`false`) for all
  three arms; the consistency check `U_wilcox < δ_CS` ⇔ signed-rank p < 0.05 is `true` for
  all three.

## B.8 WorstGroupRMSE and per-region RMSE, every arm (`C1_ARM_SUMMARY.csv`)

Trace-level means at r = 3 (n = 10 traces; per-run values in `C1_RUNS.csv`, per-seed rows in
`C1_PER_SEED.csv` with trace 32005 flagged).

| arm | ρ | `RMSE_μ` | `WorstGroupRMSE` | R0 | R1 | R2 | R3 | `Δ_group` | `Δ_c-s` |
|---|---|---|---|---|---|---|---|---|---|
| `fedavg_window` | 0 | 0.240901 | 0.252947 | 0.23745 | 0.24441 | 0.24263 | 0.23494 | 0.195335 | 0.812260 |
| `raven_wo_design` | 0 | 0.243938 | 0.257477 | 0.24221 | 0.24586 | 0.24787 | 0.23881 | 0.073627 | 0.787993 |
| `raven_ctrl` | 0.1435 | 0.256134 | 0.269535 | 0.25660 | 0.25719 | 0.25980 | 0.25102 | 0.070644 | 0.567578 |
| `raven_ctrl_floor` | 0 | 0.244190 | 0.257584 | 0.24333 | 0.24564 | 0.24868 | 0.23912 | 0.068224 | 0.789248 |
| `raven_M1mu` | 0.0101 | 0.246668 | 0.260915 | 0.24463 | 0.24864 | 0.24924 | 0.24203 | 0.077107 | 1.406032 |
| `raven_M2mu` | 0.0098 | 0.250797 | 0.266145 | 0.24965 | 0.25243 | 0.25176 | 0.24595 | 0.081316 | 1.434787 |

(`WG_R0..R3` in `C1_RUNS.csv` are the per-region values; the columns above are their
trace-level means.)

## B.9 Sensitivity without trace 32005 (declared; never primary) (`C1_SENSITIVITY_NO32005.csv`)

| estimate | full (n = 10) | without 32005 (n = 9) |
|---|---|---|
| primary HL | −0.000192 | −0.005577 |
| primary CI | [−0.018930, +0.122754] | [−0.023183, +0.035276] |
| primary Wilcoxon p | 0.9219 | 0.4961 |
| primary sd(`d_t`) | 0.102981 | 0.046561 |
| power at θ = 0, δ_CS | 0.151 | 0.361 |
| `M2mu − ctrl` HL | +0.015229 | +0.018577 |
| `M1mu − ctrl` HL | +0.002215 | +0.011652 |
| `ctrl_floor − wo_design` HL | +0.000645 | +0.000442 |
| dose slope (6 arms) | +0.044061 | −0.004573 |
| A1 `H2_ub95`, `raven_ctrl_floor` | +0.038329 | +0.039024 |
| guardrail retained share | 1.0194 | 1.0017 |

Mechanical reading of the no-32005 interval with the same rule: **also inconclusive**, and
only just — the lower bound −2.318 % misses the "inside ±2 %" region by 0.32 pp. The
sensitivity is nevertheless the crucial context for the primary: removing the single trace
32005 shrinks the CI from [−1.9 %, +12.3 %] to [−2.3 %, +3.5 %] and moves the HL to
−0.56 %, i.e. the point estimate does not favour the deletion arm once that trace is out,
and the wide primary CI is trace heterogeneity rather than a stable deletion cost.

## B.10 B3 — decision rules applied mechanically

| B3 row | condition | applies? |
|---|---|---|
| 1 | `H_mech` CI > 0 **and** floor retains ≥ 50 % of the `Δ_group` gain | **no** — the CI is not above 0 (upper bound +12.28 %, lower bound −1.89 %), although the retained share is 101.9 % ≥ 50 % |
| 2 | `H_mech` inside ±δ_CS | **no** — [−1.89 %, +12.28 %] is not inside ±2 % |
| 3 | `H_mech` inconclusive | **yes** — report the CI and the power; **no mechanism claim**; do not add traces or model seeds |
| 4 | B0-b shows the +39 % only at the original model seed | **no** — B0-b shows it at all 5 model seeds, so no outlier description is licensed |

**Applied outcome (row 3):** this round produces **no mechanism claim**. What may be written
is the inconclusive row itself: the primary CI for `RMSE_μ(raven_ctrl) − RMSE_μ(raven_ctrl_floor)`
is [−1.89 %, +12.28 %] (HL −0.019 %, p = 0.92) at n = 10 traces, r = 3, and the design's
power at δ_CS = 2 % is 0.151 — the question is not resolvable at this n. The structural
guardrail is reported next to it: the floored arm keeps 101.9 % of the FedAvg→RAVEN
`Δ_group` gain, and the cost of the tilt alone (`ctrl_floor − wo_design`) is +0.06 % with a
±0.6 pp CI. No traces, model seeds or contrasts were added after seeing these numbers, and
`r` was not raised.

## B.11 Outputs, failures, TBDs and deviations

New artefacts in `results_gatekeeping/round_v1/`: `B0_REPRO.json`, `B0_REPRO__b0a_t1.json`,
`B0_SEED32005_PROBE.csv`, `B0_SEED32005_PROBE.json`, `C1_MAPS.json`, `C1_RUNS.csv`,
`C1_PRIMARY.json`, `C1_SECONDARY.csv`, `C1_A1_CHAINS.csv`, `C1_SENSITIVITY_NO32005.csv`,
`C1_PER_SEED.csv`, `C1_ARM_SUMMARY.csv`, `C1_ANALYSIS_PROVENANCE.json`, `C1_RECON.json`,
`C1_EXECUTION_LOG.md`, the 154 per-run markers under `c1_runs/`, and this Part B section.
`scripts/c1_deletion_driver.py`, `scripts/c1_analysis.py`, `scripts/c1_registration.py`
were created.

* **Failures: none.** 150/150 B1 runs succeeded; `C1_FAILURES/` is empty. The only aborted
  attempts were two driver bugs found before any B1 run (a wrong junction path level and a
  rejected argument on a command line); both were fixed, and both are visible in
  `C1_EXECUTION_LOG.md`.
* **TBD: none in the required outputs.** Every cell of `C1_RUNS.csv`, `C1_PRIMARY.json`
  (including `dgroup_gain_retained_share`), `C1_SECONDARY.csv`, `C1_A1_CHAINS.csv` and
  `C1_SENSITIVITY_NO32005.csv` is computed. `H3_reject` is the registered
  "not tested (H2 not rejected)" string, not a missing value.
* **Deviations (all registered before the first run unless stated):** (a) 150 new runs
  instead of ≈130, for a balanced r = 3; (b) M1/M2 placed on the control map's key support
  rather than the 3568-row cross product; (c) the H2 p-value driving the graphical
  allocation is the signed-rank value (Part A's normal-approximation variant is reported
  alongside; both give the same `H2_reject`); (d) all runs use the frozen default thread
  configuration, because single-thread execution is not bit-exact; (e) the B0-b probe seeds
  `s+300000`, `s+400000` are diagnostic only and never enter a B1 endpoint.
* **Post hoc content in this report** is confined to the power diagnostic of §B.5 (required
  by B3 row 3), the `Δ_c-s` comparability caveat, and the descriptive sentences of §B.6.
  None of them feeds a decision rule.

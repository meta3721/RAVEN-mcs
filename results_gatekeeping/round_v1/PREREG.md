# PREREG — A1 gatekeeping (Part A only), RAVEN-MCS round `results_gatekeeping/round_v1`

Executable protocol: `results_gatekeeping/round_v1/PROTOCOL.md`
(byte-identical copy of the execution prompt, 11336 bytes,
sha256 `916b55766f24b4b5685e59418fe2140ad1e74e2c178ed0f75ba375c7feb8324e`),
hashed together with this file in `MANIFEST.sha256` **before any A1 number was computed**.

Discipline: `CCFA-Skills/ccf-experiment-designer`. No fabrication: every cell in
`A1_DESCRIPTIVE.csv` and `A1_POWER.csv` is computed by
`results_gatekeeping/round_v1/A1_ANALYSIS.py` from the read-only inputs listed in §6.
Nothing is imputed; a quantity that cannot be computed is written `TBD` with a reason.

## 0 Registration timeline (declared, not hidden)

| time | event | hash |
|---|---|---|
| **t0** | `PROTOCOL.md` copied byte-identical; this file first written; both hashed into `MANIFEST.sha256` **before any A1 number was computed** | `PREREG.md` = `c30ea27366df3217008aa26796c553d5d908c31b71b072728cd657e9f43e76d8` |
| **t1** | this file amended twice (see below), **still before any A1 value was read or reported** | — |
| **t2** | this registration-timeline section added; this is the operative registration | hash recorded by `MANIFEST.sha256` at finalisation and by `A1_PROVENANCE.json` |

`MANIFEST.sha256` re-prints the t0 hash — the byte-level evidence that a preregistration
existed before computation — and additionally records the sha256 of this file **as
executed** (t2), recomputed when the manifest was finalised. A file cannot contain the hash
of its own final bytes, so the executed hash lives in the manifest and in
`A1_PROVENANCE.json`, not here. The locked rules below are identical at t0, t1 and t2.

The two t1 amendments were:

* **(a) §3, H2/H3 decision statistic.** The upper bound was first written as a basic
  bootstrap percentile. It is now the **Wilcoxon-inverted distribution-free bound**, given
  as explicit order statistics (`L = W_norm[c_lo]`, `U = W_norm[c_hi]`, exact null CDF of
  `W+`), which is the estimator family the protocol itself names for A1; the bootstrap and
  the normal approximation are demoted to secondaries. This came from re-reading the
  protocol text and from internal consistency checks on the inversion, **not** from any A1
  result.
* **(b) §5, City Scanner variance scenarios.** The within-trace estimand `σ_W` was pinned
  down (SD of the paired relative difference between two model seeds of the *same arm* on
  the *same trace*), and the scenarios were restated as the admissible range `S0`/`S1`/`S2`
  with the `σ_total² = σ_B² + σ_W²` partition. This came from noticing that the available
  pilot contrast measures an arm difference on shared traces, **not** a model-seed
  replicate, and that Part B's B0 is what would measure it.

The t2 section is this table and the two paragraphs above; it changed no rule either.

**Nothing that the protocol fixes was changed at t1 or t2**: the H1 → H2 → H3 sequence,
δ = 0.5 % (SensorScope, U-Air), δ_CS = 2 %, the graphical-Holm rule, the arm list, the
seed/trace sets, the "never pooled across datasets" rule, the `B = 10 000` /
`seed = 20261003` bootstrap settings and the no-32005 sensitivity rule are exactly as the
protocol states them. The amendments changed *how a preregistered bound is computed and
named*, not *what is being tested, at which margin, on which data*.

Scope of this preregistration: **Part A only** (protocol §1 = A1.0/A1.1/A1.2, plus the
Part-A rows of protocol §4). Part B (C1 training, protocol §2) is **not** run: the
required user phrase `授权 C1 训练` has not been given. Part C (protocol §3) is out of
scope. Anything labelled `proxy` below is an admitted substitute for a Part-B quantity
that does not exist yet, and stays labelled `proxy` in every output.

---

## 1 Registration of the prior state (facts, not decisions)

Read on 2026-10-03 from frozen artefacts, before writing this file:

| fact | value | source |
|---|---|---|
| City Scanner traces | 10 (seeds 32001–32010), 100 windows, 421 clients | `results_c1_cityscanner/round_v1/CS_TRACE_MANIFEST.json` |
| City Scanner arms with runs | `fedavg_window`, `twostage_hajek`, `fedau_window`, `obsuse_window`, `raven` | `results_c1_cityscanner/round_v1/CS_TRAIN_LEDGER.json` (50 rows) |
| City Scanner no-deletion arm | `raven_wo_design`, 10 runs, seeds 32001–32010 | `results_nodesign_supplement/round_v1/runs/cityscanner_nyc_pm25/` |
| City Scanner contrast `raven − fedavg_window` | mean +5.59 %, median +0.27 %, SD 13.4 %, 5/10 seeds lower | protocol §0; re-verified in A1 |
| SensorScope / U-Air | 6 arms × 20 seeds, θ-canonical `RMSE_mu` | `results_w1_ladder/round_v5_1/TRADEOFF_V51.csv` (240 rows) |
| Region counts | City Scanner 4 regions; `argmax_group` = R2 in 240/240 w1 runs | `CS_PHI_DECISION.json`; v5.1 report §2.2 |

No City Scanner value, margin, seed set, contrast or threshold below was chosen after
seeing any Part-B/C1 RMSE. There is no Part-B/C1 RMSE: no training is run in this round.

## 2 Units, index sets and estimands (fixed now)

* **Design unit (Datasets A1):** one training *run*. For SensorScope and U-Air the run
  index is the model seed (1…20, shared across arms); the design is *paired by seed*.
* **Design unit (City Scanner):** one *event trace* (10 traces, seeds 32001–32010). At the
  currently available replication `r = 1`, the model seed equals the trace seed, so each
  trace contributes exactly one `raven` and one `fedavg_window` run and pairing is by trace.
* **Arms in scope:** `raven` and `proj_beta` on SensorScope and U-Air; `raven` on City
  Scanner. `proj_beta` is not evaluated on City Scanner: no frozen City Scanner
  `proj_beta` runs exist in the inputs, and none may be trained in Part A.
* **θ-canonical rule (U-Air / SensorScope values):** `A1_DESCRIPTIVE` uses
  `results_w1_ladder/round_v5_1/TRADEOFF_V51.csv` only — the round-v5.1 θ-canonical
  `RMSE_mu` (18 U-Air rows are `theta_trigger`, the rest `final_metrics`) and the
  θ-canonical `Delta_group`. The round-v4 values (`round_v4/TRADEOFF.csv`) are used for
  the FedAvg reference in the *power* section only, as a cross-check of paired SD, and are
  labelled as such. The v5.1 rule re-scores the prediction endpoints; it does not reopen
  any v5 verdict and is not reopened here.
* **City Scanner values:** the frozen per-trace rows of
  `results_c1_cityscanner/round_v1/tables/CS_E3.csv` (arms `raven`, `fedavg_window`).
  These are not θ-re-scored: the round-v5.1 θ trigger is documented on
  `{uair} × {30007,30016,30018}` only. Whether the underlying final-window
  non-aggregation defect can also fire in the City Scanner pipeline is **not
  established by this round** and is filed as an errata item (§8, E-A1-3); no re-score
  is invented here.
* **Relative paired differences (the H2/H3 scale is relative, not absolute):**

  ```
  d_s = RMSE_mu(arm, s) / RMSE_mu(fedavg_window, s) − 1        (per paired unit s)
  T_s = Delta_group(arm, s) − Delta_group(fedavg_window, s)     (per paired unit s)
  ```

  All H2/H3 statements are relative to the *seat-matched* `fedavg_window` run of the same
  seed/trace. A positive `d_s` means the arm predicts worse than `fedavg_window`.
* **Structural direction:** smaller `Delta_group` is better. H1 asks
  `Delta_group(arm) < Delta_group(fedavg_window)`, i.e. `median(T_s) < 0` one-sided.

## 3 A1.0 — the fixed hypothesis sequence (one chain per `(dataset, arm)`)

Fixed *before* computation, at full α = 0.05, tested strictly in order. A later
hypothesis in a chain is tested only if the previous one in that chain was rejected:

1. **H1 (structure).** `Delta_group(arm) < Delta_group(fedavg_window)`.
   Statistic: two-sided-consistent **paired Wilcoxon signed-rank** test on
   `T_s` (one-sided, `alternative = "less"`, i.e. `median(T) < 0`), n = 20 (SensorScope,
   U-Air) / n = 10 (City Scanner). Ties handled by the scipy default mid-rank
   normal approximation with continuity correction (`method="auto"`, reported);
   exact distribution used if scipy selects it. Reject iff `p_H1 < α_allocated`.
2. **H2 (prediction, non-inferiority).** `RMSE_mu(arm)/RMSE_mu(fedavg_window) − 1 < δ`.
   Decision statistic: the **Hodges–Lehmann (HL) estimate** `θ̂ = median over all pair
   averages (d_i + d_j)/2` of the paired relative differences, plus the **upper bound of
   its one-sided 95 % confidence interval** `U`.
   * Primary `U` (**preregistered now**): `U_wilcox`, the **Wilcoxon-inverted
     distribution-free bound**, written as an exact order statistic so its convention
     cannot drift. Let `W_norm` be the `N = n(n+1)/2` Walsh averages
     `(d_i + d_j)/2`, `i ≤ j`, sorted ascending (0-based indexing), and let `F` be the
     exact null CDF of the signed-rank statistic `W+`. Define
     `c_lo = max{c : F(c) ≤ 0.05}` and `c_hi = min{c : F(c) ≥ 0.95}`. Then
     * **one-sided 95 % upper bound** `U_wilcox = W_norm[c_hi]`,
     * **one-sided 95 % lower bound** `L_wilcox = W_norm[c_lo]`,
     the two-sided 90 % interval being `[W_norm[c_lo], W_norm[c_hi]]`. Derivation
     (verified numerically in the script): `P(reject "greater" at 0.05 | θ)` is
     increasing in `θ`, so the acceptance region of that one-sided lower-tail test is
     `{θ : W+ > c_lo} = [W_norm[c_lo], ∞)`; symmetrically the one-sided upper-tail test
     accepts `{θ : W+ < c_hi} = (−∞, W_norm[c_hi]]`. Coverage targets are one-sided:
     `P(θ ≤ U_wilcox) ≥ 0.95` and `P(θ ≥ L_wilcox) ≥ 0.95`.
     `F` is the exact distribution (`scipy.stats._wilcoxon._get_wilcoxon_distr`); if it is
     unavailable the normal approximation `floor(m ± z_0.95 s)` is used with
     `m = n(n+1)/4`, `s = sqrt(n(n+1)(2n+1)/24)` and the substitution is recorded in the
     output. The script verifies each bound against
     `scipy.stats.wilcoxon(..., alternative="less"/"greater")` on the same data, and the
     verification is reported in the execution report. The HL estimator is the median of
     the same `W_norm`, so the point estimate and the interval come from one coherent
     Wilcoxon inversion.
   * Secondary, reported but **not** the decision (labelled as such):
     `U_boot` = basic (reflection) bootstrap upper endpoint, resampling paired units,
     `B = 10 000`, `seed = 20261003`; and `U_norm = θ̂ + z_0.95 · SE` with
     `SE = sd(d_s)/√n`, `z_0.95 = 1.6448536269514722`.
   * **Reject H2 iff `U_wilcox < δ`** (the whole one-sided interval lies below the margin).
3. **H3 (prediction, superiority).** The same estimator family excludes 0 from below:
   **H3 tested only if H2 was rejected in the same chain** (and its own p-value is not a
   substitute). **H3 rejected iff `L_wilcox > 0`** with `L_wilcox` as defined under H2.
   Reported secondary (not the decision): the two-sided `[q_0.025, q_0.975]` bootstrap
   interval of the same `B = 10 000` bootstrap with seed 20261003.
   * `H3_reject = "not tested (H2 not rejected)"` when H2 fails; it is never `True` there.

α allocation across chains. Chains are the `(dataset, arm)` pairs. Within one dataset the
chains form one **Bretz–Maurer–Brannath–Posch graphical family** with
*equal initial weights* `w = 1/K` (`K` = number of chains in that dataset: 2 for
SensorScope, 2 for U-Air, 1 for City Scanner) and the **Holm transition matrix**
`g_ij = 1/(K−1)` for `i ≠ j`, `g_ii = 0`. A chain that completes (all hypotheses tested)
releases its weight to the remaining chains; a chain whose *current* hypothesis is not
rejected is stopped and its weight is propagated. The realised allocation `α_allocated`
of each tested hypothesis is recorded. **Datasets are never pooled**; City Scanner is a
family of size 1.

## 4 Margins (declared now, never revisited)

| dataset | margin | status |
|---|---|---|
| SensorScope | δ = 0.5 % | unchanged from v5 |
| U-Air | δ = 0.5 % | unchanged from v5 |
| City Scanner | **δ_CS = 2 %** | declared in this file **before** any A1 number; justified by the 13 % paired SD at n = 10; **never revisited** |

δ is a bound on the relative paired difference of `RMSE_mu`, i.e. H2 is
"worse than `fedavg_window` by less than δ". A margin is not an equivalence claim:
H2 passing means "not detectably worse than δ", not "equal".

## 5 A1.1 / A1.2 — outputs, labelling and power (fixed now)

* `A1_DESCRIPTIVE.csv` — one row per `(dataset, arm)` in scope, columns exactly
  `ds, arm, H1_p, H1_reject, H2_hl, H2_ub95, H2_reject, H3_reject,
  power_H2_at_delta, label` (no extra columns; supplementary columns and the
  α-allocation trace go to `A1_DESCRIPTIVE_DETAIL.csv`).
  `label = "post hoc descriptive"` on **every** row. Every value in this file is
  computed on data that already existed when the frame was written: **these rows must
  never be cited as confirmatory evidence.** They show what the fixed frame reads on
  data that already exist. `power_H2_at_delta` in this file is the power at `θ = 0`
  (the non-inferiority null-side value), with δ = δ_CS = 2 % for City Scanner and the
  corresponding δ otherwise; the full power table is `A1_POWER.csv`.
* `A1_POWER.csv` — one row per `(dataset, margin, scenario)`. Power is computed with
  the **observed paired SD** `sd(d_s)` and the n actually available, using the normal
  approximation to the preregistered one-sided decision rule:
  `power(θ) = Φ( (δ − θ)/SE − z_0.95 )`, `SE = sd(d_s)/√n`. Reported at
  `θ ∈ {0, δ/2, δ}` (`θ = 0` is the headline column; `θ = δ` is the "already at the
  margin" case, where power is only 0.05 by construction).
  Two-sided-`t` variant (`df = n−1`) is reported alongside as a robustness column.
  `MDE_80 = δ − (z_0.80 + z_0.95)·SE` is reported: the smallest true relative
  difference at which the rule reaches 80 % power.
  **Testability rule, fixed now:** H2 is called *testable* on a dataset iff
  `power(θ = 0) ≥ 0.80`, i.e. iff `MDE_80 ≤ 0`. Otherwise the verdict is
  *not testable at this n*, and the report says so plainly.
* **City Scanner replication scenarios (A1.2, protocol §1.2).** n = 10 traces ×
  r model seeds, `r ∈ {1, 3, 5}`. The variance model is the trace-cluster one:
  `Var(θ̂) = σ²_B/n + σ²_W/(n·r)`, with
  `σ²_total` = observed variance of `d_s` over the 10 traces at `r = 1` and
  `σ²_B`, `σ²_W` its between-/within-trace components.
  * The estimand of `σ_W²` in that model is fixed now: the within-trace variance of the
    paired relative difference `d_s`, and **specifically `σ_W` = the SD of the model-seed
    scatter of one arm's relative RMSE on a fixed trace** (equivalently `SD(d)` when two
    runs of the *same arm* on the *same trace* differ only in the model seed). That is
    exactly the quantity Part B's B0-b probe estimates. The two variance components are
    defined by the standard partition `σ_total² = σ_B² + σ_W²` at `r = 1`.
  * **B0 is not available** (Part B was not authorized), so `σ_W` cannot be measured from
    model-seed replicates: no City Scanner arm has ever been re-trained under a second
    model seed. Every City Scanner number with `r > 1` is therefore conditional on an
    admission, and the round reports the whole admissible range instead of one number:
    * `S0` — `σ_W = 0`, `σ_B = σ_total`: extra model seeds buy nothing and `r` is
      irrelevant. **Lower** bound on the attainable power at any `r`.
    * `S1` — `σ_W = σ_B` (neutral correlation): the within-trace scatter equals the
      between-trace scatter of the trace means. Mid reading.
    * `S2` — `σ_W = min(0.0980, σ_total)`, where 0.0980 is the SD across the 10 traces of
      the seed/trace-matched relative difference `raven_wo_design` vs `raven`
      (`results_nodesign_supplement/round_v1/tables/cityscanner_seed_rows.csv`). This
      second arm shares `raven`'s traces and model seeds and differs only in its
      π^tar support, so its contrast with `raven` removes the trace effect and its
      scatter is a **direct pilot estimate of the within-trace/within-seed scale**
      `σ_W` — not of `σ_B`. **Upper** (most optimistic) admissible reading; if
      `σ_W² > σ_total²` the scenario is reported as inadmissible instead of clipped
      silently. `σ_B² = max(σ_total² − σ_W², 0)`.
    * `S2` is the largest within-trace scatter any available City Scanner pilot
      supports; S0 is the smallest. If even S2 leaves H2 untestable, no `r` can rescue
      it, and that is the plain verdict. All rows carry `proxy_flag = proxy`, a
      `proxy_source` string and a `proxy_status` string saying that B0-b did not run.
    * A **trace-cluster bootstrap** Monte-Carlo (`B = 800`, `10 000`-order rule,
      `seed = 20261003`, 4000 replications) is run for every City Scanner scenario and
      `r ∈ {1, 3, 5}`, and reported next to the normal approximation as
      `power_boot_cluster`.
    * Every row of `A1_POWER.csv` carries `proxy_flag` and a `proxy_source` string.
  * A `trace-cluster bootstrap` variant (`B = 10 000`, seed 20261003, resampling the 10
    traces and, within a resampled trace, the `r` model seeds) is run for the City
    Scanner scenarios and reported in `A1_POWER.csv` as `power_boot_cluster`.

## 6 Sensitivity rule (declared now)

**Every estimate in this round is recomputed with trace/model seed 32005 excluded**
(protocol §0: seed 32005 carries a +39 % `raven`/`fedavg_window` ratio and is the single
dominant contributor to the +5.59 % mean on City Scanner). The exclusion applies to the
City Scanner chain (`n = 10 → 9`) and, for completeness, to every other chain
(`n = 20 → 19`; seeds are named 30001… and 1…, so "32005" exists only on City Scanner —
the other datasets' rows are recorded as `not applicable`).

**The exclusion is a sensitivity analysis and is never primary.** Primary rows use the
full seed/trace set. The no-32005 values go to `A1_SENSITIVITY_NO32005.csv`. No decision
in `A1_DESCRIPTIVE.csv` is taken from the sensitivity file, and no margin, arm, contrast
or seed set is changed as a result of it.

## 7 Stop rules and what this round will not do

* Part A is read-only: no training, no `build()` forward pass, no re-scoring, no new
  traces, no new model seeds. If a required number does not exist, the cell is `TBD`
  with the reason — never a substitute quantity.
* No Part-B (C1) run of any kind, at any r, with any arm. No `scripts/c1_deletion_driver.py`
  is created. Part B requires the exact phrase `授权 C1 训练`.
* No margin, arm, contrast, seed, endpoint, α or bootstrap seed is changed after seeing
  any number in this round.
* Writes are confined to `results_gatekeeping/round_v1/`. `src/`, the manuscripts, every
  existing results directory, `tdrive_protocol_seal_r1/`, `artifacts/` are read-only.
  X1, PATH_A NO2, full `build()`, and git are not touched.
* **Post-hoc labelling rule:** if anything is computed after a result was seen, it is
  labelled `post hoc` in the file and the report and is excluded from every decision rule.

## 8 Known open items registered before execution (errata candidates)

* **E-A1-1.** The `power_H2_at_delta` column of `A1_DESCRIPTIVE.csv` is power at `θ = 0`
  only; the θ = δ/2 and θ = δ rows live in `A1_POWER.csv`. Readers must not read the
  single column as a power curve.
* **E-A1-2.** City Scanner `H1`/`H2` use n = 10 traces, not 10 independent replicates of
  the data-generating process: the 10 traces are 10 event traces drawn over the same
  underlying City Scanner visit data, and no trace generator exists in the repo. A
  significant City Scanner row is therefore a statement about these 10 traces.
* **E-A1-3.** Whether the round-v5.1 final-window/θ defect can fire in the City Scanner
  pipeline is not established. `A1_DESCRIPTIVE` uses the frozen City Scanner numbers as
  published; no θ re-score was applied or invented.
* **E-A1-4.** `raven_wo_design` exists for City Scanner but is **not** an arm of the A1
  hierarchy (the protocol fixes the comparator as `fedavg_window`). Its only role here is
  the S1 within-trace proxy of §5.
* **E-A1-5.** The `proj_beta` City Scanner cell of the protocol's arm list (§1.1 names
  arms `raven`+`proj_beta` for SS/U-Air and `raven` for CS) is honoured as written: no
  `proj_beta` row is produced for City Scanner, and this is stated in the report rather
  than filled with `raven_wo_design` or `fedau_window`.
* **E-A1-6.** `H1_p` is a Wilcoxon signed-rank p-value and therefore has a resolution
  floor: for n = 20 paired units the smallest attainable value is `2^-n = 9.54e-07` and
  several chains sit exactly on that floor (all paired differences share a sign). A row at
  the floor means `p ≤ 9.54e-07`, not a measured value below it. Reported as-is in
  `A1_DESCRIPTIVE.csv` so the file matches the preregistered column definition; explained
  in `EXECUTION_REPORT.md`.

## 9 No-fabrication statement

Every number in `A1_DESCRIPTIVE.csv`, `A1_POWER.csv`, `A1_DESCRIPTIVE_DETAIL.csv` and
`A1_SENSITIVITY_NO32005.csv` is produced by `A1_ANALYSIS.py` from the read-only inputs of
§2 and §6 (input sha256 recorded in `MANIFEST.sha256`). No cell is imputed, rounded up,
or replaced by a different quantity. `TBD` is used wherever a value cannot be computed,
with the reason stated in the row and in `EXECUTION_REPORT.md`. The Part-A rows of
protocol §4 that belong to Part B (`B0_REPRO.json`, `B0_SEED32005_PROBE.csv`,
`C1_MAPS.json`, `C1_RUNS.csv`, `C1_PRIMARY.json`, `C1_SECONDARY.csv`, `C1_A1_CHAINS.csv`,
`C1_SENSITIVITY_NO32005.csv`) are **not** produced by this round, because Part B was not
authorized; they are listed in `EXECUTION_REPORT.md` as not produced, with the reason.

---
---

# AMENDMENT 1 — Part B (C1 training) authorized, r = 3

**Registration t3.** This block was written and its hash recorded in `MANIFEST.sha256`
**before any B1 run started** and **before any C1 RMSE existed** (no City Scanner run under
any new arm or extra model seed had been trained at that moment). It is an *append-only
extension* of this preregistration: nothing above this line was edited, and the whole of
§0–§9 remains in force for Part A. Scope of the amendment: **protocol §2 (Part B) only**.
Part C (protocol §3) stays out of scope.

## A1 Authorization (verbatim)

The user's written authorization, received through the delegating agent, is:

> 授权C1训练，r=3

(The protocol's canonical form of the phrase is `授权 C1 训练`; the authorization string as
received is quoted above verbatim, including the appended `，r=3`.)

Consequences, fixed now and not revisitable:

* Part B (protocol §2) **is authorized**. The §7 stop rule "No Part-B (C1) run of any kind,
  at any r, with any arm. No `scripts/c1_deletion_driver.py` is created." is superseded
  **for Part B only**; it remains true of Part A.
* The replication is **r = 3**, with model seeds
  `{s, s + 100000, s + 200000}` for every trace seed `s ∈ {32001 … 32010}`.
* **r is fixed at 3 and is never raised**, whatever any C1 RMSE shows (protocol §2 B1).
* "Datasets are never pooled" is unchanged: this amendment concerns the City Scanner block
  (`cityscanner_nyc_pm25`) only. SensorScope and U-Air are not touched.

## A2 Run plan (registered before the first run)

Arms (protocol §2 B1). `reused` means the frozen row at model seed `s` is read, never
re-trained; the extra model seeds `s + 100000, s + 200000` are trained.

| arm | runner `method` | key-level π^tar | deleted share ρ (realized) | runs at r = 3 |
|---|---|---|---|---|
| `fedavg_window` | `fedavg_window` | (π^tar unused, Design off) | 0 | 10 reused + 20 new |
| `raven_wo_design` | `raven_wo_design` | (π^tar unused, Design off) | 0 | 10 reused + 20 new |
| `raven_ctrl` | `raven` | control = `build_pi_target(split="test")` | ≈ 14.35 % | 10 reused + 20 new |
| `raven_ctrl_floor` | `raven` | control with every zero key set to π_floor, renormalized | 0 (expected) | 30 new |
| `raven_M1mu` | `raven` | M1 (ACS) rescaled within region to marginals μ | ≈ 1.0 % | 30 new |
| `raven_M2mu` | `raven` | M2 (NYC 311) rescaled within region to marginals μ | ≈ 1.0 % | 30 new |

* **New runs: 150**, not the ≈130 estimated in protocol §2 B1. The protocol's own arm table
  marks **three** reused arms (`fedavg_window`, `raven_wo_design`, `raven_ctrl` = frozen
  RAVEN) while its run count `3·10·r + 2·10·(r−1)` charges extra seeds for only two. The
  B1 rule "the reused arms then also need the extra model seeds" is applied to **all three**
  reused arms, because the primary contrast `raven_ctrl` vs `raven_ctrl_floor` must be
  balanced at r = 3 (a 1-seed control against a 3-seed mechanism arm would not be). This is
  a *coverage increase* registered here, before any run: no map, margin, seed, contrast or
  endpoint is chosen after seeing any C1 RMSE.
* Traces: the 10 frozen City Scanner event traces (seeds 32001–32010), unchanged. Same
  frozen μ (test region share), same `s_max`, same windows (100) and same λ as the frozen
  CS runs — inherited from `scripts/run_nodesign_supplement.py` (`p2.LOCAL_STEPS`,
  `p2.S_MAX`) and from `CS_TRAIN_SETUP.json` / `CS_PHI_DECISION.json`.
* Driver: `scripts/c1_deletion_driver.py` imports `build_setup` and `train_one` from
  `scripts/run_nodesign_supplement.py` and replaces **only** `setup["pi_target"]` per arm.
  The imported module's output root is redirected into `results_gatekeeping/round_v1/`
  (an output-path redirection only; the training path is untouched), and at extra model
  seeds the trace directory is presented under the model-seed name via a directory
  junction (again a path redirection only) so that `train_one` trains trace `s` at model
  seed `s + 100000·j`, `j ∈ {0,1,2}`.

### A2.1 Map construction (fixed now)

* Key universe: the key-level support returned by `build_pi_target(split="test")` — the
  same 1164-key object the frozen runs use. `M1_mu`/`M2_mu` are also placed on that
  universe (they are read from `MAPS_KEY_LEVEL.csv`, rows restricted to it), so that after
  region-matching **every arm has the same region marginals = μ on the operative key set**
  and only within-region shape and the zero pattern differ. Registered reason: on the raw
  3568-row cross product of `MAPS_KEY_LEVEL.csv`, phantom `(cell, stratum)` combinations
  carry mass, so the real support's region marginals would deviate from μ by up to 7.0 pp
  and the arms would not be region-matched. Both variants' numbers are recorded in
  `C1_MAPS.json`.
* π_floor = the **smallest positive control key mass** over the control map's key universe.
* `control_floor` is exactly protocol §2 B1: control map, every zero key set to π_floor,
  renormalized. Its region marginals are **not** re-matched to μ (the protocol does not ask
  for it); the resulting deviation is reported next to the structural guardrail.
* `M1_mu`/`M2_mu`: per region `r`, every key's mass is multiplied by `μ_r / Σ_{keys in r}`
  of the source column, then renormalized; region marginals therefore equal μ exactly.
* **Hard coverage requirement:** the driver must contain every risk-set key of every trace.
  A missing key is a hard error and stops the run; it is never treated as a zero.

### A2.2 Realized deleted share ρ

`ρ` is recomputed exactly as `scripts/exogenous_target_cityscanner.py` does it: over the
delivered units of events with `U = 1` on non-test splits, the share whose
`(client_id, stratum)` key carries π^tar = 0, per trace. For `fedavg_window` and
`raven_wo_design` the realized share is **0** because ζ is not applied at all (Design off);
the share the control *map* would delete (14.35 %) is reported separately in `C1_MAPS.json`
as a structural reference and is never used as those arms' ρ.

## A3 B0 (registered before B1)

* **B0-a (hard gate).** The driver must reproduce, **bit-exactly** (`|Δ| ≤ 1e-12` on
  `RMSE_mu`, `WorstGroupRMSE`, `Delta_group`, `Delta_c_s`, plus matching `eventtrace_hash`),
  frozen `raven` seed 32001 (`results_c1_cityscanner/round_v1/…/raven/seed32001/CS_ACCEPTED.json`)
  and frozen `raven_wo_design` seed 32001 (`results_nodesign_supplement/round_v1/…/raven_wo_design/seed32001/ACCEPTED.json`).
  Result → `B0_REPRO.json`. **A failure stops everything**: no B0-b, no B1, no B2.
* **B0-b (diagnostic, changes no later rule).** Trace 32005 only, arms `raven` and
  `raven_wo_design`, model seeds `{32005, 132005, 232005, 332005, 432005}`.
  Result → `B0_SEED32005_PROBE.csv` (+ a JSON summary). The verdict (trace-driven vs
  training instability) is reported; it does **not** change the primary, the arm list, the
  seeds, r, or any decision rule.

## A4 B2 — estimators (one primary)

Estimand unit: the **trace** (10 traces), cluster = trace. For arm `a` and trace `t`
`R_a(t) = (1/r) Σ_j RMSE_mu(a, t, s_t + 100000·j)` (trace-level mean over the r = 3 model
seeds), and the paired relative difference against a reference `b` is
`d_t = R_a(t)/R_b(t) − 1` (positive ⇒ `a` predicts worse than `b`). The trace-level
variant `mean_j (RMSE(a,t,j)/RMSE(b,t,j) − 1)` is reported as a declared robustness column
and is never a decision.

Estimator family (identical to Part A §3): HL `θ̂` = median of the Walsh averages
`(d_i+d_j)/2, i ≤ j`; the Wilcoxon-inverted one-sided bounds `L = W_norm[c_lo]`,
`U = W_norm[c_hi]` with the exact null CDF of `W+` (the same implementation as
`A1_ANALYSIS.py`, cross-checked against it); two-sided paired Wilcoxon signed-rank on the
`d_t`.

**Trace-cluster bootstrap** (primary interval, `B = 10000`, `seed = 20261003`): each
resample draws 10 traces with replacement and, within each drawn trace, r = 3 model seeds
with replacement from that trace's r runs of each arm; `θ̂*` is the HL of the resampled
`d*`. Primary interval = **percentile** `[q_0.025, q_0.975]` of `θ̂*`; the basic
(reflection) interval and the Wilcoxon-inverted `[L, U]` are reported as secondaries.

**Primary (single test, no multiplicity adjustment).** `H_mech`:
`RMSE_mu(raven_ctrl) > RMSE_mu(raven_ctrl_floor)`, i.e. `d_t = R_ctrl(t)/R_floor(t) − 1`.
Reading, mechanical:
* primary CI lower bound > 0 → **deletion causes a prediction cost**;
* primary CI inside `±δ_CS` (i.e. `lo ≥ −0.02` and `hi ≤ +0.02`) → **no detectable
  deletion cost** at this n;
* otherwise → **inconclusive**.

**Structural guardrail (reported next to the primary, never a substitute for it):**
`Δ_group` and `Δ_c-s` of `raven_ctrl_floor` vs `raven_ctrl` (trace-level means and the
paired contrast), plus the share of the FedAvg→RAVEN `Δ_group` gain retained,
`retained = (Δ̄_group(fedavg) − Δ̄_group(floor)) / (Δ̄_group(fedavg) − Δ̄_group(ctrl))` with
`Δ̄` the trace-level mean; if the denominator ≤ 0 the share is `TBD` with that reason.

**Secondary family (Holm step-down within this family, α = 0.05, m = 4):**
1. `raven_M1mu − raven_ctrl`
2. `raven_M2mu − raven_ctrl`
3. `raven_ctrl_floor − raven_wo_design` (the cost of the tilt alone)
4. dose-response: OLS slope of `RMSE_mu` on realized `ρ` over the 6 arms × 10 traces
   (trace-level means), with the same trace-cluster bootstrap for its CI and a bootstrap
   p-value `2·min(P*(slope* ≤ 0), P*(slope* ≥ 0))`; Holm order by p ascending, reject while
   `p_(k) ≤ 0.05/(m−k+1)`.
   A declared robustness variant (reported, **not** a Holm member): the same slope over the
   four RAVEN-Design arms only (`raven_ctrl`, `raven_ctrl_floor`, `raven_M1mu`,
   `raven_M2mu`), which share all machinery and differ only in π^tar support.

**Confirmatory A1 chains** (the only confirmatory prediction statements of this round):
`H1 → H2(δ_CS) → H3` for `raven_ctrl_floor`, `raven_M1mu`, `raven_M2mu` vs
`fedavg_window`, exactly as Part A §3, with the graphical Bretz–Maurer–Brannath–Posch
α split: the City Scanner family now has **K = 3** chains, equal initial weights `1/3`,
Holm transitions `1/(K−1) = 1/2`. Trace-level means at r = 3 on both sides.
* H1: `wilcoxon(T_t, alternative="less")` with `T_t = Δ_group(arm,t) − Δ_group(fedavg,t)`.
* H2: decision `U_wilcox < δ_CS = 0.02`. The p-value that drives the graphical allocation is
  `watson_H2 = wilcoxon(d_t − δ_CS, alternative="less").pvalue`, which is exactly equivalent
  to the `U_wilcox < δ_CS` rule at the 5 % level (consistency verified in Part A) and keeps
  the allocation and the decision coherent. Part A's normal-approximation p-value
  `Φ((θ̂ − δ_CS)/SE)` is reported alongside as `p_H2_normal_A1impl`, and both readings of
  `H2_reject` (`rule` = `U_wilcox < δ_CS` gated by H1; `graphical` = Part A's implementation)
  are written to the output. A disagreement between them is reported, never hidden.
* H3: tested only if H2 is rejected; rejected iff `L_wilcox > 0`.

**Also reported:** `WorstGroupRMSE` and per-region RMSE `R0–R3` for every arm, the per-run
table with trace 32005 marked, and every estimate recomputed with trace 32005 excluded.

## A5 Sensitivity rule (unchanged from §6)

Every estimate of this Part is recomputed with trace 32005 excluded (n = 10 → 9) into
`C1_SENSITIVITY_NO32005.csv`. **The exclusion is a declared sensitivity analysis and is
never primary.** No decision is taken from it.

## A6 B3 — decision rules (written before B1; applied mechanically afterwards)

| outcome | what may be written later (paper paused) |
|---|---|
| `H_mech` CI > 0 **and** the floor retains ≥ 50 % of the `Δ_group` gain | "On City Scanner the prediction cost is caused by deleting delivered units whose keys carry no evaluation-derived mass; a floored map keeps X % of the structural gain without that cost." |
| `H_mech` inside ±δ_CS | "Deleting 14 % of delivered units has no detectable prediction cost at n = …; the Design cost reported earlier is not a deletion effect." The seed-32005 probe then decides how that row is described. |
| `H_mech` inconclusive | Report the CI and power. No mechanism claim. Do not add traces or model seeds. |
| B0-b shows the +39 % only at the original model seed | That seed's contribution is described as a training-instability outlier, with the probe as evidence; the primary is still computed on all traces. |

## A7 Additional stop rules for Part B

* No map, margin, seed, contrast, endpoint or bootstrap setting is chosen after seeing any
  C1 RMSE. Everything above is fixed before the first B1 run.
* `r` is never raised above 3 after starting. No trace is added; no model seed outside
  `{s, s+100000, s+200000}` enters the B1 grid (the B0-b probe seeds `s+300000, s+400000`
  are diagnostic only and never enter a B1 endpoint).
* Writes stay inside `results_gatekeeping/round_v1/` and `scripts/c1_*.py`. `src/`, the
  manuscripts, every existing results directory, `tdrive_protocol_seal_r1/`, `artifacts/`,
  X1, PATH_A NO2, full `build()` and git are not touched. Frozen inputs are read-only.
* Failures: if a run fails, it is recorded in `C1_FAILURES/` and in the report and the rest
  continues; the failure list is reported plainly.
* **Post-hoc labelling rule** (unchanged): anything computed after a result was seen is
  labelled `post hoc` and excluded from every decision rule.

## A8 No-fabrication statement (Part B)

Every number in `B0_REPRO.json`, `B0_SEED32005_PROBE.csv`, `C1_MAPS.json`, `C1_RUNS.csv`,
`C1_PRIMARY.json`, `C1_SECONDARY.csv`, `C1_A1_CHAINS.csv` and `C1_SENSITIVITY_NO32005.csv`
is produced by `scripts/c1_deletion_driver.py` and `scripts/c1_analysis.py` from the frozen
inputs and the new training runs; input and artefact sha256 are recorded in
`MANIFEST.sha256`. No cell is imputed; `TBD` is used with a stated reason wherever a value
cannot be computed.

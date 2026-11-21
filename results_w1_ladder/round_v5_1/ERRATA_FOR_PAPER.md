# W1 round v5.1 — ERRATA_FOR_PAPER.md (supersedes `results_w1_ladder/round_v5/ERRATA_FOR_PAPER.md`)

Round directory: `results_w1_ladder/round_v5_1/`
Protocol: `PROTOCOL.md` (sha256 `4e1c52372a9bb155eb9f5db142bcf3d9ad9f56df8a7683bd9a0ac9c1c748742e`)
Amendments: `AMENDMENTS.md` (sha256 `113429b97ef10d04d8bc99ba49e4d99ca541464406dfcefaa48c76e14ff359e4`),
both hashed into `MANIFEST.sha256` before any v5.1 number was computed.

This file replaces the round-v5 errata. The round-v5 text is superseded, not
supplemented: where the two disagree, this file is authoritative.

**Status line added 2026-10-03 (record Part IV, item 4).** Round `round_v5_1a`
(`AMENDMENT_AM-6.md`, `O_GATES_RERUN.json`, `ORACLE_EVIDENCE.json`) re-ran the
A1′ oracle and its gates and **did not change any verdict in this file**. The
superseding facts: the v5.1 oracle was *suboptimal*, not merely imprecise (its
O-G1 sample objective exceeded a feasible comparator by `+1.11e-06`); AM-6
replaced it with the two-multiplier dual and the outcome is
`O-G0 stationarity 6.67e-01 (fail)`, `O-G1 objective 9.64e-12 (fail on 7/200)`,
O-G0 primal and complementary slackness pass, O-G2 passes exactly, the oracle is
optimal to `1e-13` in objective value on a small-K brute force (142 cases, worst
`9.95e-14`) and no feasible perturbation improves it (`122 094` points,
improvement `0.0`). **A1′ therefore remains `approximate` with
`max eps_impl = 2.42e-05`**, `alpha_linf_trained = 0.0` on all 160 cells, and
**all 20 structural contrast verdicts are unchanged with max `|Δpp| = 6.18e-04`**.
The two surviving gate failures are a stationarity-residual artefact
(`τ+2λa` cancellation at `K = 3` near-uniform ball points, multipliers `~1e9`) and
comparator-limited (CLARABEL `optimal_inaccurate` 135/200, raw infeasibility up to
`5.16e-08`). The point-level evidence tolerance (`1e-8`) is still short of the
`1e-12` the rerun set for itself. Nothing in E-v51-1 … E-v51-4 moves, and
`ERRATA_FOR_PAPER_v5_1a.md` was deliberately not written. The v5.1 quantity
`2.4e-05` in E-v51-1 §4 is superseded by `2.42e-05` from the v5.1a measurement
table; the two differ by `2e-07`.

---

## E-v51-1 (replaces E-v5-1) — the trained rules, and what the earlier residual was

**The phrase "reference not numerically stable" is deleted.** It was a statement
about the reference *code path* (a process-cached, parameterised CVXPY problem
warm-started across windows), not about the rules, and it does not belong in the
paper.

What the evidence supports:

1. **The trained rules reproduce their own replay exactly.** Rebuilding α
   window-by-window from each run's own logged `active_clients` / `beta_hat`, with
   `M_r`, `mu` from `W.build_case` and the aggregator classes imported from
   `scripts/w1_v4_train.py` (fresh instance per run, so `Q_0 = 0`), reproduces the
   run's stored `final_metrics` structural endpoints on **120/120 runs**: max
   `|Δ_group − final_metrics.Delta_group| = 4.4e-15` and max
   `|Δ_c-s − final_metrics.Delta_c_s| = 6.9e-15` (tolerance 1e-12). α itself is
   bit-exact on 118/120 runs; the two exceptions differ by 6.45e-09 and 1 ULP and
   their endpoints still agree to ≤ 4.4e-15.
   *Round v5's A1 stop was triggered by the since-amended condition `α L∞ = 0`
   (AM-1); under AM-1 (`α L∞ ≤ 1e-8`, endpoints ≤ 1e-12) the gate passes 120/120,
   observed `α L∞ = 0.0`.*

2. **The earlier residual came from the reference solver, not from drifting
   inputs.** The inputs `M_r`, `μ`, `β̂` and the active set do not depend on the
   server rule: B-G1 confirms the active sets are identical to the frozen `raven`
   run on all 120 runs (0 mismatching windows), and the endpoint residual against
   the unmodified repository replay path in round v5 was 2.1e-06 … 8.6e-05 — a
   property of the warm-started solver path, not of a different problem.

3. **The rule values are certified against an exact projection oracle, or
   reported as approximate with `eps_impl`.** Round v5.1 builds a numpy-only exact
   oracle for both trained rules (protocol §2.1) and gates it (O-G0/O-G1/O-G2,
   `GATES_V51.csv`, `A1P_ORACLE_GATES.json`). Against that oracle, measured
   over 160 arm × dataset × seed cells:

   | cell | max `eps_impl` (group / c-s) | `alpha_linf_trained` range | `alpha_linf_ref` range | verdict |
   |---|---|---|---|---|
   | `proj_beta` / SensorScope | 9.07e-06 / 9.07e-06 | 0.0 | 1.05e-04 … 1.85e-04 | `approximate` (19/20 seeds `certified`) |
   | `proj_beta` / U-Air | 1.03e-05 / 1.03e-05 | 0.0 | 9.11e-05 … 2.14e-04 | `approximate` (13/20 seeds `certified`) |
   | `proj_beta_debt` / SensorScope | 1.26e-05 / 2.42e-05 | 0.0 | 1.54e-04 … 5.74e-03 | `approximate` (1/20 seeds `certified`) |
   | `proj_beta_debt` / U-Air | 2.40e-05 / 2.40e-05 | 0.0 | 3.84e-04 … 1.17e-03 | `approximate` (1/20 seeds `certified`) |

   **The oracle itself did not clear its preregistered gates** (AM-2): O-G2
   passes exactly (uniform control, 0.0 at K = 1…64), but O-G0 fails
   (max stationarity 7.2 / 36.3 against 1e-12) and O-G1 fails (max objective gap
   +1.1e-06 against 1e-12), and the measured `eps_impl` values exceed the
   preregistered 5e-6 budget in all four cells. Per the protocol's stop rule the
   verdict for both arms on both datasets is therefore **`approximate`**, and the
   oracle's structural endpoints are reported as the rule's values with the gap
   `eps_impl` stated next to them. No claim of certification is made.

   Two facts bound the size of the gap: the trained implementations agree with
   the oracle to `alpha_linf_trained = 0.0` on **all 160 cells** at the level the
   round-v5 replay defines as exact, and the residual between them and the oracle
   (1e-05) is one to two orders of magnitude *smaller* than the residual between
   the round-v3/v4 stored reference paths and the same oracle (up to 5.7e-03).
   *E-v5-1's mechanism sentence — "the trained rules reproduce their replay
   exactly; the earlier residual came from the reference solver" — is retained;
   its stability verdict is not.*

4. **Consequence for the paper.** The structural endpoints quoted for
   `proj_beta` and `proj_beta_debt` should either be the oracle values from
   `A1P_IMPL.csv` (`d_group_oracle`, `d_cs_oracle`) or the trained values
   accompanied by the approximate-implementation gap. The two differ by at most
   `eps_impl ≤ 2.4e-05` in endpoint units, which is below the fourth decimal of
   the reported pp differences (max |Δpp| across the 20 structural contrasts
   = 6.2e-04 pp, `A1P_STRUCT_SUMMARY.json`).

5. **The structural verdicts do not move.** Recomputing the Δ_group and Δ_c-s
   rows of `round_v4/TRADEOFF_PAIRED.csv` with the oracle endpoints in place of
   the trained ones (same contrasts, same bootstrap, same Holm family) changes
   **0 of 20 verdicts** (`A1P_STRUCT_PAIRED.csv`). The largest single change in a
   reported pp difference is 6.2e-04 pp (`Delta_group`,
   `proj_beta_debt − proj_beta`, SensorScope).

---

## E-v51-2 — worst-group readings and non-inferiority for the trained rules

The θ-canonical rule (AM-3) unblocks the worst-group analysis that round v5
stopped at A2-G0. All three parts of the gate pass:

* **G0-a**: on the 222 non-trigger rows the θ re-score equals `final_metrics.json`
  **exactly** (max |Δ| = 0.0 on `RMSE_mu`, `Head_RMSE`, `Tail_RMSE`; tolerance
  1e-12) — 222/222, as expected.
* **G0-b**: the trigger set is exactly the pre-fixed
  `{uair} × {30007, 30016, 30018} × all 6 arms` = 18 rows. A sweep of all 240
  runs found **no** trigger outside the set and **no** listed row lacking the
  trigger; in each of the 18 the run's own `window_metrics.json` shows the final
  window (id 79) inactive with `a_r_size = 0` and an empty `alpha`, and the θ
  re-score matches Table II per seed within **1.56e-09 relative** (tolerance
  1e-8).
* **G0-c**: the frozen arms' stored `WorstGroupRMSE` is reproduced within
  **1.95e-09 relative** (tolerance 1e-8) on 80/80 rows.

**Canonical WorstGroupRMSE means (20 seeds, θ-canonical, never pooled):**

| dataset | arm | mean WorstGroupRMSE | worst block |
|---|---|---|---|
| SensorScope | `fedavg_window` | 8.671606 | R2 |
| SensorScope | `inst_cal` | 8.670662 | R2 |
| SensorScope | `proj_beta` | **8.669890** (lowest) | R2 |
| SensorScope | `proj_beta_debt` | 8.671088 | R2 |
| SensorScope | `raven` | 8.670660 | R2 |
| SensorScope | `uniform_window` | 8.672023 (highest) | R2 |
| U-Air | `fedavg_window` | **1.259556** (lowest) | R2 |
| U-Air | `inst_cal` | 1.263038 | R2 |
| U-Air | `proj_beta` | 1.264744 (highest) | R2 |
| U-Air | `proj_beta_debt` | 1.262306 | R2 |
| U-Air | `raven` | 1.263029 | R2 |
| U-Air | `uniform_window` | 1.260944 | R2 |

**`argmax_group` = R2 in 240/240 runs** (all six arms, both datasets,
`A2P_SUMMARY.json.argmax_group_counts = {2: 240}`): the worst of the four UTC
six-hour blocks never changes between arms on this data. Round v5's raw
observation is **confirmed**.

**Non-inferiority, δ_WG = +0.5 %, AM-5 labels** (`WORSTGROUP_NI.csv`):

| dataset | arm | comparator | mean rel diff | 90 % CI | label (AM-5) | Holm p |
|---|---|---|---|---|---|---|
| SensorScope | `uniform_window` | `fedavg_window` | +0.0048 % | [−0.0170 %, +0.0255 %] | `equivalent_zero` | 0.0000 |
| SensorScope | `uniform_window` | `raven` | +0.0158 % | [−0.0169 %, +0.0478 %] | `equivalent_zero` | 0.0000 |
| SensorScope | `proj_beta` | `fedavg_window` | −0.0199 % | [−0.0699 %, +0.0312 %] | `equivalent_zero` | 0.0000 |
| SensorScope | `proj_beta` | `raven` | −0.0089 % | [−0.0282 %, +0.0104 %] | `equivalent_zero` | 0.0000 |
| SensorScope | `proj_beta_debt` | `fedavg_window` | −0.0061 % | [−0.0663 %, +0.0539 %] | `equivalent_zero` | 0.0000 |
| SensorScope | `proj_beta_debt` | `raven` | +0.0048 % | [−0.0353 %, +0.0484 %] | `equivalent_zero` | 0.0000 |
| U-Air | `uniform_window` | `fedavg_window` | +0.1125 % | [−0.2835 %, +0.5694 %] | `inconclusive` | 0.2409 |
| U-Air | `uniform_window` | `raven` | −0.1658 % | [−0.2737 %, −0.0555 %] | `equivalent_gain` | 0.0000 |
| U-Air | `proj_beta` | `fedavg_window` | +0.4142 % | [+0.0246 %, +0.8387 %] | `harm` | 0.3848 |
| U-Air | `proj_beta` | `raven` | +0.1356 % | [+0.0450 %, +0.2281 %] | `equivalent_cost` | 0.0000 |
| U-Air | `proj_beta_debt` | `fedavg_window` | +0.2263 % | [−0.2710 %, +0.7517 %] | `inconclusive` | 0.3848 |
| U-Air | `proj_beta_debt` | `raven` | −0.0545 % | [−0.2311 %, +0.1168 %] | `equivalent_zero` | 0.0000 |

Reading, without over-claim: on SensorScope every NI row is `equivalent_zero`;
on U-Air the trained rules are non-inferior to `raven` (`equivalent_zero` /
`equivalent_cost` / `equivalent_gain`), while against `fedavg_window`
`proj_beta` shows a directional cost of +0.41 % that leaves the +0.5 % margin on
the harmful side but does **not** survive Holm adjustment (p_holm = 0.3848) —
the same directional-not-multiplicity-robust pattern the round-v5 RMSE_μ reading
showed for the same arm pair. The paired Wilcoxon contrast table is
`WORSTGROUP_PAIRED.csv`.

---

## E-v51-3 — prediction statement (AM-5 vocabulary)

**No alignment-to-accuracy benefit is claimed on either dataset, and the word
"better" is not used.**

* **SensorScope** (`A3P_TOST_V51.csv`): all four primary rows are
  `equivalent_zero` — four for four, as the protocol expected. Paired mean
  differences −0.0026 … +0.0012 RMSE_μ, 90 % CIs inside δ_P = 0.0397, every CI
  containing 0.
* **U-Air**:
  `proj_beta − uniform_window` = **equivalent within 0.5 %, with a nonzero cost
  of +0.29 %** (label `equivalent_cost`; mean +0.003418, 90 % CI
  [+0.001290, +0.005512], δ_P = 0.005967, p_tost_holm = 0.0454). The CI lies
  inside the margin *and* excludes 0; under AM-5 that is one label, not two.
  `proj_beta − fedavg_window` = **directional cost of +0.47 %, not Holm-robust**
  (label `harm` on the CI rule; mean +0.004658, 90 % CI [+0.000347, +0.009319],
  p_tost_holm = 0.3137). The other two U-Air rows are `equivalent_gain`
  (costs, i.e. the comparator is not worse).
* **Dose-response** (`A3P_DOSE.csv`): the alignment→accuracy slope includes 0 on
  both datasets. SensorScope slope +0.0325, 95 % CI [−0.0966, +0.1525];
  U-Air slope −0.1224, 95 % CI [−0.2685, +0.0362] — the U-Air point estimate has
  the opposite sign. Implied RMSE_μ change at the largest observed Δ_group gain:
  −0.002263 (SensorScope) and +0.006594 (U-Air); the 95 % CI of the implied
  change excludes the −0.25 % effect on both datasets (`dose_excludes_needed_0.25pct`
  = True), which is the clause that closed R1.
* **MDE** (`A3P_TOST_V51.csv`): at n = 20 and the Holm-adjusted level, the MDE
  exceeds δ_P on exactly one row — U-Air `proj_beta − fedavg_window`
  (0.009336 > 0.005961) — and that row is `harm`, not `inconclusive`.
* **The round-v5 decision is not re-opened**: R1 stays closed as a measured null
  and Part B (R1b) stays closed. The θ-canonical re-run moves the numbers
  slightly (U-Air `proj_beta − uniform_window` from +0.262 % to +0.286 %;
  `proj_beta − fedavg_window` from +0.357 % to +0.391 %) and moves **no**
  verdict: v5 label vs v5.1 label agree on all 8 primary rows once the AM-5
  vocabulary is applied to the v5 CI (`A3P_SIDE_BY_SIDE.csv`).

---

## E-v51-4 — θ-re-sourced U-Air Part B cells

The three U-Air trigger seeds (30007 / 30016 / 30018) carry a known
mirror/θ defect: the run-time metric evaluates the in-memory module instead of
the saved θ (`results_seed_path_audit_r1/`, record items 46–47). The paper
already treats θ as canonical for these cells; section §VII Part B's U-Air
`RMSE_mu` values are the v4 tree values and therefore need re-sourcing.

**Cell-level re-sourcing** (`A3P_RESOURCE_UPAIR.csv`, `A3P_SUMMARY.json`), 20-seed
U-Air `RMSE_mu` means:

| arm | manuscript value (v4 tree) | θ-canonical value | differs at 4 s.f. |
|---|---|---|---|
| `fedavg_window` | 1.18824 | 1.19225 | **yes** |
| `raven` | 1.19111 | 1.19537 | **yes** |
| `inst_cal` | 1.19112 | 1.19537 | **yes** |
| `uniform_window` | 1.18936 | 1.19349 | **yes** |
| `proj_beta` | 1.19248 | 1.19691 | **yes** |
| `proj_beta_debt` | 1.19037 | 1.19470 | **yes** |

The three values named in the protocol prompt (1.19248 / 1.19037 / 1.19112) are
the `proj_beta`, `proj_beta_debt` and `inst_cal` v4 cells; all three change.

**Paired-row re-sourcing** — the U-Air `RMSE_mu` rows of
`round_v4/TRADEOFF_PAIRED.csv` recomputed on θ-canonical values. Every number
below differs from v4 at the 4th significant digit:

| contrast | mean diff v4 → v5.1 | CI lo v4 → v5.1 | CI hi v4 → v5.1 | p_holm v4 → v5.1 |
|---|---|---|---|---|
| `proj_beta − uniform_window` | 0.003120 → 0.003418 | 0.000805 → 0.000901 | 0.005372 → 0.005919 | 0.1332 → 0.1198 |
| `raven − proj_beta` | −0.001363 → −0.001544 | −0.002555 → −0.002812 | −0.000247 → −0.000340 | 0.1332 → 0.1198 |
| `proj_beta − fedavg_window` | 0.004240 → 0.004658 | −0.000764 → −0.000492 | 0.009599 → 0.010110 | 0.3420 → 0.2462 |
| `uniform_window − fedavg_window` | 0.001120 → 0.001240 | −0.004098 → −0.003932 | 0.007099 → 0.007334 | 0.8408 → 0.9273 |
| `proj_beta_debt − proj_beta` | −0.002103 → −0.002212 | −0.004315 → −0.004323 | −0.000024 → −0.000104 | 0.3420 → 0.2276 |

SensorScope Part B cells are unaffected: the SensorScope θ re-score reproduces
`final_metrics.json` bit-exactly on all 120 rows, so its manuscript values stand.

---

## Status of this errata

* No training was run in this round. Part B (R1b) remains closed.
* `results_w1_ladder/round_v5/` was not modified.
* The oracle gates O-G0 and O-G1 **failed** and the O-gate verdicts are
  `approximate`; that failure is reported above and in `GATES_V51.csv` and is
  **not** smoothed over.
* Every number in this file is reproducible from `scripts/w1_v51_*.py` and the
  read-only inputs by the commands recorded in `EXECUTION_REPORT.md`.

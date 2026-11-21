# ERRATA_FOR_PAPER — W1 round v5 (R1 / R3 / R4)

Manuscript edits are paused (protocol header). Everything below is an **item for the
manuscript**, not an edit. Source of each item: `results_w1_ladder/round_v5/`
(`EXECUTION_REPORT.md` carries the full tables and the reproduction commands).

Round v5 did **not** train anything. A1/A2/A3 are read-only re-scorings and re-analyses of
the frozen round-v4/E3 artefacts, and Part B was not run (the A3 rule closes R1 as a
measured null).

---

## E-v5-1 — the `M_r`-drift explanation is false; replace it with the A1 finding

**Current manuscript text (to be replaced).** The sentence in the Design/necessity
discussion that attributes the non-zero trained-vs-replay endpoint residual to a reference
recomputed from inputs that "vary weakly with the model trajectory" / tracks "composition
and mass inputs that vary with the model trajectory". That explanation is unsupported and
must not be printed.

**What A1 measured** (`GATES_V5.csv`, `A1_GSELF.csv`, `A1_SENS_GRID.csv`,
`A1_LEGACY_XREF.csv`):

1. `M_r`, μ and the active set do **not** drift. Rebuilding α window-by-window from each
   run's **own** logged `active_clients` and `beta_hat` with the same aggregator class
   imported from the training script and the replay `M_r` reproduces the run's logged α
   **exactly** (α L∞ = 0) on 118/120 runs, and reproduces both structural endpoints to
   ≤8.9e-16 on **120/120** runs (tolerance 1e-12). The trained rules *are* the rules
   evaluated in replay.
2. The residual is on the **reference side**, and its size is measurable. Recomputing the
   replay path on a 12-cell grid (CLARABEL tolerance × raw/normalised β × cached/fresh
   problem object) moves the structural endpoints by up to 5.8e-06 (SensorScope) /
   6.2e-06 (U-Air) for `proj_beta` and by 1.3e-04 / 6.5e-05 for `proj_beta_debt`.
   The dominant axes are the problem-object axis (fresh-per-window vs cached parameterized
   solve) and, for the debt rule, the solver tolerance — consistent with the near-LP
   conditioning of the debt objective at κ=1000 (quadratic weight 1e-3). The measured
   reproducibility floor is therefore τ_x = 10 × that spread = 5.8e-05 … 1.3e-03, which is
   10–250× larger than the 5e-06 budget implied by the smallest claimed effect (0.005 in
   Δ_group units, bound 1e-3 × 0.005).
3. The residual against the stored reference columns that the round-4 gates read is
   reproduced exactly by this round: `proj_beta` 2.07e-06 (SensorScope) / 2.67e-06 (U-Air)
   on Δ_group; `proj_beta_debt` 2.89e-05 / 3.77e-05; `uniform_window` 0.0.
4. Even the **self-replay identity is not bit-exact**: 2 of 40 `proj_beta` runs
   (U-Air seeds 30001 and 30011) differ from their own logged α by 6.45e-09 and 1 ULP
   respectively (first diverging windows 0 and 37), while their endpoints still agree to
   ≤1e-15. The α-renormalisation guard in the runner does not fire (|Σα−1| ≤ 2.4e-10), the
   support is identical and the sums match to 6e-13, so the difference is solver-path level.

**Replacement text (draft, for the later edit pass).** "The residual between a trained
server-weight rule and its replay is not produced by drifting composition or mass inputs:
the replay reproduces the trained weights exactly on 118 of 120 runs and both structural
endpoints to ≤9e-16 on all 120. The residual is produced by the reference solve. Measured
over a grid of solver tolerances, β normalisations and problem-object reuse, the replay
path reproduces the structural endpoints only to τ_x = 5.8e-05 … 1.3e-03, ten to two
hundred times coarser than the 5e-06 budget implied by the smallest effect the trained
rules claim. The gates for the trained server-weight rules are therefore reported as
**self-replay exact, cross-implementation exploratory (reference not numerically stable)**,
and no tighter claim is made."

**Consequence for the round-4 gate table.** `round_v4/TRAIN_GATES.csv` is not modified and
must not be modified: its `pass` column reflects **B-G1 only** and does not express the
self-replay identity or the cross-implementation tolerance. Round 5's tri-gate file is
`GATES_V5.csv`.

---

## E-v5-2 — trained-rule `WorstGroupRMSE` readings: **not available** in this round (A2-G0 stop), and one U-Air artefact defect must be disclosed

The preregistered `WorstGroupRMSE` column is empty in all 240 rows of
`round_v4/TRADEOFF.csv` (audit item FL-10 / requirement R3). Round 5 re-scored all 240
runs from `checkpoints/final.pt` and hit the mandatory reproduction gate first.

1. **SensorScope reproduces bit-exactly**: 120/120 runs, |ΔRMSE_mu| = |ΔHead| = |ΔTail| = 0.0
   against `final_metrics.json`.
2. **U-Air fails on 18 of 120 rows** — all six arms at seeds **30007, 30016, 30018** —
   with |ΔRMSE_mu| up to 5.66e-02 (1.5 %–5.7 % relative). The recomputation is not the
   problem: over all 240 rows it agrees with the independently published
   checkpoint-based table `RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv`
   to ≤1.9e-09 (`RMSE_mu`) and ≤2.4e-09 (`WorstGroupRMSE`). The three seeds are the
   mixed-sourcing defect already recorded in
   `results_seed_path_audit_r1/C_IMPACT_RECALC.csv` and in
   `ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md` §2A N3.
3. Per protocol §2 A2-G0 ("One failure ⇒ stop A2 and report"), A2 stopped at the gate:
   **no** paired contrast, bootstrap CI, Wilcoxon, Holm or non-inferiority verdict for
   `WorstGroupRMSE` exists in this round, for any arm. `WORSTGROUP_PAIRED.csv`,
   `WORSTGROUP_NI.csv` and the `WorstGroupRMSE` column of `TRADEOFF_V5.csv` are marked
   `TBD_A2_G0_STOP`. The raw per-run re-scored values (not validated scores) are in
   `WORSTGROUP_V5.csv` with their gate flags.
4. The frozen stored `WorstGroupRMSE` of `fedavg_window` and `raven` is reproduced to
   ≤2.36e-09, i.e. **above** the 1e-10 sub-tolerance of the gate but 9 orders of magnitude
   below any reported effect; this is a floating-point path difference and is reported, not
   waived.

**Manuscript consequence.** (a) No worst-group reading and no non-inferiority statement may
be added for the trained server-weight rules in this round — the item stays open, and its
remedy is not a retrain but a decision about which side of the U-Air tree is authoritative
at seeds 30007/30016/30018. (b) If the U-Air `WorstGroupRMSE` numbers are ever printed from
the E3 tree, they must carry the caveat that at those three seeds the tree's
`final_metrics.json` is not reproducible from the same runs' checkpoints, while the Table II
per-seed file is.

---

## E-v5-3 — prediction-endpoint statement in its A3 form (never "better")

R1 asked whether structural alignment converts into prediction. On the existing 20 seeds the
answer is a **measured null**, and the manuscript sentence must be written in the
equivalence / inconclusive / harm vocabulary, never as an improvement.

`R1A_TOST.csv`, δ_P = 0.5 % of the comparator's mean RMSE_μ per dataset, Holm within
dataset × 4 contrasts, 90 % bootstrap CIs (10 000 resamples, seed 20261002):

* **SensorScope — equivalent on all four contrasts.** `proj_beta − uniform_window`
  −0.002057 (−0.026 %), 90 % CI [−0.006221, +0.002199] within δ_P = 0.039697;
  `proj_beta − fedavg_window` −0.001643 (CI [−0.005897, +0.002694]);
  `raven − proj_beta` +0.000739 (CI [−0.000905, +0.002371]);
  `proj_beta_debt − proj_beta` +0.001170 (CI [−0.002201, +0.004935]).
* **U-Air — three equivalent, one harm.**
  `proj_beta − uniform_window` +0.003120 (+0.262 %), 90 % CI [+0.001181, +0.005037],
  δ_P = 0.005947 ⇒ **equivalent** (the harm direction reported by protocol §0.2 is inside
  the preregistered margin). `proj_beta − fedavg_window` +0.004240 (+0.357 %),
  90 % CI [+0.000051, +0.008773], δ_P = 0.005941 ⇒ outside the margin on the harmful side;
  labelled **harm** by the preregistered CI rule, but its Holm-adjusted TOST p = 0.2601,
  so it is *not* a multiplicity-robust harm claim. `raven − proj_beta` −0.001363
  (CI [−0.002336, −0.000421]) and `proj_beta_debt − proj_beta` −0.002103
  (CI [−0.003885, −0.000324]) ⇒ equivalent.
* **Power.** MDE at n = 20 (Holm-adjusted, power 0.8): SensorScope 0.0034–0.0089
  (0.04 %–0.11 % of the comparator mean); U-Air 0.0020–0.0091 (0.17 %–0.77 %). Seeds
  needed for a 0.25 % effect: SensorScope 1–4, U-Air 10–189; for 0.5 %: SensorScope 1,
  U-Air 3–48. The existing n = 20 is adequate for 0.5 % on SensorScope and inadequate for
  0.25 % on U-Air (`proj_beta − fedavg_window` alone needs 189 seeds, above the round's
  60-seed cap).
* **Dose-response** ("more alignment ⇒ lower error", one test per dataset, 80 paired
  observations, seed-cluster bootstrap): SensorScope slope +0.0325, 95 % CI
  [−0.0966, +0.1525]; U-Air slope −0.1079, 95 % CI [−0.2523, +0.0461]. Both CIs include
  zero and the U-Air point estimate has the opposite sign. The implied RMSE_μ change at the
  largest observed Δ_group gain (−0.0697 SensorScope, −0.0539 U-Air) is −0.00226
  (CI [−0.01063, +0.00674]) and +0.00581 (CI [−0.00248, +0.01360]); the change needed for
  a 0.25 % gain is −0.01985 and −0.00297, so the CI excludes the needed effect on both
  datasets (decisively on SensorScope, marginally on U-Air).
* **Decision (protocol §2 A3, mechanical).** "R1 is closed as a measured null. Part B is
  not run." The clause that fires is the dose-response one (both datasets); the
  all-equivalent clause holds only for SensorScope, and the U-Air harm clause names
  `proj_beta − uniform_window`, which is equivalent. Part B additionally lacks the
  authorization phrase `授权 v5 Part B`.

**Caveat to print with any U-Air prediction number.** `round_v4/TRADEOFF.csv` — the
preregistered A3 input — inherits the E3 U-Air `final_metrics.json` values, which at seeds
30007/30016/30018 are not reproducible from the same runs' checkpoints (E-v5-2). An
exploratory repetition of the U-Air analysis with the checkpoint-based `RMSE_μ` leaves all
four verdicts unchanged (equivalent / harm / equivalent / equivalent) and moves the
dose-response slope from −0.1079 to −0.1224 (`A3_ROBUSTNESS_Uair.csv`); SensorScope is
unaffected.

---

## Summary table for the edit pass

| errata | replaces | status in round v5 | evidence |
|---|---|---|---|
| E-v5-1 | the "`M_r` varies with the model trajectory" explanation of the gate residual | measurement available; replacement text drafted above | `A1_GSELF.csv`, `A1_SENS_GRID.csv`, `A1_LEGACY_XREF.csv`, `GATES_V5.csv`, `A1_GSELF_FAIL_DIAG.json` |
| E-v5-2 | the empty `WorstGroupRMSE` column and any planned worst-group claim for the trained rules | **TBD** — A2 stopped at A2-G0 (18 U-Air rows) | `A2_G0_SUMMARY.json`, `A2_G0_FAILURES.csv`, `WORSTGROUP_V5.csv`, `A2_STOP.json` |
| E-v5-3 | any prediction-endpoint sentence that reads as an improvement | measurement available: equivalent / harm / equivalent (never "better") | `R1A_TOST.csv`, `R1A_DOSE.csv`, `A3_SUMMARY.json`, `A3_ROBUSTNESS_Uair.csv` |

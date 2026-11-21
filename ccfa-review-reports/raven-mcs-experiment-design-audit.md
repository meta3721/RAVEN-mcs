# RAVEN-MCS — Experiment-Design Audit (IEEE TMC revision)

```text
Mode: design audit (ccf-experiment-designer; primary mode `design`, result-presentation fields used for supplied results)
Venue and assumptions: IEEE TMC journal revision; method + measurement long paper; project contract TMC-J-R4
  (8 dimensions, weights 0.10/0.20/0.25/0.15/0.10/0.10/0.05/0.05; anchors 1-5; decision threshold 4/10)
Manuscript audited: TO_OVERLEAF_paper_tmc_r1_clean/main.tex, pre-fix state = snapshots/2026-10-03-pre-design-fix/main.tex
  (2230 lines, 17 pp, 0 errors / 0 undefined / 0 overfull). Post-fix line numbers are used throughout; the
  pre-fix state is reachable from the snapshot, and every correction is listed before -> after in Sec. 8.
Authoritative issue list: ccfa-review-reports/raven-mcs-tmc-review-round6.md (R5-x closure table + F1-F4, Sec. 7-8)
Evidence read (read-only; nothing re-run):
  results_w1_ladder/round_v4/{PART_A_REPORT,PART_B_REPORT,PREREG,ERRATA_v3}.md, TRADEOFF.csv, TRADEOFF_PAIRED.csv,
    TRAIN_GATES.csv, FULL_SEED_LADDER.csv, FULL_SEED_DECISIONS.csv, FULL_SEED_SUMMARY.json, A2A3_SUMMARY.json,
    TRAIN_SUMMARY.json
  results_w1_ladder/round_v3/{EXECUTION_REPORT,ERRATA_v2,PREREG}.md, MYOPIC_DIAG.json, G_UNIT_DECISIONS.csv,
    SOURCE_LADDER_CONTRASTS.csv
  results_w1_ladder/round_v2/{PHASE3_REPORT,PHASE4_REPORT,PHASE5_REPORT,EXECUTION_REPORT,PREREG}.md,
    ENDPOINT_SEMANTICS.csv, RULER_CHECK.json, COST.csv
  results_w1_ladder/round_v1/PREREG.md; RAVEN_MCS_PUBLIC_REPRO_R1 (inventory + tables/ + figures/);
  TO_OVERLEAF_paper_tmc_r1_clean/{main.tex, appendix.tex, supplemental.tex} (appendix/supplement read-only)
No-fabrication status: no experiment, training, or pipeline was run; no result directory was created or modified.
  Every number below is copied from the cited file:line or from the manuscript. Requirements in Sec. 6 are marked
  NOT RUN and carry no result.
Scope protection: idea, method, experimental configuration, published numbers, and conclusions are unchanged.
  The only numbers this pass introduces into the manuscript are the two closable-gap values named in the task
  (3.44 pp SensorScope, 1.32 pp U-Air), both taken from results_w1_ladder/round_v2/PHASE3_REPORT.md:77.
Not done here: no rescoring and no score-change claim; a reviewer pass judges that.
```

---

## 1. Claim -> evidence -> design-adequacy table

The paper's experimental claims, the endpoint each one actually rests on, the evidence that exists, and whether
the design supports the claim. `L` = line in the post-fix `main.tex`.

| # | Claim (manuscript anchor) | Endpoint it rests on | Evidence (file:line) | Design (seeds / pairing / multiplicity / intervals / pre-registration) | Adequacy |
|---|---|---|---|---|---|
| C1 | Arrival and deployment-target risks are not interchangeable under two-stage selection (L1645-1682, Fig. 2) | `D_aligned = ΔRMSE_μ − ΔRMSE_ρ` | NSW-Traffic protocol block, 5 methods x 20 paired seeds, Wilcoxon vs 0, p = 4.83e-4..5.86e-4 (L1657-1659) | 20 paired seeds; per-method paired test; the reported values are raw per-method tests and the statistical-policy sentence (L1621-1637) declares families for method comparisons, not for these five; no interval; pre-specified difference-of-differences | **Adequate** (all five p ~5e-4, so an undeclared family cannot reverse them) - record only |
| C2 | Real taxi opportunity under-serves H3 / over-serves H4; TV(π_opp, μ) = 0.142 (T-Drive), 0.192 (SS), 0.278 (UA), all > 0.05 (L1682-1689) | four-block total variation | T-Drive processed trajectories, 10 seeds (L1584-1587) | Descriptive measurement, no interval, 10 seeds; TV thresholds are protocol constants | **Adequate as a measurement**; no CI is reported for the three TV values |
| C3 | Balanced no-harm control: TimeAlign 7.7108 ± 0.0272 vs RAVEN 7.7154 ± 0.0337, one-sided 95 % upper bound 0.134 % < 3 % (L1640-1644) | `RMSE_μ` | balanced control block, 5 seeds | 5 seeds; one-sided bound against a pre-specified margin; explicitly "a sanity check, not a superiority test" | **Adequate**, and correctly self-limited |
| C4 | Design factor on SensorScope: Δ_group +1.237 %, Δ_c-s +0.597 %, prediction unchanged (L1775-1780, Table IV row) | `Δ_group`, `Δ_c-s` (structural), `RMSE_μ` | E4 one-factor ablation, matched to E3 full RAVEN per dataset x seed; `tables/E4_ABLATION_HOLM_RESULTS.csv`; Holm 9.5e-6 both | 20 paired seeds, same selection trace, Holm family per dataset x endpoint; pre-registered one-factor spec | **Adequate** |
| C5 | Design factor on U-Air: costs 6.885 % `RMSE_μ` and 6.943 % `Δ_group`, improves `Δ_c-s` 4.990 % (L1785-1792, Table IV) | same as C4 + Tail RMSE | same as C4 (all four Holm-significant) | same as C4 | **Adequate** |
| C6 | The projected reference carries the reference-side part: +0.768 pp [0.563, 0.970] SS (above the 0.5 pp line, stable), +0.286 pp [0.098, 0.471] UA (below it, split-unstable) (L244-253, L1832-1835) | `Δ_group` in pp and in closable-gap units | `FULL_SEED_DECISIONS.csv:3` (SS), `:11` (UA); v3 `G_UNIT_DECISIONS.csv` | 20 paired seeds; bootstrap 10 000, seed 20261002; Wilcoxon into Holm; band ±0.10 in G units plus an independent 0.5 pp practical line; same active set / same `M_r` / same `C_r`, all windows known in advance (`round_v1/PREREG.md:79`) | **Adequate with a ruler caveat**: ladder rows use the report-half `Δ*` (SS 0.97276, UA 1.06311), the 20-seed dashboard values use SS 0.95813 / UA 1.07103 -> gaps 3.12 vs 3.44 pp SS. Fixed in text by P0-2 (Sec. 8) |
| C7 | The remaining (P2) terms and the debt recursion at frozen strength stay inside the band (L1839-1846) | `Δ_group` in G units | `FULL_SEED_DECISIONS.csv:4` (B2−B1 dG +0.039 [0.013, 0.063]), `:5`, `:9`, `:8`; v3 `EXECUTION_REPORT.md:113-118` | as C6 | **Adequate as a non-distinguishability statement.** It is *not* a necessity test (Sec. 5). The debt half needed the frozen-configuration scope (P0-1) because the κ=1000 arm is outside the band (C10) |
| C8 | Debt is internal accounting, "neither prediction drivers nor structural contributors" (L232-236; L1839-1846; L2058-2065) | `Δ_group`, `RMSE_μ` | `TRADEOFF_PAIRED.csv:26,61`; `FULL_SEED_DECISIONS.csv:9,16` (+0.0073 pp / +0.0024 pp) | as C6, at the frozen λ and η | **Was not supportable as stated** (unscoped): L2067-2078 prints the projection-with-debt rule (κ=1000) lowest on the group endpoint on both datasets. Scoped to the frozen configuration by P0-1 |
| C9 | Worst-group tolerance: SS both RAVEN settings and U-Air RAVEN-NoDesign within the descriptive +0.5 % vs FedAU/ObsUse; U-Air Design-on outside at +7.9 %/+8.0 % (L1791-1797, L1851-1863 caption, Table III) | `WorstGroupRMSE` | `tables/E3_SCD_WORSTGROUP_VS_FEDAU_OBSUSE_HOLM.csv` (4 rows, `significant_holm_0.05 = False`); TEST seeds 30011-30020 / ALL20 | Point-estimate mean-relative tolerance, "descriptive rather than a formal non-inferiority test" (L1631-1637); Holm family on the 20-seed slice reported non-significant | **Design cannot support an equivalence reading**: a descriptive point estimate with no interval is not an interchangeability result. Fixed at one site by EA-2; the tolerance itself is correctly labelled at its definition |
| C10 | Trained server-weight rules: on the group endpoint `proj_beta_debt` < `proj_beta` < frozen RAVEN ≈ `inst_cal` < uniform < FedAvg on both datasets; projection +0.768 pp / +0.286 pp over uniform; debt variant +1.347 pp / +0.580 pp over projection (L2067-2091) | `Δ_group`; `RMSE_μ` secondary | `TRADEOFF_PAIRED.csv:22-26,52-56` (Holm 1.0e-5, 1.7e-5); `TRAIN_SUMMARY.json:17-90` means | 20 paired seeds; B-G0 exact replay; B-G1 active set 120/120; **B-G2 0/40 at 2.07e-6 (SS) / 2.67e-6 (UA) and B-G3 2.89e-5 / 3.77e-5 against a 1e-9 tolerance**; κ chosen on tuning seeds; A2 gate failed (3.34e-8 > 1e-8) -> exploratory | **Adequate only as an ordering of trained arms with exploratory status**, which the paper states (L2078-2082, L2209-2221). **`WorstGroupRMSE` was not measured for these arms** (the preregistered column is empty in all 240 `TRADEOFF.csv` rows), so the trained-rule claims have no worst-group reading |
| C11 | No prediction-endpoint contrast survives Holm on either dataset (L1862 caption, L2086-2092) | `RMSE_μ`, Head/Tail RMSE, `RMSE_ρ` | `TRADEOFF_PAIRED.csv:2-21,32-51`: 40/40 prediction rows non-significant, min `p_holm` 0.133 (UA `raven − proj_beta`, raw 0.0296) | Holm per dataset x endpoint, family size 5 per cell | **Adequate and disclosed.** This is the paper's own limiting statement, not a defect |
| C12 | The new rules cost no wall-clock time: 18.5-20.0 s vs 27.1 s on SensorScope (L2083-2085) | run wall clock | `TRAIN_SUMMARY.json` means (SS `proj_beta_debt` 18.53, `proj_beta` 19.89, `uniform` 19.96 vs `raven` 27.08) | 20 seeds per arm; single-machine timing; claim scoped to SensorScope | **Adequate**; U-Air wall clock is only partially reported in `PART_B_REPORT.md` (values exist in the CSV) and per-window solve-time percentiles exist only in `round_v2/COST.csv:18-31` (L5/L6 p95 ~447 ms SS) |
| C13 | Recoverable-gain ceiling: `H` inside [-0.03 %, +0.08 %] (SS) and \|H\| ≤ 0.217 % (UA), GO rule did not fire; margin-estimation cost -0.008 % / +0.040 % (L2092-2135) | `RMSE_μ` headroom / substitution | stress grid; U-Air re-run at 20 seeds, 270 runs, 45 traces | 20 seeds, minimum detectable effects stated (0.17-0.36 pp SS, 0.70-0.80 pp UA), pre-frozen GO rule with a positive-lower-bound requirement | **Adequate**, including the negative result |
| C14 | Design-factor setting rule: support gate returns on/off per block; switch point `w_c/w_g > 1.39` (L2008-2040) | four weighted endpoints | Table IV U-Air entries, reused as coefficients | Single-block calibration; coefficients printed without their source (`4.990`, `6.943`, `6.885`, `7.221`) | **Design cannot support a general decision standard**; the text already calls it "a decision standard for blocks of this kind" (L2035) but the coefficients are unlabelled (round-6 `R5-10`, open; hygiene item, not applied here) |
| C15 | Coverage Gate / aggregate certificate: pooled CERTIFIED validity 0.959, U-Air `a = 1.00` 0.750; the Gate never switches Design (L985-1006, L1370-1412, L2157-2160) | gate validity / `C_t` | certificate block; frozen coverage-stress oracle | Diagnostic only; correctness conditional on Assumption 1; adaptive switching not proven | **Adequate as a diagnostic**; the apparatus supports an instrument that never acts (round-6 `C2`, unchanged) |
| C16 | Decomposition of the published FedAvg gap: 2.09 pp = 68.96 % uniform + 31.04 % reference (SS); 1.47 pp = 83.07 % + 16.93 % (UA) (L237-243, L1815-1835) | `Δ_group` decomposition | `round_v3/EXECUTION_REPORT.md:29`; 20-seed pp parts with bootstrap CIs | 20 paired seeds; CIs on the pp parts; shares are ratios of the parts | **Adequate**; the two shares are point ratios without intervals, and the U-Air FedAU/ObsUse rows are correctly declared undecomposable (L1836-1838) |

**Claim-evidence status vocabulary used above:** `Adequate` = design supports the claim as written; `Adequate with caveat` = supported only under a stated ruler/scope condition; `Not supportable as stated` = the manuscript previously asserted more than the design shows (each such case is either fixed in this pass or recorded in Sec. 6).

---

## 2. Endpoint coverage

Nothing on a prediction endpoint survives Holm anywhere in the supplied evidence, and the paper says so in three
places. The audit's finding is not that the paper hides this; it is *which* published claim rests on which
endpoint, and whether the paper says so **at that place**.

### 2.1 Claims resting on `RMSE_μ` / WorstGroupRMSE

| Claim site | What it says | Does the text name the endpoint and its limit there? |
|---|---|---|
| Abstract L86-93 | "Design is worth 1.24 % of group mismatch on SensorScope at unchanged prediction, and on U-Air it costs 6.55 % of RMSE"; "a descriptive +0.5 % worst-group tolerance, not an RMSE win" | Partly. The abstract does say "not an RMSE win", but the `1.24 %` / `6.55 %` pair carries no ruler and no multiplicity statement, and the body prints `1.237 %` / `6.885 %` (L1573-1580). Round-6 `F3`/`R5-11`; untouched here (numbers frozen) |
| Contribution 4, L244-253 | Structural improvements quoted against uniform weights with paired intervals | Yes: structural endpoints named, intervals given, "+0.5 pp practical line" named |
| L1775-1780 | "their `RMSE_μ` is indistinguishable (7.9380 versus 7.9384)" | Yes: endpoint named and the comparison declared indistinguishable |
| L1791-1797, L1851-1863 | Worst-group tolerance claims | Yes: "descriptive", "TEST seeds", "not a formal non-inferiority test" |
| L1862 | "We do not claim a Holm-significant RMSE win" | Yes |
| L2086-2092 | "No prediction-endpoint contrast survives Holm correction on either dataset (`p_Holm = 1.000` SS; best raw 0.027, `p_Holm = 0.133` UA)"; arm order on `RMSE_μ` does not follow the structural order | Yes - the strongest disclosure in the paper |
| L2092-2135 | Ceiling: every `RMSE_μ` effect is inside the stated minimum detectable effect | Yes |
| L2136-2160 (Limitations) | No Holm-significant RMSE win; hybrid tables place FedAU/ObsUse first | Yes |

Verdict: **endpoint coverage is honestly reported where the negative result matters** (L1862, L2086-2092,
L2136-2160), with one residual gap that is a numbers-frozen clarity issue, not a design one: the abstract's
`1.24 %` / `6.55 %` pair has no in-body companion with a ruler (round-6 `F3`; `R5-13` is excluded from the delta
as pre-existing).

### 2.2 Claims resting on the structural endpoints (`Δ_group`, `Δ_c-s`)

These are the endpoints that carry the paper's positive results. In the trained-rule family, 16 of 20 structural
paired rows are Holm-significant (`TRADEOFF_PAIRED.csv:22-31,52-61`); in the ablation family the Design rows are
significant on both datasets (`tables/E4_ABLATION_HOLM_RESULTS.csv`). The structural claims are therefore
evidence-backed *within the protocol-constructed selection family*, and the paper's own scoping sentences
(L1537-1551, L2136-2160) keep them there.

### 2.3 The cost / accounting layer

* Wall clock: exists and is used once (C12). Per-window solver time (`round_v2/COST.csv:7-31`) and the debt
  accounting certificate `Δ_group ≤ 2‖Q‖₁/S_R + 1e-9` (240/240 pass, ratio 0.7174-0.8215,
  `PHASE5_REPORT.md:13-30`; `round_v1/PREREG.md:73`) exist in the evidence but are not in the main text. The
  accounting layer therefore reaches the paper only as the one-sided bound `\eqref{eq:debt_bound}` and the
  "matching accounting" clause (L2061-2065). **Missing-by-design, not missing-by-error**: the certificate is
  presented in the supplemental derivation. Recorded here because the debt verdict (C8) is exactly the claim that
  layer supports, and it is the layer a reviewer will look for when the claim is scoped to the frozen strength.

---

## 3. Design adequacy per claim

Dimensions checked for every claim in Sec. 1: seeds, pairing, multiplicity control, intervals, pre-registration
status, support/ruler conditions, and same-support / same-`M_r` comparability.

### 3.1 What the package does have (verified)

* **Seeds and split.** 20 seeds, tuning 30001-30010 / report 30011-30020 (`round_v1/PREREG.md:35`). The v4 main
  verdict uses all 20 (`round_v4/PREREG.md:8`, `PART_A_REPORT.md:7`); v2 Phase-4 and v3 T3/T6 are report-half
  only (`PHASE4_REPORT.md:20,40`; `SOURCE_LADDER_CONTRASTS.csv:2-6`); T-Drive/ranking prose uses the 10 TEST
  seeds (L1628-1632). Every one of those usages is declared in the manuscript.
* **Pairing.** Per-seed paired differences; bootstrap 10 000, seed 20261002, percentile interval; Wilcoxon
  signed-rank p entering Holm (`round_v1/PREREG.md:57`; `round_v3/PREREG.md:94`). Note the *three* interval
  types in play: seed SD for `Δ*`/`Δ_unif`/`Δ_myo` (`round_v2/EXECUTION_REPORT.md:51`), paired bootstrap CI for
  contrasts, and Holm-adjusted p. The manuscript uses each in the right place (`mean ± std` in tables;
  bootstrap intervals for contrasts; Holm for tests).
* **Multiplicity.** Registered family 2 datasets x 2 endpoints x 5 rung contrasts = 20 (`round_v1/PREREG.md:58-61`),
  16 computable (`PHASE4_REPORT.md:61`); v3 re-judged in G units with Holm per dataset x endpoint (8 families,
  `round_v3/EXECUTION_REPORT.md:127`); Part B uses Holm per dataset x endpoint with family size 5 per cell
  (verified arithmetically from `TRADEOFF_PAIRED.csv:24,32`).
* **Pre-registration.** Two immutable preregistrations (`round_v3/PREREG.md:7`) plus errata that correct wording
  only (`ERRATA_v2.md:3-4`) and a third errata for round v4 (`ERRATA_v3.md:3-5`). The manuscript's own claims of
  pre-registration (L246-248, L611-613, L1628-1632, L1929-1943) all trace to a frozen file.
* **Support / ruler.** `Δ*` is defined with the four qualifiers "same active set, same `M_r`, same `C_r`, all
  windows known in advance" (`round_v1/PREREG.md:79`); the manuscript prints them (L607-611). Same active set is
  gated: G1(v2) `max_M_diff = 0.0`, `max_w = 5.55e-17` (`RULER_CHECK.json:14-16`); B-G1 120/120
  (`PART_B_REPORT.md:16`). U-Air ruler misalignment is real and disclosed: `fedau_window`, `obsuse_window`,
  `raven_wo_design` are 20/20 `ruler_misaligned` and the ζ effect is therefore unreported on U-Air
  (`round_v3/EXECUTION_REPORT.md:27,68`; `PART_A_REPORT.md:39`; manuscript L1836-1838).
* **Same-`M_r`.** Holds exactly for the replay/ladder contrasts (A1 replay max error 1.11e-15 ≤ 1e-9,
  `PART_A_REPORT.md:32`; B-G0 exact, `PART_B_REPORT.md:15`). It does **not** hold exactly for the freshly trained
  arms: `β̂` is bit-identical per window, but the run's own `M_r`/mass inputs drift, giving B-G2 residuals
  2.07e-6 / 2.67e-6 and B-G3 residuals 2.89e-5 / 3.77e-5 (`PART_B_REPORT.md:20`; `TRAIN_GATES.csv:24,57,96,120`).
  The manuscript reports this as a residual rather than an identity (L2211-2221) - correct - but band verdicts
  are only issued for contrasts in the first group, so the ruler premise is not violated where it is used.

### 3.2 Claims the design cannot support, and their disposition

| Flag | Claim | Why the design cannot support it | Disposition in this pass |
|---|---|---|---|
| FL-1 | Debt "neither prediction drivers nor structural contributors" (L232-236, L1839-1846) | Part B trains an amplified-debt rule (κ=1000) that is lowest on the group endpoint on both datasets (`TRADEOFF_PAIRED.csv:26,61`); the verdict was stated without the frozen λ/η scope | **Fixed** (P0-1a/P0-1b) |
| FL-2 | Band verdicts convertible between the ruler used for ladder rows and the values quoted elsewhere | Ladder/report-half `Δ*` (0.97276 SS / 1.06311 UA) differs from the 20-seed `Δ*` (0.95813 / 1.07103); the recoverable gap is 3.12 pp vs 3.44 pp on SS `EXECUTION_REPORT.md:118` | **Fixed** (P0-2: values printed once per dataset + subset caveat) |
| FL-3 | "The per-window minimizer is not unique" read as a statement about the program `J_r`, contradicting Theorem 2's unconditional uniqueness (`L1249-1254`) | `MYOPIC_DIAG.json:10` measures the ℓ₁ surface only; the group term's ℓ₂ objective is not the measured object | **Fixed** (P0-3b: non-uniqueness scoped to the ℓ₁ surface) |
| FL-4 | Worst-group "interchangeable with FedAU-Window and ObsUse-Window" (L1782 pre-fix) | The device is a descriptive point-estimate tolerance, explicitly not a non-inferiority test; no interval exists for it | **Fixed** (EA-2 at one site); the same wording class elsewhere is scoped ("interchangeable rather than a Holm-significant win", L1923) |
| FL-5 | Debt ablation "well below the 0.5 % paired-relative minimum practical effect used elsewhere" (L2066-2067 pre-fix) | The 0.5 % device is a mean-relative worst-group tolerance for external method comparisons; the ablation reports relative changes of `Δ_group`/`Δ_c-s` | **Fixed** (EA-1) |
| FL-6 | Per-component necessity, as implied by Table IV's one-factor rows with significance stars | The registered necessity criterion (paired interval entirely beyond ±0.10 in G units) is never applied; the `Inst` row removes the projection anchor together with the coordinated terms; the frozen-replay ladder puts those terms inside the band | **Not fixed in text** (only the necessity *rule* is now stated, EA-3); converted into requirement R2 (Sec. 6) |
| FL-7 | The ablation's `Inst` row attributing effects to "instantaneous calibration" as a component | The row's arm is not defined in the manuscript; `CONFIG_REGISTRY.csv` (E4) shows `λ_g` 0.0 only for `w/o-Inst`, i.e. the removal changes the objective's group term, and Part B shows the projection alone suffices | Recorded; requirement R2 covers the reporting fix. The one text-level consequence that mattered (the borrowed ruler) is EA-1 |
| FL-8 | Any generalization beyond algorithmic/EventTrace randomness | "Those seeds capture algorithmic and EventTrace randomness, not independent cities" (L1584-1587) | Already stated; requirement R6 |
| FL-9 | Usable-update correction's empirical effect | "usable-update delivery is measured in no block" (L1533-1536); the ablation "does not establish its marginal indispensability" (L2045-2050) | Already stated; requirement R5 |
| FL-10 | Worst-group reading for the trained server-weight rules | Preregistered `WorstGroupRMSE` column is empty in all 240 `TRADEOFF.csv` rows and is not a paired endpoint in `TRADEOFF_PAIRED.csv` | Requirement R3 |
| FL-11 | Closed-loop identity of the projection arms | B-G2/B-G3 unmet against 1e-9; by the letter of the protocol Part B should have stopped | Disclosed in the manuscript (L2209-2221) and marked exploratory; requirement R4 |
| FL-12 | Five risk-interchangeability tests with no declared Holm family (C1) | The statistical-policy sentence declares families for method comparisons; these are five per-method tests against zero (L1657-1659) | Immaterial (all p ~5e-4); recorded only |

---

## 4. The analysis-convention layer: the ±0.10 band

### 4.1 What is registered

* Unit: G units, `ΔG = (Δ_a − Δ_b)/(Δ_unif − Δ*)`, numerator and denominator drawn from the **same** bootstrap
  resample; equivalence band `[−0.10, +0.10]` (`round_v3/PREREG.md:91-99`; `round_v3/EXECUTION_REPORT.md:105`).
* **Decision rule (registered):** a rung difference is *equivalent* only when its paired interval falls entirely
  inside `[−0.10, +0.10]`; the necessity direction is the interval entirely beyond `+0.10`
  (`round_v1/PREREG.md:43-44`). Interval containment, not a point estimate.
* Independent second rule: the practical line, absolute-improvement interval lower bound ≥ 0.5 pp
  (`round_v3/PREREG.md:99`).
* Unit-error history: v2 applied ±0.10 in Δ units, where it cannot fail; those verdicts are relabelled
  `superseded_units` (`ERRATA_v2.md:25-27`; `round_v3/EXECUTION_REPORT.md:128`).

### 4.2 What the manuscript had before this pass

The band was named and placed in §III-F "Structural Alignment Objective" (a modelling subsection rather than
where verdicts are read), with a correct denominator label (round-5 fix) but:

1. **no decision rule** - nothing said whether the band is read on the point estimate or on the interval;
2. **no denominator value** - `3.44` / `1.32` do not appear anywhere in `main.tex` (grep), so `+0.0073 pp`,
   `−0.268` and "inside/outside the band" were not convertible to a common unit;
3. **no non-test marking** - unlike its weaker sibling at L1631-1637 ("descriptive rather than a formal
   non-inferiority test"), the band carried no status statement;
4. **no `\label` and no cross-reference** from the places where band verdicts are actually read;
5. **no necessity direction** - the registered necessity half (interval entirely beyond +0.10) was never stated,
   which is precisely the rule that would license or forbid Table IV's necessity reading (Sec. 5);
6. **no subset caveat** - ladder contrasts use the report-half `Δ*`, whose recoverable gap differs (3.12 vs
   3.44 pp SS), so band verdicts are not convertible across the two references.

Exactly what was missing is therefore: **rule (1), value (2), status (3), label (4), necessity half (5), subset
caveat (6)**. Items 1-4 are closed by P0-2/P0-3; item 5 is stated by EA-3 (without per-component verdicts); item 6
is closed by P0-2's caveat. What remains missing after this pass is the *reporting* of per-component necessity
verdicts in G units - the evidence exists in `G_UNIT_DECISIONS.csv` and `FULL_SEED_DECISIONS.csv`, but those
files are not in the released bundle (Sec. 7), so a reader still cannot audit them from the bundle.

### 4.3 Terminology risk carried with the band

The paper calls κ the "debt weight" (L2082-2083) while `(P2)`'s debt term has an implicit frozen coefficient of 1
and λ_g = 1 is the group-term weight (`src/raven_mcs/aggregation/p2_cvxpy.py:102-108`; `PHASE4_INPUT_GAPS.md:72`;
`CONFIG_REGISTRY.csv` E4 row). The frozen configuration is correctly described in this pass as λ_g = 1 and
η = 0.01 (the values verified at `PHASE4_INPUT_GAPS.md:72` and `ERRATA_v2.md:55`), and κ is left as the arm's own
ratio parameter; a reviewer who reads λ_g as "the debt weight" would be misled. Recorded as a terminology item
for `ccf-paper-writer` (round-6 `R5-1` terminology half, still open).

---

## 5. Ablation / necessity design

### 5.1 What the ablation design can and cannot show

Table IV removes one component at a time from the full RAVEN configuration under the same Complete-aligned trace
and the same paired seeds, reports a relative change, and marks Holm significance within pre-declared families
(L1944-1952). That design supports: *"removing component X at the frozen configuration changes metric M by δ %"*.
It does **not** support per-term necessity, for four evidence-backed reasons:

1. **The registered necessity criterion is never applied.** Necessity is registered as a paired interval entirely
   beyond ±0.10 in G units (`round_v1/PREREG.md:43-44`), and the evidence contains those intervals
   (`G_UNIT_DECISIONS.csv`; `FULL_SEED_DECISIONS.csv`). The manuscript reports percentage changes and Holm stars
   instead, so a "necessary" reading of a star is unsupported.
2. **The ladder says the coordinated terms are inside the band.** `B2−B1` (group-matching term) `ΔG = +0.039`
   `[0.013, 0.063]`; `B3−B2` (variance/staleness) `−0.0027`; `L6−L5` (debt) `−0.0021`; p/q factors `−0.015` /
   `+0.003` - all inside ±0.10 (`FULL_SEED_DECISIONS.csv:4,5,8,9`; `round_v3/EXECUTION_REPORT.md:113-118`). v3
   states the conclusion explicitly: the structural gain is carried by the projection of the opportunity-corrected
   reference β̂ onto `C_r`, and the group, variance, staleness, p and q terms all fall inside the band
   (`round_v3/EXECUTION_REPORT.md:83`).
3. **The per-window matching objective is exactly degenerate.** Over 3 279 active windows the range of
   `‖M_rα − μ‖₁` on `C_r` has median `−1.13e-13` with all reported quantiles at machine zero, so the argmin is not
   unique and `Δ_myo` is one solver landing point on a flat surface (`MYOPIC_DIAG.json:3-13`;
   `round_v3/EXECUTION_REPORT.md:132-133`). The tie-break experiment shows what actually selects: using β̂ to break
   the tie gives `Δ_myo_tb = 1.05140` vs uniform `1.06213`, a 0.0107 improvement
   (`MYOPIC_DIAG.json:20-23`; `round_v3/EXECUTION_REPORT.md:134`).
4. **The necessity answer moves with the weight.** In the frozen-replay ladder the debt recursion is inside the
   band (C7); in the trained-arm family the amplified-debt rule adds +1.347 pp / +0.580 pp at Holm ~1e-5
   (`TRADEOFF_PAIRED.csv:26,61`). A necessity claim is therefore only meaningful with the weight named, which is
   why FL-1 had to be scoped.

### 5.2 Where the paper still implies a necessity the design cannot show

* **L2053-2065 (`Inst` / debt paragraph).** `Inst` is not defined at the point of use, so the row cannot be
  attributed to the coordinated `(P2)` terms: the removal is the whole calibration step, i.e. the projected
  reference anchor plus the group/variance/staleness terms, and Part B shows the projection alone already beats
  frozen RAVEN on the group endpoint (`raven − proj_beta = −0.118` pp, Holm 0.019, `PART_B_REPORT.md:59`;
  `TRADEOFF_PAIRED.csv:23`). "Debt has the narrowest but most consistent role" is true as a significance
  statement, but the magnitudes (0.0141 %/0.0040 % SS; 0.0043 %/0.0024 % UA) are two to three orders below the
  ablation's own resolution on those endpoints, and the ruler originally attached to them belonged to another
  endpoint (FL-5, fixed by EA-1).
* **Table IV caption + column structure.** Reporting `Obs`, `Use`, `Inst`, `Debt` as peer rows with significance
  stars invites a per-component necessity reading that only the `Design` row can carry. The paper's own honest
  statements are present, and stronger than Table IV: "The projected reference carries that reference-side part,
  and the design factor is the only further component that survives" (L1830-1831); "they are not the empirical
  claim" (L259-260); "the ablation does not establish its marginal indispensability" for `Use` (L2045-2050).
* **Where it is *not* over-claimed.** The paper never asserts the full `(P2)` is necessary; the v2 statement
  "P2 的其余项不是必要的" was retracted in v3 (`ERRATA_v2.md:9-17`, settled at `round_v3/EXECUTION_REPORT.md:140`)
  and no trace of it is in the manuscript. This is the correct posture and should not be traded away for a
  stronger necessity story.

### 5.3 Required design consequence

Per-term necessity must either be reported at the registered criterion (R2: analysis-only, evidence already
exists) or left as non-distinguishability. It cannot be inferred from Holm stars on relative changes.

---

## 6. Missing experiments and missing analyses — requirements list

**None of the items below were run, authorised, or simulated in this pass.** They are requirements with a
minimal design, the claim each would support, and an owner skill. Cost estimates are extrapolations from the
recorded scale of Part B (3 arms x 2 datasets x 20 seeds + 2 gate runs ≈ 45 min, `round_v4/PREREG.md:52`) and from
the recorded per-run wall clocks (SS frozen `raven` 27.1 s, new arms 18.5-20.0 s, `PART_B_REPORT.md:84`;
`TRAIN_SUMMARY.json`), not measured here. Every design below must keep the confirmed versions: the frozen RAVEN
configuration, the same driver, and the complete arms - no simplified or proxy variants.

| ID | Claim it would support | Minimal design (arms / seeds / endpoints / gates) | Cost estimate | Owner skill |
|---|---|---|---|---|
| R1 | That target-mass alignment converts into a **prediction** endpoint on at least one block (the paper's own limiting weakness, L2086-2092) | Arms: frozen RAVEN, `proj_beta`, `uniform_window`, `fedavg_window`, plus one alignment-only variant; 2 datasets x 20 seeds; endpoints `RMSE_μ` primary, `WorstGroupRMSE` secondary, Head/Tail RMSE; gates B-G0 exact replay, B-G1 active-set identity, B-G2/B-G3 at 1e-9 (must pass); Holm family declared per dataset x endpoint **before** the run | ~4 arms x 2 datasets x 20 seeds ≈ 60 min single-machine; plus gate runs | `ccf-experiment-designer` (needs explicit user authorisation) |
| R2 | Per-term necessity at the registered criterion, plus the ℓ₁-flatness tie-break | **No new training.** Report the existing ladder contrasts in G units with intervals and the necessity direction, per dataset x endpoint; add the `Δ_myo_tb` tie-break reading; state the `Inst` row's composition | Analysis-only, < 1 h | `ccf-experiment-designer` + `ccf-paper-writer` (reporting) |
| R3 | A worst-group reading for the trained server-weight rules (preregistered but never collected) | Re-score the 3 Part-B arms on `WorstGroupRMSE` if per-block scores were logged; otherwise re-run 3 arms x 2 datasets x 20 seeds; endpoints `WorstGroupRMSE` + `Δ_group`/`Δ_c-s`; same gates as R1 | 0 (logs) to ~45 min (re-run) | `ccf-experiment-designer` |
| R4 | Closed-loop identity of the projection arms (B-G2/B-G3 at 1e-9) | Re-run `proj_beta` and `proj_beta_debt` with `M_r` frozen to the recorded run (or `M_r` recorded per window); 2 arms x 2 datasets x 20 seeds; endpoints `Δ_group`, `Δ_c-s`, `RMSE_μ`; gates B-G2/B-G3 ≤ 1e-9 | ~30 min; requires a driver/`src` change (out of scope for this pass) | `ccf-experiment-designer` |
| R5 | Whether usable-update correction has any isolated empirical effect | One block with **measured** `U` (registration/attempt/completion timestamps) at the same support; 20 seeds; endpoints `Δ_group`, `Δ_c-s`, `RMSE_μ`; no-harm and active-set gates as in the main family | Data acquisition first; then ~45 min compute | `ccf-literature-searcher` (dataset discovery) -> `ccf-experiment-designer` |
| R6 | Generalization beyond algorithmic/EventTrace randomness (independent cities) | One additional city-scale block with real `R` (e.g. a second City Scanner vintage) and the same windowed family; 20 seeds; endpoints as in the main table | Medium-high (data + 1-2 days) | `ccf-experiment-designer` |
| R7 | Bundle-level auditability of the band, ladder and trained-rule claims | Inventory extension only: ship the round-v3/v4 ladder, band-decision, debt-strength and trained-rule artefacts with the public bundle, pinned by hash | Low (packaging) | `ccf-integrity-auditor` / `ccf-submission-checker` |
| R8 | Machine-readable gate verdicts for B-G2/B-G3 | Persist per-row B-G2/B-G3 verdicts (currently prose-only) and fix the `pass` column semantics in `TRAIN_GATES.csv` | Low (re-serialisation of existing numbers) | `ccf-experiment-designer` |

Priority: R1 (evidence axis, weight 0.25) > R4/R8 (design credit for the new rules) > R2/R3 (reporting of
existing evidence) > R7 (reproducibility) > R5/R6 (new capability).

**No-fabrication reminder.** No cell in this list has a result. R2 and R3 reuse existing artefacts; R1, R4, R5,
R6 are new runs and may not be described in the manuscript as done.

---

## 7. Reproducibility / bundle gaps that affect design interpretation

1. **The released bundle does not contain the ladder, band-decision or trained-rule artefacts.**
   `RAVEN_MCS_PUBLIC_REPRO_R1` (1 901 files) ships `tables/`, `figures/`, `eventtraces/`, `tdrive/`,
   `cityscanner/`, `cityscanner_p2/`, `new_target/`, `processed/`, `configs/`, `certificate/`, `scripts/`,
   `MANIFEST.csv`, `verify.py`, and `tables/E3_FORMAL_HOLM_RESULTS.csv`,
   `tables/E3_SCD_WORSTGROUP_VS_FEDAU_OBSUSE_HOLM.csv`, `tables/E4_ABLATION_HOLM_RESULTS.csv`. It contains **no**
   `results_w1_ladder/round_v2|v3|v4` file (grep for `LADDER`, `TRADEOFF`, `DEBT_STRENGTH`, `GAP_DECOMP` finds
   no semantic hit). Consequences: the +0.768 / +0.286 pp projection contrasts, the ±0.10 band verdicts, the
   0.5 pp practical-line verdicts and the κ=1000 ordering cannot be checked from the stated bundle, and neither
   the newly printed closable-gap values nor the report-half caveat can be verified there (round-6 `M7`;
   requirement R7).
2. **Gate residuals vs the exact frozen replay.** The frozen rule replays exactly (B-G0: all three endpoint
   differences 0.0, `TRAIN_g0.json`; A1 replay max error 1.11e-15 ≤ 1e-9, `PART_A_REPORT.md:32`), while the
   projection arms miss the same 1e-9 tolerance by 2.07e-6/2.67e-6 (`proj_beta`) and 2.89e-5/3.77e-5
   (`proj_beta_debt`) on the structural endpoint (`PART_B_REPORT.md:17-18`; `TRAIN_GATES.csv:24,57,96,120`).
   Mechanistically `β̂` is bit-identical per window; `uniform_window` (which does not use `β̂`) reproduces exactly;
   therefore the residual tracks the run's own `M_r`/mass inputs (`PART_B_REPORT.md:20`). This is the reason the
   ruler premise "same `M_r`" is a within-run premise for the trained arms, and it is why the band verdicts are
   issued only for replay contrasts. The manuscript states the residual (L2211-2221); the *gate* status
   (B-G2 partial, B-G3 failed, "by the letter of the protocol Part B should stop") is stated as exploratory
   rather than as a gate table.
3. **`WorstGroupRMSE` was registered and never collected for the Part-B arms** (empty 8/240 in `TRADEOFF.csv`;
   absent from `TRADEOFF_PAIRED.csv`), and the preregistered per-window solve-time median and the
   "residual pp vs Δ*" column are absent from the delivered file (`round_v4/PREREG.md:54`). Requirement R3.
4. **Gate serialisation is not machine-readable for B-G2/B-G3.** `TRAIN_GATES.csv` carries only `B-G1` rows, and
   its `pass` column is `True` only on the 40 `uniform_window` rows - tracking the ≤1e-9 replay check, not B-G1 -
   while `TRAIN_SUMMARY.json:3-5` reports B-G1 120/120 and B-G2/3 40/120. A third party reading the CSV alone
   would misread which gate failed. Requirement R8.
5. **Two evidence-internal inconsistencies that bound how far the numbers can be pushed.**
   (a) *U-Air κ-curve convergence*: `A2A3_SUMMARY.json:66` records `converged: true` (1.79e-4 < 2.63e-4) while
   `PART_A_REPORT.md:46,48,78` states the opposite ("按字面未收敛") with a 4.5e-4 last-two difference. The
   manuscript reports only the safe part (an interior optimum at κ=1000, curve rising at large κ, rule labelled
   exploratory), so no published claim depends on which file is right - but the two files disagree and the
   manuscript's "exploratory" label is what keeps this harmless.
   (b) *Two `Δ*` references*: `PHASE4_REPORT.md:79` heads its TV table "same report-seed subset", but its
   optimum-order cell (47.91 %) equals the 20-seed `Δ*/2` (0.95813), not the report-half 48.64 %
   (`PHASE5_REPORT.md:63`); hence the same ladder rows yield 3.85 pp in `PHASE4_REPORT.md:83` and 3.12 pp in
   `round_v2/EXECUTION_REPORT.md:118`. This is exactly why the recoverable gap must be printed with its seed
   block (P0-2) and why band verdicts must not be converted across references.
6. **Fallback solutions in the debt-strength sweep are not disclosed in the manuscript.** `DEBT_STRENGTH_V4.csv`
   records `solver_fail` per cell totalling 3 279 failed window-cells (≈7 %), which used fallback solutions
   (`PART_A_REPORT.md:59,79`); the flatness diagnostic independently counts 3 279 **active windows**
   (`MYOPIC_DIAG.json:2`). The two counts are numerically equal but are different objects (failed window-cells in
   a κ sweep vs active windows in a per-window diagnostic), so they must not be conflated. The manuscript
   discloses a general optimality caveat (L1634-1637, "the stored outputs do not support retrospective
   certification of exact numerical optimality") but not the ~7 % fallback count for the sweep that produced the
   κ curve. Because the κ arms are labelled exploratory this carries no claim, but an auditor comparing the two
   3 279 figures will ask.
7. **Interval-type ambiguity downstream.** Seed SD, paired bootstrap CI and Holm p coexist; only the paired
   contrasts have bootstrap intervals (`round_v2/EXECUTION_REPORT.md:51`). Any future text that quotes a `±` from
   the ladder as an inferential interval would be wrong; the manuscript's tables correctly use `mean ± std`.
8. **Not-a-pinned-retraining-archive.** The bundle verifies tabulated cells from CSVs, not a retraining replay
   (L2202-2208). Combined with (1), the design is auditable at the table level but not at the claim level for the
   band, ladder and trained-rule families.

---

## 8. Corrections applied to the manuscript in this pass

Snapshot of the pre-fix state: `snapshots/2026-10-03-pre-design-fix/main.tex` (2 230 lines, 112 608 bytes,
mtime preserved from the source). All corrections are text-level; no number was added, changed or removed except
the two closable-gap values required by P0-2, both from `round_v2/PHASE3_REPORT.md:77` (`(Δ_unif − Δ*)/2 = 3.44 pp`
SensorScope; 1.32 pp U-Air R_on).

| Edit | Evidence behind it | Before -> after (final lines) |
|---|---|---|
| **P0-1a** frozen-configuration scope in the contributions | `PHASE4_INPUT_GAPS.md:72` (λ_g = 1.0, λ_β = 1.0, λ_v = 0.1, λ_s = 0.1); `ERRATA_v2.md:55` (η = 0.01) | L232-235 -> L232-236: "...performance contribution; **at the frozen configuration ($\lambda_g=1$, $\eta=0.01$, the strength used by the frozen runs)**, instantaneous calibration and debt are neither prediction drivers nor structural contributors." |
| **P0-1b** frozen-configuration scope at the verdict, plus a label pointer | same; `TRADEOFF_PAIRED.csv:26,61` (κ=1000 arm outside the band) | L1839-1845 -> L1842-1846: "...stay inside **the band of Section~\ref{subsec:equivalence_band} at the frozen configuration ($\lambda_g=1$, $\eta=0.01$, the strength used by the frozen runs)**, so **at that strength** debt is an auditable accounting recursion for residual under-service rather than a structural contributor; ..." |
| **P0-2** closable-gap value printed once per dataset + subset caveat | `round_v2/PHASE3_REPORT.md:77` (3.44 pp SS / 1.32 pp UA, all 20 seeds); `round_v2/EXECUTION_REPORT.md:118` and `PHASE5_REPORT.md:63,68` (report-half `Δ*` 0.97276 / 1.06311, gaps 3.12 / 1.33 pp, rulers not mixable) | L605-610 -> L611-620: "...and with all windows known in advance.  **That gap is $3.44$ pp of target mass on SensorScope and $1.32$ pp on U-Air (protocol $R$ always-on) over the $20$ seeds.** ... **Read-only ladder contrasts instead use the report-half subset, whose same-support optimum differs slightly, so band verdicts are not convertible between the two.**" |
| **P0-3a** decision rule, non-test status, `\label` | `round_v1/PREREG.md:43-44` (interval containment); `round_v3/EXECUTION_REPORT.md:105`; sibling disclaimer at L1631-1637 | L611-617: "...is $\pm0.10$ in those units, **and a contrast is read as inside the band when its paired interval lies within $\pm0.10$; ... and the band itself is a practical-significance convention rather than a hypothesis test.**" New `\label{subsec:equivalence_band}` at L573, cited at L1842 (resolves to III-F, the subsection that defines the band). |
| **P0-3b** ℓ₁ scoping of the flatness sentence | `MYOPIC_DIAG.json:3-13` (ℓ₁ surface only); `round_v3/EXECUTION_REPORT.md:132-133`; Theorem 2 at L1249-1254 | L961-964 -> L973-976: "...has median $10^{-13}$, so **that $\ell_1$ surface is flat and its minimizer over $\mathcal{C}_r$ is not unique, and the group term selects among the solutions that are equivalent in $\|M_r\boldsymbol\alpha-\boldsymbol\mu\|_1$ rather than among all of $\mathcal{C}_r$.**" Removes the read against Theorem 2 (round-6 F1) without touching the theorem. |
| **EA-1** (extra) debt-ablation ruler | L1627-1637 (the 0.5 % device is a descriptive worst-group tolerance for external comparisons); `tables/E4_ABLATION_HOLM_RESULTS.csv` (the ablation statistic is a relative change) | L2063-2069 -> L2059-2065: "far below the **descriptive $+0.5\%$ worst-group tolerance that governs the external comparisons of Section~\ref{subsec:eval_rq2} on a different endpoint**.  That matches the accounting..." |
| **EA-2** (extra) worst-group equivalence wording | L1631-1637 ("descriptive rather than a formal non-inferiority test"); `tables/E3_SCD_WORSTGROUP_VS_FEDAU_OBSUSE_HOLM.csv` (no significant Holm contrast) | L1782-1783 -> L1781-1783: "Four-block worst-group RMSE **stays within the descriptive $+0.5\%$ worst-group tolerance versus** FedAU-Window and ObsUse-Window (...)" (was "is interchangeable with") |
| **EA-3** (extra) necessity half of the band rule | `round_v1/PREREG.md:43-44` (necessity = interval entirely beyond +0.10) | in the same sentence as P0-3a: "...lies within $\pm0.10$; **a component removal is read as necessary only when that interval lies entirely beyond the band in the worsening direction**, and the band itself is..." |
| **F4 (not applied)** | round-6 F4 is at L1547-1551, which is in none of the four paragraphs named by P0-1..P0-3 | Not touched, per the conditional instruction |

**Deletions (all verified duplication; every deleted passage is retained elsewhere in the paper).**

1. **§VII intro roadmap paragraph** (pre-fix L1437-1448), deleted in full; the `\subsection{Experimental Setup}`
   now follows the RQ bullets directly (L1449). Duplicated content and where it survives:
   (a) "The balanced control is a no-harm check, and a risk-interchangeability experiment tests whether
   arrival-weighted and deployment-target-weighted risks are interchangeable." -> RQ bullet 1 (L1440-1441),
   Introduction (L262-264), §VII-B (L1640-1656);
   (b) "Independent rankings follow on T-Drive taxi replay, NSW-Traffic regions, and City Scanner occupancy ...
   none of those rows is mixed into Table II." -> Introduction (L264-267), Table I caption (L1500-1504), §VII-B
   (L1700-1772);
   (c) "The main comparison is a development table under always-on protocol R on station traces, not a jointly
   measured mobile ranking; an intermittent-occupancy protocol table on the same station clients is in the
   supplemental material." -> Introduction (L262-264, L272-275), Table II caption (L1851-1853);
   (d) "A component-removal ablation drops one component at a time: on SensorScope, Design moves Δ_group while
   RMSE_μ stays essentially flat, so Δ_group is a structural diagnostic." -> §VII-E (L1944-1945, which states the
   ablation design verbatim) and §VII-C (L1775-1780, which carries the numbers), RQ bullet 3 (L1445-1446).
2. **§VII-C "Development-table findings" (L1919-1927)**, two duplicated runs removed:
   (a) "of that gap, 68.96 % on SensorScope and 83.07 % on U-Air is already recoverable by uniform server
   weights, the surviving part is carried by the projected reference, and the terms of (P2) and the debt
   recursion stay inside the equivalence band." -> stated with intervals in the same subsection (L1815-1846);
   (b) "against the no-Design baselines it ties all six on prediction while keeping the structural advantage
   against five, with Debt-Cal tying on both endpoints and TEST mean relative worst-group differences of +0.48 %
   and +0.44 % versus FedAU-Window and ObsUse-Window" -> same subsection (L1785-1806, L1794-1795).
   The paragraph's non-duplicated content (the U-Air interchangeability scoping, the under-served-block pointer,
   the intermittent-occupancy sign result) is retained verbatim.

**Length accounting (measured).** Lines 2 230 -> 2 226 (-4); words 12 256 -> 12 229 (-27); characters
112 608 -> 112 386 (-222); semicolons 105 -> 102 (-3); em dashes 0 -> 0. Net length did not increase.

**Structure counts (measured).** `\label{` 96 -> **97** (the single new band label at L573; `main.aux` now has 97
`\newlabel`, and `\newlabel{subsec:equivalence_band}` resolves to III-F). Nothing else moved:
`\begin{table` 4, `\begin{figure` 4, `\begin{equation` 37, `\cite{` 42, `\section{` 8, `\subsection{` 29,
`\begin{proposition` 4, `\begin{theorem` 2 - all identical to the pre-v4 snapshot and to the pre-fix state.

**Verification (run from `TO_OVERLEAF_paper_tmc_r1_clean`).** `pdflatex -draftmode main.tex` once, then
`pdflatex main.tex` twice: `Output written on main.pdf (17 pages, 886558 bytes)`; 0 errors (no `!` line in
`main.log`), 0 undefined references/citations, 0 `Overfull`, 21 `Underfull` boxes (identical to the pre-fix
control), 5 multiply-defined bibliography labels (pre-existing, caused by `\externaldocument{supplemental}`
sharing `reference.bib`; present in the pre-fix control with the same count). A same-input control compile of
`snapshots/2026-10-03-pre-design-fix/main.tex` gave 17 pages / 886581 bytes / 0 errors / 0 overfull / 21 underfull
/ 0 undefined, so nothing but the intended text moved. The MiKTeX wrapper exits non-zero with
`log4cxx ... setFile(...pdflatex.log) call failed` because the sandbox denies writes to `%LOCALAPPDATA%`, not
because of a LaTeX error; the LaTeX run itself completes and writes `main.pdf` and `main.log`.

---

## 9. Status and next owner

```text
Missing values: none invented; every requirement in Sec. 6 is NOT RUN
Execution priority: R1 > R4/R8 > R2/R3 > R7 > R5/R6
No-fabrication status: satisfied (read-only evidence use; no run; no new result directory)
Next CCFA owner: ccf-experiment-designer for R1/R3/R4 and for the R2 re-reporting protocol;
  ccf-integrity-auditor + ccf-submission-checker for R7/R8 (bundle inventory and gate serialisation);
  ccf-paper-writer for the manuscript-hygiene items recorded but not applied here
    (round-6 R5-8: define Proj_{C_r}(β̂) at first use, L245-246; R5-10: label the (43) coefficients as U-Air
    Table IV entries, L2030-2032; F2: the third sense of "interchangeable" at L1679-1680; F4: the doubled
    connectives at L1547-1551, outside the paragraphs this pass was authorised to edit)
```

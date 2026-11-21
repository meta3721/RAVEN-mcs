# IEEE TMC review — RAVEN-MCS (round 3, post route-A repair write)

```text
Mode:                 version-comparison (frozen 2026-09-12 contract, inherited unchanged)
Venue and assumptions: IEEE Transactions on Mobile Computing, regular paper, 20-seed paired
                      protocol; main 16 pp, supplemental 15 pp. Venue guide not re-read; the
                      prior round's format findings are carried forward unchanged.
Artifacts reviewed:   TO_OVERLEAF_paper_tmc_r1_clean/{main.tex, appendix.tex} at the post-write
                      state; the prior round's issue set M1-M6, m1-m8;
                      results_active_set_repair/round_v1/** (the repair evidence);
                      RAVEN_MCS_PUBLIC_REPRO_R1/** (the shipped bundle).

**Erratum 2026-09-27.** Concern `M9` is **withdrawn** and concern `M8`'s mechanism
attribution is **withdrawn**; `M8`'s observation stands. Both rested on the E4 tree arm
`raven_wo_inst`, which `artifacts/e4_ablation_semantic_integrity_repair_r1/E4_WO_INST_FINAL_DECISION.json`
had already declared invalid on 2026-08-12. `M7` is unaffected. Details in SS5.
Snapshot of the prior canonical report: snapshots/2026-09-27-post-routeA-write/raven-mcs-tmc-review-pre-round3.md
```

## 1. Frozen comparison contract, and one inherited arithmetic defect

| contract element | value |
|:---|:---|
| dimensions and weights | 8 dimensions; `0.10 / 0.20 / 0.25 / 0.15 / 0.10 / 0.10 / 0.05 / 0.05` |
| anchors | 1 = unacceptable, 5 = strong |
| overall mapping | weighted sum, then calibrated rounding to a 1–10 stance |
| decision threshold | 4/10 = weak reject |
| comparison threshold | absolute weighted delta below 0.05 = unchanged; otherwise improved / regressed |
| historical version | the post-Option-1 manuscript scored in round 2 |
| current version | post route-A repair write (items 26–32 in the diagnosis record) |

**Contract note, disclosed rather than silently repaired.** Round 2 states "weighted absolute
readiness = 2.85". The rubric as printed gives
`2(0.10)+3(0.20)+2(0.25)+4(0.15)+3(0.10)+2(0.10)+3(0.05)+4(0.05) = 2.75`.
The stated value is 0.10 too high. Weights, anchors and thresholds are **not** changed
mid-comparison, so the historical weighted value used below is the recomputed **2.75**; the
historical stance (4/10 weak reject) is unaffected either way, and round 2's relative-progress delta
(+0.40) is arithmetically correct as printed.

## 2. Paper summary (unchanged in substance)

Windowed-asynchronous federated completion for mobile crowdsensing, framed as target-mass alignment.
The pipeline is decomposed into opportunity (`R`), observation (`O`) and usable-update (`U`)
selection layers; the server forms a selection-corrected reference from legal pre-outcome histories
and calibrates it inside the feasible window. The Design factor is an explicit configuration with two
settings, both reported. Evidence: SensorScope, U-Air and NSW-Traffic protocol blocks, a T-Drive
replay, and a same-backbone baseline family.

**What changed in this round.** The U-Air `FedAvg-Window` row, and three further no-Design rows in
the appendix family table, were rebuilt on the active set each method's own definition licenses. The
metric scale is now disclosed. The sentence claiming a `−9.11 % / −6.17 %` improvement over
TwoStage-Hájek and FedAvg was replaced by a within-Design-family statement plus a six-comparator
qualification of the structural claim.

---

## 3. Relative-progress scorecard (frozen contract)

| dimension | historical | current | delta | weight | explaining issue IDs |
|:---|:---:|:---:|:---:|--:|:---|
| 1 Originality / novelty | 2 | 2 | 0 | 0.10 | — |
| 2 Soundness / technical quality | 3 | **4** | **+1** | 0.20 | `T1` resolved (invalid baseline); metric scale disclosed |
| 3 Evidence / experiments | 2 | 2 | 0 | 0.25 | `T1` resolved but `M8` revealed; no new predictive evidence |
| 4 Clarity / presentation | 4 | 4 | 0 | 0.15 | text sharpened; appendix juxtaposition now harder to read |
| 5 Reproducibility | 3 | **2** | **−1** | 0.10 | **`M7`** revision-induced bundle mismatch |
| 6 Significance / impact | 2 | 2 | 0 | 0.10 | `M8` sharpens the standing deduction |
| 7 Related work / positioning | 3 | 3 | 0 | 0.05 | — |
| 8 Terminology / notation | 4 | 4 | 0 | 0.05 | — |

**Weighted progress delta = +0.10. Classification: improved (marginal).**

The repair is a genuine integrity upgrade: a comparison the paper's own artifacts contradicted has
been removed and replaced by one that survives a 1600/1600 per-window active-set assertion, and the
undisclosed per-dataset standardization is now stated. It buys 0.20 on soundness. It costs 0.10 on
reproducibility because the manuscript moved and the shipped bundle did not.

**Traceable score decrease.** `5 Reproducibility −1` — issue `M7`; first seen: this round; origin:
`revision_regression`; applies to: `current`; evidence:
`RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_MAIN_EFFECTIVENESS.csv` carries U-Air `FedAvg-Window`
`RMSE_mu_mean = 1.18824` while the manuscript prints `1.1119`, and `main.tex` §Data and Code
Availability names that file as canonical.

## 4. Inherited issue ledger

| ID | round-2 concern | status | evidence in the current version |
|:--|:---|:---|:---|
| `T1` | the U-Air baseline comparison was invalid | **resolved** | four rows rebuilt; `main.tex` Table III and three `appendix.tex` tables now carry licensed-set values; the false claim is gone from the text |
| `M1` | the revision replaced a bad rule with no rule | **unresolved** | §V-E still reports the factorial without a selection rule |
| `M2`/`M5` | the recoverable-gain ceiling is nowhere stated | **unresolved** | no ceiling sentence in §VII; the F-1/H-U1 results remain outside the paper |
| `M3` | the deployment target is evaluation-derived | **unresolved** | unchanged |
| `M4` | U-Air Design-on is harmful by 6.55 % and this is not converted into a decision | **partially resolved** | the endpoint trade is now reported with the `Δ_c-s` gain and the `Δ_group` qualification; the 6.55 % harm still carries no decision |
| `M6` | the measured-`U` gap is acknowledged but never converted into a positioning decision | **unresolved** | unchanged |
| `m1`–`m8` | minor items | carried forward | not re-audited this round |

## 5. New issues

### M7 — The shipped reproduction bundle contradicts the corrected tables. **Major. Revision-induced.**

`RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_MAIN_EFFECTIVENESS.csv` reports U-Air `FedAvg-Window` at
`1.18824`, TwoStage-Hájek at `1.21596`, RAVEN-MCS-SCD at `1.11306`. The manuscript now prints
`1.1119` for FedAvg-Window, and

```text
main.tex:2092  The bundle \texttt{RAVEN\_MCS\_PUBLIC\_REPRO\_R1} contains paired seeds,
main.tex:2094  \texttt{SCD\_PHI.csv}, canonical Table~II
```

points a reader at it. Four of the bundle's eighteen tables contain any post-repair value, and none
of them is the main-effectiveness table. A reader who follows the availability statement reproduces
the superseded numbers.

Two pre-existing items sit in the same file and belong in the same pass: it calls
`TABLE_II_MAIN_EFFECTIVENESS.csv` "canonical Table II" while the main comparison is **Table III**
(Table II is the T-Drive hybrid table), and its method names (`RAVEN-MCS-Full-Design`,
`RAVEN-MCS-SCD`) do not match the manuscript's (`RAVEN-Design`, `RAVEN-NoDesign`).

*Repair condition:* regenerate the bundle tables from the repair artifacts, or scope the availability
sentence to the blocks the bundle actually covers.

### M8 — A simpler baseline matches the structural endpoints, and no component explains it. **Major. Newly revealed by evidence.**

On the licensed set, Debt-Cal ties RAVEN-NoDesign on both structural endpoints:

| metric | RAVEN-NoDesign | Debt-Cal | paired relative (TEST / ALL20) | Holm p |
|:---|:---|:---|:---|:---|
| `Delta_group` | 1.0165 | 1.0175 | -0.052 % / -0.089 % | 0.71 / 0.41 |
| `Delta_c-s` | 1.2949 | 1.2948 | -0.055 % / +0.015 % | 0.67 / 0.90 |
| `RMSE_mu` | 1.1131 | 1.1144 | -0.124 % / -0.115 % | n.s. |

Debt-Cal carries instant group calibration, debt and a reference penalty; it has no observation IPW, no
usable-update IPW and no Hajek local loss, and its reference term is set to `lambda_beta = 1e-8`.

**The mechanism sentence in the first version of this concern is withdrawn.** It read the manuscript's
ablation family as saying that removing instant calibration moves `Delta_group` from `1.0924` to
`1.1196`, and concluded that the P2 group-calibration term carries the U-Air structure. The `1.1196` came
from the E4 tree arm `raven_wo_inst`, which `E4_WO_INST_FINAL_DECISION.json` had already declared
**invalid** on 2026-08-12 (`proven_invalid: true`, 40 corrective reruns authorised) because it skipped P2
entirely. With P2 preserved, the corrected ablation moves `Delta_group` by `-0.089 %` on U-Air and
`-0.260 %` on SensorScope when instant calibration is removed, and by at most `0.26 %` for any other
single component, against `-6.943 %` for the Design factor.

The honest form of the concern is therefore stronger in one way and weaker in another. The **observation**
stands: a simpler method ties RAVEN-NoDesign on both structural endpoints, and the manuscript now says
so. The **attribution** does not: the paper's own ablation family attributes the U-Air `Delta_group`
structure to the Design factor alone, and no component explains why Debt-Cal reaches the same endpoint
without the correction family. *Diminishes* dims 3 and 6.

*Repair condition:* state in SSV that the U-Air structural effect is carried by the Design factor and that
the ablation family does not separate Debt-Cal's route to the same endpoint; or add the controlled
`design off x instant calibration off` arm, which first needs the unfinished call site recorded in the
verification report's SS0.2 to be covered.

### M9 — WITHDRAWN

The first version of this concern claimed that `tab:app_e3_uair` presents duplicate arms, on the strength
of two bitwise identities: `raven_wo_inst` (E4) equals `twostage_hajek` (E3), and `inst_cal` (E3) equals
`raven_wo_debt` (E4). **The concern is withdrawn.**

`raven_wo_inst` is not a row of that table, and the E4 directory of that name is the arm invalidated on
2026-08-12. It coincides with TwoStage-Hajek because both take the pre-repair `alpha = beta` branch of
`window_runner`, not because the paper presents one method twice. The second identity creates no
duplicate row either: `inst_cal` is a table row and `raven_wo_debt` is not, and their coincidence means
only that the Hajek local loss is numerically inert on U-Air. No manuscript table needs a duplicate-arm
marking, and dim 7's repair condition for this concern is removed below.

### Minor, this round

- The three feasibility-audit counts after `tab:app_p2_coverage` (778 warnings / 85 runs / 6438
  windows / `2.686e-8`) describe the pre-repair batch. They were deliberately left untouched because
  their population is not the 180-run set the table covers; they need a solver-log re-audit or an
  explicit scope sentence.
- `tab:app_e3_uair` now shows Debt-Cal (a no-Design method) at `RMSE_μ` 1.1144 and `Δ_group` 1.0175,
  both better than RAVEN-Design's 1.1911 and 1.0924, with only a caption clause explaining that the
  rows use different active sets. Add one sentence in the surrounding text.
- §Data and Code Availability hashes and the "24 of 54 bibliography entries unverified" item are
  unchanged from round 2.

---

## 6. Absolute-readiness scorecard (current version only)

| # | dimension | weight | score | confidence | deduction | repair condition |
|:--|:---|---:|:---:|:---|:---|:---|
| 1 | Originality / novelty | 0.10 | 2 | high | novelty rests on coordinating known estimators with a target map, and the map is not exogenous | obtain an exogenous target map |
| 2 | Soundness / technical quality | 0.20 | **4** | high | the invalid comparison is gone, the metric scale is stated, the active-set repair is asserted per window; residual: the stale bundle and the unfinished validation diff | refresh the bundle; state the audit scope |
| 3 | Evidence / experiments | 0.25 | 2 | high | no predictive endpoint separates the methods, and `M8` shows the structural endpoint is matched by a simpler baseline | report the P2-component implication, or add the 2×2 arm |
| 4 | Clarity / presentation | 0.15 | 4 | high | clear and candid; the rebuilt appendix rows now juxtapose two active sets in one table | one explanatory sentence |
| 5 | Reproducibility | 0.10 | **2** | high | `M7`: the shipped bundle contradicts the corrected main table, and `WorstGroupRMSE` for the rebuilt rows lives in a working artifact rather than the bundle | regenerate the bundle |
| 6 | Significance / impact | 0.10 | 2 | high | the only large reachable effect remains a deletion on one block, and `M8` weakens the structural contribution | a decision rule plus the ceiling |
| 7 | Related work / positioning | 0.05 | 3 | medium | positioning against non-random-selection and MCS-sampling work is reasonable | no repair condition outstanding from this round |
| 8 | Terminology / notation | 0.05 | 4 | high | manuscript terminology is consistent; the bundle's method names are not | align the bundle names |

**Weighted absolute readiness = 2.85 → 4 / 10, weak reject.** Unchanged stance.

**Remaining blocking evidence, in the order that would move the stance:**

1. **A decision rule for the Design setting** (`M1`), now the single largest gap. The factorial is
   honest but leaves a deployment choice unmade, and the paper's own support-cost measurement is the
   material a rule would use.
2. **The ceiling sentence** (`M2`/`M5`). Two pre-registered experiments already exist and are not in
   the paper; stating them converts an unbounded claim into a measured bound.
3. **An exogenous target map** (`M3`), which nothing else substitutes for.
4. **The bundle refresh** (`M7`), cheap and mechanical.
5. **The `M8` attribution gap**, now evidenced: the ablation family attributes the U-Air structural effect to the Design factor alone and does not separate Debt-Cal's route to the same endpoint.

## 7. Multi-reviewer panel

| reviewer | lens | stance |
|:---|:---|:---|
| R1, methodology | is the U-Air comparison valid, and is the repair complete? | **borderline.** `T1` is properly fixed and the per-window assertion is the right instrument. R1 will still ask why the bundle was left behind, and will spot `M9`. |
| R2, theory-to-practice | does the correction family do anything measurable? | **reject.** Unchanged from round 2, and `M8` sharpens it: the effective term is one the paper shares with a simpler baseline. |
| R3, systems and reproducibility | can I reproduce Table III? | **reject.** Not from the shipped bundle. This is the clearest new deduction in the round. |
| R4, writing (read-only) | is the text honest and readable? | **weak accept on writing alone.** The rewritten U-Air paragraph is more precise than the sentence it replaced. |

Synthesis: three of four reviewers hold a reject or borderline stance. The repair improved the
paper's integrity without creating the evidence the contribution needs, and it opened one new
reproducibility gap.

---

## 8. Concern-to-action table

| concern | severity | affected dimension | fix class | owner | score-impact condition |
|:---|:---|:---|:---|:---|:---|
| `M1` no Design-selection rule | major | 6, 4 | writing + method decision | `ccf-paper-writer`, author | +1 on 6 if a rule with a stated criterion is added |
| `M2`/`M5` ceiling unstated | major | 3, 6 | writing (evidence exists) | `ccf-paper-writer` | +1 on 3 if stated with the MDE caveat |
| `M3` evaluation-derived target | major | 1, 3 | new external evidence | author | +1 on 1 if an exogenous map is used |
| `M7` bundle contradicts Table III | **major, new** | 5 | artifact regeneration | `ccf-integrity-auditor` | +1 on 5 on refresh |
| `M8` simpler baseline matches the structure | **major** | 3, 6 | writing, or the 2x2 arm | `ccf-paper-writer`, `ccf-experiment-designer` | holds 3 at 2 until addressed |
| ~~`M9` duplicate arms in the family table~~ **withdrawn 2026-09-27** | — | — | — | — | no effect |
| feasibility-audit scope | minor | 2, 5 | re-audit or one scope sentence | `ccf-integrity-auditor` | none alone |
| appendix active-set juxtaposition | minor | 4 | one sentence | `ccf-paper-writer` | none alone |

## 9. Recommended next CCFA owner

`ccf-integrity-auditor` for `M7` and the feasibility-audit scope, because both are artifact-truth
questions with a mechanical repair. Then `ccf-paper-writer` for `M8`, `M9` and the appendix sentence.
`M1` and `M2` remain writing tasks on evidence that already exists.

## 10. Checks run

Compiled both documents after the write: main 16 pp, supplement 15 pp, 41 equation labels, 0 undefined
references or citations, 0 overfull boxes above 2 pt, `tools/freeze_appendix_refs.py --check` reports
0 to freeze and 0 unresolvable (57 kept), em dashes 2 in `main.tex` and 0 in `appendix.tex`.
Re-derived every replaced cell against the repair artifacts and confirmed the superseded values are
absent (`verify_report_claims.py`, section S11, 26 checks). Read the bundle's eighteen CSV tables and
diffed their U-Air values against the manuscript.

## 11. Unresolved or unverified

- The bundle's `TABLE_E3_MAIN_EFFECTIVENESS.csv` and `TABLE_E3_FULL_METHODS_SUPPLEMENT.csv` were not
  diffed value by value against the manuscript; only `TABLE_II_MAIN_EFFECTIVENESS.csv` was checked in
  detail. The `M7` refresh should sweep all of them.
- The `m1`–`m8` minor items from round 2 were not re-audited.
- The 24 unverified bibliography entries remain unverified; no new citation was added this round.
- TMC's current page and anonymity policy was not re-verified against the official page.
- The 2×2 arm that `M8` asks for cannot be run in the current code state; the blocker is recorded in
  `results_active_set_repair/round_v1/C3_TWO_BY_TWO.json`.

## 12. Confidence and comparability

**High confidence** in the comparison. Both versions were read directly, the contract is inherited
unchanged, and every claim above is anchored to a file path or a re-derived value. One inherited
arithmetic defect in the contract is disclosed in §1 and handled without changing any weight or
threshold. The absolute-readiness scorecard is comparable to round 2 because the venue standard,
rubric and reviewer roles are the same; the single difference is the corrected historical weighted
value, which does not move the stance.

## 13. Output self-check

Scorecards kept separate and not fused ✓ · every score of 3 or below carries a concrete deduction and
a repair condition ✓ · every decrease cites an issue ID, current evidence, origin and delta ✓ · no
weight or threshold changed mid-comparison ✓ · inherited defect disclosed rather than silently fixed ✓
· no manuscript prose rewritten ✓ · all concerns tied to a file, line, table or re-derived value ✓ ·
no acceptance probability asserted ✓

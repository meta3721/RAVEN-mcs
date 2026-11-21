# RAVEN-MCS — full scientific review after the Option 1 revision

```text
Mode: full (scientific + writing + format), assessment only. No manuscript text was changed.
Venue: IEEE Transactions on Mobile Computing, regular paper. main.pdf 16 pp. + supplemental.pdf 15 pp.
Inputs: TO_OVERLEAF_paper_tmc_r1_clean/{main.tex, appendix.tex, supplemental.tex, main.pdf,
        supplemental.pdf}; artifacts/e3_formal_runs_r1/**; artifacts/e4_core_mechanism_ablation_r1/**;
        artifacts/e3_f1_*_r1/**; artifacts/a5_a6_audit/**;
        ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md (T1–T9, D-1…D-6);
        ccfa-review-reports/raven-mcs-f1-experiment-summary.md
Previous canonical review: snapshots/raven-mcs-tmc-review-2026-09-20-pre-option1.md
Rubric frozen before scoring: the eight dimensions and weights used in
        snapshots/raven-mcs-tmc-review-2026-09-12-absolute-readiness.md.
```

---

## Paper summary

The paper reframes windowed-asynchronous federated mobile-crowdsensing completion as *target-mass
alignment*. Sensing is decomposed into opportunity `R`, observation `O`, and usable-update delivery
`U`; the arrival law need not equal the public deployment target. The server forms a
selection-corrected reference from legal pre-outcome histories (design ratio `ζ̂`, sequential
Hájek-normalized `O` and `U` factors, local Hájek), projects it onto a feasible aggregation set with
a strongly convex program (P2) under a simplex, a coordinate cap and an `ℓ2` support bound, and
carries unresolved group under-service as target debt. Two propositions and one theorem are scoped
to the ideal pooled estimator. Empirically the paper reports a development table on two station
traces, a T-Drive taxi replay, NSW-Traffic, City Scanner, and a Pilot 2 block with measured `O`.

**What the Option 1 revision changed.** `φ` — the share of training risk units whose attached
client–stratum carries zero public target mass — has been removed from every `.tex` file. It had been
the per-block switch selecting RAVEN-Design versus RAVEN-NoDesign. It is replaced by an explicit
configuration `D_t ∈ {on, off}`; equation (32) now defines the two branches of `ζ̂^o` in one place,
Algorithm 1 takes `D_t` as an input, and both settings are reported on both main blocks. Table III
gains a SensorScope `RAVEN-NoDesign` row and loses the `(forced)` label on U-Air, so it is now a
within-dataset 2×2 Design factorial. The zero-target statistic survives only as a descriptive column
in the appendix.

---

## Likely stance and calibrated score

**Weak reject, 4 / 10.** The revision fixes the single most trust-damaging element in the previous
version and adds one genuinely new evidence row. It does not touch either of the two defects that
actually determine the verdict: the deployment target is still evaluation-derived, and the paper
still does not state the ceiling on what its own correction family can achieve. A reviewer who reads
only the paper will conclude the method is honest but unproven; a reviewer who reads the released
artifacts can now also conclude that the reported tolerances sit near the ceiling rather than near a
miss, which is worse for the contribution than an ordinary negative result.

Confidence: **high** for the paper's own claims and the artifact comparisons (all numbers below were
recomputed); **medium** for venue-policy items (TMC page rules not verified this round).

---

## Quantitative scorecard

Frozen weights from the 2026-09-12 contract. 1 = unacceptable, 5 = strong.

| # | dimension | weight | score | confidence | deduction | repair condition |
|:--|:---|---:|:---:|:---|:---|:---|
| 1 | Originality / novelty | 0.10 | 2 | high | The paper states its novelty is not IPW or Hájek but their coordination with target semantics and feasibility-aware calibration; the coordinates are individually standard and the composite is not shown to buy anything measurable | A demonstrated endpoint where the composite beats its own components by more than the ceiling of any single component |
| 2 | Soundness / technical quality | 0.20 | 3 | high | The propositions are correctly scoped, but two load-bearing operational choices are unconstrained: the per-block Design setting now has **no** rule at all, and the design ratio is applied against a target map derived from the evaluation split | A stated, pre-registered, exogenous basis for the Design setting and for the target map |
| 3 | Evidence / experiments | 0.25 | 2 | high | No predictive endpoint shows a significant win; the structural endpoint is decoupled from prediction by the paper's own ablations; `U` is measured in no block; the recoverable-gain ceiling is nowhere stated | State the ceiling and either obtain a measured-`U` block or reframe the contribution as diagnostic |
| 4 | Clarity / presentation | 0.15 | 4 | high | Clear and unusually candid; residual: `g` is never defined, six scenarios are never enumerated, and the two Design settings are presented without guidance on which to deploy | Define `g`; enumerate the scenario family; state the deployment rule the reader should use |
| 5 | Reproducibility | 0.10 | 3 | medium | Bundle exists and hashes are frozen, but the newly added `WorstGroupRMSE` cell is not a stored metric in the released per-seed files and was recomputed from checkpoints; 24 of 54 bibliography entries are unverified | Ship the recomputed per-block scores and complete the bibliography verification |
| 6 | Significance / impact | 0.10 | 2 | high | The only large, reachable effect in the whole evidence base is a *deletion* on one block, and the paper does not report it as such | Report the module-ceiling map so the reader can see where the method's value actually is |
| 7 | Related work / positioning | 0.05 | 3 | medium | Positioning against non-random-selection and MCS-sampling literature is reasonable; the closest same-backbone comparators include the paper's own ablated constructions, which is disclosed but weakens the ranking | At least one independent same-backbone baseline whose aggregation family is not a RAVEN variant |
| 8 | Terminology / notation consistency | 0.05 | 4 | high | The `φ` overload and the Design/NoDesign naming drift are now gone; residual undefined `g` | Define `g` at first use |

**Weighted absolute readiness = 2.85, reported as 4 / 10 weak reject** after the calibrated rounding
used in the frozen contract. The weighted sum is not a linear acceptance map and is not fused with
the progress scorecard below.

---

## Relative-progress scorecard (frozen contract, kept separate from the above)

| dimension | historical (pre-Option-1) | current | delta | weight |
|:---|:---:|:---:|:---:|---:|
| Originality / novelty | 2 | 2 | 0 | 0.10 |
| Soundness / technical quality | 2 | 3 | **+1** | 0.20 |
| Evidence / experiments | 2 | 2 | 0 | 0.25 |
| Clarity / presentation | 3 | 4 | **+1** | 0.15 |
| Reproducibility | 3 | 3 | 0 | 0.10 |
| Significance / impact | 2 | 2 | 0 | 0.10 |
| Related work / positioning | 3 | 3 | 0 | 0.05 |
| Terminology / notation | 3 | 4 | **+1** | 0.05 |

**Weighted progress delta = +0.40. Classification: improved.** The revision is a real integrity
upgrade: it removes a data-derived switch that was keyed on evaluation-split coverage, and it
converts the main table into a within-dataset factorial, which two earlier review rounds asked for by
name. It adds no new evidence beyond one recomputed row.

**Issue provenance for the new concerns.**

| issue | provenance |
|:---|:---|
| the Design setting has no rule at all now | **revision-induced** — the previous version at least had a (bad) pre-registered rule; a real regression in dimension 2 |
| the U-Air endpoint trade is now visible in the headline table | **newly revealed** — the previous version reported one row per block and hid the conflict |
| the target map is evaluation-derived | **previously known, latent** — applies equally to both versions |
| the gain ceiling is unstated | **previously known, latent** — applies equally to both versions |
| one new `WorstGroupRMSE` cell is not stored in the bundle | **revision-induced** — introduced with the new row |

---

## Top strengths

1. **The revision removes a claim-integrity hazard rather than defending it.** `φ` selected between
   two named methods per block, and the record's own audit shows that on at least four of six blocks
   the statistic is fixed by evaluation-split coverage or by construction. Removing it, restating the
   Design factor as a configuration, and reporting both settings is what a strong reviewer would have
   demanded. Verified end to end: no `\phi` remains in any `.tex`, and none of
   `forced RAVEN-Design`, `RAVEN-Design (forced)`, `frozen heuristic`, or `Design fraction` survives
   in either built PDF.
2. **Table III is now a genuine within-dataset Design factorial.** `RAVEN-Design` and
   `RAVEN-NoDesign` are reported on SensorScope *and* U-Air from the same 20 paired seeds. The
   SensorScope `RAVEN-NoDesign` row is new: `RMSE_μ` 7.9384 ± 0.0468, `WorstGroupRMSE`
   8.6711 ± 0.0481, `Δ_group` 1.0265 ± 0.0278, `Δ_c-s` 1.2719 ± 0.0308. The recomputation path
   reproduces the published `RAVEN-Design` four-block row to 4×10⁻⁵ before being applied, which is
   the right way to add a cell.
3. **The scoping is unusually precise for the venue.** The propositions are labelled ideal-pooled,
   the calibration program is presented as a property of (P2) rather than as evidence of risk
   optimization, `U` is disclosed as measured nowhere, the protocol blocks are labelled
   semi-synthetic with their construction constants, and the within-stratum dispersion of the two
   selection margins is stated beside those constants.
4. **The build is clean.** 16 + 15 pages, 41 numbered equations, zero undefined references or
   citations, zero overfull boxes above 2 pt, and the appendix cross-reference freeze resolves with
   0 entries to freeze and 0 unresolvable.

---

## Major concerns

**M1 — The revision replaced a bad rule with no rule, and does not say so.**
*Evidence.* `main.tex` §V-E now states that the Design factor "is a configuration of the deployment,
supplied to Algorithm 1 before the window opens", that both settings are reported, and that "a
data-derived selector would have to be justified on the same evaluation it changes". Table III and
§VII-C.1 report the factorial. What no passage states is *how the per-block setting reported in each
table was chosen*. The previous version answered that with `φ`; the current version answers it with
nothing. A reviewer will read "configured" as "chosen after seeing the numbers", which is the
retrospective-selection risk the old rule was, ineffectively, there to defuse.
*Severity.* Major. *Criterion.* Soundness (dim. 2). *Fix class.* Method/soundness plus writing.
*Score impact.* +0.5 on Soundness if the paper states plainly that no pre-registered selection rule
exists for these blocks, that the factorial is the primary evidence, and that a deployment rule
requires an exogenous target map; +1 if such a map is obtained and the rule derived from it.

**M2 — The recoverable-gain ceiling is still nowhere in the paper, and it is the number that decides
the contribution.**
*Evidence.* Read from the released artifacts, the whole correction family is worth: exact `p` and `q`
together, +0.008% (SensorScope) and −0.028% (U-Air) on `RMSE_μ`; exact `p` alone, −0.005% and
+0.017%; removing the observation weighting outright, +0.012% and −0.010%; removing the usable
weighting, +0.012% and +0.024%; removing debt, +0.000% and +0.001%. Every propensity route is within
0.03% in either direction. An independently executed experiment (160 cells, 20 paired seeds, harness
reproducing the released `raven` run to 0.0000%) made the selection law deliberately harder —
within-stratum, label-correlated, marginal preserved to 5.6×10⁻¹⁷ — and the exact-propensity
advantage rose 15–21× to +0.104% and −0.251%, still below the paper's own 0.5% threshold. The paper
reports tolerances and per-block rewrites without ever telling the reader that the reachable range is
this small.
*Severity.* Major, and the closest thing to fatal, because it converts "we are competitive" into "the
measured quantity cannot move".
*Criterion.* Evidence (dim. 3), Significance (dim. 6). *Fix class.* Evidence reporting.
*Score impact.* +0.5 on Evidence for stating the ceiling honestly; +1 to +1.5 if a block is added
where the ceiling is materially larger.

**M3 — The deployment target is still evaluation-derived, and it is the paper's stated central
object.**
*Evidence.* `RMSE_μ` is computed against a `μ` built from the test-split region share, and on
SensorScope and U-Air the target map degenerates to unit counts on a station trace. The record's §1
is unambiguous: the label does not match the artifact. The Option 1 revision does not touch this and
cannot without an exogenous map.
*Severity.* Major. *Criterion.* Soundness (dim. 2), Originality (dim. 1).
*Fix class.* External evidence. *Score impact.* +1 overall if one endpoint's target is external to
the method.

**M4 — One block shows the method's own configuration being harmful by 6.55% at 10σ, and the paper
still headlines a different setting per block without resolving the conflict.**
*Evidence.* On U-Air, Design on versus off (paired, 20 seeds): `RMSE_μ` 1.1911 versus 1.1131
(+6.553%, 10.0σ), `Δ_group` 1.0924 versus 1.0165 (−6.943%, 12.7σ), tail RMSE 1.1999 versus 1.1174
(−6.875%, 10.0σ), and `Δ_c-s` 1.2334 versus 1.2949 (+4.990%, 17.1σ). On SensorScope the same
contrast is +1.237% and +0.597% on the two structural endpoints at 9.2σ and 8.6σ with prediction
unchanged (+0.005%, 0.3σ). The paper now states both, a large improvement over the previous version,
but it does not say what a practitioner should do with a setting that wins three endpoints and loses
the fourth at 17σ.
*Severity.* Major. *Criterion.* Evidence (dim. 3), Significance (dim. 6).
*Fix class.* Writing plus one analysis: a decision rule keyed to the endpoint the deployment actually
pays for. *Score impact.* +0.5 on Significance.

**M5 — The `+0.5%` tolerance is presented as a near miss when the ceiling analysis shows the gap is
structural rather than marginal.**
*Evidence.* The best any reweighting reaches is `Central-Delivered`, 0.112% better than the reported
SensorScope row and, re-anchored to the deployed U-Air setting, 5.85% *worse*. The undelivered-sample
bound (`Central-All`) is 4.442% and 12.841% better and is unreachable by any weighting. On
SensorScope the paper is therefore chasing at most 0.1%, and on U-Air the deployed setting is already
better than uncorrected central training and every federal baseline in the tree.
*Severity.* Major. *Criterion.* Evidence (dim. 3). *Fix class.* Evidence reporting.
*Score impact.* Folded into M2.

**M6 — The measured-`U` gap is acknowledged but never converted into a positioning decision.**
*Evidence.* The paper states that `U` is measured in no block. Combined with M2, the layer the paper
devotes most of its machinery to is simultaneously unmeasured and worth ≤0.03% on the reported
endpoints.
*Severity.* Major. *Criterion.* Evidence (dim. 3), Significance (dim. 6).
*Fix class.* Scope decision: obtain a measured-`U` block, or demote `U` from the contribution list.
*Score impact.* +0.5 to +1.

---

## Minor concerns

| # | concern | location | evidence | fix class |
|:--|:---|:---|:---|:---|
| m1 | `g` is never defined, yet the limitations and the theory use it | Assumption 1; Thm. 2 | source read | writing |
| m2 | the six-scenario family is never enumerated and `complete_counteracting` is invisible | §VII-A.2; supplement | record §2 L2, §4 | writing |
| m3 | one new Table III cell (`SensorScope RAVEN-NoDesign WorstGroupRMSE` = 8.6711) is not a stored metric in the released per-seed files | Table III; `tab:app_block_rmse` | recomputed from checkpoints via the `run_int_r_v2.py` path; reproduces the published row to 4×10⁻⁵ | reproducibility |
| m4 | 24 of 54 bibliography entries are unverified; one misattribution was already found and fixed in an earlier round | `reference.bib` | record §7 | reproducibility |
| m5 | two of the five same-backbone baselines are RAVEN constructions; disclosed, but they are the comparators for the headline tolerance | §VII-C.4 | `aggregation/methods.py` lines 314–320 | evidence |
| m6 | equation (32) now restates a branch that (15) already gives under the within-stratum assumption; harmless but it lengthens §V-C | §V-C, (32) | source read | writing |
| m7 | author block is still a mix of placeholders and identifiers | title page | reported in earlier rounds; **not re-checked this round** | desk |
| m8 | TMC submission page policy not verified this round | format | — | desk |

---

## Writing and presentation concerns

The revision improves presentation materially: the abstract now states the trade-off in numbers
instead of naming a fallback, Algorithm 1 is shorter and has no data-derived branch, and the appendix
section that used to be organized around the switch is now a provenance table. Three residual
writing issues:

- The abstract's "Both settings are reported on every block rather than chosen by a data-derived
  rule" is the right sentence, but it invites the follow-up question M1 leaves unanswered. A reader
  finishes the abstract knowing the settings trade off and not knowing which one the paper would
  ship.
- Table III's caption now carries both the factorial design and four paired relative effects. It is
  accurate and dense; the effects might read better in the body text with the caption stating only
  the factor.
- §VII-C.1's SensorScope paragraph interleaves the factorial contrast with the FedAvg comparison in
  one breath. Separating "Design versus Design-off" from "RAVEN versus FedAvg" would reduce the risk
  that a reader attributes the structural win to the factor rather than to the correction stack.

---

## Format / venue concerns

- 16 pages of main text plus a 15-page supplement. TMC's allowed submission length was not verified
  this round; if the cap is 14 formatted pages the paper is over and the excess is billable. Flagged
  in three consecutive rounds, still unverified.
- Cross-reference integrity is good: 41 numbered equations, 0 undefined references, and the appendix
  literal freeze resolves cleanly after the revision.
- Author masking consistency was not re-checked this round.

---

## Multi-reviewer panel

**Reviewer A — sampling and identification.**
Lens: is the estimand the one claimed? Score tendency: weak reject. Confidence: high.
Positive signal: Proposition 2 is correctly scoped, A1–A6 are split, and the paper discloses that A6
fails on the released traces. Negative signal: the target map is evaluation-derived and the
observation propensity is constructed with a stratum-constant rate, so the worked estimator is
demonstrated under its own assumption. Evidence basis: `main.tex` §VI, §VII-A.2; the A5/A6 audit;
`artifacts/a5_a6_audit/audit_records.csv`. Score-change condition: an exogenous target on one block.

**Reviewer B — experiments and endpoints.**
Lens: can the reported endpoints move at all? Score tendency: reject. Confidence: high.
Positive signal: the Design factorial is now complete and paired. Negative signal: the ceiling is
≤0.03% for every propensity route and ≤0.12% for any reweighting on SensorScope, so the paper reports
a 0.5% tolerance as though the gap were epistemic rather than structural. Evidence basis: recomputed
from `artifacts/e3_formal_runs_r1/**` and `artifacts/e4_core_mechanism_ablation_r1/**`.
Score-change condition: a block where the exact-propensity or exact-delivery advantage exceeds 1%.

**Reviewer C — systems and deployment.**
Lens: what would an operator do differently? Score tendency: weak reject. Confidence: medium.
Positive signal: the Design factor is explicit, so the deployable configuration space is stated.
Negative signal: the paper reports a setting that wins three endpoints and loses the fourth at 17σ and
offers no rule; and the only large reachable effect is deleting a module. Evidence basis: Table III;
the module ablation. Score-change condition: a decision rule tied to the endpoint the deployment is
paid for.

**Reviewer D — reproducibility.**
Lens: can the tables be rebuilt from the release? Score tendency: borderline. Confidence: medium.
Positive signal: hashes are frozen, the drivers exist, and the Design factorial was rebuilt from
checkpoints and validated against the published row. Negative signal: the new `WorstGroupRMSE` cell is
not in the released per-seed metric files, and 24 bibliography entries are unverified. Evidence basis:
run directories; the freeze manifests. Score-change condition: ship the recomputed scores.

**Panel synthesis.**
Agreement: the Option 1 revision is a genuine integrity improvement; the factorial is correct; the
build is clean. Disagreement: Reviewer C would accept a diagnostic reframing, Reviewer B treats the
ceiling as disqualifying for the current claim set. Decisive accept axis: an endpoint whose target is
external to the method, with a corrected gain above the stated tolerance. Decisive reject axis: an
evaluation-derived target combined with a correction family whose entire reachable range sits below
the reported tolerance. Unresolved evidence: whether a measured-`U` block can be obtained. Final
calibrated stance: **weak reject, 4 / 10** — unchanged in level, improved in composition.

---

## Concern-to-action table

| # | severity | action | owner | score impact |
|:--|:---|:---|:---|:---|
| M1 | major | state that no pre-registered Design-selection rule exists for these blocks; make the factorial the primary evidence; state that a deployment rule needs an exogenous target map | `ccf-paper-writer` | Soundness +0.5 |
| M2 | major | add the ceiling: every propensity route ≤0.03%, any reweighting ≤0.12% on SensorScope, the 4.44% / 12.84% undelivered-sample bound unreachable | `ccf-paper-writer` | Evidence +0.5 |
| M3 | major | obtain an exogenous deployment target for one endpoint | external | +1 overall |
| M4 | major | add a deployment rule keyed to the paid endpoint and state the 17σ `Δ_c-s` trade explicitly | `ccf-paper-writer` plus one analysis | Significance +0.5 |
| M5 | major | fold into M2 | `ccf-paper-writer` | — |
| M6 | major | obtain a measured-`U` block, or demote `U` from the contribution list | scope decision | +0.5 to +1 |
| m1 | minor | define `g` | `ccf-paper-writer` | clarity |
| m2 | minor | enumerate the six scenarios and report `complete_counteracting` | `ccf-paper-writer` | evidence clarity |
| m3 | minor | ship the recomputed per-block scores in the bundle | `ccf-submission-checker` | reproducibility |
| m4 | minor | complete the bibliography verification | `ccf-integrity-auditor` | reproducibility |
| m7 | minor | fix the author block | user | desk |

---

## Recommended next CCFA owner

`ccf-paper-writer` for M1, M2, M4, m1, m2 — all bounded text changes whose numbers are already
computed. `ccf-experiment-designer` only if a measured-`U` block or an exogenous target is pursued
(M3, M6). No rewrite was performed in this pass.

---

## Checks run

- `pdflatex main.tex` ×3 + `bibtex main`; `pdflatex supplemental.tex` ×3 + `bibtex supplemental`;
  `pdflatex main.tex` once. Result: 16 + 15 pages, 0 errors, 0 undefined references or citations,
  0 overfull boxes above 2 pt, 41 numbered equations.
- `python tools/freeze_appendix_refs.py --check`: 0 to freeze, 0 unresolvable, 57 appendix-internal
  references kept.
- Case-sensitive ripgrep for `\phi` over `main.tex`, `appendix.tex`, `supplemental.tex`: no matches.
- Text extraction of both built PDFs for `forced RAVEN-Design`, `RAVEN-Design (forced)`,
  `frozen heuristic`, `Design fraction`: no matches.
- Recomputation of every paired contrast quoted above from the per-seed `final_metrics.json` files in
  `artifacts/e3_formal_runs_r1/runs` and `artifacts/e4_core_mechanism_ablation_r1/runs` (20 paired
  seeds), and of the four-block `WorstGroupRMSE` values from the saved checkpoints.

## Unresolved or unverified

- TMC submission page policy (third consecutive round).
- Author masking (not re-checked this round).
- 24 of 54 bibliography entries.
- NSW-Traffic target-map provenance, and the 0.34% residual between the U-Air four-block identity and
  the published `RMSE_μ`, carried over from the diagnostic record.
- Whether a measured-`U` block is obtainable at all.

## Output self-check

Contract order followed; every table has consistent column counts; scores and confidence are reported
separately and the two scorecards are not fused; every score of 3 or below carries a deduction and a
repair condition; no placeholder remains; no manuscript prose was rewritten. One caveat on scope: the
absolute-readiness score is unchanged at 4/10 while the progress delta is +0.40. That is the intended
behaviour of the two-scorecard contract, not an inconsistency — the revision fixed a trust defect and
added a row without moving either of the two defects that set the verdict.

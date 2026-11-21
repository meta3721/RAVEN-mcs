# RAVEN-MCS — IEEE TMC review (current manuscript), round 12

```text
Mode: version-comparison (relative progress + absolute readiness, reported separately) with the full
  scientific, writing and format sections. Assessment only; no prose rewrite.
Date: 2026-10-06
Venue and assumptions: IEEE TMC journal revision, method-plus-measurement paper. Page budget treated as
  TMC regular 12 pp, with the project's MOPC allowance up to 18 pp.
Frozen score contract inherited from TMC-J-R4 (not modified): dimensions Originality / Soundness /
  Evidence / Clarity / Reproducibility / Significance / Related work / Terminology;
  weights 0.10 / 0.20 / 0.25 / 0.15 / 0.10 / 0.10 / 0.05 / 0.05; anchors 1-5; overall 1-10;
  |weighted delta| < 0.05 = unchanged.
Versions compared:
  historical = TO_OVERLEAF_paper_tmc_r1_clean/main.tex, sha256 88ecd743321e38e9 (the text frozen by the
               round-10 record audit and scored in the previous canonical report);
  current    = TO_OVERLEAF_paper_tmc_r1_clean/main.tex, sha256 59e4f4d5cffff4ff, 113345 B,
               mtime 2026-10-05 00:15 (the r11 text-repair pass).
  Snapshot of the historical file: snapshots/2026-10-04-pre-r11/main.tex.
  Previous canonical report archived at snapshots/2026-10-06-pre-round12-raven-mcs-tmc-review.md.
Diff: 4 hunks, +5 / -6 lines, enumerated in "Checks run". No other source file changed this span
  (appendix.tex 2026-10-02, supplemental.tex unchanged at e99e1058...).
This pass re-read the four changed sites, the availability paragraph, the equivalence-band subsection,
  the ceiling section, the limitations, the (P2) attribution, and the decision-related sentences.
  It did not re-derive the proofs and did not run a new literature search.
New evidence available this round (not in the historical comparison): results_regime_b_endpoints/round_v1/
  (P0-P2D) and results_h_headroom/round_v3{,_fix}/ — reported under "New evidence" below.
Post-review revision, 2026-10-06: this review's M2, M4 and contribution-3 items were applied as three
  prose-only edits (3 hunks, +9/-1, +63 words; no number, table, figure or claim changed; main.pdf held
  at 17 pp). The manuscript is now main.tex sha256 02447bfe6256632b..., so the "current version" of this
  comparison is the pre-edit 59e4f4d5cffff4ff. The revision ledger is Part VII of
  ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md and the response artifact is
  ccfa-review-reports/raven-mcs-r12-response-to-review.md. E1, E2 and NEW-r12-3 remain open; the next
  comparison round should score against 02447bfe... and decide whether Reproducibility moves.
```

## Frozen comparison contract

Contract `TMC-J-R4`, inherited unchanged: the eight dimensions above, their weights, anchors 1–5, overall 1–10, the `|weighted delta| < 0.05` classification threshold, the five reviewer roles, the 4/10 acceptance threshold and the 5/10 current stance, and the evidence standard (manuscript text at a stated sha256 plus named repository artifacts; no author promise substitutes for manuscript evidence). Both versions were scored under this contract before the r11 edit summary was consulted; the summary was then used only to locate the four sites.

## Relative-progress scorecard

| Dimension | Historical (88ecd743) | Current (59e4f4d5) | Delta | Weight | Explained by |
|---|---:|---:|---:|---:|---|
| Originality | 2 | 2 | 0 | 0.10 | no change in the contribution claim |
| Soundness | 5 | 5 | 0 | 0.20 | no claim touched; proofs not re-derived |
| Evidence | 3 | 3 | 0 | 0.25 | no new manuscript evidence; the new round measured the decision endpoint but the paper claims no decision skill, so nothing moves |
| Clarity | 4 | 4 | 0 | 0.15 | the terminology half of its repair condition is done; the contribution-bullet split is not |
| Reproducibility | 2 | 2 | 0 | 0.10 | M2 undone; the supplemental overfull remains |
| Significance | 2 | 2 | 0 | 0.10 | E2 unchanged |
| Related work | 3 | 3 | 0 | 0.05 | not re-searched |
| Terminology | 3 | **4** | **+1** | 0.05 | R5-16 resolved: the two colliding uses of "recoverable" are gone |

**Weighted progress delta = +0.05 → classification `improved`.**

Disclosure: the classification sits exactly on the frozen threshold (`|0.05|` is not `< 0.05`). If Terminology were held at 3 the classification would be `unchanged`. The raise rests on the historical entry's own repair condition ("one sentence that renames one of the two uses"), which the diff satisfies at both sites, and on the current text containing two `recoverable` uses in a single sense (ceiling only). It is not rounded to `unchanged`, and it is not claimed to be more than one dimension of weight 0.05.

## Issue ledger changes and provenance

| ID | first seen | status | origin | applies to | affected dims | evidence | score effect |
|---|---|---|---|---|---|---|---|
| R5-16 | round 5 | **resolved** | inherited | both | Clarity, Terminology | diff hunks 1 and 4: L1819 and L2194 now read "closed by uniform server weights"; the current file has two `recoverable` uses, both the ceiling sense (L2103, L2106) | Terminology +1 |
| M3 | round-10 state | **resolved** | inherited | both | Clarity | diff hunk 3: the privacy sentence is resequenced so its antecedent is federated learning, not `Gate_t` | none |
| A-8 | round 10 audit | **resolved** | inherited | both | Clarity | diff hunk 2: the `8.23`–`21.73` range is deleted; the qualitative claim (the uncorrected reference violates the recorded feasibility constraints) stays | none |
| M2 | round-10 state | unresolved | inherited | both | Reproducibility | current L2202–2220 names the Table II bundle, `SCD_PHI.csv`, table CSVs, T-Drive/NSW/City Scanner files; `w1/` and `PAPER_NUMBERS.csv` still unnamed | none |
| E1 | round 9 | unresolved | inherited | both | Evidence, Significance | L2096–2101 unchanged; ceiling unchanged | none |
| E2 | round 9 | unresolved | inherited | both | Significance, Originality | L229–237, L1826–1856 unchanged | none |
| NEW-r12-1 | r12 endpoint round | unresolved (constraint on E1's repair) | newly_revealed_by_evidence | current | Evidence | `P2D_REPORT.md`, `tables/P2D_CONTRASTS.csv`: on the paper's own U-Air checkpoints regime B retains 0.00–2.48 % of the exceedance mass against regime A's 17.5–33.9 %, and no threshold in {25, 35, 50, 75} µg/m³ gives either arm detection | none |
| NEW-r12-2 | round 9 (F10) | partially resolved | inherited | both | Reproducibility | `main.log` 0 multiply-defined / 0 undefined / 0 Overfull; `supplemental.log` still 1 Overfull | none |

Ledger handoff: these rows are ready for `ccf-rebuttal-writer`, which owns the canonical ledger; this review does not update that ledger itself.

## Traceable score decreases

**None.** No dimension falls; no issue in this round is a `revision_regression`; the two new rows carry no negative score effect. The validator run (see "Checks run") confirms that no current-dimension decrease lacks a traced cause, trivially satisfied here.

## Absolute-readiness scorecard (current version only)

| Dimension | Score | Weight | Confidence | Deduction | Repair condition | Expected movement |
|---|---:|---:|---|---|---|---|
| Originality | 2 | 0.10 | medium | Unchanged from the previous pass: the added objects are deployment-target semantics, a three-layer pre-outcome factorization, and a finite-window feasible set, with convex matching and two-stage IPW declared as prior ingredients (L258–263). FedPALS/FedIPW were not re-searched this pass. | A constraint-and-information mapping stating an irreducible difference from those two lines | +1, not enough alone to move the stance |
| Soundness | 5 | 0.20 | medium | None on the claims re-read; the four changed sites are wording. Proofs not re-derived. | None on this axis from the current text | none |
| Evidence | 3 | 0.25 | high | No prediction contrast survives Holm (L2096–2101). The ceiling bounds the recoverable RMSE gap at \|H\| ≤ 0.217 %. Uniform weights close 68.96 % (SensorScope) and 83.07 % (U-Air) of the FedAvg group gap. City Scanner non-inferiority is untestable at the declared margin; the deletion primary is inconclusive. **New this round: the decision endpoint the previous pass pointed at has now been measured on the paper's own checkpoints and is saturated, so it cannot serve as that endpoint either (NEW-r12-1).** | One pre-registered endpoint, on a setting whose headroom is above its detectable effect, **and whose decision quantity is not saturated** — the U-Air exceedance endpoint is excluded by measurement | +1 Evidence; the change that would move the stance to 6 |
| Clarity | 4 | 0.15 | high | The double-use defect is gone, so the remaining deduction is the one the previous pass named: contribution 3 still carries the theorem, the verdict, the κ exclusion and a table pointer in one bullet (L215–237). | Split that bullet | +1 Clarity; weighted sum 3.45; stance unchanged |
| Reproducibility | 2 | 0.10 | medium | The availability paragraph still does not name the subtree that carries the new numbers (M2), and the supplemental build keeps one Overfull box (NEW-r12-2, the F10 residue). | Name `w1/` or its index in the availability paragraph | +1 Reproducibility |
| Significance | 2 | 0.10 | medium | Unchanged: the large measured effect is the Design switch on one block, and it is a cost on RMSE_μ as well as a gain on client–stratum mismatch. | A task where the structural gain changes a quantity a deployment would act on | +1, only with the Evidence repair |
| Related work | 3 | 0.05 | medium | Positioning is honest about prior ingredients; the irreducibility claim is still a sentence rather than a mapping. | The mapping named under Originality | +1 or −1 depending on what the mapping shows |
| Terminology | 4 | 0.05 | high | Raised this round. Residual note, recorded but not charged: the text now distinguishes "the closable gap" (L606–609, uniform → hindsight optimum) from "closed by uniform server weights" (L1819, L2194), two different objects named by two near-identical words. | Fold the two names into one sentence if a reader test shows confusion | none |

Weighted readiness sum = 0.10×2 + 0.20×5 + 0.25×3 + 0.15×4 + 0.10×2 + 0.10×2 + 0.05×3 + 0.05×4 = **3.30**. Overall stance **5/10, borderline negative (held)**. The Evidence axis (weight 0.25, anchored at 3) is unchanged, and it is the axis the stance turns on.

## New evidence this round (not part of the historical comparison)

Two experiment rounds completed after the historical version was frozen. They were run against the repository's evidence tree, not against the manuscript, and the manuscript was not modified.

1. **The Design switch is not a baseline artifact.** Rebuilding the U-Air FedAvg arm so that it reproduces the stored artifacts exactly (20/20 seeds, four metrics, identical active sets) leaves the manuscript's Design-removal pattern intact: the design-off arm buys 5.2–6.2 % RMSE_μ and 5.9–9.2 % group mismatch against a 3.1–4.8 % client–stratum price, on a 288-key support identical in both arms. The record's own support-cost figures were reproduced from the same runs (+6.98 / +6.99 / +6.32 / +6.99 / +7.00 / +6.31 %). This **strengthens** an already-reported number and moves no dimension.
2. **The decision endpoint is saturated (NEW-r12-1).** Across all six conditions and both arm families, on the paper's own checkpoints, the exceedance-decision endpoint at 35 µg/m³ (and at 25, 50, 75) cannot separate the regimes on decision skill: the wider-support regime retains 0.00–2.48 % of the exceedance mass against 17.5–33.9 % for the narrow one, and its lower flip rate is entirely false-alarm suppression. The manuscript is **not** contradicted — it claims no decision skill and says the decision is "reported rather than made by the method" (L1573) — but the previous pass's suggested repair route for E1 ("a decision quantity") is now measured and closed on this block.

## Top strengths

- The negative results remain printed rather than implied, and the four edits this round removed two of the three wording defects that stood between the reader and those results.
- The Design-switch row and its price are now independently reproducible from the repository (new evidence 1); the manuscript's `6.885 %` is not an artifact of the baseline it was measured against.
- The scope statement at L1573 survives measurement: the method reports the decision rather than making it, which is exactly what the saturated endpoint shows.
- The revision is small and inspectable: four hunks, no claim touched, no new inconsistency introduced.

## Major concerns

**E1. Alignment is still not shown to buy accuracy — and the previous repair route is now measured and closed.** Severity: major. Evidence: L2096–2101 and the ceiling; plus `P2D_REPORT.md` (new). The prediction family has no Holm survivor, and the decision quantity that the round-9 pass proposed as the alternative has no discriminative power on this block at any declared threshold. Affected: Evidence, Significance. Fix class: new evidence on a different setting or a different decision quantity, pre-registered before it is run. Owner: `ccf-experiment-designer`. Score-impact condition: a pre-registered endpoint whose headroom exceeds its detectable effect **and** whose decision base rate is not saturated. Repeating the current blocks, or re-running the same U-Air exceedance endpoint, will not meet it.

**E2. The program the method is named for is still not the part that moves the endpoint.** Severity: major for venue fit, not a correctness error. Evidence: L229–237, L1826–1856, unchanged. Fix class: a setting where those terms move an endpoint, or a contribution statement that leads with the projection and the Design factor. Owner: `ccf-paper-writer` for the statement; `ccf-experiment-designer` for a setting.

## Moderate concerns

**M2. The availability paragraph still does not point at the artifacts for the new numbers.** L2202–2220 lists the frozen Table II bundle and the City Scanner/T-Drive/NSW files; the `w1/` ladder subtree that carries +0.768 pp, +0.922 pp, the ±0.10 band and ε_impl is not named. Affected: Reproducibility. Owner: `ccf-paper-writer`. Score-impact: Reproducibility 2→3.

**M4. The band's rule is on the page, its provenance is not.** The equivalence band now has a labelled subsection (L568–617) with its units, reading rule, and the "practical-significance convention rather than a hypothesis test" caveat, and the non-convertibility of ladder versus report-half verdicts. Nothing in `main.tex` states where the band, or the reading rule, was fixed before the results. Affected: Clarity, Reproducibility. Fix class: one pointer to the pre-registration artifact. Owner: `ccf-paper-writer`. Score-impact: none alone; bundled with M2 it supports Reproducibility 2→3.

**NEW-r12-3 (minor). "Closable" versus "closed".** Two different gaps are now named by two near-identical words (L606–609 and L1819/L2194). It is materially better than the previous collision, and it is recorded rather than charged. Owner: `ccf-paper-writer` if a reader test shows confusion.

## Writing and presentation concerns

- Contribution 3 (L215–237) is still one bullet carrying a theorem, a verdict, a κ exclusion and a table pointer; it is the last item of the Clarity repair condition.
- The Design-switch equation keeps its "chart fitted to one U-Air row" label (L2047); keep that label attached to every later citation of the 1.39 threshold.
- The limitations paragraph (L2149–2176) now ends with a correctly attached privacy sentence; the list remains hard to audit because each sentence changes subject.

## Format and venue concerns

- `main.pdf` remains 17 pp (round-10 audit, not re-measured). That fits an 18 pp MOPC allowance and exceeds a 12 pp regular TMC article; the submission must declare its track. Not charged as a technical defect.
- Anonymity is not applicable to a journal revision. Author names in the current source were not re-checked.

## Claim–evidence audit

| Claim | Where | Evidence | Strength |
|---|---|---|---|
| Deployment and arrival risks are not interchangeable | Abstract; contribution 1 | Proof under differing laws; not re-derived this pass | Adequate, conditional on the proof |
| Ideal sequential correction recovers compatible target mass and does not prove risk optimization | Abstract; contribution 2 | Theorem with A1–A3 | Adequate as a scoped theorem |
| The remaining structural gain is the projection; other frozen terms stay inside the band | Abstract; contribution 4; L1826–1856 | 20 paired seeds, bootstrap CIs, Holm, ±0.10 band | Strong, and the claim is the right size |
| Design on costs 6.885 % RMSE_μ and gains 4.990 % client–stratum mismatch on U-Air | Abstract; L1992–1996 | Holm-significant ablation on that block; **independently reproduced this round on a repaired baseline arm** | Adequate for that block; still not generalized |
| No Holm-significant RMSE win | Table III caption; L2096–2101 | The registered prediction family | Strong as a negative result |
| Trained projection rules improve structure and not prediction | L2079–2101 | 20 seeds; Holm on both endpoints | Adequate, correctly marked as new rules |
| City Scanner non-inferiority is untestable; deletion unresolved; one trace is a trace-level outlier | L2162–2169 | `A1_POWER.csv`, `C1_PRIMARY.json`, B0-b model seeds | Adequate, matched to artifacts |
| The deployment decision is reported rather than made by the method | L1573 | **Corroborated this round**: the decision endpoint is saturated for both regimes, so no decision-quality claim could have been supported anyway | Adequate, and now measured |
| ε_impl ≤ 2.42e-5 and its printed ratios | Appendix K | Consistent with pp = Δ/2×100 | Adequate |

## Multi-reviewer panel

```text
Reviewer: Best-justified
Lens: strongest defensible accept case
Score / score tendency: 6/10
Confidence: high
Main positive signal: the structural attribution is measured, pre-registered, and now independently
  reproducible on a repaired baseline arm; the manuscript's own scope statement survives a new
  measurement designed to test it.
Main negative signal: a measurement paper still has to show that the measurement changes a decision.
Evidence basis: L79-85, L239-255, L1811-1856, L1573; round_v3_fix/H_FIX_DIFF.csv
Score-change condition: a deployment quantity that moves with the projection.

Reviewer: Critical
Lens: strongest reject case
Score / score tendency: 4/10
Confidence: high
Main positive signal: the negative results are disclosed, so this is not an over-claim rejection; the
  four edits removed wording defects rather than adding claims.
Main negative signal: the named calibration program is still not shown to be necessary, prediction does
  not move, and the decision endpoint the previous pass proposed is now measured and saturated.
Evidence basis: L229-237, L2096-2124; results_regime_b_endpoints/round_v1/P2D_REPORT.md
Score-change condition: the Evidence repair in E1, on a setting where the decision quantity is not
  saturated. Wording repairs will not move this reviewer.

Reviewer: Method / soundness
Lens: whether the causal sentences match the diagnostics
Score / score tendency: 6/10 on soundness; does not raise the paper's stance
Confidence: medium (proofs not re-derived)
Main positive signal: the flat-surface sentence and the 0.0107 pp tie-break still agree with
  MYOPIC_DIAG.json; the four edits are wording only and introduce no new inconsistency.
Main negative signal: insufficient evidence on the proofs themselves.
Evidence basis: L964-980; MYOPIC_DIAG.json
Score-change condition: a counterexample in the proof, or a diagnostic contradicting L975-977.

Reviewer: Reproducibility auditor
Lens: can a reader rebuild the reported numbers from what the paper names
Score / score tendency: 2/5 on this dimension
Confidence: high for the paragraph, medium for the bundle
Main positive signal: the verifier clean result and the w1/ subtree both exist; the paragraph names the
  Table II bundle and the City Scanner files correctly.
Main negative signal: the subtree carrying the ladder numbers, the band and eps_impl is still unnamed,
  and the supplemental build keeps one overfull box.
Evidence basis: L2202-2220; main.log / supplemental.log; round-10 bundle audit
Score-change condition: naming w1/ or its index file in the availability paragraph.

Reviewer: Writing and presentation
Lens: can a reviewer read each sentence once
Score / score tendency: 4/5 on clarity
Confidence: high
Main positive signal: "recoverable" now carries one sense; the privacy sentence has a correct
  antecedent; the feasibility-range sentence no longer mislabels two arms' tokens.
Main negative signal: contribution 3 is still overloaded, and "closable gap" versus "closed by uniform
  weights" invites a second reading.
Evidence basis: the four diff hunks; L215-237; L568-617
Score-change condition: split contribution 3.

Agreement: the structural result is real and correctly scoped; the prediction result is a measured
  null; this revision is a wording pass and claims nothing new.
Disagreement: whether honest scoping plus an independently reproduced ablation is enough for TMC. The
  sympathetic reviewer says the measurement is the contribution; the critical reviewer says the venue's
  decision quantity still has not moved, and now has one fewer candidate instrument.
Decisive accept axis: a task where the projection changes a decision that is measurable on that task.
Decisive reject axis: Evidence, reinforced this round by the saturated decision endpoint.
Unresolved evidence: the proofs (not re-derived); irreducibility versus FedPALS and FedIPW (not
  re-searched); the bundle's own hash state (taken from the round-10 audit).
Final calibrated stance: 5/10, borderline negative. The critical axis decides.
```

## Concern-to-action table

| ID | Severity | Action | Owner | Stance effect |
|---|---|---|---|---|
| E1 | Major | Do not add seeds on SensorScope, U-Air or City Scanner, and do not re-run the U-Air exceedance endpoint: it is saturated at every declared threshold. A repair needs a setting with headroom above its detectable effect **and** a decision quantity with a non-degenerate base rate, pre-registered before the run. | `ccf-experiment-designer` | The only action that can move 5→6 |
| E2 | Major | Lead the contribution list with the projection and the Design factor; keep (P2)'s other terms as the uniqueness device. | `ccf-paper-writer` | None by itself |
| M2 | Moderate | Point the availability paragraph at the `w1/` ladder artifacts. | `ccf-paper-writer` | Reproducibility 2→3 |
| M4 | Moderate | Add one pointer to where the band and its reading rule were fixed. | `ccf-paper-writer` | None alone; supports the Reproducibility raise |
| NEW-r12-3 | Minor | Fold "closable gap" and "closed by uniform weights" into one naming scheme. | `ccf-paper-writer` | None |

## Recommended next CCFA owner

`ccf-paper-writer` for M2, M4 and NEW-r12-3, plus the contribution-3 split that completes the Clarity condition; those edits make the current claims easier to audit and do not change the stance. `ccf-experiment-designer` owns E1, and only if a setting with non-saturated decision headroom is actually proposed. `ccf-rebuttal-writer` owns the ledger handoff for the eight rows above; this review does not update the ledger itself.

## Checks run

- Hash chain: `snapshots/2026-10-04-pre-r11/main.tex` = `88ecd743321e38e9…` (identical to the hash the previous canonical report reviewed) against the current `main.tex` = `59e4f4d5cffff4ff…`, 113345 B; `supplemental.tex` unchanged at `e99e1058…`; `appendix.tex` untouched since 2026-10-02.
- Exact diff of the two versions: 4 hunks, +5 / −6 lines — (1) L1819 "recoverable → closed by uniform server weights"; (2) L1834 deletion of the `8.23`–`21.73` range; (3) L2172–2176 privacy sentence resequenced; (4) L2194 the same rename as (1). No other hunk.
- `recoverable` census: historical 4 lines (two senses) → current 2 lines (ceiling sense only, L2103/L2106).
- Availability paragraph re-read in full (L2202–2220): `w1/` and `PAPER_NUMBERS.csv` still absent.
- Build logs: `main.log` 0 multiply-defined / 0 undefined / 0 Overfull; `supplemental.log` 0 / 0 / **1 Overfull**.
- New-evidence artifacts read for this review: `results_regime_b_endpoints/round_v1/P2D_REPORT.md`, `tables/P2D_CONTRASTS.csv`, `P2C_CLASS_TEST.csv`; `results_h_headroom/round_v3_fix/H_FIX_DIFF.csv`, `H_DECISION_fix.json`; `ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md` items 45–52.
- Machine check: `CCFA-Skills/ccf-paper-reviewer/scripts/validate_version_comparison.py .rb_work/r12_contract.json` → **PASS: version comparison is internally consistent** (weights sum to 1, deltas equal current − historical, weighted delta 0.05 recomputed from the frozen weights, provenance values valid, no untraced decrease).
- The `8.23`/`21.73` question that stood as "unverified" in the previous canonical report is closed by deletion: the tokens no longer appear in `main.tex` (their source had been located in the round-10 record work).

## Unresolved or unverified

- Proofs in §VI were not re-derived.
- FedPALS and FedIPW were not re-searched; the Related-work score carries the previous pass's uncertainty.
- Page count and bundle hash state are inherited from the round-10 audit, not re-measured this pass.
- The new endpoint evidence covers U-Air only; SensorScope has no decision endpoint (`E_dec` is defined for U-Air), so the saturation finding must not be generalized to other blocks.

## Confidence and comparability

Separate from both scorecards. Comparability is **high**: the two versions are the reviewed text and its four-hunk successor, with the same contract, the same reviewer roles and the same evidence standard; no external standard changed. Confidence in the relative-progress scorecard is **high** (small, fully enumerated diff, one dimension moves). Confidence in the absolute-readiness scorecard is **medium**: the proofs were not re-derived, no literature search was run, and the bundle state is inherited. The new endpoint evidence raises confidence on one specific question only — that the U-Air decision endpoint cannot carry the Evidence axis — and it leaves the rest of the readiness judgment at the previous pass's confidence.

## Output self-check

- Section order follows the version-comparison contract, with the two scorecards kept separate and confidence reported as a third field.
- Every score of 3 or below carries a deduction, a repair condition and an expected movement.
- The progress classification (`improved`, +0.05) is disclosed as sitting exactly on the frozen threshold, and the readiness stance (5/10) is not fused with it.
- No prose was rewritten, no ledger was updated, no acceptance probability is claimed.
- Tables use consistent column counts; no placeholder remains.

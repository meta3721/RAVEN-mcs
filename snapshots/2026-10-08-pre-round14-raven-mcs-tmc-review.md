# RAVEN-MCS — IEEE TMC review (current manuscript), round 13

```text
Mode: version-comparison (relative progress + absolute readiness, reported separately) with the full
  scientific, writing and format sections. Assessment only; no prose rewrite.
Date: 2026-10-07
Venue and assumptions: IEEE TMC journal revision, method-plus-measurement paper. Page budget treated as
  TMC regular 12 pp, with the project's MOPC allowance up to 18 pp.
Frozen score contract inherited from TMC-J-R4 (not modified): dimensions Originality / Soundness /
  Evidence / Clarity / Reproducibility / Significance / Related work / Terminology;
  weights 0.10 / 0.20 / 0.25 / 0.15 / 0.10 / 0.10 / 0.05 / 0.05; anchors 1-5; overall 1-10;
  |weighted delta| < 0.05 = unchanged.
Versions compared:
  historical = TO_OVERLEAF_paper_tmc_r1_clean/main.tex, sha256 02447BFE6256632B5AF2A535BCFCE2EB1024EB3A7AC957C2158B3EEDB6B1219A,
               113854 B (the post-round-12 text: M2, M4 and CL-3 applied). No copy of this file
               existed on disk; it was reconstructed by deleting exactly the two new blocks from the
               current file and the result was confirmed byte-for-byte against this hash.
  current    = TO_OVERLEAF_paper_tmc_r1_clean/main.tex, sha256 68D9B44F17A4E48D7D010C5BB83EFC4C0951B60BC3EED39A6529B56AC4FC700B,
               116379 B, mtime 2026-10-07 17:05.
Diff: 2 hunks, +36 / -0 lines, and both hunks are insertions:
  (1) L2152-L2168, +17: "Why the weights leave the prediction endpoint flat" (mechanism paragraph,
      between the Recoverable-Gain Ceiling subsection and Limitations);
  (2) L2198-L2216, +19: a second Limitations paragraph bounding what the aggregation can claim on
      prediction.
  No other source file changed this span: supplemental.tex still e99e1058..., appendix.tex still
  2026-10-02, reference.bib touched but content-identical at 3F0BE011...
Correction to the handoff: the change is +36/-0 relative to 02447BFE, not "+45/-1". The other three
  hunks of the working diff (+9/-1: L228, L617, L2260) are the round-12 M2/M4/CL-3 edits and are
  already inside the historical version.
Build re-measured this round (not inherited): supplemental.tex then main.tex x2, out-of-tree.
  main.pdf 18 pp, 0 errors, 0 undefined, 0 multiply-defined, 0 Overfull.
  supplemental.pdf 16 pp, 0 errors, 0 undefined, 0 multiply-defined, 1 Overfull (\vbox, 3.42152 pt).
  The tree's main.pdf / main.log / main.aux are still the 2026-10-06 20:45 (17 pp) artefacts, so the
  shipped PDF does not correspond to the shipped source.
This pass re-read the two new blocks in full, the availability paragraph, the ceiling subsection, the
  projection paragraphs it cross-references (L79-L88, L1830-L1841, L2085-L2098), and the round-13
  evidence trees. It did not re-derive the proofs and did not run a new literature search.
Independent evidence intake: an integrity audit of the same two passages (numeric-audit) was produced
  by another actor at 2026-10-07 20:06 and is preserved as
  ccfa-review-reports/raven-mcs-integrity-audit-new-passages.md. A wider audit of this revision, its
  defect list and the release bundle is at ccfa-review-reports/raven-mcs-integrity-audit.md. Both are
  assessment artifacts; neither changes any score below on its own authority.
```

## Frozen comparison contract

Contract `TMC-J-R4`, inherited unchanged: the eight dimensions above, their weights, anchors 1-5, overall 1-10, the `|weighted delta| < 0.05` classification threshold, the five reviewer roles, the 4/10 acceptance threshold and the 5/10 current stance, and the evidence standard (manuscript text at a stated sha256 plus named repository artifacts; no author promise substitutes for manuscript evidence).

Two dimensions were re-derived under those anchors rather than copied from round 12, because the historical version is no longer the text round 12 scored:

* **Clarity = 5 for the historical version.** Round 12 scored the *pre-edit* text Clarity 4 with a single named deduction — contribution 3 carried a theorem, a verdict, a κ exclusion and a table pointer in one bullet. CL-3 split that bullet, and the split is present in `02447BFE`. Under the same anchors the deduction is discharged.
* **Reproducibility = 3 for the historical version.** Round 12 scored Reproducibility 2 with the deduction "the availability paragraph still does not name the subtree that carries the new numbers", and set the raise condition at "name `w1/` or its index". M2 did exactly that, and M4 added the prereg pointer. The condition is met in `02447BFE`.

Both versions were scored before the revision summary was consulted; the summary was then used only to locate the two hunks.

## Relative-progress scorecard

| Dimension | Historical (02447BFE) | Current (68D9B44F) | Delta | Weight | Explained by |
|---|---:|---:|---:|---:|---|
| Originality | 2 | 2 | 0 | 0.10 | no new contribution claim; the revision adds explanation, not objects |
| Soundness | 5 | 5 | 0 | 0.20 | the mechanism argument is correct and its numbers verify; the new defects are claim-presentation, charged to Clarity |
| Evidence | 3 | 3 | 0 | 0.25 | no pre-registered endpoint with headroom above its detectable effect; the revision explains the null and bounds it, which the pre-fixed standard says does not repair the axis |
| Clarity | 5 | **4** | **−1** | 0.15 | NEW-r13-1: the new passage contradicts the paper's own characterisation of `+0.768`, and carries two precision defects |
| Reproducibility | 3 | **2** | **−1** | 0.10 | NEW-r13-2: the revision's ~10 new numbers have no depositable source in the released bundle and no pointer from the text |
| Significance | 2 | 2 | 0 | 0.10 | E2 unchanged; no task where the structural gain moves a decision |
| Related work | 3 | 3 | 0 | 0.05 | not re-searched |
| Terminology | 4 | 4 | 0 | 0.05 | no new collision; NEW-r12-3 still recorded and still not charged |

**Weighted progress delta = −0.25 → classification `regressed`.**

This is the first `regressed` classification in this line, and it is not a judgment that the revision is worthless. The revision adds a correct and fully traceable mechanism paragraph and three measured bounds, all of which improve *understanding*; it loses a scored anchor on each of two axes because it spends the round-12 Clarity and Reproducibility gains on the new text without replacing them. Every number in the mechanism paragraph reproduces exactly from the frozen artefacts: 1 475/1 877 = 78.58 %, 1 264/1 402 = 90.16 %, 1 197/1 515 = 79.01 %, `max μ` 0.5279 % over 220 groups and 0.7862 % over 144 groups. The decrease is attributable to the new sentences' *characterisation and provenance*, not to their arithmetic.

Disclosure of judgment calls, since two anchors fall:

* Clarity 5→4 rests on one clear claim-presentation defect (NEW-r13-1) rather than on a pattern. If a reader treats "the small margin" as merely loose phrasing rather than a contradiction, Clarity holds at 5 and the weighted delta becomes −0.10, which is still `regressed`.
* Reproducibility 3→2 rests on the observation that the revision's numbers are absent from the released bundle. If the venue treats the internal `results_*` trees as the evidence of record for a revision and the bundle as a release convenience, Reproducibility holds at 3 and the weighted delta becomes −0.15, which is still `regressed`.

The classification is therefore robust to both judgment calls.

## Issue ledger changes and provenance

| ID | first seen | status | origin | applies to | affected dims | evidence | score effect |
|---|---|---|---|---|---|---|---|
| R5-16 | round 5 | resolved | inherited | both | Clarity, Terminology | the two colliding `recoverable` uses were removed before the historical version | none |
| M3 | round-10 state | resolved | inherited | both | Clarity | privacy-sentence antecedent fixed before the historical version | none |
| A-8 | round 10 audit | resolved | inherited | both | Clarity | the `8.23`–`21.73` range deleted before the historical version | none |
| M2 | round-10 state | **resolved** | inherited | both | Reproducibility | L2260–L2264 names `w1/`, `w1/PAPER_NUMBERS.csv`, `verify.py`; present in the historical version | none |
| M4 | round 12 | **resolved** | inherited | both | Clarity, Reproducibility | the band paragraph points at `w1/ladder_v3/PREREG.md`; present in the historical version | none |
| CL-3 | round 12 | **resolved** | inherited | both | Clarity | the contribution bullet split is present in the historical version | none |
| E1 | round 9 | unresolved | inherited | both | Evidence, Significance | L2096–L2101; ceiling subsection; unchanged | none |
| E2 | round 9 | unresolved | inherited | both | Significance, Originality | L229–L237, L1826–L1856; unchanged | none |
| NEW-r12-1 | round 12 | unresolved | newly_revealed_by_evidence | current | Evidence | `P2D_REPORT.md`; the revision honours it and claims no decision skill | none |
| NEW-r12-2 | round 9 (F10) | partially_resolved | inherited | both | Reproducibility | rebuilt: `main.log` 0/0/0/0; `supplemental.log` 1 Overfull `\vbox` 3.42152 pt | none |
| NEW-r12-3 | round 12 | unresolved | inherited | both | Terminology | L606–L609 vs L1819/L2194 | none |
| **NEW-r13-1** | round 13 | **unresolved** | **revision_regression** | current | **Clarity** | L2160–L2162 calls `+0.768`/`+0.286` pp "the small margin", while L1834 says `+0.768` is "above the `0.5` pp practical line and stable across the two seed halves" and L2092 gives it `p_Holm = 2.7×10^{-5}`; bundled `w1/tradeoff_v4/PART_A_REPORT.md` L15/L17 marks both pairs outside the equivalence band and SensorScope passing that line. Same passage: L2207's bound of `0.17 %` is crossed by the source (largest level mean `0.1747 %`), and L2213's "every local budget from 2 to 20 steps" covers four budgets (2, 5, 10, 20), the 2-step rung being `sealed_e2_complete_aligned_read_only` | **Clarity −1** |
| **NEW-r13-2** | round 13 | **unresolved** | **revision_regression** | current | **Reproducibility** | the ~10 numbers at L2199–L2215 come from `results_estimand_selection/round_v1`, `results_gate_dose/round_v2` and `results_new_block_traffic/round_v1`; both new blocks contain **0 `\cite`** and no pointer to any artifact; a recursive search of `RAVEN_MCS_PUBLIC_REPRO_R1` finds **no** file matching `DOSE_*`, `RISK_ROWS`, `SELECTION`, `gate_dose`, `estimand`, `new_block_traffic`, `evidence_headroom`, `HEADROOM`, `TARGET_CONCENTRATION`, `MASK`, `RHO.csv`, `S0_*` or `S1_*`, and `MANIFEST.csv` names none of those trees; `w1/PAPER_NUMBERS.csv` (presented at L2262 as "indexing the printed values") has **0 of 83** rows for the new values | **Reproducibility −1** |
| NEW-r13-3 | round 13 | unresolved | previously_undetected | both | Reproducibility | 3 of 9 `figure_data` files differ from their bundle counterparts (`FIG_E3_E3_PREDICTION_RISK.csv`, `FIG_E4_E4_COMPONENT_ABLATION.csv`, `FIG_W1_DESIGN_GATE.csv`), and the divergence reaches **printed cells**: the bundle's U-Air arm means round to `1.1911/1.1911/1.1882/1.2160/1.1914`, none of which occurs in any `.tex`, against the printed `1.1954/1.1923/1.2202/1.1958`; `tables/TABLE_II_MAIN_EFFECTIVENESS.csv`, `TABLE_E3_MAIN_EFFECTIVENESS.csv`, `TABLE_E4_COMPONENT_EFFECTS.csv`, `TABLE_E4_CORE_ABLATION.csv` and `TABLE_II_FREEZE.json` all still carry the superseded `1.18824 / 1.19111 / 1.19112`, while the bundle's own `w1/audit_v5/round_v5_1/ERRATA_FOR_PAPER.md` documents the correction it fails to ship; `BUNDLE_SUMMARY.json` `file_count 2117` vs 2 118 present and `total_bytes` short by exactly `MANIFEST.csv`; `README.md` L42 falsely says `w1/frontier/PHASE3_REPORT.md` is not redistributed; the shipped `scripts/build_public_repro_bundle.py` cannot rebuild the bundle; `verify.py` detects none of it by construction | none |
| NEW-r13-4 | round 13 | unresolved | previously_undetected | both | Reproducibility | three drivers truncated to 2 B and unrecoverable; the bundle ships their City Scanner outputs with no surviving generator | none |
| NEW-r13-5 | round 13 | unresolved | previously_undetected | both | Reproducibility | on U-Air Design-on the trace-derived `K_r ≤ 3` share is 77.389 % against the printed runner-derived 90.157 % | none |
| NEW-r13-6 | round 13 | unresolved | previously_undetected | both | Reproducibility, Clarity | `E_min = 3` is not recorded in any frozen E3 config on the measured path | none |

Ledger handoff: these rows are ready for `ccf-rebuttal-writer`, which owns the canonical ledger; this review does not update that ledger. Rows NEW-r13-3 to NEW-r13-6 are `previously_undetected` and therefore deliberately carry no score effect — they are recorded so they cannot later be used to penalise only the current version.

## Traceable score decreases

Two, each with an ID, current-version evidence, origin, affected dimension and delta:

1. **Clarity 5 → 4**, ID `NEW-r13-1`, origin `revision_regression`, evidence L2160–L2162 against L1834 and L2092 plus `w1/tradeoff_v4/PART_A_REPORT.md` L15/L17, delta −1.
2. **Reproducibility 3 → 2**, ID `NEW-r13-2`, origin `revision_regression`, evidence: the new numbers' sources are absent from the released bundle and unindexed by the file the paper names, delta −1.

The machine check confirms both are traced: `validate_version_comparison.py` reports **PASS: version comparison is internally consistent**, including its rule that no current dimension may fall without a `revision_regression` or `newly_revealed_by_evidence` issue carrying a negative current effect.

## Absolute-readiness scorecard (current version only)

| Dimension | Score | Weight | Confidence | Deduction | Repair condition | Expected movement |
|---|---:|---:|---|---|---|---|
| Originality | 2 | 0.10 | medium | Unchanged: the added objects remain deployment-target semantics, a three-layer pre-outcome factorization and a finite-window feasible set, with convex matching and two-stage IPW declared as prior ingredients. FedPALS/FedIPW not re-searched. | A constraint-and-information mapping stating an irreducible difference from those two lines | +1, not enough alone to move the stance |
| Soundness | 5 | 0.20 | medium | None on the claims: the `K_r ≤ 3` mechanism is a correct Cauchy–Schwarz consequence of the frozen `eq:Cr` constraint, and every number in the mechanism paragraph reproduces exactly. Proofs not re-derived. | None on this axis from the current text | none |
| Evidence | 3 | 0.25 | high | No pre-registered endpoint with headroom above its detectable effect, and the decision instrument the round-9 pass proposed is measured and saturated (NEW-r12-1). The revision now *explains* why these two blocks cannot supply one, which is a real gain in resolution and **not** a repair of the axis. | One pre-registered endpoint on a setting whose headroom exceeds its detectable effect and whose alignment changes a prediction or a deployment decision | +1 Evidence; the change that would move the stance to 6 |
| Clarity | 4 | 0.15 | high | The round-12 bullet split holds, but the new text contradicts the paper's own characterisation of `+0.768` (L2160–L2162 vs L1834/L2092) and prints a bound (`0.17 %`) its source crosses and a coverage claim ("every local budget from 2 to 20") covering four budgets. | Re-word "the small margin" to match L1834; write `0.175 %` or a containing bound; scope the budget claim to the four rungs run | +1 Clarity |
| Reproducibility | 2 | 0.10 | high | The revision's new numbers are not in the released bundle, are not indexed by `w1/PAPER_NUMBERS.csv`, and have no pointer from the text; the tree's PDF is a 17 pp artefact against an 18 pp source. Independently: the bundle lags the paper on 3 of 9 figure files and three drivers are lost (NEW-r13-3/-4, both-version defects). | Deposit the estimand, gate-dose and traffic outputs (or name them), add the rows to `PAPER_NUMBERS.csv`, and refresh the bundle and PDF | +1 Reproducibility |
| Significance | 2 | 0.10 | medium | Unchanged: the large measured effect is still the Design switch on one block, and it is a cost on `RMSE_μ` as well as a gain on client–stratum mismatch. The new bounds are informative and still not a deployment-actionable gain. | A task where the structural gain changes a quantity a deployment would act on | +1, only with the Evidence repair |
| Related work | 3 | 0.05 | medium | Positioning stays honest about prior ingredients; irreducibility is still a sentence rather than a mapping. | The mapping named under Originality | +1 or −1 depending on what the mapping shows |
| Terminology | 4 | 0.05 | high | Residual note only: "closable gap" versus "closed by uniform weights" remain two near-identical names for two different objects. | Fold the two names into one sentence if a reader test shows confusion | none |

Weighted readiness sum = 0.10×2 + 0.20×5 + 0.25×3 + 0.15×4 + 0.10×2 + 0.10×2 + 0.05×3 + 0.05×4 = **3.30**. Overall stance **5/10, borderline negative (maintained)**.

The historical version scored 3.55 under the same card, so readiness fell 0.25. The stance nonetheless holds, and it holds for a stated reason: the stance turns on Evidence (weight 0.25, anchored at 3), which did not move, and the fall is on two non-decisive axes. The margin is narrower than round 12's and this is disclosed rather than smoothed.

## Direct answer: is the Evidence axis repaired?

**No.** Under the criterion fixed in advance for this round — Evidence rises to 4 if and only if there is a pre-registered endpoint whose headroom exceeds its own detectable effect and whose alignment/structural quantity changes a prediction or a deployment decision — the revision supplies no such endpoint. It supplies the *complement*: a measurement of why the two blocks in question cannot supply one.

Concretely, the revision now closes the routes by measurement rather than by omission:

* the weights are pinned, not free: with `E_min = 3`, `Ē_r = min(3, K_r)`, so every window with `K_r ≤ 3` admits only the uniform vector — 78.6 % of SensorScope windows and 79.0–90.2 % of U-Air windows;
* the target is near-uniform, so the criterion itself has almost no room: the largest group holds 0.53 % (220 groups) and 0.79 % (144 groups);
* the estimand route is a level shift that preserves the selection (disagreement rate 0.0 on 20/20 seeds of both datasets);
* the gate law is null on both datasets (H1 slopes `+0.001365` SS and `−0.073079` UA, both `null`; `gate_law = not supported`), and the gate decision is unreachable by construction (`gate_decision = null`, zero difference from `always_on` on 20/20 seeds);
* the decision endpoint is saturated (NEW-r12-1, unchanged);
* a new block was tried and the federated learner, not the weighting, is what limits it.

This is a materially better *negative* result than round 12 had, and it is why Soundness and confidence rise on the specific question while Evidence does not: the axis asks whether alignment was shown to buy something, and the answer the revision supplies is "here is the bound proving it cannot, on these blocks".

**The remaining positive route, stated so it is not lost.** The only surviving shape of a repair is a block where the target is genuinely concentrated at the aggregation level, so that a window's active clients actually cover the mass the criterion measures. Round 13's own scoping points at T-Drive's four-group map (largest group 51.44 % of the mass, against 0.53 % here) or at a campaign with declared monitoring weights. That is a **new experiment, not a re-analysis of these blocks**, and it requires its own pre-registration with the headroom stated before the run. Adding seeds, re-running the U-Air exceedance endpoint, or re-wording the current passages will not move this axis.

## New evidence this round (not part of the historical comparison)

Four measurement rounds were completed between the historical and current versions; none of them modified the manuscript.

1. **Evidence-axis closure (round 13).** Every route on SensorScope and U-Air is now measured: weight freedom, estimand selection, gate law, gate decision, exceedance decision. All negative. With the checkpoint fixed and only the *evaluation* weights changed, `RMSE_μ` differs from uniform weighting by 0.8208 % (SS) and 0.2660 % (UA) — an evaluation-layer figure that bounds nothing about training.
2. **Estimand selection (round 14).** Arrival-weighted validation misstates deployment risk by −4.11 % to −4.12 % (SS, all nine configurations) and +0.27 % to +0.62 % (UA), while selecting the identical configuration on 20/20 seeds of both datasets: a level shift, not a ranking change. Both datasets are labelled `saturated` (`d̄ = 0`, Wilson [0.000, 0.161]), so this round licenses nothing positive.
3. **Gate-dose v2 (round 15).** 246 runs, 200 dose cells. `gate_law = not supported`, H1 `null` on both datasets, H2 `not_tested`, `ρ*` unreported. The descriptive part is the interesting part: `r_Δc-s` tracks `ρ` with strictly negative intervals (−0.1331 SS, −0.3565 UA), so the statistic does predict the *calibration* cost while not predicting the *prediction* cost. The G3 tolerance was amended 1e-6 → 1e-5 under authorization, with the pre-amendment verdict preserved (`GATE_G3.json` `pass: false`, 37/40); the amendment is disclosed in the tree and not in the paper, which I do not charge.
4. **NSW-Traffic new block (round 16).** `S0` `go: true` (mean 12.06 clients per window, 6.69 % of windows at `≤ 2`). `S1` `go: false`, `failed: N3`: across `local_steps` 2/5/10/20 the ratios to the centralized model are 1.02962 / 1.02814 / 1.02780 / 1.02911, none inside `1.01c`, so the 2.8–3.0 % gap is not an optimisation-budget artefact. `S2` never ran.

## Top strengths

- The negative result is now *explained* rather than merely reported. The `K_r ≤ 3` argument is short, correct, and directly checkable against the frozen `window_metrics.json`; it converts "the prediction endpoint does not move" from an unexplained null into a consequence of the class the method defines.
- Three of the four new Limitations numbers reproduce exactly from their sources, including the U-Air dose-response bounding box (6.6385 %, 6.9947 %, 7.4565 % at `ρ` 0.466245, 0.418776, 0.354430) and the arrival-weighting ranges.
- The revision's honesty discipline holds: it prints bounds against its own method (masking is a cost, the new block is a `NO-GO` on its primary check) rather than selecting the flattering half.
- The mechanism and the projection figures are mutually consistent on the substance: Design moves `RMSE_μ` by several points on U-Air (6.885 %) by changing *which* windows are active, not by re-weighting within a window.

## Major concerns

**E1. Alignment is still not shown to buy accuracy — and the revision supplies the reason rather than the repair.** Severity: major, decisive. Evidence: L2096–L2101 and the ceiling; the new mechanism paragraph L2152–L2168; `results_gate_dose/round_v2/DOSE_DECISION.json` (`gate_law = not supported`, both H1 labels `null`); `results_regime_b_endpoints/round_v1/P2D_REPORT.md`. Affected: Evidence, Significance. Fix class: new evidence on a *different* setting with a concentrated target, pre-registered before the run. Owner: `ccf-experiment-designer`. Score-impact condition: a pre-registered endpoint whose headroom exceeds its detectable effect and whose alignment changes a prediction or a deployment decision. Nothing in this revision meets it, and the revision says so itself.

**E2. The program the method is named for is still not the part that moves the endpoint.** Severity: major for venue fit, not a correctness error. Evidence: L229–L237 and L1826–L1856, unchanged. The new text makes this more visible (the mechanism paragraph effectively concedes that (P2)'s objective cannot move the prediction endpoint when the constraint pins the weights) without changing the contribution ordering. Fix class: lead the contribution list with the projection and the Design factor; or find a setting where those terms move an endpoint. Owner: `ccf-paper-writer` for the statement; `ccf-experiment-designer` for a setting.

## Moderate concerns

**NEW-r13-1. The new paragraph contradicts the paper's own characterisation of its headline projection number.** L2160–L2162, "consistent with **the small margin** of the projection over uniform server weights on the group endpoint (`+0.768` and `+0.286` pp above)", sits two pages after L1834, which calls `+0.768` "above the `0.5` pp practical line and stable across the two seed halves", and after L2092, which reports it at `p_Holm = 2.7×10^{-5}`. The bundled source (`w1/tradeoff_v4/PART_A_REPORT.md` L15/L17) agrees with L1834. The argument the new sentence wants — that the constraint leaves the objective little freedom — does not require calling a practically significant effect small, and the sentence as written invites a reader to distrust one of the two statements. Two smaller precision defects sit in the same paragraph: L2207 prints a bound of `0.17 %` that the source crosses (largest SensorScope level mean `0.1747 %`), and L2213's "for every local budget from 2 to 20 steps" describes four measured budgets (2, 5, 10, 20), with the 2-step rung not trained in that round but read from the sealed E2 runner and flagged in `GATE_AMENDMENT_A1.md` §5 as not numerically interchangeable with the fresh rungs. Owner: `ccf-paper-writer`.

**NEW-r13-2. The revision's numbers are not deposited and not pointed at.** Both new blocks contain zero `\cite` commands and one `\eqref` each, so no in-text pointer reaches any artifact. A recursive search of the release bundle returns no file for any of the eight supporting trees, and `w1/PAPER_NUMBERS.csv` — which L2262 presents as "indexing the printed values" — contains none of the new values. This is the same class of gap M2 closed for round 12's numbers, recurring for round 13's. Owner: user for the deposit decision; `ccf-paper-writer` for the pointer.

**NEW-r13-3/-4. Independent of this revision, the release bundle does not reproduce the paper, and it ships stubs it tells the reader to run.** The divergence is not confined to figures. Three of nine `figure_data` files differ from their bundle counterparts, and for `FIG_E3_E3_PREDICTION_RISK.csv` (27 of 440 rows) the bundle's U-Air arm means round to `1.1911 / 1.1911 / 1.1882 / 1.2160 / 1.1914` — **no such digits occur anywhere in the manuscript**, which prints the worktree values `1.1954 / 1.1923 / 1.2202 / 1.1958`; the E4 ablation figure reaches the abstract's own `-6.885 / -7.221`, which the bundle stores as `-6.553 / -6.875`. Five bundle tables still carry the superseded `1.18824 / 1.19111 / 1.19112`, and the bundle's **own** `w1/audit_v5/round_v5_1/ERRATA_FOR_PAPER.md` documents the correction the bundle does not carry. Separately, `scripts/rebuild_table_ii.py` — which `README.md` L14/L96 instructs the reader to run — is a **2-byte** file inside the released bundle, as is `tdrive/TD_R_FREEZE.json`; three further shipped files have no worktree original. `verify.py` is a hash-only self-check against a manifest generated *after* copying, so stale content is hashed stale and passes: it prints `checked=2116 mismatches=0` and cannot detect any of this by construction. None of it is caused by this revision, so none of it is charged against the current version alone; all of it bears on the Reproducibility axis and on whether the artifact can support the paper's claims at all. Owner: user; `ccf-integrity-auditor` for the record.

**NEW-r13-5. Two deposited artefacts disagree about the mechanism paragraph's own statistic.** On U-Air Design-on the trace-derived `K_r ≤ 3` share is 77.389 % over the same 1 402 windows, against the runner-derived 90.157 % printed. The printed number is correct against `window_metrics.json` and not derivable from the released EventTraces. Owner: user; `ccf-experiment-designer` if the traces are to be the evidence of record.

## Writing and presentation concerns

- The new Limitations paragraph changes subject every sentence (arrival weighting → masking dose → NSW block), which is the same audit difficulty round 12 flagged for the previous paragraph; it is worse here because the three measurements come from three different rounds and no sentence says so.
- `+0.768` now appears twice on the same page in two senses of "margin"; `0.17` likewise appears as a bound here and as an MDE endpoint in the ceiling subsection — the same digits, two unrelated quantities (audit item EV-2).
- The mechanism paragraph's "so the weights are free" (L2210) rests on the `≤ 2`-client share of 6.69 %, which is not printed; the printed `12.1` does not by itself carry the inference, and no source prints `12.1` (the trace mean is 12.06, the run-side roll-up 12.08).
- The mechanism paragraph's premise `E_min = 3` is not recorded in any frozen E3 run configuration; it is recovered from source defaults, so a reader cannot verify the paragraph's premise from the released runs.

## Format and venue concerns

- **Page count is now 18 pp** (measured this round; round 12 inherited 17 pp). That is the project's MOPC ceiling exactly, with zero headroom, and it exceeds a 12 pp regular TMC article. The submission must declare its track. Not charged as a technical defect, but the next addition has no room.
- The tree's `main.pdf` is still the 17 pp, 2026-10-06 artefact; anyone reading, submitting or archiving from this directory today reads a document that does not contain the revision under review.
- Anonymity is not applicable to a journal revision.

## Claim–evidence audit

| Claim | Where | Evidence | Strength |
|---|---|---|---|
| Deployment and arrival risks are not interchangeable | Abstract; contribution 1 | Proof under differing laws; not re-derived this pass | Adequate, conditional on the proof |
| Ideal sequential correction recovers compatible target mass and does not prove risk optimization | Abstract; contribution 2 | Theorem with A1–A3 | Adequate as a scoped theorem |
| The remaining structural gain is the projection; other frozen terms stay inside the band | Abstract; contribution 4; L1826–L1856 | 20 paired seeds, bootstrap CIs, Holm, ±0.10 band; `+0.768`/`+0.286` traced to `w1/tradeoff_v4/PART_A_REPORT.md` L15/L17 | Strong, and the claim is the right size |
| Design on costs 6.885 % `RMSE_μ` and gains 4.990 % client–stratum mismatch on U-Air | Abstract; L1992–L1996 | Holm-significant ablation; note the printed `6.885 %` is the θ-rescored value, the frozen runs giving `6.553 %` under the endpoint-screen ruling | Adequate for that block; the vintage should be stated |
| No Holm-significant RMSE win | Table III caption; L2096–L2101 | The registered prediction family | Strong as a negative result |
| **The weights cannot move the prediction endpoint on these blocks** | **L2152–L2168 (new)** | **`E_min = 3` and `eq:Cr`; 1 475/1 877, 1 264/1 402, 1 197/1 515 windows with `K_r ≤ 3`; verified exactly from `window_metrics.json`** | **Strong, with the `E_min` provenance gap and the U-Air trace disagreement noted above** |
| **Arrival-weighted validation misstates risk without changing a selection** | **L2199–L2204 (new)** | **nine configurations per dataset; −4.11 %…−4.12 % (SS), +0.27 %…+0.62 % (UA); disagreement rate 0.0 on 20/20 seeds both datasets** | **Strong; the U-Air lower bound depends on the θ-scoring convention** |
| **Masking raises `ρ_r` from 0 to 0.388 without a prediction cost above 0.17 %** | **L2205–L2209 (new)** | **`MASKS.json` 176/440 = 40.00 %; `DOSE_SUMMARY.csv` level means; U-Air bounding box exact** | **Adequate; the `0.17 %` bound is crossed by its own source and the cost is not monotone in `ρ`** |
| **On NSW-Traffic the learner, not the weighting, limits the endpoint** | **L2210–L2215 (new)** | **`S0_FOLLOWUP.json`; `S1_LADDER.csv`; the four frozen members include the oracle-margin arm and agree to 0.0015 %** | **Adequate in direction; the same sources record S1 as `NO-GO (N3)` and S2 as `NOT RUN`, and the sentence's "every local budget from 2 to 20" covers four budgets** |
| Trained projection rules improve structure and not prediction | L2079–L2101 | 20 seeds; Holm on both endpoints | Adequate, correctly marked as new rules |
| City Scanner non-inferiority is untestable; deletion unresolved | L2184–L2190 | `A1_POWER.csv`, `C1_PRIMARY.json`; note the `mde80` column is a signed margin, not an MDE, so the recorded "decade" reading of EV-2 is not supported by it | Adequate as stated; the supporting column is mislabelled |
| ε_impl ≤ 2.42e-5 and its printed ratios | Appendix K | Consistent with `pp = Δ/2×100` | Adequate |

## Multi-reviewer panel

```text
Reviewer: Best-justified
Lens: strongest defensible accept case
Score / score tendency: 6/10
Confidence: high
Main positive signal: the paper now answers the question a sceptical reader actually asks about a
  measured null -- why can it not move here -- with an argument that is two lines of convexity and
  five verified counts; that is a more useful contribution than another borderline-positive table.
Main negative signal: a measurement paper still has to show the measurement changes a decision, and
  this round's own bounds are the reason it cannot.
Evidence basis: L2152-L2168; window_metrics.json counts; results_gate_dose/round_v2/DOSE_DECISION.json
Score-change condition: a concentrated-target block where the projection changes a decision.

Reviewer: Critical
Lens: strongest reject case
Score / score tendency: 4/10
Confidence: high
Main positive signal: the negative results are disclosed, and the new paragraph does not oversell
  them; the revision's arithmetic is clean.
Main negative signal: the named program is still not shown necessary, the prediction endpoint still
  does not move, the decision endpoint is saturated, the new block is a NO-GO on its own primary
  check, and the revision's own numbers are not in the released bundle while the text calls a
  Holm-significant +0.768 pp a "small margin".
Evidence basis: L229-237, L2160-L2162 vs L1834/L2092, L2213; RAVEN_MCS_PUBLIC_REPRO_R1 search
Score-change condition: the Evidence repair in E1; wording repairs alone will not move this reviewer,
  and this round's wording defects move it the other way.

Reviewer: Method / soundness
Lens: whether the causal sentences match the diagnostics
Score / score tendency: 6/10 on soundness; does not raise the paper's stance
Confidence: medium (proofs not re-derived) to high on the new paragraph
Main positive signal: the mechanism is a correct consequence of the constraint as written; the K_r
  counts, the max-mu shares and the group counts all verify exactly, and the design-removal count
  (1515 -> 1402 active U-Air windows) matches the claim.
Main negative signal: the E_min premise is not in any frozen E3 config, and two deposited artefacts
  disagree about K_r on the exact windows the printed 90.2 % uses.
Evidence basis: eq:Cr L883-L896; feasibility.py; methods.py defaults; window_metrics.json;
  REACHABILITY_WINDOWS.parquet
Score-change condition: a counterexample in the proof, or a resolved trace-versus-runner accounting.

Reviewer: Reproducibility auditor
Lens: can a reader rebuild the reported numbers from what the paper names
Score / score tendency: 2/5 on this dimension
Confidence: high
Main positive signal: the mechanism paragraph's numbers are all rebuildable from the frozen run
  records, and the round-12 w1/ pointer is still in place.
Main negative signal: the revision's ten new numbers are in none of the bundle's 2 118 files and in
  none of PAPER_NUMBERS.csv's 83 rows, while the bundle simultaneously lags the paper on 3 of 9
  figure files and three drivers are gone.
Evidence basis: L2199-L2215; recursive bundle search; w1/PAPER_NUMBERS.csv; verify.py; MANIFEST.csv
Score-change condition: deposit or name the estimand, gate-dose and traffic outputs, and add the rows
  to the index.

Reviewer: Writing and presentation
Lens: can a reviewer read each sentence once
Score / score tendency: 4/5 on clarity
Confidence: high
Main positive signal: the mechanism paragraph is well ordered (constraint -> counts -> target -> what
  actually moves the endpoint) and the new Limitations paragraph is short.
Main negative signal: "the small margin" contradicts L1834/L2092 about the same number, and the
  Limitations paragraph silently mixes three rounds.
Evidence basis: L2152-L2168, L2198-L2216, L1830-L1841, L2085-L2098
Score-change condition: re-word the margin sentence; name the rounds.

Panel synthesis:
Agreement: the mechanism argument is correct and its numbers verify; the revision is honest; the
  Evidence axis is not repaired.
Disagreement: whether explaining a null with a verified bound is progress for TMC. The sympathetic
  reviewer says the explanation is the contribution; the critical reviewer says the venue's decision
  quantity moved not at all, and the revision's own provenance and wording slips cost real ground.
Decisive accept axis: a concentrated-target block where the projection changes a measurable decision.
Decisive reject axis: Evidence, unchanged, now with the mechanical reason confirmed.
Unresolved evidence: the proofs (not re-derived); irreducibility versus FedPALS/FedIPW (not
  re-searched); the trace-versus-runner K_r accounting on U-Air Design-on.
Final calibrated stance: 5/10, borderline negative, maintained with a narrower margin.
```

## Concern-to-action table

| ID | Severity | Action | Owner | Stance effect |
|---|---|---|---|---|
| E1 | Major | Do not add seeds and do not re-run the saturated U-Air exceedance endpoint. A repair needs a *concentrated-target* block (T-Drive four-group, or a campaign with declared monitoring weights) with headroom stated before the run. | `ccf-experiment-designer` | The only action that can move 5→6 |
| E2 | Major | Lead the contribution list with the projection and the Design factor; keep (P2)'s other terms as the uniqueness device. | `ccf-paper-writer` | None by itself |
| NEW-r13-1 | Moderate | Re-word "the small margin" to match L1834/L2092; write `0.175 %` or a containing bound at L2207; scope L2213 to the four rungs run and state the inherited 2-step provenance. | `ccf-paper-writer` | Clarity 4→5 |
| NEW-r13-2 | Moderate | Deposit (or name) the estimand, gate-dose and traffic outputs in the bundle and add their rows to `w1/PAPER_NUMBERS.csv`. | user; `ccf-paper-writer` for the pointer | Reproducibility 2→3 |
| NEW-r13-3 | Moderate | Refresh the bundle against the worktree, reconcile `file_count`, and add a provenance column so `verify.py` can express "pre-ruling vintage". | user | Reproducibility |
| NEW-r13-4 | Moderate | Restore or formally withdraw the three lost drivers; if withdrawn, stop presenting `cityscanner/` and `cityscanner_p2/` as rebuildable. | user | Reproducibility |
| NEW-r13-5 | Minor | Reconcile the trace and runner `K_r` accounting for U-Air Design-on, or state which artefact is the evidence of record. | user; `ccf-experiment-designer` | Reproducibility, Soundness confidence |
| NEW-r12-3 | Minor | Fold "closable gap" and "closed by uniform weights" into one naming scheme. | `ccf-paper-writer` | None |
| Format | Minor | Rebuild and re-ship `main.pdf` (18 pp) and declare the track against the MOPC ceiling. | user | None |

## Recommended next CCFA owner

`ccf-paper-writer` for NEW-r13-1, the contribution ordering (E2) and NEW-r12-3 — all wording-level and none of them able to move the stance. The user owns the deposit and bundle decisions behind NEW-r13-2/-3/-4, which are the only items that can restore Reproducibility. `ccf-experiment-designer` owns E1, and only if a concentrated-target setting is actually proposed. `ccf-rebuttal-writer` owns the ledger handoff for the rows above and the record corrections recorded in `ccfa-review-reports/raven-mcs-integrity-audit.md` §4.3 and §4.5 (ledger Part VIII §VIII.3 staleness; items 54/55). This review does not update the ledger itself.

## Checks run

- Hash chain: the historical version does not exist as a file in this workspace, so it was reconstructed — the two new blocks were deleted from the current file and the result hashed to `02447BFE6256632B…`, 113 854 B, matching the hash the round-12 report named as the next comparison target. The current file is `68D9B44F17A4E48D…`, 116 379 B, mtime 2026-10-07 17:05. `snapshots/2026-10-06-pre-r12-fix/main.tex` is `59E4F4D5…`, i.e. the pre-round-12 text, so the working diff's other three hunks are round-12 edits already inside the historical version.
- Exact diff of the two versions: 2 hunks, +36 / −0 — L2152–L2168 (+17) and L2198–L2216 (+19). No other hunk.
- Build re-measured in fixed order, out-of-tree: `main.pdf` **18 pp**, 0 errors / 0 undefined / 0 multiply-defined / 0 Overfull; `supplemental.pdf` 16 pp with 1 Overfull `\vbox` (3.42152 pt).
- Every number in the mechanism paragraph re-derived from `artifacts/…/window_metrics.json` over seeds 30001–30020: 1 877 active SensorScope windows with 1 475 at `K_r ≤ 3` (78.5828 %); 1 402 U-Air Design-on with 1 264 (90.1569 %); 1 515 U-Air Design-off with 1 197 (79.0099 %). `max μ` recomputed from the frozen target bundles: 0.0052785924 over 220 groups and 0.0078616352 over 144 groups, `Σμ = 1.000000000000000`.
- `E_min = 3` and the `eq:Cr` argument verified from `src/raven_mcs/aggregation/feasibility.py` L15–21, the `e_min: float = 3.0` defaults in `methods.py`, `training/window_runner.py` L989, `e3/final_closure/core.py` L22 and `E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json` L16.
- `+0.768` / `+0.286` traced to the bundled `RAVEN_MCS_PUBLIC_REPRO_R1/w1/tradeoff_v4/PART_A_REPORT.md` L15/L17, with intervals; `pp_group = 50 × d_group` verified exactly on `FULL_SEED_LADDER.csv`.
- Estimand and gate-dose claims re-derived: nine configurations per dataset with `disagreement_rate = 0.0` on both; `176/440 = 40.00 %` masked at `m = 0.40`; `ρ = 0.388138`; `DOSE_DECISION.json` labels `gate_law = not supported`, H1 `null` on both datasets, `H2 tested: false`.
- NSW claims re-derived: `S1_LADDER.csv` `ratio_to_c` gives 2.9619 / 2.8140 / 2.7801 / 2.9109 % at `ls = 2/5/10/20`; `S1_VERDICT.json` `go: false, failed: "N3"`; `MANIFEST.sha256` `S2 = "NOT RUN (S1 NO-GO)"`.
- Release-bundle check: recursive name search for every supporting tree returned zero files; `w1/PAPER_NUMBERS.csv` has 83 rows and zero of the new values; `verify.py` is a hash-only self-check against a `path,bytes,sha256` manifest.
- Machine check: `CCFA-Skills/ccf-paper-reviewer/scripts/validate_version_comparison.py _r13_build/r13_contract.json` → **PASS: version comparison is internally consistent** (weights sum to 1; deltas equal current − historical; weighted delta −0.25 recomputed from the frozen weights; provenance values valid; both decreases traced to `revision_regression` issues with negative current effects).

## Unresolved or unverified

- Proofs in §VI were not re-derived; Soundness is scored on the claims read and the new paragraph's argument, not on the proofs.
- FedPALS and FedIPW were not re-searched; Related work carries the previous pass's uncertainty.
- The trace-versus-runner `K_r` disagreement on U-Air Design-on is established as a fact but not explained; I did not determine which artefact is intended to be canonical.
- The full bundle sweep is complete: 2 118 files, 2 099 byte-identical to a worktree twin, 19 with none, and the three figure files plus five tables differing from what the manuscript prints. The sweep also found that `MANIFEST.csv` carries no source or provenance column, so bundle↔worktree provenance rests on basename/size/hash matching and on reading the (itself non-shipped) build script; that is closed for `w1/` (unique twins) but structurally open elsewhere. A table-numbering conflict is likewise unresolved: L2252–L2253 and the bundle README call `TABLE_II_MAIN_EFFECTIVENESS.csv` "canonical Table II" while `C3_CELL_DIFF.csv` labels the same manuscript table "Table III (UA)".
- Ledger records remain stale and partly wrong (Part VIII §VIII.3; items 54/55). Those are project-record defects, not manuscript defects, and are reported in the integrity audit rather than scored here.

## Confidence and comparability

Separate from both scorecards. Comparability is **high**: the two versions are exact byte-verified texts on the same manuscript line, scored under the same frozen contract, the same five roles and the same evidence standard, with no external standard change; the diff is two insertion-only hunks and was read in full. Confidence in the relative-progress scorecard is **high** on Evidence, Clarity and Reproducibility, where the changed sites were read in full and every printed number in them was traced to a named artifact, and **medium** on Soundness and Originality, where the proofs were not re-derived and no literature search was run. Confidence in the absolute-readiness scorecard is **medium**, inherited on the axes this revision did not touch and raised on one specific question — that the mechanism, not the weights, bounds the prediction endpoint on these blocks, which is now measured three ways and verified independently. The two judgment calls behind the negative deltas are each disclosed with their alternative outcome, and the `regressed` classification survives both.

## Output self-check

- Section order follows the version-comparison contract, with the two scorecards kept separate and confidence reported as a third field.
- Every score of 3 or below carries a deduction, a repair condition and an expected movement.
- Both score decreases are traced to a `revision_regression` issue with a negative current effect, current-version evidence and an affected dimension; the four `previously_undetected` issues carry explicit zero effects so they cannot be used against only the current version.
- The progress classification (`regressed`, −0.25) is not fused with the readiness stance (5/10), and the readiness fall (3.55 → 3.30) is disclosed alongside the reason the stance held.
- No prose was rewritten, no ledger was updated, no acceptance probability is claimed.
- Tables use consistent column counts; no placeholder remains.

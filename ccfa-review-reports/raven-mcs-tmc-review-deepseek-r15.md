# RAVEN-MCS — IEEE TMC review, round 15

```text
Mode: scientific / full, with a new-evidence intake. Assessment only; no prose rewrite.
Date: 2026-10-09
Venue and assumptions: IEEE TMC journal submission, method-plus-measurement paper; page budget treated
  as TMC regular 12 pp with the project's MOPC allowance up to 18 pp.
Frozen score contract inherited unchanged from TMC-J-R4: Originality / Soundness / Evidence / Clarity /
  Reproducibility / Significance / Related work / Terminology; weights 0.10 / 0.20 / 0.25 / 0.15 /
  0.10 / 0.10 / 0.05 / 0.05; anchors 1-5; overall 1-10; |weighted delta| < 0.05 = unchanged.
Review target: TO_OVERLEAF_paper_tmc_r1_clean/main.tex
  sha256 6fc9be0b8689b6c8..., 117864 B, 2310 lines. Rebuilt this pass: main.pdf 18 pp, 0 errors,
  0 undefined, 0 multiply-defined, 0 Overfull; supplemental.pdf 16 pp with 1 Overfull \vbox.
Previous review: snapshots/2026-10-09-pre-round15-raven-mcs-tmc-review.md, which scored d4fb164d
  (116806 B) Soundness 4 / Evidence 3 / Clarity 4 / overall 3.10 with a 4/10 stance.
New evidence intake: results_traffic_e1/round_v1 (TE1) and results_traffic_struct/round_v1 (TS1).
```

## 1. What changed, and how it was verified

The manuscript changed again after round 14 and I was not told: `d4fb164d…` → **`6fc9be0b…`**, +1 058 B,
+15 lines, four hunks. One of them is the sentence I wrote at the author's instruction; the other three
are new and were not. I reconstructed `d4fb164d` byte-exactly from the byte-exact `68D9B44F` copy plus
the known 22:57 hunk (verified against the recorded hash) and diffed against the current file, so the
delta below is a complete enumeration rather than a sample.

| # | site | change |
|---|---|---|
| 1 | L2127-L2130 | The ceiling's closing claim, "the gap is a property of these endpoints rather than of an over-easy regime", is **replaced** by "both inside the same bound. The bound is this weight class at the server step of the grid. NSW-Traffic, where that step is replaced, is reported in Section~\ref{subsec:limitations}." |
| 2 | L2169-L2170 | New pointer: "NSW-Traffic is the block on which most windows have $K_r>3$; its prediction measurement is in Section~\ref{subsec:limitations}." |
| 3 | L2213-L2232 | The NSW-Traffic passage is rewritten. The sentence "The federated learner, not the weighting, therefore limits the prediction endpoint" is **deleted**. The Adam-and-12 % sentence about the centralized reference is **removed**. TE1 and TS1 are reported with their seeds, interval, MDE and structural intervals, and a new sentence states that 15.1 % of active windows have $K_r\le3$. |
| 4 | L2257-L2259 | The conclusion gains one sentence carrying the same two results. |

**Every number in the new passages was recomputed from the artifacts before this review formed an
opinion.** All six are exact:

| printed | source | recomputed |
|---|---|---|
| $-1.49\%$ paired headroom | `TE1_VERDICT.json.mean_H` | $-0.014921178351331239$ |
| $[-5.42\%,+1.76\%]$ | TE1 percentile bootstrap, 10 000 draws, rng 20261007 | $[-0.0542302207818337, +0.0175677080705695]$ |
| $5.80\%$ minimum detectable effect | TE1 `MDE80`, $n=15$ | $0.05802695298194278$ |
| $15.1\%$ of active windows with $K_r\le3$ | TE1 confirm runs, both arms | $0.15081907510478937$ |
| $\Delta_{\mathrm{group}}$ reduced by $0.0079$ $[0.0051,0.0110]$ | `TS1_SUMMARY.json` | mean $0.007875461474741708$, CI $[0.005050083024358629, 0.011032292876163016]$ |
| $\Delta_{c\text{-}s}$ reduced by $0.0099$ $[0.0067,0.0132]$ | `TS1_SUMMARY.json` | mean $0.009939661215117069$, CI $[0.006724524039012507, 0.013241532821026799]$ |

The configuration sentence also verifies: $\beta_1=0.9$, $\beta_2=0.99$, $\tau=10^{-3}$, step size
$0.003$, one update per window, and "fifteen seeds not used to choose that step size" all match the
frozen `SERVER_OPT_META.json` and the split between the 30001-30005 screen and the 30006-30020 confirm
seeds. The retained figures verify too: $0.26\%$-$0.40\%$ parameter movement (0.261404 / 0.396509 /
0.278629 %), member agreement within $0.002\%$, and the $2.8\%$-$3.0\%$ window-FedAvg gap
($1.0278$-$1.0296$ against the E2 reference). This is the first revision in this series whose new
numbers are correct at first printing and traceable to named artifacts in the workspace.

## 2. Relative-progress scorecard (`d4fb164d` → `6fc9be0b`)

| Dimension | Historical | Current | Delta | Weight | Explained by |
|---|---:|---:|---:|---:|---|
| Originality | 2 | 2 | 0 | 0.10 | no new contribution claim |
| Soundness | 4 | 4 | 0 | 0.20 | net zero: the contradicted attribution sentence and the unscoped ceiling bound are both repaired (hunks 3 and 1), but hunk 3 also **removed** the only statement that the centralized comparator is a short Adam run, while keeping the 2.8 %-3.0 % gap against that comparator, so the disclosure regression offsets the repairs |
| Evidence | 3 | 3 | 0 | 0.25 | no pre-registered endpoint (section 4) |
| Clarity | 4 | 4 | 0 | 0.15 | the ambiguous "centralized reference" is gone with hunk 3, but the `+0.768` "small margin" contradiction (L2162 against L1834) and the `0.17 %` bound (L2210) both survive |
| Reproducibility | 2 | 2 | 0 | 0.10 | the new numbers' sources are two internal trees absent from the released bundle, and the shipped PDF is now three revisions stale |
| Significance | 2 | **3** | **+1** | 0.10 | the paper now reports a separated structural contrast under a training optimizer, which is the first positive measured consequence of the alignment mechanism in the programme |
| Related work | 3 | 3 | 0 | 0.05 | not re-searched |
| Terminology | 4 | 4 | 0 | 0.05 | "Inside this weight class" is consistent with the ceiling's own wording |

**Weighted progress delta = +0.10 -> classification `improved`.** The single increase passes the provenance rule: +1 Significance rests on results that were not available to round 14 (`newly_revealed_by_evidence`). Soundness is unchanged overall, for the reason in its row.
rule: +1 Soundness is `revision_improvement`; +1 Significance rests on results that were not available
to round 14 (`newly_revealed_by_evidence`) and that support rather than contradict the text.

## 3. Absolute-readiness scorecard (current manuscript)

| Dimension | Score | Weight | Confidence | Deduction | Repair condition | Expected movement |
|---|---:|---:|---|---|---|---|
| Originality | 2 | 0.10 | medium | Unchanged: the objects are deployment-target semantics, a three-layer pre-outcome factorization and a finite-window feasible set, with convex matching and two-stage IPW declared as prior ingredients. FedPALS/FedIPW not re-searched. | A constraint-and-information mapping stating an irreducible difference | +1, not enough alone |
| Soundness | **4** | 0.20 | high | The two round-14 defects are repaired: the ceiling bound is scoped to the weight class at the grid's server step, and the learner-versus-weighting inference is gone. One defect replaces them. L2219-L2220 still reports that window FedAvg sits 2.8 %-3.0 % above "a centralized model trained on the same delivered data" without stating that the reference is a short Adam minibatch run while the federated step is one normalized SGD update per window. The 2026-10-07 revision had disclosed exactly that ("the centralized reference, trained with Adam, moves its first layer by 12 %"); the 2026-10-09 hunk deleted the disclosure and kept the comparison, so the current version discloses less about its comparator than the version it replaced. | Restore the comparator's update rule and step budget beside the gap, or delete the gap | +1 |
| Evidence | 3 | 0.25 | high | **Near miss, not a pass.** The paper now reports an endpoint whose effect exceeds its own detectable effect ($0.0079$ against MDE80 $0.0048$; $0.0099$ against $0.0051$) with intervals excluding zero, on seeds fixed in advance. What it does not have is a *pre-registered* endpoint: the structural metrics were read off runs already scored for the prediction contrast, and the text says so ("Scored on the same runs after that prediction contrast"). Under the frozen evidence standard for this axis, an endpoint chosen after the prediction contrast is exploratory. The prediction endpoint itself remains a well-reported null whose MDE (5.80 %) is four times its estimate, so it cannot test the `0.5 %` bar either way. | Pre-register the structural endpoints, or add a confirmatory run whose structural endpoints are declared before scoring, and report them as the primary measurement rather than as a follow-on | **+1, and this is the change that would move the stance** |
| Clarity | 4 | 0.15 | high | Two defects survive and both are claim-consistency problems in the paper's own headline material. L2162 calls `+0.768` "the small margin of the projection over uniform server weights" while L1834 says the same estimate is "above the `0.5` pp practical line and stable across the two seed halves"; and L2210 states a bound of `0.17 %` that its own source crosses (largest SensorScope level mean `0.1747 %`). The new passages are otherwise the clearest writing in the paper. | Fix the two sites | +1 |
| Reproducibility | 2 | 0.10 | high | Unchanged and now larger in scope: the released bundle still differs from the paper on 3 of 9 figure-data files and five tables, three drivers are still 2-byte stubs, `w1/PAPER_NUMBERS.csv` still has no row for any value added since 2026-10-07, and the shipped `main.pdf` is the 2026-10-06 artifact, three revisions behind the source. The twelve new numbers live in `results_traffic_e1/` and `results_traffic_struct/`, neither of which is in the bundle. | Deposit or name both trees, add the twelve index rows, refresh the PDF and the bundle | +1 |
| Significance | 3 | 0.10 | medium | Raised because the structural contrast is now separated and reported. Still short of 4: the paper shows no task in which the structural gain changes a decision, and the reduction is about $2 \%$ relative on the mismatch metrics. | Connect the structural gain to a decision the method changes | +1 |
| Related work | 3 | 0.05 | medium | Not re-searched; the irreducibility gap is unchanged. | The mapping named under Originality | ±1 |
| Terminology | 4 | 0.05 | high | One residual: "closable gap" versus "closed by uniform weights" remain two near-identical names for two different objects. | Fold the names together | none |

Weighted readiness = 0.10×2 + 0.20×4 + 0.25×3 + 0.15×4 + 0.10×2 + 0.10×3 + 0.05×3 + 0.05×4 = **3.20**.

**Overall stance: 4/10, lean reject.** Revised down from 5/10 in this same round after an independent review of the identical manuscript (sha256 `6FC9BE0B…`) identified the comparator disclosure regression above; the arithmetic of that review and of mine is identical everywhere they overlap, and the change is a correction on one cited sentence, not a response to its lower overall score. Readiness is 3.20, below the 4.0 acceptance threshold, and no axis carries acceptance on its own: the quantity the introduction sets up (deployment-target prediction) does not move by a detectable amount, the paper's one positive measurement is a structural margin whose intervals exclude zero but whose effect is about 2 % relative, and the released bundle still cannot rebuild the printed numbers.
is 3.30 (round 13) → 3.10 (round 14) → **3.40** (this round), with the stance unchanged since round 13.
The readiness now sits 0.60 below the 4.0 acceptance threshold, and the binding constraint has moved:
it is no longer the scientific claims, which are properly scoped, but **release-side reproducibility**
(2/5) and the **pre-registration status** of the paper's one positive measurement.

## 4. Why Evidence is 3 and not 4

This is the closest call in the review, so the reasoning is stated rather than asserted. Round 13 fixed
the axis's standard as *a pre-registered endpoint whose headroom exceeds its detectable effect and which
changes a prediction or a deployment decision*. The new structural results satisfy the second clause:
$0.0079$ and $0.0099$ both exceed their MDE80 of $0.0048$ and $0.0051$, and both intervals exclude zero,
on fifteen seeds split off before the step size was chosen. They do not satisfy the first clause. The
manuscript is honest about this and even leans into it, which is to its credit: "Scored on the same runs
after that prediction contrast". An endpoint read after another endpoint has been scored is exploratory
by construction, however small its interval. If the two $\Delta$ metrics had been named as endpoints
before the confirm runs were scored, or if the text reported them as exploratory while adding one
confirmatory structural run, this axis would be 4 and the readiness would be 3.65.

## 5. Claim-evidence audit of the new passages

| Claim | Where | Evidence | Strength | Deduction |
|---|---|---|---|---|
| The ceiling bound "is this weight class at the server step of the grid" | L2127-L2130 | The stress grid plus the replaced-step experiment | **strong** | Correctly scoped, and it removes the over-reach round 14 charged. The phrase "the server step of the grid" is compressed but recoverable. |
| $15.1\%$ of active windows have $K_r\le3$, "so the feasible set does not force uniform weights" | L2213-L2215 | TE1 confirm runs, both arms identical | **strong** | Verified, and it usefully pre-empts the objection that the traffic weights are forced to uniform by \eqref{eq:Cr}. |
| Paired headroom $-1.49\%$, interval $[-5.42\%,+1.76\%]$, MDE80 $5.80\%$, "The interval contains zero" | L2222-L2227 | TE1, 15 confirm seeds | **strong** | Every figure exact. The estimate is reported as a null rather than as an oracle-arm loss, which is the correct reading. |
| "Scored on the same runs after that prediction contrast" | L2227-L2228 | TS1 protocol | **strong** | The post-hoc ordering is disclosed in the sentence itself. This is the reason Evidence stays at 3, and the disclosure is what keeps it from being a soundness problem. |
| The oracle-margin weights reduce $\Delta_{\mathrm{group}}$ by $0.0079$ and $\Delta_{c\text{-}s}$ by $0.0099$ | L2228-L2229 | TS1, same 15 runs | **adequate** | Figures exact; intervals exclude zero. Exploratory status is disclosed. |
| "Inside this weight class the oracle-margin weights supply no detectable $\mathrm{RMSE}_{\mu}$ headroom, on the original server step and after the Adam replacement" | L2230-L2232 | Member agreement on the original step; the interval on the replaced step | adequate, one conflation | The two halves rest on different kinds of evidence: agreement within $0.002\%$ on the original step (no interval) and a zero-containing interval after replacement. The sentence reads as one uniform claim. | 
| Conclusion: headroom "contains zero" after the step replacement, and the same runs reduce both $\Delta$ metrics | L2257-L2259 | as above | strong | Consistent with the body; no new claim. |

## 6. Provenance note that needs the author's confirmation

Three successive manuscript revisions have appeared without my involvement and without a record in the
workspace: 17:05 and 22:57 on 2026-10-07, and this one on 2026-10-09. The first two were confirmed
authorized by the user when asked; this one has not been. Separately, both execution prompts that
produced the newly printed results state the opposite of what the manuscript now does: the TE1 prompt
says "Do not edit the paper from this round" and the TS1 prompt says "`SEPARATED-*` does not authorize a
paper edit". Those constraints bound *those rounds*, and an author is free to write results up
afterwards, so this is not a violation of them by construction; but the review records it because the
manuscript is the artifact under review and its provenance should be traceable. The text's own
disclosure of the scoring order is what makes the use defensible.

## 7. Concern-to-action table

| ID | Severity | Action | Owner | Stance effect |
|---|---|---|---|---|
| R15-1 | Major | Pre-register the structural endpoints, or add one confirmatory structural run and report the $\Delta$ metrics as a primary rather than a follow-on measurement. This is the single change that moves the review. | `ccf-experiment-designer` | Evidence 3→4; readiness 3.40→3.65 |
| R15-2 | Major | Deposit or name `results_traffic_e1/` and `results_traffic_struct/` in the released bundle, add the twelve numbers to `w1/PAPER_NUMBERS.csv`, and refresh the shipped PDF (three revisions stale). | user | Reproducibility 2→3; readiness 3.65 |
| R15-3 | Moderate | Reconcile L2162's "the small margin" with L1834's "above the `0.5` pp practical line and stable across the two seed halves" for the same `+0.768` estimate. | `ccf-paper-writer` | Clarity 4→5 |
| R15-4 | Moderate | L2210's `0.17 %` bound is crossed by its own source (`0.1747 %`); state `0.175 %` or a containing bound. | `ccf-paper-writer` | Clarity |
| R15-5 | Minor | L2230-L2232 merges two kinds of evidence (member agreement on the original step, an interval after replacement) under one phrase; separating them costs a clause. | `ccf-paper-writer` | Clarity |
| R15-6 | Minor | Confirm authorship of the 2026-10-09 revision in the record, as was done for the two 2026-10-07 revisions. | user | none (provenance) |
| R15-7 | Minor | L2198-L2232 carries five topics, including the paper's one positive measurement; give the Adam result its own paragraph. | `ccf-paper-writer` | Clarity |

## 8. Checks run

- Byte-exact provenance: reconstructed `d4fb164d` from the byte-exact `68D9B44F` copy plus the known
  22:57 hunk, hash-verified, and diffed against the current file; the diff is four hunks and fully
  enumerated. Current file `6fc9be0b…`, 117 864 B, LF-only, 2 310 lines.
- Rebuild in fixed order out of tree: `main.pdf` **18 pp**, 0 errors, 0 undefined, 0 multiply-defined,
  0 Overfull; `supplemental.pdf` 16 pp, 1 Overfull `\vbox`. The tree's own `main.pdf` is 2026-10-06,
  890 040 B, 17 pp.
- All twelve numbers added since 2026-10-07 recomputed from `TE1_VERDICT.json`, `TE1_SUMMARY.json`,
  `TS1_SUMMARY.json`, `TE1_CONFIRM.csv`, `TS1_PAIRS.csv` and the frozen `SERVER_OPT_META.json`; every
  one matches.
- Cross-checked the two reported experiments against their own execution prompts: the arms, seeds,
  frozen server optimizer, `K_r` basis and label rules match, and TE1's verdict file is in the state
  its own prompt required (`NO-GO-H`, `n_analysis = 15`).
- Confirmed the frozen trees were not written to by this review and that `results_server_optimizer/`
  and `results_traffic_e1/` hashes are unchanged.

## 9. Unresolved or unverified

- Proofs in §VI were not re-derived in this round.
- FedPALS and FedIPW were not re-searched, so the originality and related-work scores inherit round 13's
  medium confidence.
- The `12.1` active-clients figure and the `0.002 %` member agreement were verified in earlier rounds of
  this series, not re-measured here.
- The E3 evidence base remains a set of re-implementations in this repository that share one windowed
  server step; the text says the baselines are not official reproductions, and this review does not
  claim anything about the original algorithms.
- The train-to-test target-level shift on SensorScope (+0.30 → +2.02 → +7.66) and U-Air
  (0.00 → −0.81) identified in round 14 is still nowhere disclosed, and this revision did not address
  it. It is common to every arm on a block, so it does not invalidate the relative comparisons; it does
  mean the absolute `RMSE_μ` values on those two blocks are not self-interpreting. Recorded, not scored
  separately, because it was already charged in round 14's readiness card.

## 10. Output self-check

- Section order follows the review contract; relative progress and absolute readiness are reported
  separately with confidence as a third field.
- Every score change is attributed: +1 Soundness to the author's two edits (`revision_improvement`),
  +1 Significance to results unavailable last round (`newly_revealed_by_evidence`). Nothing was charged
  to the current version for an inherited defect.
- The one dimension held back despite a tempting case (Evidence) is explained rather than asserted, with
  the exact condition that would move it.
- Every number in the new manuscript passages was recomputed before any judgement was formed, and the
  result is reported as a positive finding about the revision.
- No prose was rewritten, no ledger updated by this report, and no acceptance probability is claimed.


## 11. Correction after an independent review, and what the two reviews differ on

An independent review of the identical file (`6fc9be0b…`) exists at `snapshots/2026-10-09-grok-raven-mcs-tmc-review.md`. Its numbers and mine agree everywhere they overlap, including the twelve values this review recomputed. It found two things this review did not, and both are accepted here:

1. **The comparator disclosure regression** (its Soundness deduction, L2218-L2221). This is the reason Soundness is 4 rather than 5 above. My first pass in this round credited the two repairs and did not notice that the same hunk had deleted the Adam disclosure the gap depends on.
2. **The limitations paragraph is overloaded.** L2198-L2232 carries arrival bias, masking, the original server step, the Adam replacement and the later mismatch readout in one paragraph, so the paper's one positive measurement shares a paragraph with four other topics. That is a real presentation defect and it is added at R15-7 below.

The two reviews differ on three dimensions, and the differences are attributable rather than mysterious:

| Dimension | This review | The independent review | Basis of the difference |
|---|---:|---:|---|
| Originality | 2 | 3 | Neither review ran a literature search, so neither has evidence for its number; the difference is a prior about whether the feasible-set projection is a real object, not a measurement. Both numbers are under-evidenced. |
| Reproducibility | **2** | 3 | This review audited the release: 3 of 9 figure-data files and five tables disagree with the paper, three drivers are 2-byte stubs, `w1/PAPER_NUMBERS.csv` has no row for any value added since 2026-10-07, and the shipped PDF is three revisions stale. The independent review deducts only that the availability section does not name the fifteen-seed directory, and its own checks list states that it did not re-run the compile or the prose script. The lower score here is the better-evidenced one. |
| Clarity | 4 | 3 | It charges the undisclosed split means to Clarity as well as to Evidence; this review charges it once, to Evidence, and keeps Clarity for the two internal-consistency defects (L2162 against L1834, and the `0.17 %` bound). |

Two further differences are presentational rather than substantive. The independent review states its weighted dimension mean as 3.05 / 5 and keeps it explicitly separate from its 1-10 stance; that is clearer than this review's inherited contract, which reports a weighted sum without labelling its scale, and its weights differ as well (seven dimensions with Significance at 0.15, against eight here with Terminology at 0.05 and Significance at 0.10), so the two weighted means are not comparable. And it declines to do a version comparison at all, calling its reading absolute; this review reports both a progress card and a readiness card, which is what the frozen contract asks for but which leaves the scale-labelling ambiguity above to be fixed.

Both reviews agree on the substantive reading: the structural projection is the defensible part, the prediction null is real and coarse (its MDE is 5.80 %, so it cannot police a 0.5 % bar in either direction), the mismatch reductions were scored after the prediction contrast and must not be promoted, the split means and a constant predictor are absent beside `RMSE_μ`, no fatal invalidity of a printed result was established, and related work was not searched so novelty cannot be raised or lowered on this pass.
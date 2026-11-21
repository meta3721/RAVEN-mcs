# RAVEN-MCS — response to the round-12 review, and the revision it produced

```text
Mode: response-letter (journal revision summary), with the revision ledger handed to the record.
Venue and constraints: IEEE TMC journal revision. No word budget applies; the manuscript page budget is
  the binding constraint (17 pp held after this pass, against the 18 pp MOPC allowance).
Review answered: ccfa-review-reports/raven-mcs-tmc-review.md (round 12, version-comparison mode,
  contract TMC-J-R4, historical main.tex 88ecd743321e38e9, reviewed current 59e4f4d5cffff4ff).
Manuscript after this revision: main.tex sha256 02447bfe6256632b..., 113854 B, 3 hunks, +9 / -1 lines.
  Snapshot before the edits: snapshots/2026-10-06-pre-r12-fix/.
  Build: main.pdf 17 pp, 0 errors, 0 undefined, 0 multiply-defined, 0 overfull; supplemental.pdf 16 pp
  with the one pre-existing overfull box unchanged.
No new experiments were run, no bibliography entry was changed, and no number in the paper moved.
```

## Issue table

| ID | Reviewer concern | Type | Severity | Decision relevance | Evidence available | Promised change | Risk |
|---|---|---|---|---|---|---|---|
| R5-16 | "recoverable" named two quantities | terminology | moderate | low | two sites in the text | **done before this pass** (r11) | none |
| M3 | privacy sentence carried the wrong antecedent | clarity | minor | none | L2172–2176 | **done before this pass** (r11) | none |
| A-8 | feasibility range mislabelled two arms' tokens | clarity | moderate | low | round-10 record work | **done before this pass** (r11, by deletion) | the magnitude is no longer printed; the qualitative claim stays |
| M2 | availability paragraph does not name the artifacts behind the new numbers | reproducibility | moderate | medium | `w1/` tree, `verify.py` clean | **done this pass**: the paragraph now names `w1/`, `w1/PAPER_NUMBERS.csv` and `verify.py` | none |
| M4 | the band's rule is on the page, its provenance is not | clarity, reproducibility | moderate | medium | `w1/ladder_v3/PREREG.md` states both | **done this pass**: the band subsection cites that preregistration | the pointer names a file inside the released bundle, which is the artifact a reader can open |
| CL-3 | contribution 3 carried the theorem, the verdict, the κ exclusion and a table pointer in one bullet | clarity | moderate | medium | L215–237 | **done this pass**: the verdict, the κ exclusion and the prediction pointer move to their own bullet under a heading | one more bullet in the contributions list; no claim changed |
| NEW-r12-3 | "closable gap" versus "closed by uniform weights" | terminology | minor | none | L606–609, L1819, L2194 | deferred; the round-12 review did not charge it | named in the ledger rather than silently left |
| E1 | alignment is not shown to buy accuracy, and the previously suggested decision endpoint is saturated | evidence | major | decisive | L2096–2101; `results_regime_b_endpoints/round_v1/P2D_REPORT.md` | no manuscript change is possible; a new setting with non-saturated decision headroom is required | this is the axis that holds the stance at 5/10 |
| E2 | the named calibration program is not the part that moves the endpoint | significance, originality | major | high | L229–237, L1826–1856 | not addressed by prose; needs either a setting or a lead-contribution rewrite | the split bullet makes the verdict more visible but is not the E2 repair |
| NEW-r12-1 | the decision endpoint is saturated on U-Air for both regimes | evidence (constraint) | major | decisive | `tables/P2D_CONTRASTS.csv` | recorded as a boundary on E1's repair path | prevents a repeat of the same unsuccessful instrument |
| NEW-r12-2 | supplemental build keeps one overfull box | reproducibility | minor | low | `supplemental.log` | not addressed; no supplemental edit was made this pass | none |

## Response strategy

The review's own classification was `improved` (+0.05, Terminology) with the stance held at 5/10, and its blocking axis is Evidence. The response therefore does not argue about the score. It separates the two kinds of item the review produced:

1. **Auditability items** (M2, M4, the contribution-3 split). These are the revision's content. Each is now a sentence or a bullet boundary in the manuscript, at a named location, sourced from an artifact a reader can open in the released bundle. None of them changes a claim, a number, or a table.
2. **Evidence items** (E1, E2, NEW-r12-1). These are not answerable with prose, and the response says so. The round-12 review narrowed E1's repair condition by measuring the very endpoint the round-9 pass proposed: on the paper's own U-Air checkpoints the exceedance-decision endpoint retains 0.00–2.48 % of the exceedance mass in the wider-support regime against 17.5–33.9 % in the narrow one, and no threshold in {25, 35, 50, 75} µg/m³ separates them on decision skill. The paper never claimed that skill — it says the deployment decision is "reported rather than made by the method" — so nothing on the page is contradicted, and nothing on the page can be strengthened by re-running that endpoint.

## Promised paper changes, and where they landed

| Change | Location | Status |
|---|---|---|
| Name the subtree that carries the ladder, band and ε_impl numbers | Data and Code Availability, last sentence of the first paragraph | done |
| Cite the preregistration that fixed the band and its reading rule | §"Structural Alignment Objective", end of the band paragraph | done |
| Give the attribution verdict its own contribution bullet | Contributions list, new `\item` before "Target debt is an accounting recursion…" | done |

Diff summary: 3 hunks, +9 / −1 lines, +63 source words; no digit in the manuscript changed; `main.pdf` held at 17 pp.

## Claims and promises to avoid

- Do not claim that this revision improves any score. The reviewer owns the scores; the next round decides.
- Do not claim that the availability sentence makes the bundle complete. `w1/PAPER_NUMBERS.csv` is named as an index of printed values, and the record still carries open items about two of its rows.
- Do not claim that `verify.py` validates the science. It re-checks payload files against a manifest, which is a hash check, not a reproduction of the experiments.
- Do not offer the U-Air exceedance endpoint as the E1 repair again, and do not offer more seeds on the existing blocks.

## Revision ledger

The canonical ledger is updated in place: `ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md`, **Part VII — Round-12 revision ledger**. It carries the twelve-column rows for the ten items above, with `status`, `origin`, `applies_to`, affected dimension, location, evidence and remaining risk.

## Resubmission adaptation notes

None. This pass is a same-venue revision, not a resubmission; no venue constraint changed, and no new experiment or bibliography change was introduced.

## Next CCFA owner

- `ccf-paper-reviewer` — when the next comparison round runs, against `main.tex` `02447bfe…` as the new current version; its own check list will decide whether Reproducibility moves (M2 and M4 were its two conditions).
- `ccf-paper-writer` — only for E2's lead-contribution rewrite, if the authors choose that route over a new setting, and for NEW-r12-3 if a reader test shows the two gap names confuse.
- `ccf-experiment-designer` — E1, and only with a setting whose decision quantity is not saturated.

## Checklist status

```text
Checklist status:
- Constraints: journal revision; page budget 17 of 18 pp held; no word or deadline limit supplied
- Issue grouping: auditability items (M2, M4, CL-3) versus evidence items (E1, E2, NEW-r12-1)
- Positive opening: the response states the review's own classification and does not contest it
- Quote/direct answer: each row quotes the shortest phrase that identifies the issue, then answers directly
- Deeper intent: E1's deeper intent (a venue-relevant quantity that moves) is answered as a measurement
  result, not as an argument
- Evidence support: every done item names a file that exists in the released bundle; every promise names
  a manuscript location
- Promise safety: no experiment, citation or result is promised; the two evidence items are stated as
  open with the reason
- Reviewer colors: not applicable (single review, no multi-reviewer TeX response requested)
- Tone: factual, non-defensive, no rhetoric
- Word budget: not applicable
- Remaining risks: E1 and E2 remain open and carry the stance; the supplemental overfull box remains;
  NEW-r12-3 is deferred and recorded
```

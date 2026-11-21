# RAVEN-MCS honesty text repairs (execution prompt)

`ccf-paper-writer`, mode `polish`. Four bounded text edits. No manuscript copy; git supplies rollback.

## 0. Why this round exists, and what it deliberately is not

Two independent reviews of this manuscript line, plus a follow-up exchange, agreed on three text
defects that are still open in the current file, and on one premise that turned out to be empty:

- **Open.** (a) The conclusion lists the structural readout of the Adam runs without marking it as a
  later readout of the same runs, while the limitations paragraph does mark it. (b) The limitations
  paragraph reports the paired headroom's minimum detectable effect but never says what that coarseness
  means for the `0.5 %` bar the ceiling section defined, so "no detectable headroom" can be read as a
  bound on the effect rather than on the resolution. (c) The numbers added since 2026-10-07 come from
  two run trees that the Data and Code Availability section does not name, so a reader cannot locate
  their source; one review asked for exactly this and called it the availability fix.
- **Empty.** A proposed "reframe the abstract and the contribution list" repair has nothing to do: the
  abstract already states `It does not prove that deployment-target risk is optimized` and
  `not an RMSE win`, and contributions 2, 4 and 5 each carry their own qualifier. This round therefore
  makes **no** change to the abstract, the introduction, the contribution list, or the paper's stated
  scope.

**This round does not aim to raise the Significance score, and it must not be written as if it did.**
The exchange established that the paper's projection moves the mismatch statistics and not the
worst-group error, so no wording can create a usable result that the runs do not contain. These edits
make the existing record accurate and locatable. Same rule as before: revise a claim to match evidence,
never add a caveat that softens a claim the evidence supports.

## 1. Hard constraints

- Edit `TO_OVERLEAF_paper_tmc_r1_clean/main.tex` in place. Do not create copies, do not edit `src/`, the
  bibliography, the diagnosis ledger, any `results_*/` tree, or any frozen artifact. Do not commit.
- Change only the four sites in section 2. Do not touch the abstract, introduction, contribution list,
  related work, any table cell, any equation, or any number other than the `0.5 %` reference in edit 3
  (already printed in the ceiling section).
- Do not add hype, defensiveness, reviewer-facing hedging, or process language. Do not add a caveat to
  a claim the evidence supports, and do not strengthen a claim the evidence does not support.
- Preserve every LaTeX command, label, reference and unit. Keep the file's line width convention and LF
  line endings. Em dashes across the manuscript must stay at or below 3 (currently 0).
- Page budget: `main.pdf` must stay **18 pages** with 0 errors, 0 undefined, 0 multiply-defined and
  0 Overfull.
- If a required edit cannot be made without touching `src/`, write `HT_BLOCKED.md` and stop.

## 2. The four sites

### Edit 1 (mandatory) — the conclusion marks its own readout order

The conclusion currently reads: `... at an $80\%$ minimum detectable effect of $5.80\%$, and the same
fifteen runs reduce $\Delta_{\mathrm{group}}$ and $\Delta_{c\text{-}s}$
(Section~\ref{subsec:limitations}).`

Split it so that the structural readout is stated as a later readout of the same runs, using the same
wording the limitations paragraph already uses (`scored after that prediction contrast`). Do not change
any number, and do not move these figures into the abstract.

### Edit 2 (mandatory) — the limitations states what the detectable effect means for the bar

The limitations paragraph now ends the headroom sentence with `The interval contains zero.` Add to that
sentence, in the same place, that the `80 %` minimum detectable effect of `5.80 %` is too coarse to
resolve the `0.5 %` bar that the ceiling section set, and reference that section
(`\ref{subsec:ceiling}`). One clause; no new statistic, no one-sided bound.

### Edit 3 (mandatory) — the availability section names the new sources

The Data and Code Availability section names `RAVEN\_MCS\_PUBLIC\_REPRO\_R1` and its `w1/` subtree but
not the two trees behind the Adam step replacement and its structural readout. Add one or two sentences
to that section stating that those two trees are internal to this study rather than part of that
bundle, and naming:

- the prediction contrast, with the confirm seed range `30006`--`30020`;
- the structural readout;
- the file holding the test-fitted constant and the training-mean predictor.

Use the section's existing convention for paths (`\texttt{...}`) and keep it compact. Do not claim the
two trees are in the bundle: they are not.

### Edit 4 (mandatory, cosmetic) — rewrap one over-long source line

One line in the limitations paragraph is about 150 characters because an earlier edit joined two
sentences. Rewrap it to the file's width without changing a single character of content.

### Diagnostic, not an edit — contribution 4 versus the limitations

Contribution 4 says that on the prediction half of Section~\ref{subsec:eval_rq3} "the corpus is not a
null", while the limitations paragraph now says the oracle-margin weights supply no detectable
`RMSE_mu` headroom. Check whether the two sentences are about the same object before touching anything:
contribution 4 points at `Table~\ref{tab:e4_ablation}` and a named entry, whereas the limitations
sentence is about the paired oracle-margin headroom on NSW-Traffic. If they are different objects, make
**no** edit and record the check and its result in the gates file. If they are the same object, stop and
write `HT_BLOCKED.md` rather than choosing a reading unilaterally.

## 3. Gates

- **H0 — pre-edit state.** Record the pre-edit sha256 and the line count. Require that all four anchors
  match exactly once, and that the diagnostic in section 2 has been resolved to "different objects"
  before any write.
- **H1 — byte integrity.** After editing, reverse every replacement and require that the reverse
  recovers the pre-edit sha256 exactly. Require that the CRLF count is unchanged.
- **H2 — build.** Compile `supplemental.tex`, `main.tex`, `main.tex` in that order, out of tree.
  Require `main.pdf` **18 pages**, 0 errors, 0 undefined, 0 multiply-defined, 0 Overfull, and
  `supplemental.pdf` 16 pages with 1 Overfull.
- **H3 — prose.** `scripts/check_prose_quality.py --scope paper`: em dashes at or below 3, no new hard
  failure; the existing semicolon advisory may remain.
- **H4 — nothing else moved.** Require that the relative quantities (`-1.49%`, `[-5.42%,+1.76%]`,
  `5.80%`, `15.1%`, `0.0079 [0.0051,0.0110]`, `0.0099 [0.0067,0.0132]`), the two canonical
  terms (`test-fitted constant`, `training-mean predictor`), the two-constant numbers
  (`2.088`, `0.678`, `7.647`, `1.054`, `1.007`), the split means, and every table cell are byte-identical
  to the pre-edit state — which H1 proves globally — and that the abstract and the contribution list are
  byte-identical as well.

## 4. What this round does not do

- It does not raise, argue for, or restate a Significance claim, and it does not change the paper's
  scope, title, abstract, contribution list, or conclusion beyond the readout-order clause.
- It does not add a one-sided confidence bound, a skill score, a worst-group comparison, or any new
  statistic. A usable bound would need a lower-variance estimand and is a design decision, not a text
  edit.
- It does not deposit the two run trees into the bundle, does not index the new numbers in
  `w1/PAPER_NUMBERS.csv`, and does not refresh the shipped PDF. Those are release actions for the
  author.
- It does not add seeds and does not revisit any experiment.

## 5. Outputs

- `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`, edited in place.
- `results_text_repairs/round_v1/HT_GATES.md` — H0 to H4 with the evidence, plus the section-2
  diagnostic's result.
- `results_text_repairs/round_v1/HT_EDITS.md` — each edit's before and after text, verbatim.

## 6. Execution order

1. Read the four sites, run H0, resolve the diagnostic. On any failure, `HT_BLOCKED.md` and stop.
2. Apply edits 1 to 4.
3. Run H1, H2, H3, H4. On failure, revert to the pre-edit sha256 and write `HT_BLOCKED.md`.
4. Write the two output files. Stop. Propose nothing further from this round.

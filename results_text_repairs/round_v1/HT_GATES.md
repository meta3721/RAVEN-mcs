# HT gates — honesty text repairs

Round: `results_text_repairs/round_v1/`. Instruction:
`ccfa-review-reports/raven-mcs-honesty-text-repairs-execution-prompt.md`. Writer skill
`ccf-paper-writer`, mode `polish`. Target: `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`, edited in place;
no copy created. Verdict: **all gates PASS**.

## H0 — pre-edit state

- sha256 `73fa475ede18e1da11dd9118cf2e29276dc8be41b16f742440c6c9e34f5aabd3`, 119384 B, LF only.
- This matches the previous round's post-edit hash exactly, so no third-party change intervened this
  time. All four anchors matched exactly once.
- The section-2 diagnostic resolved to **different objects**, so no edit was made for it; its evidence
  is in `HT_EDITS.md`.

## H1 — byte integrity

- post-edit sha256 `3cc106ca4b6087d9d6a47d69936abf0cd95914b0285e1a86d3c938acb5ad161c`, 119922 B (+538 B).
- reversing all four edits recovers the pre-edit sha256 **exactly**: PASS.
- CRLF count unchanged: PASS.

The reverse replacement is exact, so nothing outside the four sites changed. The abstract, the
introduction, the contribution list, every table cell and every equation are therefore byte-identical
to the pre-edit state by construction.

## H2 — build

Fixed order `supplemental.tex`, `main.tex`, `main.tex`, out of tree:

- `main.pdf` **18 pages**, errors 0, undefined 0, multiply-defined 0, Overfull 0;
- `supplemental.pdf` 16 pages, Overfull 1.

Unchanged from the pre-edit build. **PASS.**

## H3 — prose

`check_prose_quality.py --scope paper`: 14698 words, **em dashes 0/3**, one advisory (semicolon
density), unchanged in kind. **PASS.**

## H4 — nothing else moved

Present and unchanged, with the counts the pre-edit state had plus the re-mentions the new availability
sentence necessarily adds:

| quantity | occurrences |
|---|---:|
| `-1.49`, `5.42`, `15.1`, `0.0079`, `0.0099`, `0.0051`, `0.0067` | 1 each |
| `5.80` | 2 |
| `test-fitted constant` | 4 (was 3; edit 3 adds one) |
| `training-mean predictor` | 5 (was 4; edit 3 adds one) |
| `2.088`, `0.678`, `7.647`, `1.054` | 2 each (metric definition and table caption; edit 3 adds no numbers) |
| `7.657`, `0.301` | 1 each |

**PASS.** One correction to this round's own rationale: edit 4 was justified as restoring the file's
width convention, but the file already contains 26 other lines longer than 120 characters, so the
convention was weaker than stated. Edit 4 is a tidy, not a repair; it changes no content character.

## What this round did not do

- No change to the abstract, the introduction, the contribution list, the title, or the paper's stated
  scope. The proposed "reframe the promise" repair had nothing to act on: the abstract already states
  that the work does not prove deployment-target risk is optimized and that the protocol table is not an
  RMSE win.
- No new statistic: no one-sided bound, no skill score, no worst-group comparison.
- No release action: the two run trees were named, not deposited; `w1/PAPER_NUMBERS.csv` was not
  extended; the shipped PDF was not refreshed.
- This round makes no Significance claim and is not a Significance repair. It makes the existing record
  accurate and locatable.

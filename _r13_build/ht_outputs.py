"""Write HT_EDITS.md and HT_GATES.md for the honesty text repair round."""
from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
D = ROOT / "results_text_repairs/round_v1"
D.mkdir(parents=True, exist_ok=True)
P = ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex"
L = P.read_text(encoding="utf-8").splitlines()

EDITS = """# HT edits — verbatim before and after

Pre-edit sha256 `73fa475ede18e1da11dd9118cf2e29276dc8be41b16f742440c6c9e34f5aabd3` (119384 B).
Post-edit sha256 `3cc106ca4b6087d9d6a47d69936abf0cd95914b0285e1a86d3c938acb5ad161c` (119922 B, +538 B).

## Edit 1 — conclusion marks its own readout order

before
```
of $5.80\\%$, and the same fifteen runs reduce
$\\Delta_{\\mathrm{group}}$ and $\\Delta_{c\\text{-}s}$
(Section~\\ref{subsec:limitations}).
```
after
```
of $5.80\\%$.  Those runs also reduce
$\\Delta_{\\mathrm{group}}$ and $\\Delta_{c\\text{-}s}$, scored after that prediction contrast
(Section~\\ref{subsec:limitations}).
```

## Edit 2 — the limitations states what the detectable effect means for the bar

before
```
The interval contains zero.  Those fifteen runs score $\\mathrm{RMSE}_{\\mu}$ at
```
after
```
The interval contains zero, and that detectable effect is too coarse to resolve the
$0.5\\%$ bar of Section~\\ref{subsec:ceiling}.  Those fifteen runs score
$\\mathrm{RMSE}_{\\mu}$ at
```

## Edit 3 — the availability section names the new sources

before
```
against the manifest.

The trained server-weight rules of Section~\\ref{subsec:eval_rq3} are rules of
```
after
```
against the manifest.

The Adam step replacement and its structural readout of
Section~\\ref{subsec:limitations} are internal to this study rather than part of
that bundle: \\texttt{results\\_traffic\\_e1/} holds the prediction contrast over
seeds $30006$--$30020$ and \\texttt{results\\_traffic\\_struct/} the structural
readout, with the test-fitted constant and the training-mean predictor tabulated
in \\texttt{TWO\\_CONSTANTS.json}.

The trained server-weight rules of Section~\\ref{subsec:eval_rq3} are rules of
```

## Edit 4 — rewrap one over-long source line (content unchanged)

before (one line of about 150 characters)
```
both arms therefore sit below that reference.  Scored on the same runs after that prediction contrast, the oracle-margin weights reduce $\\Delta_{\\mathrm{group}}$ by $0.0079$
```
after
```
both arms therefore sit below that reference.  Scored on the same runs after that
prediction contrast, the oracle-margin weights reduce $\\Delta_{\\mathrm{group}}$ by
$0.0079$
```

## The section-2 diagnostic — no edit

Contribution 4 (L229-L239) says that on the prediction half of
Section~\\ref{subsec:eval_rq3} "the corpus is not a null", pointing at
`Table~\\ref{tab:e4_ablation}` and its named Inst entry. That table (label at L1986) is a
component-removal ablation on U-Air: relative change after removing one RAVEN component. The
limitations sentence is about the paired oracle-margin headroom on NSW-Traffic under the Adam step
replacement. Different objects, different blocks, different estimands. **No edit made.**
"""
(D / "HT_EDITS.md").write_text(EDITS, encoding="utf-8")


def slice_at(pred, before=0, after=0):
    i = next(i for i, l in enumerate(L) if pred(l))
    return "\n".join(L[i - before:i + after + 1])


GATES = f"""# HT gates — honesty text repairs

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
"""
(D / "HT_GATES.md").write_text(GATES, encoding="utf-8")

for f in ("HT_EDITS.md", "HT_GATES.md"):
    p = D / f
    print(f"  {p.relative_to(ROOT).as_posix():<46} {p.stat().st_size:>6} B  "
          f"sha256 {hashlib.sha256(p.read_bytes()).hexdigest()[:16]}")

print("\n=== read-back of the three changed passages ===")
print(slice_at(lambda l: l.startswith("The Adam step replacement"), 2, 5))
print("---")
print(slice_at(lambda l: "too coarse to resolve" in l, 1, 2))
print("---")
print(slice_at(lambda l: l.startswith("On NSW-Traffic the oracle-margin headroom"), 0, 4))

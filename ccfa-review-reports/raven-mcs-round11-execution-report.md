# Round-11 execution report — five text-level repairs, one build repair

```text
Executed: 2026-10-04
Authority: user's "请直接执行，我们定的12页pp，但是先不急这改页数"
Instruction: ccfa-review-reports/raven-mcs-round11-text-repair-instruction.md
Snapshot: snapshots/2026-10-04-pre-r11/{main.tex,supplemental.tex,supplemental.bbl}
Rollback: copy those three files back over TO_OVERLEAF_paper_tmc_r1_clean/ and rebuild.
No experiment, no training, no bundle write, no git action.
```

## 1. Result in one line

**`F10` is closed.** `main.log` and `supplemental.log` now contain **zero** `multiply defined`
warnings, both PDFs keep their page counts (17 / 16), and no citation number, reference entry or
claim changed. `Reproducibility` therefore has its raise condition met: **2 → 3, weighted readiness
3.25 → 3.35** — to be confirmed by the next review round, not asserted here.

## 2. Before / after

| file | before | after | sha256 (after) |
|---|---|---|---|
| `main.tex` | 113 379 B, `88ECD743…` | 113 345 B | `59E4F4D5CFFFF4FF7DB6…` |
| `supplemental.tex` | 5 155 B, `4E59B719…` | 5 536 B | `E99E1058A3251C590AA2…` |
| `supplemental.bbl` | 2 447 B | unchanged | `7406BE7A8C4C2D906093…` |
| `main.pdf` | 888 305 B, `74DF384E…` | 888 276 B, 17 pp | content hash varies per build — see note |
| `supplemental.pdf` | 840 123 B, `D08B9183…` | 840 164 B, 16 pp | `6170CD4A4E70FD07EC3E…` |

**Note on the PDF hashes.** `pdflatex` stamps each run with a creation date and an internal
`/ID`, so `main.pdf`'s sha256 is **not** reproducible across rebuilds: two rebuilds of the identical
sources gave `353EDCB6…` and `77675B22…` at the same 888 276 bytes. The PDF's *content* is
reproducible and is what was verified — 17 pp, `8.23`/`21.73`/`[?]` all 0, `closed by uniform`
twice. Any future instruction should gate on page count, log warnings and extracted text, **not** on
a PDF sha256; the `.tex` hashes above are the ones that identify this state.

`main.tex` change blocks: **4**, +5 / −6 lines, **net −1**. Words 12 377 → 12 372.
Structure unchanged: tables 4, figures 4, equations 37, `\cite{` 42, sections 8, subsections 29,
propositions 4, theorems 2, `\label{` 97, em dashes 0, semicolons 95.

## 3. A1 — build repair (the item that closes `F10`)

**What was wrong.** Five cite keys — `wang2024lightweight`, `wang2026federated`,
`morishita2026who`, `goetze2025floss`, `wang2023cityscanner` — are cited in `appendix.tex`
(L1737, L1767, L1778, L1780, L2460) and in the main text, and `appendix.tex` is `\input` by
`supplemental.tex`. `\bibitem` therefore defined each of the five keys in `supplemental.aux`, and
`main.tex` imports that file through `xr` / `\externaldocument`, producing five
`LaTeX Warning: Label '…' multiply defined`. The two documents share **zero** label keys; only
these five cite keys collided.

**Two mechanisms were tested in a sandbox copy and rejected before the real edit.**

| attempt | mechanism | measured result | verdict |
|---|---|---|---|
| 1 | prefix the five `\bibitem` keys with a macro in `supplemental.bbl` | the prefix reached `\bibitem` but not the deduplication, and it collided in a new place: `main.log` warned on `supp:…` | **rejected** |
| 2 | suppress the five `\citation{…}` writes so `\bibitem` never sees them | the collision is created by `\bibitem` writing `\bibcite`, not by `\citation`; warnings unchanged | **rejected** |
| 3 | **locally disable the `.aux` write around the bibliography**: `\makeatletter\@fileswfalse\makeatother` before `\bibliographystyle`, `\@fileswtrue` after `\bibliography` | `multiply defined` = 0 in both logs, 17 / 16 pp, **`main.pdf` byte-identical to the baseline (888 305)** | **adopted** |

`\citation` is deliberately left intact, so BibTeX input, citation numbering and the reference list
are untouched; only the redundant `\bibcite` redefinition is suppressed. Verified in the rendered
PDF: **`[?]` count = 0 in both documents**; all five references still appear in both reference lists;
every other `\cite` in `main.tex` still resolves.

**One build-order fact the next pass needs.** `main.tex` reads `supplemental.aux`, so `main` must be
rebuilt **after** `supplemental` whenever `supplemental` changes. Building in the other order leaves
the five warnings in place from the stale import. The correct order is: `pdflatex supplemental`
(four passes) → `pdflatex main` (four passes).

**Root cause of the whole class, recorded:** `main.tex` and `appendix.tex` cite the same five works
and are compiled into two PDFs that import each other's `.aux`. Any future shared citation will
re-create the warning. The durable fix is one bibliography owner; the guard above is the local fix.

## 4. A2 — terminology (`R5-16`, two senses of "recoverable")

Four occurrences existed; three carried the *gap-share* sense and one the *ceiling* sense.

| line | before | after |
|---|---|---|
| L1819 | "is already **recoverable** by uniform server weights" | "is already **closed** by uniform server weights" |
| L2194 (conclusion) | "mostly **recoverable** by uniform server weights" | "mostly **closed** by uniform server weights" |
| L2103 / L2106 | `\subsection{Recoverable-Gain Ceiling}` … "The **recoverable** gain is bounded inside the class" | **unchanged** — this is the ceiling sense, and round 9's raise condition is satisfied without renaming it |

Gate: `recoverable by uniform` = 0 hits; `Recoverable-Gain Ceiling` = 1; `The recoverable gain` = 1.
Verified in the rendered PDF at both sites.

## 5. A3 — factual attribution (the one item that touched a claim)

**Instruction said:** take the replacement value only from the manuscript's own tables; if the two
variants have no printed value there, **drop the range** rather than carry an unverified pair.

**Step 1 reading (reported as required).** `appendix.tex` contains **no** printed feasibility-violation
value for either variant. Its `RAVEN-SimOracle` rows (L1899, L1928) carry `WorstGroupRMSE` / `RMSE_μ`
values, and its `RAVEN-NoDesign` rows (L2025, L2033, L2196) carry worst-group values — **different
quantities from the `l1`-unit feasibility violation** the sentence is about. `main.tex` reports
neither variant's violation figure.

**Pattern used: II — the range is dropped.** New sentence, L1834-1835:

```
into alignment: against the uncorrected reference, which violates the recorded
feasibility constraints and is worse than uniform weights,
```

**Gate:** `8.23`, `21.73` and the pair `8.23 to 21.73` all return **0** in the rendered `main.pdf`
and 0 in `main.tex`; the following clause (`the projection is worth $+1.188$ pp ($[0.956,1.409]$) …`)
is byte-identical.

**Carried forward as an option, NOT applied.** If the user prefers to keep the figures, the correct
attribution is that they are the `raven_wo_design` and `raven_simoracle` rows of the B0 table in
`results_w1_ladder/round_v3/EXECUTION_REPORT.md` (L62, L63), i.e. a **range across arms**, one of them
the design-free baseline — *not* the uncorrected reference, whose own value on that block is `16.81`.
That would read, for example: "…the uncorrected reference violates the recorded feasibility
constraints, and across the design and oracle variants the violation runs from 8.23 to 21.73 l1
units; against it, the projection is worth …". This needs one more authorisation because it
re-introduces two numbers.

## 6. A5 — privacy sentence detached from the coverage-gate finding

L2172-2176, reordered with **no sentence added or removed**:

| | |
|---|---|
| before | "…switching is not proven valid, and Design is not opened from `Gate_t`.  Federated learning itself does not provide a privacy guarantee." |
| after | "…switching is not proven valid.  Federated learning itself does not provide a privacy guarantee.  Design is not opened from `Gate_t`." |

Verified in the rendered PDF: the privacy sentence no longer hangs off the `Gate_t` clause, and the
paragraph no longer ends on a compliance disclaimer.

## 7. A4 and A6 — proposals only, not applied

**A4 — the availability paragraph still does not name `w1/`.** Current sentence, `main.tex`
L2219-2221: "A verifier reconstructs tabulated cells from those CSVs; the bundle is not a pinned
retraining archive, and NSW four-region is not a confirmation experiment."
**Proposed one-clause insertion** after "from those CSVs": "…and the W1 evidence behind the
structural and mechanism results is indexed in the bundle's `w1/` subtree (`PAPER_NUMBERS.csv` maps
each printed number to its source file)." Cost: one sentence, no number. Needs authorisation.

**A6 — three record corrections, identified and not applied.**
* `M-3`: `raven-mcs-tmc-review-round9.md` §7 `H9(a)` and §2.2 row 14 state that `120 of 120`
  "greps to 0". It is present once in round 9's own frozen file and once in the current file.
  Round 9 contradicts itself: §2.1 (L97) and §14 item 6 disagree with §7. Proposed fix: withdraw
  `H9(a)` at verdict level and correct the two sentences that cite it.
* `M-4`: §6 rows `R5-6`, `F1`, `F8` quote text that is absent from round 9's frozen file (`R5-6`) or
  from the current files as well (`F1`, `F8`). Proposed fix: label those three quotes as inherited
  from round 8 and mark the `F1`/`F8` wording as superseded by the current text.
* `A-6`: §6 contains 21 rows whose status cell says `closed` against a summary line reading
  "20 closed"; the diagnosis record's Part V §V.1 reproduces "20". Proposed fix: state 21, or state
  20 with `F4` explicitly excluded as already closed at round 8.

## 8. Page track

The user has settled the track as **12 pp**, with page reduction **deferred**. Nothing in this pass
added or removed a page: `main.pdf` is 17 pp before and after. When reduction is scheduled, the
candidates already identified are `C1` (Proposition 4's unused directional-derivative clause,
L1358-1360) and `C2` (~40 lines of coverage-Gate apparatus for an instrument that never acts,
L1002-1006 / L1418-1421), plus the 17-pp structure itself; that work needs its own instruction.

## 9. Gates — all passed

| gate | target | measured |
|---|---|---|
| `multiply defined` in `main.log` | 0 | **0** |
| `multiply defined` in `supplemental.log` | 0 | **0** |
| undefined references, both logs | 0 | **0 / 0** |
| undefined citations, both logs | 0 | **0 / 0** |
| `[?]` in either PDF | 0 | **0 / 0** |
| `main.pdf` pages | 17 | **17** |
| `supplemental.pdf` pages | 16 | **16** |
| structural counts | unchanged | **unchanged** (4/4/37/42/8/29/4/2/97, em dashes 0) |
| `main.tex` change blocks | ≤ 4 | **4** (+5 / −6, net −1) |
| `recoverable by uniform` | 0 | **0** |
| `8.23` / `21.73` in `main.tex` and `main.pdf` | 0 | **0 / 0** |
| pre-edit snapshot | exists and bytes match baseline | `snapshots/2026-10-04-pre-r11/`, hashes recorded |

**One pre-existing warning is NOT closed and is not part of `F10`'s citation half:** `supplemental.log`
still reports `Overfull \vbox (3.42152pt too high)` and `Text page 10 contains only floats`, unchanged
from before this pass. `main.log` has 0 overfull. If the next review requires a fully warning-clean
build, that vbox is a separate, cosmetic item.

## 10. Checks run, checks skipped

```text
Checks run: baseline hash/byte freeze of five files before any edit; sandbox experiments of three
candidate mechanisms for A1 before touching the real tree; anchored-string edits with an occurrence
count of exactly 1 asserted per edit; block-level difflib of main.tex (4 blocks) and supplemental.tex;
four pdflatex passes each in the order supplemental -> main; warning census of both logs
(multiply defined / undefined reference / undefined citation / overfull / float-page / undefined
control sequence); pdfinfo page counts; pdftotext extraction of both PDFs with per-edit string
verification at the four changed sites in the rendered output; negative searches for the withdrawn
range and the old clause order; structural-count comparison; rollback snapshot written and hashed.
Checks skipped: no proof re-derivation; no re-verification of the paper's statistics; the bundle was
not touched and its verifier was not re-run (no bundle file changed); no git action.
```

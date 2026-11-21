# Executable instruction — RAVEN-MCS round-11: five text-level repairs, one build repair, three record corrections

```text
Prepared: 2026-10-04, by the round-10 record audit
Target   : TO_OVERLEAF_paper_tmc_r1_clean/{main.tex, supplemental.tex, supplemental.bbl}
           plus three files under ccfa-review-reports/
Frozen baseline: main.tex sha256 88ECD743321E38E949844B316CAA3F3A3132D48EA4CE9115607A1A3C6BE281B7
                 (2026-10-04 10:06:17, 113379 bytes, 2246 lines, 12377 words, 17 pp)
Authority: every edit below is authorised by the user's "可以，请按重要程度排序" of 2026-10-04,
           with two exceptions carried as gates A4 and A6, which must not be executed on
           this instruction alone.
Scope    : NO new experiment. NO training. NO change to any number except the one named in A3.
           NO change to any claim's truth value. NO claim may be strengthened or weakened.
Stop rule: if any "Gate" fails, STOP that item, leave the file byte-identical to its pre-item
           state, and report. Do not attempt a workaround. Do not proceed to later items
           that depend on it.
```

---

## 0. Before touching anything

**0.1 Take a rollback snapshot.** Copy `main.tex` and `supplemental.tex` to
`snapshots/2026-10-04-pre-r11/{main.tex,supplemental.tex}`. Also copy `supplemental.bbl`.
Record sha256 of all three.

**0.2 Record the baseline.** Confirm and report: `main.tex` = `88ECD743…`, 113379 bytes;
`supplemental.tex` = `4E59B719B8B214AD232756D4E9EFABD2AC1AA0BCD74EE8E85CF40693D93A738B`, 5155 bytes;
`supplemental.bbl` sha256 (fill in). If any differs, STOP and report — the workspace is not the
state this instruction was written for.

**0.3 Build command (the only one permitted).** From `TO_OVERLEAF_paper_tmc_r1_clean/`:
`pdflatex -draftmode main` then two full `pdflatex main` passes; same for `supplemental`.
MiKTeX in this sandbox exits non-zero while writing its log even when LaTeX completes — read the
`.log` files and the exit status of the PDF, never the wrapper's exit code alone.

**0.4 Anchors are strings, not line numbers.** Every edit below is specified by a verbatim
`old_string`. If an `old_string` does not appear exactly once, STOP that item and report; do not
fuzzy-match, do not edit by line number.

---

## A1. Build repair — remove the five multiply-defined citation keys

**This is the only item that changes a score dimension if it works: `F10` closes and
`Reproducibility` goes 2 → 3 (weighted sum 3.25 → 3.35).** It touches no sentence of the paper.

**Root cause, verified — do not re-diagnose.** Five cite keys are legitimate in both documents
because `appendix.tex` is `\input` by `supplemental.tex`:
`wang2024lightweight` (appendix.tex L1737), `wang2026federated` (L1767), `morishita2026who` (L1778),
`goetze2025floss` (L1780), `wang2023cityscanner` (L2460). Both `main.aux` and `supplemental.aux`
therefore carry `\citation{…}` for them, so both `.bbl` files emit the same five `\bibitem` keys, and
`main.tex` L32-33 (`\usepackage{xr}` + `\externaldocument{supplemental}`) imports
`supplemental.aux`, producing `LaTeX Warning: Label '<key>' multiply defined` five times.
The two documents share **zero** label keys; only cite keys collide.

**Forbidden for this item.** Do NOT delete or edit any `\cite{…}`. Do NOT remove
`\usepackage{xr}` or `\externaldocument{supplemental}` from either file: main.tex needs
`supplemental.aux` for exactly one reference (`app:kappa_probe`) and appendix.tex needs `main.aux`
for exactly one (`subsec:equivalence_band`). Removing either turns a real reference into `??`.
Do NOT touch `main.bbl`, `reference.bib`, or any `.tex` prose.

**Attempt 1 — mint the five keys under a prefix in the supplemental document.**

The mechanism must make the `\bibitem` key and the `\citation` lookup agree *after* the prefix is
added; a naive `\renewcommand{\bibitem}` will break IEEEtran's `\bibitem[...]{...}` optional
argument and will print `[?]`. So do it where BibTeX writes the key.

1. In `supplemental.tex`, immediately before `\bibliographystyle{IEEEtran}` (currently L125), add:
   ```latex
   \makeatletter
   \def\bibitem{\@ifnextchar[{\@suppbib}{\@suppbib[]}}
   \def\@suppbib[#1]#2{\@lbibitem[{#1}]{supp:#2}\item\if@filesw
     {\let\protect\noexpand\immediate\write\@auxout{\string\bibcite{supp:#2}{}}}\fi}
   \makeatother
   ```
   If this exact definition does not compile, **delete it and go to step 2** — do not iterate on the
   macro more than twice.
2. Ensure the five keys carry the prefix in the shipped `.bbl`. If the macro above compiled, the
   `.bbl` still holds unprefixed `\bibitem` keys and the prefix is applied at read time; verify by
   rebuilding. If it did not compile, instead edit `supplemental.bbl` directly: change the five
   `\bibitem{<key>}` lines to `\bibitem{supp:<key>}` for `wang2024lightweight`,
   `wang2026federated`, `morishita2026who`, `goetze2025floss`, `wang2023cityscanner`, changing
   nothing else, and ALSO change the five matching `\bibcite{<key>}` entries in `supplemental.aux`
   to `\bibcite{supp:<key>}` so the lookup and the label agree.
3. Rebuild `supplemental` four passes, then `main` four passes.

**Attempt 2 — take this only if Attempt 1 prints `[?]` or changes a citation number.** Remove
`\usepackage{xr}` and `\externaldocument{supplemental}` from `main.tex` only, and replace main's
single reference into the appendix (`app:kappa_probe`, main.tex L2085 and L2231) with the literal
text `Appendix~K-A`. Keep `supplemental.tex`'s own `xr` and `\externaldocument{main}` untouched.
This is permitted **only** if the `[?]` count in `main.pdf` stays 0 and `main.pdf` stays 17 pp.

**Attempt 3 — do not attempt.** Moving Appendix K into `main.tex` changes page counts, structure and
the supplementary filing; it is out of scope for this instruction. Report it as the remaining option.

**Gate A1.** `main.log` and `supplemental.log` each contain zero `multiply defined` lines;
`main.pdf` remains 17 pp and `supplemental.pdf` 16 pp; `[?]` appears nowhere in either PDF;
`main.tex`'s `\cite{` count is still 42 and the five appendix cites are intact; `main.pdf` changes by
less than 2000 bytes. Report which attempt succeeded and the before/after warning counts. If both
attempts fail, revert from the snapshot and report `F10` as still open — that is an acceptable
outcome and must not be worked around.

---

## A2. Terminology — separate the two senses of "recoverable"

`R5-16` / independent review `M1`. Four occurrences exist; the *ceiling* sense is the section
title's and must NOT be renamed (round 9's own condition is "the two one-line disambiguations").

**Edit 2a** — `main.tex`, L1819. Old (verbatim, one line):
```
($68.96\%$, $[1.22,1.65]$) is already recoverable by uniform server weights
```
New:
```
($68.96\%$, $[1.22,1.65]$) is already closed by uniform server weights
```

**Edit 2b** — `main.tex`, L2194. Old:
```
recoverable by uniform server weights, and the surviving part requires the
```
New:
```
closed by uniform server weights, and the surviving part requires the
```

**Do not edit** `\subsection{Recoverable-Gain Ceiling}` (L2103) or "The recoverable gain is bounded
inside the class the method defines" (L2106). Those are the ceiling sense.

**Gate A2.** `recoverable by uniform` returns 0 hits in all three `.tex` files;
`Recoverable-Gain Ceiling` and `The recoverable gain` each still return 1 hit;
`main.pdf` remains 17 pp; no other sentence changed (diff the file and confirm exactly two lines).

---

## A3. Factual attribution — the feasibility-violation range at L1834-1835

`A-8` of the round-10 audit. **This item decides which object the paper says is infeasible, so it is
not a wording change.** Read the whole item before editing.

**Verified facts.** The tokens `8.23` and `21.73` occur exactly twice in the repository evidence, as
the last column of the B0 table in `results_w1_ladder/round_v3/EXECUTION_REPORT.md`:
**L62** `| SS | raven_wo_design… | … | 8.23 |` and **L63** `| SS | raven_simoracle | … | 21.73 |`.
The same table gives `raven` = **16.81** (the arm the sentence is about), `raven_wo_obs` 15.36,
`raven_wo_use` 16.01, `count` 5.97, `uniform` 0. The companion per-seed file
`round_v3/SOURCE_LADDER.csv` (column `outside_Cr_l1`, `ds=sensorscope`, `rule=B0`) gives block means
`raven` 16.683, `raven_simoracle` 22.106, `raven_wo_obs` 15.380, `raven_wo_use` 15.699,
`raven_wo_design` 7.836, `count` 5.621, `uniform` 0.

**Prohibited in this item.** Do NOT use any number supplied above as the replacement value — the
four known seed subsets give 7.836 / 7.839 / 8.13 / 7.592 for the design-free arm, so the exact
provenance of the printed pair is not established. Do NOT recompute anything, do NOT open a new
artifact, and do NOT introduce a number that is not printed in a table of the current manuscript.

**Step 1 — source from the manuscript's own tables.** Open `main.tex` and `appendix.tex` and read the
tables that report the `raven_wo_design` and `raven_simoracle` variants (search those two strings in
`appendix.tex`; expect `tab:app_block_rmse`). Report the exact printed value for each variant and the
table label it came from. **If either variant has no printed value in the manuscript, say so and go
straight to Pattern II.**

**Step 2 — the edit.** Current text, `main.tex` L1833-1836 (verbatim, whitespace-insensitive):
```
Imposing $\mathcal{C}_r$ and projecting onto it is what turns the reconstruction
into alignment: against the uncorrected reference, which violates the recorded
feasibility constraints by $8.23$ to $21.73$ and is worse than uniform weights,
the projection is worth $+1.188$ pp ($[0.956,1.409]$) on SensorScope and
```
Rewrite the attribution so the range is not attached to "the uncorrected reference". Use one of:
* **Pattern I (preferred if both variants have a printed value):**
  "…into alignment: the uncorrected reference violates the recorded feasibility constraints, and
  across the design and oracle variants the violation reaches $X$ to $Y$; against it, the projection
  is worth …" — with `X`, `Y` the values read in Step 1 and the constraint string unchanged.
* **Pattern II (if only one variant's value is available, or neither is):**
  "…into alignment: the uncorrected reference violates the recorded feasibility constraints and is
  worse than uniform weights; against it, the projection is worth …" — i.e. drop the range entirely.
  **Dropping is the correct fallback. Inventing or carrying an unverified pair is not.**

**Constraints.** Keep `$+1.188$ pp ($[0.956,1.409]$)` and everything after it byte-identical. Keep
the sentence's claim size: it may not assert a stronger infeasibility claim than the source table
supports. The edit must not add or remove more than 2 lines.

**Gate A3.** Report: the Step 1 readings with their table labels; the pattern used; whether the two
numbers were kept or dropped; and a confirmation that `8.23` and `21.73` now appear in `main.tex`
either 0 times (Pattern II) or in a sentence whose subject is named as the design/oracle variants
(Pattern I). `main.pdf` remains 17 pp.

---

## A4. GATE — the availability paragraph may NOT be edited on this instruction

Naming `w1/` in `main.tex` L2211-2221 is a manuscript edit and the user has not authorised it.
Report instead, without editing: the exact current sentence that would need the clause, and a
one-clause proposal. **Do not apply it.**

---

## A5. Wording — detach the privacy sentence from the coverage-gate finding

`H5`. The sentence is already inside `\subsection{Limitations}` (L2148); the defect is that it
follows a coverage-oracle result sentence, so it reads as a non sequitur.

**Edit 5a.** Current text, `main.tex` L2172-2176 (verbatim across the line breaks):
```
On a frozen coverage-stress oracle, pooled CERTIFIED
validity is $0.959$ and U-Air $a=1.00$ is $0.750$; adaptive RESET/CERTIFIED
switching is not proven valid, and Design is not opened from
$\mathrm{Gate}_t$.  Federated learning itself does not provide a privacy
guarantee.
```
Replace with exactly:
```
On a frozen coverage-stress oracle, pooled CERTIFIED
validity is $0.959$ and U-Air $a=1.00$ is $0.750$; adaptive RESET/CERTIFIED
switching is not proven valid.  Federated learning itself does not provide a
privacy guarantee.  Design is not opened from $\mathrm{Gate}_t$.
```
This moves the privacy sentence away from the `Gate_t` clause it currently hangs off, and leaves the
paragraph ending on the Design-boundary statement rather than on a compliance disclaimer.
No other sentence in the paragraph changes, and no sentence is added or deleted.

**Gate A5.** Either the swap is applied and the paragraph's sentence count is unchanged and
`main.pdf` stays 17 pp, or the item is reported as a no-op with the reason.

---

## A6. GATE — record-side corrections may NOT be executed on this instruction

Three record corrections were identified but the user has not authorised edits to the review
reports. Report, without editing:
* `M-3`: `ccfa-review-reports/raven-mcs-tmc-review-round9.md` §7 `H9(a)` states `120 of 120` greps
  to 0. Measured: it is present once in round 9's own frozen file and once in the current file
  (probe `120$ of $120`). List the exact line numbers of the claim and of the contradicting §2.1
  sentence (L97 and §14 item 6).
* `M-4`: same report §6 rows `R5-6`, `F1`, `F8` carry quotes that are absent from round 9's frozen
  file and, for `F1` and `F8`, from the current files too.
* `A-6`: same report §6 table has 21 rows whose status says `closed` against a summary line reading
  "20 closed"; `ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md` §V.1 reproduces "20".
Propose the exact replacement wording for each; do not apply it.

---

## A7. Forbidden, in one list

* No change to any number other than the two positions of `A3`.
* No change to any proof, theorem, proposition, table, figure, caption or label text.
* No `\cite` removal; no removal of `xr`/`\externaldocument`; no edit to `main.bbl`,
  `reference.bib`, `appendix.tex`, or any `results_*` directory.
* No use of the `8.23`/`21.73` values as replacements (see `A3`).
* No new experiment, no training, no bundle write, no git commit, no file uploaded anywhere.
* No substitution of a nearby string for a failed `old_string`.
* Do not rename the ceiling sense of "recoverable".

## A8. Deliverable and report

**Deliverable:** the edited `main.tex`, `supplemental.tex`, `supplemental.bbl`, both rebuilt PDFs,
and `snapshots/2026-10-04-pre-r11/`.

**Report, in this order:**
1. Before/after for each item: `sha256`, bytes, lines, words, pages.
2. `A1`: which attempt succeeded; the five warning lines before and after; `multiply defined` count
   in each log (target 0); any change to a printed citation number.
3. `A2`: the four `recoverable` occurrences before and after with their lines.
4. `A3`: the Step 1 table readings; the pattern used; the final sentence verbatim; the `8.23`/`21.73`
   count in `main.tex`.
5. `A5`: applied or no-op, with the final paragraph verbatim.
6. `A4` and `A6`: proposals only.
7. Build evidence: both logs' last line, page counts, and a grep for `[?]` in both PDFs.
8. Anything that deviated, and every gate that failed.

**Gate A8 (final).** `main.pdf` 17 pp, `supplemental.pdf` 16 pp, 0 undefined references, the
structural counts unchanged (`\begin{table` 4, `\begin{figure` 4, `\begin{equation` 37, `\cite{` 42,
`\section{` 8, `\subsection{` 29, `\begin{proposition` 4, `\begin{theorem` 2, `\label{` 97),
em dashes 0, `multiply defined` 0 in both logs. If any fails, revert that item and report.

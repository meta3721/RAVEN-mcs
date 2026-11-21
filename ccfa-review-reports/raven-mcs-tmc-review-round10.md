# RAVEN-MCS — Round 10 Record and Bundle Audit

```text
Date of audit        : 2026-10-04
Scope                : the round-9 review record, the P0 manuscript pass it triggered, the
                       diagnosis record's Part V synchronisation, and the M7 public-bundle
                       refresh — i.e. an audit of the RECORD, not a re-review of the paper
Frozen contract      : TMC-J-R4, inherited unchanged (8 dimensions, weights
                       0.10/0.20/0.25/0.15/0.10/0.10/0.05/0.05, anchors 1-5, threshold 4/10,
                       |weighted delta| < 0.05 = unchanged)
Nothing was re-run    : no experiment, no training, no build, no bundle write, no git action.
                       Every number below was re-measured from files on disk.
Deliverable           : severity-ranked findings only — no scores are awarded to the manuscript
                       this round, because no manuscript text changed during it.
```

---

## 1. Frozen artifacts

Hashes and mtimes taken before any reading and re-taken after all analysis; identical at both points.

| File | sha256 | mtime | bytes |
|---|---|---|---|
| `TO_OVERLEAF_paper_tmc_r1_clean/main.tex` | `88ECD743321E38E949844B316CAA3F3A3132D48EA4CE9115607A1A3C6BE281B7` | 2026-10-04 10:06:17 | 113 379 |
| `TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex` | `29ADD10FB7F8424714FD19632054B28AF33F184580DE69F0094864121332B627` | 2026-10-02 15:42:00 | 102 457 |
| `TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex` | `4E59B719B8B214AD2327…` | 2026-10-04 10:07:54 | 5 155 |
| `TO_OVERLEAF_paper_tmc_r1_clean/main.pdf` | `74DF384ED9359751A117…` | 2026-10-04 10:08:07 | 888 305 |
| `ccfa-review-reports/raven-mcs-tmc-review-round9.md` | `A8EF8FA5956631144B00…` | 2026-10-04 09:58:08 | 104 981 |
| `ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md` | `4655895CF7D99AB6D9B9…` → see §6 | 2026-10-04 19:10:30 | 279 795 |
| `RAVEN_MCS_PUBLIC_REPRO_R1/MANIFEST.csv` | `F1751CB15E86BB6755B6…` | 2026-10-04 18:21:35 | 291 056 |
| `RAVEN_MCS_PUBLIC_REPRO_R1/BUNDLE_SUMMARY.json` | `E827C9264ADCAA97EBCC…` | 2026-10-04 18:21:06 | 811 |

**Two snapshots are byte-identical to each other and to round 9's frozen file**, which settles a
question the record left open: `snapshots/2026-10-03-pre-page-recovery/main.tex` and
`snapshots/2026-10-04-pre-p0-fix/main.tex` both hash to
`2FD3CEF245B76F57B604017FFA5AE9F9545F55C3D8A599F94F45CFEAD5CBD075` (112 870 bytes). The
"page-recovery reversion" therefore produced **no byte change**, and the two snapshots are one state,
not two.

**Structural counts, current `main.tex`, all identical to round 9's:** `\begin{table` 4,
`\begin{figure` 4, `\begin{equation` 37, `\cite{` 42, `\section{` 8, `\subsection{` 29,
`\begin{proposition` 4, `\begin{theorem` 2, `\label{` 97; em dashes 0, semicolons 95, words 12 377;
`main.pdf` 17 pp, `supplemental.pdf` 16 pp. **No numbering-drift discount applies.**

---

## 2. What this round verified, claim by claim

| # | claim under test | source | result |
|---|---|---|---|
| 1 | the `P0` pass happened **after** round 9 signed off | round-9 §0 freeze table vs `main.tex` mtime | **TRUE** — freeze 09:37:24 (112 870 B), current 10:06:17 (113 379 B) |
| 2 | the `closed` rows of round 9 still hold in the current file | round-9 §6 deciding quotes vs current `main.tex`, two independent passes | **21 of 21 verdicts hold; 17 of 21 quoted strings survive** — 3 quotes were never in round 9's frozen file (M-4), and the §6 table's own count is 21 against a summary that says 20 (A-6) |
| 3 | round 9's `H9(a)` ("`120 of 120` … all five lost") | `120$ of $120` probe on four file states | **FALSE** — the string is present in the frozen file and in the current one |
| 4 | bundle payload is byte-identical to its sources | 214 files, path-wise SHA-256 | **TRUE** — 214/214 identical, 0 mismatches |
| 5 | `verify.py` passes on the shipped bundle | re-run | **TRUE** — `checked=2116 mismatches=0` |
| 6 | bundle counts and sizes in the record | `BUNDLE_SUMMARY.json`, `MANIFEST.csv`, `EXCLUDED_HASHES.csv` | numbers correct; one wording error (A-5) |
| 7 | `PAPER_NUMBERS.csv` rows are checkable at the named source | 70 `located` rows resolved and opened; `source_sha256` verified on all 70 | 50 verbatim, **20 derived** (all reconstructible), 12 of 70 annotated; **sha256 70/70 match, 0 mismatches** (A-2) |
| 8 | the availability paragraph still omits `w1/` | `main.tex` L2211-2221 | **TRUE**, unchanged and still unauthorised |
| 9 | the paper and its evidence are versioned | `git ls-files` vs disk | paper/bundle tracked; **review + evidence untracked** (M-2) |
| 10 | `appendix.tex` untouched by the `P0` pass | hash + mtime | **TRUE** — 2026-10-02 15:42:00, hash unchanged since round 8 |
| 11 | the bundle's own verifier passes and its indexes are consistent | `verify.py`; `MANIFEST.csv` row-by-row | **TRUE** — `checked=2116 mismatches=0`; all **216** `w1/` manifest rows exist with matching sha256; the only `w1/` file not in the manifest is `w1/MANIFEST_ADDITIONS.csv`, which cannot hash itself |
| 12 | every copied artifact equals its source | 217 files enumerated, path-wise SHA-256, cross-checked | **TRUE** — 214/214 copied artifacts byte-identical, 0 mismatches; the 3 files with no source are the bundle-authored indexes. The `tradeoff_v4` subtree matches only after removing the bundle's added leading `runs/` level |
| 13 | the excluded-file list is a truthful "hash-listed, not redistributed" record | 610 rows resolved against both roots | **TRUE** — 610/610 resolve in the working tree with matching sizes and hashes; 0 present under the bundle root; total 29 380 661 bytes |
| 14 | the `H2` mechanism numbers are in the shipped bundle | `w1/ladder_v3/MYOPIC_DIAG.json` | **TRUE** — `n_windows` 3279, `range_median` `-1.1302070390684094e-13`, `d_myo_tb` `1.051402204950762`, `d_unif` `1.0621341226159433`, `max_abs_diff_tb_vs_unif` `0.033694057466112426`, sha256 `E765D27181983E7D…` |

---

## 3. Findings — major and moderate

**Scope of each finding, stated up front, because most of this round is not about the paper.** The
paper is in the state round 9 left it in plus the five `P0` sentences; nothing in this audit touches
its claims, numbers or proofs.

| finding | attaches to | affects the submitted paper? |
|---|---|---|
| `M-1` | the review process — which version a verdict is valid for | **no** — record only; the finding says so in its own first line |
| `M-2` | repository version control | **no**, but it weakens the provenance of every number whose only source is an unversioned tree |
| `M-3` | the round-9 report's `H9(a)` | **no** — and the item it reports as lost is actually present |
| `M-4` | the round-9 report's quoted evidence | **no** — the verdicts hold; the quotations do not |
| `A-1`, `A-3`, `A-4`, `A-5`, `A-6` | the diagnosis record and the bundle indexes | **no** — metadata and labels |
| `A-2` | the bundle's provenance column | **no**, but it is the one an outside reader would hit first |
| `A-7` | repository hygiene | **no** |

So the honest headline for the manuscript is: **round 10 found no new defect in the paper.** Every
finding here is a finding about the record, the review trail, or the released bundle.

### MAJOR

**M-1 — Round 9's approval carries no validity rule against later edits, and after this round the paper has been edited by more than one writer.**
**Scope first: this is not a defect of the paper.** No posted verdict moved, no claim broke, and the 21
closed rows all still hold §5). It is a defect of *verification traceability*, and it is stated here
because round 10 is a record audit. round 9 froze `main.tex` at `2FD3CEF2…`, 112 870 bytes, mtime
**09:37:24**, and indexed all of its verdicts to that file ("Every line number indexes the current
2239-line `main.tex`"). The `P0` pass rewrote the same file at **10:06:17** (113 379 bytes,
`88ECD743…`), **4 change blocks, +19 / −12 lines, net +7**, and rebuilt both PDFs at 10:08.
Nothing in the round-9 report, in Part V, or in the correction block states that the object of the
review was replaced after the review closed, and round 9's own closure rule — "a closure is not undone
by a defect elsewhere unless the verdict sentence itself is contradicted" — quietly assumes the file
will not move.

**Round 10 checked whether anything moved without a record, and found nothing.** The current file's
hash is the one the `P0` record prints; the round-9 file's hash is the one round 9 froze; the two
snapshots around the page-recovery reversion are byte-identical to each other and to the round-9 file.
So every visible change in `main.tex` between the round-8 state and now is attributable to a recorded
pass. **What cannot be checked at all** is any edit made without a snapshot, because the snapshot
corpus is the only anchor: a writer who edits in place leaves no trace of the *fact* of the edit, only
of its result. M-1 is therefore not evidence of an unrecorded change — it is the statement that no such
evidence could exist, and that the previous round's verdicts have no standing rule deciding whether
they survive one.

**What this means with several writers on the file.** Each pass — mine, the user's own edits, another
tool's — lands without provenance, so "the review approved this" is a claim about a byte string, not
about the paper. The practical consequence is not that a later writer damages the paper; it is that a
verdict gets cited as current after the text it described has been replaced, which is exactly what
M-4 shows round 9 doing with round 8's quotes. Fix, and it is one line of discipline rather than any
edit: every pass records the hash it started from and the hash it ended at, and every pass that lands
after a review either re-validates the affected verdicts against the new hash or marks them stale. The
`P0` record did print its hash; what it did not do is carry that obligation for the review that
preceded it.

**M-2 — The whole evidence and review base is untracked in git; only the narrative is versioned.**
`git ls-files` versus disk:

| tree | tracked | on disk | bytes |
|---|---|---|---|
| `TO_OVERLEAF_paper_tmc_r1_clean/` | 32 | 56 | — (the four `.tex` **are** tracked; the PDFs and build logs are not) |
| `RAVEN_MCS_PUBLIC_REPRO_R1/` | 1 863 | 2 118 | 171.9 MiB |
| `ccfa-review-reports/` | **0** | 49 | 1 607 064 |
| `snapshots/` | **0** | 44 | 3 707 694 |
| `results_w1_ladder/` | **0** | 2 368 | 38 472 532 |
| `results_gatekeeping/` | **0** | 184 | 545 429 |
| `results_exogenous_target/` | **0** | 30 | 3 920 567 |

**2 676 evidence files / 46.05 MB are unversioned** (`git ls-files` against those five trees returns
**0**), and so is all ten rounds of review. The repository is frozen at a single commit whose subject
line is "Add City Scanner NYC PM2.5 ingest and the C1 spatial/T-Drive kill harness" — i.e. the last
commit predates rounds 4-10. Two consequences that
matter for the submission rather than for hygiene: (i) a manuscript value whose only source is a
`results_*` tree has no versioned provenance, so an accidental regeneration would be undetectable;
(ii) the released PDFs (`main.pdf`, `supplemental.pdf`) are themselves untracked, so the frozen page
counts and hashes the record quotes cannot be tied to any committed state. Fix is a decision, not an
edit: commit the review corpus and the `results_*` trees, or publish them as a second artifact with
its own hash manifest.

**M-3 — Round 9's `H9(a)` is false, and round 9's own report contains the evidence that falsifies it.**
`H9(a)` states that the trained rules' own-replay count is gone: §2.2 row 14 records the pre-pass text
as `L2226-2227 "…reproduce their own replay exactly, **$120$ of $120$**"` and concludes **"All five
lost from all three files (`120 of 120` = 0 hits)"**, and §7 repeats "`120 of 120` now greps to **0**
in all three files". A probe for the LaTeX form `120$ of $120` returns **1 hit in the frozen
round-9 file and 1 hit in the current file** (cross-checked on four states: pre-reattribution 2,
pre-page-recovery 1, pre-`P0` 1, current 1). The §2.1 relocation audit in the *same report* counted
"120/120 trained own-replay" as **carried** among its 16 present elements. So the report contradicts
itself on this item, and the surviving element is the true one. Two knock-on effects: round 9's
Reproducibility deduction of 0.10 (weight-based) rests partly on a loss that did not occur, and
`P0` action 6's "restore the `120 of 120` replay count" was a **no-op** — the count was never missing.
The genuinely lost items in the same row are `10^{-10}` (0 hits in all four states from
pre-page-recovery onward) and `structural endpoint` (0 hits), both of which remain open. Fix:
withdraw `H9(a)` at verdict level and correct the readiness sentence that cites it.

**M-4 — Four of round 9's `closed` rows quote text that is not in round 9's own frozen artifact, so three closure determinations and one "re-verified" label are unfounded as written.**
An independent pass re-checked every `closed` row's deciding quote against `main.tex` `88ECD743…` and
against the file round 9 actually froze (`2FD3CEF2…`), normalising whitespace and searching
whitespace-insensitively. Result: **17 of 21 quotes found in the current text, 4 not**, and the four
failures are of three different kinds.

| row | quoted text | in round-9's frozen file? | in the current file? | what it means |
|---|---|---|---|---|
| `R5-6` | "\eqref{eq:debt_bound} carries debt as a one-sided residual bound, not as a benefit term." | **no** | **no** | the quote exists verbatim **only in `snapshots/2026-10-03-pre-reattribution/main.tex` L1849** — i.e. in the round-8 state, not the round-9 state. Round 9's row says "Unchanged; **re-verified**", but nothing was re-verified: the quote was inherited from round 8 unchanged. The current text (L1854) reads "contribution, whose bound \eqref{eq:debt_bound} is one-sided", which does carry the one-sided reading, so the **closure is substantively intact and the provenance claim is not** |
| `F1` | "Over all $240$ rule runs … at most $0.11\%$ of any of the four `Inst` readings and $2.16\%$, $7.62\%$, $2.73\%$ and $4.89\%$ of the four `debt` readings." | **yes** (`supplemental.tex` L109-112) | **no** | round 9 closed `F1` by declaring this sentence the *replacement* for the withdrawn `6`–`16 %` range, while its own `H3` row calls the same sentence's `Inst` half false. The sentence does not exist in the current file at all: the per-reading form is **gone**, every token (`0.11\%`, `2.16`, `7.62`, `2.73`, `4.89`, `Inst readings`, `debt readings`) returns **0 hits in all three current `.tex` files**, and what stands instead is the `\Delta`-unit bound with its `\times50` conversion and only the `17 % / 0.13 % / 0.16 %` ratios. So the true state is *better* than round 9's row describes — and the row describes a state that no longer exists |
| `F8` | "the distance between a trained rule's server weights and the exact minimizer of its projection problem, **in percentage points of group mass** rather than as a relative tolerance" | **yes** (`supplemental.tex` L106-108) | first clause yes, **quoted unit clause no** | the current text (L108-109) reads "That distance is reported in the $\Delta$ units of the structural endpoints and not as a relative tolerance"; "percentage points of group mass" is **0 hits in all three current files**. `F8`'s verdict (the symbol is defined, with a unit) holds; its quoted wording is stale |
| `F4` | none — the row's quote cell is a meta-assertion, "the '…rather than…, and…, and…' chain is absent" | — | the chain **is** present (L1540-1544) | a genuinely odd row, but the reading is the intended one: the chain *should* be present, because `R5-12` quotes the same lines as present and `F4`'s subject was the *doubled* connectives that are gone. No defect in the paper; wording defect in the report |

Consequence: round 9's closure table presents inherited quotes as re-read ones. For `F2`, which round 9
did repair, the difference is invisible; for `R5-6` it means one of the "re-verified" rows was never
opened. **The verdicts survive** (§5), but the table's authority rests on a verification that did not
happen for at least these rows. Fix: mark inherited quotes as inherited, or re-quote at freeze time.

---

### MODERATE

**A-1 — Three numeric inconsistencies inside the record's own round-10 synchronisation, all now fixed.**
(i) Part V §V.2 and the header both reported the `P0` pass as "**20 inserted / 23 deleted / +5 net**";
measured by the newline convention the rest of the record uses, the file went **2 239 → 2 246 lines,
i.e. +7** (the `+5` came from counting `Compare-Object` change blocks). (ii) The `H3` row asserted
that "the unit identity `1 pp = 0.02` mass is printed with the bound"; no such identity is printed —
`supplemental.tex` L110-111 says `2.42\times10^{-5}` in the `\Delta` units of the structural
endpoints, "equivalently `1.21\times10^{-3}` in the percentage-point convention", and `0.02` occurs
**0 times** in `supplemental.tex`. (iii) §V.3 defect 3 said the four stored-but-unprinted rows are
"in no `.tex` file"; `0.0325` occurs once in `appendix.tex` L1928 (an unrelated `\pm`), so the correct
scope is exactly what the CSV prints — *not in `main.tex` or `supplemental.tex`*. **Applied:**
2 239 → 2 246 and `+7` written in both places, the `H3` row rewritten to the conversion actually
printed, and defect 3 rescoped.

**A-2 — `PAPER_NUMBERS.csv` reports 70 rows as `located` while only 50 carry a value that the named file prints verbatim, and 13 of the 20 others point the reader at the wrong column.**
Measured by exhaustive enumeration (and independently reproduced): of the 70 rows with a `source_file`, **50** contain their `printed_value` verbatim in that file and **20** do not; `source_row_or_key` documents a transformation for only **12** of the 70. The 20 break down as `GAP_DECOMPOSITION.csv` 13, `MYOPIC_DIAG.json` 2, `tables/TABLE_II_WORSTGROUP_PER_SEED.csv` 2, `LADDER_PAIRED.csv` 1, `round_v5_1/ERRATA_FOR_PAPER.md` 1, `round_v5_1a/EXECUTION_REPORT.md` 1. **All 20 are reconstructible and were verified as such**: the `GAP_DECOMPOSITION` rows are the stored `pp_total` / `pp_seg1` columns (the paper's `2.09` is the stored `2.0915537027880617` exactly), its confidence-interval rows are the stored Δ-space `delta_total_ci` / `seg1_ci` under `×50` (`1.87` / `2.31` = `[0.037422…, 0.046145…] × 50`), the `WorstGroupRMSE` rows are 20-seed means, `20/20` is a count of unchanged verdicts, `10^{-13}` is the order of magnitude of a stored `-1.13e-13`, and `0.0337` is a rounding of a stored `0.033694057466112426` (**the stored value rounds to `0.03369`, not to the printed `0.0337` — a rounding-presentation, not a data, discrepancy**). So `located` is true in substance, but it does double duty for *printed at this row* and *computed from this row*, and in 13 cases the row key names an intermediate cell rather than the column that already holds the endpoint value — `GAP_DECOMPOSITION.csv` has `pp_total`, `pp_seg1`, `pp_seg2` columns, so `2.09` needs no arithmetic at all and the key still sends the reader to the Δ cell. Fix: split the status into `located` and `derived_from`, and point each row at the column that carries it.

**A-3 — A bundled source is declared absent while it is present, byte-identically.**
`PAPER_NUMBERS.csv` rows 1-2 (printed `3.44`, `1.32` pp) assert that the only file stating them,
`results_w1_ladder/round_v2/PHASE3_REPORT.md`, "is NOT in the protocol's artifact list and was not
copied". That file **is** in the bundle at `w1/frontier/PHASE3_REPORT.md` — 13 599 bytes, sha256
`1D1C39F75098BE6AA862F888B8260F4E44166ED441CE9CE4C2FD6F80971F8281`, identical to the working-tree
original copied on 2026-10-02 17:45 — and it contains both values on **line 77**
(`(Δ_unif − Δ*)/2 = 3.44 pp` and `可回收 **1.32 pp**`). The rows therefore need the source filled in
and the sentence rewritten, not merely a status flip. **Applied** to the record: §V.3 defect 1 now
records the bundled path and hash, and the correction block says the same.

**A-4 — Six `UNLOCATED` rows are not unlocatable; their conversion is printed in the paper.**
The rows for `1.84e-2`, `1.54e-2`, `1.46e-4` and the ratios `17 %`, `0.13 %`, `0.16 %` are marked
`UNLOCATED` because "no bundle file stores" the `Δ`-unit readings. True as stated — and misleading,
because the conversion factor is the paper's own definition (`main.tex` L604, `pp = Δ/2 × 100`, i.e.
`×50`), so the six values are reconstructible from the published text plus the stored readings. They
are a labelling gap in the M7 instruction, not missing evidence. **Applied** to the record: §V.3 now
says the conversion is printed and that these rows should be `derived`, not `UNLOCATED`.

**A-5 — The bundle refresh met its purpose but the record keeps describing it more narrowly than what was accepted.**
The bundle contains **214 payload files under `w1/` plus 2 index files = 216**, and the added set is
**217** files because it includes the rebuilt root `MANIFEST.csv`; Part V and correction item 42 both
said "217 files / 2 921 397 bytes added **under `w1/`**", which is true of 216 of them. Separately,
the M7 protocol required the refresh's own report to list the unlocated rows verbatim and to record
`G-M7-1…4`; the bundle carries no such report file — the gates and the unlocated list exist only in
the diagnosis record and in the round-9 review. **Applied:** the count is now stated as
"216 under `w1/` plus the rebuilt `MANIFEST.csv`" in the header and in item 42. **Open:** the
gate report has no artifact of its own.

**A-6 — Round 9's closure-count arithmetic does not close, and the diagnosis record copied the wrong number.**
Round 9's §6 table contains **21** rows whose status cell says `closed` (`R5-1`, `R5-2`, `R5-3`, `R5-4`,
`R5-6`, `R5-7`, `R5-8`, `R5-9`, `R5-10`, `R5-11`, `R5-12`, `R5-14`, `F1`, `F2`, `F3`, `F4`, `F5`, `F6`,
`F7`, `F8`, `F9`), while its own §6 summary line reads "**20 closed**" and then lists the same **21**
IDs — `F4` is in the list but outside the count. The diagnosis record's Part V §V.1 reproduced "20
closed" in its scorecard row without re-counting. One of the two is wrong; on the table's own evidence
the count is 21 (or 20 with `F4`, which was already closed at round 8, excluded from the "new" tally).
**Applied:** §V.1 now records the discrepancy instead of asserting the number.

**A-7 — The five "major axes" of the paper's evidence base are on disk with no hash manifest and no version control.**
Tied to M-2 but separable and actionable on its own: `results_w1_ladder`, `results_gatekeeping` and
`results_exogenous_target` total **2 582 files / 42.9 MB** with per-round `EXECUTION_REPORT.md`
narratives but no top-level hash inventory. The bundle covers the paper-facing subset (214 files) and
hash-lists a further 610 files, which leaves roughly **1 750 evidence files reachable only through
the working tree**. Fix: emit one `MANIFEST.sha256` per round tree, or extend `EXCLUDED_HASHES.csv`
to the remainder.

**A-8 — The feasibility-violation range at L1835 is sourced, and the source mislabels it: `8.23` and `21.73` are the `raven_wo_design` and `raven_simoracle` arms, not "the uncorrected reference", whose own value on that block is `16.81`.**
Round 9 left `main.tex` L1835's "violates the recorded feasibility constraints by $8.23$ to $21.73$" as
*unverified*, and a later independent reader (the 2026-10-04 review in `raven-mcs-tmc-review.md`)
carried that status forward. The tokens do exist, exactly twice in the repository's evidence:
`results_w1_ladder/round_v3/EXECUTION_REPORT.md` **L62** (`raven_wo_design … 8.23`) and **L63**
(`raven_simoracle … 21.73`) — the last column of that report's B0 table, which the `PAPER_NUMBERS.csv`
rows for `main.tex,1835` also cite (`w1/ladder_v3/EXECUTION_REPORT.md` L62-63). So the figure is
located, and what it is is a **range across arms**: the low end is the design-off arm and the high end
is the oracle arm. The arms in between are `raven` **16.81** (the arm the sentence is actually about),
`raven_wo_obs` 15.36, `raven_wo_use` 16.01 and `count` 5.97, against `uniform` 0. Measured against the
companion per-seed artifact, the block means are `raven` 16.68, `raven_simoracle` 22.11,
`raven_wo_obs` 15.38, `raven_wo_use` 15.70, `raven_wo_design` 7.84, `count` 5.62, `uniform` 0; the
cross-arm span is `[7.84, 22.11]` and the `raven ∪ raven_simoracle` span is `[11.55, 21.44]`, so no
single-arm reading reproduces `8.23`–`21.73` either. The parenthetical needs one of two wording
repairs: name the arms ("across the design-free and oracle variants, 8.23 to 21.73"), or give the
reference's own value. As printed it attaches the two most extreme arms in the table — one of them the
design-off baseline — to a subject that is neither. | `round_v3/EXECUTION_REPORT.md` L59-66;
`round_v3/SOURCE_LADDER.csv` (`outside_Cr_l1`, sensorscope/`B0`); `w1/PAPER_NUMBERS.csv` L37-38;
`main.tex` L1834-1836

## 4. Minor observations (recorded, not scored)

| # | observation |
|---|---|
| m-1 | `snapshots/2026-10-03-pre-page-recovery/` and `snapshots/2026-10-04-pre-p0-fix/` are byte-identical; two rollback points, one state. Harmless, but a future rollback would gain nothing from the older one. |
| m-2 | The diagnosis record's header still quotes `main.tex` at "2 242 lines" from the round-7/8 pass while the same header now documents the `P0` pass; the two are consistent in sequence but a reader scanning only the header sees two line counts with no pointer from the older one to the newer. |
| m-3 | `BUNDLE_SUMMARY.json` `total_bytes` is exactly `MANIFEST.csv` short (291 056 B) and `file_count` is 2 117 against 2 118 files on disk; §V.3 now shows the arithmetic closes once the describing files are excluded, so this is a convention rather than a defect. |
| m-4 | The M7 protocol's §8 item 4 (`main.tex` L2211-2221 naming `w1/`) remains **unauthorised**; recorded in §V.3 and still the cheapest available improvement to the availability paragraph. |
| m-5 | Two scratch trees are untracked and undeclared: `.m7_work/` (44 files, the refresh's scripts and intermediate inventories) and `.sync_diag/` (the round-10 fix scripts plus two pre-edit copies of this record). Neither is in the bundle or in git. |
| m-6 | The paper's `appendix.tex` and the bundled `w1/frontier/PHASE3_REPORT.md` both carry the pre-existing `Local-Hajek 1.1923` vs θ-canonical `1.19349` divergence, unchanged since 2026-10-02 and never in an authorised edit set. |
| m-7 | **Round 9 contradicts itself on the same element, and its §2.1 sentence is the true one.** §2.1 (L97) says "All sixteen named elements are present; nothing was dropped in the move", while §2.2 row 14 and §7 `H9(a)` say the `120 of 120` count was lost. The count is present (§3 M-3), so §2.1 is right and `H9(a)` is wrong — but §14's self-check item 6 then repeats the false version ("3 of them … degraded rather than carried"). Two of the three are genuinely degraded (`10^{-10}`, `structural endpoint`), so `H9` survives with two sub-findings instead of three, and `H9`'s headline should be renumbered. |
| m-8 | **The rollback corpus is not uniform, so some snapshots cannot restore the whole submission.** Of sixteen snapshot directories, only eight carry `main.tex`; `2026-10-03-pre-reattribution` (the version round 9 measured against) carries `main.tex` **and compiled artifacts** (`main.aux`, `main.log`, `main.pdf`) but **no `supplemental.tex`**, and `2026-10-03-pre-appendix-resourcing` carries only `appendix.tex`. `2026-10-04-pre-p0-fix` is complete for the `P0` pass (`main.tex` + `supplemental.tex`), which is the pass that matters most; the gap is in the older points. |

---

## 5. Closure re-validation — round 9's `closed` rows against the current file

The check M-1 calls for, run on `88ECD743…`. Two columns, because the two questions are different:
whether the **verdict** still holds (my own pass, reading each site), and whether **round 9's deciding
quote** can still be found (an independent pass, exact quotes, whitespace-insensitive).

| issue | verdict still holds in the current file | round 9's deciding quote still present |
|---|---|---|
| `R5-1` | yes — "are not shown to contribute at the frozen configuration" (L1843) | yes |
| `R5-2` | yes — "practical-significance convention rather than a hypothesis test" (L612-614) | yes |
| `R5-3` | yes — "`3.44` pp … and `1.32` pp on U-Air" (L608) | yes |
| `R5-4` | yes — "reported as exploratory" (L2090 and L2241) | yes |
| `R5-6` | **yes, in different words** — "whose bound \eqref{eq:debt_bound} is one-sided" (L1854) | **NO** — round 9's quote exists only in the round-8 state (`pre-reattribution` L1849) (M-4) |
| `R5-7` | yes — "does not amplify" (L224) | yes |
| `R5-8` | yes — "Imposing $\mathcal{C}_r$ and projecting onto it" (L1833) | yes |
| `R5-9` | yes — the unsupported "oracle values" clause still absent | yes |
| `R5-10` | yes — "the design factor costs" (L2042/L2048) | yes |
| `R5-11` | yes — "$+0.922$ pp", and `1.24` absent (L81) | yes |
| `R5-12` | yes — the construction sentence, no doubled connectives (L1540) | yes |
| `R5-14` | yes — "outside the $\pm0.10$ band in the same units" (L1838) | yes |
| `F1` | **yes, and more strongly than round 9 says** — the withdrawn `6`–`16 %` range *and* the per-reading form are both absent from all three files; what stands is the `\Delta`-unit bound with its `\times50` conversion (L109-117) | **NO** — round 9 quotes the per-reading sentence at `supplemental.tex` L109-114, which is verbatim in **round 9's own frozen file** and absent from the current one (M-4) |
| `F2` | yes — "not numerically stable" absent, two frames named (L2227) | yes |
| `F3` | yes — abstract ruler restored (L81) | yes |
| `F4` | yes — doubled connectives absent (L1540-1544) | n/a — the row carries no verbatim quote (M-4) |
| `F5` | yes — the scoped prediction-half sentence, grammatical (L235) | yes |
| `F6` | yes — "ladder" a single hit, qualifier retained (L2088) | yes |
| `F7` | yes — `sanity check`, `No test result tunes`, `does not provide a privacy`, `no best worst-group` each 1 hit (L1641) | yes |
| `F8` | **yes, in different words** — `\varepsilon_{\mathrm{impl}}` is defined with a unit; the unit is now the `\Delta` one (L106-109) | **NO** — round 9 quotes "percentage points of group mass", absent from all three current files and from the current supplement (M-4) |
| `F9` | yes — "are not mixed into that development table" (L235) | yes |

**Result: no closure was undone by the `P0` pass — 21 of 21 verdicts hold.** But **my first pass at this
table was wrong on three rows** (`R5-6`, `F1`, `F8`): I substituted a present string I had grepped
myself for round 9's quoted string, and so recorded "yes" where the exact quote is absent. The
independent pass, searching round 9's quotations verbatim, returned **17 of 21 found**. Both statements
are true and they answer different questions: the *verdicts* are intact, the *quotations* are not, and
three of them were never in round 9's frozen file to begin with. Combined with the structural counts
in §1, the version split of M-1 is a **record-keeping** defect, not a substantive one — and M-4 shows
the same weakness predates the split.

---

## 6. Corrections applied to the diagnosis record during this audit

`ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md`, from `1B2DB470…` (2 571 lines,
276 821 B) to the state recorded in the header: A-1 (three numeric fixes), A-3 and A-4 (§V.3 defect 1
and defect 2 rewritten), A-5 (count wording in the header and in item 42), **A-6 (§V.1's closure count
now records the 21-vs-20 discrepancy instead of asserting the number)**, M-1 (a pointer to this report
and to the re-validation in §5), plus §V.3's defect list going from three items to four and its
heading with it. Backups of both pre-edit states are in `.sync_diag/`.

**Not applied, because they are manuscript or repository actions and need their own authorisation:**
the `main.tex` L2211-2221 `w1/` pointer (m-4); any git commit (M-2, A-7); the `PAPER_NUMBERS.csv`
status split and the two false rows (A-2, A-3); `H9(a)`'s withdrawal and the stale quotes of `R5-6`,
`F1` and `F8` in the round-9 report (M-3, M-4); and the deletion of the scratch trees (m-5).

---

## 7. Checks run, checks skipped, unresolved risks

```text
Checks run: sha256 + mtime freeze/re-freeze of 8 artifacts; structural counts of the current
main.tex (tables/figures/equations/citations/sections/subsections/propositions/theorems/labels,
em dashes, semicolons, words) and page counts from both logs; byte-identity audit of all 214 bundled
payload files against their working-tree sources by path (0 mismatches), independently repeated by a
second pass that enumerated all 217 files under w1/ and cross-checked the totals; re-run of the
bundle's own verify.py (checked=2116 mismatches=0); row-level audit of all 83 PAPER_NUMBERS.csv rows
(verbatim substring test of printed_value in the named file; source resolvability; source_sha256 on
all 70 sourced rows, 0 mismatches); MANIFEST.csv / MANIFEST_ADDITIONS.csv / EXCLUDED_HASHES.csv row and
byte reconciliation including the MANIFEST self-exclusion arithmetic and a sha256 re-verification of
all 610 excluded files; git ls-files versus disk for seven trees; the H9(a) probe
and the R5-6 / F1 / F8 quote probes on four to eight file states; closure re-validation of round 9's
closed rows, done twice with different methods (verdict-reading and exact-quote matching); and four
content assertions re-measured rather than assumed: the README's "no checkpoints, no training scripts"
promise (the 217 files under `w1/` are 132 `.json`, 56 `.csv`, 22 `.md`, 7 `.sha256` - nothing else),
the classification of the 610 excluded files (exactly five basenames, 122 each: `final.pt`,
`atomic_rho_v2.parquet`, `pair_state.parquet`, `delta_cs_state_v6.parquet`, `window_metrics.json`),
a copy-provenance spot check of six bundled artifacts against their working-tree sources (6/6
identical) plus a sampled `round_v4` run file, and a scan of the whole shipped bundle for the
withdrawn `F1` per-reading wording (0 files carry it; the one apparent hit is an unrelated
`0.04 %-0.11 %` power range in `round_v5/ERRATA_FOR_PAPER.md`).
Checks skipped: no experiment, build, or bundle write; no line-by-line proof reading of appendix.tex;
no re-derivation of the paper's statistics; the round-7 and earlier reports were not re-audited (only
rounds 8-9 and the records around them); the round-v1 evidence tree, which publishes no paper number,
was not opened.
Unresolved risks: (i) whether any earlier review round also audited a version that a later pass
superseded - only round 8 -> 9 and 9 -> P0 were checked here, although M-4 shows the same failure mode
already existed at round 9; (ii) the byte-level provenance of the compiled PDFs, which are untracked
and therefore unverifiable against any committed state; (iii) whether the round-8 report carries
stale quotes of its own - its `R5-6` quote is the one round 9 inherited, so the practice may predate
round 9 and was not traced further back.
Closed during this audit: the third risk carried by rounds 9-10 was whether the 610 hash-listed
excluded files still match their recorded hashes. Measured: all **610** `source_path` entries resolve
inside the working tree, with **0** byte-count mismatches and **0** sha256 mismatches, and none is
present under the bundle root - i.e. `EXCLUDED_HASHES.csv` is a truthful "hash-listed but not
redistributed" record. (Its `bundle_destination` column is the constant string `not redistributed`
on all 610 rows, which duplicates the `reason` column rather than naming a path; a convention, not a
defect, but the column name promises a destination it never gives.)
```

---

## 8. Cross-check against the independent 2026-10-04 review

A second reviewer (Grok, output kept at `ccfa-review-reports/raven-mcs-tmc-review.md`) reviewed the
**same frozen manuscript**: its header names `sha256 prefix 88ECD743…, 2026-10-04 10:06`, which is the
current `main.tex` to the digit. It is a submission review, not a record audit, so the two documents
answer different questions; where they overlap, the comparison is:

| item | this audit | the independent review | agreement |
|---|---|---|---|
| frozen object | `88ECD743…`, 10:06:17, 113 379 B | `88ECD743…`, 10:06 | same file, same minute |
| weighted readiness | 3.25 / 5-10 (inherited from round 9) | 3.25 / 5-10, `unchanged` | **agree** |
| dimension profile | Soundness 5, Evidence 3, Clarity 4, Reproducibility 2 | identical, including the 2s | **agree** |
| the decisive axis | Evidence (0.25), no Holm-surviving prediction endpoint | `E1`, same axis, "the only action that can move 5→6" | **agree** |
| the named program is not what moves the endpoint | `H2` fix + Part IV attribution; now printed | `E2`, "major for venue fit, not a correctness error" | **agree**, and it reads the same three sites (L229-237, L247-255, L1826-1856) |
| the bundle | `M7` closed by the round-10 audit; `w1/` present, verifier clean | cites the round-10 audit for exactly this, and asks only for the availability paragraph to name `w1/` | **agree** |
| what it could not see | M-1 (version split), M-3 (`H9(a)` false), M-4 (inherited quotes), A-2/A-8 | not addressed; outside a submission review's scope | complementary, not contradictory |
| `8.23`-`21.73` | **located** (A-8): the `raven_wo_design` / `raven_simoracle` table cells, mislabelled | "not re-located this pass … stays unverified" | **this audit is further on**, and its finding is that the sentence needs a wording repair |
| Reproducibility raise | its own condition (`F10` cleared) is **not** met, so the raise is not yet earned | "Name that subtree … **+1 Reproducibility**" | **disagreement** (see below) |
| `C1` / `C2` free space | open: Proposition 4's unused clause, ~40 lines of coverage-Gate apparatus | not raised | this audit adds two open items |
| page track | not assessed | 17 pp fits an 18 pp MOPC allowance and exceeds 12 pp regular; the track must be declared | the independent review adds a real submission risk |
| "recoverable" | `R5-16`, the one open issue blocking Terminology | `M1`, same two sites (L1819 vs L2106), same fix | **agree**, identical diagnosis |

**The one substantive disagreement is the Reproducibility step.** The independent review grants
`2 → 3` on the bundle repair alone. This record has held, through rounds 8-10, that the dimension's
raise condition is the conjunction that was used to make the deduction — `M7` **and** `F10` — so
clearing `M7` while `F10` (five multiply-defined citation labels plus the supplemental
`Overfull \vbox`) is still open earns half a step, not a step. Which reading is right is a scoring
convention, not a fact, and the two reviews should not be averaged: the honest statement is
**3.25 with `M7` closed, and 3.35 if `F10` is also cleared**. `F10`'s five labels are
`wang2023cityscanner`, `wang2024lightweight`, `wang2026federated`, `morishita2026who` and
`goetze2025floss` — all five are cite keys that appear in **both** `main.bbl` (54 bibitems) and
`supplemental.bbl` (5 bibitems), which is a two-driver artefact rather than a defect in either source
file, and it is mechanical.


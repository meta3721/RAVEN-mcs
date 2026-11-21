"""Write the TMC rule-verification record and append the round's addendum to the repair report."""
from __future__ import annotations

import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "ccf-review-report"

VER = """# TMC submission-rule verification

Verification date: **2026-10-17** (all fetches on this date). Purpose: re-check the current official IEEE
Computer Society / IEEE TMC requirements, because the previous review recorded an unresolved 403 and the
repair round had to report the page and author rules as unverified.

## Sources actually retrieved

| # | URL | HTTP | usable |
|---|---|---|---|
| 1 | https://www.computer.org/publications/author-resources | 200 | **yes**, full policy text for CS journals |
| 2 | https://www.computer.org/csdl/journal/tm/write-for-us/15075 | 200 | **no**: returns only the CSDL shell; content is client-rendered |
| 3 | https://www.computer.org/csdl/journal/tm | 200 | **no**: shell only |
| 4 | https://mc.manuscriptcentral.com/tmc-cs | **403** | no: Cloudflare interstitial ("Just a moment…") |
| 5 | https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=1564003 | 200 | **no**: Xplore shell, no full text |
| 6 | https://journals.ieeeauthorcenter.ieee.org/ | 200 | partly: navigation only, no per-journal limits |
| 7 | https://www.computer.org/publications/publishing-services | 200 | **no**: page not found |
| 8 | https://www.computer.org/publications/author-resources/calls-for-papers | 200 | not relevant to limits |

Excluded by policy: search hits at `aje.cn`, `csdn.net`, a 2008-era TMC front-matter PDF, and a path
containing a Sci-Hub-derived archive name. **No historical TMC rule and no other journal's rule was used as
if it were the current TMC rule**, per the instruction.

## Verified rules (source 1, CS policy for journals)

| rule | official statement (paraphrased closely) | applies to this paper | paper status |
|---|---|---|---|
| Page accounting | "All page limits include abstracts, references, and author biographies." | yes | 14 pp **includes** the bibliography; there are no author biographies |
| Abstract length | Journal regular/special-issue paper: **100 to 200 words** | yes | **176 words** measured from the abstract block: compliant |
| Abstract content | must state nature and significance; no mathematical expressions or bibliographic references | yes | abstract contains no equations and no citations: compliant |
| Supplemental material | "must be submitted as separate files and must not be included within the same PDF file as the main paper submission" | yes | `supplemental.pdf` is a separate file; no supplemental content sits inside `main.pdf`: compliant |
| File-size cap | manuscript files and supplemental files may not exceed **350 MB** | yes | main 866 KB, supplemental 1.27 MB: compliant |
| Author biographies | journals: "not required, and there is not a specific style format" | yes | none present: compliant either way |
| Template | "Using an article template is required for journal submissions"; LaTeX must pass the IEEE LaTeX Analyzer | yes | `\\documentclass[letterpaper,journal]{IEEEtran}` | 
| Column format | double-column preferred; a double-column page is 7.875 x 10.75 in with 9.5-pt type and 11.5-pt leading | yes | two-column `journal` class, US Letter (612 x 792 pt) for submission |
| Overlength charges | a Mandatory Overlength Page Charge (MOPC) policy applies to journals | yes | policy existence verified; **the per-journal free-page count was not captured** (section truncated) |

Two follow-ups that the same page names but that were not completed here: the IEEE LaTeX Analyzer run
(`latexqc.ieee.org`) and the double-anonymous-review section, which is present on the page but whose
applicability to TMC was not established.

## Not verified - reported as unverified, not substituted

1. **TMC's current page limit for a regular paper.** The only official location for it is the TMC
   "Author Information / Write for us" page (source 2), which this fetch cannot render, and the TMC
   submission site (source 4) returns 403. **Therefore "14 pages" is the user's budget and the delivered
   count, not a verified TMC limit.**
2. **The TMC free-page count under the MOPC policy**, and the per-page charge.
3. **TMC's review model** (single- vs double-anonymous) and whether an anonymised or full-author version is
   required at submission.
4. **TMC-specific supplemental-material rules** beyond the CS general policy.

## Consequence, stated as a risk rather than resolved

- If the current TMC regular-paper limit is **14 pages or more**, the delivered body is within it and no
  overlength charge arises at 14.
- If the current limit is **lower than 14**, the body is over and the author must decide between compression
  and accepting overlength charges.
- If the limit is higher and the free allocation is larger, the paper has unused room but no violation.

This round does **not** choose among these, because none is verified. The correct action before submission is
to open the TMC author page in a browser session (or the ScholarOne submission form, which states the limit)
and record the figure and its date in this file.

## Author-information status (S5, unchanged)

The block is still a mixed placeholder/real state and cannot be called submission-ready:

| field | current text | state |
|---|---|---|
| first author name | `****` (main.tex L61) and `***` (L63) | placeholder |
| first author e-mail | `****@csu.edu.cn` (L63) | placeholder |
| second author | `Anfeng Liu`, `afengliu@mail.csu.edu.cn` | real |
| affiliation | School of Electronic Information, Central South University, Changsha 410083, China | real |
| funding note | NSFC U24A20248 | real |

Filling these needs authoritative identity information from the author; guessing is prohibited by the
instruction.
"""
(OUT / "TMC_RULE_VERIFICATION_20261017.md").write_text(VER, encoding="utf-8")
print("wrote TMC_RULE_VERIFICATION_20261017.md",
      (OUT / "TMC_RULE_VERIFICATION_20261017.md").stat().st_size, "B")

ADD = """

---

## Addendum: the tree moved again during the verification round (2026-10-17, ~16:50-16:52)

While this round was re-checking the TMC rules, both sources changed on disk without any write from this
session. Recorded so the status above is read against the right files.

| file | after this round's repairs | now |
|---|---|---|
| `main.tex` | 86379 B, `55742929` | **89404 B, `3C936D22`** (mtime 16:50) |
| `appendix.tex` | 92523 B, `180421A6` | **91776 B, `3602168D`** (mtime 16:52) |
| `main.pdf` | 854153 B, `7CA83766` | **866197 B, `DE613014`** |
| `supplemental.pdf` | 1270723 B, `165F4702` | **1272081 B, `AC300A97`** |
| `figure_data/FIG_E3_E3_PREDICTION_RISK.csv` | 53593 B, `91E49822` | unchanged, `91E49822` |

Survival of this round's repairs in the new text:

| repair | marker | survives |
|---|---|---|
| S2 condition mapping | `rests on A1--A3` | **yes** |
| S2 closing clause | `does not establish the clauses it does not check` | **no**, rewritten by the external edit |
| S4 terminology | `The support rule sets Design on exactly when` | **yes** |
| S1 Fig. 5 identity | `supports no same-support claim of its own` | **yes** |
| S1 Table XVIII identity | `current-runner re-run that keeps every delivered client` | **yes** |
| S1 Fig. 6 pointer | `Row identities are those stated in` | **yes** |
| S3 availability entry | `SUBMISSION\\_EVIDENCE\\_INDEX.md` | **yes** |

Rebuild of the new source: `main.pdf` **14 pages**, 0 errors, 0 undefined references, 0 Overfull; the
supplement builds after main with 0 undefined references. The page budget therefore still holds, but it holds
for a text this round did not fully author, so the S1-S4 statuses above should be re-confirmed against
`3C936D22` before submission.

Unresolved by the external edit: the three author placeholders are still present (`****`, `***`,
`****@csu.edu.cn`), so S5 remains open.
"""
R = OUT / "PAPER_SUBMISSION_REPAIR_REPORT.md"
t = R.read_text(encoding="utf-8")
if "the tree moved again during the verification round" not in t:
    R.write_text(t.rstrip("\n") + ADD + "\n", encoding="utf-8")
    print("addendum appended to PAPER_SUBMISSION_REPAIR_REPORT.md", R.stat().st_size, "B")
else:
    print("addendum already present")

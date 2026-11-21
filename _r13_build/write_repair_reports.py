"""Write the two submission-repair deliverables and append the S1 resolution to the pending-items file."""
from __future__ import annotations

import hashlib
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "ccf-review-report"
OUT.mkdir(parents=True, exist_ok=True)

REPORT = """# PAPER_SUBMISSION_REPAIR_REPORT

Instruction: `C:/Users/szr/Desktop/record/1/ccfa-review-reports/paper-submission-repair-instructions.md`.
Review used as the locating clue: `C:/Users/szr/Desktop/record/1/ccfa-review-reports/submission-readiness-review.md`.
Skills applied: `ccf-integrity-auditor` (S1/S2 number and method identity), `ccf-paper-writer` (text),
`ccf-submission-checker` (compile and materials), `ccf-visual-composer` (figure redraw from the certified
CSV).

## Authorization actually exercised

Read existing configs, logs, CSVs and saved summaries; computed means of existing CSVs; edited the three
TeX sources, one figure-data CSV and the figure it feeds; compiled both PDFs; organised small delivery
materials. **No training, no model inference, no checkpoint loading, no trace replay, no re-scoring, no new
statistical test, no new experiment, no upload.** Single process, small files only.

## Baseline recorded before any edit

| item | value |
|---|---|
| body / supplement pages | **14 / 14** (both shipped PDFs) |
| compile state | 0 errors, 0 undefined, 0 multiply-defined, 0 Overfull |
| body tables / appendix tables | 7 / 23 kept (verified by the review; not re-counted here) |
| author block | `\\author{**** and Anfeng Liu`; email `****@csu.edu.cn`; a third `***` in the second thanks |
| sources | `main.tex`, `appendix.tex`, `supplemental.tex` (+`reference.bib`, `.bbl` files) |
| version control for rollback | `tmp/remaining_compress/*.before` untouched; this round's before-hashes are in the diff file |

## S1 - U-Air cross-figure/table support and scoring identity: **partial**

**What was wrong, established from existing records only.** The review's discrepancy is real and is not a
single bad cell. Per-method 20-seed means in `figure_data/FIG_E3_E3_PREDICTION_RISK.csv` against
`appendix.tex` Table XVIII, all methods and both endpoints:

| method | figure `RMSE_mu` | Table XVIII | figure `Delta_group` | Table XVIII |
|---|---:|---:|---:|---:|
| FedAvg-Window | 1.178988 | 1.1119 | 1.121762 | 1.0446 |
| FedAsync-Window | 1.179098 | 1.1119 | 1.122289 | 1.0451 |
| TimeAlign-Agg | 1.179107 | 1.1120 | 1.121775 | 1.0448 |
| Debt-Cal | 1.180413 | 1.1144 | - | 1.0175 |
| Local-Hajek | 1.192251 | 1.1923 | 1.121762 | 1.1218 |
| TwoStage-Hajek | 1.220198 | 1.2202 | 1.119606 | 1.1196 |
| Inst-Cal | 1.195374 | 1.1954 | - | 1.0924 |
| RAVEN-Design | 1.195366 | 1.1954 | 1.092362 | 1.0924 |
| RAVEN-SimOracle | 1.195830 | 1.1958 | - | 1.0922 |
| Central-All | 1.055571 | 1.0556 | - | - |
| Central-Delivered | 1.178155 | 1.1782 | - | - |

Seven of eleven rows agree to every printed digit. Exactly four disagree, and they are the four arms whose
theta re-score the earlier audit had to measure at all.

**Two distinct causes, both documented.**

1. **Stale scoring (an error, now fixed).** In the figure CSV the four arms' `RMSE_mu` was still the
   pre-theta value on seeds 30007/30016/30018. Substituting the certified theta values from
   `results_seed_path_audit_r1/C7_E3_ARMS_THETA.csv` moves the FedAvg mean from `1.178988` to `1.192251`,
   which is **identical to Local-Hajek's theta mean `1.192251`** and matches
   `results_w1_ladder/round_v5_1/ERRATA_FOR_PAPER.md` E-v51-4 (`fedavg_window` `1.18824 -> 1.19225`)
   independently. The four arms' `Tail_RMSE` was already theta and was left untouched.
   **Applied:** 12 cells in `figure_data/FIG_E3_E3_PREDICTION_RISK.csv` (`27b9046 -> 91e49822`, byte length
   unchanged, EOL preserved), then `make_figures.fig4_prediction()` regenerated only
   `figures/fig4_e3_prediction_risk.pdf/.png` (`3788538 -> 42d3efe` and `f5ab06d -> 0ef749b`).
2. **Different active-set support (not an error; now labelled).** `scripts/audit_table2_uair_fedavg.py`'s
   own record states that the frozen U-Air FedAvg runs **drop** clients with `pi_tar = 0` while FedAU,
   ObsUse and RAVEN-NoDesign **keep** them, and that `fedavg_window_current` is a **current-runner re-run
   that keeps every delivered client** (`results_table2_audit`: `1.1923` for the frozen arm against
   `1.1119` for the current one; `raven` is `+0.26 %` against the frozen arm and `+7.5 %` against the
   current one). Table XVIII's caption already declared the mixed support. **The two exhibits are
   therefore two different comparisons, and the figure must not carry the same-support conclusion.**
   **Applied (captions only, no numbers):** Table XVIII's caption now states that its FedAvg row is the
   current-runner re-run and names the two figures as the different comparison; Fig. 5's caption now states
   that its rows are the frozen run set, that some active sets differ from Table XVIII's, and that the
   figure supports no same-support claim of its own; Fig. 6's caption points at Fig. 5's identity statement.

**Passing condition, honestly assessed.** "Same-identity data consistent": satisfied for the theta scoring
and for the seven rows that already agreed. "Different identities explicitly marked": satisfied by the three
captions. "The unverified exhibit no longer carries the comparative conclusion": satisfied, since the
U-Air comparison now rests on Table XVIII and Table IV.

**Still open (not closable from records, and not guessed).** The per-arm support documentation exists only
for `fedavg_window`. For `fedasync_window`, `flamf_timealign_adapted` and `debt_cal` there is no saved
record stating which active set their frozen runs used, so the two exhibits **cannot be unified** without a
re-run, which this round was not authorized to do. Required record: one line per arm naming the active-set
rule used by its frozen run (whether `pi_tar = 0` clients were dropped). Options for the author: keep the
labelled dual presentation as delivered; or authorize a current-runner re-run of those three arms so the
figure can be unified to Table XVIII; or remove Figs. 5-6 entirely, since both of their conclusions are
fully retained by certified tables.

## S2 - Appendix H's summary of the theorem conditions: **resolved**

`appendix.tex` said `the reconstruction results follow from A5 alone`. The propositions say otherwise:
`prop:reconstruction` is "Under A1--A3" (main.tex:992) and `prop:practical_plugin` is "Assume A1, A4, A5,
and A6b" plus a positive stabilized window mass at the true margins and a shared
`\\mathcal{A}_r, M_r, \\mathcal{C}_r` (main.tex:1059-1062). Replaced with a statement that assigns A1--A3 to
the ideal reconstruction, A1/A4/A5/A6b plus the shared-state and positive-mass conditions to the
perturbation form, A6a to the sharp form, and says explicitly that the section audits A5, A6a and A6b only
and does not establish the clauses it does not check. No theorem, proof, or assumption strength was
changed, and no clause was weakened to match the appendix.

## S3 - Reviewer-facing evidence entry: **resolved within the delivery's limits**

`main.tex`'s Data and Code Availability now names a concrete entry,
`\\texttt{submission\\_evidence/}\\allowbreak\\texttt{SUBMISSION\\_EVIDENCE\\_INDEX.md}`, instead of pointing
at an undefined "revision evidence record". There is **one** index: 16 files in
`RAVEN_MCS_PUBLIC_REPRO_R1/submission_evidence/`, plus a single pointer line added to the bundle README so
no second, conflicting list exists. Each index row carries paper location, quantity, unit, protocol or
comparator, file path relative to the working tree, key or line, scoring identity, and access status, using
exactly four statuses: `packaged`, `local-only`, `public`, and (for the unverified item) the report-level
caveat. No C-drive path is presented as something a reviewer would open.

| paper location | index coverage |
|---|---|
| Table IV and the corrected W1 prediction values | `W1_TRADEOFF_V51.csv`, theta-canonical |
| independent projection and the `kappa=1000` variant | `W1_A1P_IMPL_RERUN.csv`, `approximate`, `eps_impl <= 2.42e-05` |
| concentration (Table VI) | `TE2_CONCENTRATION_STEP3/STEP4.json`, `TE2_FROZEN_PREREG.json`, `TE2_MAIN.csv` |
| Adam sensitivity | `TE1_ADAM_VERDICT.json`, `TE1_CONFIRM.csv`, `TS1_STRUCT_SUMMARY.json`, `TS1_PAIRS.csv` |
| learning and development geometry (Table VII, appendix XXIX-XXX, Fig. 8) | `results_main_rebuild_r1/`, status `local-only` |
| `3.44` / `1.32` pp still used in Sec. V | `W1_PHASE3_REPORT_round_v2.md` line 77, **report-level only** |

**Not claimed:** that anything local was made public or uploaded; that the learning/geometry material is
bundled; that `3.44/1.32` pp were recomputed from raw values. They remain `UNLOCATED` in
`w1/PAPER_NUMBERS.csv`, and the index says so in its "open items" section.

## S4 - Design/Gate terminology: **resolved**

`appendix.tex`'s Table XXVI caption called the offline rule "the gate". Changed to "the support rule", which
is the term the caption's own first sentence already used. No code, no method identity, no algorithm, and no
`Design:=Gate` semantics were touched; the historical coverage-controlled candidate is unaffected.

## S5 - Author block and official rules: **unresolved, reported not patched**

Three placeholders remain and were **not** filled, because no authoritative identity information exists in
the project's materials and the instruction forbids guessing:

| field | current | needed |
|---|---|---|
| first author name | `****` (also `***` in the second thanks) | the real name |
| first author e-mail | `****@csu.edu.cn` | the real address |
| author order and affiliation | `Anfeng Liu`, School of Electronic Information, Central South University, Changsha 410083, China | confirmation, plus any further authors |

The block is a mixed placeholder/real state and is therefore **not a finished submission file**.

**Official-rule verification: not closed.** The Computer Society author resources page
(`https://www.computer.org/publications/author-resources`) was the checkable entry recorded by the review
and returned 403 to that review; this round did not obtain a reliable current statement of the TMC regular
paper type, page limit, reference/biography counting, supplemental-material policy, or author-information
requirement. **14/14 satisfies the user's budget and is not evidence of compliance with the current TMC
policy.** No historical rule and no other journal's rule was substituted.

## Final compile acceptance

| check | result |
|---|---|
| body pages | **14** (limit 14) |
| supplement pages | **14** (limit: not more than the body) |
| errors / undefined references / duplicate labels / missing figures | **0 / 0 / 0 / 0** |
| Overfull boxes | **0** (one appeared from the new availability path and was fixed with `\\allowbreak`) |
| embedded fonts | yes (45 `/FontFile` markers in `main.pdf`, 35 in `supplemental.pdf`) |
| cross-PDF references | supplement builds after main and reads `main.aux`; 0 undefined |
| index-referenced files exist | 16/16 present |
| numbers changed | only the 12 figure-CSV cells listed above; no other printed value moved |

## The four required status statements

1. **Evidence-consistency repair: partial.** S1 is half closed: the demonstrable scoring error is fixed from
   certified data and the two exhibits are now explicitly different comparisons, but three of the four
   mismatched arms have no saved support record, so the exhibits cannot be unified without a re-run. S2 and
   S4 are closed. S3 is closed inside the delivery, with `3.44/1.32` pp left explicitly report-level.
2. **14-page budget: met.** 14/14 by measured PDF page count, both PDFs, after all edits.
3. **Submission package: not complete.** Author placeholders remain and the current TMC rules are unverified,
   so the file set cannot be called submission-ready.
4. **Remaining scientific deficiencies: unchanged by this round.** The full mechanism's independent value
   over the simple projection is still not established (the projection is faster and better on SensorScope's
   group endpoint; Use is not significant and default Debt is tiny, so "every term is necessary" cannot be
   the claim); the structural improvement's task/system value still rests on development geometry and does
   not produce a prediction win; the true `U` is unmeasured on every block; the coverage Gate's `0.750`
   failure cell and the conditional debt bound remain bounds, not guarantees. **A successful compile is not
   evidence of submission or acceptance quality**, and no experiment was resumed by this round.
"""

DIFF = """# PAPER_SUBMISSION_REPAIR_DIFF

Substantive differences introduced by this repair round. Every change is listed with its before-hash so any
line can be reverted. Rollback source for the pre-compression state remains `tmp/remaining_compress/*.before`
and was not touched.

## Files changed

| file | before | after | nature |
|---|---|---|---|
| `TO_OVERLEAF_paper_tmc_r1_clean/main.tex` | 86353 B, `AEAFDB92` | 86379 B, `55742929` | one availability sentence re-pointed at the new index entry, with `\\allowbreak` to avoid an Overfull |
| `TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex` | 91918 B, `3ED0BF54` | 92523 B, `180421A6` | S2 condition mapping (7 lines to 8), S4 terminology (2 words), three captions labelled for S1 |
| `figure_data/FIG_E3_E3_PREDICTION_RISK.csv` | 53593 B, `27B90460` | 53593 B, `91E49822` | 12 `RMSE_mu` cells replaced by their certified theta values; byte length and EOL unchanged |
| `figures/fig4_e3_prediction_risk.pdf` | `37885384` | `42D3EFED` | regenerated from the corrected CSV by `make_figures.fig4_prediction()` |
| `figures/fig4_e3_prediction_risk.png` | `F5AB06D3` | `0EF749B2` | same regeneration |
| `main.pdf` | 852420 B | 854153 B, `7CA83766` | rebuilt |
| `supplemental.pdf` | 1294010 B | 1270723 B, `165F4702` | rebuilt |
| `RAVEN_MCS_PUBLIC_REPRO_R1/README.md` | - | - | one pointer line to the new index (no second list created) |
| `RAVEN_MCS_PUBLIC_REPRO_R1/submission_evidence/` | absent | 16 files | new: the single evidence index plus 15 small certified summaries |

## Substantive text changes

1. **Appendix H opening** (S2). Before: A5, A6a, A6b described as separate, with `the reconstruction results
   follow from A5 alone`. After: `prop:reconstruction` assigned to A1--A3; `prop:practical_plugin` assigned to
   A1, A4, A5, A6b plus the shared-state and positive-mass conditions; A6a assigned to the sharp form; and an
   explicit statement that the section audits only A5, A6a and A6b. Theorems, proofs and assumptions unchanged.
2. **Table XXVI caption** (S4). `The gate sets Design on exactly when ...` became `The support rule sets
   Design on exactly when ...`. No method or code semantics touched.
3. **Table XVIII caption** (S1). Added that its FedAvg row is the current-runner re-run keeping every
   delivered client, and that the same-named rows of Figs. 5-6 are a different comparison.
4. **Fig. 5 caption** (S1). Added that the rows are the frozen run set, that some active sets differ from
   Table XVIII's, and that the figure supports no same-support claim of its own. The `same backbone` wording
   is no longer the caption's only identity statement.
5. **Fig. 6 caption** (S1). Points at Fig. 5's identity statement.
6. **Data and Code Availability** (S3). `remain in their separate result directories ... the revision
   evidence record` became an explicit pointer to `submission_evidence/SUBMISSION_EVIDENCE_INDEX.md`.

## Numbers changed

Only the 12 figure cells, each with two independent certified sources (`C7_E3_ARMS_THETA.csv` and
`ERRATA_FOR_PAPER.md` E-v51-4). Per arm, the three affected seeds:

| arm | seed | was | now |
|---|---:|---:|---:|
| FedAvg-Window | 30007 / 30016 / 30018 | 1.096894 / 1.051261 / 1.103172 | 1.193597 / 1.144226 / 1.178757 |
| FedAsync-Window | 30007 / 30016 / 30018 | 1.098314 / 1.050899 / 1.102365 | 1.194356 / 1.143752 / 1.177704 |
| TimeAlign-Agg | 30007 / 30016 / 30018 | 1.097188 / 1.051842 / 1.103314 | 1.193975 / 1.145255 / 1.179407 |
| Debt-Cal | 30007 / 30016 / 30018 | 1.096564 / 1.056577 / 1.101810 | 1.192130 / 1.143039 / 1.180361 |

Ranking consequence, stated rather than smoothed: after the correction the four arms sit at
`1.1923-1.1934`, i.e. at Local-Hajek's level, so the U-Air `RMSE_mu` picture in Fig. 6 is
`Central-All < Central-Delivered < FedAvg ~ FedAsync ~ TimeAlign ~ Debt-Cal < Local-Hajek ~ Inst-Cal ~ RAVEN`,
with RAVEN-Design at `1.1954` — **no longer** an ordering in which the four baselines appear worse than they
are. No other printed number in the paper moved.

## Claim-evidence map and pending items

`PAPER_CLAIM_EVIDENCE_MAP.md` and `PAPER_EVIDENCE_PENDING_ITEMS.md` are **updated, not rewritten**: the S1
entry now records what was closed (theta scoring, with its two sources), what was labelled (support
identity), and what remains open (per-arm support records for three arms), and the earlier "cannot be
confirmed" text is retained beneath the new status so the history is not erased. No prior pending item was
deleted, and F1, A03 drift, A02 exogenous target and the innovation-gap items stand unchanged.

## What this diff does not contain

No training, inference, checkpoint loading, trace replay, re-scoring, new statistical test, method
redefinition, algorithm change, new figure beyond the stated regeneration, page-limit change, or upload.
"""

(OUT / "PAPER_SUBMISSION_REPAIR_REPORT.md").write_text(REPORT, encoding="utf-8")
(OUT / "PAPER_SUBMISSION_REPAIR_DIFF.md").write_text(DIFF, encoding="utf-8")
print("wrote", (OUT / "PAPER_SUBMISSION_REPAIR_REPORT.md").stat().st_size, "B and",
      (OUT / "PAPER_SUBMISSION_REPAIR_DIFF.md").stat().st_size, "B")

# append the S1 status to the pending items, preserving the existing text
PEND = OUT / "PAPER_EVIDENCE_PENDING_ITEMS.md"
t = PEND.read_text(encoding="utf-8")
ADD = """
## 2026-10-17 repair-round update on the structural figure source difference (S1)

Status change, appended without deleting the 2026-10-16 entry above. The difference is now resolved into two
separate causes. (a) **Scoring:** the four affected arms' `RMSE_mu` in
`figure_data/FIG_E3_E3_PREDICTION_RISK.csv` was still pre-theta on seeds 30007/30016/30018; substituting the
certified theta values moves `FedAvg-Window` from `1.178988` to `1.192251`, identical to Local-Hajek's theta
mean and consistent with `results_w1_ladder/round_v5_1/ERRATA_FOR_PAPER.md` E-v51-4. The 12 cells were
corrected from existing certified CSVs and the figure was regenerated; no inference was run. (b) **Support
identity:** `scripts/audit_table2_uair_fedavg.py` records that the frozen U-Air FedAvg runs dropped
`pi_tar = 0` clients while FedAU/ObsUse/RAVEN-NoDesign kept them, and that `fedavg_window_current` is a
current-runner re-run keeping every delivered client (`results_table2_audit`). The two exhibits are therefore
different comparisons and are now labelled as such in Table XVIII and in both figure captions. **Still
open:** no saved record states which active set `fedasync_window`, `flamf_timealign_adapted` and `debt_cal`
used in their frozen runs, so the exhibits cannot be unified without a re-run, which this round was not
authorized to perform. The figure no longer carries the U-Air comparative conclusion.
"""
if "repair-round update on the structural figure source" not in t:
    PEND.write_text(t.rstrip("\n") + "\n" + ADD, encoding="utf-8")
    print("appended the S1 status to PAPER_EVIDENCE_PENDING_ITEMS.md")
else:
    print("pending items already carry the S1 update")

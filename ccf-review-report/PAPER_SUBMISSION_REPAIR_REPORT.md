# PAPER_SUBMISSION_REPAIR_REPORT

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
| author block | `\author{**** and Anfeng Liu`; email `****@csu.edu.cn`; a third `***` in the second thanks |
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
`\mathcal{A}_r, M_r, \mathcal{C}_r` (main.tex:1059-1062). Replaced with a statement that assigns A1--A3 to
the ideal reconstruction, A1/A4/A5/A6b plus the shared-state and positive-mass conditions to the
perturbation form, A6a to the sharp form, and says explicitly that the section audits A5, A6a and A6b only
and does not establish the clauses it does not check. No theorem, proof, or assumption strength was
changed, and no clause was weakened to match the appendix.

## S3 - Reviewer-facing evidence entry: **resolved within the delivery's limits**

`main.tex`'s Data and Code Availability now names a concrete entry,
`\texttt{submission\_evidence/}\allowbreak\texttt{SUBMISSION\_EVIDENCE\_INDEX.md}`, instead of pointing
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
| Overfull boxes | **0** (one appeared from the new availability path and was fixed with `\allowbreak`) |
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
| S2 closing clause | `does not establish the clauses it does not check` | **yes**, intact at `appendix.tex` L1467-1468; the first probe reported `no` only because the sentence is split across those two lines, which is a defect of the probe, not of the text |
| S4 terminology | `The support rule sets Design on exactly when` | **yes** |
| S1 Fig. 5 identity | `supports no same-support claim of its own` | **yes** |
| S1 Table XVIII identity | `current-runner re-run that keeps every delivered client` | **yes** |
| S1 Fig. 6 pointer | `Row identities are those stated in` | **yes** |
| S3 availability entry | `SUBMISSION\_EVIDENCE\_INDEX.md` | **yes** |

All seven repair markers therefore survive the external edit. What the external edit changed outside those markers was **not** characterised here: it grew `main.tex` by 3025 B and shrank `appendix.tex` by 747 B, and no copy of the 86379 B version is retained, so a line-level diff against it is not possible from this workspace.

Rebuild of the new source: `main.pdf` **14 pages**, 0 errors, 0 undefined references, 0 Overfull; the
supplement builds after main with 0 undefined references. The page budget therefore still holds, but it holds
for a text this round did not fully author, so the S1-S4 statuses above should be re-confirmed against
`3C936D22` before submission.

Unresolved by the external edit: the three author placeholders are still present (`****`, `***`,
`****@csu.edu.cn`), so S5 remains open.


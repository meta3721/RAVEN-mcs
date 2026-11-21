# PAPER_SUBMISSION_REPAIR_DIFF

Substantive differences introduced by this repair round. Every change is listed with its before-hash so any
line can be reverted. Rollback source for the pre-compression state remains `tmp/remaining_compress/*.before`
and was not touched.

## Files changed

| file | before | after | nature |
|---|---|---|---|
| `TO_OVERLEAF_paper_tmc_r1_clean/main.tex` | 86353 B, `AEAFDB92` | 86379 B, `55742929` | one availability sentence re-pointed at the new index entry, with `\allowbreak` to avoid an Overfull |
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

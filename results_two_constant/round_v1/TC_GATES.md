# TC gates — two-constant disclosure

Round: `results_two_constant/round_v1/`. Instruction:
`ccfa-review-reports/raven-mcs-two-constant-disclosure-execution-prompt.md`.
Writer skill `ccf-paper-writer`, mode `polish`. Target: `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`,
edited in place; no copy created.

Verdict: **all gates PASS**. One provenance observation is recorded at the end and is unresolved.

## G0 — independent recomputation

Recomputed from the target arrays through the repository's scoring path
(`runner._predict` + `runner._mu_weights_for_test` + `metrics.rmse_mu`, test split), not copied from
the instruction:

| block | test-fitted constant | expected | training-mean predictor | expected | ratio | test mean | train mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| SensorScope | 2.0878 | 2.0878 | 7.6471 | 7.6471 | 3.7 | 7.6572 | 0.3006 |
| U-Air | 0.6781 | 0.6781 | 1.0537 | 1.0537 | 1.6 | -0.8066 | 0.0000 |
| NSW-Traffic | 1.0067 | 1.0067 | 1.0067 | 1.0067 | 1.0 | 0.0027 | 0.0000 |

All six match to four decimal places. Definitions used: test-fitted constant =
`sqrt(sum_i w_i (y_i - sum_j w_j y_j)^2)`; training-mean predictor =
`sqrt(sum_i w_i (y_i - ybar_train)^2)`. Per-block detail, sources and the checkpoints are in
`TC_TWO_CONSTANTS.json`. **PASS.**

## G1 — byte-level integrity

- pre-edit: `1d6515ff7d7dfe958ee2469984001c43786a550eb2b0c17cca66d0ecca25606a`, 118894 B
- post-edit: `73fa475ede18e1da11dd9118cf2e29276dc8be41b16f742440c6c9e34f5aabd3`, 119384 B (+490 B)
- reversing all three edits recovers the pre-edit sha256 **exactly**: PASS
- CRLF count unchanged (0 before and after; the file is LF only): PASS

Because the reverse replacement is exact, no byte outside the three edited sites changed, so the
relative quantities (`H`, the interval, the MDE, the `K_r <= 3` share, both `Delta` values) are
byte-identical by construction.

## G2 — build

Compiled in the fixed order `supplemental.tex`, `main.tex`, `main.tex`, out of tree:

- `main.pdf` **18 pages**, errors 0, undefined 0, multiply-defined 0, Overfull 0 — unchanged from the
  pre-edit build;
- `supplemental.pdf` 16 pages, Overfull 1 — unchanged.

**PASS** (the page budget is not consumed).

## G3 — prose

`check_prose_quality.py --scope paper`: 14 623 words, **em dashes 0/3**, one advisory
(semicolon density), unchanged in kind from the pre-edit run. **PASS.**

## G4 — nothing else moved

- `a constant predictor attains` — 0 occurrences (required 0).
- `a constant predictor on` — 0 occurrences (required 0).
- bare `a constant predictor` — 0 occurrences; the two canonical terms are used instead:
  `test-fitted constant` 3x, `training-mean predictor` 4x.
- relative quantities present and unchanged: `-1.49%` (L2245), `[-5.42%,+1.76%]` and
  `5.80%` (L2246), `15.1%` (L2230), `0.0079 [0.0051,0.0110]` and `0.0099 [0.0067,0.0132]` (L2252),
  the conclusion's `5.80%` (L2283).
- new numbers introduced are confined to the allowed set: the three test-fitted constants, the three
  training-mean predictors, the two ratios, and repeats of the already-present split means.

**PASS.**

## The three edits

**Edit A — metric definition.** Replaced `and a constant predictor attains ... under the same weights.
On SensorScope and U-Air the training and test target levels differ, so an absolute RMSE_mu on those
two blocks reflects that difference as well as prediction error; the relative columns are invariant to
it.` with a version that names the two references separately, states that the first is fitted on the
scored test labels, states that the second uses only the training split, and gives the two ratios
(`3.7x`, `1.6x`).

**Edit B — NSW-Traffic sentence.** `against $1.007$ for a constant predictor on the same test weights,
so the contrast is between two arms that both leave the constant` became `against $1.007$ for the
test-fitted constant on the same test weights, where the training-mean predictor takes the same value;
both arms therefore sit below that reference`. The arms' levels, ranges, headroom, interval and MDE are
untouched.

**Edit C — main table caption.** The table `tab:main_effectiveness` does carry an absolute
`RMSE_mu` column (SensorScope about 7.93, U-Air about 1.11), so the conditional edit applied: one
caption sentence now gives both references for the blocks the table covers
(`2.088` / `0.678` and `7.647` / `1.054`) and says the absolute column is read against the
training-mean predictor. No cell, row or column was changed.

## Provenance observation (unresolved, not a gate failure)

The pre-edit state this round found was `1d6515ff…` (118894 B). The last state this session produced was
`7b874f285a6dd323cecdab3cba4c190cea3b47701c5b75ddc289d00e566ad765` (118819 B), i.e. the file grew by
75 B between the two, from a source other than this session. Not identified: the change is not in the
Data and Code Availability section, does not name `results_traffic_e1/`, `results_traffic_struct/`,
`TE1`, `TS1`, seed 30006 or a `round_v1` path, and it did not touch the three sites this round edited
(their pre-edit anchors matched). It is the fourth manuscript revision in this series that appeared
without a record in the workspace. G1 makes this round's own footprint exact; the intervening 75 B is
not attributable from the artifacts available here and should be confirmed by the author.

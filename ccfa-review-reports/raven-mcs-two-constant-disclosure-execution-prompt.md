# RAVEN-MCS two-constant disclosure (execution prompt)

`ccf-paper-writer`, mode `polish`. One bounded text change to the manuscript. No manuscript copy is
created; git supplies rollback.

## 0. Why this edit exists

Two independent reviews of `main.tex` (sha256 `6FC9BE0B…` at the time of review) charged the Evidence
axis for the same defect, which is **in the current text**:

> The metric definition prints test-split target means `7.657`, `-0.807`, `0.003`, training-split means
> `0.301`, `0`, `0`, and "a constant predictor attains `RMSE_mu` of `2.088`, `0.678` and `1.007` under
> the same weights."

`2.088` and `0.678` are fitted **on the test labels**: they are the weighted standard deviation of the
scored test target, i.e. the best achievable constant *after seeing test Y*. A reader cannot tell that
from the sentence, and `2.088` is **not deployable**. The deployable reference is the **training-split
mean evaluated on the test split**, whose `RMSE_mu` is `7.647` (SensorScope) and `1.054` (U-Air). The
current wording therefore makes the absolute federated errors look far worse than a practitioner-facing
reference would, and it hides which reference each absolute number should be read against. One review
put it exactly: *"the text calls the test-label constant 'a constant predictor', and the reader cannot
see from this sentence that 2.088 cannot be deployed."*

This edit fixes only that. It is a precision-and-disclosure repair, not a scope change.

## 1. Hard constraints

- Edit `TO_OVERLEAF_paper_tmc_r1_clean/main.tex` **in place**. Do not create `v2`, `revised`, dated or
  `final` copies. Do not edit `src/`, the paper's bibliography, the diagnosis ledger, any
  `results_*/` tree, or any frozen artifact. Do not commit or push.
- Change **only** the sites in section 3. Do not reframe the abstract, the introduction, the
  contribution list, or the conclusion's claims.
- Do not add, remove or restate any other number. Do not add a skill-score column, do not add a table
  row, do not re-source any existing figure, and do not touch the relative quantities
  (`Delta_group`, `Delta_c-s`, `H`, the paired intervals, the MDE, the `K_r <= 3` share).
- Prose rules from `ccf-humanization`: no defensive phrasing, no reviewer-facing hedging, no
  boilerplate caveat, no meta-commentary. This is a definitional statement about a metric, so write it
  flatly. Em dashes in the whole manuscript must stay at or below 3 (currently 0).
- Preserve every LaTeX command, label, reference, equation and unit. Keep the file's existing line
  width convention and LF line endings.
- The page budget is binding: `main.pdf` must stay **18 pages** with 0 errors, 0 undefined, 0
  multiply-defined and 0 Overfull. If the edit pushes it over, compress within this edit rather than
  accepting 19 pages.
- If any required change cannot be made without touching `src/`, write `TC_BLOCKED.md` under the output
  directory and stop.

## 2. The two references, and the numbers

Both are `RMSE_mu` values under the repository's own scoring weights
(`runner._predict` + `runner._mu_weights_for_test` + `metrics.rmse_mu`), on the test split.

| block | test mean | training mean | **test-fitted constant** (oracle) | **training-mean predictor** (deployable) |
|---|---:|---:|---:|---:|
| SensorScope | 7.6572 | 0.3006 | **2.0878** | **7.6471** |
| U-Air | -0.8066 | 0.0000 | **0.6781** | **1.0537** |
| NSW-Traffic | 0.0027 | 0.0000 | **1.0067** | **1.0067** |

Derivations, so nothing has to be guessed:

- test-fitted constant = `sqrt(sum_i w_i (y_i - sum_j w_j y_j)^2)`, the weighted standard deviation of
  the scored test target;
- training-mean predictor = `sqrt(sum_i w_i (y_i - ybar_train)^2)`, the same weights, with the
  training-split mean as the constant.

Context that the text may need, all verified:

| comparison | SensorScope | U-Air | NSW-Traffic |
|---|---:|---:|---:|
| frozen `fedavg_window` `RMSE_mu` | 7.9144 | 1.2108 | no such arm in the frozen tree |
| against the test-fitted constant | +279.1 % | +78.6 % | - |
| against the training-mean predictor | **+3.5 %** | **+14.9 %** | - |
| Adam confirm set, window FedAvg | - | - | 0.9671 |
| Adam confirm set, oracle-margin arm | - | - | 0.9731 |
| either constant on NSW-Traffic | - | - | 1.0067, so both arms are **3.9 % below** it |

**Naming, used consistently and defined once.** Use exactly two canonical terms:

- **test-fitted constant** — the constant fitted on the scored test labels; state once that it is fitted
  there, so it is a floor for the metric rather than a deployable predictor;
- **training-mean predictor** — the training-split target mean applied to the test split.

Do not use "a constant predictor" bare, "the constant" unqualified, "oracle" as a bare noun, or any
third synonym.

**One trap, stated so it cannot be walked into.** NSW-Traffic's skill does **not** replicate across seed
sets: the five screen seeds that chose the step size average **17.0 %** below the constant, while the
fifteen confirm seeds average **3.9 %**. Only the confirm-set figure may appear in the manuscript, and
no sentence may imply that the larger screen figure is the result.

## 3. Required edits

### Edit A (mandatory) — the metric definition

Locate the sentence added most recently near the `RMSE_mu` definition, which currently reads
`... but a constant predictor attains \mathrm{RMSE}_{\mu} of $2.088$, $0.678$ and $1.007$ under the
same weights`. Replace it so that the paragraph states, in this order:

1. the two target levels per block (test `7.657`, `-0.807`, `0.003`; training `0.301`, `0`, `0`);
2. the **test-fitted constant** `2.088`, `0.678`, `1.007`, with one clause saying it is fitted on the
   scored test labels;
3. the **training-mean predictor** `7.647`, `1.054`, `1.007`, with one clause saying it uses only the
   training split;
4. one sentence saying that on SensorScope and U-Air the two references differ (by about `3.7x` and
   `1.6x`), because those blocks' training and test target levels differ, so an absolute
   `RMSE_mu` there is read against the training-mean predictor; and that the relative quantities are
   invariant to the difference.

Keep it to four sentences at most. A model wording, to be adapted rather than copied:

> The test-split target means are `7.657`, `-0.807` and `0.003` on SensorScope, U-Air and NSW-Traffic,
> against training-split means of `0.301`, `0`, and `0`. Fitted on the scored test labels, the best
> constant attains `RMSE_mu` of `2.088`, `0.678` and `1.007`; the training-mean predictor, which uses
> only the training split, attains `7.647`, `1.054` and `1.007`. On SensorScope and U-Air the two
> differ by about `3.7x` and `1.6x`, because the training and test target levels differ, so an absolute
> `RMSE_mu` on those blocks is read against the training-mean predictor; the relative quantities are
> invariant to that difference.

### Edit B (mandatory) — the NSW-Traffic sentence

In the limitations passage, the sentence about the fifteen Adam runs currently compares against
`$1.007$ for a constant predictor on the same test weights`. Relabel it so it names the **test-fitted
constant** and notes that on this block the training-mean predictor coincides with it at `1.007`. Do
not change the arms' levels (`0.967`, `0.973`), the ranges, the headroom, the interval or the MDE.

### Edit C (conditional) — the main effectiveness table

Find `Table~\ref{tab:main_effectiveness}`. If it reports absolute `RMSE_mu` entries, add **one caption
sentence** giving the test-fitted constant and the training-mean predictor for the blocks the table
covers, so every absolute entry has a same-protocol reference beside it. Do not change any cell, row
order, or column, and do not add a row.

## 4. Gates

Run these in order. Any failure is a STOP: write `TC_BLOCKED.md` with the failing gate's evidence.

- **G0 — independent recomputation.** Recompute all six constants in section 2 from the repository's
  scoring path and the target arrays. They must match this prompt to four decimal places. Do not copy
  the values from this prompt; if they disagree, the prompt is wrong and the round stops.
- **G1 — byte-level integrity.** Record the pre-edit sha256. After editing, apply the reverse of every
  replacement and require that it recovers the pre-edit sha256 exactly. Require that the CRLF count is
  unchanged.
- **G2 — build.** Compile in the fixed order `supplemental.tex`, `main.tex`, `main.tex` out of tree.
  Require `main.pdf` **18 pages**, 0 errors, 0 undefined, 0 multiply-defined, 0 Overfull, and
  `supplemental.pdf` 16 pages with 1 Overfull, i.e. unchanged.
- **G3 — prose.** Run `scripts/check_prose_quality.py --scope paper`. Require em dashes at or below 3
  and no new hard failure; the existing semicolon-density advisory may remain.
- **G4 — nothing else moved.** Require that the old wording `a constant predictor attains` occurs zero
  times, that `Delta_{\mathrm{group}}`, `\Delta_{c\text{-}s}`, the headroom, the interval, the MDE and
  the `K_r` share are byte-identical to the pre-edit state, and that no new number other than the three
  test-fitted constants, the three training-mean predictors, the two ratios and the already-present
  split means appears in the file.

## 5. What this edit does not do

- It does not change what the paper claims, its scope, or its contribution framing. Raising
  Significance by reframing the paper as "structural projection plus an explicit prediction null" is a
  separate authorial decision and is not part of this task.
- It does not add a skill-score quantity, does not attach the `0.967`/`0.973` figures to a named
  per-seed file, and does not add the test-split constant to any verdict file. Those are separate
  tasks.
- It does not add seeds. Chasing the `0.5 %` headroom bar at the observed paired standard deviation
  would need on the order of 2 000 to 8 000 pairs and is explicitly out of scope.
- It does not touch the training-mean predictor's own caveat: on SensorScope and U-Air that predictor
  is close to the federated arms, and the edit must not spin that fact either way.

## 6. Outputs

- `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`, edited in place.
- `results_two_constant/round_v1/TC_GATES.md` — G0's six recomputed constants with the scoring path
  named, G1's pre/post sha256 and the reverse-replacement result, G2's page counts and log counters,
  G3's prose report, G4's grep evidence.
- `results_two_constant/round_v1/TC_TWO_CONSTANTS.json` — the six constants, the two ratios, the frozen
  arm levels and the confirm-set levels, each with its source file.

## 7. Execution order

1. Read the three sites. Run G0. On mismatch, write `TC_BLOCKED.md` and stop.
2. Apply A, then B, then C if the table condition holds.
3. Run G1, G2, G3, G4. On any failure, revert to the pre-edit hash and write `TC_BLOCKED.md`.
4. Write the two output files. Stop. Do not propose further paper edits from this task.

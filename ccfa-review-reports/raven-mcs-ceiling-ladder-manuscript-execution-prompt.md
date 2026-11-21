# Ceiling ladder into the manuscript (execution prompt)

`ccf-paper-writer`, mode `draft` with format preservation. Four bounded insertions into
`TO_OVERLEAF_paper_tmc_r1_clean/main.tex`, edited in place. This plan exists because round 16 named it
the single largest available readiness gain: the project now holds a **pre-registered, adequately
powered, separated measurement of the recoverable-gain ceiling**, and the manuscript does not report it.

## 0. The authorial decision this plan implements, and the one it does not

Round 16's finding is a scope decision, not a defect, so it is put to the author before any write.

**What the author is approving.** That the Recoverable-Gain Ceiling subsection states a **measured**
bound in addition to its two existing arguments: over a pre-registered ladder of deployment-target
concentration, up to the most extreme concentration that exists, the recoverable gain of the weight class
stays below the subsection's own `0.5 %` bar, with the upper end of the interval at `+0.130 %` at the
extreme. That the limitations paragraph gains one cross-reference to it, that the conclusion gains one
clause, and that the availability section names the run tree and the frozen pre-registration behind it.

**What the author is not approving.** No repositioning of the contribution, no change to the title, the
abstract or the contribution list, and no promotion of the exploratory structural readout. The paper's
self-description stays what it is; the ceiling section gains a measurement, and gate W5 proves the scope
did not drift.

**The honest framing, which must survive into the prose.** The paper's own bar in this subsection is
`H >= 0.5 %` (L2131-L2132). The ladder must be compared to **that** bar. The `2 %` figure used as the
decision threshold in the TE2 experiment design is this session's internal planning choice and must not
appear anywhere in the manuscript.

## 1. Hard constraints

- Edit `TO_OVERLEAF_paper_tmc_r1_clean/main.tex` in place. No `v2`, `revised`, dated or `final` copy. Do
  not edit `src/`, the bibliography, the diagnosis ledger, any `results_*/` tree, or any frozen artifact.
  Do not commit.
- Run the `ccf-humanization` preflight first and apply `../ccf-humanization/references/humanization-policy.md`.
  Load only `references/prose-quality-guardrails.md` beyond it: this is a bounded section-level task, so
  the venue guides, exemplar cards, length budgets, storyline blueprint and section modules stay unloaded.
- The new text is **not** a defensive caveat and **not** hype. It states a measurement, its scope, and what
  it bounds. Do not write "we acknowledge", "it should be noted", "while this is encouraging", or any
  reviewer-facing hedge; these are hard failures, not style preferences.
- Do not invent, round differently, or re-derive any number. Quote the values in section 2 exactly as the
  named artifacts carry them, in the manuscript's existing style (`\mathrm{RMSE}_{\mu}`, percentages to
  three decimals where the section already uses that precision).
- Preserve every LaTeX command, label, reference, equation, table and unit. Keep LF endings and the
  file's line width convention. Full-paper em dashes must stay at or below 3 (currently 0).
- `main.pdf` must stay **18 pages**. The project's page allowance is a hard 18 pp. If an insertion pushes
  it to 19, write `CW_BLOCKED.md` with the exact overflow and stop; do not exceed the allowance and do not
  cut other content without approval.
- The named method and configuration must be the genuine ones: these are full E3 real runs on NSW-Traffic
  at the frozen configuration with a **declared, re-weighted deployment target**. That re-weighting is part
  of the scientifically relevant configuration and is stated as such. Nothing here is a simplified, proxy
  or debug variant, and the prose must not say that anything is confirmed, approved or ready.

## 2. The claim and its exact numbers

Source of every value: `results_traffic_e2/round_v1/TE2_STEP4_VERDICT.json` (rungs; each percentage is `100 * mean_gap / control_mean` and each interval `100 * boot_lo|boot_hi / control_mean`, computed from the artifact's own fields rather than from its rounded `pct_of_control`), `TE2_VERDICT.json`
(the `kappa = 5` cell and its injection record), `TE2_FROZEN_PREREG.json` (what was fixed before the runs),
`TE2_TARGET_ARTIFACT_KAPPA5.json` (the re-weighted target).

**Quantity.** The gap from the uncorrected member to the oracle-margin member, both scored by
`\mathrm{RMSE}_{\mu}` under the same concentrated target, paired on 20 seeds (30001-30020), at the frozen
server step, one update per window.

| rung: target concentration, top-1 region share | gap, % of the uncorrected member |
|---|---:|
| frozen target, `0.2500` | `+0.001` (interval `[-0.010, +0.015]`, contains zero) |
| `0.6322` | `+0.022` (interval `[+0.005, +0.042]`) |
| `0.7746` | `+0.045` (interval `[+0.024, +0.069]`) |
| **single region, `1.0000`** | **`+0.097` (interval `[+0.067, +0.130]`)** |

**Required content of the new ceiling paragraph.** In three to five sentences, in the subsection's own
voice:

1. A third measured quantity bounds the class: the recoverable gain as the deployment target concentrates,
   from the frozen target up to the most extreme concentration that exists, namely all of the target mass
   on one region.
2. The ladder and its numbers, including that the gain rises with concentration and that the two most
   concentrated rungs have intervals excluding zero.
3. **The bound**: at the extreme, `+0.097 %` with interval `[+0.067 %, +0.130 %]`, so the interval's upper
   end lies **below the `0.5 %` bar this subsection set**, and concentration cannot be pushed further.
4. The scope, in the same breath and without hedging: a single block, at the frozen server step, under a
   declared deployment target; the single-region setting is an upper bound on concentration, not a
   deployment scenario; the uncorrected member is this block's Hájek aggregation, not window FedAvg, so
   these values extend the section's bound to this block rather than reproducing the grid's `H` on it.
5. The endpoint and the concentration levels were fixed before the runs; cite the pre-registration.

**Required content of the other three sites.**

- **Limitations** (after the sentence reporting that the detectable effect cannot resolve the `0.5 %` bar):
  one sentence pointing to the ceiling paragraph, saying that the concentration ladder bounds what
  re-weighting inside this class could buy on this block, so the null is not an artefact of the target
  being nearly uniform. No new numbers here.
- **Conclusion**: one clause at most, factual, carrying `+0.097 %` and the `0.5 %` bar. If it does not fit
  without sounding like a second result, omit it and note the omission in the gates file.
- **Data and Code Availability**: extend the sentence that already names the two trees so it also names
  `results\_traffic\_e2/` and the frozen pre-registration file, in the section's existing `\texttt{}` and
  internal-to-this-study style.

**Forbidden in the new text.** Claiming that the projection is validated or that concentration helps the
method; presenting the single-region target as a realistic deployment; importing the `2 %` design
threshold; describing the run as a simulation or a proxy; restating the exploratory structural readout;
any sentence whose function is to protect the paper rather than to report.

## 3. Sites

1. `\subsection{Recoverable-Gain Ceiling}` / `\label{subsec:ceiling}` — a new paragraph **after** the
   sentence that ends `... NSW-Traffic, where that step is replaced, is reported in
   Section~\ref{subsec:limitations}.` Inserted there, the ladder completes the subsection's own closing
   move instead of competing with it.
2. The limitations paragraph that contains `too coarse to resolve the` — one cross-referencing sentence.
3. The conclusion sentence carrying the `5.80\%` detectable effect — at most one clause.
4. The Data and Code Availability sentence carrying `results\_traffic\_e1/` — extended.

## 4. Gates

- **W0 - pre-edit state.** Record the pre-edit sha256, byte count and line count. Require the four anchors
  to match exactly once each. Require a recorded authorial sign-off on section 0 before any write; if the
  sign-off is absent, write `CW_BLOCKED.md` and stop.
- **W1 - byte integrity.** Reverse every insertion and require the reverse replacement to recover the
  pre-edit sha256 exactly, with the CRLF count unchanged.
- **W2 - build.** `supplemental.tex`, `main.tex`, `main.tex`, out of tree: `main.pdf` **18 pages**, 0
  errors, 0 undefined, 0 multiply-defined, 0 Overfull; `supplemental.pdf` 16 pages with 1 Overfull. On a
  19-page `main.pdf`, `CW_BLOCKED.md` and stop.
- **W3 - prose.** `ccf-humanization` preflight clean; `scripts/check_prose_quality.py --scope paper` with
  em dashes at or below 3 and no new hard failure; no banned phrase from section 1 present.
- **W4 - number traceability.** A scripted comparison of every number the new text prints against the
  artifact that carries it, written to `CW_NUMBERS.json`. Any mismatch fails the gate.
- **W5 - scope did not drift.** Require the **title line, the abstract block, and the contribution list**
  to be byte-identical to the pre-edit state, and every value added on 2026-10-07 and later to be
  unchanged. W1 proves this globally; W5 exhibits it for the three regions a reviewer would check first.

## 5. What this round does not do

- It does not change the title, abstract, contribution list, or the paper's stated scope.
- It does not add a table or a figure. A four-row table would be the clearest presentation, but it costs
  more page budget than the prose it replaces and the 18 pp allowance is already tight; if the author wants
  the table, that is a separate request routed to `ccf-visual-composer` with its own budget decision.
- It does not run any experiment, re-score any checkpoint, or touch any result tree.
- It does not promote the exploratory structural readout, and it does not add the ladder to the abstract.
- It does not deposit the run tree into the release bundle; that is the separate Reproducibility repair.

## 6. Outputs

- `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`, edited in place.
- `results_paper_ceiling/round_v1/CW_GATES.md` - W0 to W5 with evidence, plus the recorded sign-off.
- `results_paper_ceiling/round_v1/CW_EDITS.md` - each insertion verbatim, before and after.
- `results_paper_ceiling/round_v1/CW_NUMBERS.json` - number to artifact to value.
- `results_paper_ceiling/round_v1/CW_BLOCKED.md` - only on failure, never as a workaround.

## 7. Execution order

1. `ccf-humanization` preflight; confirm the sign-off in section 0 is recorded. Otherwise stop.
2. W0, then the four insertions.
3. W1, W2, W3, W4, W5. On any failure, revert to the pre-edit sha256 and write `CW_BLOCKED.md`.
4. Write the outputs. Then hand off, in this order: `ccf-integrity-auditor` for number and claim
   consistency across the whole paper, then `ccf-paper-reviewer` for a round-17 read of the Evidence axis,
   which is the axis this change is intended to move.

## 8. Sign-off block (to be filled by the author before execution)

```text
Approve the ceiling paragraph as scoped in section 2 (yes / no):
Approve one cross-reference in the limitations (yes / no):
Approve one clause in the conclusion (yes / no):
Approve naming results_traffic_e2/ and the pre-registration in the availability section (yes / no):
Accept that the title, abstract and contribution list stay unchanged (yes / no):
If the build reaches 19 pages: stop and report, or authorize a named cut (name it):
```

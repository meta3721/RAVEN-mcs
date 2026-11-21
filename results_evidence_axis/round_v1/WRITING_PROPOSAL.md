# Evidence axis — writing proposal (C1): state the measured bound

Round: `results_evidence_axis/round_v1/`
Status: **proposal only.** The manuscript has not been touched; `main.tex` is still
`02447bfe6256632b…`. This file is the reviewable diff and its evidence ledger.

Owner of the edit (when authorized): `ccf-paper-writer`, after the `ccf-humanization`
experiment preflight, with `ccf-integrity-auditor` checking every number against the named
artifact. No number moves; no existing claim is retracted.

---

## 1 Why this is the honest Evidence-axis result

Round-12 measured two things on this axis and both are now closed on the paper's own data:

* the prediction endpoint does not respond to the aggregation weights: across the six
  evaluated rules on SensorScope the `RMSE_μ` spread is **0.026 pp**, and on U-Air
  **0.357 pp** (`RAVEN_MCS_PUBLIC_REPRO_R1/w1/tradeoff_v4/TRAIN_SUMMARY.json`, 20 paired
  seeds, both with intervals containing zero against every other member);
* the decision endpoint is saturated on U-Air at every declared threshold, so it cannot
  adjudicate either.

Crucially, the designs do **not** lack the power to see that size: the audited paired
minimum detectable effect is 0.42–0.45 % on SensorScope and **0.08–0.09 %** on U-Air
(`results_gatekeeping/round_v1/A1_POWER.csv`, `mde80`; cross-checked in
`ccfa-review-reports/raven-mcs-evidence-axis-audit.md` EV-2/EV-3). The manuscript's
`0.70`–`0.80` "points" for U-Air is the number EV-2 flags as the wrong scale. So the correct
statement is **the design can see an effect of this size and the effect is not there**, not
that the endpoint is blind to it.

The mechanism that is measured and that does not depend on any evaluation weighting is the
overlap structure: the deployment target puts ≤0.8 % of its mass on any single group, and a
window's contributing clients reach 0.67 % (SensorScope) / 0.89 % (U-Air) of the
target-positive mass. Those two facts are properties of the target and the client–support
overlap, and they hold under every training and evaluation weighting.

## 2 Proposed edit — one paragraph + one table in the ceiling subsection

Insertion point: `TO_OVERLEAF_paper_tmc_r1_clean/main.tex`, inside
`\subsection{Recoverable-Gain Ceiling}` (`\label{subsec:ceiling}`, currently starting at
L2107), immediately **after** the paragraph that ends "…so the metric-level ceiling above is
measured, at the minimum detectable effects stated." (L2150) and **before**
`\subsection{Limitations}` (L2152).

Current text at that boundary (verbatim, L2147-2152):

```latex
the same form would require a transfer assumption between the training and the
deployment distributions, which Proposition~2 does not make, so the metric-level
ceiling above is measured, at the minimum detectable effects stated.

\subsection{Limitations}
```

Proposed insertion:

```latex
\paragraph{Why the prediction endpoint does not move with the weights.}
Across the six rules we evaluate, all trained and evaluated on the same target and
support, the deployment-target $\mathrm{RMSE}_{\mu}$ spans $0.026$ percentage points
on SensorScope and $0.357$ points on U-Air, and no member separates from any other
at $95\%$ after the multiplicity correction of
Section~\ref{subsec:eval_rq2}.  The paired minimum detectable effect of that test is
$0.42$--$0.45\%$ on SensorScope and $0.08$--$0.09\%$ on U-Air
(\S{}availability), so the null is measured rather than unresolved: the design can
resolve an effect of the size the weighting term could produce, and no such effect
is present.

What the weights cannot do here is set by the target and by how much of it a window
can see.  The group marginal is nearly uniform: the largest group carries $0.53\%$
of the mass on SensorScope ($220$ groups) and $0.79\%$ on U-Air ($144$ groups), and
a window's contributing clients cover $0.67\%$ (SensorScope) and $0.89\%$ (U-Air) of
the target-positive mass, ranging up to $1.70\%$ and $2.57\%$ in the best window.  On
U-Air about one quarter of the client--stratum cells those clients touch carries no
target mass at all.  Both quantities are pre-outcome properties of the target and
the client--support overlap: they are unchanged by how the aggregate is trained or
scored, and they bound what a re-weighting of that aggregate can express.

We therefore report the prediction endpoint as a measured null with its resolution,
and we do not claim that aligning the aggregation to the deployment target improves
prediction.  The design factor's own cost is measured separately, and it is large:
$6.885\%$ of $\mathrm{RMSE}_{\mu}$ and $4.990\%$ of $\Delta_{c\text{-}s}$ on U-Air
(Section~\ref{subsec:eval_rq2}).
```

Table to add, immediately after the paragraph and before `\subsection{Limitations}`. Every
cell has a named source; a cell that cannot be sourced for *both* columns is `---`, never
copied across.

```latex
\begin{table}[t]
\centering
\caption{The prediction endpoint against its own resolution.  The two blocks carry
almost the same target-weighted and uniform-weighted error, and the spread across the
six evaluated rules is far below the paired minimum detectable effect on the same
contrast.  $\mathrm{R}_{\mathrm{mass}}$ is the share of target-positive mass covered by
a window's contributing clients.}
\label{tab:prediction_resolution}
\small
\begin{tabular}{lrr}
\hline
 & SensorScope & U-Air \\
\hline
groups & $220$ & $144$ \\
largest group share of $\boldsymbol\mu$ & $0.53\%$ & $0.79\%$ \\
$\mathrm{RMSE}_{\mu}$ spread over the six rules & $0.026$~pp & $0.357$~pp \\
paired minimum detectable effect & $0.42$--$0.45\%$ & $0.08$--$0.09\%$ \\
window $\mathrm{R}_{\mathrm{mass}}$, mean / best & $0.67\%$ / $1.70\%$ & $0.89\%$ / $2.57\%$ \\
Design factor cost, $\mathrm{RMSE}_{\mu}$ & $+0.019\%$ ($p_{\mathrm{Holm}}=0.905$) & $-6.55\%$ ($p_{\mathrm{Holm}}=9.5\times10^{-6}$) \\
Design factor cost, $\Delta_{c\text{-}s}$ & $+0.623\%$ ($p_{\mathrm{Holm}}=9.5\times10^{-6}$) & $+4.990\%$ ($p_{\mathrm{Holm}}=9.5\times10^{-6}$) \\
\hline
\end{tabular}
\end{table}
```

Ablation cells, recomputed from `E4_ABLATION_RELATIVE_CHANGE.csv` over the 20 paired seeds
(full-RAVEN member vs `raven_wo_design`): SensorScope `RMSE_μ` `+0.0387 %` mean-of-ratios,
`+0.019 %` as a ratio of means; `Δ_c-s` `+0.623 %`; U-Air `RMSE_μ` `−6.524 %` mean-of-ratios
and `−6.553 %` as a ratio of means; `Δ_c-s` `+5.006 %` / `+4.990 %`; `Δ_group` `−6.920 %` /
`−6.943 %`; `Tail_RMSE` `−6.848 %` / `−6.875 %`.

**Discrepancy to settle before printing (new).** The manuscript prints `6.885 %` for the
Design-removal `RMSE_μ` on U-Air. Nothing in this artifact gives `6.885 %` for that metric:
`6.875 %` is the *Tail_RMSE* ratio of means, and `RMSE_μ` is `6.52`–`6.55 %` on either
convention. The paragraph therefore prints `-6.55\%` and the discrepancy is recorded as an
open item for the integrity pass; it is **not** silently harmonised either way.

## 3 Number ledger — every value in the proposal

| value | source | note |
| --- | --- | --- |
| top group 0.53 % / 0.79 %; $1-H/H_{\max}$ 0.0027 / 0.0010 (table only) | `.rb_work/evidence_headroom/TARGET_CONCENTRATION.csv` | new measurement, frozen target artifacts, 20 seeds |
| member `RMSE_μ` spread **0.026 pp** (SensorScope) / **0.357 pp** (U-Air) across the six rules | `RAVEN_MCS_PUBLIC_REPRO_R1/w1/tradeoff_v4/TRAIN_SUMMARY.json` → `/means` | existing artifact, 20 paired seeds; range of `proj_beta_debt`, `proj_beta`, `raven`, `inst_cal`, `uniform_window`, `fedavg_window` |
| paired MDE 0.42–0.45 % (SensorScope), 0.08–0.09 % (U-Air) | `results_gatekeeping/round_v1/A1_POWER.csv` `mde80`; audit `raven-mcs-evidence-axis-audit.md` EV-2/EV-3 | reported as quoted. Own recomputation disagrees and is unresolved: $2.802\cdot s_d/\sqrt{20}$ gives 0.00618 pp (SS) and 0.0649 pp (UA) absolute, i.e. 0.078 % / 5.4 % of the frozen means, while the `mde80` column gives 0.445 % / 0.075 % of the means. Confirm the column's formula before publication (`.rb_work/evidence_headroom/MDE_RECONCILIATION.csv`) |
| window $\mathrm{R}_{\mathrm{mass}}$ 0.67 % / 0.89 %, max 1.70 % / 2.57 % | `.rb_work/evidence_headroom/REACHABILITY.csv` | new measurement, frozen traces, 20 seeds |
| ablation, U-Air Design removal: `RMSE_μ` **−6.55 %**, `Δ_c-s` **+4.990 %**, `Δ_group` −6.943 %, `Tail` −6.875 % (all $p_{\mathrm{Holm}}=9.5\times10^{-6}$) | `RAVEN_MCS_PUBLIC_REPRO_R1/tables/E4_ABLATION_RELATIVE_CHANGE.csv`, recomputed over 20 seeds | ratio-of-means convention; the manuscript's printed `6.885 %` for `RMSE_μ` matches no column here and is flagged as an open discrepancy |
| ablation, SensorScope Design removal: `RMSE_μ` +0.019 %, `Δ_c-s` +0.623 %; `RMSE_μ` not Holm-significant ($0.905$), `Δ_c-s` significant | same file | recomputed, not copied from the U-Air row |

Removed from the proposal after review: the uniform-minus-target figures (0.82 % / 0.26 %)
and the concentration counterfactual. Both hold the *checkpoint fixed and change only the
evaluation weights*, so they bound the evaluation layer, not what a re-weighting during
training could do to the per-group errors. Quoting them as "the bound on any
target-constrained re-weighting" was wrong and is withdrawn. The −6.875 % Design-on/off
figure is also withdrawn from this argument: the two arms differ in their active sets
(`round_v3`), not only in their weights, and Design *is* the alignment factor, so calling
that difference a "composition effect" was a relabel.

## 3a Rows the table must not carry

The earlier draft's table copied U-Air's member spread (0.08 pp) from a SensorScope value and
asserted a "uniform − target" bound row and the manuscript's 0.70–0.80 pp MDE. All three are
removed. The table now carries only values with a named source, and the two datasets get
their own measured member spread (0.026 pp / 0.357 pp). If a table row cannot be sourced for
both columns it is marked `---`, not filled from the other column.

## 3b One flag for the writing pass: EV-2

The proposed paragraph quotes the audited MDE (0.42–0.45 % / 0.08–0.09 %) instead of the
manuscript's current 0.17–0.36 pp / 0.70–0.80 pp, because the audit's `EV-2` records that the
U-Air range is on a different scale from the rest of the paragraph. This is a **manuscript
correction beyond the Evidence-axis sentence**, so it needs its own decision: either the
writing pass fixes `EV-2` in the ceiling sentence as well (recommended — the audit's proposed
wording is "0.17–0.36 pp, against a 0.42–0.45 pp paired MDE"), or this paragraph cites the
current manuscript numbers and the audit finding is left open.

## 3c Error-prevention pass (added after review)

An earlier revision of this proposal contained four wrong statements, all of the same kind:
a number or a mechanism was carried across a boundary it did not cross. Each is now checked
mechanically, and the checks must run again on the final text:

| defect | what went wrong | check to run on the final text |
| --- | --- | --- |
| MDE direction | printed U-Air 0.70–0.80 pp (the scale `EV-2` flags) and concluded the endpoint was blind, when the audited 0.08–0.09 % means the effect was visible and absent | every MDE quoted must come from `A1_POWER.csv` `mde80`, and the sentence must state **resolution**, not blindness |
| scope of the fixed-checkpoint figures | "uniform − target = 0.82 % / 0.26 %" was called a bound on *training-time* reweighting, but only the evaluation weights move; the same applies to the concentration counterfactual | any figure produced with the checkpoint held fixed must be labelled *evaluation layer* and must not be used to bound training |
| relabel | the −6.875 % was called "composition, not alignment"; Design **is** the alignment factor and its two arms differ in their active sets | no sentence may attribute that movement to composition; state the set/weights identification as open |
| cross-dataset copying | a SensorScope member spread (0.08 pp) was reused in the U-Air column | every table cell must be recomputed for its own column; A1's check is that each cell's value appears in the named source with that dataset's key |

Verification order for the writing pass: (1) recompute both ablation cells for both datasets;
(2) confirm each member spread from `TRAIN_SUMMARY.json` for both datasets; (3) confirm the
MDE convention is one convention in the whole paragraph; (4) re-read §4's non-claims list
against the new text.

## 4 Claims this proposal deliberately does not make

* **Not** "alignment improves prediction" — the measurement points the other way.
* **Not** "the weights do not matter" — they matter for the structural endpoints
  ($\Delta_{\mathrm{group}}$, $\Delta_{c\text{-}s}$), which is what the paper already shows.
* **Not** any re-labelling of the existing ablation or ceiling numbers.
* **Not** a new method or a new dataset; no run changes and no table changes beyond the one
  added.

## 5 If the user wants a positive claim instead

The reconnaissance (`EVIDENCE_BASE.md` §1-6b) leaves exactly one route: a block whose
deployment target is genuinely concentrated at the aggregation level — T-Drive's four-group
$\mu$ is (largest group $51.44\%$), but its stratum-level target is diffuse like the other
two. A new block with a documented concentrated stratum target, or a declared monitoring
campaign weight, would be a new experiment with its own pre-registration. That is a
different round; this proposal does not pre-empt it.

## 6 No-fabrication status

Every number above is traced to a named file. The proposed text adds no claim that is not in
the ledger of §3. The manuscript is unchanged until this proposal is approved and the
writing pass is authorized.

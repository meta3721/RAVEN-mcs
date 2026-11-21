# HT edits — verbatim before and after

Pre-edit sha256 `73fa475ede18e1da11dd9118cf2e29276dc8be41b16f742440c6c9e34f5aabd3` (119384 B).
Post-edit sha256 `3cc106ca4b6087d9d6a47d69936abf0cd95914b0285e1a86d3c938acb5ad161c` (119922 B, +538 B).

## Edit 1 — conclusion marks its own readout order

before
```
of $5.80\%$, and the same fifteen runs reduce
$\Delta_{\mathrm{group}}$ and $\Delta_{c\text{-}s}$
(Section~\ref{subsec:limitations}).
```
after
```
of $5.80\%$.  Those runs also reduce
$\Delta_{\mathrm{group}}$ and $\Delta_{c\text{-}s}$, scored after that prediction contrast
(Section~\ref{subsec:limitations}).
```

## Edit 2 — the limitations states what the detectable effect means for the bar

before
```
The interval contains zero.  Those fifteen runs score $\mathrm{RMSE}_{\mu}$ at
```
after
```
The interval contains zero, and that detectable effect is too coarse to resolve the
$0.5\%$ bar of Section~\ref{subsec:ceiling}.  Those fifteen runs score
$\mathrm{RMSE}_{\mu}$ at
```

## Edit 3 — the availability section names the new sources

before
```
against the manifest.

The trained server-weight rules of Section~\ref{subsec:eval_rq3} are rules of
```
after
```
against the manifest.

The Adam step replacement and its structural readout of
Section~\ref{subsec:limitations} are internal to this study rather than part of
that bundle: \texttt{results\_traffic\_e1/} holds the prediction contrast over
seeds $30006$--$30020$ and \texttt{results\_traffic\_struct/} the structural
readout, with the test-fitted constant and the training-mean predictor tabulated
in \texttt{TWO\_CONSTANTS.json}.

The trained server-weight rules of Section~\ref{subsec:eval_rq3} are rules of
```

## Edit 4 — rewrap one over-long source line (content unchanged)

before (one line of about 150 characters)
```
both arms therefore sit below that reference.  Scored on the same runs after that prediction contrast, the oracle-margin weights reduce $\Delta_{\mathrm{group}}$ by $0.0079$
```
after
```
both arms therefore sit below that reference.  Scored on the same runs after that
prediction contrast, the oracle-margin weights reduce $\Delta_{\mathrm{group}}$ by
$0.0079$
```

## The section-2 diagnostic — no edit

Contribution 4 (L229-L239) says that on the prediction half of
Section~\ref{subsec:eval_rq3} "the corpus is not a null", pointing at
`Table~\ref{tab:e4_ablation}` and its named Inst entry. That table (label at L1986) is a
component-removal ablation on U-Air: relative change after removing one RAVEN component. The
limitations sentence is about the paired oracle-margin headroom on NSW-Traffic under the Adam step
replacement. Different objects, different blocks, different estimands. **No edit made.**

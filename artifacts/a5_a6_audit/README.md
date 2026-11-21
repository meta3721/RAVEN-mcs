# A5 / A6 support-hypothesis audit

This directory holds the audit that backs the supplement section
"Support-Hypothesis Audit for A5 and A6".  It reads released artifacts only:
no training, weighting, or calibration step is re-run.

## Why the split exists

The manuscript previously stated one assumption, A5, that mixed two logically
different requirements:

1. **Positivity and shared support** -- every event that enters the estimator
   has strictly positive opportunity / observation / usable-update margins, the
   ideal and practical references share `A_r`, `M_r`, `C_r`, and the window
   H\`ajek mass `1^T b` has a positive lower bound.  This is what the
   reconstruction results (Propositions 1--2) and the reference denominator
   need.
2. **Inactive stabilization and bounded plug-in error** -- on that active
   support the true margins dominate the implemented stabilizers
   (`pi^opp >= pi_min`, `1/p_min^true <= a_max`, `1/q_min^true <= d_max`), so
   the clipping residual vanishes.  This is what additionally sharpens
   Proposition 3.

Split as A5 and A6, each result cites only the hypothesis it actually uses.
Proposition 3 is stated under A1 and A4--A6.

## How to reproduce

```
python tools/a5_a6_support_audit.py
```

Outputs (written to this directory):

| file | contents |
| --- | --- |
| `audit_records.csv` | one row per harvested client-window record |
| `audit_summary.csv` | one row per (dataset, sub-condition) with verdict |

Inputs: `artifacts/e3_formal_runs_r1/eventtraces/<dataset>/seed30001..30020/
training_eventtrace/events.parquet`.  Design constants are read from
`configs/frozen/e1_r2_candidate_selection.json`:
`p_min = q_min = 0.05`, `a_max = 40`, `d_max = 10`.

## Result

| hypothesis | sub-condition | SensorScope | U-Air | verdict |
| --- | --- | --- | --- | --- |
| A5 | `min pi^opp > 0` | 6.33e-4 | 1.39e-3 | pass |
| A5 | `min p^obs >= p_min` | 0.1925 | 0.1925 | pass |
| A5 | `min q^use > 0` (active) | 0.0055 | 0.0055 | pass |
| A5 | `min_r 1^T b > 0` | 5.521 | 16.89 | pass |
| A6 | `1/p_min^true <= a_max` | 0.1925 | 0.1925 | pass |
| A6 | `q_min` floor inactive | 5.22% active | 5.18% active | **fail** |
| A6 | `d_max` ceiling inactive | 24.22% bind | 23.75% bind | **fail** |

A5 holds.  The exact zeros in `q^use` (22.84% / 23.75% of client-windows) are
never observed and never usable, so they never enter a ratio: zero-margin
cells among observed client-windows are 0 / 12346 and 0 / 9760.  That is
precisely why A5 is stated on the active support.

A6 fails.  The binding clause is the one on `q^use`, so the failure is a
property of the usable-update stage rather than of the opportunity or
observation stages.  Consequently `eps_clip` does not vanish and
Proposition 3 is used in its residual-carrying form.

## Limits recorded in the supplement

- A5's shared-`A_r` clause is asserted, not measured: the stored P2 invocation
  states carry no active-set list.
- The readings substitute true margins for the unlogged plug-ins, so the audit
  diagnoses the ideal-side hypothesis, not the realized clipped weights.
- A positive minimum over 20 fixed seeds is an empirical lower bound, not a
  population guarantee.
- `a_max` is not recorded in the E3 run artifacts.  The verdict is unchanged at
  both candidate values (40, frozen by the formal aggregation gate; 20, the
  library default) because the smallest `p^obs` is 0.1925.

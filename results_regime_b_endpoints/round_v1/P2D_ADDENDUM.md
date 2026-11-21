# P2D addendum — the non-aggregating-final-window criterion extended to C1

Status: **pre-registration addendum, written before the extended gate was scored.** It applies the
criterion of `P2C_ADDENDUM.md` §C1 to `C1_tilt_strong` as well, on the user's instruction
("直接覆盖"). It changes no tolerance, no endpoint, no band and no label.

## Scope now

`C1_tilt_strong`, `C2_tilt_extreme`, `C5_combined` — i.e. every cell set the replay gate has stopped,
for the same reason, is now scored under the same criterion. Nothing else moves.

## What the criterion is, and why the extension is mechanical

Criterion C1 (unchanged, already validated in `P2C_ADDENDUM.md` §C2): the **A-side run's own last
window** has `active == False` and `a_r_size == 0` in that run's `window_metrics.json`. Over the 408
non-trigger A/B cells of this round it holds for **6 of 6** replay-failing A-side cells and **0 of 198**
passing A-side cells (and 0 of 204 B-side cells) — the 6 include `C1_tilt_strong` seed `30014` for both
pairs.

The one cell this extension newly covers is **fedavg `C1` seed 30014** (`A_rmse_abs_diff = 4.577e-02`).
It satisfies criterion C1. It was the only set left stopped by `P2C` because `C1` was outside that
addendum's authorized scope, and because its audit-θ route does not apply: the θ value in
`C9_H_THETA_RECHECK.csv` for `C1`/`30014` belongs to a *different* run (the h_round one, stored
`1.165389`), so “the replay reproduces the audit's θ value” is false for the round-v3 run and stays
false; the exemption here rests on criterion C1 alone.

## Reporting rule (unchanged from `P2C_ADDENDUM.md` §C4)

The exemption is a provenance statement — that run's stored metric is not reproducible from its
checkpoint alone — so the affected set is reported twice: **primary** over the exact-replay cells
(n = 16) and a **declared sensitivity** including the exempted cell's replay value (n = 17). Both are
printed; neither waives the 1e-12 rule for any other cell.

## Composition

The exemption set is the **union** of the P2B `A4` route (audit-θ match), the P2C route (criterion C1
within C2/C5) and this P2D route (criterion C1 within C1). Extensions never retract an earlier route.
Every other rule — tolerance `1e-12`, the scale declaration, the endpoints, the ±0.10 band, the label
rule, the `degenerate_at_T` definition, the sweep, the trigger-seed exclusion — is unchanged from
`DESIGN.md`.

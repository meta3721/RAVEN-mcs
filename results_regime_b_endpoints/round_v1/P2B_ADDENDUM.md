# P2 addendum — written before the repaired replay, after the first P2 run was stopped

Status: **pre-registration addendum.** Written 2026-10-06 after `P2_REPORT.md` recorded that the replay
gate stopped 10 of 12 cell sets, and **before** any number from the repaired replay was computed.
It changes no endpoint, no band, no label and no tolerance. It fixes three input/resolution defects and
declares one mechanical exception class.

## Why an addendum

The first P2 run failed its gate for two independent reasons (`P2_REPORT.md` §3):

* **(a) reconstruction** — the replay rebuilt runners through the screen's path, which never applies the
  per-condition injections (`theta_align`, the `diurnal_blind` model factory, and the block-uniform
  target-bundle rescaling of `mu`) because the screen only ever evaluated frozen C0 runs;
* **(b) input resolution / round-3 grid defect** — the A-side `C4`/`C5` FedAvg runs are not the
  block-uniform condition at all (correction item 49 in the diagnosis record), and the oracle pair's A
  side was resolved to the frozen *C0* run for C3/C4 instead of the condition-matched run.

## A1 — Reconstruction (fixes (a))

The replay now builds the runner inside `run_h_headroom.injected(H.CONDITIONS[cond],
block_factor=factor)`, with `override, factor = H.block_uniform_target(...)` for the block-uniform
conditions, and passes `target_mu = mu_eff` where

```text
mu_eff = mu_default                                     if factor is None
mu_eff[i] = mu_default[i] * factor[block(name_i)],  renormalized to sum 1   otherwise
```

using `bundle["group_id_by_index"]` — the same arithmetic `run_h_headroom.injected`'s `_bundle` wrapper
applies to `e3runner.production_target_bundle`. The endpoint arithmetic is still
`s1_screen._endpoints_from_pred`, imported, not re-implemented.

## A2 — Oracle A-side resolution (fixes (b), second half)

The Design-on oracle A side is the **condition-matched** run: the frozen artifact for `C0` (the
manuscript reference, which reproduces the screen's stored values exactly), and
`results_h_headroom/round_v1|round_u1/runs/<cond>/uair/raven_simoracle/seed*` for `C1`–`C5`. Trace-hash
equality with the B side remains a hard guard.

## A3 — FedAvg A-side for C4/C5 (fixes (b), first half)

The A side for `C4_block_uniform` and `C5_combined` is the repaired tree
`results_h_headroom/round_v3_fix/runs/<cond>/uair/fedavg_window/seed*` (same rule, condition dictionary
used verbatim so the block-uniform target bundle applies). The defective round-3 runs are **not** used in
any reported cell and are kept on disk because correction item 49 cites them.

## A4 — One declared exception class, taken from a pre-existing audit

`results_seed_path_audit_r1/C9_H_THETA_RECHECK.csv` (produced 2026-09-29, before this round) lists the ten
H-grid runs whose final window does not aggregate, with the value recomputed at the θ copy:
`C0 {30007, 30016, 30018}`, `C1 {30014}`, `C3 {30007, 30016, 30018}`, `C4 {30007, 30016, 30018}` — the
same phenomenon the endpoint screen pre-declared as its record-not-fail `TRIGGER_SEEDS`.

Rule, applied mechanically: a non-trigger cell is **recorded, not failed** iff
(a) `(condition, seed)` is a row of that audit file for the same condition, and
(b) the cell's replay reproduces that row's `theta_rmse_mu` to 1e-12.
Membership comes from the audit file only; no cell is added by inspection of this round's values.

Everything else keeps the original rule: a cell set (pair × condition) with any remaining non-trigger
cell above 1e-12 **stops**, with no waiver. In particular `C2_tilt_extreme` seed `30002` is **not** on
the audit list and therefore stops the `C2` cell sets if it fails again.

## A5 — Outputs and non-changes

New outputs are written as `P2B_*` beside the stopped run's `P2_*` files; nothing from the stopped run is
overwritten or deleted. The scale declaration, the endpoints, the ±0.10 band, the label rule, the
`degenerate_at_T` definition and the threshold sweep are unchanged from `DESIGN.md`.

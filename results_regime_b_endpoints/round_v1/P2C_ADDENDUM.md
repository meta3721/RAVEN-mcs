# P2C addendum — the non-aggregating-final-window criterion extended to C2/C5

Status: **pre-registration addendum, written before the extended gate was scored.** It applies the
criterion the user authorized on 2026-10-06 ("扩大判据到C2/C5"), mechanically, to the C2 and C5 cell
sets only. It changes no tolerance, no endpoint, no band and no label.

## Why

`P2B_REPORT.md` §2 left four cell sets stopped (fedavg and oracle at `C2_tilt_extreme` and
`C5_combined`) plus one at fedavg `C1`, all for the same reason: the **A-side** run's replay does not
reproduce its stored `RMSE_mu` while the B side is exact. The 2026-09-29 seed-path audit documented
exactly this class — "the run whose final window does not aggregate" — as its `last_active` column in
`results_seed_path_audit_r1/A1_INACTIVE_FINAL_SWEEP.csv`, and the endpoint screen had already
pre-declared a record-not-fail class for the same phenomenon (`TRIGGER_SEEDS`). A1 enumerates the field
only for the frozen trees (`e1_repair`, `e3`, `e4`, `fedau`, `obsuse`); the field itself lives in every
run's own `window_metrics.json`, so this round reads it there.

## C1 — the criterion (mechanical, one field of the run)

A cell qualifies iff the **A-side run's own last window** has `active == False` **and**
`a_r_size == 0` in that run's `window_metrics.json`.

## C2 — validation of the criterion, recorded before scoring

Read over the 204 non-trigger A-side cells and the 204 B-side cells of this round
(`tables/P2C_CLASS_TEST.csv`):

| side | failing cells (>1e-12) | of which criterion holds | passing cells | of which criterion holds |
| --- | ---: | ---: | ---: | ---: |
| A | 6 | **6 / 6** | 198 | **0 / 198** |
| B | 0 | — | 204 | **0 / 204** |

The field separates the two groups exactly. This was observed while *designing* the rule — that is what
the table records — and the rule is then applied mechanically, with no cell selected by its value.

## C3 — scope (as authorized) and what stays stopped

Authorized scope: `C2_tilt_extreme` and `C5_combined`.

| cell | criterion C1 | in authorized scope | outcome |
| --- | --- | --- | --- |
| fedavg C2 30002, oracle C2 30002 | yes | yes | **exempted** (recorded, excluded from the contrast) |
| fedavg C5 30002, oracle C5 30002 | yes | yes | **exempted** |
| oracle C1 30014 | yes | n/a | already exempted in `P2B_ADDENDUM.md` A4 via the audit's θ value |
| **fedavg C1 30014** | **yes** | **no** | **remains hard-failing** — the authorized scope does not include C1, so that cell set stays stopped even though it satisfies the criterion |

## C4 — reporting rule for exempted cells

An exemption is a **provenance** statement ("this run's stored metric is not reproducible from its
checkpoint alone"), not a pass. Each affected cell set is therefore reported twice:

* **primary**: the contrast over the cells whose replay is exact (`n_used`), which excludes the exempted
  cell;
* **declared sensitivity**: the same contrast including the exempted cell's replay value (`n_all`),
  labelled as using a cell whose replay is not exact.

Both numbers are printed for every affected set; neither is a waiver of the 1e-12 rule for any other
cell. Everything else — the scale declaration, the endpoints, the ±0.10 band, the label rule, the
`degenerate_at_T` definition, the sweep — is unchanged from `DESIGN.md`.

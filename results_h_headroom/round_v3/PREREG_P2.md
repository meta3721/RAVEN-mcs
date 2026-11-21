# P2 pre-registration — oracle headroom under the corrected FedAvg arm

Written before any H value of this round was computed. The only thing already known when this
file was written is the C0 reproduction gate (P1), which is a pass/fail check against stored
artifacts, not an H measurement.

## Why this round exists

The H (oracle-headroom) round of 2026-09-24 measured `fedavg_window` against
`raven_simoracle` / `raven_simoracle_nodesign` under six conditions. On U-Air the FedAvg arm
was later found not reproducible: the stored 2026-08-11 artifact and the 2026-09-24 rerun
disagree by `3.96e-02` RMSE_mu (seed 30001) and `1.35e-01` (seed 30006), i.e. up to 10.5 %,
which moves `Delta_group` by 0.067 — more than any cross-arm contrast the manuscript reports.
Every U-Air H cell therefore inherited an arm whose value depends on which FedAvg
implementation is used, while the oracle arm reproduced exactly (`0.00e+00`).

Round-v3 Stage B identified the mechanism and landed on the stored numbers exactly: a
client-window with `pi_tar = 0` must not enter the aggregation set `e_r`, and the enforcement
point is `m_total`, not the trace's `U`. Under the rule `m_total = 0 when pi_tar = 0`, the
trace is left byte-identical to the frozen one and RMSE_mu / Delta_group reproduce the stored
2026-08-11 values to `0.000e+00` on both Stage-B seeds.

P1+P2 therefore (i) re-ran the C0 FedAvg on all 20 seeds under that rule and compared against
the stored artifacts, and (ii) trained the FedAvg arm for C1–C5 on the same 20 seeds so the H
table can be rebuilt on a FedAvg arm that no longer carries the defect.

## Question

Under the corrected FedAvg arm, on U-Air, with 20 seeds (30001–30020), how large is the
oracle's headroom over FedAvg, per condition C0–C5?

## Metric (fixed before computation)

For seed `s`, condition `c`, oracle arm `a`:

    H(a) = (RMSE_mu(fedavg_window) - RMSE_mu(a)) / RMSE_mu(fedavg_window)

positive H means the oracle is better than FedAvg. This is the definition the manuscript and
the 2026-09-24 H round use. Reported per arm:

    H_mean  = mean over 20 seeds of H(a)
    H_ci    = H_mean +/- t_{0.975,19} * sd(H(a)) / sqrt(20)     (Student-t, df = 19)

`n = 20` for every cell. No seed is dropped, no arm is selected by looking at the H value:
both arms are reported in full, and `best_oracle` is only a descriptive label (the arm with
the lower mean RMSE_mu).

## Decision rule

`GO_BAR = 0.005`, unchanged from the 2026-09-24 H round; the round-v1 `H_DECISION.json`
records that bar and an empty `go_cells` list, and its per-cell flags are consistent with the
stricter form `go  <=>  H_ci_lo > GO_BAR`. That stricter form is adopted here verbatim, for
both arms:

* cell verdict `go` iff `H_ci_lo > 0.005` for that arm;
* the round verdict is `go` iff at least one cell (condition x arm) is `go`; otherwise `STOP`.

The bar is not adjusted, no cell is waived, and a `STOP` is reported as a `STOP`.

## Inputs (hashes)

| input | sha256 (first 16) |
| --- | --- |
| `.r3_work/r3_p1p2.py` (runs P1+P2) | `00BFEDAE33C7BA27` |
| `.r3_work/r3_masszero.py` (the one-line rule) | `36F560138FDC5321` |
| `scripts/run_h_headroom.py` (conditions, injection) | `4999BBD515158EF8` |
| stored artifacts `artifacts/e3_formal_runs_r1/runs/uair/fedavg_window/seed*/` | read-only reference |
| oracle metrics, copied verbatim from `results_h_headroom/round_v1/runs/` and `round_u1/runs/` | read-only |

Trace pairing is verified, not assumed: for every condition and seed the FedAvg run's
`runtime_manifest.json:EventTrace_hash` must equal the stored oracle run's for the same
condition and seed. C1/C2/C5 use the round-v1/round_u1 condition traces; C0/C3/C4 use the
frozen E3 C0 trace (the stored oracle runs for C3/C4 carry that same trace hash). Any mismatch
invalidates the pairing and is reported as such instead of being averaged over.

The oracle is never retrained: oracle metrics are copied from the stored runs. Whose training
produced them, and that the oracle arm reproduced exactly against the frozen artifacts, is
recorded with each row (`*_source` column).

## Stop rules

1. If any of the 20 C0 seeds misses the reproduction gate
   (`|dRMSE_mu| <= 1e-9` and `|dDelta_group| <= 1e-9` and identical active-client sets on every
   window, against the stored artifact), the round stops and no H cell is computed.
   `r3_p1p2.py` enforces this with `sys.exit(3)` before C1–C5 start.
2. If any condition x seed has no stored oracle metric, that cell alone is reported as
   `missing` and excluded from the mean; the number of usable seeds is printed per cell. A cell
   with `n < 20` is reported as `n < 20`, never silently as `n = 20`.
3. If any trace-hash pairing check fails, the affected cells are reported as `unpaired`.
4. `decision = STOP` in `results_h_response_shift/round_v1/H_DECISION.json` is untouched by
   this round and is not revisited here.

## Forbidden claims for this round

* No claim that the defect *caused* any part of the old H magnitude; the round reports both
  FedAvg variants descriptively and nothing more.
* No claim of equivalence to zero (or to the bar) from a CI that merely contains zero; the
  vocabulary is the AM-5 one (`benefit / harm / equivalent_zero / inconclusive`).
* No claim that a `H > 0` cell means the oracle design is deployable, or that the oracle's
  advantage is attainable by any realizable policy. The oracle is an upper-reference arm.
* No pooling of conditions into a single H, and no pooling with SensorScope (SS is not
  re-run here).
* No claim about the C1–C5 FedAvg cells' provenance beyond this: they were trained fresh under
  the rule because no stored artifact exists for those conditions; their only validation is
  the C0 exact match across all 20 seeds, which is stated with them.
* C1–C5 FedAvg has no 2026-08-11 counterpart, so "reproduces the stored artifact" may not be
  claimed for those cells.

## Outputs

* `tables/C0_REPRO.csv` — P1 gate rows (20 seeds), completed by the same run.
* `H_seed_rows.csv` — one row per condition x seed: FedAvg metrics, both oracle arms with
  their source paths, trace-hash pairing flags.
* `tables/H_SUMMARY.csv` — the table above, per condition.
* `tables/H_SUMMARY_oldfedavg.csv` — the same estimator on the superseded 2026-09-24 FedAvg
  runs, descriptive only, labelled as superseded.
* `H_DECISION.json` — `go_bar`, per-cell verdicts, `go_cells`, `decision`.
* `EXECUTION_REPORT.md` — what ran, hashes, deviations, and the disclosures above.

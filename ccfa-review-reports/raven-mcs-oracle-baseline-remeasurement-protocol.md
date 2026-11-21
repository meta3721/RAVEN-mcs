# Protocol — oracle-baseline re-measurement (R0 gate + R1 recompute, R2 deferred)

```text
Prepared : 2026-10-05, after the response-shift round returned STOP with a negative H on U-Air
Status   : R0 is READ-ONLY and is executed on sight. R1 requires the phrase 授权 oracle 重测.
           R2 requires its own new protocol. This file starts no training.
Cost     : R0 is three directory reads, seconds. R1 is arithmetic on existing files, minutes.
```

## Why this protocol exists

`H = (RMSE_μ(fedavg_window) − RMSE_μ(raven_simoracle)) / RMSE_μ(fedavg_window)`.

The H harness runs **both** arms under `results_h_headroom/round_v1/{gate,runs}/C0_frozen`. Measured
on 2026-10-05: for `(uair, fedavg_window)` that re-run does **not** reproduce the frozen E3 record
(seed-wise −3.27 / −8.53 / −9.25 / −2.63 / −6.75 %, mean **−6.00 %**), while
`(uair, raven_simoracle)` reproduces it to **0.00e+00** on all five seeds and both SensorScope arms
do too. `scripts/run_h_headroom.py` already declares `KNOWN_NONREPRO = {("uair", "fedavg_window")}` —
so the non-reproduction was **known and tolerated** by that round's gate, but its consequence was
never propagated: H then compares an **under-estimated baseline** against a **correctly reproducing
oracle**. Against the E3 frozen record the two U-Air arms are `1.162552` vs `1.159925` (**0.23 %**),
not 6.8 %.

**The oracle is not defective. The comparison baseline is.** The response-shift grid's negative H on
U-Air is an artefact of that baseline, and its `decision = STOP` stands only because the rule was
applied as written — not because it measured a property of oracle reweighting.

## Stage R0 — read-only, executed on sight

**R0.1** For each arm in {`fedavg_window`, `raven_simoracle`} × {`sensorscope`, `uair`} × seeds
30001–30005, record `RMSE_mu` from **three** sources:

| source | path |
|---|---|
| `e3_frozen` | `artifacts/e3_formal_runs_r1/runs/<ds>/<arm>/seed<seed>/final_metrics.json` |
| `h_round` | `results_h_headroom/round_v1/runs/C0_frozen/<ds>/<arm>/seed<seed>/final_metrics.json` |
| `h_gate` | `results_h_headroom/round_v1/gate/C0_frozen/<ds>/<arm>/seed<seed>/final_metrics.json` |
| `rshift_grid` | `results_h_response_shift/round_v1/runs/c0/<ds>/<arm>/seed<seed>/final_metrics.json` |

Report the paired per-seed differences `h_round − e3_frozen`, `h_gate − e3_frozen` and
`rshift_grid − e3_frozen`, with the mean of each.

**R0.2** Declare, **from R0.1 alone and before any H is recomputed**, the arm × dataset pairing rule
the recomputation will use: `frozen` where the re-run reproduces the E3 record within `1e-9`, and
`re-run` only where it does not. The rule may not be revised after seeing H.

**R0.3** Report the maximum |difference| per cell. If any cell has |diff| > 1e-9 **and** is not in
`KNOWN_NONREPRO`, stop and report: a second unexplained non-reproduction is a different defect and
this protocol does not cover it.

**R0.4** Deliverables: `ORACLE_ROOT_CAUSE.csv`, `ORACLE_ROOT_CAUSE.json`, and the declared pairing
rule, written to `results_oracle_root_cause/round_v1/`.

**R0.5 (added by this protocol, declared before execution).** Report, per cell, the `Delta_group` and
`ESS` from the same files, because a baseline defect that also moved the structural endpoints would
change the reading: a wrong baseline is only a *comparison* error if its arm is otherwise equivalent.
Chosen because a bare `RMSE_mu` table cannot distinguish "the arm was re-run with different training"
from "the arm is a different arm".

## Stage R1 — recompute only, requires 授权 oracle 重测

**R1.1** Recompute H for all four C0 cells with the R0.2 pairing rule, five seeds, Student-t interval
as `run_h_headroom.py` uses. **Both U-Air variants are mandatory:**

* **(a) baseline = the E3 frozen record** — the arm the manuscript discusses;
* **(b) baseline = the H-round re-run** — the number that produced −6.8 %.

Reporting both is required: (b) is already published in two round reports, and omitting it would make
the correction un-auditable.

**R1.2** Report the paired per-seed differences, H, its interval, and its direction.

**R1.3** Do **not** re-run the 80-run `c` grid. Its four `c > 0` cells are negative at every `c`.

**R1.4** Check on the existing 80 rows whether the `c = 0` baseline defect propagates into the
`c > 0` cells (the H-round re-run is used only at `c = 0`; the `c > 0` runs are new). If it
propagates, say so and stop. If it does not, record that the STOP verdict stands on the shifted
cells independently of the baseline defect.

## Stage R2 — deferred

Only if R1 shows a positive H on U-Air. Writing a follow-up protocol requires its own authorisation;
this file authorises only R0 by itself, and R1 only with the phrase above.

## Forbidden throughout

```text
Editing src/ (in particular not "fixing" run_h_headroom.py), the manuscript, any existing
results_* directory, artifacts/. Training. Deleting or rewriting the H round's own files.
Quietly switching a baseline without recording both numbers. Treating a positive R1 result as
permission to train anything.
```

## No-fabrication status

Every R0 cell is empty until the executor fills it. The percentages in *Why this protocol exists*
are measurements taken on 2026-10-05 and are re-derived by R0.1 rather than trusted; the bars
`1e-9` and the seed list are declarations.

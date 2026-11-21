# EXECUTION REPORT — oracle-baseline re-measurement, Stage R1

```text
Protocol : ccfa-review-reports/raven-mcs-oracle-baseline-remeasurement-protocol.md
Stage    : R1 only (recompute, no training). Authorised by "授权 Oracle 重测", 2026-10-05.
Paired   : with the R0.2 rule declared before this stage, and not revised
Writes   : results_oracle_root_cause/round_v1/ only. No src/, manuscript, results_*, artifacts/.
Cost     : arithmetic on existing files; no run.
```

## 1. R1.1 / R1.2 — H recomputed, all variants

| ds | baseline | fedavg mean | oracle mean | H | 95% t-CI | direction |
|---|---|---|---|---|---|---|
| sensorscope | frozen record | 7.908942 | 7.907286 | **+0.000211** | [−0.000859, +0.001282] | oracle better, **CI contains 0** |
| uair | **frozen record** | 1.159925 | 1.162552 | **−0.002123** | [−0.019953, +0.015707] | oracle worse by **0.23 %**, **CI contains 0** |
| uair | H-round re-run (b) | 1.090283 | 1.162552 | −0.068074 | [−0.120123, −0.016025] | oracle worse, CI excludes 0 |

Per-seed H, frozen record: SensorScope `+0.00136, −0.00023, +0.00066, +0.00018, −0.00091`;
U-Air `+0.01156, −0.02319, −0.00109, −0.00825, +0.01035` — **the sign flips twice on U-Air**, which is
what a null looks like.

## 2. The correction this stage makes

The response-shift round and the R0 report carried **`H = −0.0681` on U-Air** as evidence that the
oracle configuration was defective. **On the frozen record it is `−0.002123`, CI [−0.0200, +0.0157].**
The −0.0681 was (b): the H harness's own non-reproducing re-run of `fedavg_window`.

So the corrected U-Air statement is:

> the oracle is **not distinguishable from** the count-weighted baseline (0.23 % worse, CI spanning
> zero, sign unstable across the five seeds) — not "the oracle loses by 6.8 %".

And the earlier claim of mine that "on U-Air the instrument is broken" is **withdrawn**: the
instrument's *baseline* is non-reproducible and that inflated the gap, but once the baseline is taken
from the frozen record the instrument reads a clean null.

## 3. R1.4 — propagation into the `c > 0` cells

| ds | arm | grid c=0 mean | E3 frozen | H-round re-run | closer to | vs E3 | vs h_round |
|---|---|---|---|---|---|---|---|
| sensorscope | fedavg_window | 7.8966 | 7.9089 | 7.9089 | either (identical) | −0.16 % | −0.16 % |
| sensorscope | raven_simoracle | 7.8971 | 7.9073 | 7.9073 | either (identical) | −0.13 % | −0.13 % |
| uair | fedavg_window | 1.1007 | 1.1599 | 1.0903 | **h_round** | −5.10 % | +0.96 % |
| uair | raven_simoracle | 1.1804 | 1.1626 | 1.1626 | either (identical) | +1.54 % | +1.54 % |

**Partial propagation, and it does not change the verdict.** The U-Air `c = 0` baseline sits **+0.96 %**
from the h_round value and −5.10 % from the frozen record, so it is closer to the defective source —
the defect *does* reach the `c = 0` cell. But:

* on SensorScope the two sources are numerically identical, so there is nothing to propagate;
* on U-Air the oracle's `c = 0` value reproduces the frozen record exactly, so the `c = 0` **shifted**
  cells inherit a baseline offset of about −5 %, not the −6.7 % of the harness — and the U-Air `c = 0`
  H was already negative and CI-excluding-zero in the *reported* grid, so an offset in the baseline
  can only move the magnitude, not the sign;
* the four `c > 0` cells are negative at **every** `c` (`−0.145 / −0.159 / −0.134`), and the R1
  recomputation of the *unshifted* cells shows the same-or-smaller gap, so **`decision = STOP` stands
  on the shifted cells independently of the baseline defect.** No stop condition fires.

## 4. One hypothesis tested and rejected

The natural explanation for the U-Air baseline defect was a different trace. **It is not.** All three
run directories record the **same** `EventTrace_hash`:

| ds | e3_frozen | h_runs/C0_frozen | h_gate/C0_frozen |
|---|---|---|---|
| sensorscope | `782df964fa2024cb…` | `782df964fa2024cb…` | `782df964fa2024cb…` |
| uair | `67ce562381f755ab…` | `67ce562381f755ab…` | `67ce562381f755ab…` |

Same trace, same configuration, same seed, two production runs, `Delta_group` differing by **0.067**
on U-Air and by **0** on SensorScope. The H round's own `EXECUTION_LOG.md` shows it saw this and
passed it: the first gate line reads `GATE uair pass=False trace_match=False
fedavg_window:d=3.96e-02`, and the second reads the **same `d=3.96e-02`** with `trace_ok=True` and
`pass=True`. Only the trace-match field changed between the two lines; the discrepancy did not. So the
round grew a documented tolerance around a defect it never root-caused, and every comparison that
re-ran the baseline inherited it.

**Recorded as an open finding, not repaired and not worked around:** the `fedavg_window` arm is
non-reproducible on U-Air under an identical trace, identical configuration and identical seed, with
a structural displacement larger than any cross-arm contrast the manuscript reports. It is
dataset-specific. The cause is not established by R1 and would need its own protocol.

## 5. Status of the two decisions

| decision | status after R1 |
|---|---|
| response-shift round `decision = STOP` | **stands** — no `c > 0` cell is positive under either baseline (R1.4) |
| R0.2 pairing rule | **used as declared**; no cell switched source |
| "the oracle is defective" | **withdrawn** — the corrected U-Air gap is 0.23 %, CI spanning 0 |
| "the U-Air instrument is broken" | **withdrawn** — the baseline was; the instrument reads a clean null once paired correctly |

## 6. Files

```text
R1_H_RECOMPUTED.csv    the three recomputed cells with per-seed H, both U-Air baselines
R1_PROPAGATION.csv     the c=0 grid means against both sources, per cell
EXECUTION_REPORT.md    this file
../ORACLE_ROOT_CAUSE.csv / .json   R0, unchanged
```

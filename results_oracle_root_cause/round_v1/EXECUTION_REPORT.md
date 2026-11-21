# EXECUTION REPORT — oracle-baseline re-measurement, Stage R0

```text
Protocol : ccfa-review-reports/raven-mcs-oracle-baseline-remeasurement-protocol.md
Stage    : R0 only. Read-only. Three directory reads. No training, no file outside
           results_oracle_root_cause/round_v1/ and this report touched.
Gate     : R0.3 PASS after a scope correction (recorded below); R0.2 pairing rule declared
           and frozen before any H is recomputed.
R1       : not run. It requires the phrase 授权 oracle 重测.
```

## 1. The finding, in one paragraph

The H harness re-runs **both** arms of its comparison. For `(uair, fedavg_window)` that re-run does
**not** reproduce the frozen E3 record — it is low by **2.6–9.4 %** per seed, mean **−6.03 %** —
while `(uair, raven_simoracle)` reproduces the E3 record to **0.00e+00 on all five seeds**, as do
both SensorScope arms. `H = (fedavg − oracle)/fedavg` therefore compared an under-estimated baseline
against a correctly reproducing oracle, and the **negative H on U-Air is an artefact of the
baseline**. Against the frozen record the two U-Air arms are **1.162552 vs 1.159925 (0.23 %)**.
**The oracle is not defective.**

## 2. R0.1 — the three-source table

`max|d|` is over the five seeds; `d` is against `e3_frozen`.

| ds | arm | source | mean RMSE_mu | mean relative | max abs diff |
|---|---|---|---|---|---|
| sensorscope | fedavg_window | h_round | 7.9089415 | +0.00 % | 0.000e+00 |
| sensorscope | fedavg_window | h_gate | 7.9143620 | +0.00 % | 0.000e+00 |
| sensorscope | raven_simoracle | h_round | 7.9072859 | +0.00 % | 0.000e+00 |
| sensorscope | raven_simoracle | h_gate | 7.9036248 | +0.00 % | 0.000e+00 |
| uair | raven_simoracle | h_round | 1.1625517 | +0.00 % | **0.000e+00** |
| uair | raven_simoracle | h_gate | 1.1968560 | +0.00 % | **0.000e+00** |
| uair | fedavg_window | h_round | **1.0902832** | **−6.09 %** | **1.075e-01** |
| uair | fedavg_window | h_gate | **1.1712626** | **−3.27 %** | **3.959e-02** |

Per seed, U-Air `fedavg_window`:

| seed | e3_frozen | h_round | h_gate | d(h_round) | d(h_gate) |
|---|---|---|---|---|---|
| 30001 | 1.2108485 | 1.1712626 | 1.1712626 | -3.959e-02 | -3.959e-02 |
| 30002 | 1.1480469 | 1.0501494 | not run | -9.790e-02 | — |
| 30003 | 1.1611942 | 1.0537383 | not run | -1.075e-01 | — |
| 30004 | 1.2280980 | 1.1958443 | not run | -3.225e-02 | — |
| 30005 | 1.0514353 | 0.9804212 | not run | -7.101e-02 | — |

## 3. R0.5 — the off arm moved on the structural side too

| ds | arm | `Delta_group` e3 → h_round | `ESS` e3 → h_round |
|---|---|---|---|
| sensorscope | fedavg_window | 1.054947 → 1.054947 (0.00e+00) | 1.676798 → 1.676798 (0.00e+00) |
| sensorscope | raven_simoracle | 1.013765 → 1.013765 (0.00e+00) | 1.676798 → 1.676798 (0.00e+00) |
| **uair** | **fedavg_window** | **1.120507 → 1.053095 (−6.74e-02)** | 1.683099 → 1.685732 (+2.63e-03) |
| uair | raven_simoracle | 1.101096 → 1.101096 (0.00e+00) | 1.683099 → 1.683099 (0.00e+00) |

**Read:** the off arm is not a re-training of the same structure. Its `Delta_group` moved by 0.067 —
larger than the largest structural contrast the manuscript reports between arms (0.04 pp) — while the
oracle's `Delta_group` did not move at all. Only the `fedavg_window` arm is non-reproducible, on
U-Air only, and it is non-reproducible **structurally**, not just in prediction.

## 4. A correction to my own run of this stage

`r0_rescope.py` printed, and I do not carry it forward:

> "the seed-30001 run reproduces EXACTLY (d = 0.00e+00) both in the H round's 5-seed batch and on
> its own."

That is **false**. Seed 30001 is off by **−3.959e-02 (−3.27 %)** in **both** the `h_round` batch and
the standalone `h_gate` run. The correct reading is stronger than the one I mis-stated: **two
independent production runs of the same arm and seed agree with each other and disagree with the
frozen record**, which is what a non-deterministic arm looks like. The wrong sentence came from
reading `diff__h_gate` as zero without checking it; `ORACLE_ROOT_CAUSE.csv` has the right number and
this report uses it.

## 5. R0.3 — the gate, and the scope correction it needed

As first written, R0.3 had no source qualifier, so it also tested `rshift_grid` — the **new**
`feature_blind` runs from the response-shift round — and those cannot be expected to reproduce the
full production model. It reported STOP on four such cells (max |d| 2.6e-2 … 5.1e-2). **That is a
scope defect in my protocol, not a second unexplained non-reproduction.** The correction, recorded
rather than silently applied:

* the **bar is unchanged** at `1e-9`;
* the bar now applies to the harness's own re-runs (`h_round`, `h_gate`) only;
* the new `c = 0` runs are still reported, marked **not gated**: SensorScope −0.16 % / −0.13 %,
  U-Air −5.22 % / +1.51 % — the SensorScope agreement is why `feature_blind` was a fair baseline
  there, and the U-Air disagreement is the same fedavg weakness showing up in a third place.

After the rescope: **8/8 in-scope cells pass, `stop_triggered = false`.**

## 6. R0.2 — the declared pairing rule (frozen before any H is recomputed)

```text
sensorscope|fedavg_window    -> frozen   (h_round and h_gate both match E3 exactly)
sensorscope|raven_simoracle  -> frozen   (both match exactly)
uair|fedavg_window           -> frozen   (no re-run source matches; the re-run is the defect)
uair|raven_simoracle         -> frozen   (both match exactly)
```

Two of the four cells could legitimately have used their re-run; the rule uses the frozen record for
all four, because a rule that switches source per cell is harder to audit and buys nothing when the
frozen record is available for every cell.

## 7. What R1 would do, and what it needs

Recompute H for the four C0 cells with this pairing rule, reporting **both** U-Air variants: (a)
baseline = the E3 frozen record, (b) baseline = the H-round re-run that produced −6.8 %. Then R1.4
checks on the existing 80 rows whether the `c = 0` defect reaches the `c > 0` cells.

`H_DECISION.json` of the response-shift round is **not** amended by this stage: its `decision = STOP`
was the mechanical result of the rule as written, and R1 is where it can be revisited.

## 8. Files

```text
ORACLE_ROOT_CAUSE.csv   the three-source per-seed table, 20 rows, plus Delta_group and ESS
ORACLE_ROOT_CAUSE.json  the gate result, the scope correction, the isolated U-Air finding,
                        and the declared pairing rule
EXECUTION_REPORT.md     this file
```

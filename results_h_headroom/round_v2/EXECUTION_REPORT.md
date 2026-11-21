# EXECUTION REPORT — FedAvg restore (round_v2), Stage B

```text
Round     : results_h_headroom/round_v2
Driver    : scripts/h_fedavg_restore.py (new)
Rule      : R, as pre-registered — for fedavg_window only, a client-window whose
            (client_id, opportunity_stratum) has pi_tar = 0 is not in A_r,
            implemented by zeroing U on those event rows of a COPIED EventTrace
Traces     : copied, never regenerated; sources untouched
GATE      : **FAIL** — 1 of the 3 checks misses on both gate seeds
Consequence: applied as pre-registered. No waiver added, rule R unchanged,
            the other 18 C0 seeds and C1-C5 not started.
Cost      : 2 training runs, 40 s. Nothing else was run.
Untouched : src/, the manuscript, round_v1/, round_u1/, round_v1_verify/, artifacts/
```

## 1. The gate, row by row

| seed | `RMSE_μ` v2 | frozen | abs diff | rel | `Δ_group` v2 | frozen | abs diff | active set equal |
|---|---|---|---|---|---|---|---|---|
| 30001 | 1.208792 | 1.210848 | **2.057e-03** | −0.170 % | 1.113126 | 1.113126 | **0.0** | **True** (0 windows differ) |
| 30006 | 1.283748 | 1.285612 | **1.864e-03** | −0.145 % | 1.195136 | 1.195136 | **0.0** | **True** (0 windows differ) |

Pass requires all three checks on both seeds. **Two pass, one misses:**

* **active-client set equal on every window — PASS**, and not approximately: **zero** differing
  windows out of the full window list on both seeds. Rule R did exactly what it was written to do.
* **`|Δ_group| ≤ 1e-9` — PASS, and exactly 0.0** on both seeds.
* **`|RMSE_μ| ≤ 1e-9` — FAIL**, by 2.1e-03 and 1.9e-03.

## 2. What Rule R fixed, in numbers

| seed | round_v1 / round_u1 rerun | **round_v2 (rule R)** | frozen | old rel | **new rel** |
|---|---|---|---|---|---|
| 30001 | 1.1712626 | **1.2087917** | 1.2108485 | −3.269 % | **−0.170 %** |
| 30006 | 1.1502492 | **1.2837478** | 1.2856116 | −10.529 % | **−0.145 %** |

The defect that broke H is **17× to 73× smaller** and no longer changes any comparison's sign by
itself. The mechanism in the instruction's §0 is **confirmed**: the extra client-slots with
`pi_tar = 0` were the cause of the active-set difference, and removing them restores the active set
and the composition exactly.

## 3. The residual, and why the gate is right to stop

The residual is **negative on both seeds and on every endpoint**:

| seed | `RMSE_μ` | `Head_RMSE` | `Tail_RMSE` |
|---|---|---|---|
| 30001 | −2.06e-03 | −1.98e-03 | −2.13e-03 |
| 30006 | −1.86e-03 | −1.65e-03 | −2.07e-03 |

A uniform negative offset of ~0.15 % across three endpoints and two seeds is **not** floating-point
noise, and it is **not** a composition error — `Δ_group` is a function of the composition alone and it
is now exact to 0.0. So the leftover lives in the **label** side, and the instruction's own gate is the
thing that catches it. The tolerance was not relaxed and no waiver was added, as forbidden.

Two candidates, recorded as candidates and **not** resolved here:

1. **The trace fields the H round's trace comparison ignored.** `GATE_uair.json` lists
   `trace_meta_keys_ignored = [drift_magnitude, drift_period, occupancy_A]`. The first two drive the
   U/O realizations and the third is the occupancy. If the stored trace's `occupancy_A` differs from
   the one the frozen E3 run used, Rule R restores the *set* of active clients (as it did) while the
   *per-unit observability* behind the labels can still differ.
2. **A second, smaller active-set effect inside the trained windows** that leaves the window-level
   membership identical but changes which units are in the local update — again invisible to
   `Δ_group`.

The instruction forbids trying a second filter in this round, so neither is tested.

## 4. What is and is not established

* **Established:** Rule R is the correct fix for the active-set defect. The frozen active set and the
  frozen composition are recovered **exactly** on both gate seeds, verified window by window.
* **Established:** the instruction's §0 diagnosis is right — the extra `pi_tar = 0` client-slots were
  the cause, and the 20/20 U-Air FedAvg reruns being 1.82–10.53 % low is explained by them.
* **Not established:** that `fedavg_window` can be reproduced to the frozen record's `RMSE_μ` at all.
  It cannot, under rule R alone, to within 1e-9.
* **Not established:** anything about H, `round_v1`'s or `round_u1`'s ceilings. **No H was
  recomputed**, no oracle file was copied, `main.tex`'s `|H| ≤ 0.217%` sentence is untouched, and
  `H_DECISION.json` for round_v2 does not exist.
* **Unchanged:** every previous conclusion, including R1's — that the corrected U-Air oracle gap is
  0.23 % with a CI spanning zero.

## 5. Files

```text
GATE_C0.json                 pass: false, both rows, the three checks, differing windows (none),
                             and the pre-registered consequence
tables/C0_REPRO.csv          the gate rows with Head/Tail and the old reruns for scale
eventtraces/C0_frozen/uair/seed30001|30006/training_eventtrace   the two filtered copies
runs/C0_frozen/uair/fedavg_window/seed30001|30006/              the two runs
```

## 6. The one thing a next protocol would need to decide first

Whether the `RMSE_μ` gate at 1e-9 is the right gate for this arm at all. The frozen record was
produced by an earlier code state; `Δ_group` and the active set are provenance-checkable and now
exact, but `RMSE_μ` on U-Air has already been shown non-reproducible **without** an active-set
difference (R0: two production runs, same trace hash, same seed, `Δ_group` differing by 0.067). A next
protocol should either name the label-side mechanism or state which of the three checks it treats as
the reproduction criterion — and say so **before** running.

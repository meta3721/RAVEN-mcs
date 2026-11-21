# P2C report — the non-aggregating-final-window criterion extended to C2/C5

Round: `results_regime_b_endpoints/round_v1/` · executed 2026-10-06, on user authorization
("扩大判据到C2/C5"). Addendum written before scoring: `P2C_ADDENDUM.md`. Scorer: `.rb_work/p2c_score.py`.
Re-scoring only — the replay values are `P2B_RUNS.csv`, unchanged. No manuscript file touched.

## 1. Gate after the extension

| | first P2 | P2B | **P2C** |
| --- | ---: | ---: | ---: |
| cell sets passing | 2 / 12 | 7 / 12 | **11 / 12** |
| exempted cells | 0 | 1 (oracle C1 30014) | **4** (C2/C5 seed 30002 × both pairs) + the C1 one |
| still stopped | 10 | 5 | **1** |

Criterion C1 of the addendum — *the A-side run's own last window is inactive (`active == False`,
`a_r_size == 0`)* — separates the replay-mismatch cells exactly: it holds for **6 / 6** failing A-side
cells and **0 / 198** passing A-side cells, and for **0 / 204** B-side cells
(`tables/P2C_CLASS_TEST.csv`). The four cells newly exempted are `C2_tilt_extreme` and `C5_combined`,
seed `30002`, both pairs; each exemption is a provenance statement (that run's stored metric is not
reproducible from its checkpoint alone) and each is excluded from the primary contrast.

**Still stopped: fedavg `C1` seed 30014** (`4.58e-02`). It satisfies criterion C1 but `C1` is outside
the authorized scope, and its audit-θ route does not apply because the audit file's θ value for that
cell belongs to a different run. Reported as stopped, not waived.

## 2. Reportable endpoint results (11 sets)

Primary = exact-replay cells only; sensitivity = the affected sets' contrast with the exempted cell's
replay included (declared, labelled as using a cell whose replay is not exact).

| pair | condition | n (primary) | `E_dec` A | `E_dec` B | r [95 % CI] | TP share A / B | sensitivity r (n) |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| fedavg | C0 | 17 | 0.336755 | 0.087341 | −38.9 % [−60.0, −17.8] | 33.8 % / 0.11 % | = primary |
| fedavg | C2 | 16 | 0.230444 | 0.088050 | **−25.9 %** [−45.5, −6.3] | 19.8 % / 0.27 % | −29.6 % (17) |
| fedavg | C3 | 17 | 0.334012 | 0.087341 | −38.4 % [−59.5, −17.4] | 33.8 % / 0.11 % | = primary |
| fedavg | C4 | 17 | 0.336594 | 0.085870 | −39.1 % [−60.3, −18.0] | 33.8 % / 0.10 % | = primary |
| fedavg | C5 | 16 | 0.227167 | 0.086638 | **−25.3 %** [−44.6, −6.0] | 18.5 % / 0.59 % | −29.1 % (17) |
| oracle | C0 | 17 | 0.342089 | 0.091010 | −36.5 % [−57.9, −15.0] | 33.4 % / 0.11 % | = primary |
| oracle | C1 | 16 | 0.235685 | 0.095584 | −23.5 % [−42.5, −4.5] | 19.7 % / 2.06 % | −23.8 % (17) |
| oracle | C2 | 16 | 0.208890 | 0.085954 | **−28.4 %** [−47.8, −9.0] | 18.6 % / 0.00 % | −32.0 % (17) |
| oracle | C3 | 17 | 0.341935 | 0.091966 | −35.9 % [−57.5, −14.3] | 33.9 % / 0.11 % | = primary |
| oracle | C4 | 17 | 0.343925 | 0.089560 | −36.9 % [−58.4, −15.4] | 33.9 % / 0.10 % | = primary |
| oracle | C5 | 16 | 0.203898 | 0.084458 | **−27.5 %** [−46.6, −8.3] | 17.5 % / 0.00 % | −31.1 % (17) |

Every set repeats the same reading, now across all six conditions and both arm families: regime B's
`E_dec` is **23–39 % lower**, entirely through false-alarm suppression (A's false alarms 0.20–0.28 → B's
0.001–0.006), while B's retention of the exceedance mass collapses to **0.0–0.6 %** (2.06 % in the one
tilt-stressed oracle cell) against A's **17.5–33.9 %**. The primary/sensitivity pairs differ by 3–4 pp
and never change the sign, the interval's exclusion of zero, or the conclusion.

**No decision-quality claim survives for either regime, in any of the 11 reportable sets.**

## 3. What changed and what did not

* **Changed**: the gate now passes 11 of 12 sets; four cells are exempted under a criterion validated to
  discriminate exactly, with the exclusion reported and a labelled sensitivity beside it.
* **Not changed**: the tolerance (1e-12), the scope beyond C2/C5, the endpoints, the ±0.10 band, the
  label rule, the `degenerate_at_T` definition, the scale declaration, the P0 price, and the round-3 H
  verdict. `fedavg C1` remains stopped.
* **Not claimed**: that the exempted cells would have passed with a different reconstruction — they are
  recorded as not reproducible from their checkpoints, which is why they are excluded rather than
  counted.

## 4. Outputs

`P2C_ADDENDUM.md`, `P2C_REPORT.md`, `tables/P2C_CLASS_TEST.csv`, `tables/P2C_RUNS_SCORED.csv`,
`tables/P2C_GATE.csv`, `tables/P2C_CONTRASTS.csv`, `P2C_GATE.json`.

# P2D report — criterion extended to C1; the endpoint gate now passes 12 of 12 sets

Round: `results_regime_b_endpoints/round_v1/` · executed 2026-10-06 on the user's instruction
("直接覆盖"). Addendum written before scoring: `P2D_ADDENDUM.md`. Scorer: `.rb_work/p2d_score.py`.
Re-scoring only — replay values from `P2B_RUNS.csv`, unchanged. No manuscript file touched.

## 1. Gate

| | first P2 | P2B | P2C | **P2D** |
| --- | ---: | ---: | ---: | ---: |
| cell sets passing | 2 / 12 | 7 / 12 | 11 / 12 | **12 / 12** |
| exempted cells | 0 | 1 | 5 | **6** |
| hard-failing sets | 10 | 5 | 1 | **0** |

Every exemption rests on the one criterion validated in `P2C_ADDENDUM.md` §C2 — the A-side run's own
last window is inactive — except the oracle `C1` cell, which additionally matches its audit θ value
(`P2B_ADDENDUM.md` §A4). The exemption set is the union of the three routes; no earlier route was
retracted. The six exempted cells are `C1 30014`, `C2 30002`, `C5 30002` for both pairs (the oracle
`C1` cell is counted once, matched by both routes). Each is a provenance statement: that run's stored
metric is not reproducible from its checkpoint alone. Each affected set is reported twice, primary over
exact-replay cells and a declared sensitivity including the exempted cell.

## 2. Reportable results — all twelve sets

| pair | condition | n (primary) | `E_dec` A | `E_dec` B | r [95 % CI] | TP share A / B | seeds TP A / B | sensitivity r (n=17) |
| --- | --- | ---: | ---: | ---: | --- | --- | --- | ---: |
| fedavg | C0 | 17 | 0.336755 | 0.087341 | −38.9 % [−60.0, −17.8] | 33.8 % / 0.11 % | 8 / 1 | = primary |
| fedavg | C1 | 16 | 0.220977 | 0.096665 | **−20.1 %** [−39.2, −1.0] | 17.8 % / 2.48 % | 5 / 1 | −21.7 % |
| fedavg | C2 | 16 | 0.230444 | 0.088050 | **−25.9 %** [−45.5, −6.3] | 19.8 % / 0.27 % | 6 / 1 | −29.6 % |
| fedavg | C3 | 17 | 0.334012 | 0.087341 | −38.4 % [−59.5, −17.4] | 33.8 % / 0.11 % | 8 / 1 | = primary |
| fedavg | C4 | 17 | 0.336594 | 0.085870 | −39.1 % [−60.3, −18.0] | 33.8 % / 0.10 % | 8 / 1 | = primary |
| fedavg | C5 | 16 | 0.227167 | 0.086638 | **−25.3 %** [−44.6, −6.0] | 18.5 % / 0.59 % | 6 / 1 | −29.1 % |
| oracle | C0 | 17 | 0.342089 | 0.091010 | −36.5 % [−57.9, −15.0] | 33.4 % / 0.11 % | 7 / 1 | = primary |
| oracle | C1 | 16 | 0.235685 | 0.095584 | −23.5 % [−42.5, −4.5] | 19.7 % / 2.06 % | 6 / 1 | −23.8 % |
| oracle | C2 | 16 | 0.208890 | 0.085954 | −28.4 % [−47.8, −9.0] | 18.6 % / 0.00 % | 6 / 0 | −32.0 % |
| oracle | C3 | 17 | 0.341935 | 0.091966 | −35.9 % [−57.5, −14.3] | 33.9 % / 0.11 % | 7 / 1 | = primary |
| oracle | C4 | 17 | 0.343925 | 0.089560 | −36.9 % [−58.4, −15.4] | 33.9 % / 0.10 % | 7 / 1 | = primary |
| oracle | C5 | 16 | 0.203898 | 0.084458 | −27.5 % [−46.6, −8.3] | 17.5 % / 0.00 % | 7 / 0 | −31.1 % |

Across all twelve sets, over all six conditions and both arm families:

* regime B's `E_dec` is lower in every set, by **20.1 % to 39.1 %** (CI upper bound below zero in all
  twelve);
* the entire movement is false-alarm suppression — A's false alarms `0.20–0.28` against B's
  `0.001–0.006`;
* B's retention of the exceedance mass is **0.00 – 2.48 %** against A's **17.5 – 33.9 %**, with B at
  exactly zero on both `C2` and both `C5` cells;
* the primary and sensitivity values differ by ≤ 3.6 pp and never change the sign, the interval or the
  conclusion.

**Reading:** the decision endpoint moves in regime B's favour only by giving up exceedance detection.
No set supports a decision-quality claim for either regime, and none contradicts the P0 price
(`Delta_c-s` +3.1 … +4.8 %) — the two endpoints simply measure opposing sides of the same rule change.

## 3. Boundary

The tolerance (1e-12) was never changed; the criterion had to pass a discrimination test before use
(6/6 failing vs 0/198 passing A-side cells); each exemption is disclosed, counted, and offset by a
labelled sensitivity; the trigger seeds stayed excluded; the endpoints, band, labels, scale declaration
and sweep are unchanged from `DESIGN.md`. No manuscript file was touched.

## 4. Outputs

`P2D_ADDENDUM.md`, `P2D_REPORT.md`, `tables/P2D_RUNS_SCORED.csv`, `tables/P2D_GATE.csv`,
`tables/P2D_CONTRASTS.csv`, `P2D_GATE.json`.

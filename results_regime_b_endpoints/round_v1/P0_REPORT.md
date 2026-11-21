# P0 execution report — calibration endpoint (`Delta_c-s`) under regime B

Round: `results_regime_b_endpoints/round_v1/` · Phase **P0** · executed 2026-10-06 (UTC 10:5x)
Pre-registration: `DESIGN.md` (sha256 `cd2db441…`), written before any confirmatory cell was read.
Executor: `.rb_work/rb_endpoints.py` `--p0`. No training, no checkpoint replay (that is P1), no
manuscript edit, no `src/` edit.

## 1. Guards

| guard | rule | result |
| --- | --- | --- |
| support | `pair_support_size == 288` on both sides | **288 on all 240 cells**, both sides |
| metric consistency | `delta_c_s_summary.Delta_c_s == final_metrics.Delta_c_s` ≤ 1e-12 | pass, 240/240 |
| trace pairing | A and B `EventTrace_hash` equal per cell | pass, **240/240, 0 unpaired** |
| reproduction | A-side FedAvg C0 `Delta_c-s` == frozen artifact | **max abs diff `0.000e+00`**, traces equal 20/20 |

Because the support is the same 288 keys in both regimes, `Delta_c-s` is on one scale and the paired
contrast is well-posed by construction (not by assumption).

## 2. T1 — calibration endpoint, paired (n = 20 seeds per cell, Student-t CI, df = 19)

`r = (M_B − M_A) / M_A`; **positive = regime B worse**.

| cell set | role | A (mean) | B (mean) | r (mean) | 95 % CI | seeds `r>0` | label |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- |
| FedAvg, C0 | reconnaissance | 1.262132 | 1.313777 | **+4.094 %** | [+3.597, +4.592] | 20/20 | `equivalent_zero` |
| FedAvg, C1 strong tilt | confirmatory | 1.314136 | 1.359793 | **+3.485 %** | [+2.928, +4.042] | 20/20 | `equivalent_zero` |
| FedAvg, C2 extreme tilt | confirmatory | 1.302376 | 1.342910 | **+3.121 %** | [+2.672, +3.570] | 20/20 | `equivalent_zero` |
| FedAvg, C3 low capacity | confirmatory | 1.262132 | 1.313777 | **+4.094 %** | [+3.597, +4.592] | 20/20 | `equivalent_zero` |
| FedAvg, C4 block-uniform | confirmatory | 1.262132 | 1.313777 | **+4.094 %** | [+3.597, +4.592] | 20/20 | `equivalent_zero` |
| FedAvg, C5 combined | confirmatory | 1.302376 | 1.342910 | **+3.121 %** | [+2.672, +3.570] | 20/20 | `equivalent_zero` |
| oracle Design-on → off, C0 | confirmatory | 1.234191 | 1.292646 | **+4.751 %** | [+4.207, +5.295] | 20/20 | `equivalent_zero` |
| oracle, C1 | confirmatory | 1.291975 | 1.342836 | **+3.951 %** | [+3.322, +4.579] | 20/20 | `equivalent_zero` |
| oracle, C2 | confirmatory | 1.281387 | 1.329302 | **+3.752 %** | [+3.256, +4.247] | 20/20 | `equivalent_zero` |
| oracle, C3 | confirmatory | 1.234191 | 1.292646 | **+4.751 %** | [+4.207, +5.295] | 20/20 | `equivalent_zero` |
| oracle, C4 | confirmatory | 1.234191 | 1.292646 | **+4.751 %** | [+4.207, +5.295] | 20/20 | `equivalent_zero` |
| oracle, C5 | confirmatory | 1.281051 | 1.329295 | **+3.778 %** | [+3.288, +4.267] | 20/20 | `equivalent_zero` |

All twelve cells: interval excludes zero, sign identical on every seed, and the two arm families agree
in size (+3.1 % to +4.8 %). **Regime B pays a calibration price, and it is not an artifact of one
weighting rule.** The mechanism is visible in the stored summaries: the overlap between the run's
contributing keys and the `pi_tar` keys rises from 83–98 (A) to 107–130 (B) — keeping the zero-mass
pairs dilutes `Pi_hat` across keys that carry no target mass, which is exactly what the L1 distance
then charges for.

## 3. T3 — companion endpoints (same pairs, context only)

FedAvg pair: `Delta_group −5.87 % … −8.20 %`, `RMSE_mu −5.18 % … −6.38 %`, tail `−5.24 % … −6.70 %`
(B better in every cell, 20/20 seeds).
Oracle pair: `Delta_group −5.51 % … −8.92 %`, `RMSE_mu −5.85 % … −6.48 %`, tail `−6.13 % … −6.82 %`
(B better on 19–20 of 20 seeds per cell).

So the trade-off vector on U-Air is: **B buys 5–9 % on prediction/group/tail and pays 3–5 % on
calibration**, in both arm families, at every condition, on every seed.

This is the same pattern the manuscript's own Design-removal row prices for the full RAVEN arm
(`Delta_group −6.943 %`, `RMSE_mu −6.885 %`, tail `−7.221 %`, `Delta_c-s +4.990 %`, Holm-adjusted).
The numbers here are a different arm (FedAvg and the oracle), so this **corroborates** that row rather
than reproducing it.

## 4. A defect found and fixed during execution (disclosed)

The first P0 run paired A and B through the frozen artifact directory for all six conditions and
therefore reported **60 `unpaired` oracle cells** (`trace_hash`) at C1/C2/C5: the frozen artifact set
contains only the *C0-trace* Design-on oracle. The guard behaved as specified — it refused the pairing
instead of averaging it. Diagnosis: the frozen set has no condition axis, so the Design-on side for
C1/C2/C5 is the round-v1/u1 `raven_simoracle` run, which sits on the same trace as its `nodesign`
counterpart (e.g. C1: `29a8d79ad148` on both sides).

Fix: the A side is now resolved to the **trace-matched** Design-on oracle (frozen for C0/C3/C4, the
condition runs for C1/C2/C5), recorded per cell in `P0_CELLS.csv:A_side_source`. This is input
resolution only — no endpoint, band, label, guard or cell set changed. The superseded run is preserved
at `P0_run1_resolver_unpaired/` with its unpaired list intact.

## 5. Label caveat (protocol observation, not a re-labelling)

Every cell above carries the label `equivalent_zero`, because the pre-declared band is `±0.10`
relative and all twelve changes fall inside it (3.1–4.8 %). The band was fixed in `DESIGN.md` before
any value was read, so the labels stand as computed and are **not** revised here. Two consequences are
recorded for the record's benefit:

* the same band also labels `Delta_group −5.9 … −8.2 %` as `equivalent_zero`, i.e. it is coarser than
  the materiality the manuscript itself assigns to changes of this size (its ablation treats
  `+4.990 %` as Holm-significant);
* the reading that does not depend on the band is the one printed beside it: the CI excludes zero in
  all twelve cells and the sign is identical on **240/240** seed pairs.

For any future round, a per-endpoint band taken from the manuscript's own materiality statement is the
better pre-registration; changing it now, after seeing values, is exactly what the design forbids.

## 6. What P0 settles and what it does not

* **Settled**: the prediction/group gain of regime B is *not* free — it comes with a calibration price
  of +3.1 % to +4.8 %, consistent in sign across every condition, both arm families and all 240 seed
  pairs, on a 288-key support identical in both regimes.
* **Not settled (P1)**: whether the decision endpoint moves the same way. `E_dec` requires the
  checkpoint replay and the scale declaration; both are specified in `DESIGN.md` §P1 and await the
  user's approval of the declaration.
* **Not claimed**: that the calibration price *causes* or is caused by the prediction gain (one rule
  change moves both); that the trade-off extends to SensorScope (out of scope, support cost ≈0); that
  regime A or B is "better" overall.

## 7. Forbidden-claim compliance

No overall "better/worse" claim (the result is a trade-off vector); no equivalence claim from a CI
containing zero (none does); no pooling used for a label (the `POOLED_all6` rows are marked
`pooled_descriptive` and carry no finding); no threshold, band, cell set or endpoint adjusted; no claim
about `E_dec` before P1; no SensorScope extension; no manuscript file touched.

## 8. Outputs

`P0_CELLS.csv` (240 cells, per-side values, guards, `A_side_source`), `tables/P0_CONTRASTS.csv`
(both pairs × six conditions × four endpoints + pooled descriptive rows),
`tables/P0_REPRODUCTION_GUARD.csv`, `P0_DECISION.json`,
`P0_run1_resolver_unpaired/` (superseded first run, preserved).

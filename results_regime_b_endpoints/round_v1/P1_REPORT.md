# P1 execution report — decision endpoint (`E_dec`) under the approved scale declaration

Round: `results_regime_b_endpoints/round_v1/` · Phase **P1** · executed 2026-10-06
Pre-registration: `DESIGN.md` (sha256 `cd2db441…`). Executor: `.rb_work/rb_p1.py`,
summary `.rb_work/p1_summary.py`. Read-only on every input; no training; no manuscript edit.

## 0. Scale declaration — approved and grounded

The declaration was presented to the user and P1 was executed on the user's instruction, so it is
recorded here as approved. Verbatim:

```text
dataset = uair | conversion = OFFLINE_LINEAR_CONVERSION | primary_domain = physical
sigma = 17.36325121670317 | zscore_applied = true | T_DEC = 35.0 (physical, unchanged)
applied identically to both regimes; no per-cell or fitted sigma; no threshold tuning
```

Grounding, asserted by the executor before any regime-B cell was read:

| quantity | value |
| --- | --- |
| A-side `metric_scale_policy.json: sigma` | `17.36325121670317` |
| declared `sigma` | `17.36325121670317` |
| `dataset._scaler_std` | `17.36325121670317` |
| `policy == declared` and `declared == dataset` (≤1e-9 / ≤1e-6) | **true / true** |

So the declared value is the dataset's own scale, not a fitted one; it is the value the manuscript's
own artifacts declare and the screen itself asserts (`|policy.sigma − dataset.target_std| ≤ 1e-6`).

## 1. P1a — positive control (the screen's own function, end to end)

`s1_screen.evaluate("uair", arm, seed)` replayed for the 40 stored frozen U-Air cells
(`fedavg_window`, `raven`; seeds 30001–30020) and compared with `SCREEN_RUNS.csv`:

| check | result |
| --- | --- |
| cells | 40 (34 non-trigger, 6 trigger) |
| non-trigger `max|Δ|` over `E_dec`, `E_mix`, `E_group`, `base_rate`, `RMSE_mu` | **2.220e-16** ≤ 1e-12 → pass |
| trigger cells (30007/30016/30018), recorded not failed | `E_dec` diffs `0.0 … 6.9e-17` |

`tables/P1_CONTROL.csv`, `P1_CONTROL.json`. The replay path reproduces the only stored decision-endpoint
numbers that exist, so the arithmetic used below is the screen's.

## 2. P1b — `E_dec` on the FedAvg C0 pair (17 non-trigger seeds)

Replay gate: `|RMSE_mu_recomputed − stored| = 0.00e+00` on **40/40 run cells** (both sides). The
decomposition sums to the screen's `E_dec` on 40/40 cells. Both runtime manifests carry the same
`EventTrace_hash`, and the A side reproduces the screen's stored frozen `fedavg_window` `E_dec` exactly
(`max|Δ| = 0.000e+00`, 17/17 seeds) — so the A side of this contrast *is* the manuscript's FedAvg.

| endpoint | A (frozen rule) | B (old rule) | B − A | seeds B<A / B>A |
| --- | ---: | ---: | ---: | --- |
| `E_dec` | 0.336755 | 0.087341 | **−24.94 pp** (relative −38.91 %, CI [−59.99, −17.84]) | 9 / 0 (8 ties) |
| `missed` (true positives lost) | 0.056912 | 0.085861 | **+2.89 pp** | — |
| `false_alarm` | 0.279843 | 0.001480 | **−27.84 pp** | 9 / 0 |
| `base_rate` (constant) | 0.085954 | 0.085954 | 0.00 pp | — |

**Decision skill, the number that decides how to read this:**

| side | true positives retained (share of the 0.085954 exceedance mass) | seeds with any correct exceedance |
| --- | ---: | ---: |
| A (frozen rule) | **33.8 %** (0.029042) | 8 / 17 |
| B (old rule) | **0.1 %** (0.000092) | 1 / 17 |

So B's `E_dec` is 39 % lower **not because B decides better**: B stops predicting exceedances
altogether (`missed` rises to exactly the exceedance mass on 16 of 17 seeds), which removes A's large
false-alarm load and, with it, the last true positives A had. Neither arm has usable decision ability.

**Threshold sweep (descriptive, declared in `DESIGN.md`, no threshold selected):**

| T (µg/m³) | base rate | `E_dec` A | `E_dec` B | missed A / B | false alarm A / B | seeds with any TP (A / B) |
| ---: | ---: | ---: | ---: | --- | --- | --- |
| 25 | 0.200210 | 0.799790 | 0.799790 | 0.000 / 0.000 | 0.800 / 0.800 | 17 / 17 |
| **35** | 0.085954 | 0.336755 | 0.087341 | 0.057 / 0.086 | 0.280 / 0.001 | 8 / 1 |
| 50 | 0.019916 | 0.019916 | 0.019916 | 0.020 / 0.020 | 0.000 / 0.000 | 0 / 0 |
| 75 | 0.000524 | 0.000524 | 0.000524 | 0.001 / 0.001 | 0.000 / 0.000 | 0 / 0 |

At 25 both arms over-predict (every non-exceedance below 25 becomes a false alarm, and the "true
positives" are the exceedances they trivially exceed); at 50 and 75 both miss everything; at 35 the
only asymmetry is A's false alarms versus B's complete loss of positives. **No declared threshold gives
either arm decision skill**, so the endpoint cannot adjudicate the regime trade-off.

## 3. Verdict

1. **The decision endpoint does not contradict P0 and does not support a decision-quality claim.** Its
   only movement in B's favour is false-alarm suppression bought by giving up the last true positives.
2. **P0 remains the substantive price**: calibration `Delta_c-s` +3.1 … +4.8 % (CI excludes zero in all
   twelve cells, 240/240 seed pairs same sign) against prediction/group/tail gains of 5–9 %.
3. **The pre-declared `degenerate_at_T35` flag did not fire** (`false`), because it required *both*
   sides to have `missed == base_rate` exactly; A misses 66 % of the mass rather than 100 %. The flag is
   reported as computed and **not** redefined. The substantive statement above (A 33.8 % / B 0.1 % of
   exceedance mass retained; no threshold with skill) is printed beside it so the reading does not
   depend on the flag's definition.

## 4. Protocol observations (recorded, not applied retroactively)

* **The relative estimator is undefined for the parts.** Per-seed `r = (B−A)/A` divides by zero when
  A's `missed` is 0 (2 seeds) or B's `false_alarm` is 0 (16 seeds). The parts are therefore reported as
  **percentage-point differences** with the zero-denominator counts shown, and the relative form only
  where defined (`rel_n_defined` in `tables/P1_SUMMARY.csv`). No endpoint, band or label changed.
* **`missed`, `false_alarm`, `base_rate` and the sweep were not pre-declared as headline endpoints** in
  `DESIGN.md` §P1; they were pre-declared as the mandatory companion readout of `E_dec`. They are used
  here exactly in that role: they explain an endpoint movement, they are not a second result.
* **Three execution defects, all disclosed and fixed before the reported numbers**: (i) the trace path
  template was not formatted per seed (`FileNotFoundError`); (ii) seeds ≥ 30006 resolve to `round_u1`,
  not `round_v1`; (iii) the sweep rows were collected after the run dictionaries had been trimmed, so
  the first complete P1b produced an empty `P1_SWEEP.csv`. The gate caught (i) and (ii) by crashing
  rather than by producing numbers; (iii) was caught by the summary reader. No value reported above was
  computed before its fix.

## 5. Forbidden-claim compliance

No decision-quality claim from a saturated endpoint (the split is printed with every number); no
"regime B is better/worse overall" claim; no equivalence claim from a CI containing zero (the `E_dec`
CI excludes zero, and is reported as false-alarm suppression, not benefit); no threshold selected or
preferred (all four are printed for both sides); no band, endpoint, guard or cell set adjusted; no
SensorScope extension; no manuscript file touched.

## 6. What remains

`DESIGN.md` priority **P2**: `E_dec` for the other five conditions and the oracle pair (440 run cells,
~4 minutes at the measured 0.5 s/cell). Given §2–§3, its expected value is a *generality check on a
saturated endpoint*, not a new endpoint: it can show whether the saturation and the A-has-some-skill /
B-has-none pattern hold across tilt strength, backbone and target law. Not executed here.

## 7. Outputs

`tables/P1_CONTROL.csv`, `P1_CONTROL.json`, `tables/P1_RUNS.csv` (40 cells, both sides),
`tables/P1_SWEEP.csv`, `tables/P1_SUMMARY.csv`, `tables/P1_SWEEP_SUMMARY.csv`, `P1_SUMMARY.json`,
`P1_DECISION.json`.

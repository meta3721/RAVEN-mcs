# EXECUTION REPORT — scheme C: error of the deployment total

```text
Round     : results_aggregate_total/round_v1
Prereg    : PREREG.md sha256 1d7193b48fdc58ddd7f9ed4158982c73f638f5d396b09241cea7342f3da554f8
            (9062 bytes), hashed in MANIFEST.sha256 before any E was computed
Cost      : no training, no model, no y-hat. 200 replay rebuilds + 40 closed-form floors, 3 min
DECISION  : gate = pass (200/200), sensorscope = open, uair = null,
            aggregate_path = CLOSED
Writes    : results_aggregate_total/round_v1/ only
Untouched : src/, the manuscript, every other results_* directory, artifacts/, git
```

## 1. Gate (§2) — 200/200 pass

| quantity | value |
|---|---|
| runs rebuilt | **200** (5 arms × 20 seeds × 2 datasets) |
| `max |‖ω̄ − μ‖₁ − stored Δ_group|` | **8.88e-16** |
| gate bar | 1e-8 → **pass**, with 7 orders of margin |
| windows used = active windows = case M windows | **true on all 200 rows** (92–98 SensorScope, 63–75 U-Air) |

The rebuild is exact, not merely within tolerance, so `ω̄` is the same vector the stored `Δ_group` was
computed from. U-Air seeds 30007/30016/30018 were treated as ordinary seeds, as §2 requires: they
pass with the same 4.4e-16–8.9e-16 differences as every other seed.

## 2. Result — E and the dose–response

`E = |(ω̄ − μ)·m|` with `m_g` the unweighted mean of the **test-split label** in group `g`
(SensorScope °C after inverting the train z-score; U-Air μg/m³). No `ŷ` is used anywhere.

| arm | E, SensorScope | E, U-Air |
|---|---|---|
| `fedavg_window` | 0.3782 | 0.7988 |
| `raven` | 0.3614 | 0.8190 |
| `uniform_window` | 0.3694 | 0.8571 |
| `proj_beta` | **0.3574** | 0.8131 |
| `proj_beta_debt` | 0.3609 | 0.8529 |

| dataset | n | slope | 95% CI | label |
|---|---|---|---|---|
| SensorScope | 80 | **+0.36587** | **[+0.26571, +0.47217]** | **open** |
| U-Air | 80 | +1.27048 | [−1.76992, +3.81911] | **null** |

**`aggregate_path = closed`**, because §5 requires *both* datasets `open` and U-Air's interval spans 0.

## 3. The floor — and a correction I had to make to my own computation

§4 asks for `E_floor`, the best the deployment total could be if the composition were re-optimised
over the delivered groups. **It is 0.0 on all 40 traces**: for every trace the values `{m_g : g delivered}`
bracket `K = Σ_h μ_h m_h`, so a two-group mixture reproduces the deployment total exactly.
`TOTAL_FLOOR.csv` records `K`, the delivered `m`-range, `|D|` (100–119 SensorScope, 65–77 U-Air) and
the μ-mass on the delivered groups (0.51–0.59 and 0.45–0.53).

Consequences that matter for reading the result:

* **`E − E_floor = E`.** The arms are nowhere near the floor: they sit at 0.36 of a total that could
  be matched to 0 by reweighting the delivered groups. Nothing here says the composition is
  constraint-limited; it says the rule's own weights are far from the total-matching weights.
* **The floor does not rescue the U-Air null.** A floor of 0 makes `E` a pure property of the
  composition, which is exactly what the regression tests.

**Disclosure — two wrong versions were computed first and are withdrawn.** (i) An LP over the
delivered simplex returned 0.74–13.1; it was wrong. (ii) A "vertex scan" then returned 0.0001–0.68;
it was wrong too, and its stated justification was wrong: `|Σ w_g m_g − K|` is convex in `w`, but a
convex function's minimum over a polytope is **not** generally at a vertex — the minimum sits where
the affine argument crosses `K`. The correct closed form is
`floor = 0 if min_{g∈D} m_g ≤ K ≤ max_{g∈D} m_g else min(|min−K|, |max−K|)`, which is what
`TOTAL_FLOOR.csv` reports, and it is corroborated by a 20 000-draw random search per trace that never
went below it. The first two attempts are recorded rather than deleted because the audit trail of a
wrong floor is worth more than a clean file.

## 4. What this round establishes, and what it does not

* **Establishes:** the deployment total of the *label* moves with `Δ_group` on SensorScope —
  a lower `Δ_group` comes with a lower total error, slope +0.366 with the interval clear of 0.
  This is the first endpoint in this project where the structural ordering carries over to a
  label-side quantity, and it uses no model output.
* **Establishes:** it does **not** carry over on U-Air (slope +1.27, CI [−1.77, +3.82]).
* **Does not establish:** that any arm is better than another in a practical sense. The whole spread
  of `E` across the five arms is **0.021** on SensorScope on a mean of 0.365, and the `E` spread on
  U-Air is 0.058 on 0.83 with the sign not stable. The slope is a gradient across contrasts, not an
  arm-level win.
* **Does not establish** anything about prediction: `E` is a property of the label and the
  composition, not of `ŷ`.

## 5. Deviations and amendments (declared before the hash)

```text
A-C1  W.build_case reads p2_invocation_states.json from
      artifacts/e4_core_mechanism_ablation_r1/runs, which holds the five ablation arms x 20 seeds x
      2 datasets with 20/20 non-empty files for raven_wo_use. It is NOT readable from the scored
      runs: fedavg_window and raven have no such file under artifacts/e3_formal_runs_r1/runs, and
      all 120 trained-arm cells under results_w1_ladder/round_v4/train/v4/C0_frozen hold `{}`
      (3 bytes). The instruction's own path is the only available one.
A-C2  Windows are the run's own `active == true` entries, paired positionally with the case's M_r.
      Measured: active count == case M count on all 200 runs, so no truncation occurred.
A-C3  eta is constant as §2 declares, so omega_bar = mean of coverage_mix over the used windows.
A-C4  The rebuild was validated before the hash: SensorScope seed 30001 reproduced the stored
      Delta_group to 2.2e-16 / 4.4e-16 / 6.7e-16 for fedavg_window / raven / proj_beta.
A-C5  §4's LP was replaced by the closed form of §3 above, because the LP returned values above the
      arms' own E, which is impossible for a correct minimisation. The replacement is declared here
      and the two withdrawn attempts are documented in §3; no rule of §0, §1, §2, §3, §5 changes.
A-C6  E_floor is reported per trace in TOTAL_FLOOR.csv and per run in TOTAL_RUNS.csv; E − E_floor
      equals E because the floor is 0.
```

## 6. Files

```text
PREREG.md            the frozen rule set + amendments, hashed first
MANIFEST.sha256      PREREG.md digest
TOTAL_RUNS.csv       200 rows: gate columns, E, E_floor, E-E_floor, dropped mass, units
TOTAL_FLOOR.csv      40 rows: closed-form floor, K, delivered m-range, |D|, mu-mass on D
TOTAL_DOSE.csv       2 rows: slope, CI, label per dataset
TOTAL_DECISION.json  gate pass, sensorscope open, uair null, aggregate_path closed
EXECUTION_REPORT.md  this file
```

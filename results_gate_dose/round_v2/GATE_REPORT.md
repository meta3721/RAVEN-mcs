# Part II — gate result: **FAILED at G3**. The round stops here.

Round: `results_gate_dose/round_v2/`
Instruction: `raven-mcs-estimand-gate-execution-prompt.md`, sha256 `ffb4bde6…`
Executed 2026-10-07 under the authorization phrase `授权门控剂量`.
Driver: `scripts/estimand_gate_round2.py`. Round v1 read-only inputs verified.

## 1 II-P0 — input hashes: PASS

| input | check | result |
| --- | --- | --- |
| `round_v1/MASKS.json` | content `6b456bd378e92ead…` | PASS |
| `round_v1/TARGET_WIRING.json` | content `b9de9d9b7d7e7823…` | PASS |
| `round_v1/RHO.csv` | file `302cd48c779e9a2a…` | PASS |
| `scripts/gate_dose.py::CONFIRMED` items 2–4 | frame/unrounded/θ-endpoints/stop-round | PASS |

Levels re-read as locked: SensorScope `{0, 0.10, 0.25, 0.40}`, U-Air `{0, 0.10, 0.20}`.

## 2 Gates

**G1 — determinism: PASS.** `raven`, m = 0, seed 30001, run twice per dataset.
θ bit-equal (`max|Δθ| = 0.000e+00`) and all four endpoints `|Δ| = 0` on both datasets.

**G2 — off-arm reproduction: PASS.** `raven_wo_design`, m = 0, seeds 30001–30002, both
datasets: `active_clients` identical on every window; largest absolute deviation over the
four endpoints **2.2e-15** (tolerance 1e-9).

**G3 — on-arm drift bound: FAIL.** All 40 fresh `raven` m = 0 runs compared with the stored
artifacts, bounds fixed before the run at relative 1e-6 per endpoint:

* `active_clients` identical on every window: **40/40**;
* relative bounds: **37/40 pass, 3/40 fail**.

| dataset | seed | `RMSE_mu` | `Delta_group` | `Delta_c_s` | `Tail_RMSE` |
| --- | ---: | ---: | ---: | ---: | ---: |
| uair | 30002 | **2.131e-06** | 8.410e-09 | 1.328e-09 | **2.229e-06** |
| sensorscope | 30019 | 1.229e-07 | **1.516e-06** | 2.365e-09 | 1.170e-07 |
| sensorscope | 30003 | 6.187e-08 | **1.023e-06** | 1.628e-15 | 5.809e-08 |

Worst per dataset: SensorScope 1.516e-06, U-Air 2.229e-06, against the fixed 1e-6.
The misses are marginal — a factor of 1.02 to 2.23 over the bound — and every one of them
passes the structural check: the active sets are identical, so the deviation is pure
floating-point path drift in the θ trajectory, exactly the drift the bound exists to
measure.

## 3 Consequence

`GATE.json` was written with `"pass": false` (JSON boolean) and Part II stopped, as II-3
requires. **No waivers, no second rule, no re-test after seeing the numbers.**

* II-P1: G1 ✓, G2 ✓, the 40 m = 0 runs ✓, G3 ✗ → stop.
* II-P2 (200 dose cells): **not started**. There is no `DOSE_CELLS.csv`, no
  `GATE_POLICY.csv`, no `DOSE_DECISION.json`.
* II-P3: not started.

## 4 Diagnostics, recorded but not applied

`G3`'s justification in the instruction says the bound "is four orders of magnitude below
δ = 0.5 % and above the measured drift (5.3e-8 relative on SensorScope)". The measured
SensorScope figure holds for the cell it came from (seed 30001: `RMSE_mu` 5.31e-08), but
not for all 20 seeds or all four endpoints: the observed relative drift reaches 1.5e-06
(Δ_group, SensorScope seed 30019) and 2.2e-06 (U-Air seed 30002). The bound and the
justifying measurement therefore disagree, in the direction of the bound being too tight by
roughly 2×.

That is a defect in the frozen bound, not a numerical failure of the run, and it is
**recorded here rather than repaired**: changing a tolerance after seeing which cells miss
it is exactly what the round forbids. What it means for the user's decision:

* Running II-P2 would require either a revised G3 bound (a pre-registration amendment, to be
  declared as such) or a re-run motivated by a *pre-declared* reason unrelated to these
  numbers.
* The drift is ≥4 orders below δ = 0.5 %, so a bound such as 1e-5 would still screen the
  effect sizes the design is about; but that is the user's call, not the driver's.

## 5 Artifacts written

`INPUT_HASHES.json`, `GATE.json` (`pass: false`), `GATE_G1.json`, `GATE_G2.json`,
`GATE_G3.json`, `M0_RUNS.json`, and the 52 run directories under `runs/`
(`g1_rep1` 2, `g1_rep2` 2, `g2` 4, `m0` 40, plus 4 from the earlier II-P0-less trial). The
runs are retained as audit material; nothing was deleted. Round v1's outputs are unchanged,
and `src/`, the manuscript, `artifacts/` and every other `results_*` remain untouched.

## 6 No-fabrication status

Every number above is read from the JSON files named in §5. No dose cell exists, so no H1,
H2, H3, `gate_law` or `ρ*` value is reported or implied.

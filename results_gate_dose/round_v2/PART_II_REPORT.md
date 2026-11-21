# Part II — resolution: `gate_law = not supported`, `gate_decision` null

Round: `results_gate_dose/round_v2/`
Instruction: `raven-mcs-estimand-gate-execution-prompt.md`, sha256 `ffb4bde6…`
Executed 2026-10-07 under the authorization phrase `授权门控剂量`. Driver:
`scripts/estimand_gate_round2.py`. No `src/`, manuscript, `artifacts/` or round_v1 write.

## 1 Gate

| gate | bound | result |
| --- | --- | --- |
| II-P0 input hashes | round_v1 `MASKS` content `6b456bd3…`, `TARGET_WIRING` content `b9de9d9b…`, `RHO.csv` file `302cd48c…`, `CONFIRMED` 2–4 | **PASS** |
| G1 determinism | θ bit-equal, four endpoints `\|Δ\| = 0` | **PASS** (both datasets) |
| G2 off-arm reproduction | `active_clients` identical; four endpoints ≤ 1e-9 absolute | **PASS** (largest 2.2e-15) |
| G3 on-arm drift, original bound 1e-6 | 37/40 cells | **FAIL** |
| G3 on-arm drift, **amended** bound 1e-5 + p95 ≤ 2e-6 | 40/40 cells, p95 ≤ 1.05e-6 (SS) / 1.32e-7 (UA) | **PASS** |

The original G3 fail is preserved verbatim in `GATE_G3.json` and `GATE_ORIGINAL.json`
(`pass: false`); the amendment and its justification are in `GATE_AMENDMENT.md`, authorized
before the amended verdict was computed. `GATE.json` now reads `pass: true`,
`G3_original_pass: false`, `G3_amended: true`, `amended: true`.

**A withdrawn confirmation rule, disclosed.** The first amendment draft fixed a confirmation
on seeds 30021–30025. That is impossible — the frozen artifacts hold exactly seeds
30001–30020 and there are no EventTraces beyond 30020, so those seeds have neither a stored
reference nor a trace. The rule was withdrawn in writing before any such run existed and the
job that would have executed it was cancelled before writing any gate file; no `t_confirm`
directory exists. The rule actually used is in `GATE_AMENDMENT.md` §5: reuse of the 40
bit-reproducible m = 0 runs (labelled as reused in `M0_RUNS.json`: 0 new, 40 reused), the
amended verdict reported beside the original per cell, and a 95th-percentile condition.

## 2 H1 — the primary hypothesis

`r_RMSE` regressed on realized ρ across all (level, seed) cells; seed-cluster bootstrap,
10 000 draws, `default_rng(20261007)`, percentile 95 %.

| dataset | cells | slope `b` | 95 % CI | label | θ-excluded slope |
| --- | ---: | ---: | --- | --- | ---: |
| SensorScope | 80 | **+0.001365** | [−0.003556, +0.006356] | **`null`** | +0.001365 |
| U-Air | 60 | **−0.073079** | [−0.165370, +0.022770] | **`null`** | −0.024948 |

Both intervals contain zero. **`gate_law = not supported`** (it requires SensorScope `open`
and U-Air not `harm`).

**H2 is `not_tested`** — it is licensed only when H1 supports the law, which it does not.
**`ρ*` is not reported** for the same reason: the two computed values (SensorScope −0.4947,
U-Air +1.3751) are printed in `DOSE_DECISION.json` as fit artefacts only and carry no claim.

## 3 The per-level reading

| dataset | level | ρ | `r_RMSE` mean [95 % CI] | `r_Δc-s` | `r_Δgroup` | `r_Tail` |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| SensorScope | 0 | 0.0000 | −0.0053 % [−0.0377, +0.0271] | −0.59 % | −1.23 % | −0.005 % |
| SensorScope | 0.10 | 0.0974 | +0.1419 % [−0.0041, +0.2879] | −1.47 % | −1.11 % | +0.135 % |
| SensorScope | 0.25 | 0.2453 | +0.1747 % [+0.0139, +0.3355] | −3.26 % | +0.32 % | +0.168 % |
| SensorScope | 0.40 | 0.3881 | +0.0586 % [−0.1621, +0.2793] | −5.77 % | +0.75 % | +0.058 % |
| U-Air | 0 | 0.3544 | +7.4565 % [+6.1057, +8.8073] | −4.75 % | +7.50 % | +7.857 % |
| U-Air | 0.10 | 0.4188 | +6.9947 % [+5.5875, +8.4020] | −6.52 % | +7.31 % | +7.351 % |
| U-Air | 0.20 | 0.4662 | +6.6385 % [+4.6755, +8.6015] | −8.79 % | +5.71 % | +6.938 % |

Every `r_Δc-s` interval excludes zero (slope −0.1331 SS, −0.3565 UA, both CIs strictly
negative); `r_Δgroup` is **+0.0568** on SensorScope (CI [+0.0216, +0.0937]) and **−0.1523**
on U-Air (CI [−0.2288, −0.0799]) — opposite signs, so that slope is not a law either. On
the prediction endpoint the SensorScope dose produces at most **+0.17 %** against δ = 0.5 %.

## 4 H3 — does the pre-outcome gate choose the better setting?

SensorScope only (on U-Air every level has ρ > 0, so `gate == always_off`; descriptive).

| policy vs | `w_pred` difference [95 % CI] | `w_eq` difference |
| --- | --- | --- |
| `always_on` | **0.000000** [0, 0] (all 20 seeds exactly zero) | 0.000000 [0, 0] |
| `always_off` | −0.0494 % [−0.0789, −0.0189] | +0.4939 % [+0.1885, +0.7888] |

**`gate_decision = null`.** Under `w_pred` the gate beats `always_off` but is *identical* to
`always_on` — structurally, not by chance: at ρ = 0 the gate's rule *is* `always_on`, so that
comparison is identically zero and the protocol's "open" condition (CI upper bound < 0 for
**both** differences) can never be met. This is reported as measured, with the structural
reason recorded beside it.

**Base rate.** Share of SensorScope cells where `off` is optimal: **0.20** under `w_pred`
(4/20, Wilson [0.081, 0.416] — non-degenerate), **0.00** under `w_eq` (0/20, Wilson
[0.000, 0.161]). Per II-5 the second is labelled **`saturated`**; the first is reported as a
non-degenerate base rate next to the `null` label.

## 5 What Part II licenses

**Nothing.** Per II-6, `gate_law = supported` is what would license "a structural statistic
computed before training predicts the sign and size of the prediction cost of Design"; that
label was not earned. `gate_decision = open` was not earned either. SensorScope's `null`
means the gate stays "a decision chart fitted to this U-Air ablation row" (`main.tex`
L2050–2051), exactly as written.

## 6 Execution defects, all disclosed and fixed before the reported numbers

1. **Dose cells overwrote each other.** `run_one` built `runs/dose/<ds>/<arm>/seed<seed>/`
   without the level, so the three SensorScope levels would have written to the same
   directories. Caught by the first dose attempt failing on a `KeyError` before any cell was
   reported; the layout is now `runs/dose/<ds>/m<level>/<arm>/seed<seed>/` and the partial
   directory was deleted before the real run. No reported number was produced under the old
   layout.
2. **Level-key formatting.** `RHO.csv` carries `m` as float (`0.1`), while `MASKS.json` keys
   are strings (`"0.1"` / `"0.25"`); the lookup mixed them. Fixed with one canonical
   `norm_level`, asserted by printing both level lists.
3. **`p3` was not wired into the CLI**, so the first `p3` invocation exited with
   "stage p3 not enabled yet" and wrote nothing.
4. **H3 column naming** (`J_w_pred_gate` vs `J_pred_*`) and **`gd.wilson` did not exist**;
   both raised before any decision file was written.
5. **The amendment's first confirmation rule was impossible** (§1) and was withdrawn in
   writing before execution.

## 7 Outputs

`INPUT_HASHES.json`, `GATE.json`, `GATE_ORIGINAL.json`, `GATE_G1.json`, `GATE_G2.json`,
`GATE_G3.json`, `GATE_G3_AMENDED.json`, `GATE_AMENDMENT.md`, `GATE_REPORT.md` (the original
stop record), `M0_RUNS.json` (40 reused, 0 new), `DOSE_RUNS.json` (200), `THETA_SCORED.csv`
(11 cells), `tables/DOSE_CELLS.csv` (280 = 14 cells × 20 seeds), `tables/DOSE_CELLS_PAIRED.csv`
(140), `tables/DOSE_SUMMARY.csv`, `tables/DOSE_SLOPES.csv`, `tables/GATE_POLICY.csv`,
`DOSE_DECISION.json`, and 246 run directories plus 11 frozen-θ replays under `_theta/`.

**θ-scored cells (11).** All `uair`, `raven`, levels 0/0.10/0.20: seeds 30007, 30016, 30018
at every level plus 30019 at the two non-zero levels. Each has an inactive last window; per
round_v1 §3 they are scored from the saved checkpoint, `RMSE_mu` and `Tail_RMSE` from the
replay, the structural endpoints from the stored metrics, and all of them are listed in
`THETA_SCORED.csv`. The stored-vs-replayed `RMSE_mu` moves by up to 5.1 %.

## 8 No-fabrication status

Every number is written by the driver from the named files. The two H1 labels, the H3
labels, the base rates and the slopes are as computed; `H2` and `ρ*` carry no value because
the protocol conditions them on an `open` H1 that did not occur.

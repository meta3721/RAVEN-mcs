# P2B report — both repairs executed: faithful replay + repaired C4/C5 A side

Round: `results_regime_b_endpoints/round_v1/` · executed 2026-10-06
Addendum (written before the repaired run): `P2B_ADDENDUM.md`. Executors: `.rb_work/repair_c45.py`,
`.rb_work/rb_p2b.py`, `.rb_work/rederive_h_fix.py`. No manuscript file touched.

---

## 1. Repair 2 — the C4/C5 A side is now the block-uniform condition

`results_h_headroom/round_v3_fix/runs/<cond>/uair/fedavg_window/seed*`, 40 runs (2 conditions × 20
seeds), trained with `H.CONDITIONS[cond]` passed verbatim so `H.injected(cond, block_factor=factor)`
applies the target-bundle rescaling that round 3 skipped (correction item 49). The defective runs are
untouched and stay on disk.

| condition | Δ`RMSE_mu` (fixed − defective) | Δ`Delta_group` | Δ`Delta_c-s` | runs changed |
| --- | --- | --- | --- | ---: |
| C4 block-uniform | **+0.003157** (min +0.002544, max +0.003561) | +0.000745 (−0.0108 … +0.0146) | **0.0 exactly** | 20/20 |
| C5 combined | **+0.003102** (min +0.002720, max +0.003418) | −0.001281 (−0.0143 … +0.0043) | **0.0 exactly** | 20/20 |

`Delta_c-s` is unchanged **by construction**: it is `sum_{k,s} |Pi_hat_ks - pi_tar_ks|` on
`client × opportunity_stratum`, and the block-uniform law rescales the *group* target mass and the
positive client-stratum masses by strictly positive factors, leaving the zero-mass set — and hence
`Pi_hat` — alone. So the repair moves exactly the two metrics that use the group mass, and nothing else.
`tables/C45_REPAIR_GATE.csv`, `REPAIR_GATE.json`.

### Re-derived round-3 H rows (same estimator, `go_bar = 0.005`, same oracle arms and seeds)

| condition | FedAvg before → after | `H_best` before → after | 95 % CI (after) | `go` |
| --- | --- | --- | --- | --- |
| C0 – C3 | unchanged (|Δ| ≤ 4.4e-16) | unchanged | — | yes |
| C4 block-uniform | 1.188238 → **1.191394** | 0.059330 → **0.061820** | [+0.047162, +0.076477] | **yes (unchanged)** |
| C5 combined | 1.179322 → **1.182424** | 0.052110 → **0.054595** | [+0.040396, +0.068793] | **yes (unchanged)** |

Round decision stays **`go`**, and the six `go` cells are still the Design-off oracle arm
(`tables/H_SUMMARY_fix.csv`, `tables/H_FIX_DIFF.csv`, `H_DECISION_fix.json`). The repair moves the C4/C5
H levels by ≈ +0.0025 (≈ +4 % of the value) and changes no verdict. The P0 `Delta_c-s` cells for C4/C5
are numerically unchanged for the reason above — they were never affected by the defect, only
mislabelled by it.

---

## 2. Repair 1 — the replay is now faithful, and the gate passes 7 of 12 sets

The replay builds the runner inside `run_h_headroom.injected(CONDITIONS[cond], block_factor=factor)`,
passes the block-rescaled `mu`, and resolves the oracle A side to the condition-matched run. A four-cell
probe before the full run reproduced the stored RMSE **exactly** on C0, C3, C4 and C5 for both pairs —
including the C3 `diurnal_blind` and C4/C5 block-uniform cells that the first P2 run missed.

| gate result | first P2 run | **P2B (repaired)** |
| --- | ---: | ---: |
| cell sets passing | 2 / 12 | **7 / 12** |
| hard-failing sets | 10 | 5 |
| max abs ΔRMSE over non-trigger cells | `9.09e-02` | **`0.00e+00` on every passing set** |

Still stopped, with the reason and without any waiver:

| stopped set | failing cells | why it is not exempted |
| --- | --- | --- |
| fedavg C1 | seed 30014 (`4.58e-02`) | the audit file's θ value for that cell belongs to a *different* run (the h_round one, stored `1.165389`), so the addendum's mechanical test correctly does not fire |
| oracle C1 | — | **passes**, one cell (30014) exempted with its replay matching the audit's `theta_rmse_mu` to 1e-12 |
| fedavg C2, oracle C2, fedavg C5, oracle C5 | seed 30002 (`8.4e-02 … 9.2e-02`) | no pre-existing list covers C2/C5; `A1_INACTIVE_FINAL_SWEEP.csv` covers only the frozen `e3` tree, where seed 30002 has an active final window. Left stopped rather than retro-fitting an exemption |

The pattern is consistent across the stopped cells: the **A side** (a Design-on run) misses while the B
side is exact — the same shape as the class the 2026-09-29 θ audit documented for C0/C1/C3/C4, but for
C2/C5 there is no pre-existing membership list to apply mechanically, so those four sets remain stopped.

---

## 3. Reportable endpoint results (7 gate-passing sets)

| pair | condition | n | `E_dec` A | `E_dec` B | r [95 % CI] | TP share A / B | seeds with TP A / B |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| fedavg_rule | C0 | 17 | 0.336755 | 0.087341 | −38.9 % [−60.0, −17.8] | 33.8 % / 0.11 % | 8 / 1 |
| fedavg_rule | C3 | 17 | 0.334012 | 0.087341 | −38.4 % [−59.5, −17.4] | 33.8 % / 0.11 % | 8 / 1 |
| fedavg_rule | C4 | 17 | 0.336594 | 0.085870 | −39.1 % [−60.3, −18.0] | 33.8 % / 0.10 % | 8 / 1 |
| oracle_design | C0 | 17 | 0.342089 | 0.091010 | −36.5 % [−57.9, −15.0] | 33.4 % / 0.11 % | 7 / 1 |
| oracle_design | C1 | 16 | 0.235685 | 0.095584 | −23.5 % [−42.5, −4.5] | 19.7 % / 2.1 % | 6 / 1 |
| oracle_design | C3 | 17 | 0.341935 | 0.091966 | −35.9 % [−57.5, −14.3] | 33.9 % / 0.11 % | 7 / 1 |
| oracle_design | C4 | 17 | 0.343925 | 0.089560 | −36.9 % [−58.4, −15.4] | 33.9 % / 0.10 % | 7 / 1 |

Every reportable set repeats the P1 pattern: regime B's `E_dec` is 23–39 % lower, and the decomposition
shows that this is false-alarm suppression (A's false alarms 0.20–0.28 → B's 0.001–0.006) while B's
retention of the exceedance mass collapses to 0.1 % (2.1 % in the one tilt-stressed oracle cell) against
A's 20–34 %. **No set supports a decision-quality claim for either regime**; the endpoint is saturated
for B everywhere it is reportable. `tables/P2B_CONTRASTS.csv`, `tables/P2B_GATE.csv`,
`tables/P2B_RUNS.csv`, `P2B_GATE.json`, `tables/P2B_SWEEP.csv`.

---

## 4. What this changes, and what it does not

* **Does not change** the round-3 H conclusion (`decision = go`, six Design-off cells) — only the C4/C5
  levels move, and the verdict is identical before and after.
* **Does not change** the P0 `Delta_c-s` price (+3.1 … +4.8 %, CI excludes zero in all twelve cells).
* **Does not change** the decision-endpoint reading: still no decision skill on either side, in any
  reportable set.
* **Does change** the provenance of the C4/C5 FedAvg arm and of the replay path: both are now faithful,
  and the five still-stopped sets are stopped for a *narrower* and better-understood reason than before.
* No tolerance was loosened, no exemption was invented after seeing values, no stopped cell set is
  reported, and no manuscript file was touched.

## 5. Outputs

`P2B_ADDENDUM.md`, `P2B_REPORT.md`, `tables/P2B_{RUNS,SWEEP,GATE,CONTRASTS}.csv`, `P2B_GATE.json`;
`results_h_headroom/round_v3_fix/`: `runs/` (40 repaired runs), `tables/C45_REPAIR_GATE.csv`,
`REPAIR_GATE.json`, `tables/H_SUMMARY_fix.csv`, `tables/H_FIX_DIFF.csv`, `H_DECISION_fix.json`.

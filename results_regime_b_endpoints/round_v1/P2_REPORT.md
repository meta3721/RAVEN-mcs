# P2 execution report — stopped by its own replay gate (10 of 12 cell sets)

Round: `results_regime_b_endpoints/round_v1/` · Phase **P2** · executed 2026-10-06 (285 s wall)
Pre-registration: `DESIGN.md` (sha256 `cd2db441…`), stop rule 1:
*"Replay gate failure (> 1e-12 on a non-trigger cell) stops the round for that cell set; no waiver, no
tolerance loosening."* That rule is applied here as written.

## 1. Gate outcome

| pair | condition | non-trigger cells | A-side failures | B-side failures | max abs ΔRMSE (A / B) | gate |
| --- | --- | ---: | ---: | ---: | --- | --- |
| fedavg_rule | C0_frozen | 17 | 0 | 0 | `0.000e+00` / `0.000e+00` | **pass** |
| fedavg_rule | C1_tilt_strong | 17 | 1 (seed 30014) | 0 | `4.58e-02` / `0.000e+00` | fail |
| fedavg_rule | C2_tilt_extreme | 17 | 1 (seed 30002) | 0 | `8.38e-02` / `0.000e+00` | fail |
| fedavg_rule | C3_low_capacity | 17 | 17 | 17 | `3.29e-04` / `3.78e-04` | fail |
| fedavg_rule | C4_block_uniform | 17 | 0 | 17 | `0.000e+00` / `3.22e-03` | fail |
| fedavg_rule | C5_combined | 17 | 17 | 17 | `8.45e-02` / `3.22e-03` | fail |
| oracle_design | C0_frozen | 17 | 0 | 0 | `0.000e+00` / `0.000e+00` | **pass** |
| oracle_design | C1_tilt_strong | 17 | 1 (seed 30014) | 0 | `4.52e-02` / `0.000e+00` | fail |
| oracle_design | C2_tilt_extreme | 17 | 1 (seed 30002) | 0 | `9.09e-02` / `0.000e+00` | fail |
| oracle_design | C3_low_capacity | 17 | 0 | 17 | `0.000e+00` / `4.09e-04` | fail |
| oracle_design | C4_block_uniform | 17 | 0 | 17 | `0.000e+00` / `3.26e-03` | fail |
| oracle_design | C5_combined | 17 | 17 | 17 | `8.85e-02` / `3.22e-03` | fail |

Pairing, replay gate, and the decomposition assertion are otherwise clean: **240/240 cells traced-matched**
and the decomposition equals the screen's `E_dec` on **240/240** cells. `tables/P2_GATE.csv`,
`P2_GATE.json`, `tables/P2_GATED_CONTRASTS.csv`.

## 2. What is reportable (the two gate-passing sets)

| pair | n | `E_dec` A | `E_dec` B | r | 95 % CI | seeds B<A | `missed` A→B | `false_alarm` A→B | TP share A / B | seeds with any TP (A / B) |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- | --- | --- | --- |
| fedavg_rule | 17 | 0.336755 | 0.087341 | **−38.91 %** | [−59.99, −17.84] | 9 | 0.0569 → 0.0859 | 0.2798 → 0.0015 | **33.8 % / 0.1 %** | 8 / 1 |
| oracle_design | 17 | 0.342089 | 0.091010 | **−36.45 %** | [−57.91, −14.99] | 10 | 0.0572 → 0.0859 | 0.2849 → 0.0051 | **33.4 % / 0.1 %** | 7 / 1 |

Sweep on the same 34 gate-passing cells per side (descriptive, no threshold selected):

| T (µg/m³) | `E_dec` A | `E_dec` B | missed A / B | false alarm A / B | seeds with any TP (A / B) |
| ---: | ---: | ---: | --- | --- | --- |
| 25 | 0.799790 | 0.799790 | 0.000 / 0.000 | 0.800 / 0.800 | 34 / 34 |
| 35 | 0.339422 | 0.089176 | 0.057 / 0.086 | 0.282 / 0.003 | 15 / 2 |
| 50 | 0.019916 | 0.019916 | 0.020 / 0.020 | 0.000 / 0.000 | 0 / 0 |
| 75 | 0.000524 | 0.000524 | 0.001 / 0.001 | 0.000 / 0.000 | 0 / 0 |

So the C0 conclusion of P1 generalises across the two arm families: regime B's lower `E_dec` is
false-alarm suppression, and B retains essentially no exceedance detection in either family. **No other
condition is reportable from this run.**

## 3. Diagnosis of the gate failures — two distinct causes

**(a) The replay reconstruction is missing the per-condition injections (executor defect, fixable).**
The training runs were produced under `run_h_headroom.injected(...)`, which sets `theta_align`, the
observation tail scale, the `diurnal_blind` model factory, and — for `block_uniform` — the rescaled
target bundle `mu`. My P2 replay rebuilds the runner through the *screen's* path, which never needed
those injections because the screen only ever evaluated frozen C0 runs. The fingerprints match exactly:

| condition | what the run injected | replay symptom |
| --- | --- | --- |
| C3 `diurnal_blind` | `deterministic_common_ndmf = _diurnal_blind_factory` | both sides miss by ~3e-04 (small, same architecture) |
| C4/C5 `block_uniform` | `production_target_bundle` rescales `mu` by block factors | B side misses by ~3.2e-03 (metric weighting uses `mu`) |
| C1/C2/C5 `theta_align` | `build_joint_pi_opp(theta_align=θ)` | A side misses by 4.5e-02 on one seed each (30014 / 30002) |
| oracle A side at C3/C4 | resolver prefers the frozen run, which is a **C0** run | A side passes at 0.0 while the B side fails — the tell |

The last line is the most informative: for the oracle pair at C3/C4 the A side reproduces *exactly*
(`0.000e+00`) precisely because it is the frozen C0 run replayed through the path that reproduces C0 —
i.e. the resolver, not the data, is what makes those two cells disagree. This is the same
input-resolution class of defect as P0's 60 unpaired cells.

**(b) The A-side `C4`/`C5` runs are not the condition they are labelled with (round-3 grid defect).**
`results_h_headroom/round_v3/runs/C4_block_uniform/.../fedavg_window/seed*` are **identical on every
numeric field to the C0 runs, on all 20 seeds** (only `runtime_seconds` differs), and their recorded
`pi_tar_hash` equals the C0 one (`8bab153a707d1267`) — the same hash the h_round C4 runs carry. Cause,
in `r3_p1p2.train_fedavg`: the injected condition was built as `dict(H.CONDITIONS["C0_frozen"])` with
only `theta`/`tail_scale`/`model` overwritten, so `target` stayed `"test_share"` and
`H.injected(...)` skipped its `block_uniform` branch (the `_bundle` patch that rescales `mu`). The
`pi_target_override` that *was* passed does not change the zero-mass set — block-uniform rescaling
multiplies positive masses — so it left no trace in the metrics. The h_round B-side C4/C5 runs did carry
the `_bundle` patch (`RMSE_mu 1.174352` vs `1.171263` at C0 seed 30001), so **the two sides of the C4/C5
comparisons are not the same condition.**

Consequences outside this round: the round-3 (§Part VI) H-table rows for **C4** and **C5** have a
FedAvg arm that is not the block-uniform condition — C4 is C0-with-a-no-op-override, C5 is
θ=4 + `diurnal_blind` on `test_share`; and this round's P0 `Delta_c-s` cells for C4/C5 inherit the same
A side. The C0–C3 rows are unaffected. This is reported here and is not repaired by this round.

## 4. Actions explicitly NOT taken

* The tolerance was not raised and no cell was waived (the gate is reported failing as it stands).
* No individual seed was dropped to keep a cell set alive.
* No contrast is reported for the ten stopped cell sets beyond the failure inventory.
* Nothing under `TO_OVERLEAF_paper_tmc_r1_clean/` was touched.

## 5. Repair path (needs a decision)

1. **Replay fidelity (cheap, ~10 min)**: replay under `run_h_headroom.CONDITIONS` + `injected(cond,
   block_factor=factor)` and resolve the oracle A side to the condition-matched run, then re-apply the
   same gate. This addresses cause (a) for C1, C2, C3, C5-B and C4-B.
2. **A-side condition repair (new training, ~3 min)**: re-run the round-3 C4/C5 FedAvg runs with
   `target="block_uniform"` **and** `block_factor=factor` so the `_bundle` patch actually applies, then
   re-derive the round-3 H-table rows for C4/C5 and correct Part VI in the ledger.
3. **Or narrow the scope**: declare C4/C5 out of scope for the endpoint round and annotate round 3's C4
   row as condition-invalid.

Option 2 changes a delivered table and a ledger entry, so it is not started without authorization.

## 6. Outputs

`tables/P2_RUNS.csv` (240 cells), `tables/P2_SWEEP.csv`, `tables/P2_GATE.csv`,
`tables/P2_GATED_CONTRASTS.csv`, `tables/P2_GATED_SWEEP_SUMMARY.csv`, `P2_GATE.json`,
`P2_DECISION.json` (the ungated dump produced by the executor, superseded by `P2_GATE.json`).

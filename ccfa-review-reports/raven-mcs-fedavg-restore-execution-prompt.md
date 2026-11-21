# Executable instruction: restore U-Air FedAvg to the frozen active set, then recompute H

```text
Mode: design + execution prompt.
Contract: CCFA-Skills/ccf-experiment-designer. Protocol, not publication prose.
Why this round exists: the H-round U-Air gate waived fedavg_window. On C0, all 20
seeds 30001–30020 rerun below the frozen record (relative RMSE −1.82% to −10.53%).
The same runs are the denominator of round_v1, round_v1_verify, and round_u1.
This round puts that denominator back on the frozen active set and recomputes H.
Output: results_h_headroom/round_v2/ only.
Forbidden: editing src/, the manuscript, results_h_headroom/round_v1/,
           results_h_headroom/round_u1/, results_h_headroom/round_v1_verify/,
           artifacts/, any other results directory;
           retraining raven_simoracle or raven_simoracle_nodesign;
           retraining SensorScope;
           regenerating EventTraces;
           a waiver list (KNOWN_NONREPRO or any successor);
           relaxing the trace comparison, the tolerance, or the active-set check
           after a failure;
           git commit/push.
The user asked for the re-run. It still starts only after Stage B passes.
A Stage B failure stops the round. Do not try a second filter in this round.
```

## 0 What is already measured

C0 U-Air `fedavg_window` in `round_v1` (seeds 30001–30005, source `reuse`) and `round_u1` (seeds 30006–30020, source `new`) was compared with `artifacts/e3_formal_runs_r1/runs/uair/fedavg_window/seed<seed>/final_metrics.json`. All 20 reruns are lower. Seed 30001 differs by `3.958590e-02` (the waived `d=3.96e-02`). Seed 30006 differs by `1.353624e-01` (the waived `d=1.35e-01`).

`raven_simoracle` on the same 20 C0 seeds matches the frozen record with max absolute `RMSE_μ` difference `0`.

Active sets, frozen versus the H/U1 rerun, using `window_metrics.json` and the frozen EventTrace:

| seed | extra client-slots | of which `(client, stratum)` has `pi_tar = 0` | shared slots with `pi_tar > 0` | shared slots with a zero |
|---|---:|---:|---:|---:|
| 30001 | 55 | 55 | 153 | 0 |
| 30006 | 56 | 56 | 135 | 0 |

`pi_tar` is `build_pi_target(..., split="test")` on the sealed U-Air atomic table, with `target_group_main` aliased from `target_group`. 288 keys, 216 positive, 72 zero. No extra slot has a positive mass. No shared slot has a zero mass. The rerun never drops a frozen client on these two seeds.

`H = (RMSE_μ(FedAvg) − RMSE_μ(oracle)) / RMSE_μ(FedAvg)`. `round_u1` pins the U-Air oracle to `raven_simoracle_nodesign` (`FREEZE_ARM_DATASET=uair`). The six U-Air `H_RMSE_mu` cells of that table are the source of `main.tex` `|H| ≤ 0.217%`. This round does not edit that sentence.

SensorScope is outside this round. Its gate had `d=0` on both arms.

## 1 The one pre-registered change

Rule R, locked by the table above. For `fedavg_window` only, a client-window whose `(client_id, opportunity_stratum)` has `pi_tar = 0` is not in `A_r`.

Implementation, in a new script `scripts/h_fedavg_restore.py`. Do not edit `src/`.

- Copy the EventTrace the H round already used. Do not call `generate_trace`.
- On the copy, set `U = 0` on each event row whose stratum has `pi_tar = 0` under the `pi_target` that run will actually use.
- C0, C3, C4 use the test-split target. C4 and C5 also build `block_uniform_target` from `scripts/run_h_headroom.py`; a zero stays a zero under that rescaling, and the filter still reads the override that the run passes in.
- C1, C2, C5 keep the traces already stored for that condition and seed. Seeds 30001–30005 come from `results_h_headroom/round_v1/eventtraces/`. Seeds 30006–30020 come from `results_h_headroom/round_u1/eventtraces/`.
- C0, C3, C4 copies come from `artifacts/e3_formal_runs_r1/eventtraces/uair/seed<seed>/`.
- Write copies under `results_h_headroom/round_v2/eventtraces/`. Leave the source traces unchanged.
- Train with `run_e3_real`, `local_steps=2`, the same condition injection `run_h_headroom.py` uses for that condition (theta, tail scale, diurnal-blind factory, block-uniform override). The method is `fedavg_window`.

`pass` in every JSON file is a JSON boolean, not the string `"True"`.

## 2 Stage B — two-seed gate, then the other C0 seeds

Train C0 `fedavg_window` seed 30001 first, then seed 30006. Compare each with the frozen `final_metrics.json` and `window_metrics.json`.

Pass, all three, on both seeds:

- active-client set equal on every window
- `|RMSE_μ(rerun) − RMSE_μ(frozen)| ≤ 1e-9`
- `|Δ_group(rerun) − Δ_group(frozen)| ≤ 1e-9`

Any miss stops the round. Write `GATE_C0.json` with `pass: false` and the window ids that differ. Do not add a waiver. Do not change rule R. Do not start the other 18 C0 seeds or any stress condition.

If both seeds pass, train C0 seeds 30002–30005 and 30007–30020 under the same rule and the same three checks. Any miss stops the round before C1–C5. A C0 cell that fails is reported; it is not replaced by the old rerun.

## 3 Stage C — the stress grid, FedAvg only

Runs only after all 20 C0 seeds pass.

| condition | theta | tail scale | model | target | seeds |
|---|---:|---:|---|---|---|
| C1_tilt_strong | 2.5 | 0.25 | full | test share | 30001–30020 |
| C2_tilt_extreme | 4.0 | 0.10 | full | test share | 30001–30020 |
| C3_low_capacity | 1.25 | 0.55 | diurnal-blind | test share | 30001–30020 |
| C4_block_uniform | 1.25 | 0.55 | full | block-uniform | 30001–30020 |
| C5_combined | 4.0 | 0.10 | diurnal-blind | block-uniform | 30001–30020 |

These 100 runs have no frozen FedAvg twin. They are accepted because they use the runner that passed Stage B, not because their RMSE is close to `round_v1` or `round_u1`. Do not compare them to those reruns as a pass rule.

Oracle arms are not trained. Copy `RMSE_μ`, `Tail_RMSE`, and `RMSE_ρ` from the existing run directories:

- seeds 30001–30005: `results_h_headroom/round_v1/runs/<condition>/uair/<arm>/seed<seed>/final_metrics.json`
- seeds 30006–30020: `results_h_headroom/round_u1/runs/<condition>/uair/<arm>/seed<seed>/final_metrics.json`

Arms copied: `raven_simoracle`, `raven_simoracle_nodesign`. C0 `raven_simoracle` is the arm already shown bit-identical to the frozen record on these 20 seeds. `raven_simoracle_nodesign` has no directory under `artifacts/e3_formal_runs_r1/runs/uair/`; this round reuses the stored H-round value and does not call it a frozen reproduction.

## 4 H, same definition, new denominator

For each condition, over the 20 U-Air seeds:

```text
H          = (fedavg_v2 − nodesign) / fedavg_v2
H_design   = (fedavg_v2 − simoracle) / fedavg_v2
H_nodesign = (fedavg_v2 − nodesign) / fedavg_v2
```

`fedavg_v2` is this round. `nodesign` and `simoracle` are the copied arms. The U-Air oracle stays pinned to nodesign, so `H` equals `H_nodesign`. Interval: Student-t, `ppf(0.975, n−1)`, the same interval `run_h_headroom.py` writes. Also record the same three ratios for `Tail_RMSE` and `RMSE_ρ`.

`design_support_cost = (simoracle − nodesign) / nodesign` does not use FedAvg. Copy it from `round_u1/tables/H_summary.csv` for the six U-Air rows. Do not recompute it from a new training.

GO rule, unchanged: a non-C0 cell is GO only if `H ≥ 0.005` and the interval lower bound is `> 0`. C0 cannot be GO. `H_DECISION.json` is `STOP` when no cell is GO, `GO` when one is, `INCOMPLETE` if any of the 120 FedAvg runs or any copied oracle file is missing.

## 5 What this round does not rerun

- SensorScope, all conditions.
- Every `raven_simoracle` and `raven_simoracle_nodesign` directory.
- The response-shift grid. Its U-Air FedAvg is a later product of the same runner; it is not a denominator of `round_v1` or `round_u1`.
- `src/` and `main.tex`. The `|H| ≤ 0.217%` sentence stays until a later writing pass is asked for.

## 6 Result tables

`results_h_headroom/round_v2/tables/C0_REPRO.csv`

| seed | RMSE_μ v2 | RMSE_μ frozen | abs diff | Δ_group abs diff | active-set equal | pass |
|---|---|---|---|---|---|---|
| 30001–30020 | TBD | TBD | TBD | TBD | TBD | TBD |

`results_h_headroom/round_v2/tables/H_summary.csv`

| condition | n | H | ci_lo | ci_hi | H_design | H_nodesign | fedavg_RMSE_μ mean | go |
|---|---:|---|---|---|---|---|---|---|
| C0_frozen … C5_combined | 20 | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

`H_seed_rows.csv` carries condition, seed, fedavg source `round_v2`, oracle source path, and the three metrics for each arm.

## 7 Execution order

| Priority | Step | Cost | Stop |
|---|---|---|---|
| P0 | Stage B seeds 30001, 30006 | 2 trains | any of the three checks fails |
| P1 | remaining 18 C0 seeds | 18 trains | any seed fails the same three checks |
| P2 | C1–C5, 20 seeds | 100 trains | a missing oracle file, or a missing FedAvg file |
| P3 | H table and `H_DECISION.json` | none | `INCOMPLETE` if any input is missing |

## 8 No-fabrication status

Stage A counts in section 0 were read from the stored window metrics, the frozen EventTraces, and `build_pi_target`. Every Stage B and Stage C number is `TBD` until the new script writes it. No H value in this file is a result.

Next owner after `H_DECISION.json` exists: report the six H cells. `ccf-paper-writer` only if a later request asks to replace the U-Air ceiling sentence.

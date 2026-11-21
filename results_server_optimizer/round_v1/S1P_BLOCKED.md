# S1' — NSW-Traffic: the block as recorded, and its resolution

This file keeps both states so the history is not lost: the round stopped the NSW-Traffic block under
section 1's STOP rule, and the block was afterwards resolved by explicit user authorization.

## 1. The block (recorded 2026-10-08, before authorization)

`run_e3_real` calls `assert_schedulable_e3_run` before doing any work. For

- `dataset = "traffic"`, `scenario = "complete_aligned"`, any seed in `30001..30020`
  (`FORMAL_SEEDS`), and
- `method` in `E2_TRAFFIC_REUSED_METHODS = [fedavg_window, fedasync_window,
  flamf_timealign_adapted, twostage_hajek, raven]`

it raises `DuplicateReusedTrafficRunBlocked` with code `DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED`.
Stage A trains `fedavg_window` on all three blocks, so all 15 traffic cells were refused. The exact
error text is preserved per cell in `tables/STAGE_A_VALIDATION.csv`.

The instruction forbids editing `src/`, and the guard is a deliberate protocol control
(`REUSE_ONLY_NO_RERUN from sealed E2 Traffic Complete-aligned`), so the refusal was recorded rather
than worked around, exactly as `S1P_REPORT.md` deviation 1 described at the time. Consequence: N3'
for NSW-Traffic was reported as `BLOCKED`, no traffic cell was trained, Stage C did not run for it,
and **GO-H was unreachable**, because section 6's `K_r` clause excludes SensorScope and U-Air and
NSW-Traffic was the only remaining block.

## 2. Provenance of the conflict (corrected after further checking)

`src/raven_mcs/e3/protocol_closure/` is untracked in git, so file mtimes record only the last write.
`reuse_guard.py` carries mtime **2026-10-07 17:00:29** and `real_runner/runner.py` **17:00:32**, both
after the earlier new-block traffic round finished at 16:27:41 — which is why that round's fresh
`traffic/complete_aligned/fedavg_window` runs exist. **But the guard module is not new**: the canary
evidence `artifacts/e3_multidataset_real_runner_canary_r1/E3_CANARY_TRAFFIC_REUSE_GUARD.json`
(mtime **2026-08-10 21:57:49**) reports `formal_block_still_active: true` and
`is_reused_e2_helper: true`, both produced by calling this guard's own functions. What the 2026-10-07
writes mark is the **wiring into `run_e3_real`**. Recorded in the diagnosis ledger Part IX items
64 (amended) and 66.

Note also that `E2_TRAFFIC_REUSED_METHODS` contains `raven` as well as `fedavg_window`, and that the
canary guard `e3/canary/traffic_reuse_guard.py` imports this one and adds a strictly wider exclusion
(the same five methods on traffic at any seed, including the canary seed 31001).

## 3. The resolution (2026-10-08, under explicit user authorization)

The user authorized a narrow, reversible relaxation and chose its form: an explicit, default-`False`
`allow_reused_traffic_rerun` parameter on `assert_schedulable_e3_run`, read by `run_e3_real` from
`source_identity`. No existing caller changes behaviour; the exemption announces itself with a
`RuntimeWarning`; `is_reused_e2_traffic_block` and `filter_new_schedule` are unchanged; and the canary
path is unaffected (verified: its evidence builder still returns `status: PASS`, the five sealed
methods are still refused at seed 31001, and the six permitted arms still pass).

Byte-level backup of every file the change touched, a sha256 manifest of 9 175 sealed-evidence files
(hashes only, not copies) and a runnable `RESTORE.py` are under `backup_pre_guard_change/`.
`reuse_guard.py` went `46d26da601b82672` -> `3d79703e5456016b` (exemption) -> `57223308d88df73d`
(docstring correction); `runner.py` `4c25921a042e1954` -> `c82b261c10c3eb2b`.

## 4. What the traffic block produced once run

- Stage A, 15 cells, all complete: validation means `eta_s=1e-3` 0.864388, **`eta_s=3e-3` 0.819805
  (selected)**, `eta_s=1e-2` 0.907197, each over 5/5 screen seeds.
- **N3' = PASS**: `c = 0.9737694569747332`, new `fedavg = 0.8350944692092265`,
  `ratio_to_c = 0.8575895076886716`. SensorScope 0.986505 PASS, U-Air 0.832921 PASS.
- Traffic identity test (the gap amendment A2 left): override disabled versus override with plain
  SGD gives 32/32 deterministic fields equal, a **byte-identical checkpoint** and an identical
  `K_r <= 3` share; a forced repeat of one cell reproduced `RMSE_mu`, the checkpoint hash and the
  validation `RMSE_mu` exactly.
- Stage C: **NO-GO-H**, `mean_H = -0.080700`, CI `[-0.268877, +0.017194]`, `MDE80(n=5) = 0.349835`,
  `K_r <= 3` share 0.111111. Note `kr_excluded_from_GO = False` for traffic: this NO-GO-H is a
  **measured** result, not the structural exclusion that applies to SensorScope and U-Air.

Every exempted run carries `REUSE_GUARD_EXEMPTION.json` in its run directory (15/15 for Stage A), and
the ledger cannot carry it — `run_e3_real` writes only five named fields from `source_identity` — so
the driver records it in `SERVER_OPT_META.json` as well (ledger items 71).

## 5. What would still unblock a *materially* different traffic experiment

Nothing here authorizes comparing these new runs with the frozen E3 traffic evidence as if they were
the same objects: the E3 traffic block reused E2 rather than retraining it, and the runner has drifted
since (the 2026-08-11 runs recorded `runner_source_hash = 2f5728de...`, and the file now hashes to
`c82b261c...`). Any future traffic run must carry that caveat, and a fair centralized-versus-federated
statement additionally needs the centralized arm retrained under the same optimizer.

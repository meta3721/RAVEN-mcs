# S1' — server optimizer re-screen: report

- Instruction: `ccfa-review-reports/raven-mcs-s1prime-server-optimizer-execution-prompt.md`, sha256 `14b09cbfafa40db088fb65d117229810916b0a8ef12037f0305eb3c7e22aebd4`
- Driver: `results_server_optimizer/round_v1/driver/s1p_driver.py`, sha256 `308007730989dafc1544b0ad3e60d0a3a949a3cb4f3b802cfb2084c6605ac98e`
- Frozen config: `S1P_FROZEN_CONFIG.json`, sha256 `a041ba42e9c139f70356a5cbe0213cb15f6819123dd16e4b678a45ed82df4cde`
- No manuscript, `tdrive_protocol_seal_r1/`, or frozen artifact was edited; no commit, no push. No EventTrace was created. All round outputs are under `results_server_optimizer/round_v1/`. `src/` **was** changed, but only after this round closed and only under explicit user authorization: the E3 reuse guard gained a default-off `allow_reused_traffic_rerun` opt-in so that NSW-Traffic could be run (ledger Part IX item 65; byte-level backup and `RESTORE.py` under `backup_pre_guard_change/`). Every NSW-Traffic run in this report carries that exemption, recorded per run in `REUSE_GUARD_EXEMPTION.json` and `SERVER_OPT_META.json`.

## 1. Section-0 premises, independently recomputed

Reconstructed `theta_init = deterministic_common_ndmf(n_spatial, seed=run_seed).state_dict()` (the init path at `window_runner.py` L192 / `runner.py` L476) and compared it against every frozen checkpoint. `src/raven_mcs/models/common_ndmf.py` is content-identical to the frozen runs' commit `b01db69e` (empty git diff), so the reconstruction is exact; all 84 checkpoints also match the `checkpoint_hash` recorded in their own `runtime_manifest.json`.

| section-0 claim | recomputed (seeds 30001-30003) | holds |
| --- | --- | --- |
| fedavg_window / raven / local_hajek move 0.26 % on SensorScope | 0.2614 / 0.2708 / 0.2614 % | yes |
| ... 0.40 % on U-Air | 0.3965 / 0.4032 / 0.3965 % | yes |
| ... 0.28 % on NSW-Traffic | local_hajek 0.2786 % (the E3 traffic tree has no fedavg_window/raven) | yes for the arms that exist |
| mostly through the output bias `head.8.bias` | top-1 by squared movement: 41-47 % (SS), 41-47 % (UA), 51-62 % (Traffic) | yes |
| spatial embeddings move 0.01 % | 0.0050-0.0088 % (2 d.p. -> 0.01 %) | yes |
| SensorScope `central_all` moves `head.0.weight` by 12.2 % | 12.1524 % | yes |

Additional fact section 0 does not state: `central_all` / `central_delivered` move only 2.4-3.2 % of their total norm, so the centralized references are themselves barely trained. This matters for interpreting N3' (see deviations).

## 2. Gates

- **G1** reads-after-update audit: STOP condition not fired. The one real finding is **L1204** `after_hash = self._theta_hash()`, evaluated inside the base `_process_window` before the optimizer step, so `WindowMetrics.theta_hash_after` and the per-client `global_model_hash` / `model_hash_after` log `theta_sgd`; `final_metrics.json` has 32 keys and no hash key, so no decision metric is affected.
- **G0** identity test: **deterministic verdict True** over 4 (block, arm) pairs (32 fields each, 0 deterministic mismatches, `checkpoints/final.pt` byte-identical). The literal reading including `runtime_seconds` is False, which no pair of runs can satisfy because it is a wall clock; the field is named in one place in the driver and both values are recorded in `S1P_G0_COMPARE.json`.
- **G2** determinism: **True** (same config twice, `eta_s = 1e-3` FedAdam).
- NSW-Traffic was not gated at G0 (amendment A2: the E3 traffic tree has no `fedavg_window` and no `raven` arm).

### Frozen-artifact diagnostic (disclosure only, amendment A1)

| block | arm | frozen `RMSE_mu` | re-run `RMSE_mu` | relative |
| --- | --- | --- | --- | --- |
| sensorscope | fedavg_window | 7.914361980993586 | 7.914361980993586 | 0.000e+00 |
| sensorscope | raven | 7.913791224192832 | 7.913791224192832 | 0.000e+00 |
| uair | fedavg_window | 1.210848485707097 | 1.1712625825964957 | 3.269e-02 |
| uair | raven | 1.201716880706229 | 1.201716880706229 | 0.000e+00 |

SensorScope `fedavg_window`, SensorScope `raven` and U-Air `raven` reproduce the frozen artifacts exactly (U-Air `raven` with a byte-identical checkpoint). **U-Air `fedavg_window` does not** (-3.27 %, active windows 66 -> 74, `a_r_size` systematically one larger). That arm is a Table II baseline, so it is reported as a finding in its own right; it does not affect this round, whose comparisons are all same-tree re-runs.

## 3. Stage A — optimizer grid

Grid `eta_s in {1e-3, 3e-3, 1e-2}`, arm `fedavg_window`, blocks x 5 screen seeds. Selection on the **validation** split only; the frozen configuration was written before any test value was read.

| block | eta_s | n non-diverged | mean validation `RMSE_mu` |
| --- | --- | --- | --- |
| sensorscope | 0.001 | 5 | 3.4287507881327777 |
| sensorscope | 0.003 | 5 | 3.446440478205382 |
| sensorscope | 0.01 | 5 | 3.415263775693982 |
| uair | 0.001 | 5 | 1.2644849348292768 |
| uair | 0.003 | 5 | 1.2473460841447461 |
| uair | 0.01 | 5 | 1.267419881996209 |
| traffic | 0.001 | 5 | 0.8643880405673758 |
| traffic | 0.003 | 5 | 0.8198046723735383 |
| traffic | 0.01 | 5 | 0.907196502773617 |

Selected: SensorScope `eta_s* = 0.01`, U-Air `eta_s* = 0.003`, NSW-Traffic `eta_s* = 0.003`.

### N3' on test

| block | verdict | eta_s* | c (frozen central_delivered) | frozen fedavg_window | new fedavg | ratio to c |
| --- | --- | --- | --- | --- | --- | --- |
| sensorscope | PASS | 0.01 | 7.952597152468874 | 7.908941521700865 | 7.84527305561617 | 0.9865045223849438 |
| uair | PASS | 0.003 | 1.1735735654775155 | 1.1599245853724733 | 0.9774940049430552 | 0.8329209464984179 |
| traffic | PASS | 0.003 | 0.9737694569747332 | None | 0.8350944692092265 | 0.8575895076886716 |

### What the server optimizer actually did

| block | eta_s | mean overall parameter movement |
| --- | --- | --- |
| sensorscope | 0.001 | 2.491 % |
| sensorscope | 0.003 | 6.108 % |
| sensorscope | 0.01 | 18.366 % |
| uair | 0.001 | 2.800 % |
| uair | 0.003 | 7.311 % |
| uair | 0.01 | 22.055 % |
| traffic | 0.001 | 4.049 % |
| traffic | 0.003 | 9.151 % |
| traffic | 0.01 | 22.024 % |

Against 0.26 % (SensorScope), 0.40 % (U-Air) and 0.28 % (NSW-Traffic) under the frozen SGD server step, FedAdam moves the model 2.5-22 %, i.e. 7-70x more. The round's own question - does a standard server optimizer make the federated learner learn - is therefore answered **yes**, and this also confirms section 0's diagnosis that the tiny fixed server step was the bottleneck.

## 4. Stage B — rounds per window

**Not run.** Section 5 applies Stage B only to blocks not PASS at Stage A, and SensorScope, U-Air and NSW-Traffic all PASS.

## 5. Stage C — headroom re-measure

| block | mean H | bootstrap 95 % CI | MDE80 (n = 5) | K_r<=3 share | verdict |
| --- | --- | --- | --- | --- | --- |
| sensorscope | -0.018749 | [-0.039045, 0.001548] | 4.353e-02 | 0.7525773195876289 | NO-GO-H |
| uair | -0.163333 | [-0.247807, -0.059271] | 2.050e-01 | 0.6621621621621622 | NO-GO-H |
| traffic | -0.080700 | [-0.268877, 0.017194] | 3.498e-01 | 0.1111111111111111 | NO-GO-H |

- **sensorscope**: H >= 1 %: False; lower bound > 0.5 %: False; MDE80 < 0.5 H: False; section-6 K_r clause (0.7525773195876289 > 0.25): excluded from GO = True.
- **uair**: H >= 1 %: False; lower bound > 0.5 %: False; MDE80 < 0.5 H: False; section-6 K_r clause (0.6621621621621622 > 0.25): excluded from GO = True.

**The verdict is NO-GO-H on all three blocks, and on NSW-Traffic it is a measured result rather than a structural one.** Section 6 forbids upgrading SensorScope or U-Air to GO when more than 25 % of active windows have `K_r <= 3`, and under the new configuration both are far above that (0.753 and 0.662). NSW-Traffic is the one block the clause does not exclude (its share is 0.111), so it was run: H there is negative and its interval contains zero. On U-Air the oracle arm is *significantly worse* than plain FedAvg (the whole interval is below zero), which is the opposite of headroom. The plain reading is therefore that the oracle-margin reference supplies no headroom on any of the three blocks once the learner actually trains - which is the point section 0 raised when it observed that the earlier H was measured on an untrained model.

## 6. Deviations, blocks and corrections

1. **NSW-Traffic was refused at first, then run under an authorized exemption.** The E3 reuse guard (`src/raven_mcs/e3/protocol_closure/reuse_guard.py`) refuses `traffic` + `complete_aligned` + seed in 30001..30020 + `{fedavg_window, raven}` with `DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED`, so the first pass recorded all 15 traffic cells as BLOCKED and stopped that block rather than editing `src/` (`S1P_BLOCKED.md`, which is kept as the historical record). The user then authorized a narrow, reversible relaxation and asked for the block; it was run and all three blocks now PASS N3'. Two provenance points, correcting an earlier statement in this session: the guard module is **not** new - its functions were already refusing correctly in the 2026-08-10 canary evidence - and what the 2026-10-07 17:00:29/17:00:32 writes mark is the **wiring into `run_e3_real`**, which is why the 15:25-16:27 traffic round could train sealed-method cells (ledger Part IX items 64/66).
2. **G0's literal wording cannot be met.** `runtime_seconds` is a wall clock; the deterministic reading is used, the excluded field and both of its values are reported in `S1P_G0_COMPARE.json`.
3. **The runner emits no validation metric.** `run_e3_real` calls `_predict(..., split="test")` only, and `window_metrics.json` rows carry just `{window_id, active, active_clients, a_r_size, alpha, beta_hat}`. Validation `RMSE_mu` is therefore computed by this driver as read-only post-processing from the saved checkpoint, with `mu_g` from a `TargetBuilder(split="validation")` build on the same `target_group_main` mapping. This choice and its exact formula were pre-registered in the driver source *before* the grid ran; the test-`mu`-weighted variant is not used for selection.
4. **The test seal is procedural, not physical.** The runner writes test metrics into each run directory as part of its own output contract, which cannot be changed without editing `src/`. No test-derived value was written to any file, and no selection code path read one, before `S1P_FROZEN_CONFIG.json` existed.
5. **One cell was damaged by my own tooling and repaired.** I terminated the first Stage A attempt to restructure the traffic handling; `A_eta0.003/sensorscope/fedavg_window/seed30005` was left without `final_metrics.json` or `checkpoints/final.pt`. It was detected (1 cell with `ckpt_ok=False`), its directory verified as incomplete and under the round tree, removed, and re-run; the selection was then redone. The first frozen configuration (`fe84a4c6fb1124ed...`) is superseded by `57b4bcec0cb030cf...`; the selection outcome did not change. No test value was used in either pass.
6. **An empty-directory artefact initially mis-classified the traffic cells.** `run_one` creates the run directory before `run_e3_real` reaches the guard, so 15 empty directories were left behind and the following pass reported them as `diverged` rather than `BLOCKED`. They were verified empty and removed, and the pass was repeated so the refusal is recorded as `BLOCKED` with the guard's own error text.
7. **N3' PASS on U-Air is not a like-for-like optimizer comparison.** The reference `central_delivered` moves only ~3.2 % of its parameter norm (section 1), so it is itself barely trained. The federated arm now moves 7.3 %, beats that reference, and would likely also beat a centralized model trained with the same optimizer. A fair centralized-vs-federated statement needs the centralized arm retrained under FedAdam, which is outside this round. The N3' rule as written was applied unchanged.
8. **GO-H was evaluable only on NSW-Traffic, and that measurement is NO-GO-H.** SensorScope and U-Air are excluded by the section-6 `K_r` clause; traffic is not, and its H is negative with an interval containing zero.
9. **G0's identity property was re-established on NSW-Traffic.** Amendment A2 had excluded traffic from G0 because the E3 traffic tree lacks those arms, so the override had never been checked there. It now has been: override disabled versus override with plain SGD on `traffic/fedavg_window/seed30001` gives 32/32 deterministic fields equal, only `runtime_seconds` differing, a byte-identical checkpoint, and an identical `K_r <= 3` share; a forced repeat of one cell reproduced its `RMSE_mu`, checkpoint hash and validation `RMSE_mu` exactly. See `S1P_TRAFFIC_G0_DIAGNOSTIC.json`.
10. **The exemption is not recorded in the run ledger, and an earlier claim that it was has been withdrawn.** `run_e3_real` writes only `git_commit`, `source_manifest_hash`, `method_source_hash`, `runner_source_hash` and `dataset_hash` out of `source_identity` (`runner.py` L307-L311), so a custom key never reaches the ledger. The driver therefore writes `REUSE_GUARD_EXEMPTION.json` and a `reuse_guard_exemption` field in `SERVER_OPT_META.json` into every exempted run (15/15 traffic cells in Stage A), and the guard docstring was corrected to say so (ledger item 71).
11. **The E3 metric schema has no loss field at all.** `final_metrics.json` carries the same 32 keys on all three blocks, and none of them is a training loss; the loss-like keys (`Gap_mis`, `target_risk_objective`, `empirical_risk_objective`, `active_window_count`, ...) exist only in the older 21-key **E2** schema. So section 4's "final training Hajek loss" is unobtainable on every block, not just traffic - the fourth place this instruction assumes an artifact that does not exist. An earlier reading in this session that called several E3 fields `None` was reading absent keys through `dict.get` and is withdrawn.
12. **Two defects in this session's own driver, found and fixed; no reported number changed.** The skip test did not require a run to be complete, so a directory left behind by a guard refusal was later treated as a finished run (it mis-classified traffic cells twice); it now requires both `final_metrics.json` and `checkpoints/final.pt`. And level selection could average over fewer than the five screen seeds - on the first traffic attempt `eta_s=1e-3` was selected from a single surviving seed and the following pass crashed on a missing file; a level is now selectable only when all five screen seeds are usable, otherwise the block reports `NO_ELIGIBLE_LEVEL`. The final traffic selection uses 5/5 seeds.

## 7. Deviations from the instruction's own assumptions, summarised

| instruction assumes | actual | handling |
| --- | --- | --- |
| base class `WindowRunner` | the class is `FullWindowRunner` | corrected in the driver |
| `eta = 0.01` recorded in configs | dataclass default only; not in any `config_snapshot.json` | verified in code, asserted at runtime |
| G0 can match the frozen files bit-exact | impossible for artifact-vintage reasons | amendment A1: identity test against a re-run |
| traffic has `fedavg_window` / `raven` | E3 traffic tree has neither | A2 for G0; traffic re-run under the item-65 exemption |
| each run records validation `RMSE_mu` | no validation metric is emitted | computed read-only, pre-registered |
| `MDE80` at n = 15 | screen is n = 5 | amendment A3; traffic shows 5/5 usable screen seeds |
| each run records a training loss | the E3 schema has no loss field at all | recorded as unobtainable (deviation 11) |
| the guard is a 2026-10-07 addition | it existed by 2026-08-10; 2026-10-07 is the wiring | corrected (deviation 1, ledger item 66) |
| an exempted run records the exemption in its ledger | `source_identity` is filtered to five keys | driver writes a per-run record (deviation 10) |

## 8. Files

- `results_server_optimizer/round_v1/backup_pre_guard_change/BACKUP_MANIFEST.json`
- `results_server_optimizer/round_v1/backup_pre_guard_change/RESTORE.py`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/__init__.py`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/__pycache__/__init__.cpython-311.pyc`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/__pycache__/central_reference.cpython-311.pyc`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/__pycache__/constants.cpython-311.pyc`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/__pycache__/method_registry.cpython-311.pyc`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/__pycache__/pair_state.cpython-311.pyc`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/__pycache__/reuse_guard.cpython-311.pyc`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/central_reference.py`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/complete_aligned.py`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/constants.py`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/method_registry.py`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/pair_state.py`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/protocol_closure/reuse_guard.py`
- `results_server_optimizer/round_v1/backup_pre_guard_change/src/src/raven_mcs/e3/real_runner/runner.py`
- `results_server_optimizer/round_v1/driver/__pycache__/s1p_driver.cpython-311.pyc`
- `results_server_optimizer/round_v1/driver/check_artifact_consistency.py`
- `results_server_optimizer/round_v1/driver/gate_g0_compare.py`
- `results_server_optimizer/round_v1/driver/gates_run.log`
- `results_server_optimizer/round_v1/driver/preflight_section0.py`
- `results_server_optimizer/round_v1/driver/s1p_driver.py`
- `results_server_optimizer/round_v1/driver/stageA.log`
- `results_server_optimizer/round_v1/driver/stageA_final_stderr.log`
- `results_server_optimizer/round_v1/driver/stageA_repair.log`
- `results_server_optimizer/round_v1/driver/stageA_repair_stderr.log`
- `results_server_optimizer/round_v1/driver/stageA_stderr.log`
- `results_server_optimizer/round_v1/driver/stageA_traffic.log`
- `results_server_optimizer/round_v1/driver/stageA_traffic2.log`
- `results_server_optimizer/round_v1/driver/stageA_traffic2_stderr.log`
- `results_server_optimizer/round_v1/driver/stageA_traffic_stderr.log`
- `results_server_optimizer/round_v1/driver/stageC.log`
- `results_server_optimizer/round_v1/driver/stageC_stderr.log`
- `results_server_optimizer/round_v1/driver/stageC_traffic.log`
- `results_server_optimizer/round_v1/driver/stageC_traffic_stderr.log`
- `results_server_optimizer/round_v1/driver/traffic_identity_check.py`
- `results_server_optimizer/round_v1/driver/write_final_artifacts.py`
- `results_server_optimizer/round_v1/driver/write_gates_doc.py`
- `results_server_optimizer/round_v1/PREFLIGHT_SECTION0.json`
- `results_server_optimizer/round_v1/S1P_BLOCKED.md`
- `results_server_optimizer/round_v1/S1P_FROZEN_CONFIG.json`
- `results_server_optimizer/round_v1/S1P_G0_COMPARE.json`
- `results_server_optimizer/round_v1/S1P_G2.json`
- `results_server_optimizer/round_v1/S1P_GATES.json`
- `results_server_optimizer/round_v1/S1P_GATES.md`
- `results_server_optimizer/round_v1/S1P_REPORT.md`
- `results_server_optimizer/round_v1/S1P_STAGE_A_VERDICT.json`
- `results_server_optimizer/round_v1/S1P_STAGE_C_H.json`
- `results_server_optimizer/round_v1/S1P_TRAFFIC_G0_DIAGNOSTIC.json`
- `results_server_optimizer/round_v1/S1P_VERDICT.json`
- `results_server_optimizer/round_v1/tables/MOVEMENT.csv`
- `results_server_optimizer/round_v1/tables/STAGE_A_GRID.csv`
- `results_server_optimizer/round_v1/tables/STAGE_A_VALIDATION.csv`
- `results_server_optimizer/round_v1/tables/STAGE_B_GRID.csv`
- `results_server_optimizer/round_v1/tables/STAGE_C_H.csv`


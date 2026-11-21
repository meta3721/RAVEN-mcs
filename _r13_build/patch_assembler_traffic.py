import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\driver\write_final_artifacts.py")
t = p.read_text(encoding="utf-8")

PAIRS = []

# --- verdict: Stage B reason ---
PAIRS.append((
'''                "reason": "section 5 runs Stage B only for blocks not PASS at Stage A; SensorScope and "
                          "U-Air both PASS, and NSW-Traffic is blocked before any run"},''',
'''                "reason": "section 5 applies Stage B only to blocks not PASS at Stage A; SensorScope, "
                          "U-Air and NSW-Traffic all PASS, so no block qualified"},'''))

# --- header: src/ was edited after the round closed ---
PAIRS.append((
'''A("- No `src/`, manuscript, `tdrive_protocol_seal_r1/`, or frozen artifact was edited. No commit, "
  "no push. No EventTrace created. All outputs are under `results_server_optimizer/round_v1/`.")''',
'''A("- No manuscript, `tdrive_protocol_seal_r1/`, or frozen artifact was edited; no commit, no push. "
  "No EventTrace was created. All round outputs are under `results_server_optimizer/round_v1/`. "
  "`src/` **was** changed, but only after this round closed and only under explicit user "
  "authorization: the E3 reuse guard gained a default-off `allow_reused_traffic_rerun` opt-in so "
  "that NSW-Traffic could be run (ledger Part IX item 65; byte-level backup and `RESTORE.py` under "
  "`backup_pre_guard_change/`). Every NSW-Traffic run in this report carries that exemption, "
  "recorded per run in `REUSE_GUARD_EXEMPTION.json` and `SERVER_OPT_META.json`.")'''))

# --- selection line: traffic now has an eta_s* ---
PAIRS.append((
'''  f"NSW-Traffic blocked.")''',
'''  f"NSW-Traffic `eta_s* = {cfg['per_block']['traffic'].get('eta_s_star')}`.")'''))

# --- movement table: include traffic ---
PAIRS.append((
'''for b in ("sensorscope", "uair"):
    for eta in ("0.001", "0.003", "0.01"):''',
'''for b in ("sensorscope", "uair", "traffic"):
    for eta in ("0.001", "0.003", "0.01"):'''))

PAIRS.append((
'''A("Against 0.26 % (SensorScope) and 0.40 % (U-Air) under the frozen SGD server step, FedAdam moves the "
  "model 2.5-22 %, i.e. 7-70x more. The round's own question - does a standard server optimizer make "
  "the federated learner learn - is therefore answered **yes**, and this also confirms section 0's "
  "diagnosis that the tiny fixed server step was the bottleneck.")''',
'''A("Against 0.26 % (SensorScope), 0.40 % (U-Air) and 0.28 % (NSW-Traffic) under the frozen SGD server "
  "step, FedAdam moves the model 2.5-22 %, i.e. 7-70x more. The round's own question - does a standard "
  "server optimizer make the federated learner learn - is therefore answered **yes**, and this also "
  "confirms section 0's diagnosis that the tiny fixed server step was the bottleneck.")'''))

# --- Stage B ---
PAIRS.append((
'''A("**Not run.** Section 5 applies Stage B only to blocks not PASS at Stage A. SensorScope and U-Air "
  "both PASS; NSW-Traffic is blocked before any run (section 5).")''',
'''A("**Not run.** Section 5 applies Stage B only to blocks not PASS at Stage A, and SensorScope, "
  "U-Air and NSW-Traffic all PASS.")'''))

# --- Stage C conclusion: measured, not structural ---
PAIRS.append((
'''    A("**GO-H is unreachable in this round by construction.** Section 6 forbids upgrading SensorScope "
      "or U-Air to GO when more than 25 % of active windows have `K_r <= 3`, and both blocks are far "
      "above that (78.6 % and 90.2 % on the frozen runs, and the same order under the new config). "
      "NSW-Traffic - the one block where the clause would not apply - cannot be run at all (section 6 "
      "of this report). So the H measurement is reported and the verdict is NO-GO-H, for a structural "
      "reason rather than a measured failure.")''',
'''    A("**The verdict is NO-GO-H on all three blocks, and on NSW-Traffic it is a measured result rather "
      "than a structural one.** Section 6 forbids upgrading SensorScope or U-Air to GO when more than "
      "25 % of active windows have `K_r <= 3`, and under the new configuration both are far above that "
      "(0.753 and 0.662). NSW-Traffic is the one block the clause does not exclude (its share is "
      "0.111), so it was run: H there is negative and its interval contains zero. On U-Air the oracle "
      "arm is *significantly worse* than plain FedAvg (the whole interval is below zero), which is the "
      "opposite of headroom. The plain reading is therefore that the oracle-margin reference supplies "
      "no headroom on any of the three blocks once the learner actually trains - which is the point "
      "section 0 raised when it observed that the earlier H was measured on an untrained model.")'''))

# --- deviation 1: rewritten narrative ---
PAIRS.append((
'''A("1. **NSW-Traffic Stage A BLOCKED (section 1 STOP condition).** `src/raven_mcs/e3/protocol_closure/"
  "reuse_guard.py` refuses `traffic` + `complete_aligned` + seed in 30001..30020 + "
  "`{fedavg_window, raven}` with `DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED`. The module is **untracked** "
  "and its mtime is **2026-10-07 17:00:29**, i.e. it was added *after* the earlier traffic round "
  "finished at 16:27 - which is how that round's fresh `traffic/complete_aligned/fedavg_window` runs "
  "exist. Stage A trains `fedavg_window` on traffic, so all 15 cells are refused. Meeting this "
  "condition would require editing `src/`, so it is recorded as a block (see `S1P_BLOCKED.md`) rather "
  "than worked around, and the SensorScope/U-Air cells are unaffected. This is the third place the "
  "instruction assumes an artifact that does not exist (after G0's traffic arms and the validation "
  "metric).")''',
'''A("1. **NSW-Traffic was refused at first, then run under an authorized exemption.** The E3 reuse "
  "guard (`src/raven_mcs/e3/protocol_closure/reuse_guard.py`) refuses `traffic` + `complete_aligned` "
  "+ seed in 30001..30020 + `{fedavg_window, raven}` with `DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED`, so "
  "the first pass recorded all 15 traffic cells as BLOCKED and stopped that block rather than editing "
  "`src/` (`S1P_BLOCKED.md`, which is kept as the historical record). The user then authorized a "
  "narrow, reversible relaxation and asked for the block; it was run and all three blocks now PASS "
  "N3'. Two provenance points, correcting an earlier statement in this session: the guard module is "
  "**not** new - its functions were already refusing correctly in the 2026-08-10 canary evidence - and "
  "what the 2026-10-07 17:00:29/17:00:32 writes mark is the **wiring into `run_e3_real`**, which is "
  "why the 15:25-16:27 traffic round could train sealed-method cells (ledger Part IX items 64/66).")'''))

# --- deviation 8 + new deviations 9-12 ---
PAIRS.append((
'''A("8. **GO-H is unreachable in this round** (section 5): SensorScope and U-Air are excluded by the "
  "section-6 `K_r` clause, and NSW-Traffic is blocked.")''',
'''A("8. **GO-H was evaluable only on NSW-Traffic, and that measurement is NO-GO-H.** SensorScope and "
  "U-Air are excluded by the section-6 `K_r` clause; traffic is not, and its H is negative with an "
  "interval containing zero.")
A("9. **G0's identity property was re-established on NSW-Traffic.** Amendment A2 had excluded traffic "
  "from G0 because the E3 traffic tree lacks those arms, so the override had never been checked "
  "there. It now has been: override disabled versus override with plain SGD on "
  "`traffic/fedavg_window/seed30001` gives 32/32 deterministic fields equal, only `runtime_seconds` "
  "differing, a byte-identical checkpoint, and an identical `K_r <= 3` share; a forced repeat of one "
  "cell reproduced its `RMSE_mu`, checkpoint hash and validation `RMSE_mu` exactly. See "
  "`S1P_TRAFFIC_G0_DIAGNOSTIC.json`.")
A("10. **The exemption is not recorded in the run ledger, and an earlier claim that it was has been "
  "withdrawn.** `run_e3_real` writes only `git_commit`, `source_manifest_hash`, `method_source_hash`, "
  "`runner_source_hash` and `dataset_hash` out of `source_identity` (`runner.py` L307-L311), so a "
  "custom key never reaches the ledger. The driver therefore writes `REUSE_GUARD_EXEMPTION.json` and "
  "a `reuse_guard_exemption` field in `SERVER_OPT_META.json` into every exempted run (15/15 traffic "
  "cells in Stage A), and the guard docstring was corrected to say so (ledger item 71).")
A("11. **The E3 metric schema has no loss field at all.** `final_metrics.json` carries the same 32 "
  "keys on all three blocks, and none of them is a training loss; the loss-like keys "
  "(`Gap_mis`, `target_risk_objective`, `empirical_risk_objective`, `active_window_count`, ...) exist "
  "only in the older 21-key **E2** schema. So section 4's \\"final training Hajek loss\\" is "
  "unobtainable on every block, not just traffic - the fourth place this instruction assumes an "
  "artifact that does not exist. An earlier reading in this session that called several E3 fields "
  "`None` was reading absent keys through `dict.get` and is withdrawn.")
A("12. **Two defects in this session's own driver, found and fixed; no reported number changed.** The "
  "skip test did not require a run to be complete, so a directory left behind by a guard refusal was "
  "later treated as a finished run (it mis-classified traffic cells twice); it now requires both "
  "`final_metrics.json` and `checkpoints/final.pt`. And level selection could average over fewer than "
  "the five screen seeds - on the first traffic attempt `eta_s=1e-3` was selected from a single "
  "surviving seed and the following pass crashed on a missing file; a level is now selectable only "
  "when all five screen seeds are usable, otherwise the block reports `NO_ELIGIBLE_LEVEL`. The final "
  "traffic selection uses 5/5 seeds.")'''))

# --- section 7 table: corrected handling + new rows ---
PAIRS.append((
'''A("| traffic has `fedavg_window` / `raven` | E3 traffic tree has neither | amendment A2 for G0; Stage A blocked |")''',
'''A("| traffic has `fedavg_window` / `raven` | E3 traffic tree has neither | A2 for G0; traffic re-run under the item-65 exemption |")'''))

PAIRS.append((
'''A("| `MDE80` at n = 15 | screen is n = 5 | amendment A3 |")''',
'''A("| `MDE80` at n = 15 | screen is n = 5 | amendment A3; traffic shows 5/5 usable screen seeds |")
A("| each run records a training loss | the E3 schema has no loss field at all | recorded as unobtainable (deviation 11) |")
A("| the guard is a 2026-10-07 addition | it existed by 2026-08-10; 2026-10-07 is the wiring | corrected (deviation 1, ledger item 66) |")
A("| an exempted run records the exemption in its ledger | `source_identity` is filtered to five keys | driver writes a per-run record (deviation 10) |")'''))

for old, new in PAIRS:
    n = t.count(old)
    assert n == 1, f"anchor count {n} for: {old[:70]!r}"
    t = t.replace(old, new)

p.write_text(t, encoding="utf-8")
print(f"patched {len(PAIRS)} anchors in write_final_artifacts.py")

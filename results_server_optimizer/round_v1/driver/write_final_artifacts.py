"""Assemble S1P_VERDICT.json, S1P_REPORT.md and S1P_BLOCKED.md from the recorded evidence."""
from __future__ import annotations

import csv
import hashlib
import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_server_optimizer" / "round_v1"
INSTR = ROOT / "ccfa-review-reports/raven-mcs-s1prime-server-optimizer-execution-prompt.md"


def sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def jload(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


cfg = jload(OUT / "S1P_FROZEN_CONFIG.json")
av = jload(OUT / "S1P_STAGE_A_VERDICT.json")
cv = jload(OUT / "S1P_STAGE_C_H.json")
g0 = jload(OUT / "S1P_G0_COMPARE.json")
g2 = jload(OUT / "S1P_G2.json")
pf = jload(OUT / "PREFLIGHT_SECTION0.json")
grid = list(csv.DictReader((OUT / "tables" / "STAGE_A_GRID.csv").open(encoding="utf-8")))

n3 = {b: (av["N3_prime"].get(b, {}) if av else {}).get("verdict") for b in ("sensorscope", "uair", "traffic")}
h = (cv or {}).get("H", {})

verdict = {
    "instruction_sha256": sha(INSTR),
    "driver_sha256": sha(OUT / "driver" / "s1p_driver.py"),
    "frozen_config_sha256": sha(OUT / "S1P_FROZEN_CONFIG.json") if (OUT / "S1P_FROZEN_CONFIG.json").is_file() else None,
    "N3_prime_per_block": n3,
    "H_verdict_per_block": {b: (h.get(b, {}) or {}).get("verdict") for b in ("sensorscope", "uair", "traffic")},
    "stage_B": {"run": False,
                "reason": "section 5 applies Stage B only to blocks not PASS at Stage A; SensorScope, "
                          "U-Air and NSW-Traffic all PASS, so no block qualified"},
    "gate_law_note": "not applicable to this round; H is the endpoint",
    "created_utc": datetime.now(timezone.utc).isoformat(),
}
(OUT / "S1P_VERDICT.json").write_text(json.dumps(verdict, indent=2, sort_keys=True, default=str) + "\n",
                                     encoding="utf-8")

# ------------------------------------------------------------------ report
L = []
A = L.append
A("# S1' — server optimizer re-screen: report")
A("")
A(f"- Instruction: `{INSTR.relative_to(ROOT).as_posix()}`, sha256 `{sha(INSTR)}`")
A(f"- Driver: `results_server_optimizer/round_v1/driver/s1p_driver.py`, "
  f"sha256 `{sha(OUT / 'driver' / 's1p_driver.py')}`")
A(f"- Frozen config: `S1P_FROZEN_CONFIG.json`, "
  f"sha256 `{verdict['frozen_config_sha256']}`")
A("- No manuscript, `tdrive_protocol_seal_r1/`, or frozen artifact was edited; no commit, no push. "
  "No EventTrace was created. All round outputs are under `results_server_optimizer/round_v1/`. "
  "`src/` **was** changed, but only after this round closed and only under explicit user "
  "authorization: the E3 reuse guard gained a default-off `allow_reused_traffic_rerun` opt-in so "
  "that NSW-Traffic could be run (ledger Part IX item 65; byte-level backup and `RESTORE.py` under "
  "`backup_pre_guard_change/`). Every NSW-Traffic run in this report carries that exemption, "
  "recorded per run in `REUSE_GUARD_EXEMPTION.json` and `SERVER_OPT_META.json`.")
A("")
A("## 1. Section-0 premises, independently recomputed")
A("")
A("Reconstructed `theta_init = deterministic_common_ndmf(n_spatial, seed=run_seed).state_dict()` "
  "(the init path at `window_runner.py` L192 / `runner.py` L476) and compared it against every frozen "
  "checkpoint. `src/raven_mcs/models/common_ndmf.py` is content-identical to the frozen runs' commit "
  "`b01db69e` (empty git diff), so the reconstruction is exact; all 84 checkpoints also match the "
  "`checkpoint_hash` recorded in their own `runtime_manifest.json`.")
A("")
A("| section-0 claim | recomputed (seeds 30001-30003) | holds |")
A("| --- | --- | --- |")
A("| fedavg_window / raven / local_hajek move 0.26 % on SensorScope | 0.2614 / 0.2708 / 0.2614 % | yes |")
A("| ... 0.40 % on U-Air | 0.3965 / 0.4032 / 0.3965 % | yes |")
A("| ... 0.28 % on NSW-Traffic | local_hajek 0.2786 % (the E3 traffic tree has no fedavg_window/raven) | yes for the arms that exist |")
A("| mostly through the output bias `head.8.bias` | top-1 by squared movement: 41-47 % (SS), 41-47 % (UA), 51-62 % (Traffic) | yes |")
A("| spatial embeddings move 0.01 % | 0.0050-0.0088 % (2 d.p. -> 0.01 %) | yes |")
A("| SensorScope `central_all` moves `head.0.weight` by 12.2 % | 12.1524 % | yes |")
A("")
A("Additional fact section 0 does not state: `central_all` / `central_delivered` move only 2.4-3.2 % "
  "of their total norm, so the centralized references are themselves barely trained. This matters for "
  "interpreting N3' (see deviations).")
A("")
A("## 2. Gates")
A("")
A(f"- **G1** reads-after-update audit: STOP condition not fired. The one real finding is **L1204** "
  f"`after_hash = self._theta_hash()`, evaluated inside the base `_process_window` before the optimizer "
  f"step, so `WindowMetrics.theta_hash_after` and the per-client `global_model_hash` / "
  f"`model_hash_after` log `theta_sgd`; `final_metrics.json` has 32 keys and no hash key, so no "
  f"decision metric is affected.")
A(f"- **G0** identity test: **deterministic verdict {g0['G0a']['pass']}** over 4 (block, arm) pairs "
  f"(32 fields each, 0 deterministic mismatches, `checkpoints/final.pt` byte-identical). The literal "
  f"reading including `runtime_seconds` is {g0['G0b_literal']['pass']}, which no pair of runs can "
  f"satisfy because it is a wall clock; the field is named in one place in the driver and both values "
  f"are recorded in `S1P_G0_COMPARE.json`.")
A(f"- **G2** determinism: **{g2['pass']}** (same config twice, `eta_s = 1e-3` FedAdam).")
A(f"- NSW-Traffic was not gated at G0 (amendment A2: the E3 traffic tree has no `fedavg_window` and no "
  f"`raven` arm).")
A("")
A("### Frozen-artifact diagnostic (disclosure only, amendment A1)")
A("")
A("| block | arm | frozen `RMSE_mu` | re-run `RMSE_mu` | relative |")
A("| --- | --- | --- | --- | --- |")
for r in (g0 or {}).get("rows", []):
    f = (r.get("frozen_artifact_diagnostic") or {}).get("RMSE_mu")
    if f:
        A(f"| {r['block']} | {r['arm']} | {f['frozen']!r} | {f['rerun_baseline']!r} | {f['rel_diff']:.3e} |")
A("")
A("SensorScope `fedavg_window`, SensorScope `raven` and U-Air `raven` reproduce the frozen artifacts "
  "exactly (U-Air `raven` with a byte-identical checkpoint). **U-Air `fedavg_window` does not** "
  "(-3.27 %, active windows 66 -> 74, `a_r_size` systematically one larger). That arm is a Table II "
  "baseline, so it is reported as a finding in its own right; it does not affect this round, whose "
  "comparisons are all same-tree re-runs.")
A("")
A("## 3. Stage A — optimizer grid")
A("")
A("Grid `eta_s in {1e-3, 3e-3, 1e-2}`, arm `fedavg_window`, blocks x 5 screen seeds. Selection on the "
  "**validation** split only; the frozen configuration was written before any test value was read.")
A("")
A("| block | eta_s | n non-diverged | mean validation `RMSE_mu` |")
A("| --- | --- | --- | --- |")
for b in ("sensorscope", "uair", "traffic"):
    lv = (cfg["per_block"].get(b, {}) or {}).get("levels", {}) or {}
    for k in sorted(lv, key=float):
        v = lv[k]
        A(f"| {b} | {k} | {v['n_non_diverged']} | {v['mean_val_RMSE_mu']} |")
A("")
A(f"Selected: SensorScope `eta_s* = {cfg['per_block']['sensorscope'].get('eta_s_star')}`, "
  f"U-Air `eta_s* = {cfg['per_block']['uair'].get('eta_s_star')}`, "
  f"NSW-Traffic `eta_s* = {cfg['per_block']['traffic'].get('eta_s_star')}`.")
A("")
A("### N3' on test")
A("")
A("| block | verdict | eta_s* | c (frozen central_delivered) | frozen fedavg_window | new fedavg | ratio to c |")
A("| --- | --- | --- | --- | --- | --- | --- |")
for b in ("sensorscope", "uair", "traffic"):
    v = (av or {}).get("N3_prime", {}).get(b, {})
    A(f"| {b} | {v.get('verdict')} | {v.get('eta_s_star')} | {v.get('c_central_delivered')} | "
      f"{v.get('frozen_fedavg_window')} | {v.get('new_fedavg')} | {v.get('ratio_to_c')} |")
A("")
A("### What the server optimizer actually did")
A("")
A("| block | eta_s | mean overall parameter movement |")
A("| --- | --- | --- |")
for b in ("sensorscope", "uair", "traffic"):
    for eta in ("0.001", "0.003", "0.01"):
        vals = [float(r["overall_rel_movement"]) for r in grid
                if r["block"] == b and r["eta_s"] == eta and r.get("overall_rel_movement")]
        if vals:
            A(f"| {b} | {eta} | {100 * sum(vals) / len(vals):.3f} % |")
A("")
A("Against 0.26 % (SensorScope), 0.40 % (U-Air) and 0.28 % (NSW-Traffic) under the frozen SGD server "
  "step, FedAdam moves the model 2.5-22 %, i.e. 7-70x more. The round's own question - does a standard "
  "server optimizer make the federated learner learn - is therefore answered **yes**, and this also "
  "confirms section 0's diagnosis that the tiny fixed server step was the bottleneck.")
A("")
A("## 4. Stage B — rounds per window")
A("")
A("**Not run.** Section 5 applies Stage B only to blocks not PASS at Stage A, and SensorScope, "
  "U-Air and NSW-Traffic all PASS.")
A("")
A("## 5. Stage C — headroom re-measure")
A("")
if cv:
    A("| block | mean H | bootstrap 95 % CI | MDE80 (n = 5) | K_r<=3 share | verdict |")
    A("| --- | --- | --- | --- | --- | --- |")
    for b in ("sensorscope", "uair", "traffic"):
        v = h.get(b, {}) or {}
        if v.get("verdict") == "not_run":
            A(f"| {b} | - | - | - | - | not_run ({v.get('reason')}) |")
        else:
            kr = v.get("kr_clause", {})
            A(f"| {b} | {v['mean_H']:.6f} | [{v['boot_lo']:.6f}, {v['boot_hi']:.6f}] | {v['MDE80_n5']:.3e} | "
              f"{kr.get('share_kr_le3')} | {v['verdict']} |")
    A("")
    for b in ("sensorscope", "uair"):
        v = h.get(b, {}) or {}
        if v.get("verdict") == "not_run":
            continue
        A(f"- **{b}**: H >= 1 %: {v['cond_mean_ge_1pct']}; lower bound > 0.5 %: {v['cond_lcb_gt_0.5pct']}; "
          f"MDE80 < 0.5 H: {v['cond_mde_lt_half_H']}; section-6 K_r clause "
          f"({v['kr_clause']['share_kr_le3']} > {v['kr_clause']['threshold']}): "
          f"excluded from GO = {v['kr_clause']['excluded_from_GO']}.")
    A("")
    A("**The verdict is NO-GO-H on all three blocks, and on NSW-Traffic it is a measured result rather "
      "than a structural one.** Section 6 forbids upgrading SensorScope or U-Air to GO when more than "
      "25 % of active windows have `K_r <= 3`, and under the new configuration both are far above that "
      "(0.753 and 0.662). NSW-Traffic is the one block the clause does not exclude (its share is "
      "0.111), so it was run: H there is negative and its interval contains zero. On U-Air the oracle "
      "arm is *significantly worse* than plain FedAvg (the whole interval is below zero), which is the "
      "opposite of headroom. The plain reading is therefore that the oracle-margin reference supplies "
      "no headroom on any of the three blocks once the learner actually trains - which is the point "
      "section 0 raised when it observed that the earlier H was measured on an untrained model.")
A("")
A("## 6. Deviations, blocks and corrections")
A("")
A("1. **NSW-Traffic was refused at first, then run under an authorized exemption.** The E3 reuse "
  "guard (`src/raven_mcs/e3/protocol_closure/reuse_guard.py`) refuses `traffic` + `complete_aligned` "
  "+ seed in 30001..30020 + `{fedavg_window, raven}` with `DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED`, so "
  "the first pass recorded all 15 traffic cells as BLOCKED and stopped that block rather than editing "
  "`src/` (`S1P_BLOCKED.md`, which is kept as the historical record). The user then authorized a "
  "narrow, reversible relaxation and asked for the block; it was run and all three blocks now PASS "
  "N3'. Two provenance points, correcting an earlier statement in this session: the guard module is "
  "**not** new - its functions were already refusing correctly in the 2026-08-10 canary evidence - and "
  "what the 2026-10-07 17:00:29/17:00:32 writes mark is the **wiring into `run_e3_real`**, which is "
  "why the 15:25-16:27 traffic round could train sealed-method cells (ledger Part IX items 64/66).")
A("2. **G0's literal wording cannot be met.** `runtime_seconds` is a wall clock; the deterministic "
  "reading is used, the excluded field and both of its values are reported in `S1P_G0_COMPARE.json`.")
A("3. **The runner emits no validation metric.** `run_e3_real` calls `_predict(..., split=\"test\")` "
  "only, and `window_metrics.json` rows carry just `{window_id, active, active_clients, a_r_size, "
  "alpha, beta_hat}`. Validation `RMSE_mu` is therefore computed by this driver as read-only "
  "post-processing from the saved checkpoint, with `mu_g` from a `TargetBuilder(split=\"validation\")` "
  "build on the same `target_group_main` mapping. This choice and its exact formula were pre-registered "
  "in the driver source *before* the grid ran; the test-`mu`-weighted variant is not used for "
  "selection.")
A("4. **The test seal is procedural, not physical.** The runner writes test metrics into each run "
  "directory as part of its own output contract, which cannot be changed without editing `src/`. No "
  "test-derived value was written to any file, and no selection code path read one, before "
  "`S1P_FROZEN_CONFIG.json` existed.")
A("5. **One cell was damaged by my own tooling and repaired.** I terminated the first Stage A attempt "
  "to restructure the traffic handling; `A_eta0.003/sensorscope/fedavg_window/seed30005` was left "
  "without `final_metrics.json` or `checkpoints/final.pt`. It was detected (1 cell with "
  "`ckpt_ok=False`), its directory verified as incomplete and under the round tree, removed, and "
  "re-run; the selection was then redone. The first frozen configuration "
  "(`fe84a4c6fb1124ed...`) is superseded by `57b4bcec0cb030cf...`; the selection outcome did not "
  "change. No test value was used in either pass.")
A("6. **An empty-directory artefact initially mis-classified the traffic cells.** `run_one` creates the "
  "run directory before `run_e3_real` reaches the guard, so 15 empty directories were left behind and "
  "the following pass reported them as `diverged` rather than `BLOCKED`. They were verified empty and "
  "removed, and the pass was repeated so the refusal is recorded as `BLOCKED` with the guard's own "
  "error text.")
A("7. **N3' PASS on U-Air is not a like-for-like optimizer comparison.** The reference "
  "`central_delivered` moves only ~3.2 % of its parameter norm (section 1), so it is itself barely "
  "trained. The federated arm now moves 7.3 %, beats that reference, and would likely also beat a "
  "centralized model trained with the same optimizer. A fair centralized-vs-federated statement needs "
  "the centralized arm retrained under FedAdam, which is outside this round. The N3' rule as written "
  "was applied unchanged.")
A("8. **GO-H was evaluable only on NSW-Traffic, and that measurement is NO-GO-H.** SensorScope and "
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
  "only in the older 21-key **E2** schema. So section 4's \"final training Hajek loss\" is "
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
  "traffic selection uses 5/5 seeds.")
A("")
A("## 7. Deviations from the instruction's own assumptions, summarised")
A("")
A("| instruction assumes | actual | handling |")
A("| --- | --- | --- |")
A("| base class `WindowRunner` | the class is `FullWindowRunner` | corrected in the driver |")
A("| `eta = 0.01` recorded in configs | dataclass default only; not in any `config_snapshot.json` | verified in code, asserted at runtime |")
A("| G0 can match the frozen files bit-exact | impossible for artifact-vintage reasons | amendment A1: identity test against a re-run |")
A("| traffic has `fedavg_window` / `raven` | E3 traffic tree has neither | A2 for G0; traffic re-run under the item-65 exemption |")
A("| each run records validation `RMSE_mu` | no validation metric is emitted | computed read-only, pre-registered |")
A("| `MDE80` at n = 15 | screen is n = 5 | amendment A3; traffic shows 5/5 usable screen seeds |")
A("| each run records a training loss | the E3 schema has no loss field at all | recorded as unobtainable (deviation 11) |")
A("| the guard is a 2026-10-07 addition | it existed by 2026-08-10; 2026-10-07 is the wiring | corrected (deviation 1, ledger item 66) |")
A("| an exempted run records the exemption in its ledger | `source_identity` is filtered to five keys | driver writes a per-run record (deviation 10) |")
A("")
A("## 8. Files")
A("")
for f in sorted((OUT).rglob("*")):
    if f.is_file() and "runs/" not in f.as_posix():
        A(f"- `{f.relative_to(ROOT).as_posix()}`")
A("")
(OUT / "S1P_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")

blocked = f"""# S1' — BLOCKED: NSW-Traffic Stage A

Per section 1 of the instruction ("Any condition below that cannot be met without editing `src/` is a
STOP"), the NSW-Traffic block of Stage A is **BLOCKED**. The SensorScope and U-Air blocks ran to
completion; this file records the refusal rather than silently dropping the block.

## The condition

`run_e3_real` calls `assert_schedulable_e3_run` before doing any work. For

- `dataset = "traffic"`, `scenario = "complete_aligned"`, any seed in `30001..30020`
  (`FORMAL_SEEDS`), and
- `method` in `E2_TRAFFIC_REUSED_METHODS = [fedavg_window, fedasync_window,
  flamf_timealign_adapted, twostage_hajek, raven]`

it raises `DuplicateReusedTrafficRunBlocked` with code `DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED`.

Stage A trains `fedavg_window` on all three blocks, so **all 15 traffic cells** are refused. The exact
error text is preserved per cell in `tables/STAGE_A_VALIDATION.csv`.

## Why it was not worked around

The instruction forbids editing `src/`, and the guard is a deliberate protocol control
(`REUSE_ONLY_NO_RERUN from sealed E2 Traffic Complete-aligned`). Monkeypatching the guard out would
silently disable a control the project put in place on purpose, so the refusal is reported instead.

## Provenance of the conflict

`src/raven_mcs/e3/protocol_closure/` is **untracked** in git and `reuse_guard.py` has mtime
**2026-10-07 17:00:29**. The earlier new-block traffic round ran at 15:19-16:27 on the same day and
produced fresh `traffic/complete_aligned/fedavg_window` runs, which the guard would refuse today. The
instruction was therefore written against a tree that did not yet contain this guard.

Note also that `E2_TRAFFIC_REUSED_METHODS` contains `raven` as well as `fedavg_window`, so Stage C's
descriptive `raven` arm on traffic would also be refused (`raven_simoracle` is not in the list and
would be allowed).

## Consequences

1. N3' for NSW-Traffic is reported as `BLOCKED`, not as `FAIL`; no traffic cell was trained.
2. Stage B is not run (section 5 applies it only to blocks not PASS, and both eligible blocks PASS).
3. Stage C does not run for traffic.
4. **GO-H is unreachable in this round**: section 6 forbids upgrading SensorScope or U-Air to GO when
   more than 25 % of active windows have `K_r <= 3`, and both are far above that threshold
   (78.6 % and 90.2 %). NSW-Traffic was the only block to which the clause would not apply.

## What would unblock it

Either the guard is amended by someone authorized to change `src/` (for example to exempt runs written
into a new results tree), or the instruction is revised to drop the NSW-Traffic block. Both are user
decisions.
"""
# S1P_BLOCKED.md is owned separately (write_blocked_record.py) so that the pre-authorization
# block text is not restored on every regeneration.
# # S1P_BLOCKED.md is owned separately (write_blocked_record.py) so that the pre-authorization
# block text is not restored on every regeneration.
# (OUT / "S1P_BLOCKED.md").write_text(blocked, encoding="utf-8")
print("wrote S1P_VERDICT.json, S1P_REPORT.md, S1P_BLOCKED.md")
print("N3':", n3)
print("H :", verdict["H_verdict_per_block"])

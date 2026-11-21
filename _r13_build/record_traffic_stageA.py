"""Record the traffic Stage A completion, the traffic identity test, and three self-corrections;
fix the guard docstring claim that the ledger can carry the exemption."""
from __future__ import annotations

import hashlib
import json
import pathlib
import py_compile
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
GUARD = ROOT / "src/raven_mcs/e3/protocol_closure/reuse_guard.py"
LEDGER = ROOT / "ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md"
BACKUP = ROOT / "results_server_optimizer/round_v1/backup_pre_guard_change"


def sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


pre_guard_sha = sha(GUARD)

# ---------------------------------------------------------------- guard docstring correction
g = GUARD.read_text(encoding="utf-8")
OLD = "so every exempted run records the exemption in its run ledger."
NEW = ("The run ledger carries only `git_commit`, `source_manifest_hash`, `method_source_hash`, "
       "`runner_source_hash` and `dataset_hash` from `source_identity` (runner.py L307-L311), so the "
       "exemption itself must be recorded by the caller - in this workspace the S1' driver writes "
       "`REUSE_GUARD_EXEMPTION.json` and a `reuse_guard_exemption` field in `SERVER_OPT_META.json` "
       "into every exempted run directory.")
assert g.count(OLD) == 1, "docstring anchor"
g = g.replace(OLD, NEW)
GUARD.write_text(g, encoding="utf-8")
py_compile.compile(str(GUARD), doraise=True, cfile=None)
post_guard_sha = sha(GUARD)
print(f"guard docstring corrected: {pre_guard_sha[:16]} -> {post_guard_sha[:16]}")

# behaviour + canary must still hold after the docstring edit
ver = subprocess.run([sys.executable, "-c", r'''
import sys, warnings
sys.path.insert(0, r"C:\Cursor\raven.mcs\src")
from raven_mcs.e3.protocol_closure.reuse_guard import assert_schedulable_e3_run
from raven_mcs.e3.canary.traffic_reuse_guard import assert_canary_schedulable, build_traffic_reuse_guard_evidence
kw = dict(dataset="traffic", scenario="complete_aligned", seed=30001, method="fedavg_window")
out = {}
try: assert_schedulable_e3_run(**kw); out["default"] = "NO_RAISE"
except Exception as e: out["default"] = type(e).__name__
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    try: assert_schedulable_e3_run(**kw, allow_reused_traffic_rerun=True); out["optin"] = "NO_RAISE"
    except Exception as e: out["optin"] = type(e).__name__
    out["warned"] = any(issubclass(x.category, RuntimeWarning) for x in w)
try: assert_canary_schedulable(dataset="traffic", method="fedavg_window", seed=31001); out["canary"] = "NO_RAISE"
except Exception as e: out["canary"] = type(e).__name__
out["canary_evidence"] = build_traffic_reuse_guard_evidence()["status"]
print(__import__("json").dumps(out))
'''], capture_output=True, text=True, timeout=120)
res = json.loads(ver.stdout.strip().splitlines()[-1])
print("verification:", json.dumps(res))
assert res == {"default": "DuplicateReusedTrafficRunBlocked", "optin": "NO_RAISE", "warned": True,
               "canary": "CanaryTrafficSealedMethodBlocked", "canary_evidence": "PASS"}, res

# update the backup manifest so it reflects the current post-change hashes
man = json.loads((BACKUP / "BACKUP_MANIFEST.json").read_text(encoding="utf-8"))
man["post_change_sha256"]["reuse_guard.py"] = post_guard_sha
man["docstring_correction_utc"] = datetime.now(timezone.utc).isoformat()
man["docstring_correction_note"] = ("the guard docstring claimed the ledger records the exemption; "
                                    "runner.py writes only five named fields, so the claim was "
                                    "corrected and the driver records it instead")
(BACKUP / "BACKUP_MANIFEST.json").write_text(json.dumps(man, indent=2, sort_keys=True), encoding="utf-8")
print("backup manifest updated")

# ---------------------------------------------------------------- ledger items 69-73
t = LEDGER.read_text(encoding="utf-8")
assert "item 69" not in t
APPEND = """

## IX.5 Third-pass additions (items 69-73), 2026-10-08

| # | correction | evidence |
|:--|:---|:---|
| 69 | **The NSW-Traffic Stage A was completed under the recorded exemption, and all three blocks PASS N3'.** After the user authorized the narrow guard exemption and asked for the traffic block, its 15 grid cells ran (`fedavg_window`, `eta_s in {1e-3, 3e-3, 1e-2}` x seeds 30001-30005; all 15 complete). Validation means: `eta_s=1e-3` 0.864388, **`eta_s=3e-3` 0.819805 (selected)**, `eta_s=1e-2` 0.907197, each over 5/5 usable screen seeds. N3' on test against the frozen `central_delivered` on the same seeds: `c = 0.9737694569747332`, new `fedavg = 0.8350944692092265`, `ratio_to_c = 0.8575895076886716` -> **PASS** (SensorScope 0.986505 PASS, U-Air 0.832921 PASS). For NSW-Traffic `frozen_fedavg_window` is `None` because the E3 traffic tree has no such arm, so N3's PARTIAL branch is not evaluable there and only PASS/FAIL apply; this is recorded rather than papered over. Every traffic run carries `REUSE_GUARD_EXEMPTION.json` plus a `reuse_guard_exemption` field in `SERVER_OPT_META.json` (15/15), so each identifies itself as exempted. | `results_server_optimizer/round_v1/{S1P_FROZEN_CONFIG.json,S1P_STAGE_A_VERDICT.json,tables/STAGE_A_GRID.csv}`; `runs/A_eta*/traffic/fedavg_window/seed*/REUSE_GUARD_EXEMPTION.json` |
| 70 | **Traffic passed its own identity test, closing the gap amendment A2 left.** A2 had excluded NSW-Traffic from G0 because the E3 traffic tree lacks `fedavg_window` and `raven`, so the override had never been checked there. Running `traffic/fedavg_window/seed30001` with the override disabled and again with the override active but the server optimizer set to plain SGD gives **32/32 deterministic fields equal**, only `runtime_seconds` differing, and a **byte-identical final checkpoint** (`15de443736271d97`); the `K_r <= 3` share is identical (0.111111). A forced repeat of one traffic cell reproduced `RMSE_mu` (0.8628721594092053), the checkpoint hash (`7180a33de2eea17c`) and the validation `RMSE_mu` (0.8562045367964333) exactly. The identity property and determinism therefore now hold on all three blocks. | `results_server_optimizer/round_v1/S1P_TRAFFIC_G0_DIAGNOSTIC.json`; driver `traffic_identity_check.py` |
| 71 | **Correction to item 65: the ledger cannot carry the exemption, so item 65's wording was wrong.** `run_e3_real` writes only `git_commit`, `source_manifest_hash`, `method_source_hash`, `runner_source_hash` and `dataset_hash` out of `source_identity` (`runner.py` L307-L311), so a custom key such as `allow_reused_traffic_rerun` never reaches the ledger. Item 65 (and the guard's own docstring) claimed that every exempted run records the exemption in its run ledger; that was false as written. Fixed in two places: the driver now writes `REUSE_GUARD_EXEMPTION.json` and a `reuse_guard_exemption` field in `SERVER_OPT_META.json` into every exempted run directory (15/15 traffic cells), and the guard docstring now states where the record actually lives. The guard file hash after this correction is recorded in `backup_pre_guard_change/BACKUP_MANIFEST.json`. | `src/raven_mcs/e3/real_runner/runner.py` L307-L311; `src/raven_mcs/e3/protocol_closure/reuse_guard.py`; `results_server_optimizer/round_v1/backup_pre_guard_change/BACKUP_MANIFEST.json` |
| 72 | **Two defects in this session's own driver, both found and fixed; neither changed a reported number.** (a) `run_one` created the run directory *before* calling `run_e3_real`, so a guard refusal left an empty directory that a later pass treated as a completed run and skipped - this mis-classified traffic cells as `diverged` twice before it was caught. Fixed with a completeness gate (a cell counts as done only when both `final_metrics.json` and `checkpoints/final.pt` exist) plus a `RUN_FAILED.json` marker on failure. (b) Level selection could average over fewer than the five screen seeds: on the first traffic attempt `eta_s=1e-3` was selected from a **single** surviving seed and the following test pass then crashed on a missing `final_metrics.json`. Fixed by requiring all five screen seeds to be usable for a level to be selectable (otherwise the block is reported `NO_ELIGIBLE_LEVEL`) and by tolerating a missing cell in the test pass. Both changes only tighten validity or prevent a false skip; the final traffic selection uses 5/5 seeds, and the frozen configuration's selection was identical across every pass that produced it. | driver `s1p_driver.py` (`run_complete`, `all_screen_seeds_usable`); `runs/*/RUN_FAILED.json` |
| 73 | **The E3 metric schema has no loss field at all, and the E2 schema is a different, older set.** `artifacts/e3_formal_runs_r1/runs/<block>/<arm>/final_metrics.json` carries the **same 32 keys** for `sensorscope/raven`, `uair/raven` and `traffic/raven_simoracle` (`missing_vs_SS = []`, `extra_vs_SS = []`). `artifacts/e2_traffic_formal_runs_r1/runs/<seed>/complete_aligned/fedavg_window/final_metrics.json` carries a **different 21-key** schema whose extras include `Gap_mis`, `target_risk_objective`, `empirical_risk_objective`, `active_window_count`, `completed_windows`, `P2_solver_failure_count`, `stale_update_count`, `hard_arrival_count` and `group_rmse` - none of which exists in the E3 schema. Two consequences. (i) The S1' instruction's "final training Hajek loss" is **not obtainable on any block**, not merely on traffic: this is the fourth place that instruction assumes an artifact that does not exist (after G0's traffic arms, the validation metric, and the frozen-uniformity of G0). (ii) An earlier reading in this session which described several E3 fields as "`None`" was reading **absent** keys through `dict.get` and is withdrawn; the traffic `final_metrics.json` contains no non-finite value. | key-set comparison over the four `final_metrics.json` files; `results_server_optimizer/round_v1/tables/STAGE_A_VALIDATION.csv` (`hajek_target_risk_objective` empty for every cell) |
"""
LEDGER.write_text(t.rstrip("\n") + APPEND, encoding="utf-8")
print("appended ledger items 69-73")
print("ledger lines:", len(LEDGER.read_text(encoding="utf-8").splitlines()))

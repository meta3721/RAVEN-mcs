"""One-shot, reversible unblocking of the E3 traffic reuse guard (user-authorized 2026-10-08).

Form chosen by the user: an explicit, default-False opt-in parameter on
`assert_schedulable_e3_run`, read by `run_e3_real` from `source_identity`, so that
(a) no existing caller changes behaviour, and
(b) every exempted run carries the opt-in inside its own ledger `source_identity`.

Also appends ledger Part IX (items 63-65) and annotates the S1' round documents.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import py_compile
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
GUARD = ROOT / "src/raven_mcs/e3/protocol_closure/reuse_guard.py"
RUNNER = ROOT / "src/raven_mcs/e3/real_runner/runner.py"
BACKUP = ROOT / "results_server_optimizer/round_v1/backup_pre_guard_change"
OUT = ROOT / "results_server_optimizer/round_v1"
LEDGER = ROOT / "ccfa-review-reports/raven-mcs-metric-definition-diagnosis.md"
AUD = json.loads((ROOT / "_r13_build/SRC_UNTRACKED_AUDIT.json").read_text(encoding="utf-8"))


def sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def check_compile(p: pathlib.Path) -> None:
    py_compile.compile(str(p), doraise=True, cfile=None)


# ---------------------------------------------------------------- 0. safety: backup must match
man = json.loads((BACKUP / "BACKUP_MANIFEST.json").read_text(encoding="utf-8"))
by_src = {c["source"]: c for c in man["copied_files"]}
for rel, live in (("src/raven_mcs/e3/protocol_closure/reuse_guard.py", GUARD),
                  ("src/raven_mcs/e3/real_runner/runner.py", RUNNER)):
    assert rel in by_src, f"{rel} missing from backup manifest"
    assert sha(live) == by_src[rel]["sha256"], f"{rel} changed since the backup; aborting"
print("pre-flight: backup matches the live files")

pre = {"reuse_guard.py": sha(GUARD), "runner.py": sha(RUNNER)}

# ---------------------------------------------------------------- 1. guard edit
g = GUARD.read_text(encoding="utf-8")

OLD_DOC = '"""Refuse scheduling of the sealed E2 Traffic Complete-aligned 100-run block."""'
NEW_DOC = '''"""Refuse scheduling of the sealed E2 Traffic Complete-aligned 100-run block.

Exemption (2026-10-08): `assert_schedulable_e3_run` accepts an explicit, default-False
`allow_reused_traffic_rerun` opt-in.  The default behaviour is unchanged for every existing caller;
only a caller that passes the flag can schedule a reused-block cell, and `run_e3_real` reads that flag
from its own `source_identity`, so every exempted run records the exemption in its run ledger.  The
exemption is announced with a `RuntimeWarning` so it cannot be exercised silently.  Authorized
explicitly by the user; recorded in the diagnosis ledger Part IX item 65.
"""'''
assert g.count(OLD_DOC) == 1, "guard docstring anchor"
g = g.replace(OLD_DOC, NEW_DOC)

OLD_ASSERT = '''def assert_schedulable_e3_run(
    *,
    dataset: str,
    scenario: str,
    seed: int,
    method: str,
) -> None:
    if is_reused_e2_traffic_block(
        dataset=dataset, scenario=scenario, seed=seed, method=method
    ):'''
NEW_ASSERT = '''def assert_schedulable_e3_run(
    *,
    dataset: str,
    scenario: str,
    seed: int,
    method: str,
    allow_reused_traffic_rerun: bool = False,
) -> None:
    if allow_reused_traffic_rerun and is_reused_e2_traffic_block(
        dataset=dataset, scenario=scenario, seed=seed, method=method
    ):
        import warnings

        warnings.warn(
            "REUSED_TRAFFIC_RERUN_ALLOWED: scheduling "
            f"dataset={dataset} scenario={scenario} seed={seed} method={method}, which is "
            "REUSE_ONLY_NO_RERUN from the sealed E2 Traffic Complete-aligned block, because the "
            "caller passed allow_reused_traffic_rerun=True. The artifacts this run writes are NOT "
            "the sealed objects.",
            RuntimeWarning,
            stacklevel=2,
        )
        return
    if is_reused_e2_traffic_block(
        dataset=dataset, scenario=scenario, seed=seed, method=method
    ):'''
assert g.count(OLD_ASSERT) == 1, "guard assert anchor"
g = g.replace(OLD_ASSERT, NEW_ASSERT)
GUARD.write_text(g, encoding="utf-8")
check_compile(GUARD)
print("edited reuse_guard.py")

# ---------------------------------------------------------------- 2. runner edit
r = RUNNER.read_text(encoding="utf-8")
OLD_CALL = '''    assert_schedulable_e3_run(
        dataset=dataset_name, scenario=scenario, seed=int(seed), method=method
    )'''
NEW_CALL = '''    assert_schedulable_e3_run(
        dataset=dataset_name,
        scenario=scenario,
        seed=int(seed),
        method=method,
        allow_reused_traffic_rerun=bool(
            (source_identity or {}).get("allow_reused_traffic_rerun", False)
        ),
    )'''
assert r.count(OLD_CALL) == 1, "runner call anchor"
r = r.replace(OLD_CALL, NEW_CALL)
RUNNER.write_text(r, encoding="utf-8")
check_compile(RUNNER)
print("edited real_runner/runner.py")

post = {"reuse_guard.py": sha(GUARD), "runner.py": sha(RUNNER)}

# ---------------------------------------------------------------- 3. behaviour verification
ver = subprocess.run(
    [sys.executable, "-c", r'''
import sys, warnings
sys.path.insert(0, r"C:\Cursor\raven.mcs\src")
from raven_mcs.e3.protocol_closure.reuse_guard import assert_schedulable_e3_run, is_reused_e2_traffic_block
kw = dict(dataset="traffic", scenario="complete_aligned", seed=30001, method="fedavg_window")
out = {}
try:
    assert_schedulable_e3_run(**kw); out["default"] = "NO_RAISE"
except Exception as e:
    out["default"] = type(e).__name__
try:
    assert_schedulable_e3_run(**kw, allow_reused_traffic_rerun=False); out["explicit_false"] = "NO_RAISE"
except Exception as e:
    out["explicit_false"] = type(e).__name__
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    try:
        assert_schedulable_e3_run(**kw, allow_reused_traffic_rerun=True); out["explicit_true"] = "NO_RAISE"
    except Exception as e:
        out["explicit_true"] = type(e).__name__
    out["warning_emitted"] = any(issubclass(x.category, RuntimeWarning) and "REUSED_TRAFFIC_RERUN_ALLOWED" in str(x.message) for x in w)
out["predicate_still_true"] = is_reused_e2_traffic_block(**kw)
out["non_reused_method_allowed"] = "NO_RAISE"
try:
    assert_schedulable_e3_run(dataset="traffic", scenario="complete_aligned", seed=30001, method="raven_simoracle")
except Exception as e:
    out["non_reused_method_allowed"] = type(e).__name__
try:
    assert_schedulable_e3_run(dataset="sensorscope", scenario="complete_aligned", seed=30001, method="fedavg_window")
    out["sensorscope_allowed"] = "NO_RAISE"
except Exception as e:
    out["sensorscope_allowed"] = type(e).__name__
print(__import__("json").dumps(out))
'''],
    capture_output=True, text=True, timeout=120,
)
verification = json.loads(ver.stdout.strip().splitlines()[-1]) if ver.stdout.strip() else {"error": ver.stderr[-500:]}
print("verification:", json.dumps(verification))
assert verification.get("default") == "DuplicateReusedTrafficRunBlocked", "default behaviour changed!"
assert verification.get("explicit_false") == "DuplicateReusedTrafficRunBlocked", "explicit False must refuse"
assert verification.get("explicit_true") == "NO_RAISE", "explicit True must allow"
assert verification.get("warning_emitted") is True, "exemption must announce itself"
assert verification.get("predicate_still_true") is True, "predicate semantics must not change"
assert verification.get("non_reused_method_allowed") == "NO_RAISE"
assert verification.get("sensorscope_allowed") == "NO_RAISE"

# ---------------------------------------------------------------- 4. restore script
restore = BACKUP / "RESTORE.py"
restore.write_text(f'''"""Restore src/raven_mcs/e3/{{protocol_closure/reuse_guard.py,real_runner/runner.py}} to their
pre-2026-10-08 state from this backup. Run with the project venv python."""
import hashlib, pathlib, shutil, sys

ROOT = pathlib.Path(r"{ROOT}")
B = pathlib.Path(__file__).resolve().parent
EXPECT = {{"src/raven_mcs/e3/protocol_closure/reuse_guard.py": "{pre['reuse_guard.py']}",
         "src/raven_mcs/e3/real_runner/runner.py": "{pre['runner.py']}"}}
for rel, want in EXPECT.items():
    src = B / "src" / rel
    dst = ROOT / rel
    shutil.copy2(src, dst)
    got = hashlib.sha256(dst.read_bytes()).hexdigest()
    print(("RESTORED " if got == want else "MISMATCH ") + rel + " " + got[:16])
    if got != want:
        sys.exit(1)
print("restore complete")
''', encoding="utf-8")
check_compile(restore)

# ---------------------------------------------------------------- 5. update backup manifest
man["guard_exemption_applied_utc"] = datetime.now(timezone.utc).isoformat()
man["post_change_sha256"] = post
man["pre_change_sha256"] = pre
man["restore_script"] = str(restore.relative_to(ROOT)).replace("\\", "/")
man["form"] = ("explicit default-False allow_reused_traffic_rerun on assert_schedulable_e3_run, read by "
               "run_e3_real from source_identity; no-op for every existing caller")
(BACKUP / "BACKUP_MANIFEST.json").write_text(json.dumps(man, indent=2, sort_keys=True), encoding="utf-8")
print("updated backup manifest")

# ---------------------------------------------------------------- 6. ledger Part IX
led = LEDGER.read_text(encoding="utf-8")
assert "Part IX" not in led, "Part IX already present"
n_by_date = ", ".join(f"`{d}` {n}" for d, n in AUD["files_by_date"].items())
part = f"""

---

# Part IX — Record corrections, 2026-10-08 (workspace hygiene, the traffic lineage, and the reuse-guard exemption)

Owner: `ccf-rebuttal-writer`. This continues the correction series of VI.5 (items 45-52) and VIII.1
(items 53-62) and is **not** a review ledger. Every item was measured on 2026-10-08 in this session.

## IX.1 Corrections (items 63-65)

| # | correction | evidence |
|:--|:---|:---|
| 63 | **85 of the entries under `src/` are untracked, and the cause is "never staged", not an ignore rule; 82 % of the affected files predate the last commit.** `git ls-files src` gives 116 tracked files; `git status --porcelain -- src` gives 85 untracked entries, which expand to **{AUD['untracked_files_total']} files / {AUD['untracked_bytes_total'] / 1e6:.1f} MB**. `git check-ignore -v` returns nothing for `reuse_guard.py`, `real_runner/runner.py` or `protocol_closure/__init__.py`; `.gitignore` has no `src`/`e3`/`protocol` rule; `core.excludesfile` is unset — so no ignore rule explains it. The untracked set is **{AUD['files_by_month'].get('2026-08', 0)} files from 2026-08, {AUD['files_by_month'].get('2026-09', 0)} from 2026-09 and {AUD['files_by_month'].get('2026-10', 0)} from 2026-10**, i.e. most of it predates HEAD (`{AUD['head_commit'][:7]}`, {AUD['head_commit_date']}, the last commit in the repository). It is therefore not "work after the last commit" but whole packages that were never added. The largest untracked packages are `src/raven_mcs/e3/` (125 files, 2026-08-28 17:01:55 -> 2026-10-07 17:00:59), `src/raven_mcs/e4/` (30), `src/raven_mcs/paper_data_r1/` (16), `src/raven_mcs/tdrive_protocol_seal_r1/` (15), and six 9-11-file packages all stamped 2026-08-28 17:01:55-56. Files by date: {n_by_date}. **Attribution limit, stated so it is not over-read:** mtimes record *when*, never *who*. The workspace therefore **cannot** establish that several agents caused the untracking. What it does establish is that the tree was worked on across at least eleven distinct days with commits stopped on 2026-09-11, which is consistent with the project record naming more than one agent (handoff §10-§16 are "another Agent"), but that is corroboration, not proof. | `_r13_build/SRC_UNTRACKED_AUDIT.json` (script `_r13_build/audit_src_untracked.py`); `git ls-files src`; `git status --porcelain -- src`; `git check-ignore -v`; `git log -1 --format=%ci` |
| 64 | **The three NSW-Traffic run trees are three different experiments, and the reuse guard protects the oldest of them, not the newest.** (i) `artifacts/e2_traffic_formal_runs_r1` — 2026-08-07 23:32 to 08-09 07:51, 20 seeds x 6 scenarios x 5 arms (`fedavg_window`, `fedasync_window`, `flamf_timealign_adapted`, `twostage_hajek`, `raven`) = 600 runs; its `complete_aligned` subset (20 x 5 = **100 runs**) is exactly the "sealed E2 Traffic Complete-aligned 100-run block" the guard names. (ii) `artifacts/e3_formal_runs_r1/runs/traffic` — 2026-08-11 15:47 to 17:37, 6 arms x 20 seeds = 120 runs; E3 **reused** E2's traces (`E3_TRAFFIC_EVENTTRACE_REUSE_AUDIT.csv` marks every row `COPIED` from `e2_traffic_formal_runs_r1/eventtraces/<seed>/complete_aligned/training_eventtrace`) and trained only the arms outside the reuse list, so `fedavg_window` and `raven` have **no E3 counterpart** — which is why the S1' instruction's three traffic arms do not all exist and why no frozen traffic `fedavg_window` exists. (iii) `results_new_block_traffic/round_v1` — 2026-10-07 15:25 to 16:27:41, S0 (read-only family screen) plus an S1 ladder that **trained** `fedavg_window` at `local_steps` 5/10/20 x seeds 30001-30003 (9 runs) and **read** the 2-step rung from the sealed E2 grid (`local_steps_source = sealed_e2_complete_aligned_read_only`). Guard provenance: `reuse_guard.py` mtime **2026-10-07 17:00:29** and `real_runner/runner.py` mtime **2026-10-07 17:00:32**, i.e. both postdate the 16:27:41 end of round (iii). Round (iii)'s driver `scripts/new_block_traffic_stages.py` contains no guard bypass (grep for `guard`/`assert_schedulable`/`DuplicateReused`: 0 hits) and its nine `traffic + complete_aligned + seed 30001-30003 + fedavg_window` runs succeeded, which are precisely the cells the guard refuses, so the guard was not enforced on that path at that time. **Limit:** round (iii)'s ledger records `runner_source_hash: null` (it passed no `source_identity`), and both files are untracked, so the runner version in force during round (iii) cannot be read directly. | `artifacts/e2_traffic_formal_runs_r1/runs/30001/*/`; `artifacts/e3_formal_runs_r1/E3_TRAFFIC_EVENTTRACE_REUSE_AUDIT.csv`; `results_new_block_traffic/round_v1/S1_LADDER.csv`; file mtimes; `scripts/new_block_traffic_stages.py` |
| 65 | **The E3 traffic reuse guard was relaxed on 2026-10-08 by explicit user authorization, in one narrow, reversible form.** `assert_schedulable_e3_run` gains a default-`False` `allow_reused_traffic_rerun` parameter; `run_e3_real` reads it from its own `source_identity`, so an exempted run records the exemption inside its own ledger, and the guard emits a `RuntimeWarning` when the exemption is exercised so it cannot be silent. `is_reused_e2_traffic_block` is unchanged and still returns `True` for those cells, so any caller asking "is this a reused block?" gets the same answer as before. Verified after the edit: default -> `DuplicateReusedTrafficRunBlocked`; `allow_reused_traffic_rerun=False` -> `DuplicateReusedTrafficRunBlocked`; `allow_reused_traffic_rerun=True` -> no raise with the warning emitted; `raven_simoracle` and SensorScope cells unaffected. `reuse_guard.py` {pre['reuse_guard.py'][:16]} -> {post['reuse_guard.py'][:16]}; `runner.py` {pre['runner.py'][:16]} -> {post['runner.py'][:16]}. Every file a change would touch was copied byte-for-byte to `results_server_optimizer/round_v1/backup_pre_guard_change/` **before** the edit, together with sha256 manifests of 9 175 sealed-evidence files (hashes only) and a runnable `RESTORE.py`. **Caveats that must travel with any later traffic run:** the guard exists because E3 traffic reused E2 rather than retraining, and the runner has drifted since the E3 runs (their ledger records `runner_source_hash = 2f5728de...`; the worktree file now hashes to {post['runner.py'][:16]}), so a new traffic run is **not** the same object as the frozen E3 traffic evidence and must never be compared to it as if it were. The S1' round itself ran entirely under the **unmodified** guard: no cell of that round used the exemption. | `src/raven_mcs/e3/protocol_closure/reuse_guard.py`; `src/raven_mcs/e3/real_runner/runner.py`; `results_server_optimizer/round_v1/backup_pre_guard_change/BACKUP_MANIFEST.json` |

## IX.2 Ledger rules honoured

* Items 63-65 are corrections and provenance records, not scorecard entries.
* Item 63 states an attribution limit rather than converting a timestamp pattern into a claim about
  authorship.
* Item 64 corrects a conflation in this session's own reporting (the 16:27 round is not the block the
  guard protects).
* Item 65 records an authorized exception together with its reversal path and the caveat that the
  newly permitted runs are not the sealed objects.

## IX.3 Standing state after this part

`src/` now differs from its pre-2026-10-08 state in exactly two files, both recorded above with hashes
and a restore script. The S1' round (`results_server_optimizer/round_v1/`) is unchanged and was
produced under the unmodified guard.
"""
LEDGER.write_text(led.rstrip("\n") + part, encoding="utf-8")
print("appended ledger Part IX (items 63-65)")

# ---------------------------------------------------------------- 7. annotate the S1' documents
note = f"""
> **Post-round note (2026-10-08).** The NSW-Traffic block recorded below was blocked by the E3
> protocol-closure reuse guard. After this round closed, the user authorized a narrow, reversible
> relaxation of that guard (an explicit, default-`False` `allow_reused_traffic_rerun` opt-in on
> `assert_schedulable_e3_run`, read by `run_e3_real` from `source_identity`). **This round itself ran
> entirely under the unmodified guard and no cell of it used the exemption.** The change, its hashes,
> its backup (`results_server_optimizer/round_v1/backup_pre_guard_change/`, including `RESTORE.py`)
> and the caveat that newly permitted traffic runs are not the sealed E3 objects are recorded in the
> diagnosis ledger Part IX item 65.
"""
for name in ("S1P_BLOCKED.md",):
    p = OUT / name
    t = p.read_text(encoding="utf-8")
    lines = t.split("\n")
    p.write_text("\n".join([lines[0], note.strip()] + lines[1:]), encoding="utf-8")
    print("annotated", name)

rp = OUT / "S1P_REPORT.md"
t = rp.read_text(encoding="utf-8")
anchor = "## 7. Deviations from the instruction's own assumptions, summarised"
assert t.count(anchor) == 1
t = t.replace(anchor, note.strip() + "\n\n" + anchor)
rp.write_text(t, encoding="utf-8")
print("annotated S1P_REPORT.md")

print()
print("PRE :", json.dumps(pre))
print("POST:", json.dumps(post))

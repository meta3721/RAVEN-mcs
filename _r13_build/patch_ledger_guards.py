"""Amend ledger item 64 and append items 66-68 (two-guard relationship; docx audit; self-correction)."""
from __future__ import annotations

import pathlib

LEDGER = pathlib.Path(r"C:\Cursor\raven.mcs\ccfa-review-reports\raven-mcs-metric-diagnosis-ledger.md")
LEDGER = pathlib.Path(r"C:\Cursor\raven.mcs\ccfa-review-reports\raven-mcs-metric-definition-diagnosis.md")
t = LEDGER.read_text(encoding="utf-8")
assert "Part IX" in t, "Part IX missing"

OLD = ("Guard provenance: `reuse_guard.py` mtime **2026-10-07 17:00:29** and "
       "`real_runner/runner.py` mtime **2026-10-07 17:00:32**, i.e. both postdate the 16:27:41 end of "
       "round (iii).")
NEW = ("Guard provenance - **[amended 2026-10-08, see item 66]** `reuse_guard.py` mtime "
       "**2026-10-07 17:00:29** and `real_runner/runner.py` mtime **2026-10-07 17:00:32**, both after "
       "the 16:27:41 end of round (iii). As first written this invited the reading that the guard "
       "*module* was created then; item 66 corrects that. What the timestamps establish is that both "
       "files were last written after round (iii) closed and that the guard was therefore not "
       "enforced on round (iii)'s path - not that the module is new.")
n = t.count(OLD)
assert n == 1, f"item-64 anchor count {n}"
t = t.replace(OLD, NEW)

APPEND = """

## IX.4 Second-pass corrections and additions (items 66-68), 2026-10-08

| # | correction | evidence |
|:--|:---|:---|
| 66 | **Correction to item 64: the protocol-closure guard is not new.** Item 64 recorded only that `reuse_guard.py` has mtime 2026-10-07 17:00:29, which invited the reading that the guard was created then. It was not. `artifacts/e3_multidataset_real_runner_canary_r1/E3_CANARY_TRAFFIC_REUSE_GUARD.json` (**mtime 2026-08-10 21:57:49**, duplicated at `artifacts/e3_numerical_integrity_clean_canary_fix_r1/E3_CANARY_TRAFFIC_REUSE_GUARD.json` 2026-08-11 09:29:51) reports `formal_block_still_active: true` and `is_reused_e2_helper: true`, and both of those values are produced by **calling the protocol-closure guard's own functions** (`assert_schedulable_e3_run`, `is_reused_e2_traffic_block`) through `e3/canary/traffic_reuse_guard.py`. The guard therefore existed and refused correctly on **2026-08-10**, two months before the timestamp item 64 cites. What the 2026-10-07 17:00:29 / 17:00:32 writes mark is the **wiring of the guard into `run_e3_real`** (plus a rewrite of the untracked guard file) - which is what let round (iii) at 15:25-16:27 train nine `fedavg_window` traffic cells that the guard refuses today. Both files are untracked, so neither the guard's nor the runner's pre-17:00 content can be read; the wiring inference rests on the timestamps, on those nine runs succeeding, and on the driver containing no bypass. | `artifacts/e3_multidataset_real_runner_canary_r1/E3_CANARY_TRAFFIC_REUSE_GUARD.json`; `src/raven_mcs/e3/canary/traffic_reuse_guard.py`; file mtimes |
| 67 | **There are two traffic guards, not one, and they are layered.** `e3/protocol_closure/reuse_guard.py` (the formal-seed guard) refuses `traffic + complete_aligned + seed in 30001..30020 + {fedavg_window, fedasync_window, flamf_timealign_adapted, twostage_hajek, raven}` with `DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED`. `e3/canary/traffic_reuse_guard.py` (the canary guard) **imports the formal-seed guard** and adds a strictly wider exclusion: the same five methods on traffic at **any** seed, including the canary seed 31001, raising `REUSED_METHOD_PATH_NOT_EXECUTED_IN_TRAFFIC_CANARY`. Its recorded proof lists the canary's permitted traffic methods as exactly `local_hajek, inst_cal, debt_cal, raven_simoracle, central_all, central_delivered` - **exactly the six arms present in `artifacts/e3_formal_runs_r1/runs/traffic`** - so the arm gap recorded in item 64 is the guard's design rather than an accident. Verified after the item-65 exemption: `build_traffic_reuse_guard_evidence()` still returns `status: PASS`, `duplicate_blocked: true`, `formal_block_still_active: true`; `assert_canary_schedulable` still raises for `fedavg_window` and `raven` at seed 31001 and still permits `raven_simoracle` and `debt_cal`; the new opt-in does **not** leak into the canary path, because the canary guard calls `assert_schedulable_e3_run` without the flag and independently raises its own code. | `src/raven_mcs/e3/canary/traffic_reuse_guard.py`; `E3_CANARY_TRAFFIC_REUSE_GUARD.json`; live re-run of the evidence builder |
| 68 | **The V2.3 design document contains neither guard and no reuse/seal-block policy.** `参考文件/RAVEN-MCS_V2.3_实验设计方案.docx` (mtime 2026-07-26 20:39, 405 866 B; 242 non-empty paragraphs, 35 tables, 26 859 extracted characters) has **zero** occurrences of `guard`, `守卫`, `sealed` as a run-block concept, `复用`, `重跑` in the reuse sense, `金丝雀`, `canary`, `30001`, `31001`, `REUSED`, `DUPLICATE`, `REUSE_ONLY`, `traffic_reuse_guard`, `reuse_guard`, `protocol_closure`, `E2_TRAFFIC` or `CanaryTrafficSealed`. Its thirteen `封`-family hits are configuration **freeze** rules (e.g. "冻结配置后生成 frozen_config.yaml 和 hash", "测试段只在最终冻结配置后运行一次"), a different concept. What the document does specify, and what the guards later operationalise, is: **G1 事件复现** ("同一 seed 下所有方法的 R、O、E、U、计算时延、网络时延完全相同"); the test-once rule and the manifest requirement ("每个 run 的 manifest.json 至少包含 Git commit、dirty 状态、数据哈希、配置哈希、环境哈希…"); a staged seed protocol ("先 3 个种子筛选，再用 5 个种子确认；最终冻结后跑 20 种子"); and NSW Traffic as a controlled dataset with a mandatory station-quality gate. The reuse/seal policy itself lives only in code plus the 2026-08-10 evidence. Note for item A3 of the S1' round: the document's own staged logic (small screen, then confirmation, then 20) is consistent with reading the S1' instruction's `n = 15` as the eventual confirmatory set rather than the screen, although the document's numbers (3 / 5 / 20) are not the instruction's (5 / 15). | `_r13_build/DESIGN_V23_EXTRACT.txt`; `_r13_build/DESIGN_V23_GUARD_SEARCH.md`; scripts `extract_design_docx.py`, `search_design_concepts.py` |
"""

LEDGER.write_text(t.rstrip("\n") + APPEND, encoding="utf-8")
print("amended item 64; appended items 66-68")
print("ledger lines:", len(LEDGER.read_text(encoding="utf-8").splitlines()))

"""Append ledger item 74: the NSW-Traffic Stage C result and the round's closing verdict."""
from __future__ import annotations

import pathlib

LEDGER = pathlib.Path(r"C:\Cursor\raven.mcs\ccfa-review-reports\raven-mcs-metric-definition-diagnosis.md")
t = LEDGER.read_text(encoding="utf-8")
assert "item 74" not in t

APPEND = """

## IX.6 Fourth-pass addition (item 74), 2026-10-08: the NSW-Traffic Stage C and the round's close

| # | correction | evidence |
|:--|:---|:---|
| 74 | **NSW-Traffic Stage C was run, and H is negative on all three blocks: the oracle-margin route is closed by measurement, not by undertraining.** With the frozen configuration (`eta_s* = 3e-3`) and both arms (the user chose to run `raven` as well, so the recorded exemption was exercised for it too), the paired-by-seed headroom is `mean_H = -0.080700`, bootstrap 95 % CI `[-0.268877, +0.017194]`, `MDE80(n = 5) = 0.349835`, `K_r <= 3` share `0.111111`, and **`kr_excluded_from_GO = False`** - so this NO-GO-H is a *measured* result, unlike SensorScope and U-Air where section 6's clause excludes the block before H is even consulted. Combined with the earlier runs: N3' is PASS on all three blocks (SensorScope 0.986505, U-Air 0.832921, NSW-Traffic 0.857589 against the frozen `central_delivered` on the same seeds), and H is negative everywhere (SensorScope -0.018749 CI `[-0.039045, +0.001548]`; U-Air **-0.163333 CI `[-0.247807, -0.059271]`, strictly negative**; NSW-Traffic as above). Two conclusions follow and should travel together: a standard server optimizer *does* make the federated learner train (parameter movement rises 7-70x over the frozen SGD step), and once it does, the oracle-margin reference `raven_simoracle` supplies **no headroom on any block** - on U-Air it is significantly *worse* than plain FedAvg. That is the measured form of the concern section 0 raised when it noted the earlier H had been measured on an untrained model. A process note in the same item: an intermediate one-shot fixer (`_r13_build/fix_artifacts_after_traffic.py`, now retired to `.superseded`) rewrote the traffic Stage C entry back to `not_run`; it was caught by re-reading `tables/STAGE_C_H.csv`, the Stage C computation was re-executed compute-only with every run skipped as complete, and the assembler now stamps `created_utc` itself so the fixer is unnecessary. No incorrect value survives in the final artifacts (`S1P_VERDICT.json`, `S1P_STAGE_C_H.json`, `tables/STAGE_C_H.csv`). | `results_server_optimizer/round_v1/{S1P_VERDICT.json,S1P_STAGE_C_H.json,tables/STAGE_C_H.csv,S1P_REPORT.md,S1P_BLOCKED.md}`; `driver/stageC_traffic.log` |
"""

LEDGER.write_text(t.rstrip("\n") + APPEND, encoding="utf-8")
print("appended ledger item 74")
print("ledger lines:", len(LEDGER.read_text(encoding="utf-8").splitlines()))

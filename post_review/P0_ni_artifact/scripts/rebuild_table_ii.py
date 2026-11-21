"""Check that TABLE_II_MAIN_EFFECTIVENESS.csv matches the manuscript 4-decimal freeze.

Does not retrain. Run from the bundle root:

    python scripts/rebuild_table_ii.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "tables" / "TABLE_II_MAIN_EFFECTIVENESS.csv"
FREEZE_PATH = ROOT / "tables" / "TABLE_II_FREEZE.json"

DISPLAY = {
    "RMSE_mu": "RMSE_mu_mean",
    "WorstGroupRMSE": "WorstGroupRMSE_mean",
    "Delta_group": "Delta_group_mean",
    "Delta_c_s": "Delta_c_s_mean",
}


def round4(x: float) -> float:
    return round(float(x) + 1e-15, 4)


def main() -> int:
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    bad = 0
    print("dataset\tmethod\tRMSE_mu\tWorstGroup\tDelta_group\tDelta_c_s\trole")
    for r in rows:
        ds, method = r["dataset"], r["method"]
        shown = {k: round4(r[col]) for k, col in DISPLAY.items()}
        print(
            f"{ds}\t{method}\t{shown['RMSE_mu']:.4f}\t"
            f"{shown['WorstGroupRMSE']:.4f}\t{shown['Delta_group']:.4f}\t"
            f"{shown['Delta_c_s']:.4f}\t{r['role']}"
        )
        expected = freeze.get(ds, {}).get(method)
        if not expected:
            continue
        for key, want in expected.items():
            got = shown[key]
            if got != float(want):
                print(f"MISMATCH {ds} {method} {key}: got {got} want {want}", file=sys.stderr)
                bad += 1
    if bad:
        print(f"FAIL mismatches={bad}", file=sys.stderr)
        return 1
    print("OK Table II 4-decimal freeze matched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

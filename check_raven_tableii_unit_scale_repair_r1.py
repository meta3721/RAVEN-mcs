"""T2R-G1 … T2R-G28 checker."""

from __future__ import annotations

from pathlib import Path

from raven_mcs.final_table_ii_unit_scale_repair_r1.gates import run_gates
from raven_mcs.final_table_ii_unit_scale_repair_r1.constants import OUT_DIR


def main() -> int:
    root = Path(__file__).resolve().parent
    out = root / OUT_DIR
    result = run_gates(root, out)
    print(f"T2R gates {result['n_pass']}/{result['n_total']} all_pass={result['all_pass']}")
    for gid, payload in result["gates"].items():
        mark = "PASS" if payload["pass"] else "FAIL"
        print(f"  {gid} {mark}: {payload['detail']}")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""FDAF-G1 … FDAF-G52 checker."""

from __future__ import annotations

from pathlib import Path

from raven_mcs.final_paper_data_asset_freeze_r1.gates import run_gates
from raven_mcs.final_paper_data_asset_freeze_r1.constants import OUT_DIR


def main() -> int:
    root = Path(__file__).resolve().parent
    out = root / OUT_DIR
    result = run_gates(root, out)
    print(f"FDAF gates {result['n_pass']}/{result['n_total']} all_pass={result['all_pass']}")
    for gid, payload in result["gates"].items():
        mark = "PASS" if payload["pass"] else "FAIL"
        print(f"  {gid} {mark}: {payload['detail']}")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

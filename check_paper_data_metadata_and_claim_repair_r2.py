"""R2-G1 … R2-G30 checker for paper-data metadata and claim repair."""

from __future__ import annotations

from pathlib import Path

from raven_mcs.paper_data_r2.gates import run_gates


def main() -> int:
    root = Path(__file__).resolve().parent
    paper = root / "paper_ready_r2"
    result = run_gates(root, paper, {})
    print(f"R2 gates {result['n_pass']}/{result['n_total']} all_pass={result['all_pass']}")
    for gid, payload in result["gates"].items():
        mark = "PASS" if payload["pass"] else "FAIL"
        print(f"  {gid} {mark}: {payload['detail']}")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

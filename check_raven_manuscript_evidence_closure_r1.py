"""MEC-G1 … MEC-G33 checker."""

from __future__ import annotations

from pathlib import Path

from raven_mcs.manuscript_evidence_closure_r1.gates import run_gates


def main() -> int:
    root = Path(__file__).resolve().parent
    out = root / "manuscript_evidence_closure_r1"
    result = run_gates(root, out)
    print(f"MEC gates {result['n_pass']}/{result['n_total']} all_pass={result['all_pass']}")
    for gid, payload in result["gates"].items():
        mark = "PASS" if payload["pass"] else "FAIL"
        print(f"  {gid} {mark}: {payload['detail']}")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

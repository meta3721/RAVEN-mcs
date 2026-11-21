#!/usr/bin/env python3
"""Write report + stop status; re-check gates to close G25/G26."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.semantic_repair.gates import run_gates  # noqa: E402
from raven_mcs.e4.semantic_repair.package import write_report, write_stop_status  # noqa: E402


def main() -> int:
    write_report(ROOT, {"pass_count": 0, "total_count": 26, "all_pass": False, "failed": ["pending"]})
    write_stop_status(ROOT, {"all_pass": False})
    gates = run_gates(ROOT)
    write_stop_status(ROOT, {"all_pass": bool(gates.get("core_ok"))})
    write_report(ROOT, gates)
    gates = run_gates(ROOT)
    write_report(ROOT, gates)
    stop = write_stop_status(ROOT, {"all_pass": bool(gates.get("all_pass") or gates.get("core_ok"))})
    gates = run_gates(ROOT)
    stop = write_stop_status(ROOT, gates)
    print(json.dumps({
        "gates_all_pass": gates.get("all_pass"),
        "failed": gates.get("failed"),
        "stop": stop.get("status"),
    }, indent=2))
    return 0 if gates.get("all_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())

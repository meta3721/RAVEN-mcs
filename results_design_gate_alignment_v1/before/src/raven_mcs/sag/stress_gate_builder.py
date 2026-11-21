"""Artifact-derived R1I-S0..S24 gates. No hardcoded pass=True in the runner."""

from __future__ import annotations

from typing import Any, Sequence


def gate_row(
    gid: str,
    description: str,
    evidence: str,
    metric: str,
    expected: str,
    observed: Any,
    passed: bool,
) -> dict[str, Any]:
    return {
        "gate_id": gid,
        "description": description,
        "evidence_file": evidence,
        "metric": metric,
        "expected": expected,
        "observed": str(observed),
        "pass": bool(passed),
    }


def build_gates(checks: Sequence[tuple]) -> list[dict[str, Any]]:
    return [gate_row(*item) for item in checks]

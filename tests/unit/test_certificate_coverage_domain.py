"""Δ coverage is defined only on common nonempty active sets."""

from __future__ import annotations


def common_support_rows(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        if int(row.get("both_empty") or 0) == 1:
            continue
        if int(row.get("active_set_mismatch") or 0) == 1:
            continue
        if row.get("Delta_beta") is None:
            continue
        out.append(row)
    return out


def test_coverage_domain_excludes_mismatch_and_empty() -> None:
    rows = [
        {"both_empty": 1, "active_set_mismatch": 0, "Delta_beta": None},
        {"both_empty": 0, "active_set_mismatch": 1, "Delta_beta": 0.1},
        {"both_empty": 0, "active_set_mismatch": 0, "Delta_beta": 0.2},
    ]
    kept = common_support_rows(rows)
    assert len(kept) == 1
    assert kept[0]["Delta_beta"] == 0.2

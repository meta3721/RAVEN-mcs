"""Strict non-wrap chronology audit."""
from __future__ import annotations

from typing import Any


def audit_nonwrap_chronology(schedule: dict[str, Any]) -> dict[str, Any]:
    rows = schedule["rows"]
    audit = dict(schedule.get("audit") or {})
    by_client: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        by_client.setdefault(str(r["client_id"]), []).append(r)

    per_client = 0
    wraparound = 0
    mono_idx = 0
    mono_ts = 0
    for _cid, items in by_client.items():
        items = sorted(items, key=lambda x: int(x["window_id"]))
        prev_wid = -1
        prev_si = -1
        prev_t0 = -1
        for r in items:
            wid = int(r["window_id"])
            si = int(r.get("source_start_index", -1))
            t0 = int(r.get("source_timestamp_min", -1))
            if wid <= prev_wid:
                per_client += 1
            if prev_si >= 0 and si < prev_si:
                mono_idx += 1
            if prev_t0 >= 0 and t0 < prev_t0:
                wraparound += 1
                mono_ts += 1
            prev_wid = wid
            prev_si = si
            prev_t0 = t0

    modulo_usage = int(audit.get("modulo_operator_usage_count", 0))
    repeated = int(audit.get("repeated_block_count", 0))
    unique_ratio = float(audit.get("unique_window_payload_ratio", 0.0))
    global_viol = int(per_client + mono_idx + mono_ts)
    status = (
        "PASS"
        if (
            wraparound == 0
            and modulo_usage == 0
            and mono_idx == 0
            and mono_ts == 0
            and per_client == 0
            and repeated == 0
            and unique_ratio >= 0.80
            and int(audit.get("schedule_uniforms_used_count", 0)) > 0
        )
        else "FAIL"
    )
    return {
        "per_client_monotonic_violation_count": int(per_client + mono_idx + mono_ts),
        "global_monotonic_violation_count": int(global_viol),
        "wraparound_count": int(wraparound),
        "modulo_operator_usage_count": int(modulo_usage),
        "repeated_block_count": int(repeated),
        "duplicate_window_payload_count": int(audit.get("duplicate_window_payload_count", 0)),
        "unique_window_payload_ratio": unique_ratio,
        "source_reuse_count": int(audit.get("source_reuse_count", 0)),
        "chronology_status": status,
        "chronological_order_status": status,
        "maximum_legal_continuous_windows": audit.get("maximum_legal_continuous_windows"),
        "limiting_client": audit.get("limiting_client"),
    }

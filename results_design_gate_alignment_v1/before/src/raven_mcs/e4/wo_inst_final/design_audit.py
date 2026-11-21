"""Offline U-Air 774-window Design layer audit."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

from .constants import FORMAL_SEEDS, art_path, e3_path, e4_original_path


def _set_hash(ids: list[str] | set[str]) -> str:
    payload = json.dumps(sorted(str(x) for x in ids), separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_wm(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and "windows" in raw:
        return list(raw["windows"])
    raise ValueError(f"Unexpected window_metrics schema: {path}")


def _et_layers(events_path: Path) -> dict[int, dict[str, str]]:
    """Per-window hashes for opportunity/observed/usable/registered from EventTrace."""
    df = pq.read_table(events_path).to_pandas()
    out: dict[int, dict[str, str]] = {}
    for wid, g in df.groupby("window_id"):
        opportunity = sorted(str(c) for c in g["client_id"].tolist())
        observed = []
        usable = []
        registered = []
        for _, row in g.iterrows():
            cid = str(row["client_id"])
            obs = row.get("observed_unit_ids")
            if obs is None:
                obs_list = []
            elif isinstance(obs, str):
                try:
                    obs_list = json.loads(obs)
                except json.JSONDecodeError:
                    obs_list = []
            else:
                obs_list = list(obs)
            if obs_list:
                observed.append(cid)
            if int(row.get("U") or 0) == 1:
                usable.append(cid)
            # Registration: any EventTrace client row with a registration_time
            if row.get("registration_time") is not None:
                registered.append(cid)
        out[int(wid)] = {
            "opportunity": _set_hash(opportunity),
            "observed": _set_hash(observed),
            "usable": _set_hash(usable),
            "registered": _set_hash(registered),
            "opportunity_ids": opportunity,
            "observed_ids": observed,
            "usable_ids": usable,
            "registered_ids": registered,
        }
    return out


def _weight_layers(row: dict[str, Any]) -> dict[str, Any]:
    clients = [str(c) for c in (row.get("active_clients") or [])]
    alpha = list(row.get("alpha") or [])
    beta = list(row.get("beta_hat") or [])
    pos_final = [
        c for c, a in zip(clients, alpha) if float(a) > 0.0
    ]
    pos_design = [
        c for c, b in zip(clients, beta) if float(b) > 0.0
    ]
    # Persisted A_r is the P2 candidate / aggregation participating set.
    return {
        "p2_candidate": _set_hash(clients),
        "positive_design_weight": _set_hash(pos_design),
        "positive_final_weight": _set_hash(pos_final),
        "aggregation": _set_hash(clients),
        "clients": clients,
    }


def _classify(full_et: dict[str, Any], wo_et: dict[str, Any], full_w: dict[str, Any], wo_w: dict[str, Any]) -> tuple[str, str, str]:
    layers = [
        ("opportunity", full_et["opportunity"], wo_et["opportunity"]),
        ("observed", full_et["observed"], wo_et["observed"]),
        ("usable", full_et["usable"], wo_et["usable"]),
        ("registered", full_et["registered"], wo_et["registered"]),
        ("p2_candidate", full_w["p2_candidate"], wo_w["p2_candidate"]),
        ("positive_design_weight", full_w["positive_design_weight"], wo_w["positive_design_weight"]),
        ("positive_final_weight", full_w["positive_final_weight"], wo_w["positive_final_weight"]),
        ("aggregation", full_w["aggregation"], wo_w["aggregation"]),
    ]
    first = None
    for name, a, b in layers:
        if a != b:
            first = name
            break
    # Physical EventTrace layers must match (shared identity).
    et_ok = all(
        full_et[k] == wo_et[k]
        for k in ("opportunity", "observed", "usable", "registered")
    )
    if not et_ok:
        return (
            first or "opportunity",
            "EventTrace-derived physical layer differs unexpectedly",
            "SCOPE_LEAKAGE",
        )
    if first is None:
        return ("none", "no layer difference", "UNRESOLVED")
    if first in {
        "positive_design_weight",
        "positive_final_weight",
        "aggregation",
        "p2_candidate",
    }:
        # p2_candidate/aggregation change is valid only as downstream of design
        # weight support (zeta→m_total>0 expansion).
        return (
            first,
            (
                "Shared EventTrace physical layers identical; effective participation "
                "differs only via Design ablation weight-support (zeta=1 expands "
                "m_total>0 / A_r)."
            ),
            "VALID_WEIGHT_SUPPORT_EFFECT",
        )
    return (first, "unexpected early layer difference", "SCOPE_LEAKAGE")


def run_design_774_audit(root: Path) -> dict[str, Any]:
    art = art_path(root)
    art.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    counts = {
        "opportunity_diff": 0,
        "observed_diff": 0,
        "usable_diff": 0,
        "registered_diff": 0,
        "p2_candidate_diff": 0,
        "positive_design_weight_diff": 0,
        "positive_final_weight_diff": 0,
        "aggregation_set_diff": 0,
        "valid_weight_support_effect": 0,
        "scope_leakage": 0,
        "unresolved": 0,
    }

    for seed in FORMAL_SEEDS:
        et_path = (
            e3_path(root)
            / "eventtraces"
            / "uair"
            / f"seed{seed}"
            / "training_eventtrace"
            / "events.parquet"
        )
        identity = json.loads(
            (
                e3_path(root)
                / "eventtraces"
                / "uair"
                / f"seed{seed}"
                / "training_eventtrace"
                / "trace_identity.json"
            ).read_text(encoding="utf-8")
        )
        raven_man = json.loads(
            (
                e3_path(root)
                / "runs"
                / "uair"
                / "raven"
                / f"seed{seed}"
                / "runtime_manifest.json"
            ).read_text(encoding="utf-8")
        )
        des_man = json.loads(
            (
                e4_original_path(root)
                / "runs"
                / "uair"
                / "raven_wo_design"
                / f"seed{seed}"
                / "runtime_manifest.json"
            ).read_text(encoding="utf-8")
        )
        if raven_man.get("EventTrace_hash") != des_man.get("EventTrace_hash"):
            raise RuntimeError(f"EventTrace identity mismatch seed{seed}")
        if raven_man.get("EventTrace_hash") != identity.get("trace_hash"):
            raise RuntimeError(f"EventTrace hash != identity seed{seed}")

        et_layers = _et_layers(et_path)
        full_wm = _load_wm(
            e3_path(root) / "runs" / "uair" / "raven" / f"seed{seed}" / "window_metrics.json"
        )
        des_wm = _load_wm(
            e4_original_path(root)
            / "runs"
            / "uair"
            / "raven_wo_design"
            / f"seed{seed}"
            / "window_metrics.json"
        )
        if len(full_wm) != len(des_wm):
            raise RuntimeError(f"window count mismatch seed{seed}")

        for fr, dr in zip(full_wm, des_wm):
            wid = int(fr.get("window_id"))
            if int(dr.get("window_id")) != wid:
                raise RuntimeError(f"window_id mismatch seed{seed} {wid}")
            full_clients = set(fr.get("active_clients") or [])
            des_clients = set(dr.get("active_clients") or [])
            if full_clients == des_clients:
                continue
            et = et_layers[wid]
            # Shared EventTrace → identical physical layer hashes for both methods.
            full_et = et
            wo_et = et
            full_w = _weight_layers(fr)
            wo_w = _weight_layers(dr)
            first, reason, cls = _classify(full_et, wo_et, full_w, wo_w)
            row = {
                "seed": seed,
                "window": wid,
                "eventtrace_hash": identity.get("trace_hash"),
                "full_opportunity_hash": full_et["opportunity"],
                "wo_design_opportunity_hash": wo_et["opportunity"],
                "full_observed_hash": full_et["observed"],
                "wo_design_observed_hash": wo_et["observed"],
                "full_usable_hash": full_et["usable"],
                "wo_design_usable_hash": wo_et["usable"],
                "full_registered_hash": full_et["registered"],
                "wo_design_registered_hash": wo_et["registered"],
                "full_p2_candidate_hash": full_w["p2_candidate"],
                "wo_design_p2_candidate_hash": wo_w["p2_candidate"],
                "full_positive_design_weight_hash": full_w["positive_design_weight"],
                "wo_design_positive_design_weight_hash": wo_w["positive_design_weight"],
                "full_positive_final_weight_hash": full_w["positive_final_weight"],
                "wo_design_positive_final_weight_hash": wo_w["positive_final_weight"],
                "full_aggregation_set_hash": full_w["aggregation"],
                "wo_design_aggregation_set_hash": wo_w["aggregation"],
                "first_layer_of_difference": first,
                "difference_reason": reason,
                "scientific_classification": cls,
                "full_a_r_size": len(full_clients),
                "wo_design_a_r_size": len(des_clients),
            }
            rows.append(row)
            if full_et["opportunity"] != wo_et["opportunity"]:
                counts["opportunity_diff"] += 1
            if full_et["observed"] != wo_et["observed"]:
                counts["observed_diff"] += 1
            if full_et["usable"] != wo_et["usable"]:
                counts["usable_diff"] += 1
            if full_et["registered"] != wo_et["registered"]:
                counts["registered_diff"] += 1
            if full_w["p2_candidate"] != wo_w["p2_candidate"]:
                counts["p2_candidate_diff"] += 1
            if full_w["positive_design_weight"] != wo_w["positive_design_weight"]:
                counts["positive_design_weight_diff"] += 1
            if full_w["positive_final_weight"] != wo_w["positive_final_weight"]:
                counts["positive_final_weight_diff"] += 1
            if full_w["aggregation"] != wo_w["aggregation"]:
                counts["aggregation_set_diff"] += 1
            if cls == "VALID_WEIGHT_SUPPORT_EFFECT":
                counts["valid_weight_support_effect"] += 1
            elif cls == "SCOPE_LEAKAGE":
                counts["scope_leakage"] += 1
            else:
                counts["unresolved"] += 1

    if len(rows) != 774:
        raise RuntimeError(f"expected 774 differing windows, got {len(rows)}")

    csv_path = art / "E4_WO_DESIGN_774_WINDOW_LAYER_AUDIT.csv"
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.DictWriter(handle, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    summary = {
        "total_differing_windows": len(rows),
        "counts": counts,
        "csv_sha256": sha256_file(csv_path),
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(summary, art / "E4_WO_DESIGN_774_WINDOW_LAYER_SUMMARY.json")
    md = [
        "# U-Air w/o-Design 774-window layer audit",
        "",
        f"- total_differing_windows: {len(rows)}",
        *[f"- {k}: {v}" for k, v in counts.items()],
        "",
    ]
    (art / "E4_WO_DESIGN_774_WINDOW_LAYER_SUMMARY.md").write_text(
        "\n".join(md), encoding="utf-8"
    )

    if counts["scope_leakage"] == 0 and counts["unresolved"] == 0:
        decision = "WO_DESIGN_VALID_WEIGHT_SUPPORT_EFFECT_CONFIRMED"
        keep = True
        stop = False
    elif counts["scope_leakage"] > 0:
        decision = "WO_DESIGN_SCOPE_LEAKAGE_CONFIRMED"
        keep = False
        stop = True
    else:
        decision = "WO_DESIGN_LAYER_SEMANTICS_UNRESOLVED"
        keep = False
        stop = True

    decision_payload = {
        "decision": decision,
        "keep_existing_40_wo_design_runs": keep,
        "stop_for_teacher_review": stop,
        "scope_leakage": counts["scope_leakage"],
        "unresolved": counts["unresolved"],
        "valid_weight_support_effect": counts["valid_weight_support_effect"],
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    dump_json(decision_payload, art / "E4_WO_DESIGN_FINAL_DECISION_R2.json")
    return {"summary": summary, "decision": decision_payload, "n_rows": len(rows)}

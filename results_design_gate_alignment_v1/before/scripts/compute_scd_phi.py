#!/usr/bin/env python3
"""Compute SensorScope / U-Air zero-target mass fraction phi.

Follows post_review/C2_scd_phi/HANDOFF_EXECUTOR.md. Measures only.
Does not train, does not edit the manuscript, does not change Design flags.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.correction.pi_target import build_pi_target  # noqa: E402
from raven_mcs.e3.canary.dataset_load import (  # noqa: E402
    load_spatial_to_client,
    verify_dataset_hash,
)
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum  # noqa: E402
from raven_mcs.simulation.event_trace import load_event_trace  # noqa: E402

OUT = ROOT / "post_review" / "C2_scd_phi"
ET = ROOT / "artifacts" / "e3_formal_runs_r1" / "eventtraces"
DATASETS = ("sensorscope", "uair")
SEEDS = list(range(30001, 30021))
G1 = {"sensorscope": 0.0, "uair": 0.2546875}
ATOL = 1e-12
ZERO = 0.0


def _pi_of(pi_target: dict[tuple[str, str], float], client_id: str, stratum: str) -> float:
    return float(pi_target.get((str(client_id), str(stratum)), 0.0))


def prepare(dataset: str):
    atomic = pd.read_parquet(ROOT / "data" / "processed" / dataset / "atomic_units.parquet")
    atomic_sealed, _ = apply_sealed_opportunity_stratum(atomic, dataset=dataset, root=ROOT)
    spatial_to_client = load_spatial_to_client(ROOT, dataset)
    atomic_for_pi = atomic_sealed.copy()
    if "target_group_main" not in atomic_for_pi.columns:
        atomic_for_pi["target_group_main"] = atomic_for_pi["target_group"].astype(str)
    pi_frame = build_pi_target(atomic_for_pi, spatial_to_client, split="test")
    pi_target = {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in pi_frame.itertuples()
    }
    unit_stratum = {
        str(r.unit_id): str(r.opportunity_stratum) for r in atomic_sealed.itertuples(index=False)
    }
    unit_client: dict[str, str] = {}
    for r in atomic_sealed.itertuples(index=False):
        sid = str(r.spatial_id)
        if sid not in spatial_to_client:
            raise ValueError(f"{dataset}: spatial_id {sid} lacks client mapping")
        unit_client[str(r.unit_id)] = str(spatial_to_client[sid])
    train = atomic_sealed.loc[atomic_sealed["split"].astype(str) == "train"]
    return pi_target, unit_stratum, unit_client, train


def phi_train_unit(train, pi_target, unit_stratum, unit_client):
    uids = train["unit_id"].astype(str).unique()
    zeros = 0
    for uid in uids:
        pi = _pi_of(pi_target, unit_client[uid], unit_stratum[uid])
        zeros += int(pi <= ZERO)
    n = int(len(uids))
    return n, zeros, (zeros / n) if n else float("nan")


def phi_train_pair(train, pi_target, unit_client):
    pairs = set()
    for r in train.itertuples(index=False):
        uid = str(r.unit_id)
        pairs.add((unit_client[uid], str(r.opportunity_stratum)))
    zeros = 0
    for cid, stratum in pairs:
        zeros += int(_pi_of(pi_target, cid, stratum) <= ZERO)
    n = int(len(pairs))
    return n, zeros, (zeros / n) if n else float("nan")


def _close(a: float, b: float) -> bool:
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= ATOL


def compute_eventtrace(dataset: str, pi_target, unit_stratum, unit_client):
    n_app = 0
    n_app_zero = 0
    pooled_uids: set[str] = set()
    seed_rows = []
    missing = []
    for seed in SEEDS:
        trace_dir = ET / dataset / f"seed{seed}" / "training_eventtrace"
        if not (trace_dir / "events.parquet").is_file():
            missing.append(str(trace_dir.relative_to(ROOT)).replace("\\", "/"))
            continue
        trace, _identity = load_event_trace(trace_dir)
        seed_app = 0
        seed_app_zero = 0
        seed_uids: set[str] = set()
        for rec in trace.events.itertuples(index=False):
            cid = str(rec.client_id)
            risk = rec.risk_set_unit_ids or []
            for uid_raw in risk:
                uid = str(uid_raw)
                s = unit_stratum.get(uid, "unknown")
                pi = _pi_of(pi_target, cid, s)
                is_zero = int(pi <= ZERO)
                n_app += 1
                n_app_zero += is_zero
                seed_app += 1
                seed_app_zero += is_zero
                seed_uids.add(uid)
                pooled_uids.add(uid)
        n_u = int(len(seed_uids))
        n_u_zero = 0
        for uid in seed_uids:
            pi = _pi_of(pi_target, unit_client[uid], unit_stratum[uid])
            n_u_zero += int(pi <= ZERO)
        seed_rows.append(
            {
                "dataset": dataset,
                "seed": int(seed),
                "n_et_appearances": int(seed_app),
                "n_et_appearances_zero": int(seed_app_zero),
                "phi_et_occ_seed": (seed_app_zero / seed_app) if seed_app else float("nan"),
                "n_et_unique_units": n_u,
                "n_et_unique_zero": int(n_u_zero),
                "phi_et_unique_seed": (n_u_zero / n_u) if n_u else float("nan"),
            }
        )
    if missing:
        raise FileNotFoundError("missing EventTraces: " + ", ".join(missing))
    n_u_pool = int(len(pooled_uids))
    n_u_pool_zero = 0
    for uid in pooled_uids:
        pi = _pi_of(pi_target, unit_client[uid], unit_stratum[uid])
        n_u_pool_zero += int(pi <= ZERO)
    return {
        "n_et_appearances": int(n_app),
        "n_et_appearances_zero": int(n_app_zero),
        "phi_et_occ": (n_app_zero / n_app) if n_app else float("nan"),
        "n_et_unique_units": n_u_pool,
        "n_et_unique_zero": int(n_u_pool_zero),
        "phi_et_unique": (n_u_pool_zero / n_u_pool) if n_u_pool else float("nan"),
        "seed_rows": seed_rows,
    }


def decide(rows: list[dict]) -> dict:
    by_ds = {r["dataset"]: r for r in rows}
    ss = by_ds["sensorscope"]
    ua = by_ds["uair"]
    wiring_ok = bool(ss["phi_et_occ_matches_g1"] and ua["phi_et_occ_matches_g1"])
    ss_train = float(ss["phi_train_unit"])
    ss_occ = float(ss["phi_et_occ"])
    ua_train = float(ua["phi_train_unit"])
    ua_occ = float(ua["phi_et_occ"])
    ss_zero = _close(ss_train, 0.0) and _close(ss_occ, 0.0)
    ua_signal = ua_train > 0.0
    table_sign = ss_zero and ua_signal

    if not wiring_ok:
        status, reason = "STOP", "PHI_WIRING_MISMATCH"
    elif (ss_train > 0.0) or (ss_occ > 0.0):
        status, reason = "STOP", "SENSORSCOPE_PHI_POSITIVE"
    elif _close(ua_train, 0.0) and _close(ua_occ, 0.2546875):
        status, reason = "STOP", "TRAIN_UNIT_PHI_ZERO_BUT_ET_NOT"
    elif not ua_signal:
        status, reason = "STOP", "UAIR_TRAIN_UNIT_PHI_ZERO"
    elif not table_sign:
        status, reason = "STOP", "RULE_DOES_NOT_RECOVER_TABLE_SIGN"
    else:
        status, reason = "PASS", None

    ua_pct = round(100.0 * ua_train, 1)
    out = {
        "experiment_id": "SCD-PHI-SS-UA",
        "status": status,
        "reason": reason,
        "checks": {
            "wiring": wiring_ok,
            "ss_positivity": ss_zero,
            "ua_signal": ua_signal,
            "rule_recovers_table_sign": table_sign,
        },
        "phi_et_occ": {
            "sensorscope": ss_occ,
            "uair": ua_occ,
        },
        "phi_train_unit": {
            "sensorscope": ss_train,
            "uair": ua_train,
        },
        "uair_phi_train_unit_percent_one_decimal": ua_pct,
        "uair_phi_et_occ_percent_one_decimal": round(100.0 * ua_occ, 1),
        "uair_train_percent_matches_paper_25_5": ua_pct == 25.5,
        "rule_preview_not_applied": "Design_ON iff phi_scd == 0",
        "algorithm_2_rewritten": False,
    }
    if status == "PASS":
        out["phi_scd"] = {
            "definition": "phi_train_unit",
            "sensorscope": ss_train,
            "uair": ua_train,
        }
    else:
        out["phi_scd"] = None
    return out


def write_report(rows: list[dict], seed_rows: list[dict], decision: dict) -> str:
    by_ds = {r["dataset"]: r for r in rows}
    lines = [
        "# SCD phi report (SensorScope / U-Air)",
        "",
        "This round measures zero-target mass fraction. It does not rewrite Algorithm 2.",
        "",
        f"Decision: **{decision['status']}**"
        + (f" (`{decision['reason']}`)" if decision.get("reason") else "")
        + ".",
        "",
        "## Dataset summary",
        "",
        "| dataset | phi_train_unit | phi_train_pair | phi_et_occ | phi_et_unique | G1 expected | match G1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for ds in DATASETS:
        r = by_ds[ds]
        lines.append(
            f"| {ds} | {r['phi_train_unit']:.10g} | {r['phi_train_pair']:.10g} | "
            f"{r['phi_et_occ']:.10g} | {r['phi_et_unique']:.10g} | "
            f"{r['g1_phi_et_occ_expected']} | {r['phi_et_occ_matches_g1']} |"
        )
    lines.extend(
        [
            "",
            "Counts:",
            "",
        ]
    )
    for ds in DATASETS:
        r = by_ds[ds]
        lines.append(
            f"- {ds}: train units {r['n_train_zero']}/{r['n_train_units']}; "
            f"train pairs {r['n_train_pairs_zero']}/{r['n_train_pairs']}; "
            f"ET appearances {r['n_et_appearances_zero']}/{r['n_et_appearances']}; "
            f"ET unique {r['n_et_unique_zero']}/{r['n_et_unique_units']}; "
            f"atomic hash ok={r['atomic_hash_ok']}"
        )

    def _seed_span(dataset: str, col: str) -> tuple[float, float]:
        vals = [float(x[col]) for x in seed_rows if x["dataset"] == dataset]
        return min(vals), max(vals)

    lines.extend(["", "## Seed span (always-on traces 30001-30020)", ""])
    for ds in DATASETS:
        occ_lo, occ_hi = _seed_span(ds, "phi_et_occ_seed")
        uniq_lo, uniq_hi = _seed_span(ds, "phi_et_unique_seed")
        lines.append(
            f"- {ds}: phi_et_occ_seed in [{occ_lo:.10g}, {occ_hi:.10g}]; "
            f"phi_et_unique_seed in [{uniq_lo:.10g}, {uniq_hi:.10g}]"
        )

    ua = by_ds["uair"]
    ua_train_pct = round(100.0 * float(ua["phi_train_unit"]), 1)
    ua_occ_pct = round(100.0 * float(ua["phi_et_occ"]), 1)
    lines.extend(
        [
            "",
            "## Paper number 25.5%",
            "",
            f"- G1 / manuscript 25.5% is `phi_et_occ` on U-Air = {ua['phi_et_occ']} "
            f"({ua_occ_pct}%). Wiring match: {ua['phi_et_occ_matches_g1']}.",
            f"- Transferable candidate `phi_train_unit` on U-Air = {ua['phi_train_unit']} "
            f"({ua_train_pct}%). One-decimal match to 25.5: {ua_train_pct == 25.5}.",
            "",
            "## Table-sign preview (not applied)",
            "",
        ]
    )
    if decision["status"] == "PASS":
        lines.extend(
            [
                "Freeze `phi_scd := phi_train_unit`. Preview rule: Design ON iff phi_scd = 0.",
                "SensorScope phi_train_unit = 0 (ON); U-Air phi_train_unit > 0 (OFF).",
                "This report does not rewrite Algorithm 2 and does not change method keys.",
            ]
        )
    else:
        lines.append(
            "No freeze. Stop conditions in HANDOFF_EXECUTOR.md §5. Ask the human."
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(parents=True, exist_ok=True)

    rows = []
    seed_rows: list[dict] = []
    hash_records = []
    for dataset in DATASETS:
        href = verify_dataset_hash(ROOT, dataset)
        hash_records.append(href)
        if not href["match"]:
            raise SystemExit(
                f"FROZEN_DATASET_HASH_MISMATCH: {dataset} expected={href['expected']} got={href['got']}"
            )
        pi_target, unit_stratum, unit_client, train = prepare(dataset)
        n_tu, z_tu, phi_tu = phi_train_unit(train, pi_target, unit_stratum, unit_client)
        n_tp, z_tp, phi_tp = phi_train_pair(train, pi_target, unit_client)
        et = compute_eventtrace(dataset, pi_target, unit_stratum, unit_client)
        expected = G1[dataset]
        match = _close(float(et["phi_et_occ"]), expected)
        rows.append(
            {
                "dataset": dataset,
                "n_train_units": int(n_tu),
                "n_train_zero": int(z_tu),
                "phi_train_unit": float(phi_tu),
                "n_train_pairs": int(n_tp),
                "n_train_pairs_zero": int(z_tp),
                "phi_train_pair": float(phi_tp),
                "n_et_appearances": int(et["n_et_appearances"]),
                "n_et_appearances_zero": int(et["n_et_appearances_zero"]),
                "phi_et_occ": float(et["phi_et_occ"]),
                "n_et_unique_units": int(et["n_et_unique_units"]),
                "n_et_unique_zero": int(et["n_et_unique_zero"]),
                "phi_et_unique": float(et["phi_et_unique"]),
                "g1_phi_et_occ_expected": expected,
                "phi_et_occ_matches_g1": bool(match),
                "atomic_hash_ok": True,
            }
        )
        seed_rows.extend(et["seed_rows"])

    summary = pd.DataFrame(rows)
    seeds = pd.DataFrame(seed_rows)
    summary.to_csv(OUT / "tables" / "SCD_PHI.csv", index=False)
    seeds.to_csv(OUT / "tables" / "SCD_PHI_BY_SEED.csv", index=False)

    decision = decide(rows)
    payload = {
        "experiment_id": "SCD-PHI-SS-UA",
        "eventtrace_root": "artifacts/e3_formal_runs_r1/eventtraces",
        "pi_target_builder": "raven_mcs.correction.pi_target.build_pi_target",
        "pi_target_split": "test",
        "zero_test": "pi <= 0.0",
        "seeds": SEEDS,
        "atomic_hashes": hash_records,
        "rows": rows,
        "decision": decision,
    }
    (OUT / "SCD_PHI.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (OUT / "SCD_PHI_DECISION.json").write_text(
        json.dumps(decision, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "REPORT.md").write_text(write_report(rows, seed_rows, decision), encoding="utf-8")

    print(json.dumps(decision, indent=2))
    if decision["status"] != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

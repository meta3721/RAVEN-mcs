"""Canonical E3 method registry and per-method source hashes."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from raven_mcs.aggregation.method_policy import POLICY_MAP

ROOT = Path(__file__).resolve().parents[4]

# Exactly one canonical id per semantic method.
CANONICAL_METHODS: dict[str, dict[str, Any]] = {
    "fedavg_window": {"role": "MAIN_BASELINE", "display": "FedAvg-Window", "aliases": ["fedavg"]},
    "fedasync_window": {"role": "MAIN_BASELINE", "display": "FedAsync-Window", "aliases": ["fedasync"]},
    "flamf_timealign_adapted": {
        "role": "MAIN_BASELINE",
        "display": "TimeAlign-Agg",
        "aliases": ["timealign_agg", "timealign", "time_align", "time_align_agg"],
    },
    "local_hajek": {"role": "MAIN_BASELINE", "display": "Local-Hajek", "aliases": []},
    "twostage_hajek": {"role": "MAIN_BASELINE", "display": "TwoStage-Hajek", "aliases": ["two_stage_hajek"]},
    "inst_cal": {"role": "MAIN_BASELINE", "display": "Inst-Cal", "aliases": ["instant_calibration"]},
    "debt_cal": {"role": "MAIN_BASELINE", "display": "Debt-Cal", "aliases": []},
    "raven": {"role": "RAVEN", "display": "RAVEN-MCS", "aliases": ["raven_mcs"]},
    "raven_simoracle": {"role": "ORACLE", "display": "RAVEN-SimOracle", "aliases": ["simoracle"]},
    "central_all": {"role": "REFERENCE_ONLY", "display": "Central-All", "aliases": ["centralall"]},
    "central_delivered": {"role": "REFERENCE_ONLY", "display": "Central-Delivered", "aliases": ["centraldelivered"]},
    "flamf_original": {"role": "EXTERNAL", "display": "FLAMF-Original", "aliases": ["flamf"], "excluded": True},
}

METHOD_SOURCE_FILES: dict[str, list[str]] = {
    "fedavg_window": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
    ],
    "fedasync_window": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
    ],
    "flamf_timealign_adapted": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
    ],
    "local_hajek": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
        "src/raven_mcs/correction/hajek.py",
    ],
    "twostage_hajek": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
        "src/raven_mcs/correction/hajek.py",
    ],
    "inst_cal": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
        "src/raven_mcs/aggregation/p2_cvxpy.py",
    ],
    "debt_cal": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
        "src/raven_mcs/aggregation/p2_cvxpy.py",
        "src/raven_mcs/metrics/debt.py",
    ],
    "raven": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
        "src/raven_mcs/aggregation/p2_cvxpy.py",
        "src/raven_mcs/correction/hajek.py",
        "src/raven_mcs/metrics/debt.py",
    ],
    "raven_simoracle": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
        "src/raven_mcs/aggregation/p2_cvxpy.py",
        "src/raven_mcs/simulation/replay.py",
        "src/raven_mcs/e3/protocol_closure/constants.py",
    ],
    "central_all": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/e3/protocol_closure/central_reference.py",
        "src/raven_mcs/models/common_ndmf.py",
    ],
    "central_delivered": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/e3/protocol_closure/central_reference.py",
        "src/raven_mcs/models/common_ndmf.py",
    ],
    "flamf_original": [],
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonicalization_payload() -> dict[str, Any]:
    aliases = []
    for canon, meta in CANONICAL_METHODS.items():
        for alias in meta.get("aliases", []):
            aliases.append(
                {
                    "alias": alias,
                    "canonical_method_id": canon,
                    "classification": "ALIAS_ONLY",
                }
            )
    # Also record timealign_agg explicitly even if listed above
    return {
        "canonical_methods": [
            {
                "method_id": mid,
                "display": meta["display"],
                "role": meta["role"],
                "excluded": bool(meta.get("excluded", False)),
                "in_policy_map": mid in POLICY_MAP,
            }
            for mid, meta in CANONICAL_METHODS.items()
        ],
        "aliases": aliases,
        "n_canonical_semantic_methods": len(CANONICAL_METHODS),
        "n_non_excluded_canonical": sum(1 for m in CANONICAL_METHODS.values() if not m.get("excluded")),
        "rule": "aliases must not appear twice in run matrix / table / Holm family / ledger logical counts",
    }


def method_source_hashes(root: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    out: dict[str, Any] = {"methods": {}}
    for method, files in METHOD_SOURCE_FILES.items():
        if method == "flamf_original":
            out["methods"][method] = {
                "status": "EXCLUDED_WITH_REASON",
                "implementation_hash": None,
                "files": [],
                "reason": "external original FLAMF not faithfully reproduced; TimeAlign must not be renamed",
            }
            continue
        file_hashes = []
        for rel in files:
            p = root / rel
            if p.is_file():
                file_hashes.append({"path": rel, "sha256": _sha(p)})
        digest = hashlib.sha256(
            "|".join(f"{f['path']}:{f['sha256']}" for f in file_hashes).encode("utf-8")
        ).hexdigest()
        out["methods"][method] = {
            "status": "HASHED",
            "implementation_hash": digest,
            "files": file_hashes,
        }
    return out

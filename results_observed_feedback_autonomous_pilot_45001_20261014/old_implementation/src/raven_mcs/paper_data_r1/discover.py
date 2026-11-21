"""Discover relevant sealed evidence paths (read-only scan)."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .io_util import sha256_file, write_csv, write_json

KEYWORDS = re.compile(
    r"(e0|e1|e2|e3|e4|raven|sensorscope|u-?air|traffic|nsw|t-?drive|"
    r"formal|accepted|sealed|evidence|claim|metrics|statistics|ablation|"
    r"eventtrace|p2|solver|debt|hajek|manifest|provenance|checkpoint|"
    r"report|summary)",
    re.I,
)

INTERESTING_SUFFIXES = {
    ".csv",
    ".json",
    ".jsonl",
    ".md",
    ".parquet",
    ".npz",
    ".npy",
    ".pkl",
    ".log",
    ".yaml",
    ".yml",
    ".txt",
    ".tex",
    ".zip",
}

SCAN_ROOTS = [
    "artifacts",
    "deliverables",
    "outputs",
    "docs/reports",
    "configs/frozen",
    "data/manifests",
    "data/raw/tdrive_speed",
    "data/processed/tdrive_speed",
]

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "paper_ready_r1",
}

# Prefer hashing metadata + small/medium files; skip hashing huge binaries during discovery.
MAX_HASH_BYTES = 50 * 1024 * 1024


def _infer_round(path: str) -> str:
    low = path.lower()
    for tag in ("e4", "e3", "e2", "e1", "e0"):
        if f"/{tag}_" in low or f"\\{tag}_" in low or f"/{tag}/" in low or f"\\{tag}\\" in low:
            return tag.upper()
        if f"_{tag}_" in low or low.startswith(tag):
            return tag.upper()
    if "tdrive" in low or "t-drive" in low:
        return "TDRIVE"
    return ""


def _infer_dataset(path: str) -> str:
    low = path.lower()
    if "sensorscope" in low:
        return "SensorScope"
    if "uair" in low or "u-air" in low:
        return "U-Air"
    if "traffic" in low or "nsw" in low:
        return "NSW-Traffic"
    if "tdrive" in low or "t-drive" in low:
        return "T-Drive-Speed"
    if "balanced" in low:
        return "Balanced"
    return ""


def _infer_status(path: str) -> str:
    low = path.lower()
    if "superseded" in low or "gen1" in low:
        return "SUPERSEDED"
    if "invalid" in low or "gen0" in low:
        return "INVALID"
    if "not_comparable" in low or "not-comparable" in low:
        return "NOT_COMPARABLE"
    if "canary" in low:
        return "CANARY"
    if "sealed" in low or "final" in low or "formal" in low:
        return "VALID_CANDIDATE"
    return ""


def _candidate_layer(path: str) -> str:
    low = path.lower()
    if "e4_ablation_semantic" in low or "ablation_semantic_integrity_repair" in low:
        return "FULL_ARCHIVE"
    if any(x in low for x in ("superseded", "invalid", "canary", "gen0")):
        return "FULL_ARCHIVE"
    if any(
        x in low
        for x in (
            "claim",
            "summary",
            "statistics",
            "formal_results",
            "evidence_index",
            "paper",
            "final_valid",
        )
    ):
        return "PAPER_CORE"
    if any(x in low for x in ("supporting", "solver", "p2", "hajek", "runtime", "diagnostic")):
        return "PAPER_SUPPORTING"
    return "FULL_ARCHIVE"


def discover_sources(root: Path, out_dir: Path) -> list[dict[str, Any]]:
    root = Path(root)
    rows: list[dict[str, Any]] = []
    for rel_root in SCAN_ROOTS:
        base = root / rel_root
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if any(part in SKIP_DIR_NAMES for part in p.parts):
                continue
            rel = str(p.relative_to(root)).replace("\\", "/")
            name_l = p.name.lower()
            rel_l = rel.lower()
            if p.suffix.lower() not in INTERESTING_SUFFIXES and not KEYWORDS.search(name_l):
                if not KEYWORDS.search(rel_l):
                    continue
            if not KEYWORDS.search(rel_l) and p.suffix.lower() not in INTERESTING_SUFFIXES:
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            size = int(st.st_size)
            digest = ""
            notes = ""
            if size <= MAX_HASH_BYTES and p.suffix.lower() not in {".zip", ".parquet", ".npz", ".npy", ".pkl"}:
                try:
                    digest = sha256_file(p)
                except OSError as exc:
                    notes = f"hash_failed:{exc}"
            else:
                notes = "sha256_deferred_large_or_binary"
            seed_m = re.search(r"seed[_-]?(\d{4,6})", rel_l)
            method_m = re.search(
                r"(fedavg_window|fedasync_window|flamf_timealign_adapted|local_hajek|"
                r"twostage_hajek|inst_cal|debt_cal|raven_wo_\w+|raven_simoracle|raven|"
                r"central_all|central_delivered)",
                rel_l,
            )
            rows.append(
                {
                    "source_path": rel,
                    "type": p.suffix.lower().lstrip(".") or "file",
                    "size_bytes": size,
                    "mtime": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
                    "sha256": digest,
                    "inferred_round": _infer_round(rel),
                    "inferred_dataset": _infer_dataset(rel),
                    "inferred_method": method_m.group(1) if method_m else "",
                    "inferred_seed": seed_m.group(1) if seed_m else "",
                    "inferred_status": _infer_status(rel),
                    "candidate_layer": _candidate_layer(rel),
                    "notes": notes,
                }
            )
    # Always register critical sealed roots even if empty match edge-cases
    critical = [
        "artifacts/e2_traffic_formal_runs_r1",
        "artifacts/e2_traffic_formal_results_analysis_r1",
        "artifacts/e2_traffic_numerical_tolerance_and_final_claim_seal_r1",
        "artifacts/e2_traffic_offline_metric_reconstruction_r1",
        "artifacts/e3_formal_runs_r1",
        "artifacts/e3_final_evidence_provenance_and_wording_seal_r1",
        "artifacts/e3_formal_evidence_integrity_and_claim_closure_r1",
        "artifacts/e3_local_hajek_weight_and_p2_certificate_final_closure_r1",
        "artifacts/e4_wo_inst_reference_penalty_final_correction_r1",
        "artifacts/e4_ablation_semantic_integrity_repair_r1",
        "artifacts/e4_core_mechanism_ablation_r1",
        "outputs/statistics/E1_R2_FINAL_SEALED",
        "outputs/paper/E1_R2_FINAL",
        "outputs/aggregate/E1_R2",
    ]
    have = {r["source_path"] for r in rows}
    for c in critical:
        if c not in have and (root / c).exists():
            p = root / c
            st = p.stat()
            rows.append(
                {
                    "source_path": c,
                    "type": "dir" if p.is_dir() else p.suffix.lower().lstrip("."),
                    "size_bytes": int(st.st_size) if p.is_file() else 0,
                    "mtime": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
                    "sha256": sha256_file(p) if p.is_file() and st.st_size <= MAX_HASH_BYTES else "",
                    "inferred_round": _infer_round(c),
                    "inferred_dataset": _infer_dataset(c),
                    "inferred_method": "",
                    "inferred_seed": "",
                    "inferred_status": "VALID_CANDIDATE",
                    "candidate_layer": "PAPER_CORE",
                    "notes": "critical_root_registered",
                }
            )

    out_dir = Path(out_dir)
    write_csv(out_dir / "ALL_RELEVANT_SOURCE_PATHS.csv", rows)
    write_json(
        out_dir / "ALL_RELEVANT_SOURCE_PATHS.json",
        {
            "n_paths": len(rows),
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "paths": rows,
        },
    )
    return rows

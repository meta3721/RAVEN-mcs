"""ZIP packaging with a physical-member manifest and reopen verification."""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path
from typing import Any

from raven_mcs.paper_data_r1.io_util import write_csv, write_json

ZIP_NAME = "TO_SUBMIT_TDRIVE_REAL_MOBILITY_PROTOCOL_SEAL_R1.zip"

INCLUDE_PREFIXES = (
    "00_inventory/",
    "01_dataset/",
    "02_semantics/",
    "03_target/",
    "04_selection/",
    "05_split/",
    "06_eventtrace/",
    "07_methods/",
    "08_metrics/",
    "09_statistics/",
    "10_output/",
    "11_future_run_matrix/",
    "12_audits/",
    "13_freeze/",
    "14_diagnostics/",
)

ROOT_FILES = (
    "TDRIVE_REAL_MOBILITY_PROTOCOL_SEAL_R1_REPORT.md",
    "TDRIVE_PROTOCOL_GATES_R1.json",
)


def _members(out: Path) -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = []
    for p in out.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(out).as_posix()
        if rel.endswith(".zip"):
            continue
        if rel in {
            "TDRIVE_PROTOCOL_SEAL_R1_ZIP_MANIFEST.csv",
            "TDRIVE_PROTOCOL_SEAL_R1_ZIP_VERIFICATION.json",
        }:
            continue
        if rel in ROOT_FILES or any(rel.startswith(pref) for pref in INCLUDE_PREFIXES):
            files.append((p, rel))
    check = out.parent / "check_tdrive_real_mobility_protocol_seal_r1.py"
    if check.is_file():
        files.append((check, "check_tdrive_real_mobility_protocol_seal_r1.py"))
    files.sort(key=lambda x: x[1])
    return files


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def package_zip(root: Path, out: Path) -> dict[str, Any]:
    out = Path(out)
    root = Path(root)
    zip_path = out / ZIP_NAME
    if zip_path.exists():
        zip_path.unlink()
    members = _members(out)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src, arc in members:
            zf.write(src, arc)

    rows = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        for name in names:
            data = zf.read(name)
            rows.append({"relative_path": name, "size_bytes": len(data), "sha256": _sha256_bytes(data)})
    rows.sort(key=lambda r: r["relative_path"])
    write_csv(out / "TDRIVE_PROTOCOL_SEAL_R1_ZIP_MANIFEST.csv", rows)

    expected = {arc: src for src, arc in members}
    mismatches = []
    missing = []
    extra = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        znames = set(zf.namelist())
        for arc, src in expected.items():
            if arc not in znames:
                missing.append(arc)
                continue
            data = zf.read(arc)
            disk = src.read_bytes()
            if hashlib.sha256(data).digest() != hashlib.sha256(disk).digest():
                mismatches.append(arc)
        extra = sorted(znames - set(expected))
    verify = {
        "zip_path": str(zip_path.relative_to(root).as_posix()) if str(zip_path).startswith(str(root)) else str(zip_path),
        "n_members": len(rows),
        "n_expected": len(expected),
        "missing": missing,
        "extra": extra,
        "mismatches": mismatches,
        "pass": not missing and not mismatches,
        "reopened": True,
    }
    write_json(out / "TDRIVE_PROTOCOL_SEAL_R1_ZIP_VERIFICATION.json", verify)

    dest_dir = root / "deliverables"
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(zip_path, dest_dir / ZIP_NAME)
    shutil.copy2(out / "TDRIVE_PROTOCOL_SEAL_R1_ZIP_MANIFEST.csv", dest_dir / "TDRIVE_PROTOCOL_SEAL_R1_ZIP_MANIFEST.csv")
    return verify

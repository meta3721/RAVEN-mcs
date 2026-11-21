"""CORE and FULL ZIP packaging with physical manifests and reopen verify."""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path
from typing import Any

from raven_mcs.paper_data_r1.io_util import sha256_file, write_csv, write_json
from raven_mcs.final_paper_data_asset_freeze_r1.constants import CORE_PREFIXES, CORE_ROOT_FILES, CORE_ZIP, FULL_ZIP


def _iter_files(base: Path, prefixes: tuple[str, ...] | None) -> list[Path]:
    files = []
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(base).as_posix()
        if rel.endswith(".zip"):
            continue
        if "ZIP_MANIFEST.csv" in rel or "ZIP_VERIFICATION.json" in rel:
            continue
        if prefixes is None:
            files.append(p)
            continue
        if rel in CORE_ROOT_FILES or any(rel.startswith(pref) for pref in prefixes):
            files.append(p)
    return files


def _zip(path: Path, members: list[tuple[Path, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src, arc in sorted(members, key=lambda x: x[1]):
            zf.write(src, arc)


def _manifest(zip_path: Path) -> list[dict[str, Any]]:
    rows = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            data = zf.read(name)
            rows.append({"relative_path": name, "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    rows.sort(key=lambda r: r["relative_path"])
    return rows


def _verify(zip_path: Path, members: list[tuple[Path, str]]) -> dict[str, Any]:
    expected = {arc for _, arc in members}
    missing, mismatches, extra = [], [], []
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())
        extra = sorted(names - expected)
        for src, arc in members:
            if arc not in names:
                missing.append(arc)
                continue
            if hashlib.sha256(zf.read(arc)).digest() != hashlib.sha256(src.read_bytes()).digest():
                mismatches.append(arc)
    return {
        "zip": zip_path.name,
        "n_members": len(expected),
        "missing": missing,
        "mismatches": mismatches,
        "extra": extra,
        "pass": not missing and not mismatches,
        "reopened": True,
    }


def package(root: Path, out: Path) -> dict[str, Any]:
    out, root = Path(out), Path(root)
    deliverables = root / "deliverables"
    deliverables.mkdir(parents=True, exist_ok=True)
    check = root / "check_raven_final_paper_data_asset_freeze_r1.py"

    core_files = _iter_files(out, CORE_PREFIXES)
    core_members = [(p, p.relative_to(out).as_posix()) for p in core_files]
    if check.is_file():
        core_members.append((check, check.name))
    core_zip = out / CORE_ZIP
    _zip(core_zip, core_members)
    core_man = _manifest(core_zip)
    write_csv(out / "21_MANIFESTS/CORE_ZIP_MANIFEST.csv", core_man)
    core_ver = _verify(core_zip, core_members)
    write_json(out / "21_MANIFESTS/CORE_ZIP_VERIFICATION.json", core_ver)

    full_files = _iter_files(out, None)
    full_members = [(p, p.relative_to(out).as_posix()) for p in full_files]
    if check.is_file():
        full_members.append((check, check.name))
    full_zip = out / FULL_ZIP
    _zip(full_zip, full_members)
    full_man = _manifest(full_zip)
    write_csv(out / "21_MANIFESTS/FULL_ZIP_MANIFEST.csv", full_man)
    full_ver = _verify(full_zip, full_members)
    write_json(out / "21_MANIFESTS/FULL_ZIP_VERIFICATION.json", full_ver)

    shutil.copy2(core_zip, deliverables / CORE_ZIP)
    shutil.copy2(full_zip, deliverables / FULL_ZIP)
    shutil.copy2(out / "21_MANIFESTS/CORE_ZIP_MANIFEST.csv", deliverables / "RAVEN_MCS_FINAL_PAPER_DATA_CORE_R1_ZIP_MANIFEST.csv")
    shutil.copy2(out / "21_MANIFESTS/FULL_ZIP_MANIFEST.csv", deliverables / "RAVEN_MCS_FINAL_PAPER_DATA_FULL_R1_ZIP_MANIFEST.csv")
    return {
        "core_zip": str(core_zip),
        "full_zip": str(full_zip),
        "core_pass": core_ver["pass"],
        "full_pass": full_ver["pass"],
        "n_core": len(core_man),
        "n_full": len(full_man),
        "core_sha256": sha256_file(core_zip),
        "full_sha256": sha256_file(full_zip),
    }

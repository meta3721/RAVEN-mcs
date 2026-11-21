"""ZIP packaging: manifests generated from physical ZIP members after creation."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path
from typing import Any, Iterable

from .io_util import sha256_file, write_csv, write_json

CORE_PREFIXES = (
    "00_index/",
    "01_core_data/",
    "04_statistics/",
    "05_provenance/",
    "06_table_sources/",
    "07_figure_sources/",
    "08_tdrive_readiness/",
    "10_reports/",
)
FULL_PREFIXES = CORE_PREFIXES + (
    "02_supporting_data/",
    "03_raw_evidence/",
    "09_archive_manifest/",
)


def _iter_files(base: Path, prefixes: Iterable[str] | None = None) -> list[Path]:
    files: list[Path] = []
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(base).as_posix()
        if rel.startswith("_work/"):
            continue
        if rel.endswith(".zip"):
            continue
        if prefixes is not None and not any(rel.startswith(pref) for pref in prefixes):
            continue
        # FULL zip manifest is written AFTER the zip; exclude from zip members
        if rel in {
            "09_archive_manifest/FULL_R2_ZIP_MANIFEST.csv",
            "09_archive_manifest/CORE_R2_ZIP_MANIFEST.csv",
            "09_archive_manifest/FULL_EVIDENCE_ZIP_MANIFEST.csv",
            "09_archive_manifest/CORE_ZIP_MANIFEST.csv",
        }:
            continue
        files.append(p)
    return files


def _build_zip(zip_path: Path, members: list[tuple[Path, str]]) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src, arc in sorted(members, key=lambda x: x[1]):
            zf.write(src, arc)


def manifest_from_zip(zip_path: Path) -> list[dict[str, Any]]:
    rows = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            data = zf.read(name)
            rows.append(
                {
                    "relative_path": name,
                    "size_bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
            )
    rows.sort(key=lambda r: r["relative_path"])
    return rows


def verify_zip(zip_path: Path, manifest_rows: list[dict[str, Any]]) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())
        missing = []
        mismatch = []
        for row in manifest_rows:
            rel = row["relative_path"]
            if rel not in names:
                missing.append(rel)
                continue
            data = zf.read(rel)
            digest = hashlib.sha256(data).hexdigest()
            if digest != row["sha256"] or len(data) != int(row["size_bytes"]):
                mismatch.append({"path": rel, "expected": row["sha256"], "got": digest})
        extra = sorted(names - {r["relative_path"] for r in manifest_rows})
    return {
        "zip": str(zip_path),
        "n_manifest": len(manifest_rows),
        "missing": missing,
        "mismatch": mismatch,
        "extra": extra,
        "pass": len(missing) == 0 and len(mismatch) == 0 and len(extra) == 0,
    }


def package_all(paper: Path, deliverables: Path) -> dict[str, Any]:
    paper = Path(paper)
    deliverables = Path(deliverables)
    deliverables.mkdir(parents=True, exist_ok=True)
    man_dir = paper / "09_archive_manifest"
    man_dir.mkdir(parents=True, exist_ok=True)

    core_members = [(p, p.relative_to(paper).as_posix()) for p in _iter_files(paper, CORE_PREFIXES)]
    core_zip = deliverables / "RAVEN_MCS_PAPER_DATA_CORE_R2.zip"
    _build_zip(core_zip, core_members)
    core_manifest = manifest_from_zip(core_zip)
    write_csv(man_dir / "CORE_R2_ZIP_MANIFEST.csv", core_manifest)
    write_csv(man_dir / "CORE_ZIP_MANIFEST.csv", core_manifest)
    core_ver = verify_zip(core_zip, core_manifest)
    write_json(man_dir / "CORE_ZIP_VERIFICATION.json", core_ver)
    (paper / "RAVEN_MCS_PAPER_DATA_CORE_R2.zip").write_bytes(core_zip.read_bytes())

    full_members = [(p, p.relative_to(paper).as_posix()) for p in _iter_files(paper, FULL_PREFIXES)]
    # include CORE manifest in FULL (already on disk)
    full_zip = deliverables / "RAVEN_MCS_PAPER_DATA_FULL_EVIDENCE_R2.zip"
    _build_zip(full_zip, full_members)
    full_manifest = manifest_from_zip(full_zip)
    write_csv(man_dir / "FULL_R2_ZIP_MANIFEST.csv", full_manifest)
    write_csv(man_dir / "FULL_EVIDENCE_ZIP_MANIFEST.csv", full_manifest)
    full_ver = verify_zip(full_zip, full_manifest)
    write_json(man_dir / "FULL_ZIP_VERIFICATION.json", full_ver)
    write_json(man_dir / "FULL_EVIDENCE_ZIP_VERIFICATION.json", full_ver)
    (paper / "RAVEN_MCS_PAPER_DATA_FULL_EVIDENCE_R2.zip").write_bytes(full_zip.read_bytes())

    write_csv(
        man_dir / "EVENTTRACE_ARCHIVE_POLICY.csv",
        [{"policy": "hash_and_path_index_only", "optional_zip": "not generated"}],
    )
    write_csv(
        man_dir / "CHECKPOINT_ARCHIVE_POLICY.csv",
        [{"policy": "hash_and_path_index_only", "optional_zip": "not generated"}],
    )
    return {
        "core_zip": str(core_zip),
        "full_zip": str(full_zip),
        "core_verification": core_ver,
        "full_verification": full_ver,
        "n_core_members": len(core_manifest),
        "n_full_members": len(full_manifest),
        "core_sha256": sha256_file(core_zip),
        "full_sha256": sha256_file(full_zip),
    }

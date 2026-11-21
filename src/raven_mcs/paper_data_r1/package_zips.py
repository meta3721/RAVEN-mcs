"""ZIP packaging with reopen-verify manifests."""

from __future__ import annotations

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

FULL_PREFIXES = (
    "00_index/",
    "01_core_data/",
    "02_supporting_data/",
    "03_raw_evidence/",
    "04_statistics/",
    "05_provenance/",
    "06_table_sources/",
    "07_figure_sources/",
    "08_tdrive_readiness/",
    "09_archive_manifest/",
    "10_reports/",
)


def _iter_files(base: Path, prefixes: Iterable[str] | None = None) -> list[Path]:
    files: list[Path] = []
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(base).as_posix()
        if prefixes is not None and not any(rel.startswith(pref) for pref in prefixes):
            continue
        # Skip previous zips inside paper_ready
        if rel.endswith(".zip"):
            continue
        files.append(p)
    return files


def _build_zip(zip_path: Path, root_files: list[tuple[Path, str]]) -> list[dict[str, Any]]:
    zip_path = Path(zip_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists():
        zip_path.unlink()
    rows: list[dict[str, Any]] = []
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src, arcname in sorted(root_files, key=lambda x: x[1]):
            zf.write(src, arcname)
            rows.append(
                {
                    "relative_path": arcname,
                    "size_bytes": src.stat().st_size,
                    "sha256": sha256_file(src),
                }
            )
    return rows


def verify_zip(zip_path: Path, manifest_rows: list[dict[str, Any]]) -> dict[str, Any]:
    zip_path = Path(zip_path)
    missing = []
    mismatch = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())
        for row in manifest_rows:
            rel = row["relative_path"]
            if rel not in names:
                missing.append(rel)
                continue
            data = zf.read(rel)
            digest = __import__("hashlib").sha256(data).hexdigest()
            if digest != row["sha256"]:
                mismatch.append({"path": rel, "expected": row["sha256"], "got": digest})
            if len(data) != int(row["size_bytes"]):
                mismatch.append(
                    {
                        "path": rel,
                        "size_expected": row["size_bytes"],
                        "size_got": len(data),
                    }
                )
        extra = sorted(names - {r["relative_path"] for r in manifest_rows})
    return {
        "zip": str(zip_path),
        "n_manifest": len(manifest_rows),
        "missing": missing,
        "mismatch": mismatch,
        "extra": extra,
        "pass": len(missing) == 0 and len(mismatch) == 0,
    }


def package_all(paper: Path, deliverables: Path) -> dict[str, Any]:
    paper = Path(paper)
    deliverables = Path(deliverables)
    deliverables.mkdir(parents=True, exist_ok=True)
    manifest_dir = paper / "09_archive_manifest"
    manifest_dir.mkdir(parents=True, exist_ok=True)

    # CORE
    core_files = []
    for p in _iter_files(paper, CORE_PREFIXES):
        rel = p.relative_to(paper).as_posix()
        core_files.append((p, rel))
    core_zip = deliverables / "RAVEN_MCS_PAPER_DATA_CORE_R1.zip"
    core_manifest = _build_zip(core_zip, core_files)
    # also copy zip into paper root
    core_zip_paper = paper / "RAVEN_MCS_PAPER_DATA_CORE_R1.zip"
    if core_zip_paper.exists():
        core_zip_paper.unlink()
    core_zip_paper.write_bytes(core_zip.read_bytes())
    write_csv(manifest_dir / "CORE_ZIP_MANIFEST.csv", core_manifest)
    core_ver = verify_zip(core_zip, core_manifest)
    write_json(manifest_dir / "CORE_ZIP_VERIFICATION.json", core_ver)

    # FULL
    full_files = []
    for p in _iter_files(paper, FULL_PREFIXES):
        rel = p.relative_to(paper).as_posix()
        # avoid packaging the core zip itself if present under paper
        full_files.append((p, rel))
    full_zip = deliverables / "RAVEN_MCS_PAPER_DATA_FULL_EVIDENCE_R1.zip"
    full_manifest = _build_zip(full_zip, full_files)
    full_zip_paper = paper / "RAVEN_MCS_PAPER_DATA_FULL_EVIDENCE_R1.zip"
    if full_zip_paper.exists():
        full_zip_paper.unlink()
    full_zip_paper.write_bytes(full_zip.read_bytes())
    write_csv(manifest_dir / "FULL_EVIDENCE_ZIP_MANIFEST.csv", full_manifest)
    full_ver = verify_zip(full_zip, full_manifest)
    write_json(manifest_dir / "FULL_EVIDENCE_ZIP_VERIFICATION.json", full_ver)

    # EventTrace / checkpoint archives: hash+path index already in provenance; optional empty marker
    write_csv(
        manifest_dir / "EVENTTRACE_ARCHIVE_POLICY.csv",
        [
            {
                "policy": "hash_and_path_index_only",
                "reason": "EventTraces bulky; hashes preserved in E2_EVENTTRACE_INDEX_120 and E3/E4 provenance",
                "optional_zip": "RAVEN_MCS_EVENTTRACE_ARCHIVE_R1.zip not generated",
            }
        ],
    )
    write_csv(
        manifest_dir / "CHECKPOINT_ARCHIVE_POLICY.csv",
        [
            {
                "policy": "hash_and_path_index_only",
                "reason": "Checkpoints bulky; inventory retained in sealed artifact roots",
                "optional_zip": "RAVEN_MCS_CHECKPOINT_ARCHIVE_R1.zip not generated",
            }
        ],
    )

    return {
        "core_zip": str(core_zip),
        "full_zip": str(full_zip),
        "core_verification": core_ver,
        "full_verification": full_ver,
        "n_core_members": len(core_manifest),
        "n_full_members": len(full_manifest),
    }

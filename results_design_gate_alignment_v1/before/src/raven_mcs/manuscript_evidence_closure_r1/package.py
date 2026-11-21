"""ZIP with physical-member manifest and reopen verification."""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path
from typing import Any

from raven_mcs.paper_data_r1.io_util import write_csv, write_json

ZIP_NAME = "TO_SUBMIT_RAVEN_MCS_MANUSCRIPT_EVIDENCE_CLOSURE_R1.zip"
PREFIXES = (
    "00_audit/",
    "01_table_sources/",
    "02_tables/",
    "03_figure_sources/",
    "04_figures/",
    "05_results/",
    "06_discussion/",
    "07_claim_alignment/",
    "08_provenance/",
    "09_tdrive_decision/",
    "10_report/",
)
ROOT_FILES = (
    "RAVEN_MCS_MANUSCRIPT_EVIDENCE_CLOSURE_R1_REPORT.md",
    "MANUSCRIPT_EVIDENCE_GATES_R1.json",
)


def package_zip(root: Path, out: Path) -> dict[str, Any]:
    out, root = Path(out), Path(root)
    members = []
    for p in out.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(out).as_posix()
        if rel.endswith(".zip") or rel.endswith("ZIP_MANIFEST.csv") or rel.endswith("ZIP_VERIFICATION.json"):
            continue
        if rel in ROOT_FILES or any(rel.startswith(pref) for pref in PREFIXES):
            members.append((p, rel))
    check = root / "check_raven_manuscript_evidence_closure_r1.py"
    if check.is_file():
        members.append((check, check.name))
    members.sort(key=lambda x: x[1])
    zip_path = out / ZIP_NAME
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src, arc in members:
            zf.write(src, arc)
    rows = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            data = zf.read(name)
            rows.append({"relative_path": name, "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    rows.sort(key=lambda r: r["relative_path"])
    write_csv(out / "RAVEN_MCS_MANUSCRIPT_EVIDENCE_CLOSURE_R1_ZIP_MANIFEST.csv", rows)
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
    verify = {
        "n_members": len(rows),
        "missing": missing,
        "extra": extra,
        "mismatches": mismatches,
        "pass": not missing and not mismatches,
        "reopened": True,
        "zip_path": "manuscript_evidence_closure_r1/" + ZIP_NAME,
    }
    write_json(out / "RAVEN_MCS_MANUSCRIPT_EVIDENCE_CLOSURE_R1_ZIP_VERIFICATION.json", verify)
    dest = root / "deliverables"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(zip_path, dest / ZIP_NAME)
    shutil.copy2(out / "RAVEN_MCS_MANUSCRIPT_EVIDENCE_CLOSURE_R1_ZIP_MANIFEST.csv", dest / "RAVEN_MCS_MANUSCRIPT_EVIDENCE_CLOSURE_R1_ZIP_MANIFEST.csv")
    return verify

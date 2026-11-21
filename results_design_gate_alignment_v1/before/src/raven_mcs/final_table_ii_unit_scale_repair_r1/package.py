"""ZIP the Table II repair tree."""

from __future__ import annotations

import hashlib
import shutil
import zipfile
from pathlib import Path
from typing import Any

from raven_mcs.paper_data_r1.io_util import sha256_file, write_csv, write_json
from raven_mcs.final_table_ii_unit_scale_repair_r1.constants import ZIP_NAME


def package(root: Path, out: Path) -> dict[str, Any]:
    root, out = Path(root), Path(out)
    skip = {ZIP_NAME, "TABLEII_REPAIR_R1_ZIP_MANIFEST.csv", "TABLEII_REPAIR_R1_ZIP_VERIFICATION.json"}
    files = [p for p in out.rglob("*") if p.is_file() and p.name not in skip and p.suffix.lower() != ".zip"]
    members = [(p, p.relative_to(out).as_posix()) for p in files]
    zip_path = out / ZIP_NAME
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for src, arc in sorted(members, key=lambda x: x[1]):
            zf.write(src, arc)
    rows, missing, mismatches = [], [], []
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())
        expected = {arc for _, arc in members}
        for src, arc in members:
            data = zf.read(arc) if arc in names else b""
            digest = hashlib.sha256(data).hexdigest()
            rows.append({"relative_path": arc, "size_bytes": len(data), "sha256": digest})
            if arc not in names:
                missing.append(arc)
            elif hashlib.sha256(src.read_bytes()).hexdigest() != digest:
                mismatches.append(arc)
        extra = sorted(names - expected)
    rows.sort(key=lambda r: r["relative_path"])
    write_csv(out / "07_REPORT/TABLEII_REPAIR_R1_ZIP_MANIFEST.csv", rows)
    ver = {
        "zip": ZIP_NAME,
        "n_members": len(rows),
        "missing": missing,
        "mismatches": mismatches,
        "extra": extra,
        "pass": not missing and not mismatches,
        "reopened": True,
        "sha256": sha256_file(zip_path),
    }
    write_json(out / "07_REPORT/TABLEII_REPAIR_R1_ZIP_VERIFICATION.json", ver)
    deliverables = root / "deliverables"
    deliverables.mkdir(parents=True, exist_ok=True)
    shutil.copy2(zip_path, deliverables / ZIP_NAME)
    shutil.copy2(zip_path, root / ZIP_NAME)
    return {"zip": ZIP_NAME, "pass": ver["pass"], "n_members": ver["n_members"], "sha256": ver["sha256"]}

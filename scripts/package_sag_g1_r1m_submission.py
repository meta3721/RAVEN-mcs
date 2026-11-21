"""Package R1m aggregate certificate formal implementation into deliverables/."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_NAME = "TO_SUBMIT_SAG_G1_R1M_AGGREGATE_CERTIFICATE_FORMAL_IMPLEMENTATION"
STAGING = ROOT / "deliverables" / PKG_NAME
ZIP_PATH = ROOT / "deliverables" / f"{PKG_NAME}.zip"
R1M = ROOT / "results_sag_g1" / "round_r1m"
SKIP = {".DS_Store", "Thumbs.db"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel_files(root: Path) -> list[Path]:
    return [p for p in sorted(root.rglob("*")) if p.is_file() and p.name not in SKIP]


def main() -> None:
    if not R1M.is_dir():
        raise SystemExit(f"missing {R1M}")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    shutil.copytree(R1M, STAGING / "round_r1m", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *SKIP))
    verdict = json.loads((R1M / "summary" / "R1M_VERDICT.json").read_text(encoding="utf-8"))
    report = R1M / "summary" / "RAVEN_MCS_R1M_AGGREGATE_CERTIFICATE_FORMAL_AUDIT_REPORT.md"
    (STAGING / "report").mkdir(parents=True, exist_ok=True)
    if report.is_file():
        shutil.copy2(report, STAGING / "report" / report.name)
    summary = [
        "# SAG G1-R1m Aggregate Certificate Formal Implementation",
        "",
        f"UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Verdict",
        "",
        f"**{verdict.get('executive_verdict')}**",
        "",
        f"- PRIMARY_USABLE (SensorScope a=0.40): {verdict.get('primary_usable')}",
        f"- SECONDARY_SAFE (U-Air a=0.20): {verdict.get('secondary_safe')}",
        "- Method: `raven_mcs` → `gate_mode=aggregate_coverage`.",
        "- Predictor: AGGREGATE_COVERAGE_RIDGE_V1, ridge_alpha=1.0.",
        "- RESET: MISCOVERAGE_TRIGGERED_RESET_V1 only.",
        "- SAG not started. 5-seed not started.",
        "",
        "## Read order",
        "",
        "1. `report/RAVEN_MCS_R1M_AGGREGATE_CERTIFICATE_FORMAL_AUDIT_REPORT.md`",
        "2. `round_r1m/gates/R1M_GATE_REPORT.md`",
        "3. `round_r1m/primary/R1M_SENSORSCOPE_A040_PRIMARY_SUMMARY.md`",
        "4. `round_r1m/secondary/R1M_UAIR_A020_SECONDARY_SUMMARY.md`",
        "5. `round_r1m/figures/`",
        "",
        "STOP: do not start SAG this round even if READY_FOR_SAG_*.",
        "",
    ]
    (STAGING / "report" / "R1M_SUBMISSION_SUMMARY.md").write_text("\n".join(summary), encoding="utf-8")
    files = [p for p in rel_files(STAGING) if p.name not in {"MANIFEST.json", "SHA256SUMS.txt"}]
    lines, records = [], []
    for p in files:
        rel = p.relative_to(STAGING).as_posix()
        digest = sha256_file(p)
        records.append({"path": rel, "bytes": p.stat().st_size, "sha256": digest})
        lines.append(f"{digest}  {rel}")
    (STAGING / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (STAGING / "MANIFEST.json").write_text(
        json.dumps(
            {
                "package": PKG_NAME,
                "generated_utc": datetime.now(timezone.utc).isoformat(),
                "executive_verdict": verdict.get("executive_verdict"),
                "sag_started": False,
                "five_seed_started": False,
                "n_files": len(records),
                "files": records,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in rel_files(STAGING):
            zf.write(p, p.relative_to(STAGING).as_posix())
    print(json.dumps({"zip": str(ZIP_PATH), "sha256": sha256_file(ZIP_PATH), "verdict": verdict.get("executive_verdict")}, indent=2))


if __name__ == "__main__":
    main()

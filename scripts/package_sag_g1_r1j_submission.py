"""Package SAG G1-R1j evidence into deliverables/."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_NAME = "TO_SUBMIT_SAG_G1_R1J_DYNAMIC_COV_STRESS_AUDIT"
STAGING = ROOT / "deliverables" / PKG_NAME
ZIP_PATH = ROOT / "deliverables" / f"{PKG_NAME}.zip"
R1J = ROOT / "results_sag_g1" / "round_r1j"
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
    if not R1J.is_dir():
        raise SystemExit(f"missing {R1J}")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    shutil.copytree(R1J, STAGING / "round_r1j", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *SKIP))
    verdict = json.loads((R1J / "summary" / "R1J_VERDICT.json").read_text(encoding="utf-8"))
    report = R1J / "summary" / "RAVEN_MCS_SAG_G1_R1J_DYNAMIC_COV_STRESS_AUDIT_REPORT.md"
    (STAGING / "report").mkdir(parents=True, exist_ok=True)
    if report.is_file():
        shutil.copy2(report, STAGING / "report" / report.name)
    summary = [
        "# SAG G1-R1j 实验提交摘要（给老师）",
        "",
        f"生成时间（UTC）：{datetime.now(timezone.utc).isoformat()}",
        "",
        "## 裁决",
        "",
        f"**{verdict.get('executive_verdict')}**",
        "",
        f"- SensorScope: `{verdict.get('sensorscope')}`",
        f"- U-Air: `{verdict.get('uair')}`",
        "- R1i oracle / stress grid / mask / target / pi_safe / tau / delta 未改。",
        "- 未 post-hoc 调 predictor / calibration / stress。",
        "- 未跑 SAG / 5-seed。",
        "",
        "## 建议阅读顺序",
        "",
        "1. `report/RAVEN_MCS_SAG_G1_R1J_DYNAMIC_COV_STRESS_AUDIT_REPORT.md`",
        "2. `round_r1j/boundary_eval/R1J_SENSORSCOPE_A040_BOUNDARY_SUMMARY.md`",
        "3. `round_r1j/boundary_eval/R1J_UAIR_A020_BOUNDARY_SUMMARY.md`",
        "4. `round_r1j/gate_eval/R1J_GATE_METRICS.csv`",
        "5. `round_r1j/figures/R1J_ORACLE_VS_DYNAMIC_COV_SCATTER.png`",
        "",
        "STOP：即使 READY_FOR_SAG 也不得本轮启动 SAG。",
        "",
    ]
    (STAGING / "report" / "R1J_SUBMISSION_SUMMARY_CN.md").write_text("\n".join(summary), encoding="utf-8")
    files = [p for p in rel_files(STAGING) if p.name not in {"MANIFEST.json", "SHA256SUMS.txt"}]
    lines = []
    records = []
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
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "executive_verdict": verdict.get("executive_verdict"),
                "sensorscope": verdict.get("sensorscope"),
                "uair": verdict.get("uair"),
                "n_files": len(records) + 2,
                "files": records,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in rel_files(STAGING):
            zf.write(p, arcname=f"{PKG_NAME}/{p.relative_to(STAGING).as_posix()}")
    verify = {
        "zip": ZIP_PATH.name,
        "zip_bytes": ZIP_PATH.stat().st_size,
        "zip_sha256": sha256_file(ZIP_PATH),
        "executive_verdict": verdict.get("executive_verdict"),
        "sensorscope": verdict.get("sensorscope"),
        "uair": verdict.get("uair"),
    }
    (ROOT / "deliverables" / f"{PKG_NAME}_ZIP_VERIFICATION.json").write_text(
        json.dumps(verify, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(verify, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

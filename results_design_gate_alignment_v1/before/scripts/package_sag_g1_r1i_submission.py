"""Package SAG G1-R1i evidence into deliverables/."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_NAME = "TO_SUBMIT_SAG_G1_R1I_EXOGENOUS_COVERAGE_STRESS_ORACLE"
STAGING = ROOT / "deliverables" / PKG_NAME
ZIP_PATH = ROOT / "deliverables" / f"{PKG_NAME}.zip"
R1I = ROOT / "results_sag_g1" / "round_r1i"
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
    if not R1I.is_dir():
        raise SystemExit(f"missing {R1I}")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    shutil.copytree(R1I, STAGING / "round_r1i", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *SKIP))
    verdict = json.loads((R1I / "summary" / "R1I_VERDICT.json").read_text(encoding="utf-8"))
    report = R1I / "summary" / "RAVEN_MCS_SAG_G1_R1I_EXOGENOUS_COVERAGE_STRESS_ORACLE_REPORT.md"
    (STAGING / "report").mkdir(parents=True, exist_ok=True)
    if report.is_file():
        shutil.copy2(report, STAGING / "report" / report.name)
    by_ds = verdict.get("by_dataset") or {}
    summary = [
        "# SAG G1-R1i 实验提交摘要（给老师）",
        "",
        f"生成时间（UTC）：{datetime.now(timezone.utc).isoformat()}",
        "",
        "## 裁决",
        "",
        f"**{verdict.get('executive_verdict')}**",
        "",
        f"- SensorScope: `{by_ds.get('sensorscope')}`",
        f"- U-Air: `{by_ds.get('uair')}`",
        f"- a=1.00 复现 natural: `{verdict.get('baseline_ok')}`",
        f"- nested monotonicity: `{verdict.get('monotonicity_ok')}` violations={verdict.get('n_mono_violations')}",
        "- tau_cov / target law / pi_safe / E3-v2 natural track 未改。",
        "- 未跑 predictor / calibration / dynamic C_cov / SAG / 5-seed。",
        "- 本轮未根据 crossing 补 stress level。",
        "",
        "## 两条 track 必须分开",
        "",
        "- Natural E3-v2：真实 deployment / natural-regime evaluation。",
        "- Controlled availability stress：coverage-boundary mechanism evaluation。",
        "- 禁止把 stress 写成“真实自然 deployment 的主要结果”。",
        "",
        "## 建议阅读顺序",
        "",
        "1. `report/RAVEN_MCS_SAG_G1_R1I_EXOGENOUS_COVERAGE_STRESS_ORACLE_REPORT.md`",
        "2. `round_r1i/stress_spec/R1I_STRESS_LEVEL_FREEZE.md`",
        "3. `round_r1i/oracle_stress/R1I_ORACLE_STRESS_SUMMARY.csv`",
        "4. `round_r1i/boundary_analysis/R1I_DATASET_VERDICTS.json`",
        "5. `round_r1i/figures/R1I_ORACLE_STRESS_CURVES.png`",
        "",
        "STOP：不得自动进入 dynamic certificate / SAG / 5-seed。",
        "",
    ]
    (STAGING / "report" / "R1I_SUBMISSION_SUMMARY_CN.md").write_text("\n".join(summary), encoding="utf-8")
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
                "by_dataset": by_ds,
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
        "by_dataset": by_ds,
    }
    (ROOT / "deliverables" / f"{PKG_NAME}_ZIP_VERIFICATION.json").write_text(
        json.dumps(verify, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(verify, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Package SAG G1-R1g evidence into deliverables/."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_NAME = "TO_SUBMIT_SAG_G1_R1G_E3V1_ROOTCAUSE_E3V2_SPEC"
STAGING = ROOT / "deliverables" / PKG_NAME
ZIP_PATH = ROOT / "deliverables" / f"{PKG_NAME}.zip"
R1G = ROOT / "results_sag_g1" / "round_r1g"
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
    if not R1G.is_dir():
        raise SystemExit(f"missing {R1G}")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    shutil.copytree(R1G, STAGING / "round_r1g", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *SKIP))
    verdict = json.loads((R1G / "summary" / "R1G_VERDICT.json").read_text(encoding="utf-8"))
    report = R1G / "summary" / "RAVEN_MCS_SAG_G1_R1G_E3_PROTOCOL_ROOT_CAUSE_AND_V2_SPEC_REPORT.md"
    if report.is_file():
        (STAGING / "report").mkdir(parents=True, exist_ok=True)
        shutil.copy2(report, STAGING / "report" / report.name)
    routing = verdict.get("e3v2_routing") or {}
    rc = verdict.get("root_cause") or {}
    summary = [
        "# SAG G1-R1g 实验提交摘要（给老师）",
        "",
        f"生成时间（UTC）：{datetime.now(timezone.utc).isoformat()}",
        "",
        "## 裁决",
        "",
        f"**{verdict.get('executive_verdict')}**",
        "",
        f"- E3-v1 root cause: `{rc.get('primary')}` codes={rc.get('codes')}",
        f"- E3-v2 routing: SensorScope={routing.get('sensorscope')} U-Air={routing.get('uair')}",
        "- tau_cov / target law / pi_safe 未改；未跑 SAG / 5-seed / predictor repair。",
        "",
        "## 建议阅读顺序",
        "",
        "1. `report/RAVEN_MCS_SAG_G1_R1G_E3_PROTOCOL_ROOT_CAUSE_AND_V2_SPEC_REPORT.md`",
        "2. `round_r1g/e3v1_root_cause/E3V1_ROOT_CAUSE_ATTRIBUTION.md`",
        "3. `round_r1g/e3v2_spec/E3V2_WINDOW_RULE_FREEZE.md`",
        "4. `round_r1g/e3v2_oracle_precheck/E3V2_ORACLE_PRECHECK_SUMMARY.csv`",
        "",
        "STOP：不得自动进入 dynamic certificate / SAG。",
        "",
    ]
    (STAGING / "report").mkdir(parents=True, exist_ok=True)
    (STAGING / "report" / "R1G_SUBMISSION_SUMMARY_CN.md").write_text("\n".join(summary), encoding="utf-8")
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
                "e3v2_routing": routing,
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
    }
    (ROOT / "deliverables" / f"{PKG_NAME}_ZIP_VERIFICATION.json").write_text(
        json.dumps(verify, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(verify, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

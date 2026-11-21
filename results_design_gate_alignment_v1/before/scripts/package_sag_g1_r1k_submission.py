"""Package SAG G1-R1k evidence into deliverables/."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_NAME = "TO_SUBMIT_SAG_G1_R1K_CERTIFICATE_ARCHITECTURE_AUDIT"
STAGING = ROOT / "deliverables" / PKG_NAME
ZIP_PATH = ROOT / "deliverables" / f"{PKG_NAME}.zip"
R1K = ROOT / "results_sag_g1" / "round_r1k"
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
    if not R1K.is_dir():
        raise SystemExit(f"missing {R1K}")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    shutil.copytree(R1K, STAGING / "round_r1k", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *SKIP))
    verdict = json.loads((R1K / "summary" / "R1K_VERDICT.json").read_text(encoding="utf-8"))
    report = R1K / "summary" / "RAVEN_MCS_SAG_G1_R1K_CERTIFICATE_ARCHITECTURE_AUDIT_REPORT.md"
    (STAGING / "report").mkdir(parents=True, exist_ok=True)
    if report.is_file():
        shutil.copy2(report, STAGING / "report" / report.name)
    summary = [
        "# SAG G1-R1k 实验提交摘要（给老师）",
        "",
        f"生成时间（UTC）：{datetime.now(timezone.utc).isoformat()}",
        "",
        "## 裁决",
        "",
        f"**{verdict.get('executive_verdict')}**",
        "",
        f"- Pairwise barrier: `{verdict.get('pairwise_barrier')}`",
        f"- Scale: `{verdict.get('scale')}`",
        f"- Aggregate: `{verdict.get('aggregate')}`",
        f"- Theory decision: `{verdict.get('theory_decision')}`",
        "- 未改论文 / 未跑 SAG / 5-seed / 未改 stress/tau/pi_safe。",
        "- Aggregate 只是 feasibility candidate，不是正式方法替换。",
        "",
        "## 建议阅读顺序",
        "",
        "1. `report/RAVEN_MCS_SAG_G1_R1K_CERTIFICATE_ARCHITECTURE_AUDIT_REPORT.md`",
        "2. `round_r1k/pairwise_barrier/PAIRWISE_POSITIVE_LCB_BARRIER_DERIVATION.md`",
        "3. `round_r1k/theory_boundary/R1K_THEORY_CHANGE_DECISION.md`",
        "4. `round_r1k/aggregate_eval/R1K_SENSOR_A040_ARCHITECTURE_SUMMARY.md`",
        "5. `round_r1k/figures/R1K_PAIRWISE_VS_AGGREGATE_GATE.png`",
        "",
        "STOP：即使 aggregate 可行，本轮也不得启动 SAG；下一步是理论层确认。",
        "",
    ]
    (STAGING / "report" / "R1K_SUBMISSION_SUMMARY_CN.md").write_text("\n".join(summary), encoding="utf-8")
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
                "pairwise_barrier": verdict.get("pairwise_barrier"),
                "aggregate": verdict.get("aggregate"),
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
        "pairwise_barrier": verdict.get("pairwise_barrier"),
        "aggregate": verdict.get("aggregate"),
    }
    (ROOT / "deliverables" / f"{PKG_NAME}_ZIP_VERIFICATION.json").write_text(
        json.dumps(verify, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(verify, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

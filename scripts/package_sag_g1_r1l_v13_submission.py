"""Package R1l-v1.3 canonical alias + source closure into deliverables/."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_NAME = "TO_SUBMIT_SAG_G1_R1L_V13_CANONICAL_ALIAS_SOURCE_CLOSURE"
STAGING = ROOT / "deliverables" / PKG_NAME
ZIP_PATH = ROOT / "deliverables" / f"{PKG_NAME}.zip"
R1L = ROOT / "results_sag_g1" / "round_r1l_v13"
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
    if not R1L.is_dir():
        raise SystemExit(f"missing {R1L}")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    shutil.copytree(R1L, STAGING / "round_r1l_v13", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *SKIP))
    verdict = json.loads((R1L / "summary" / "R1L_V13_VERDICT.json").read_text(encoding="utf-8"))
    report = R1L / "summary" / "RAVEN_MCS_R1L_V13_CANONICAL_ALIAS_SOURCE_CLOSURE_REPORT.md"
    (STAGING / "report").mkdir(parents=True, exist_ok=True)
    if report.is_file():
        shutil.copy2(report, STAGING / "report" / report.name)
    summary = [
        "# SAG G1-R1l-v1.3 Canonical method alias + source closure（给老师）",
        "",
        f"生成时间（UTC）：{datetime.now(timezone.utc).isoformat()}",
        "",
        "## 裁决",
        "",
        f"**{verdict.get('executive_verdict')}**",
        "",
        "- 正式 paper method key：`raven_mcs` → `gate_mode=aggregate_coverage`。",
        "- `raven_mcs_formal` 仅为内部 alias，不再作为 paper-facing 唯一名。",
        "- Legacy always-on 明确为 `raven_legacy_always_on`（历史 `raven` 仍 legacy_only）。",
        "- Source snapshot 含 `certificates.py` 与 formal routing 传递依赖。",
        "- 无新实验 / R1m / SAG / 5-seed。R1l 系列到此停止。",
        "",
        "## 建议阅读顺序",
        "",
        "1. `report/RAVEN_MCS_R1L_V13_CANONICAL_ALIAS_SOURCE_CLOSURE_REPORT.md`",
        "2. `round_r1l_v13/interface/R1L_V13_FORMAL_EXECUTION_CHAIN.md`",
        "3. `round_r1l_v13/interface/R1L_V13_METHOD_RESOLUTION_TABLE.csv`",
        "4. `round_r1l_v13/audit/R1L_V13_TRANSITIVE_SOURCE_CLOSURE.csv`",
        "",
        "STOP：即使 THEORY_CLOSURE_PASS 也不得本轮启动 R1m/SAG。",
        "",
    ]
    (STAGING / "report" / "R1L_V13_SUBMISSION_SUMMARY_CN.md").write_text("\n".join(summary), encoding="utf-8")
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
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "executive_verdict": verdict.get("executive_verdict"),
                "n_min": verdict.get("n_min"),
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
        "n_min": verdict.get("n_min"),
    }
    (ROOT / "deliverables" / f"{PKG_NAME}_ZIP_VERIFICATION.json").write_text(
        json.dumps(verify, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(verify, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

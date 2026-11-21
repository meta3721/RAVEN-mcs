"""Package R1l-v1.1 final theory patch into deliverables/."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_NAME = "TO_SUBMIT_SAG_G1_R1L_V11_FINAL_THEORY_PATCH"
STAGING = ROOT / "deliverables" / PKG_NAME
ZIP_PATH = ROOT / "deliverables" / f"{PKG_NAME}.zip"
R1L = ROOT / "results_sag_g1" / "round_r1l_v11"
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
    shutil.copytree(R1L, STAGING / "round_r1l_v11", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *SKIP))
    verdict = json.loads((R1L / "summary" / "R1L_V11_VERDICT.json").read_text(encoding="utf-8"))
    report = R1L / "summary" / "RAVEN_MCS_R1L_V11_FINAL_THEORY_PATCH_REPORT.md"
    (STAGING / "report").mkdir(parents=True, exist_ok=True)
    if report.is_file():
        shutil.copy2(report, STAGING / "report" / report.name)
    summary = [
        "# SAG G1-R1l-v1.1 最终理论补丁（给老师）",
        "",
        f"生成时间（UTC）：{datetime.now(timezone.utc).isoformat()}",
        "",
        "## 裁决",
        "",
        f"**{verdict.get('executive_verdict')}**",
        "",
        "- 本轮只做理论补丁，没有新实验 / R1m / SAG / 5-seed。",
        "- P0-1：Theorem 1 ties 改为 randomized rank + 正确事件包含。",
        "- P0-2：availability corollary 收窄到 designated entity 必要条件。",
        "- P0-3：CERTIFIED 不证明 exchangeability；Theorem 1 仍 conditional on A。",
        "- P1-1：certified block 内冻结 predictor snapshot，仅 RESET 后 refit。",
        "- P1-2：gate evidence 全部是 round_r1l_v11/ 包内相对路径。",
        "- P1-3：Section VII 标记为 LEGACY / PRE-R1m，未改旧实验数字。",
        "",
        "## 建议阅读顺序",
        "",
        "1. `report/RAVEN_MCS_R1L_V11_FINAL_THEORY_PATCH_REPORT.md`",
        "2. `round_r1l_v11/summary/R1L_V11_GATE_REPORT.md`",
        "3. `round_r1l_v11/proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md`",
        "4. `round_r1l_v11/proofs/COROLLARY1_AVAILABILITY_BARRIER.md`",
        "",
        "STOP：即使 THEORY_CLOSURE_PASS 也不得本轮启动 R1m/SAG。",
        "",
    ]
    (STAGING / "report" / "R1L_V11_SUBMISSION_SUMMARY_CN.md").write_text("\n".join(summary), encoding="utf-8")
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

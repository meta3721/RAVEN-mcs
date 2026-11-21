"""Package SAG G1-R1h evidence into deliverables/."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_NAME = "TO_SUBMIT_SAG_G1_R1H_MATCHED_ROOTCAUSE_BOUNDARY_AUDIT"
STAGING = ROOT / "deliverables" / PKG_NAME
ZIP_PATH = ROOT / "deliverables" / f"{PKG_NAME}.zip"
R1H = ROOT / "results_sag_g1" / "round_r1h"
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
    if not R1H.is_dir():
        raise SystemExit(f"missing {R1H}")
    if STAGING.exists():
        shutil.rmtree(STAGING)
    shutil.copytree(R1H, STAGING / "round_r1h", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *SKIP))
    verdict = json.loads((R1H / "summary" / "R1H_VERDICT.json").read_text(encoding="utf-8"))
    causal = json.loads((R1H / "matched_counterfactual" / "CFM1_ROOT_CAUSE_VERDICT.json").read_text(encoding="utf-8"))
    boundary = json.loads((R1H / "boundary_audit" / "E3V2_BOUNDARY_REPRESENTATIVENESS_VERDICT.json").read_text(encoding="utf-8"))
    report = R1H / "summary" / "RAVEN_MCS_SAG_G1_R1H_MATCHED_ROOTCAUSE_BOUNDARY_AUDIT_REPORT.md"
    (STAGING / "report").mkdir(parents=True, exist_ok=True)
    if report.is_file():
        shutil.copy2(report, STAGING / "report" / report.name)
    summary = [
        "# SAG G1-R1h 实验提交摘要（给老师）",
        "",
        f"生成时间（UTC）：{datetime.now(timezone.utc).isoformat()}",
        "",
        "## 裁决",
        "",
        f"**{verdict.get('executive_verdict')}**",
        "",
        f"- CF-M1 causal: `{causal.get('verdict')}`",
        f"- sampling_caused_ceiling_strict: `{causal.get('sampling_caused_ceiling_strict')}`",
        f"- E3-v2 boundary: `{boundary.get('verdict')}`",
        f"- U-Air unsafe: n={boundary.get('uair_n_unsafe')} complete={boundary.get('uair_unsafe_complete')} "
        f"partial={boundary.get('uair_unsafe_partial')} interior_unsafe={boundary.get('uair_interior_unsafe')}",
        "- tau_cov / target law / pi_safe 未改；未跑 SAG / 5-seed / predictor repair / coverage stress。",
        "",
        "## 建议阅读顺序",
        "",
        "1. `report/RAVEN_MCS_SAG_G1_R1H_MATCHED_ROOTCAUSE_BOUNDARY_AUDIT_REPORT.md`",
        "2. `round_r1h/matched_counterfactual/CFM1_ROOT_CAUSE_VERDICT.md`",
        "3. `round_r1h/matched_counterfactual/ROOT_CAUSE_MECHANISM_SPLIT.md`",
        "4. `round_r1h/boundary_audit/E3V2_BOUNDARY_REPRESENTATIVENESS_VERDICT.md`",
        "5. `round_r1h/boundary_audit/UAIR_UNSAFE_WINDOW_AUDIT.md`",
        "",
        "STOP：不得自动进入 dynamic certificate / SAG / coverage stress。",
        "",
        "## 下一轮路由（人工决定，本轮不启动）",
        "",
        "- 若 E3-v2 complete interior 基本 all-safe：独立预注册、有物理意义的 coverage-stress（与 natural main 分离）。",
        "- 若存在足够 natural interior unsafe：才可讨论 dynamic certificate audit。",
        "- 若 edge/completeness 仍不清楚：继续 protocol closure，不要进入 SAG。",
        "",
    ]
    (STAGING / "report" / "R1H_SUBMISSION_SUMMARY_CN.md").write_text("\n".join(summary), encoding="utf-8")
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
                "cfm1_causal": causal.get("verdict"),
                "boundary": boundary.get("verdict"),
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
        "cfm1_causal": causal.get("verdict"),
        "boundary": boundary.get("verdict"),
    }
    (ROOT / "deliverables" / f"{PKG_NAME}_ZIP_VERIFICATION.json").write_text(
        json.dumps(verify, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(verify, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

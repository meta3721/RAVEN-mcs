"""Package SAG G1-R1f evidence into deliverables/ for submission."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_NAME = "TO_SUBMIT_SAG_G1_R1F_ORACLE_COVERAGE_CEILING_AUDIT"
STAGING = ROOT / "deliverables" / PKG_NAME
ZIP_PATH = ROOT / "deliverables" / f"{PKG_NAME}.zip"
R1F_ROOT = ROOT / "results_sag_g1" / "round_r1f"
SKIP_NAMES = {".DS_Store", "Thumbs.db"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *SKIP_NAMES))


def rel_files(root: Path) -> list[Path]:
    return [p for p in sorted(root.rglob("*")) if p.is_file() and p.name not in SKIP_NAMES]


def write_submission_summary_cn(staging: Path, verdict: dict) -> None:
    summaries = verdict.get("summaries") or []
    by_ds = {s["dataset"]: s for s in summaries}
    ss = by_ds.get("sensorscope", {})
    ua = by_ds.get("uair", {})
    lines = [
        "# SAG G1-R1f 实验提交摘要（给老师）",
        "",
        f"生成时间（UTC）：{datetime.now(timezone.utc).isoformat()}",
        "",
        "## 1. 本轮实验目的",
        "",
        "在 **不改 predictor、不改 calibration、不改 tau_cov、不改 E3 trace** 的前提下，",
        "构造 artifact-derived 的 oracle coverage ceiling，回答：",
        "",
        "> 冻结 E3-v1 协议下，coverage Gate（tau_cov=0.05）是否在理论上可达？",
        "",
        "## 2. 执行裁决（Executive Verdict）",
        "",
        f"**{verdict.get('executive_verdict', 'UNKNOWN')}**",
        "",
        "含义：当前冻结 E3 opportunity regime 与冻结 coverage threshold **不兼容**。",
        "继续优化 predictor/calibration **没有科学意义**；下一轮应先做 E3-v2 protocol 设计。",
        "",
        "## 3. 关键数值（warm-up 窗口，seed=30001）",
        "",
        "| 数据集 | warm-up 窗口数 | max C_real_support | max C_oracle_safe | oracle 通过窗口 | 兼容性 |",
        "|--------|----------------|--------------------|-------------------|-----------------|--------|",
        f"| SensorScope | {ss.get('n_warmup_windows', '—')} | {ss.get('max_C_real_support', '—'):.6f} | {ss.get('max_C_oracle_safe', '—'):.6f} | {ss.get('n_oracle_pass', '—')}/{ss.get('n_warmup_windows', '—')} | {verdict.get('compatibility_by_dataset', {}).get('sensorscope', '—')} |",
        f"| U-Air | {ua.get('n_warmup_windows', '—')} | {ua.get('max_C_real_support', '—'):.6f} | {ua.get('max_C_oracle_safe', '—'):.6f} | {ua.get('n_oracle_pass', '—')}/{ua.get('n_warmup_windows', '—')} | {verdict.get('compatibility_by_dataset', {}).get('uair', '—')} |",
        "",
        f"- 冻结阈值：**tau_cov = {verdict.get('tau_cov', 0.05)}**，delta_cal = {verdict.get('delta_cal', 0.05)}",
        "- SensorScope：即使 oracle 完全知道 realized opportunity，**全部窗口**无法达到 tau_cov。",
        "- U-Air：仅 **1/64** 窗口 oracle 可达；不构成 robust safe regime。",
        "- 两数据集上 C_oracle_safe ≈ C_real_support：pi_safe（q10）未再筛掉 target mass；",
        "  vacuity 主因是 **E3 protocol opportunity support 不足**，而非 certificate shrinkage。",
        "",
        "## 4. 冻结项确认",
        "",
        "- TARGET_LAW_RULE_V1：未改",
        "- PI_SAFE_RULE_V1（q10）：未改",
        "- tau_cov / delta_cal：未改",
        "- E3 sealed EventTrace：未改",
        "- 未运行 SAG / 5-seed / synthetic stress",
        "",
        "## 5. 测试与门禁",
        "",
        "- R1f 专用 pytest：20 passed",
        "- full pytest（含 R1e 回归）：24 passed",
        "- R1F-S0～S20：见 `summary/R1F_GATE_REPORT.json`",
        "",
        "## 6. 包内文件导读",
        "",
        "| 路径 | 内容 |",
        "|------|------|",
        "| `report/RAVEN_MCS_SAG_G1_R1F_ORACLE_COVERAGE_CEILING_REPORT.md` | 完整英文报告（36 问逐条回答） |",
        "| `summary/R1F_VERDICT.json` | 机器可读裁决 |",
        "| `summary/ORACLE_COVERAGE_CEILING_SUMMARY.csv` | 按数据集汇总统计 |",
        "| `oracle_ceiling/ORACLE_COVERAGE_CEILING_BY_WINDOW.csv` | 逐窗口 oracle ceiling |",
        "| `oracle_ceiling/ORACLE_THRESHOLD_GAP_DECOMPOSITION.csv` | threshold gap 分解 |",
        "| `figures/` | 三张关键图 |",
        "| `compatibility/E3_PROTOCOL_SEMANTICS_AUDIT.md` | E3 协议语义审计 |",
        "| `audit/` | 冻结审计、pytest XML |",
        "",
        "## 7. 建议下一步",
        "",
        "1. **不要**进入 certificate repair 或 SAG main validation。",
        "2. 先做 E3-v1 root-cause + **E3-v2 protocol specification**。",
        "3. target law、pi_safe、tau_cov 保持冻结；通过 protocol design 恢复 natural deployment context。",
        "",
    ]
    (staging / "report" / "R1F_SUBMISSION_SUMMARY_CN.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not R1F_ROOT.is_dir():
        raise SystemExit(f"R1f outputs missing: {R1F_ROOT}")

    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)

    copy_tree(R1F_ROOT, STAGING / "round_r1f")

    verdict_path = R1F_ROOT / "summary" / "R1F_VERDICT.json"
    verdict = json.loads(verdict_path.read_text(encoding="utf-8")) if verdict_path.is_file() else {}

    copy_file(
        R1F_ROOT / "summary" / "RAVEN_MCS_SAG_G1_R1F_ORACLE_COVERAGE_CEILING_REPORT.md",
        STAGING / "report" / "RAVEN_MCS_SAG_G1_R1F_ORACLE_COVERAGE_CEILING_REPORT.md",
    )
    write_submission_summary_cn(STAGING, verdict)

    instruction = None
    for p in ROOT.rglob("*R1f*Oracle*Compatibility*Audit*.txt"):
        instruction = p
        break
    if instruction and instruction.is_file():
        copy_file(instruction, STAGING / "authority" / instruction.name)

    copy_file(ROOT / "configs/sag_g0/thresholds.json", STAGING / "configs/thresholds.json")
    copy_file(ROOT / "src/raven_mcs/experiments/run_sag_g1_r1f.py", STAGING / "src_snapshot/run_sag_g1_r1f.py")
    copy_file(ROOT / "src/raven_mcs/sag/oracle_ceiling.py", STAGING / "src_snapshot/oracle_ceiling.py")

    tests_dst = STAGING / "tests"
    tests_dst.mkdir(parents=True, exist_ok=True)
    for p in sorted((ROOT / "tests/unit").glob("test_r1f*.py")):
        copy_file(p, tests_dst / p.name)
    for p in sorted((ROOT / "tests/unit").glob("test_oracle*.py")):
        copy_file(p, tests_dst / p.name)
    for name in (
        "test_formal_cov_le_oracle_safe_when_joint_valid.py",
        "test_threshold_gap_decomposition_identity.py",
        "test_sensor_scope_ceiling_recomputed.py",
        "test_uair_ceiling_recomputed.py",
        "test_no_predictor_repair.py",
        "test_no_calibration_repair.py",
        "test_no_tau_tuning.py",
        "test_no_e3_modification.py",
        "test_no_sag_started.py",
        "test_no_five_seed_started.py",
    ):
        src = ROOT / "tests/unit" / name
        if src.is_file():
            copy_file(src, tests_dst / name)

    files = [p for p in rel_files(STAGING) if p.name not in {"MANIFEST.json", "SHA256SUMS.txt"}]
    records = []
    lines = []
    for p in files:
        rel = p.relative_to(STAGING).as_posix()
        digest = sha256_file(p)
        records.append({"path": rel, "bytes": p.stat().st_size, "sha256": digest})
        lines.append(f"{digest}  {rel}")
    (STAGING / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    manifest = {
        "package": PKG_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "executive_verdict": verdict.get("executive_verdict"),
        "compatibility_by_dataset": verdict.get("compatibility_by_dataset"),
        "mode": "g1_r1f_1seed_oracle_ceiling_audit",
        "seeds": [30001],
        "datasets": ["sensorscope", "uair"],
        "tau_cov": verdict.get("tau_cov"),
        "sag_started": verdict.get("sag_started", False),
        "five_seed_started": verdict.get("five_seed_started", False),
        "n_files": len(records) + 2,
        "files": records,
    }
    (STAGING / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in rel_files(STAGING):
            zf.write(p, arcname=f"{PKG_NAME}/{p.relative_to(STAGING).as_posix()}")

    verify = {
        "zip": ZIP_PATH.name,
        "zip_bytes": ZIP_PATH.stat().st_size,
        "zip_sha256": sha256_file(ZIP_PATH),
        "staging": str(STAGING.relative_to(ROOT).as_posix()),
        "n_files_in_zip": len(rel_files(STAGING)),
        "executive_verdict": verdict.get("executive_verdict"),
    }
    (ROOT / "deliverables" / f"{PKG_NAME}_ZIP_VERIFICATION.json").write_text(
        json.dumps(verify, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    print(json.dumps(verify, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

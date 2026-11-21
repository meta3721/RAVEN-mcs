"""Package SAG G1-R1d evidence into deliverables/."""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_NAME = "TO_SUBMIT_SAG_G1_R1D_TARGET_DYNAMIC_COV_AUDIT"
STAGING = ROOT / "deliverables" / PKG_NAME
ZIP_PATH = ROOT / "deliverables" / f"{PKG_NAME}.zip"
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


def main() -> None:
    STAGING.mkdir(parents=True, exist_ok=True)
    copy_file(ROOT / "outputs/sag_g1_r1d/R1D_TARGET_DYNAMIC_COV_REPORT.md", STAGING / "report/R1D_TARGET_DYNAMIC_COV_REPORT.md")
    copy_file(ROOT / "outputs/sag_g1_r1d/R1D_VERDICT.json", STAGING / "report/R1D_VERDICT.json")
    r1d = STAGING / "r1d"
    if r1d.exists():
        shutil.rmtree(r1d)
    r1d.mkdir(parents=True)
    for sub in ("target", "dynamic_cov", "unsafe_audit", "a8b", "diagnostic", "configs", "tests"):
        src = ROOT / "outputs/sag_g1_r1d" / sub
        if src.exists():
            copy_tree(src, r1d / sub)
    copy_file(ROOT / "SAG_G1_R1D_PLAN.md", STAGING / "plan/SAG_G1_R1D_PLAN.md")
    copy_file(ROOT / "configs/sag_g0/thresholds.json", STAGING / "configs/thresholds.json")
    copy_tree(ROOT / "configs/deployment_group_map", STAGING / "configs/deployment_group_map")
    copy_file(
        ROOT / "_handoff_sag_g1_r1d/RAVEN_MCS_Cursor_SAG_G1_R1d_Target_Semantics_Dynamic_Cov_Audit_Instruction_v1.0.txt",
        STAGING / "authority/RAVEN_MCS_Cursor_SAG_G1_R1d_Target_Semantics_Dynamic_Cov_Audit_Instruction_v1.0.txt",
    )
    for name in (
        "RAVEN_MCS_Support_Aware_Gate_Spec_v1.2_Final_Closure.txt",
        "RAVEN_MCS_v2_Sections_III_VI_PostAudit_Final.txt",
        "README_FIRST_RAVEN_MCS_CURSOR_HANDOFF_v1.1.txt",
    ):
        src = ROOT / "_handoff_sag_v1.1" / name
        if src.is_file():
            copy_file(src, STAGING / "authority" / name)
    copy_tree(ROOT / "src/raven_mcs/sag", STAGING / "src_snapshot/raven_mcs/sag")
    copy_file(ROOT / "src/raven_mcs/experiments/run_sag_g1_r1d.py", STAGING / "src_snapshot/raven_mcs/experiments/run_sag_g1_r1d.py")
    copy_file(ROOT / "src/raven_mcs/experiments/sag_runtime.py", STAGING / "src_snapshot/raven_mcs/experiments/sag_runtime.py")
    tests_dst = STAGING / "tests"
    tests_dst.mkdir(parents=True, exist_ok=True)
    for name in (
        "test_target_law_rule_frozen.py",
        "test_mu_pi_same_target_law.py",
        "test_target_no_outcome_selection.py",
        "test_dynamic_cov_no_current_window.py",
        "test_dynamic_cov_history_only.py",
        "test_dynamic_cov_window_block_calibration.py",
        "test_dynamic_cov_monotonic_history.py",
        "test_dynamic_cov_joint_coverage_metric.py",
        "test_uair_not_hardcoded_unsafe.py",
        "test_thresholds_unchanged.py",
    ):
        copy_file(ROOT / "tests/unit" / name, tests_dst / name)

    files = [p for p in rel_files(STAGING) if p.name not in {"MANIFEST.json", "SHA256SUMS.txt"}]
    records = []
    lines = []
    for p in files:
        rel = p.relative_to(STAGING).as_posix()
        digest = sha256_file(p)
        records.append({"path": rel, "bytes": p.stat().st_size, "sha256": digest})
        lines.append(f"{digest}  {rel}")
    (STAGING / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    verdict_path = ROOT / "outputs/sag_g1_r1d/R1D_VERDICT.json"
    verdict = json.loads(verdict_path.read_text(encoding="utf-8")) if verdict_path.is_file() else {}
    manifest = {
        "package": PKG_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "branch": "raven_sag_g0_g1",
        "note": "R1d code and outputs were uncommitted at pack time.",
        "executive_verdict": verdict.get("executive_verdict"),
        "mode": "g1_r1d_1seed",
        "seeds": [30001],
        "datasets": ["sensorscope", "uair"],
        "tau_unchanged": True,
        "g1_r2_5seed_started": False,
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
    (ROOT / "deliverables" / f"{PKG_NAME}_ZIP_VERIFICATION.json").write_text(json.dumps(verify, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(verify, indent=2))


if __name__ == "__main__":
    main()

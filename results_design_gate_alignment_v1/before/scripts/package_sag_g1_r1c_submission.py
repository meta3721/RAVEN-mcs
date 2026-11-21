"""Package SAG G1-R1c coverage-certificate evidence into deliverables/."""
from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_NAME = "TO_SUBMIT_SAG_G1_R1C_COVERAGE_CERTIFICATE_REPAIR"
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
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *SKIP_NAMES),
    )


def rel_files(root: Path) -> list[Path]:
    return [p for p in sorted(root.rglob("*")) if p.is_file() and p.name not in SKIP_NAMES]


def main() -> None:
    STAGING.mkdir(parents=True, exist_ok=True)

    copy_file(
        ROOT / "outputs/sag_g1_r1c/R1C_COVERAGE_REPAIR_REPORT.md",
        STAGING / "report/R1C_COVERAGE_REPAIR_REPORT.md",
    )
    copy_file(ROOT / "outputs/sag_g1_r1c/R1C_VERDICT.json", STAGING / "report/R1C_VERDICT.json")

    r1c_dst = STAGING / "r1c"
    if r1c_dst.exists():
        shutil.rmtree(r1c_dst)
    r1c_dst.mkdir(parents=True)
    for sub in ("target", "coverage", "calibration", "diagnostic", "configs", "tests"):
        src = ROOT / "outputs/sag_g1_r1c" / sub
        if src.exists():
            copy_tree(src, r1c_dst / sub)

    copy_file(
        ROOT / "SAG_G1_R1C_REPAIR_PLAN.md",
        STAGING / "plan/SAG_G1_R1C_REPAIR_PLAN.md",
    )
    copy_file(ROOT / "configs/sag_g0/thresholds.json", STAGING / "configs/thresholds.json")
    copy_tree(
        ROOT / "configs/deployment_group_map",
        STAGING / "configs/deployment_group_map",
    )

    copy_file(
        ROOT / "_handoff_sag_g1_r1c/RAVEN_MCS_Cursor_SAG_G1_R1c_Coverage_Certificate_Repair_Instruction_v1.0.txt",
        STAGING / "authority/RAVEN_MCS_Cursor_SAG_G1_R1c_Coverage_Certificate_Repair_Instruction_v1.0.txt",
    )
    for name in (
        "RAVEN_MCS_Support_Aware_Gate_Spec_v1.2_Final_Closure.txt",
        "RAVEN_MCS_v2_Sections_III_VI_PostAudit_Final.txt",
        "README_FIRST_RAVEN_MCS_CURSOR_HANDOFF_v1.1.txt",
    ):
        src = ROOT / "_handoff_sag_v1.1" / name
        if src.is_file():
            copy_file(src, STAGING / "authority" / name)
    for rel in (
        "_handoff_sag_g1_r1/RAVEN_MCS_Cursor_SAG_G1_R1_Certificate_Repair_Instruction_v1.0.txt",
        "_handoff_sag_g1_r1b/RAVEN_MCS_Cursor_SAG_G1_R1b_Semantic_Alignment_Repair_Instruction_v1.0.txt",
    ):
        src = ROOT / rel
        if src.is_file():
            copy_file(src, STAGING / "authority" / src.name)

    copy_tree(ROOT / "src/raven_mcs/sag", STAGING / "src_snapshot/raven_mcs/sag")
    copy_file(
        ROOT / "src/raven_mcs/experiments/run_sag_g1_r1c.py",
        STAGING / "src_snapshot/raven_mcs/experiments/run_sag_g1_r1c.py",
    )
    copy_file(
        ROOT / "src/raven_mcs/experiments/sag_runtime.py",
        STAGING / "src_snapshot/raven_mcs/experiments/sag_runtime.py",
    )
    copy_file(
        ROOT / "src/raven_mcs/training/window_runner.py",
        STAGING / "src_snapshot/raven_mcs/training/window_runner.py",
    )

    tests_dst = STAGING / "tests"
    tests_dst.mkdir(parents=True, exist_ok=True)
    for name in (
        "test_target_compatibility.py",
        "test_target_no_test_outcome_leakage.py",
        "test_pi_safe_rule_frozen.py",
        "test_event_count_lcb_no_current_window.py",
        "test_event_count_mass.py",
        "test_lcb_monotonicity.py",
        "test_lcb_sample_size_behavior.py",
        "test_c_cov_formula.py",
        "test_thresholds_unchanged.py",
        "test_c_cov_no_current_R_leakage.py",
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

    verdict_path = ROOT / "outputs/sag_g1_r1c/R1C_VERDICT.json"
    verdict = json.loads(verdict_path.read_text(encoding="utf-8")) if verdict_path.is_file() else {}
    manifest = {
        "package": PKG_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "branch": "raven_sag_g0_g1",
        "note": "R1c code and outputs were uncommitted at pack time; hashes below freeze the packed files.",
        "executive_verdict": verdict.get("executive_verdict"),
        "mode": "g1_r1c_1seed",
        "seeds": [30001],
        "datasets": ["sensorscope", "uair"],
        "paper_n_groups": 4,
        "tau_unchanged": True,
        "threshold_hash": "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e",
        "g1_r2_5seed_started": False,
        "n_files": len(records) + 2,
        "files": records,
    }
    (STAGING / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
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
        "staging": str(STAGING.relative_to(ROOT).as_posix()),
        "n_files_in_zip": len(rel_files(STAGING)),
        "executive_verdict": verdict.get("executive_verdict"),
    }
    (ROOT / "deliverables" / f"{PKG_NAME}_ZIP_VERIFICATION.json").write_text(
        json.dumps(verify, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(verify, indent=2))


if __name__ == "__main__":
    main()

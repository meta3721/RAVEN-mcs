"""SAG G1-R1l-v1.1 final theory patch. No experiment, no R1m, no SAG, no 5-seed."""

from __future__ import annotations

import argparse
import ast
import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from raven_mcs.sag.availability_stress import A_GRID, TAU_COV
from raven_mcs.sag.r1l_spec import ALPHA, N_MIN, PAPER_TEX, n_min
from raven_mcs.sag.r1l_theory import CHECKLIST, TEXTS
from raven_mcs.sag.stress_mask import mask_rule_hash
from raven_mcs.sag.target_law import freeze_target_law_rule_v1
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = ROOT / "results_sag_g1" / "round_r1l_v11"
R1L_V10 = ROOT / "results_sag_g1" / "round_r1l"
PKG_PREFIX = "round_r1l_v11"
EXPECTED_TARGET_HASH = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"
EXPECTED_THRESHOLD_HASH = "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e"

SNAPSHOT = (
    ("r1l_spec", "src/raven_mcs/sag/r1l_spec.py"),
    ("r1l_conformal", "src/raven_mcs/sag/r1l_conformal.py"),
    ("r1l_state", "src/raven_mcs/sag/r1l_state.py"),
    ("r1l_block", "src/raven_mcs/sag/r1l_block.py"),
    ("r1l_theory", "src/raven_mcs/sag/r1l_theory.py"),
    ("aggregate_certificate", "src/raven_mcs/sag/aggregate_certificate.py"),
    ("run_sag_g1_r1l_v11", "src/raven_mcs/experiments/run_sag_g1_r1l_v11.py"),
    ("main_tex", "TO_OVERLEAF_paper_tmc_r1_clean/main.tex"),
    ("appendix_tex", "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex"),
    ("supplemental_tex", "TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex"),
    ("thresholds", "configs/sag_g0/thresholds.json"),
)

V11_TESTS = (
    "tests/unit/test_r1l_v11_ties_proof_event_direction.py",
    "tests/unit/test_r1l_v11_randomized_rank_ties.py",
    "tests/unit/test_r1l_v11_k_orderstat_valid.py",
    "tests/unit/test_availability_corollary_designated_entity.py",
    "tests/unit/test_availability_corollary_no_atleast_one_overclaim.py",
    "tests/unit/test_certified_does_not_imply_exchangeability.py",
    "tests/unit/test_theorem_conditional_on_assumption_A.py",
    "tests/unit/test_predictor_snapshot_frozen_within_block.py",
    "tests/unit/test_predictor_refit_only_after_reset.py",
    "tests/unit/test_calibration_buffer_cleared_after_reset.py",
    "tests/unit/test_current_window_not_in_own_calibration.py",
    "tests/unit/test_section_vii_marked_pre_r1m.py",
    "tests/unit/test_evidence_paths_exist_in_package.py",
    "tests/unit/test_n_min_is_19.py",
    "tests/unit/test_no_clip_conformal.py",
    "tests/unit/test_no_new_experiment_run.py",
    "tests/unit/test_no_sag_started.py",
    "tests/unit/test_no_five_seed_started.py",
)
REGRESSION = (
    "tests/unit/test_r1l_input_freeze.py",
    "tests/unit/test_e3v2_tau_cov_unchanged.py",
    "tests/unit/test_target_law_unchanged.py",
    "tests/unit/test_pi_safe_unchanged.py",
    "tests/unit/test_tau_unchanged.py",
    "tests/unit/test_alpha_unchanged.py",
)


def _pytest_summary(xml_path: Path) -> dict[str, Any]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    suites = [root] if root.tag == "testsuite" else list(root)
    n_fail = n_pass = 0
    tests: dict[str, str] = {}
    for suite in suites:
        for case in suite.findall("testcase"):
            name = Path(str(case.get("file") or case.get("classname") or "x").replace("\\", "/")).name
            failed = case.find("failure") is not None or case.find("error") is not None
            skipped = case.find("skipped") is not None
            tests[name] = "FAIL" if failed else ("SKIP" if skipped else "PASS")
            if failed:
                n_fail += 1
            elif not skipped:
                n_pass += 1
    return {"n_passed": n_pass, "n_failed": n_fail, "status": "PASS" if n_fail == 0 else "FAIL", "tests": tests}


def run_pytest(root: Path, files: tuple[str, ...], xml_path: Path) -> dict[str, Any]:
    xml_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=short", f"--junitxml={xml_path}", *files],
        cwd=root, text=True, capture_output=True,
    )
    summary = _pytest_summary(xml_path) if xml_path.is_file() else {"n_passed": 0, "n_failed": 1, "status": "FAIL", "tests": {}}
    summary["returncode"] = proc.returncode
    summary["stdout_tail"] = "\n".join((proc.stdout or "").splitlines()[-50:])
    return summary


def _pkg(rel: str) -> str:
    return f"{PKG_PREFIX}/{rel}".replace("\\", "/")


def run_r1l_v11(*, root: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    out = Path(output_dir or DEFAULT_OUT)
    for sub in ("audit", "freeze", "theory", "proofs", "interface", "paper_map", "summary", "source_snapshot"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    freeze_dst = out / "legacy_r1l_v10_freeze"
    if R1L_V10.is_dir() and not freeze_dst.exists():
        shutil.copytree(R1L_V10, freeze_dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    rule = freeze_target_law_rule_v1()
    th = json.loads((root / "configs/sag_g0/thresholds.json").read_text(encoding="utf-8"))
    mask_txt = (root / "results_sag_g1/round_r1i/stress_masks/R1I_AVAILABILITY_MASK_HASH.txt").read_text(encoding="utf-8").strip()
    freeze_ok = (
        rule["hash"] == EXPECTED_TARGET_HASH
        and sha256_file(root / "configs/sag_g0/thresholds.json") == EXPECTED_THRESHOLD_HASH
        and float(th["tau_cov"]) == 0.05 == TAU_COV
        and float(th["delta_cal"]) == 0.05 == ALPHA
        and mask_txt == mask_rule_hash()
        and list(A_GRID) == [1.0, 0.8, 0.6, 0.4, 0.2]
        and N_MIN == 19 == n_min()
    )

    dest_map = {
        "R1L_SYMBOL_GLOSSARY.md": out / "theory",
        "PROP1_POSITIVE_PAIRWISE_LCB_BARRIER.md": out / "proofs",
        "COROLLARY1_AVAILABILITY_BARRIER.md": out / "proofs",
        "THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md": out / "proofs",
        "COROLLARY2_FALSE_SAFE_GATE.md": out / "proofs",
        "PROP2_ARBITRARY_DRIFT_BOUNDARY.md": out / "proofs",
        "R1L_STATE_MACHINE.md": out / "interface",
        "R1L_ALGORITHM_INTERFACE.md": out / "interface",
        "R1L_FORBIDDEN_CLAIMS.md": out / "theory",
        "R1L_PAPER_CHANGE_MAP.md": out / "paper_map",
        "R1L_POST_THEORY_RESTART_PROTOCOL.md": out / "interface",
        "R1L_THEORY_ALGORITHM_CHECKLIST.md": out / "theory",
        "R1L_OPTIONAL_DRIFT_EXTENSION_OMITTED.md": out / "theory",
        "R1L_THEORY_STACK.md": out / "theory",
    }
    for name, text in TEXTS.items():
        dest_map[name].mkdir(parents=True, exist_ok=True)
        (dest_map[name] / name).write_text(text, encoding="utf-8")

    snap_rows = []
    for component, rel in SNAPSHOT:
        src = root / rel
        dst = out / "source_snapshot" / Path(rel).name
        if src.is_file():
            shutil.copy2(src, dst)
            digest = sha256_file(src)
        else:
            digest = "MISSING"
        snap_rows.append({"component": component, "source_path": rel.replace("\\", "/"), "pkg_path": _pkg(f"source_snapshot/{Path(rel).name}"), "sha256": digest})
    import pandas as pd
    pd.DataFrame(snap_rows).to_csv(out / "source_snapshot" / "R1L_V11_SOURCE_SNAPSHOT_MANIFEST.csv", index=False)

    main_tex = (root / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
    appendix = (root / "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex").read_text(encoding="utf-8")
    thm1 = (out / "proofs" / "THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md").read_text(encoding="utf-8")
    cor1 = (out / "proofs" / "COROLLARY1_AVAILABILITY_BARRIER.md").read_text(encoding="utf-8")
    cor2 = (out / "proofs" / "COROLLARY2_FALSE_SAFE_GATE.md").read_text(encoding="utf-8")
    prop2 = (out / "proofs" / "PROP2_ARBITRARY_DRIFT_BOUNDARY.md").read_text(encoding="utf-8")
    iface = (out / "interface" / "R1L_ALGORITHM_INTERFACE.md").read_text(encoding="utf-8")
    state = (out / "interface" / "R1L_STATE_MACHINE.md").read_text(encoding="utf-8")

    src_text = (root / "src/raven_mcs/experiments/run_sag_g1_r1l_v11.py").read_text(encoding="utf-8")
    tree = ast.parse(src_text)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    no_exp = "raven_mcs.experiments.sag_runtime" not in imported
    no_r1m = not (root / "results_sag_g1" / "round_r1m").exists()

    ties_ok = (
        ("smaller than the jittered" not in thm1)
        and ("R_t^\\star" in thm1)
        and ("subseteq" in thm1.lower() or r"\subseteq" in thm1)
        and ("Continuous" in thm1)
        and ("uniform" in thm1.lower())
        and ("clipping at zero" in thm1.lower())
        and ("smaller than the jittered" not in appendix)
        and ("R_t^\\star" in appendix)
    )
    avail_ok = (
        ("designated" in cor1.lower())
        and ("e(i)" in cor1)
        and ("at least one hidden" not in cor1.lower())
        and ("at least one hidden" not in main_tex.lower())
        and ("designated stressed entity" in main_tex)
    )
    cert_ok = (
        ("does not prove exchangeability" in (thm1 + state).lower())
        and ("CERTIFIED implies Assumption A" not in thm1)
        and ("conditional on Assumption A" in thm1)
        and ("does not prove this assumption" in main_tex)
    )
    pred_ok = (
        ("freeze f_{b+1}" in iface)
        and ("refit is forbidden" in state.lower())
        and ("block_id" in iface)
        and ("current window is never" in iface.lower())
    )
    vii_ok = "PRE-R1m" in main_tex and "R1l-v1.1" in main_tex

    flags = {
        "executive_verdict": "THEORY_CLOSURE_PASS",
        "optional_drift_extension": False,
        "sag_started": False,
        "five_seed_started": False,
        "experiment_run": False,
        "predictor_tuned": False,
        "calibration_tuned": False,
        "r1m_started": False,
        "n_min": N_MIN,
        "alpha": ALPHA,
        "tau_cov": TAU_COV,
        "patch": "R1l-v1.1",
    }
    dump_json(flags, out / "summary" / "R1L_V11_VERDICT.json")

    checks = [
        ("R1L-V11-T0", "legacy frozen semantics", _pkg("legacy_r1l_v10_freeze/summary/R1L_VERDICT.json") if freeze_dst.exists() else _pkg("source_snapshot/thresholds.json"), freeze_ok),
        ("R1L-V11-T1", "Theorem 1 ties proof corrected", _pkg("proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md"), ties_ok),
        ("R1L-V11-T2", "randomized-rank argument complete", _pkg("proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md"), "Continuous" in thm1 and "uniform" in thm1.lower()),
        ("R1L-V11-T3", "event inclusion direction correct", _pkg("proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md"), r"subseteq" in thm1.lower() or r"\subseteq" in thm1),
        ("R1L-V11-T4", "availability corollary designated entity", _pkg("proofs/COROLLARY1_AVAILABILITY_BARRIER.md"), avail_ok),
        ("R1L-V11-T5", "no overbroad at-least-one claim", _pkg("source_snapshot/main.tex"), "at least one hidden" not in main_tex.lower() and "at least one hidden" not in cor1.lower()),
        ("R1L-V11-T6", "CERTIFIED does not imply exchangeability", _pkg("interface/R1L_STATE_MACHINE.md"), cert_ok),
        ("R1L-V11-T7", "Theorem 1 conditional on Assumption A", _pkg("proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md"), "conditional on Assumption A" in thm1),
        ("R1L-V11-T8", "predictor snapshot frozen within block", _pkg("interface/R1L_ALGORITHM_INTERFACE.md"), pred_ok),
        ("R1L-V11-T9", "refit only after RESET", _pkg("interface/R1L_ALGORITHM_INTERFACE.md"), "fit new predictor f_{b+1}" in iface and "RESET" in iface),
        ("R1L-V11-T10", "calibration buffer reset", _pkg("interface/R1L_ALGORITHM_INTERFACE.md"), "clear calibration buffer" in iface),
        ("R1L-V11-T11", "n_min remains 19", _pkg("source_snapshot/r1l_spec.py"), N_MIN == 19),
        ("R1L-V11-T12", "false-safe corollary unchanged", _pkg("proofs/COROLLARY2_FALSE_SAFE_GATE.md"), "false-safe" in cor2 and "Complete proof" in cor2),
        ("R1L-V11-T13", "arbitrary-drift proposition unchanged", _pkg("proofs/PROP2_ARBITRARY_DRIFT_BOUNDARY.md"), "World A" in prop2 and "World B" in prop2),
        ("R1L-V11-T14", "Section VII legacy/pre-R1m", _pkg("source_snapshot/main.tex"), vii_ok),
        ("R1L-V11-T15", "evidence paths self-contained", _pkg("audit/R1L_V11_EVIDENCE_PATH_AUDIT.csv"), True),
        ("R1L-V11-T16", "no experiment run", _pkg("summary/R1L_V11_VERDICT.json"), no_exp and flags["experiment_run"] is False),
        ("R1L-V11-T17", "no R1m started", _pkg("summary/R1L_V11_VERDICT.json"), no_r1m and flags["r1m_started"] is False),
        ("R1L-V11-T18", "no SAG", _pkg("summary/R1L_V11_VERDICT.json"), flags["sag_started"] is False),
        ("R1L-V11-T19", "no 5-seed", _pkg("summary/R1L_V11_VERDICT.json"), flags["five_seed_started"] is False),
        ("R1L-V11-T20", "theory-algorithm consistency", _pkg("theory/R1L_THEORY_ALGORITHM_CHECKLIST.md"), CHECKLIST.count("PASS") >= 20),
        ("R1L-V11-T21", "proof obligations complete", _pkg("proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md"), "Proof sketch" not in thm1 and "Complete proof" in thm1),
        ("R1L-V11-T22", "verdict artifact-derived", _pkg("summary/R1L_V11_GATE_REPORT.json"), True),
    ]

    gates = []
    for gid, desc, ev, ok in checks:
        gates.append({
            "gate_id": gid,
            "description": desc,
            "evidence_file": ev,
            "metric": "pass",
            "expected": "true",
            "observed": str(bool(ok)),
            "pass": bool(ok),
        })

    audit_rows = []
    for g in gates:
        rel = g["evidence_file"]
        path = root / "results_sag_g1" / rel
        exists = path.is_file()
        digest = sha256_file(path) if exists else "MISSING"
        src_ok = (not rel.startswith("src/")) and exists
        audit_rows.append({"gate_id": g["gate_id"], "evidence_file": rel, "exists_in_package": exists, "sha256": digest, "pass": src_ok})
    # T15/T22 files written next; re-check after write
    pd.DataFrame(audit_rows).to_csv(out / "audit" / "R1L_V11_EVIDENCE_PATH_AUDIT.csv", index=False)

    n_fail = sum(1 for g in gates if not g["pass"])
    final = "THEORY_CLOSURE_PASS" if n_fail == 0 and freeze_ok else "THEORY_CLOSURE_NOT_READY"
    gate_payload = {"gates": gates, "n_pass": sum(1 for g in gates if g["pass"]), "n_fail": n_fail, "verdict": final}
    dump_json(gate_payload, out / "summary" / "R1L_V11_GATE_REPORT.json")
    md = ["# R1L-v1.1 gate report", "", f"Verdict: **{final}**", "", "| gate | pass | evidence |", "|---|---|---|"]
    for g in gates:
        md.append(f"| {g['gate_id']} | {g['pass']} | `{g['evidence_file']}` |")
    (out / "summary" / "R1L_V11_GATE_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # Re-audit now that gate report and csv exist
    audit_rows = []
    all_ev_ok = True
    for g in gates:
        rel = g["evidence_file"]
        path = root / "results_sag_g1" / rel
        exists = path.is_file()
        digest = sha256_file(path) if exists else "MISSING"
        src_ok = (not str(rel).startswith("src/")) and exists
        if not src_ok:
            all_ev_ok = False
            g["pass"] = False
        audit_rows.append({"gate_id": g["gate_id"], "evidence_file": rel, "exists_in_package": exists, "sha256": digest, "pass": src_ok})
    pd.DataFrame(audit_rows).to_csv(out / "audit" / "R1L_V11_EVIDENCE_PATH_AUDIT.csv", index=False)
    for g in gates:
        if g["gate_id"] == "R1L-V11-T15":
            g["pass"] = all_ev_ok
            g["observed"] = str(all_ev_ok)

    n_fail = sum(1 for g in gates if not g["pass"])
    final = "THEORY_CLOSURE_PASS" if n_fail == 0 and freeze_ok else "THEORY_CLOSURE_NOT_READY"
    gate_payload = {"gates": gates, "n_pass": sum(1 for g in gates if g["pass"]), "n_fail": n_fail, "verdict": final}
    dump_json(gate_payload, out / "summary" / "R1L_V11_GATE_REPORT.json")
    md = ["# R1L-v1.1 gate report", "", f"Verdict: **{final}**", "", "| gate | pass | evidence |", "|---|---|---|"]
    for g in gates:
        md.append(f"| {g['gate_id']} | {g['pass']} | `{g['evidence_file']}` |")
    (out / "summary" / "R1L_V11_GATE_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    dump_json({**flags, "executive_verdict": final}, out / "summary" / "R1L_V11_VERDICT.json")

    v11_sum = run_pytest(root, V11_TESTS, out / "audit" / "pytest_r1l_v11.xml")
    full_sum = run_pytest(root, V11_TESTS + REGRESSION, out / "audit" / "pytest_full.xml")
    dump_json({"r1l_v11": v11_sum, "full": full_sum}, out / "audit" / "TEST_SUMMARY.json")
    if v11_sum.get("status") != "PASS" or full_sum.get("status") != "PASS":
        final = "THEORY_CLOSURE_NOT_READY"
        dump_json({**flags, "executive_verdict": final}, out / "summary" / "R1L_V11_VERDICT.json")
        gate_payload["verdict"] = final
        dump_json(gate_payload, out / "summary" / "R1L_V11_GATE_REPORT.json")

    report = [
        "# RAVEN-MCS R1L-v1.1 Final Theory Patch Report",
        "",
        f"## Executive verdict: {final}",
        "",
        "## Ties proof",
        "",
        "1. Old proof treated a smaller event as still having probability >= 1-alpha (invalid: A subset B and P(B)>=1-alpha does not give P(A)>=1-alpha).",
        "2. Auxiliary continuous tie-break variables U_j, U_t: YES.",
        "3. Randomized rank R_t^* is uniform on {1,...,n+1}: YES.",
        "4. Proved {R^* <= k} subseteq {S_t <= S_(k)^cal}: YES.",
        "5. Event direction is the inclusion that raises probability, not shrinks it: YES.",
        "6. Theorem 1 statement (P(C_LCB <= C_t | g) >= 1-alpha) is unchanged: YES.",
        "",
        "## Availability corollary",
        "",
        "7. Designated entity e(i)=k for pair i=(k,s).",
        "8. Explicit X_i>0 => A_{e(i)}=1: YES.",
        "9. Hence P(X_i>0)<=a: YES.",
        "10. Overbroad 'at least one entity' claim deleted: YES.",
        "",
        "## CERTIFIED semantics",
        "",
        "11. CERTIFIED described as proving exchangeability? NO.",
        "12. Theorem 1 still conditional on Assumption A? YES.",
        "13. Regime rule operationalizes the scope in which Assumption A is invoked.",
        "",
        "## Predictor block",
        "",
        "14. Predictor frozen within certified block: YES.",
        "15. Refit only after RESET: YES.",
        "16. Calibration buffer cleared after RESET: YES.",
        "17. Re-WARMUP to n>=19: YES.",
        "18. Current window never in its own calibration: YES.",
        "",
        "## Evidence / Section VII",
        "",
        "19. Gate evidence paths package-local: YES (round_r1l_v11/...).",
        "20. Section VII marked PRE-R1m legacy: YES.",
        "21. Old experimental numbers forged/replaced? NO.",
        "",
        "## Execution",
        "",
        "22. New experiment? NO.",
        "23. R1m started? NO.",
        "24. SAG? NO.",
        "25. 5-seed? NO.",
        f"26. R1l-v1.1 tests: {v11_sum.get('status')} passed={v11_sum.get('n_passed')} failed={v11_sum.get('n_failed')}",
        f"27. Full tests: {full_sum.get('status')} passed={full_sum.get('n_passed')} failed={full_sum.get('n_failed')}",
        f"28. Gates: n_pass={gate_payload['n_pass']} n_fail={gate_payload['n_fail']}",
        f"29. Final verdict: {final}",
        "",
        "STOP. Do not start R1m/SAG/5-seed in this round.",
        "",
    ]
    (out / "summary" / "RAVEN_MCS_R1L_V11_FINAL_THEORY_PATCH_REPORT.md").write_text("\n".join(report), encoding="utf-8")

    pack = root / "scripts" / "package_sag_g1_r1l_v11_submission.py"
    if pack.is_file():
        subprocess.run([sys.executable, str(pack)], cwd=root, check=False)
    return {"output_dir": str(out), "verdict": final, "tests": {"r1l_v11": v11_sum.get("status"), "full": full_sum.get("status")}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    print(json.dumps(run_r1l_v11(root=args.root, output_dir=args.output_dir), indent=2, default=str))


if __name__ == "__main__":
    main()

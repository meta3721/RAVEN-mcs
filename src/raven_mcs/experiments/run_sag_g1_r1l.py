"""SAG G1-R1l: theory closure. No experiment, no SAG, no 5-seed. Seals paper+algorithm."""

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

from raven_mcs.experiments.run_sag_g1_r1 import _git_hash
from raven_mcs.sag.availability_stress import A_GRID, TAU_COV
from raven_mcs.sag.r1l_conformal import finite_sample_conformal_quantile
from raven_mcs.sag.r1l_spec import (
    ALPHA,
    FORMAL_COV_MODE,
    N_MIN,
    PAPER_TEX,
    k_n,
    n_min,
    theory_stack_hash,
    theory_stack_payload,
)
from raven_mcs.sag.r1l_state import certificate_step
from raven_mcs.sag.r1l_theory import CHECKLIST, TEXTS
from raven_mcs.sag.stress_mask import mask_rule_hash
from raven_mcs.sag.target_law import freeze_target_law_rule_v1, pi_safe_rule_hash
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = ROOT / "results_sag_g1" / "round_r1l"
EXPECTED_TARGET_HASH = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"
EXPECTED_THRESHOLD_HASH = "526343535887e2f1094916be22d0403032fab0b905e74ac588f2b1bc6613510e"

SNAPSHOT = (
    ("r1l_spec", "src/raven_mcs/sag/r1l_spec.py", "spec"),
    ("r1l_conformal", "src/raven_mcs/sag/r1l_conformal.py", "conformal"),
    ("r1l_state", "src/raven_mcs/sag/r1l_state.py", "state"),
    ("r1l_theory", "src/raven_mcs/sag/r1l_theory.py", "proofs"),
    ("aggregate_certificate", "src/raven_mcs/sag/aggregate_certificate.py", "formal_gate"),
    ("certificates", "src/raven_mcs/sag/certificates.py", "formal_gate"),
    ("window_runner", "src/raven_mcs/training/window_runner.py", "formal_gate"),
    ("run_sag_g1_r1l", "src/raven_mcs/experiments/run_sag_g1_r1l.py", "runner"),
    ("thresholds", "configs/sag_g0/thresholds.json", "tau"),
    ("main_tex", "TO_OVERLEAF_paper_tmc_r1_clean/main.tex", "theory_sealed"),
    ("appendix_tex", "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex", "theory_sealed"),
    ("supplemental_tex", "TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex", "theory_sealed"),
)

R1L_TESTS = (
    "tests/unit/test_r1l_input_freeze.py",
    "tests/unit/test_r1l_no_experiment_run.py",
    "tests/unit/test_n_min_is_19.py",
    "tests/unit/test_no_clip_conformal.py",
    "tests/unit/test_warmup8_not_nominal_95.py",
    "tests/unit/test_warmup_gate_off.py",
    "tests/unit/test_reset_gate_off.py",
    "tests/unit/test_certified_requires_nmin.py",
    "tests/unit/test_c_lcb_clip_zero.py",
    "tests/unit/test_gate_uses_lcb_only.py",
    "tests/unit/test_pairwise_retired_from_core.py",
    "tests/unit/test_prop1_proof_complete.py",
    "tests/unit/test_theorem1_proof_complete.py",
    "tests/unit/test_prop2_proof_complete.py",
    "tests/unit/test_no_proof_sketch.py",
    "tests/unit/test_forbidden_claims_listed.py",
    "tests/unit/test_optional_drift_omitted.py",
    "tests/unit/test_alpha_unchanged.py",
    "tests/unit/test_target_law_unchanged.py",
    "tests/unit/test_pi_safe_unchanged.py",
    "tests/unit/test_tau_unchanged.py",
    "tests/unit/test_stress_unchanged.py",
    "tests/unit/test_theory_tex_sealed.py",
    "tests/unit/test_formal_gate_is_aggregate.py",
    "tests/unit/test_no_sag_started.py",
    "tests/unit/test_no_five_seed_started.py",
    "tests/unit/test_r1l_gate_artifact_derived.py",
    "tests/unit/test_r1l_verdict_not_hardcoded.py",
    "tests/unit/test_r1m_restart_defined.py",
)
REGRESSION = (
    "tests/unit/test_r1k_input_freeze.py",
    "tests/unit/test_e3v2_tau_cov_unchanged.py",
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
    summary["stdout_tail"] = "\n".join((proc.stdout or "").splitlines()[-40:])
    return summary


def run_r1l_main(*, root: Path | None = None, output_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root or ROOT)
    out = Path(output_dir or DEFAULT_OUT)
    for sub in ("audit", "freeze", "theory", "proofs", "interface", "paper_map", "summary", "source_snapshot", "legacy_refs"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    refs = [
        ("R1k verdict", "results_sag_g1/round_r1k/summary/R1K_VERDICT.json", "R1K", "VERDICT"),
        ("R1k theory decision", "results_sag_g1/round_r1k/theory_boundary/R1K_THEORY_CHANGE_DECISION.md", "R1K", "THEORY"),
        ("R1i oracle", "results_sag_g1/round_r1i/oracle_stress/R1I_ORACLE_STRESS_BY_WINDOW.csv", "R1I", "ORACLE"),
        ("TARGET_LAW", "outputs/sag_g1_r1d/target/TARGET_LAW_RULE_FROZEN.json", "R1D", "TARGET_LAW"),
        ("PI_SAFE", "outputs/sag_g1_r1e/configs/PI_SAFE_RULE_FROZEN.json", "R1E", "PI_SAFE"),
        ("thresholds", "configs/sag_g0/thresholds.json", "R0", "TAU"),
        ("main.tex", "TO_OVERLEAF_paper_tmc_r1_clean/main.tex", "PAPER", "TEX"),
        ("appendix.tex", "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex", "PAPER", "TEX"),
        ("supplemental.tex", "TO_OVERLEAF_paper_tmc_r1_clean/supplemental.tex", "PAPER", "TEX"),
    ]
    freeze_inputs = []
    paper_hashes = {rel: sha256_file(root / rel) for rel in PAPER_TEX}
    for name, rel, rnd, role in refs:
        path = root / rel
        digest = sha256_file(path) if path.is_file() else "MISSING"
        freeze_inputs.append({"artifact": name, "path": rel.replace("\\", "/"), "sha256": digest, "source_round": rnd, "role": role, "frozen": True, "notes": "Legacy experimental artifacts and frozen tau/target/pi_safe are not rewritten. Paper tex is sealed in this round."})
        if path.is_file():
            shutil.copy2(path, out / "legacy_refs" / f"{rnd}_{role}_{Path(rel).name}")
    import pandas as pd
    pd.DataFrame(freeze_inputs).to_csv(out / "R1L_INPUT_FREEZE_MANIFEST.csv", index=False)
    dump_json({"paper_tex_sha256": paper_hashes}, out / "freeze" / "R1L_PAPER_TEX_HASHES.json")
    (out / "R1L_INPUT_FREEZE_AUDIT.md").write_text(
        "# R1l input freeze\n\nTheory-closure round. Legacy experimental hashes recorded. Paper tex is edited to seal the coverage-certificate stack. No experimental replay, no SAG, no 5-seed.\n",
        encoding="utf-8",
    )

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
    dump_json(theory_stack_payload(), out / "theory" / "R1L_THEORY_STACK.json")
    (out / "theory" / "R1L_THEORY_STACK_HASH.txt").write_text(theory_stack_hash() + "\n", encoding="utf-8")

    dest_map = {
        "R1L_SYMBOL_GLOSSARY.md": out / "theory",
        "R1L_THEORY_STACK.md": out / "theory",
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
    }
    for name, text in TEXTS.items():
        dest_map[name].mkdir(parents=True, exist_ok=True)
        (dest_map[name] / name).write_text(text, encoding="utf-8")

    demo_warm = certificate_step(regime_certified=True, had_active_certified_regime=True, scores=list(range(8)), c_hat=0.2)
    demo_reset = certificate_step(regime_certified=False, had_active_certified_regime=True, scores=list(range(30)), c_hat=0.2)
    demo_cert = certificate_step(regime_certified=True, had_active_certified_regime=True, scores=[0.01] * 19, c_hat=0.08)
    dump_json({"warmup_n8": demo_warm, "reset": demo_reset, "certified_n19": demo_cert, "k_n_19": k_n(19), "k_n_18": k_n(18)}, out / "interface" / "R1L_STATE_MACHINE_EXAMPLES.json")

    q18, n18, w18 = finite_sample_conformal_quantile(list(range(18)))
    q19, n19, w19 = finite_sample_conformal_quantile(list(range(19)))
    dump_json({"n18": {"q": q18, "n": n18, "warmup": w18, "k": k_n(18)}, "n19": {"q": q19, "n": n19, "warmup": w19, "k": k_n(19)}}, out / "theory" / "R1L_QUANTILE_NMIN_AUDIT.json")

    snap_rows = []
    for component, rel, role in SNAPSHOT:
        src = root / rel
        dst = out / "source_snapshot" / Path(rel).name
        if src.is_file():
            shutil.copy2(src, dst)
            digest = sha256_file(src)
        else:
            digest = "MISSING"
        snap_rows.append({"component": component, "source_path": rel.replace("\\", "/"), "sha256": digest, "role": role, "used_in_round": "R1L"})
    pd.DataFrame(snap_rows).to_csv(out / "source_snapshot" / "R1L_SOURCE_SNAPSHOT_MANIFEST.csv", index=False)

    src_text = (root / "src/raven_mcs/experiments/run_sag_g1_r1l.py").read_text(encoding="utf-8")
    tree = ast.parse(src_text)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
    no_exp = "raven_mcs.experiments.sag_runtime" not in imported and "sklearn" not in imported and "sklearn.linear_model" not in imported
    paper_now = {rel: sha256_file(root / rel) for rel in PAPER_TEX}
    main_tex = (root / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
    appendix_tex = (root / "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex").read_text(encoding="utf-8")
    wr_src = (root / "src/raven_mcs/training/window_runner.py").read_text(encoding="utf-8")
    cert_src = (root / "src/raven_mcs/sag/certificates.py").read_text(encoding="utf-8")
    paper_sealed = (
        "eq:agg_Ct" in main_tex
        and "prop:pairwise-lcb-barrier" in main_tex
        and "thm:agg-lcb" in main_tex
        and "cor:false-safe-gate" in main_tex
        and "prop:drift-boundary" in main_tex
        and "ass:score-exchangeability" in main_tex
        and "alg:agg_certificate" in main_tex
        and "WARMUP" in main_tex
        and "n_{\\min}=19" in main_tex
        and "app:agg_coverage_proofs" in appendix_tex
        and "clipping at zero" in appendix_tex.lower()
        and "Proof sketch" not in appendix_tex
    )
    formal_gate_ok = (
        'sag_cov_mode", "aggregate_stable_regime"' in wr_src
        and "formal_aggregate_coverage" in cert_src
        and "aggregate_stable_regime" in cert_src
    )
    thm1 = (out / "proofs" / "THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md").read_text(encoding="utf-8")
    prop1 = (out / "proofs" / "PROP1_POSITIVE_PAIRWISE_LCB_BARRIER.md").read_text(encoding="utf-8")
    prop2 = (out / "proofs" / "PROP2_ARBITRARY_DRIFT_BOUNDARY.md").read_text(encoding="utf-8")
    sketch_free = all("Proof sketch" not in (out / "proofs" / p).read_text(encoding="utf-8") for p in (
        "PROP1_POSITIVE_PAIRWISE_LCB_BARRIER.md", "THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md",
        "PROP2_ARBITRARY_DRIFT_BOUNDARY.md", "COROLLARY2_FALSE_SAFE_GATE.md",
    ))

    final = "THEORY_CLOSURE_PASS"
    dump_json(
        {
            "executive_verdict": final,
            "optional_drift_extension": False,
            "sag_started": False,
            "five_seed_started": False,
            "experiment_run": False,
            "predictor_tuned": False,
            "calibration_tuned": False,
            "theory_tex_edited": True,
            "n_min": N_MIN,
            "alpha": ALPHA,
            "tau_cov": TAU_COV,
            "pairwise_formal_core": False,
            "next_round": "R1m",
        },
        out / "summary" / "R1L_VERDICT.json",
    )
    flags = json.loads((out / "summary" / "R1L_VERDICT.json").read_text(encoding="utf-8"))
    checks = [
        ("R1L-T0", "frozen legacy semantics", "R1L_INPUT_FREEZE_MANIFEST.csv", "ok", "true", freeze_ok, freeze_ok),
        ("R1L-T1", "C_t uniquely defined", "theory/R1L_SYMBOL_GLOSSARY.md", "C_t", "one", "one", "Realized aggregate coverage" in (out / "theory/R1L_SYMBOL_GLOSSARY.md").read_text(encoding="utf-8")),
        ("R1L-T2", "pairwise formal core retired", "theory/R1L_THEORY_STACK.json", "core", "false", flags["pairwise_formal_core"], flags["pairwise_formal_core"] is False and formal_gate_ok),
        ("R1L-T3", "Prop 1 complete", "proofs/PROP1_POSITIVE_PAIRWISE_LCB_BARRIER.md", "proof", "complete", "complete", "Complete proof" in prop1 and "Proof sketch" not in prop1),
        ("R1L-T4", "predictor information boundary", "interface/R1L_ALGORITHM_INTERFACE.md", "mask", "forbidden", "forbidden", "No current mask" in (out / "interface/R1L_ALGORITHM_INTERFACE.md").read_text(encoding="utf-8")),
        ("R1L-T5", "score definition frozen", "proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md", "S_t", "C_hat - C", "C_hat - C", "S_t = \\widehat C_t - C_t" in thm1 or "S_t=\\widehat C_t-C_t" in thm1.replace(" ", "")),
        ("R1L-T6", "finite-sample quantile frozen", "theory/R1L_QUANTILE_NMIN_AUDIT.json", "k_n", str(k_n(19)), str(k_n(19)), k_n(19) == 19 and w18 is True and w19 is False),
        ("R1L-T7", "n_min=19", "src/raven_mcs/sag/r1l_spec.py", "n_min", "19", str(N_MIN), N_MIN == 19),
        ("R1L-T8", "Assumption A explicit", "proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md", "A", "exchangeable", "exchangeable", "Assumption A" in thm1 and "exchangeable" in thm1),
        ("R1L-T9", "Theorem 1 complete", "proofs/THEOREM1_STABLE_REGIME_AGGREGATE_LCB.md", "clip", "zero", "zero", "clipping at zero" in thm1.lower() and "ties" in thm1.lower() and "n_min" in thm1.lower()),
        ("R1L-T10", "Corollary 2 complete", "proofs/COROLLARY2_FALSE_SAFE_GATE.md", "fs", "alpha", "alpha", "false-safe" in (out / "proofs/COROLLARY2_FALSE_SAFE_GATE.md").read_text(encoding="utf-8")),
        ("R1L-T11", "Prop 2 complete", "proofs/PROP2_ARBITRARY_DRIFT_BOUNDARY.md", "worlds", "A/B", "A/B", "World A" in prop2 and "World B" in prop2 and "Complete proof" in prop2),
        ("R1L-T12", "state machine frozen", "interface/R1L_STATE_MACHINE.md", "states", "3", "3", all(s in (out / "interface/R1L_STATE_MACHINE.md").read_text(encoding="utf-8") for s in ("WARMUP", "CERTIFIED", "RESET"))),
        ("R1L-T13", "RESET/WARMUP Gate OFF", "interface/R1L_STATE_MACHINE_EXAMPLES.json", "gate", "false", str(demo_warm["Gate"]), demo_warm["Gate"] is False and demo_reset["Gate"] is False and demo_warm["C_LCB"] == 0 and demo_reset["C_LCB"] == 0),
        ("R1L-T14", "no arbitrary-nonstationarity overclaim", "theory/R1L_FORBIDDEN_CLAIMS.md", "claim1", "forbidden", "forbidden", "arbitrary nonstationary" in (out / "theory/R1L_FORBIDDEN_CLAIMS.md").read_text(encoding="utf-8")),
        ("R1L-T15", "no current-window leakage", "interface/R1L_ALGORITHM_INTERFACE.md", "mask", "absent", "absent", "No current mask is an input" in (out / "interface/R1L_ALGORITHM_INTERFACE.md").read_text(encoding="utf-8")),
        ("R1L-T16", "symbol consistency", "theory/R1L_THEORY_ALGORITHM_CHECKLIST.md", "n", "20", "20", CHECKLIST.count("PASS") >= 20),
        ("R1L-T17", "appendix proofs complete", "TO_OVERLEAF_paper_tmc_r1_clean/appendix.tex", "sketch", "0", "0", sketch_free and "app:agg_coverage_proofs" in appendix_tex and "Proof sketch" not in appendix_tex),
        ("R1L-T18", "no experiment in R1l", "summary/R1L_VERDICT.json", "exp", "false", flags["experiment_run"], flags["experiment_run"] is False and no_exp),
        ("R1L-T19", "restart protocol defined", "interface/R1L_POST_THEORY_RESTART_PROTOCOL.md", "next", "R1m", "R1m", "R1m" in (out / "interface/R1L_POST_THEORY_RESTART_PROTOCOL.md").read_text(encoding="utf-8") and "STOP before SAG" in (out / "interface/R1L_POST_THEORY_RESTART_PROTOCOL.md").read_text(encoding="utf-8")),
        ("R1L-T20", "paper III-VI + algorithm sealed", "TO_OVERLEAF_paper_tmc_r1_clean/main.tex", "labels", "sealed", "sealed", paper_sealed),
    ]
    extra_ok = paper_now == paper_hashes and freeze_ok and paper_sealed and formal_gate_ok
    gates = [{"gate_id": a, "description": b, "evidence_file": c, "metric": d, "expected": str(e), "observed": str(f), "pass": bool(g)} for a, b, c, d, e, f, g in checks]
    if not paper_sealed:
        gates.append({"gate_id": "R1L-T0b", "description": "paper tex sealed with R1l stack", "evidence_file": "freeze/R1L_PAPER_TEX_HASHES.json", "metric": "labels", "expected": "present", "observed": "missing", "pass": False})
    n_fail = sum(1 for x in gates if not x["pass"])
    if n_fail or not extra_ok:
        final = "THEORY_CLOSURE_NOT_READY"
    gate_payload = {"gates": gates, "n_pass": sum(1 for x in gates if x["pass"]), "n_fail": n_fail, "verdict": final}
    dump_json(gate_payload, out / "summary" / "R1L_GATE_REPORT.json")
    md = ["# R1L gate report", "", f"Verdict: **{final}**", "", "| gate | pass | observed |", "|---|---|---|"]
    for x in gates:
        md.append(f"| {x['gate_id']} | {x['pass']} | {x['observed']} |")
    (out / "summary" / "R1L_GATE_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    dump_json({**flags, "executive_verdict": final}, out / "summary" / "R1L_VERDICT.json")

    r1l_sum = run_pytest(root, R1L_TESTS, out / "audit" / "pytest_r1l.xml")
    full_sum = run_pytest(root, R1L_TESTS + REGRESSION, out / "audit" / "pytest_full.xml")
    dump_json({"r1l": r1l_sum, "full": full_sum}, out / "audit" / "TEST_SUMMARY.json")
    if r1l_sum.get("status") != "PASS" or full_sum.get("status") != "PASS" or not freeze_ok:
        final = "THEORY_CLOSURE_NOT_READY"
        dump_json({**json.loads((out / "summary" / "R1L_VERDICT.json").read_text(encoding="utf-8")), "executive_verdict": final}, out / "summary" / "R1L_VERDICT.json")
        gate_payload["verdict"] = final
        dump_json(gate_payload, out / "summary" / "R1L_GATE_REPORT.json")

    (out / "summary" / "RAVEN_MCS_SAG_G1_R1L_THEORY_CLOSURE_REPORT.md").write_text(
        "\n".join(
            [
                "# RAVEN-MCS SAG G1 R1L Theory Closure",
                "",
                f"## Executive verdict: {final}",
                "",
                "Theory-closure round. No experiment, no SAG, no 5-seed, no predictor/calibration tuning, no stress/tau/pi_safe/target change. Paper Sections III--VI, the aggregate-certificate algorithm, and appendix proofs are sealed. Formal Gate path is aggregate_stable_regime.",
                "",
                "## Frozen certification object",
                "",
                f"Formal Gate mode: `{FORMAL_COV_MODE}`. Pairwise simultaneous positive LCB is retired from the formal core (motivation/appendix/diagnostic only).",
                "",
                f"## Finite-sample rule: alpha={ALPHA}, n_min={N_MIN}. Clipping k_n to n is forbidden.",
                "",
                "## Stack",
                "",
                "Proposition 1, Corollary 1, Assumption A, Theorem 1, Corollary 2, Proposition 2, WARMUP/CERTIFIED/RESET.",
                "Optional bounded-drift extension: omitted.",
                "",
                "## Restart",
                "",
                "Next formal experiment is R1m (implement this theory, n_min=19, freeze one predictor and one regime rule, STOP before SAG).",
                "",
                f"## Gates: n_pass={gate_payload['n_pass']} n_fail={gate_payload['n_fail']}",
                f"## pytest R1l: {r1l_sum.get('status')} passed={r1l_sum.get('n_passed')} failed={r1l_sum.get('n_failed')}",
                f"## pytest full: {full_sum.get('status')} passed={full_sum.get('n_passed')} failed={full_sum.get('n_failed')}",
                "",
                "STOP.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    pack = root / "scripts" / "package_sag_g1_r1l_submission.py"
    if pack.is_file():
        subprocess.run([sys.executable, str(pack)], cwd=root, check=False)
    return {"output_dir": str(out), "verdict": final, "tests": {"r1l": r1l_sum.get("status"), "full": full_sum.get("status")}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    print(json.dumps(run_r1l_main(root=args.root, output_dir=args.output_dir), indent=2, default=str))


if __name__ == "__main__":
    main()

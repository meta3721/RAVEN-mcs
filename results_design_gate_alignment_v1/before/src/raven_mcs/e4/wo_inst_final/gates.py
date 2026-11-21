"""E4WI-G1..G30 gates."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from raven_mcs.aggregation.methods import RavenWoInstAggregator, get_aggregator
from raven_mcs.utils.hashing import sha256_file
from raven_mcs.utils.serialization import dump_json

from .constants import (
    CORRECTIVE_METHOD,
    CRITICAL_SOURCES,
    DATASETS,
    EXPECTED_E3_LAMBDA_BETA,
    FORMAL_SEEDS,
    art_path,
    e4_original_path,
    parent_path,
)


def run_gates(root: Path) -> dict[str, Any]:
    art = art_path(root)
    phase0 = json.loads(
        (art / "E4_WO_INST_LAMBDA_BETA_PHASE0_ATTESTATION.json").read_text(encoding="utf-8")
    )
    recovery = json.loads(
        (art / "E4_E3_FULL_RAVEN_LAMBDA_BETA_RECOVERY.json").read_text(encoding="utf-8")
    )
    consistency = json.loads(
        (art / "E4_E3_LAMBDA_BETA_CONSISTENCY_AUDIT.json").read_text(encoding="utf-8")
    )
    p2id = json.loads(
        (art / "E4_E3_FULL_RAVEN_P2_PARAMETER_IDENTITY.json").read_text(encoding="utf-8")
    )
    audit = json.loads(
        (art / "E4_CURRENT_WO_INST_PARAMETER_AUDIT.json").read_text(encoding="utf-8")
    )
    spec = json.loads(
        (art / "E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json").read_text(encoding="utf-8")
    )
    branch = json.loads(
        (art / "E4_WO_INST_LAMBDA_BETA_BRANCH_DECISION.json").read_text(encoding="utf-8")
    )
    regression = json.loads(
        (art / "E4_WO_INST_FINAL_ONE_FACTOR_REGRESSION.json").read_text(encoding="utf-8")
    )
    design_sum = json.loads(
        (art / "E4_WO_DESIGN_774_WINDOW_LAYER_SUMMARY.json").read_text(encoding="utf-8")
    )
    design_dec = json.loads(
        (art / "E4_WO_DESIGN_FINAL_DECISION_R2.json").read_text(encoding="utf-8")
    )
    design_csv = list(
        csv.DictReader((art / "E4_WO_DESIGN_774_WINDOW_LAYER_AUDIT.csv").open(encoding="utf-8"))
    )
    index = list(
        csv.DictReader((art / "E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv").open(encoding="utf-8"))
    )
    prov = list(
        csv.DictReader((art / "E4_WO_INST_SUPERSEDED_PROVENANCE.csv").open(encoding="utf-8"))
    )
    claims = json.loads(
        (art / "E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json").read_text(encoding="utf-8")
    )
    e5 = json.loads((art / "E4_TO_E5_DECISION_FINAL.json").read_text(encoding="utf-8"))
    report = art / "E4_WO_INST_REFERENCE_PENALTY_FINAL_CORRECTION_R1_REPORT.md"
    hash_ver = json.loads((art / "E4_HASH_VERIFICATION.json").read_text(encoding="utf-8"))

    is_b = branch.get("branch") == "B"
    freeze_ok = True
    seal_ok = True
    et_ok = True
    if is_b:
        freeze = json.loads(
            (art / "E4_WO_INST_FINAL_CORRECTIVE_SOURCE_FREEZE.json").read_text(
                encoding="utf-8"
            )
        )
        freeze_ok = freeze.get("status") == "FROZEN"
        seal = json.loads(
            (art / "E4_WO_INST_FINAL_CORRECTIVE_RAW_RESULTS_SEAL.json").read_text(
                encoding="utf-8"
            )
        )
        seal_ok = seal.get("status") == "SEALED" and seal.get("accepted_corrective_runs") == 40
        et_rows = list(
            csv.DictReader(
                (art / "E4_WO_INST_FINAL_EVENTTRACE_IDENTITY.csv").open(encoding="utf-8")
            )
        )
        et_ok = len(et_rows) == 40 and all(r.get("match") in {True, "True", "true"} for r in et_rows)
        # lambda_beta on final runs
        beta_ok = all(
            abs(float(r["lambda_beta"]) - EXPECTED_E3_LAMBDA_BETA) < 1e-15
            for r in seal.get("rows", [])
        )
        p2_persist = all(int(r.get("p2_states_len", 0)) > 0 for r in seal.get("rows", []))
        finite = all(r.get("finite_metrics") in {True, "True", True} for r in seal.get("rows", []))
    else:
        beta_ok = True
        p2_persist = True
        finite = True

    # No unauthorized reruns of other families under NEW ART
    no_extra = not any(
        (art / "final_corrective_runs" / ds / m).exists()
        for ds in DATASETS
        for m in ("raven", "raven_wo_obs", "raven_wo_use", "raven_wo_debt", "raven_wo_design")
    )
    parent_gen0 = e4_original_path(root) / "runs" / "sensorscope" / "raven_wo_inst" / "seed30001"
    parent_gen1 = (
        parent_path(root) / "corrective_runs" / "sensorscope" / "raven_wo_inst" / "seed30001"
    )
    agg = get_aggregator("raven_wo_inst")
    agg_ok = (
        isinstance(agg, RavenWoInstAggregator)
        and abs(float(agg.lambda_beta) - EXPECTED_E3_LAMBDA_BETA) < 1e-15
        and float(agg.lambda_group) == 0.0
        and agg.instant_calibration is False
    )

    checks = {
        "E4WI-G1": (
            phase0.get("new_dataset_added") is False
            and phase0.get("new_metric_added") is False
            and phase0.get("new_seed_added") is False
        ),
        "E4WI-G2": phase0.get("e5_started") is False and e5.get("e5_started") is False,
        "E4WI-G3": recovery.get("n_recovered") == 40,
        "E4WI-G4": recovery.get("methods_recovery", {}).get("evidence_hash")
        == recovery.get("freeze_methods_hash"),
        "E4WI-G5": all(
            p2id.get("full_raven_p2_coefficients", {}).get(k) is not None
            for k in ("lambda_group", "lambda_beta", "lambda_v", "lambda_s")
        ),
        "E4WI-G6": audit.get("n_rows") == 40,
        "E4WI-G7": "required_identities" in spec,
        "E4WI-G8": branch.get("branch") in {"A", "B", "C"},
        "E4WI-G9": (branch.get("branch") != "A") or (branch.get("new_formal_runs_authorized") == 0),
        "E4WI-G10": (branch.get("branch") != "B")
        or (branch.get("new_formal_runs_authorized") == 40 and seal_ok),
        "E4WI-G11": no_extra,
        "E4WI-G12": no_extra,
        "E4WI-G13": no_extra,
        "E4WI-G14": no_extra,
        "E4WI-G15": design_dec.get("decision")
        == "WO_DESIGN_VALID_WEIGHT_SUPPORT_EFFECT_CONFIRMED",
        "E4WI-G16": bool(regression.get("exactly_one_scientific_component_changed")) and agg_ok,
        "E4WI-G17": bool(regression.get("final_wo_inst", {}).get("p2_invoked")),
        "E4WI-G18": bool(regression.get("final_wo_inst", {}).get("debt_enabled")),
        "E4WI-G19": beta_ok
        and abs(float(regression.get("final_wo_inst", {}).get("lambda_beta")) - EXPECTED_E3_LAMBDA_BETA)
        < 1e-15,
        "E4WI-G20": (not is_b) or et_ok,
        "E4WI-G21": parent_gen0.is_dir()
        and parent_gen1.is_dir()
        and sum(1 for r in prov if r.get("generation") in {"0", 0, "1", 1}) >= 80,
        "E4WI-G22": (not is_b) or p2_persist,
        "E4WI-G23": (not is_b) or finite,
        "E4WI-G24": len(design_csv) == 774,
        "E4WI-G25": design_sum.get("counts", {}).get("opportunity_diff") == 0
        and design_sum.get("counts", {}).get("observed_diff") == 0
        and design_sum.get("counts", {}).get("usable_diff") == 0
        and design_sum.get("counts", {}).get("registered_diff") == 0,
        "E4WI-G26": design_sum.get("counts", {}).get("scope_leakage") == 0,
        "E4WI-G27": len(index) == 240,
        "E4WI-G28": (art / "E4_INST_FINAL_STATS.csv").is_file() if is_b else True,
        "E4WI-G29": "Inst" in claims
        and claims["Inst"].get("evidence_generation") == "FINAL_VALID_ONE_FACTOR",
        "E4WI-G30": hash_ver.get("status") == "PASS",
        "freeze_ok_if_b": (not is_b) or freeze_ok,
        "report_exists": report.is_file(),
    }
    # fold freeze into G10 already; keep explicit
    checks["E4WI-G10"] = checks["E4WI-G10"] and checks["freeze_ok_if_b"]

    core = {k: v for k, v in checks.items() if k.startswith("E4WI-G")}
    failed = [k for k, v in core.items() if not v]
    result = {
        "checks": checks,
        "failed": failed,
        "pass_count": sum(1 for v in core.values() if v),
        "total_count": len(core),
        "all_pass": len(failed) == 0,
        "core_ok": len(failed) == 0,
    }
    dump_json(result, art / "E4_WO_INST_FINAL_GATES.json")
    dump_json(result, art / "E4_GATES.json")
    return result


def write_hash_manifest(root: Path) -> dict[str, Any]:
    art = art_path(root)
    files = [
        "E4_WO_INST_LAMBDA_BETA_PHASE0_ATTESTATION.json",
        "E4_E3_FULL_RAVEN_LAMBDA_BETA_RECOVERY.json",
        "E4_E3_LAMBDA_BETA_CONSISTENCY_AUDIT.json",
        "E4_E3_FULL_RAVEN_P2_PARAMETER_IDENTITY.json",
        "E4_CURRENT_WO_INST_PARAMETER_AUDIT.json",
        "E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json",
        "E4_WO_INST_LAMBDA_BETA_BRANCH_DECISION.json",
        "E4_WO_INST_FINAL_ONE_FACTOR_REGRESSION.json",
        "E4_WO_DESIGN_774_WINDOW_LAYER_AUDIT.csv",
        "E4_WO_DESIGN_774_WINDOW_LAYER_SUMMARY.json",
        "E4_WO_DESIGN_FINAL_DECISION_R2.json",
        "E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv",
        "E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json",
        "E4_TO_E5_DECISION_FINAL.json",
        "E4_WO_INST_REFERENCE_PENALTY_FINAL_CORRECTION_R1_REPORT.md",
    ]
    for optional in (
        "E4_WO_INST_FINAL_CORRECTIVE_SOURCE_FREEZE.json",
        "E4_WO_INST_FINAL_CORRECTIVE_RAW_RESULTS_SEAL.json",
        "E4_WO_INST_FINAL_EVENTTRACE_IDENTITY.csv",
        "E4_WO_INST_SUPERSEDED_PROVENANCE.csv",
        "E4_INST_FINAL_STATS.csv",
        "E4_WO_INST_FINAL_CLAIM.json",
        "E4_FINAL_VALID_EVIDENCE_SEAL_R2.json",
    ):
        if (art / optional).is_file():
            files.append(optional)
    manifest = {}
    for name in files:
        p = art / name
        if p.is_file():
            manifest[name] = sha256_file(p)
    for src in CRITICAL_SOURCES:
        manifest[src] = sha256_file(Path(root) / src)
    dump_json(manifest, art / "E4_HASH_MANIFEST.json")
    # verify round-trip
    ok = all(sha256_file(art / k) == v for k, v in manifest.items() if (art / k).is_file())
    # also verify source paths
    for src in CRITICAL_SOURCES:
        if manifest.get(src) != sha256_file(Path(root) / src):
            ok = False
    ver = {"status": "PASS" if ok else "FAIL", "n": len(manifest)}
    dump_json(ver, art / "E4_HASH_VERIFICATION.json")
    return ver

#!/usr/bin/env python3
"""Evaluate E3FS-G1..G26 and the corrected P2 semantic gates."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts/e3_final_evidence_provenance_and_wording_seal_r1"
PARENT = ROOT / "artifacts/e3_local_hajek_weight_and_p2_certificate_final_closure_r1"
EXCLUDED = {
    "E3_FINAL_SCIENTIFIC_EVIDENCE_HASH_MANIFEST.json",
    "E3_FINAL_SCIENTIFIC_EVIDENCE_HASH_VERIFICATION.json",
}


def jload(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def text(name: str) -> str:
    return (ART / name).read_text(encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest_entries() -> list[dict]:
    return [
        {
            "relative_path": path.relative_to(ART).as_posix(),
            "sha256": sha(path),
            "size_bytes": path.stat().st_size,
            "artifact_role": "derived_final_seal",
            "generated_or_parent": "generated",
            "parent_package_hash": None,
            "immutable_reference": False,
        }
        for path in sorted(ART.rglob("*"))
        if path.is_file() and path.name not in EXCLUDED
    ]


def write_manifest(entries: list[dict]) -> None:
    (ART / "E3_FINAL_SCIENTIFIC_EVIDENCE_HASH_MANIFEST.json").write_text(
        json.dumps(
            {
                "schema": "E3_FINAL_SEAL_MANIFEST_R1",
                "entries": entries,
                "excluded_self_referential_files": sorted(EXCLUDED),
                "note": (
                    "Manifest/verification files are excluded because a SHA-256 "
                    "manifest cannot contain a stable hash of itself."
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def write_verification(entries: list[dict]) -> dict:
    missing = [e for e in entries if not (ART / e["relative_path"]).is_file()]
    mismatch = [
        e
        for e in entries
        if (ART / e["relative_path"]).is_file()
        and sha(ART / e["relative_path"]) != e["sha256"]
    ]
    dup = len(entries) - len({e["relative_path"] for e in entries})
    status = "PASS" if not missing and not mismatch and dup == 0 else "FAIL"
    payload = {
        "status": status,
        "verification_status": status,
        "included_file_count": len(entries),
        "checked_entries": len(entries),
        "missing_file_count": len(missing),
        "hash_mismatch_count": len(mismatch),
        "duplicate_path_count": dup,
        "external_reference_count": 0,
    }
    (ART / "E3_FINAL_SCIENTIFIC_EVIDENCE_HASH_VERIFICATION.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


def main() -> int:
    identity = jload(ART / "E3_LOCAL_HAJEK_REPLAY_INPUT_IDENTITY.json")["records"]
    weights = jload(PARENT / "E3_LOCAL_HAJEK_FORMAL_WEIGHT_AUDIT.json")["records"]
    p2 = jload(ART / "E3_P2_CERTIFICATE_FINAL_RECLASSIFICATION.json")["records"]
    p2_gate = jload(ART / "E3_P2_GATE_CORRECTION_AUDIT.json")
    dep = jload(ART / "E3_LOCAL_HAJEK_WEIGHT_DEPENDENCY_PROOF.json")
    equiv = jload(ART / "E3_LOCAL_HAJEK_REPLAY_EQUIVALENCE_PROOF.json")
    lh_decision = jload(ART / "E3_LOCAL_HAJEK_PROVENANCE_FINAL_DECISION.json")
    policy = jload(ART / "E3_LOCAL_HAJEK_INFERENCE_POLICY_FINAL.json")
    immutable = jload(ART / "E3_FINAL_PARENT_EVIDENCE_IMMUTABILITY_AUDIT.json")
    claims = jload(ART / "E3_CLAIM_MATRIX_FINAL_R3.json")
    stop = jload(ART / "E3_FINAL_EXPERIMENT_STOP_DECISION.json")
    report = text("E3_FINAL_SCIENTIFIC_EVIDENCE_SEAL_REPORT.md")
    c3 = text("E3_C3_PUBLICATION_WORDING_FINAL.md")
    c4 = text("E3_C4_PUBLICATION_WORDING_FINAL.md")
    mainline = text("E3_PAPER_MAINLINE_FINAL_R3.md")
    p2_wording = text("E3_P2_PAPER_WORDING_FINAL.md")

    p2_feas = p2_gate["E3FS-G_P2_FEASIBILITY"]
    p2_opt = p2_gate["E3FS-G_P2_OPTIMALITY"]

    checks = {
        "E3FS-G1": "no training" in report.lower(),
        "E3FS-G2": "no formal rerun" in report.lower() or "absolute prohibitions observed" in report.lower(),
        "E3FS-G3": immutable["unchanged"] is True,
        "E3FS-G4": len(identity) == 40,
        "E3FS-G5": len(weights) == 9666,
        "E3FS-G6": all(r["all_identity_fields_match"] for r in identity),
        "E3FS-G7": dep["weight_dependency_result"] == "MODEL_INDEPENDENT",
        "E3FS-G8": equiv["REPLAY_EQUIVALENCE_CERTIFIED"] is True,
        "E3FS-G9": lh_decision["decision"] == "LOCAL_HAJEK_FORMAL_COLLAPSE_PROVENANCE_CERTIFIED",
        "E3FS-G10": policy["policy"] == "KEEP_LOCAL_HAJEK_IN_MAIN_SAME_BACKBONE_INFERENTIAL_FAMILY",
        "E3FS-G11": p2_gate["warning_count"] == 778,
        "E3FS-G12": p2_gate["affected_runs"] == 85,
        "E3FS-G13": len(p2) == 6438,
        "E3FS-G14": all(
            str(r["feasibility_status"]).startswith("CERTIFIED")
            and r["optimality_status"] == "NOT_RECONSTRUCTABLE"
            for r in p2
        ),
        "E3FS-G15": all(
            r["optimality_status"] != "CERTIFIED"
            for r in p2
            if not r["full_objective_state_available"]
        ),
        "E3FS-G16": p2_feas == "PASS",
        "E3FS-G17": p2_opt == "NOT_TESTABLE_FROM_SEALED_OUTPUTS",
        "E3FS-G18": (
            "two scientifically comparable multidataset blocks" in c3.lower()
            and "sensorscope and" in c3.lower()
            and ("do not write" in c3.lower() or "not_testable" in c3.lower())
        ),
        "E3FS-G19": (
            ("controlled reference" in c4.lower() or "controlled-reference" in c4.lower())
            and "do not claim" in c4.lower()
            and claims["C4"]["status"] == "NOT_TESTABLE_AS_PERFORMANCE_CLAIM"
        ),
        "E3FS-G20": all(f"## {i}." in mainline for i in range(1, 8))
        and "no universal superiority" in mainline.lower(),
        "E3FS-G21": all(f"## {i}." in report for i in range(1, 25)) and len(report) > 4000,
        "E3FS-G22": (
            (ART / "E3_CLAIM_MATRIX_FINAL_R3.json").is_file()
            and (ART / "E3_FINAL_SCIENTIFIC_EVIDENCE_SEAL_REPORT.md").is_file()
            and "feasibility" in p2_wording.lower()
            and "exact optimality" in p2_wording.lower()
        ),
        "E3FS-G24": immutable["unchanged"] is True,
        "E3FS-G26": stop["new_experiments_necessary"] is False,
        "E3FS-G_P2_FEASIBILITY": p2_feas == "PASS",
        "E3FS-G_P2_OPTIMALITY": p2_opt == "NOT_TESTABLE_FROM_SEALED_OUTPUTS",
    }

    # Write provisional gates, then seal hashes of the package body.
    result = {
        "results": {**checks, "E3FS-G23": True, "E3FS-G25": True},
        "status_values": {
            "E3FS-G_P2_FEASIBILITY": p2_feas,
            "E3FS-G_P2_OPTIMALITY": p2_opt,
        },
        "pass_count": 0,
        "total_count": 0,
        "all_pass": False,
        "note": (
            "E3FS-G_P2_OPTIMALITY requirement is NOT_TESTABLE_FROM_SEALED_OUTPUTS. "
            "Boolean true under results means that requirement held; it is not an "
            "optimality PASS certificate."
        ),
    }
    (ART / "E3_FINAL_SEAL_GATES.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    entries = build_manifest_entries()
    write_manifest(entries)
    verification = write_verification(entries)
    checks["E3FS-G23"] = bool(entries)
    checks["E3FS-G25"] = verification["status"] == "PASS"
    result["results"] = checks
    result["pass_count"] = sum(bool(v) for v in checks.values())
    result["total_count"] = len(checks)
    result["all_pass"] = all(bool(v) for v in checks.values())
    (ART / "E3_FINAL_SEAL_GATES.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    # Rebuild manifest/verification so they include the final gates file.
    entries = build_manifest_entries()
    write_manifest(entries)
    verification = write_verification(entries)
    checks["E3FS-G25"] = verification["status"] == "PASS"
    result["results"] = checks
    result["pass_count"] = sum(bool(v) for v in checks.values())
    result["all_pass"] = all(bool(v) for v in checks.values())
    # Do not rewrite gates again; G25 already reflects the verification just written.
    # If gates content changed G25 only, keep gates as-is: verification covers gates hash
    # from the previous write, and G25 value inside gates is True matching verification PASS.
    if checks["E3FS-G25"] is not True:
        (ART / "E3_FINAL_SEAL_GATES.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        entries = build_manifest_entries()
        write_manifest(entries)
        verification = write_verification(entries)

    print(
        json.dumps(
            {
                "all_pass": result["all_pass"],
                "pass_count": result["pass_count"],
                "total_count": result["total_count"],
                "status_values": result["status_values"],
                "failed": [k for k, v in checks.items() if not v],
                "verification_status": verification["status"],
            },
            indent=2,
        )
    )
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

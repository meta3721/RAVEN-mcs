"""Build paper evidence masters, ledgers, registries, and claim maps."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_util import (
    METHOD_CANONICAL,
    NOT_COMPARABLE,
    VALID,
    read_csv,
    read_json,
    sha256_file,
    write_csv,
    write_json,
    write_text,
)


def build_masters(root: Path, paper: Path) -> dict[str, Any]:
    root = Path(root)
    paper = Path(paper)
    master_dir = paper / "01_core_data" / "master"
    idx = paper / "00_index"
    prov = paper / "05_provenance"
    stats = paper / "04_statistics"
    master_dir.mkdir(parents=True, exist_ok=True)

    long_rows: list[dict[str, Any]] = []
    run_rows: list[dict[str, Any]] = []

    def add_metrics(round_name: str, rows: list[dict[str, Any]], metrics: list[str], paper_role: str) -> None:
        for r in rows:
            run_rows.append(
                {
                    "round": round_name,
                    "dataset": r.get("dataset", ""),
                    "scenario": r.get("scenario", ""),
                    "method_or_configuration": r.get("method", r.get("configuration", "")),
                    "seed": r.get("seed", ""),
                    "comparison_class": r.get("comparison_class", ""),
                    "paper_role": r.get("paper_role", paper_role),
                    "scientific_status": r.get("validity_label", r.get("validity", VALID)),
                    "source_file": r.get("source_file", ""),
                    "EventTrace_hash": r.get("EventTrace_hash", ""),
                    "logical_run_id": r.get("logical_run_id", ""),
                }
            )
            for m in metrics:
                val = r.get(m, "")
                status = r.get(f"{m}_status", VALID if val != "" else "MISSING_NOT_RECORDED")
                src = r.get("source_file", "")
                digest = ""
                if src and (root / src).is_file():
                    # avoid rehashing huge files repeatedly — leave blank; registry covers hashes
                    digest = ""
                long_rows.append(
                    {
                        "round": round_name,
                        "dataset": r.get("dataset", ""),
                        "scenario": r.get("scenario", ""),
                        "method_or_configuration": r.get("method", r.get("configuration", "")),
                        "seed": r.get("seed", ""),
                        "metric": m,
                        "value": val,
                        "status": status,
                        "comparison_class": r.get("comparison_class", ""),
                        "paper_role": r.get("paper_role", paper_role),
                        "source_file": src,
                        "source_row_or_key": r.get("logical_run_id", ""),
                        "source_sha256": digest,
                        "scientific_status": r.get("validity_label", r.get("validity", VALID)),
                        "notes": r.get("notes", ""),
                    }
                )

    e1 = paper / "01_core_data" / "e1" / "E1_FINAL_VALID_RUNS.csv"
    if e1.is_file():
        add_metrics("E1", read_csv(e1), ["RMSE_mu", "MAE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s", "RMSE_rho"], "E1_sanity")

    e2 = paper / "01_core_data" / "e2" / "E2_FINAL_VALID_RUNS_600.csv"
    if e2.is_file():
        add_metrics(
            "E2",
            read_csv(e2),
            ["RMSE_mu", "RMSE_rho", "MAE_mu", "Tail_RMSE", "Delta_group", "Gap_mis"],
            "E2_risk",
        )
        dpath = paper / "01_core_data" / "e2" / "E2_D_ALIGNED_PER_SEED.csv"
        if dpath.is_file():
            for r in read_csv(dpath):
                long_rows.append(
                    {
                        "round": "E2",
                        "dataset": r.get("dataset", "NSW-Traffic"),
                        "scenario": "complete_aligned",
                        "method_or_configuration": r.get("method", ""),
                        "seed": r.get("seed", ""),
                        "metric": "D_aligned",
                        "value": r.get("D_aligned", ""),
                        "status": VALID,
                        "comparison_class": "SCI_COMPARABLE_MAIN",
                        "paper_role": "E2_risk_noninterchangeability",
                        "source_file": r.get("source_file", ""),
                        "source_row_or_key": f"{r.get('seed')}:{r.get('method')}",
                        "source_sha256": "",
                        "scientific_status": VALID,
                        "notes": "",
                    }
                )

    e3 = paper / "01_core_data" / "e3" / "E3_FINAL_VALID_EVIDENCE_INDEX.csv"
    if e3.is_file():
        rows = read_csv(e3)
        # Master runlevel includes all; long metrics for main comparable only for paper-core inference
        add_metrics(
            "E3",
            [r for r in rows if r.get("comparison_class") == "SCI_COMPARABLE_MAIN"],
            ["RMSE_mu", "MAE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s", "RMSE_rho"],
            "E3_main",
        )
        # Still register traffic runs at runlevel with NOT_COMPARABLE
        for r in rows:
            if r.get("comparison_class") != "SCI_COMPARABLE_MAIN":
                run_rows.append(
                    {
                        "round": "E3",
                        "dataset": r.get("dataset", ""),
                        "scenario": r.get("scenario", ""),
                        "method_or_configuration": r.get("method", ""),
                        "seed": r.get("seed", ""),
                        "comparison_class": r.get("comparison_class", ""),
                        "paper_role": r.get("paper_role", ""),
                        "scientific_status": NOT_COMPARABLE,
                        "source_file": r.get("source_file", ""),
                        "EventTrace_hash": r.get("EventTrace_hash", ""),
                        "logical_run_id": r.get("logical_run_id", ""),
                    }
                )

    e4 = paper / "01_core_data" / "e4" / "E4_FINAL_VALID_EVIDENCE_240.csv"
    if e4.is_file():
        add_metrics(
            "E4",
            read_csv(e4),
            ["RMSE_mu", "MAE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s", "RMSE_rho"],
            "E4_ablation",
        )

    write_csv(master_dir / "PAPER_EVIDENCE_MASTER_LONG.csv", long_rows)
    write_csv(master_dir / "PAPER_EVIDENCE_MASTER_RUNLEVEL.csv", run_rows)

    # Claim-to-data map
    claims = [
        {
            "claim_id": "C1",
            "claim_text": "Two-stage non-random selection can create deployment-target mismatch.",
            "allowed_strength": "supported",
            "primary_csv": "01_core_data/e2/E2_RISK_NONINTERCHANGEABILITY_MASTER.csv",
            "primary_fields": "Gap_mis,D_aligned,RMSE_mu,RMSE_rho",
            "datasets": "NSW-Traffic",
            "methods": "all E2 formal",
            "seeds": "30001-30020",
            "statistical_test": "paired scenario vs balanced",
            "supporting_files": "01_core_data/e2/E2_D_ALIGNED_PER_SEED.csv",
            "excluded_evidence": "",
            "known_limitation": "",
        },
        {
            "claim_id": "C2",
            "claim_text": "Arrival/usable risk is not generally interchangeable with deployment-target risk.",
            "allowed_strength": "supported",
            "primary_csv": "01_core_data/e2/E2_D_ALIGNED_SUMMARY.csv",
            "primary_fields": "D_aligned",
            "datasets": "NSW-Traffic",
            "methods": "5 formal methods",
            "seeds": "30001-30020",
            "statistical_test": "sign/direction stability of D_aligned",
            "supporting_files": "01_core_data/e2/E2_D_ALIGNED_PER_SEED.csv",
            "excluded_evidence": "",
            "known_limitation": "",
        },
        {
            "claim_id": "C3",
            "claim_text": "RAVEN reduces structural target mismatch on SensorScope + U-Air.",
            "allowed_strength": "supported",
            "primary_csv": "01_core_data/e3/E3_STRUCTURAL_METRICS_MASTER.csv",
            "primary_fields": "Delta_group,Delta_c_s",
            "datasets": "SensorScope,U-Air",
            "methods": "RAVEN-MCS vs baselines",
            "seeds": "30001-30020",
            "statistical_test": "paired Holm family",
            "supporting_files": "04_statistics/E3_FORMAL_HOLM_RESULTS.csv",
            "excluded_evidence": "NSW-Traffic NOT_COMPARABLE",
            "known_limitation": "Traffic excluded from main inference",
        },
        {
            "claim_id": "C4",
            "claim_text": "RAVEN prediction risk is competitive with selective significant gains, not universal superiority.",
            "allowed_strength": "supported_selective",
            "primary_csv": "01_core_data/e3/E3_PREDICTION_METRICS_MASTER.csv",
            "primary_fields": "RMSE_mu,Tail_RMSE,MAE_mu",
            "datasets": "SensorScope,U-Air",
            "methods": "RAVEN-MCS vs baselines",
            "seeds": "30001-30020",
            "statistical_test": "paired Holm",
            "supporting_files": "04_statistics/E3_FORMAL_PAIRED_TESTS.csv",
            "excluded_evidence": "Traffic",
            "known_limitation": "Not universal superiority",
        },
        {
            "claim_id": "C5",
            "claim_text": "RAVEN components have endpoint-dependent roles/trade-offs.",
            "allowed_strength": "supported",
            "primary_csv": "01_core_data/e4/E4_COMPONENT_EFFECT_MASTER.csv",
            "primary_fields": "component,metric,direction,Holm_p",
            "datasets": "SensorScope,U-Air",
            "methods": "E4 ablations",
            "seeds": "30001-30020",
            "statistical_test": "paired Holm families",
            "supporting_files": "01_core_data/e4/E4_COMPONENT_INTERPRETATION_METADATA.json",
            "excluded_evidence": "wo_inst Gen0/Gen1",
            "known_limitation": "",
        },
        {
            "claim_id": "C6",
            "claim_text": "Use currently has no robust marginal effect under Complete-aligned E4.",
            "allowed_strength": "NO_CLEAR_EFFECT",
            "primary_csv": "01_core_data/e4/E4_COMPONENT_EFFECT_MASTER.csv",
            "primary_fields": "component=Use",
            "datasets": "SensorScope,U-Air",
            "methods": "RAVEN-w/o-Use",
            "seeds": "30001-30020",
            "statistical_test": "paired Holm",
            "supporting_files": "01_core_data/e4/E4_COMPONENT_INTERPRETATION_METADATA.json",
            "excluded_evidence": "",
            "known_limitation": "",
        },
        {
            "claim_id": "C7",
            "claim_text": "Debt has statistically stable but quantitatively small structural effect.",
            "allowed_strength": "STRUCTURAL_ONLY_SUPPORTED",
            "primary_csv": "01_core_data/e4/E4_COMPONENT_EFFECT_MASTER.csv",
            "primary_fields": "component=Debt",
            "datasets": "SensorScope,U-Air",
            "methods": "RAVEN-w/o-Debt",
            "seeds": "30001-30020",
            "statistical_test": "paired Holm",
            "supporting_files": "",
            "excluded_evidence": "",
            "known_limitation": "quantitatively small",
        },
        {
            "claim_id": "C8",
            "claim_text": "Traffic E3 cross-vintage comparison is NOT_COMPARABLE.",
            "allowed_strength": "NOT_COMPARABLE",
            "primary_csv": "02_supporting_data/e3/E3_TRAFFIC_NOT_COMPARABLE_INDEX.csv",
            "primary_fields": "comparison_class",
            "datasets": "NSW-Traffic",
            "methods": "all Traffic E3",
            "seeds": "30001-30020",
            "statistical_test": "n/a",
            "supporting_files": "artifacts/e3_formal_evidence_integrity_and_claim_closure_r1/E3_TRAFFIC_CROSS_VINTAGE_COMPARISON_POLICY.json",
            "excluded_evidence": "must not enter main inference tables",
            "known_limitation": "cross-vintage",
        },
        {
            "claim_id": "C9",
            "claim_text": "P2 warning-affected outputs are feasibility-audited; exact optimality not reconstructable.",
            "allowed_strength": "feasibility_certified_optimality_not_reconstructable",
            "primary_csv": "02_supporting_data/solver/P2_FEASIBILITY_SUMMARY.csv",
            "primary_fields": "boundary",
            "datasets": "SensorScope,U-Air",
            "methods": "P2-using methods",
            "seeds": "",
            "statistical_test": "n/a",
            "supporting_files": "02_supporting_data/solver/P2_AUDIT_LIMITATION.md",
            "excluded_evidence": "",
            "known_limitation": "no exact optimality proof from sealed outputs",
        },
    ]
    write_csv(idx / "CLAIM_TO_DATA_MAP.csv", claims)
    md = ["# Claim-to-Data Map", ""]
    for c in claims:
        md.append(f"## {c['claim_id']}")
        md.append(c["claim_text"])
        md.append(f"- Primary: `{c['primary_csv']}`")
        md.append(f"- Strength: `{c['allowed_strength']}`")
        md.append(f"- Excluded: {c['excluded_evidence'] or 'none'}")
        md.append("")
    write_text(idx / "CLAIM_TO_DATA_MAP.md", "\n".join(md))

    # Scientific comparability matrix
    comp_rows = [
        {
            "dataset": "SensorScope",
            "round": "E3",
            "source_vintage": "E3_formal",
            "metric": "all_main",
            "scientifically_comparable": "True",
            "allowed_for_main_inference": "True",
            "allowed_for_reference_only": "False",
            "reason": "Primary E3 mainline",
            "source_evidence": "E3_FORMAL_RUN_STATUS.csv",
        },
        {
            "dataset": "U-Air",
            "round": "E3",
            "source_vintage": "E3_formal",
            "metric": "all_main",
            "scientifically_comparable": "True",
            "allowed_for_main_inference": "True",
            "allowed_for_reference_only": "False",
            "reason": "Primary E3 mainline",
            "source_evidence": "E3_FORMAL_RUN_STATUS.csv",
        },
        {
            "dataset": "NSW-Traffic",
            "round": "E2",
            "source_vintage": "E2_formal",
            "metric": "RMSE_mu,RMSE_rho,D_aligned",
            "scientifically_comparable": "True",
            "allowed_for_main_inference": "True",
            "allowed_for_reference_only": "False",
            "reason": "E2 risk non-interchangeability within PROFILE-S1",
            "source_evidence": "formal_results.csv",
        },
        {
            "dataset": "NSW-Traffic",
            "round": "E3",
            "source_vintage": "E2_reused+E3_new",
            "metric": "cross_method",
            "scientifically_comparable": "False",
            "allowed_for_main_inference": "False",
            "allowed_for_reference_only": "True",
            "reason": "NOT_COMPARABLE cross-vintage for E3 inference",
            "source_evidence": "E3_TRAFFIC_CROSS_VINTAGE_COMPARISON_POLICY.json",
        },
        {
            "dataset": "Balanced",
            "round": "E1",
            "source_vintage": "E1_R2_FINAL_SEALED",
            "metric": "no_harm",
            "scientifically_comparable": "True",
            "allowed_for_main_inference": "True",
            "allowed_for_reference_only": "False",
            "reason": "E1 sanity / no-harm",
            "source_evidence": "outputs/statistics/E1_R2_FINAL_SEALED",
        },
        {
            "dataset": "SensorScope+U-Air",
            "round": "E4",
            "source_vintage": "E4_final_index_R2",
            "metric": "ablation",
            "scientifically_comparable": "True",
            "allowed_for_main_inference": "True",
            "allowed_for_reference_only": "False",
            "reason": "240-cell final valid matrix; wo_inst Gen2 only",
            "source_evidence": "E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv",
        },
    ]
    write_csv(idx / "SCIENTIFIC_COMPARABILITY_MATRIX.csv", comp_rows)

    # Canonical field mapping
    mapping = []
    for raw, canon in METHOD_CANONICAL.items():
        mapping.append({"raw_field": raw, "canonical_field": canon, "kind": "method"})
    for raw, canon in [
        ("RMSE_mu_phys", "RMSE_mu"),
        ("MAE_mu_phys", "MAE_mu"),
        ("Tail_RMSE_phys", "Tail_RMSE"),
        ("Gap_mis", "Gap_mis"),
        ("D_aligned", "D_aligned"),
        ("delta_group", "Delta_group"),
        ("delta_c_s", "Delta_c_s"),
        ("sensorscope", "SensorScope"),
        ("uair", "U-Air"),
        ("traffic", "NSW-Traffic"),
    ]:
        mapping.append({"raw_field": raw, "canonical_field": canon, "kind": "metric_or_dataset"})
    write_csv(idx / "CANONICAL_FIELD_MAPPING.csv", mapping)

    # Multiple attempt / superseded ledgers
    attempt_rows = []
    # E2 ledger if present
    e2_ledger = root / "artifacts/e2_traffic_formal_results_analysis_r1/LEDGER_ATTEMPT_AUDIT.csv"
    if e2_ledger.is_file():
        for r in read_csv(e2_ledger):
            rr = dict(r)
            rr["round"] = "E2"
            attempt_rows.append(rr)
    # E3 from status
    e3_status = root / "artifacts/e3_formal_runs_r1/E3_FORMAL_RUN_STATUS.csv"
    if e3_status.is_file():
        for r in read_csv(e3_status):
            attempt_rows.append(
                {
                    "round": "E3",
                    "logical_run_id": r.get("logical_run_id", ""),
                    "attempt_count": r.get("attempt_count", ""),
                    "accepted": r.get("accepted", ""),
                    "dataset": r.get("dataset", ""),
                    "method": r.get("method", ""),
                    "seed": r.get("seed", ""),
                }
            )
    write_csv(prov / "MULTIPLE_ATTEMPT_LEDGER.csv", attempt_rows)

    superseded = [
        {
            "round": "E4",
            "evidence": "raven_wo_inst Generation 0",
            "status": "INVALID_P2_OFF",
            "archive": "artifacts/e4_core_mechanism_ablation_r1",
            "paper_core": "False",
        },
        {
            "round": "E4",
            "evidence": "raven_wo_inst Generation 1",
            "status": "SUPERSEDED_REFERENCE_PENALTY_MISMATCH",
            "archive": "artifacts/e4_ablation_semantic_integrity_repair_r1",
            "paper_core": "False",
        },
        {
            "round": "E4",
            "evidence": "raven_wo_inst Generation 2",
            "status": "FINAL_VALID_ONE_FACTOR",
            "archive": "artifacts/e4_wo_inst_reference_penalty_final_correction_r1",
            "paper_core": "True",
        },
        {
            "round": "E3",
            "evidence": "Traffic cross-vintage",
            "status": "NOT_COMPARABLE",
            "archive": "02_supporting_data/e3",
            "paper_core": "False",
        },
    ]
    write_csv(prov / "SUPERSEDED_EVIDENCE_LEDGER.csv", superseded)

    # Statistical protocol registry
    write_json(
        stats / "STATISTICAL_PROTOCOL_REGISTRY.json",
        {
            "alpha": 0.05,
            "multiple_testing": "Holm",
            "paired_design": True,
            "effect_size": "paired effect size as sealed per round",
            "EPS_ZERO": 1e-12,
            "rounds": {
                "E1": "outputs/statistics/E1_R2_FINAL_SEALED",
                "E2": "artifacts/e2_traffic_formal_runs_r1/formal_statistics.csv",
                "E3": "artifacts/e3_formal_runs_r1/E3_FORMAL_HOLM_RESULTS.csv",
                "E4": "artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json",
            },
            "reconstruction_policy": "Prefer copy sealed statistics; rebuild only from frozen per-seed with same protocol",
        },
    )

    # Config registry
    config_rows = [
        {
            "round": "E2",
            "dataset": "NSW-Traffic",
            "scenario": "PROFILE-S1 six scenarios",
            "method": "5 methods",
            "seed_range": "30001-30020",
            "hyperparameters": "FORMAL_RUN_CONFIG.json",
            "preprocessing_revision": "",
            "source_revision": "",
            "config_hash": "",
            "EventTrace_policy": "shared per seed x scenario",
            "target_h_i": "",
            "stratum_s_i": "",
            "accepted_run_count": 600,
        },
        {
            "round": "E3",
            "dataset": "SensorScope,U-Air",
            "scenario": "complete_aligned",
            "method": "all formal methods",
            "seed_range": "30001-30020",
            "hyperparameters": "E3 formal freeze",
            "preprocessing_revision": "",
            "source_revision": "",
            "config_hash": "",
            "EventTrace_policy": "per dataset x seed shared",
            "target_h_i": "",
            "stratum_s_i": "",
            "accepted_run_count": 440,
        },
        {
            "round": "E4",
            "dataset": "SensorScope,U-Air",
            "scenario": "ablation",
            "method": "6 configurations",
            "seed_range": "30001-30020",
            "hyperparameters": "matched E3 lambdas; wo_inst Gen2 one-factor",
            "preprocessing_revision": "",
            "source_revision": "",
            "config_hash": "",
            "EventTrace_policy": "shared with E3",
            "target_h_i": "",
            "stratum_s_i": "",
            "accepted_run_count": 240,
        },
    ]
    write_csv(prov / "FINAL_CONFIG_REGISTRY.csv", config_rows)

    # Scientific source hash registry (critical files)
    hash_rows = []
    critical = [
        ("E2", "artifacts/e2_traffic_formal_runs_r1/formal_results.csv", "e2_runs"),
        ("E2", "artifacts/e2_traffic_formal_runs_r1/eventtrace_manifest.csv", "e2_eventtraces"),
        ("E3", "artifacts/e3_formal_runs_r1/E3_FORMAL_RUN_STATUS.csv", "e3_status"),
        ("E3", "artifacts/e3_formal_runs_r1/E3_FORMAL_SUMMARY.csv", "e3_summary"),
        ("E4", "artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv", "e4_index"),
        (
            "E4",
            "artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_COMPONENT_CLAIM_MATRIX_FINAL_R3.json",
            "e4_claims",
        ),
        ("E1", "outputs/aggregate/E1_R2/per_seed_metrics.csv", "e1_per_seed"),
    ]
    snap = paper / "03_raw_evidence" / "source_snapshots"
    snap.mkdir(parents=True, exist_ok=True)
    for round_name, rel, role in critical:
        src = root / rel
        if not src.is_file():
            hash_rows.append(
                {
                    "round": round_name,
                    "source_revision": "",
                    "relative_path": rel,
                    "sha256": "",
                    "role": role,
                    "present_in_package": "False",
                    "archive_reference": "",
                }
            )
            continue
        digest = sha256_file(src)
        present = "True"
        if src.stat().st_size < 20_000_000:
            from .io_util import copy_file

            copy_file(src, snap / Path(rel).name)
        hash_rows.append(
            {
                "round": round_name,
                "source_revision": "",
                "relative_path": rel,
                "sha256": digest,
                "role": role,
                "present_in_package": present,
                "archive_reference": f"03_raw_evidence/source_snapshots/{Path(rel).name}",
            }
        )
    write_csv(prov / "SCIENTIFIC_SOURCE_HASH_REGISTRY.csv", hash_rows)

    return {
        "n_long": len(long_rows),
        "n_runlevel": len(run_rows),
        "n_claims": len(claims),
    }

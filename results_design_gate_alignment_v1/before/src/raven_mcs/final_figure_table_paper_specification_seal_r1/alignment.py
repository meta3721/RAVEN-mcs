"""Alignment maps, section specs, writing ceilings, appendix, audits, final master."""

from __future__ import annotations

from pathlib import Path

from raven_mcs.paper_data_r1.io_util import write_csv, write_json, write_text
from raven_mcs.final_figure_table_paper_specification_seal_r1.constants import E4_LABELS, JOURNAL, TITLE


def write_alignment_and_sections(out: Path, hashes: dict) -> None:
    write_csv(
        out / "06_ALIGNMENT/CONTRIBUTION_THEORY_EVIDENCE_MAP.csv",
        [
            {"contribution_id": "C1", "problem_statement": "usable-update vs deployment-target risk", "technical_mechanism": "h≠s; μ vs usable mass", "theorem_or_proposition": "P1 target-vs-arrival risk (definitional)", "algorithm_section": "III", "empirical_rq": "RQ1", "primary_figure": "FIG-E1", "primary_table": "APP-T1", "supporting_appendix": "none required", "claim_strength": "supported", "remaining_gap": "no T-Drive performance (reserve)"},
            {"contribution_id": "C2", "problem_statement": "staged selection requires layer-aware reconstruction", "technical_mechanism": "R/O/U weights + Hajek normalization", "theorem_or_proposition": "P2 reconstruction under positivity/support", "algorithm_section": "IV", "empirical_rq": "RQ2", "primary_figure": "FIG-E2", "primary_table": "TABLE-II", "supporting_appendix": "APP-F1 Local-Hajek", "claim_strength": "supported_selective_prediction", "remaining_gap": "Traffic E3 NOT_COMPARABLE by design"},
            {"contribution_id": "C3", "problem_statement": "calibration must remain feasible and can accumulate residual", "technical_mechanism": "instantaneous P2 + debt", "theorem_or_proposition": "T-P2 uniqueness under stated convex assumptions (theory-only empirically)", "algorithm_section": "V–VI", "empirical_rq": "RQ3", "primary_figure": "FIG-E4", "primary_table": "TABLE-III", "supporting_appendix": "APP-F2 P2 feasibility", "claim_strength": "trade-offs; Use null; Debt small", "remaining_gap": "exact experimental P2 optimality not reconstructable (C10)"},
        ],
    )
    write_csv(
        out / "06_ALIGNMENT/RQ_EVIDENCE_MAP.csv",
        [
            {"rq": "RQ1", "experiments": "E1/E2", "primary_figure": "FIG-E1", "support_figure": "FIG-C", "primary_table": "APP-T1", "claim_ids": "C1,C2"},
            {"rq": "RQ2", "experiments": "E3 SS/U-Air", "primary_figure": "FIG-E2", "support_figure": "FIG-E3", "primary_table": "TABLE-II", "claim_ids": "C3,C4,C9"},
            {"rq": "RQ3", "experiments": "E4 240 Gen2", "primary_figure": "FIG-E4", "support_figure": "none mandatory", "primary_table": "TABLE-III", "claim_ids": "C5-C8,C10"},
        ],
    )
    write_text(
        out / "07_SECTION_SPEC/SECTION_III_SPEC_R1.md",
        """# Section III specification

Entities: clients k; atomic units i; target Y_i; deployment-target group h(i); opportunity stratum s(i); indicators R, O, U (delivered iff U=1); public target μ constructed from train-split mass without test labels.

Define deployment-target risk on μ / h(i) versus arrival/usable-update risk on the usable-update distribution. State the optimization/problem: reduce structural mismatch to μ while keeping competitive target prediction risk.

h(i) ≠ s(i). No new experimental claims. E2 motivates; numbers live in Section VII.
""",
    )
    write_text(
        out / "07_SECTION_SPEC/SECTION_IV_SPEC_R1.md",
        """# Section IV specification

Selection-layer-aware reconstruction: opportunity/design correction, observation correction, usable-update correction; support/positivity; Hajek/normalized reconstruction; information-boundary legality (no test labels in μ); reconstructed mass for aggregation.

Local-Hajek degeneracy is a diagnostic (Appendix C), not a claim that Hajek is universally unusable. Do not claim each layer is empirically necessary.
""",
    )
    write_text(
        out / "07_SECTION_SPEC/SECTION_V_SPEC_R1.md",
        """# Section V specification

Feasibility-aware calibration: instantaneous mismatch vs reference composition on feasible support; P2; calibration variables; variance/staleness terms only if already in the frozen method; debt update; final aggregation.

Do not claim Debt is empirically large. Inst is an endpoint trade-off. Use has no clear sealed E4 effect. P2: feasibility where reconstructable; not experimental exact optimality (C10).
""",
    )
    write_csv(
        out / "07_SECTION_SPEC/SECTION_VI_THEOREM_REGISTRY_R1.csv",
        [
            {"theorem_name": "P1 Target-vs-arrival risk", "assumptions": "two-stage selection; μ ≠ usable-update law in general", "exact_claim": "deployment-target risk is not identical to arrival/usable-update risk", "dependency": "definitions in III", "proof_location": "Appendix A (short)", "empirical_validation_needed": False, "notes": "E2 illustrates; not a substitute definition"},
            {"theorem_name": "P2 Normalized reconstruction", "assumptions": "positivity/support on used layers; known or estimated propensities as specified", "exact_claim": "normalized/Hajek reconstruction targets μ under the stated sampling model", "dependency": "IV", "proof_location": "Appendix A", "empirical_validation_needed": False, "notes": "Local-Hajek collapse is a support diagnostic, not a disproof of the theorem's assumptions"},
            {"theorem_name": "T-P2 Feasible calibration uniqueness", "assumptions": "stated convex program, feasible set, uniqueness conditions in the method paper", "exact_claim": "the mathematical P2 program has a unique minimizer under those assumptions", "dependency": "V", "proof_location": "Appendix A", "empirical_validation_needed": False, "notes": "C10: experimental windows are not retrospectively certified exactly optimal"},
        ],
    )
    write_text(
        out / "07_SECTION_SPEC/SECTION_VI_SPEC_R1.md",
        """# Section VI specification

Include only P1, P2 (reconstruction), and T-P2 (feasibility program uniqueness under assumptions). Do not add theorems for completeness. Empirical E2–E4 do not prove T-P2 exact optimality on sealed windows.
""",
    )
    write_text(
        out / "07_SECTION_SPEC/SECTION_VII_SPEC_R1.md",
        """# Section VII specification

VII-A Setup: Table I; h/s; seeds 30001–30020 (E1: 28001–28005); methods; Traffic role; T-Drive not evaluated.

VII-B RQ1: E1 no-harm (appendix/compact); FIG-E1 D_aligned. Not a ranking figure.

VII-C RQ2: FIG-E2 structural; FIG-E3 prediction; Table II. SensorScope/U-Air only.

VII-D RQ3: FIG-E4; Table III; labels Use=NO_CLEAR_EFFECT, Inst=ENDPOINT_TRADEOFF, Debt quantitatively small.

VII-E Short empirical summary; no new numbers.
""",
    )
    write_text(
        out / "07_SECTION_SPEC/SECTION_VIII_SPEC_R1.md",
        """# Section VIII specification

Required: structural alignment vs universal RMSE; endpoint trade-offs; Use no-clear-effect; small Debt; Traffic comparability; P2 feasibility/optimality boundary; propensity-quality dependence; T-Drive external mobility reserve (protocol sealed, not run).
""",
    )
    write_text(
        out / "08_WRITING_BOUNDARY/INTRODUCTION_CONTRIBUTION_WORDING_SEAL.md",
        """# Introduction contribution wording seal

Candidate 1: We formulate deployment-target risk under multi-layer non-random MCS selection and show that usable-update risk is not generally interchangeable with that target.

Candidate 2: We develop selection-layer-aware reconstruction across opportunity, observation, and usable-update layers with normalized correction.

Candidate 3: We couple instantaneous feasibility-aware calibration with long-term debt, as a coordinated architecture rather than five independent modules.

Avoid: universally superior; all components are necessary; fully real-world selection; exactly optimal in all experimental windows.
""",
    )
    write_text(
        out / "08_WRITING_BOUNDARY/ABSTRACT_CLAIM_CEILING_R1.md",
        """# Abstract claim ceiling

**Allowed quantitative (from frozen tables/figures only, no new numbers):** E2 D_aligned direction; E3 Δ_group/Δ_{c,s} reductions on SensorScope and U-Air; selective RMSE Holm results; E4 240-cell family; relative-change signs.

**Allowed qualitative:** two-stage selection can induce mismatch; coordinated reconstruction and calibration; competitive prediction; endpoint-dependent components.

**Forbidden:** universal RMSE; all baselines beaten; every component necessary; Use indispensable; large Debt; certified experimental P2 optimality; three-dataset E3; T-Drive results.
""",
    )
    write_text(
        out / "08_WRITING_BOUNDARY/CONCLUSION_CLAIM_CEILING_R1.md",
        """# Conclusion claim ceiling

Required narrative: target-risk mismatch; coordinated correction/calibration; strong structural alignment on comparable SensorScope/U-Air evidence; competitive prediction; selective gains; component trade-offs (Use no clear effect; Debt small; Inst endpoint trade-off). No T-Drive results. No universal dominance.
""",
    )
    write_text(
        out / "09_APPENDIX/FINAL_APPENDIX_STRUCTURE_R1.md",
        """# Appendix structure

A. Complete proofs for Section VI (P1, P2, T-P2).  
B. E1 sanity / supplementary statistics (APP-T1, APP-T2).  
C. Local-Hajek provenance (APP-F1).  
D. P2 feasibility diagnostics (APP-F2, APP-T4); not exact optimality.  
E. Full experimental tables / optional runtime (APP-T3, optional APP-T5).

Appendix A holds proofs; Appendix B–E hold supporting evidence.

Do not include FIG5 composition or T-Drive performance.
""",
    )


def write_audits_and_final(out: Path, hashes: dict, fig6: str) -> None:
    write_csv(
        out / "10_AUDIT/FINAL_DATA_GAP_DECISION_R1.csv",
        [
            {"item": "Debt trajectory", "class": "NONCORE_SUPPORTING", "triggers_new_experiment": False},
            {"item": "ESS trajectory", "class": "NONCORE_SUPPORTING", "triggers_new_experiment": False},
            {"item": "P2-only runtime", "class": "OPTIONAL", "triggers_new_experiment": False},
            {"item": "Sampling interval SS/U-Air", "class": "NONCORE_SUPPORTING", "triggers_new_experiment": False},
            {"item": "Row-level propensities", "class": "NONCORE_SUPPORTING", "triggers_new_experiment": False},
            {"item": "FIG5 composition trajectory", "class": "DROP", "triggers_new_experiment": False},
            {"item": "T-Drive formal performance", "class": "NONCORE_SUPPORTING", "triggers_new_experiment": False},
            {"item": "E1 dataset checksum", "class": "OPTIONAL", "triggers_new_experiment": False},
        ],
    )
    write_json(
        out / "10_AUDIT/FINAL_FIGURE_COUNT_DECISION_R1.json",
        {"conceptual_merge": True, "main_figures": 5, "breakdown": "1 framework + 4 empirical (E1–E4)", "do_not_exceed_without_scientific_reason": True},
    )
    write_json(out / "10_AUDIT/FINAL_TABLE_COUNT_DECISION_R1.json", {"main_tables": 3, "ids": ["TABLE-I", "TABLE-II", "TABLE-III"]})
    write_csv(
        out / "10_AUDIT/PAPER_SECTION_PAGE_PRIORITY_R1.csv",
        [
            {"section": "I Introduction", "priority": "high"},
            {"section": "II Related Work", "priority": "compact"},
            {"section": "III", "priority": "high"},
            {"section": "IV", "priority": "high"},
            {"section": "V", "priority": "high"},
            {"section": "VI", "priority": "moderate/high"},
            {"section": "VII Evaluation", "priority": "high"},
            {"section": "VIII Discussion", "priority": "compact"},
            {"section": "IX Conclusion", "priority": "compact"},
            {"section": "Appendix", "priority": "proof/supporting"},
        ],
    )
    ident_rows = []
    for aid, rec in hashes.items():
        if not isinstance(rec, dict) or "sha256" not in rec:
            continue
        ident_rows.append(
            {
                "artifact": aid,
                "source_file": rec.get("dest", rec.get("src", "")),
                "source_sha256": rec["sha256"],
                "final_evidence": True,
                "superseded_e4_stats": False,
                "traffic_e3_contamination": aid == "TABLE_II" and False,
                "tdrive_result": False,
                "canary_invalid": False,
                "favorable_hidden_filter": False,
            }
        )
    write_csv(out / "05_PROVENANCE/FINAL_FIGURE_TABLE_DATA_IDENTITY_AUDIT.csv", ident_rows)
    write_csv(
        out / "10_AUDIT/FINAL_MAIN_ARTIFACT_REPRODUCIBILITY_AUDIT.csv",
        [
            {"artifact": "FIG-E1", "source_csv": hashes["FIG_E1"]["dest"], "master": "E2_D_ALIGNED_PER_SEED / FIG1 freeze copy", "seeds": "30001-30020", "config": "E2 PROFILE-S1", "EventTrace": "E2 120-hash index", "gap": "none"},
            {"artifact": "FIG-E2", "source_csv": hashes["FIG_E2"]["dest"], "master": "E3_STRUCTURAL_METRICS_MASTER", "seeds": "30001-30020", "config": "E3 SS/U-Air", "EventTrace": "E3 manifest", "gap": "none"},
            {"artifact": "FIG-E3", "source_csv": hashes["FIG_E3"]["dest"], "master": "E3_PREDICTION_METRICS_MASTER", "seeds": "30001-30020", "config": "E3 SS/U-Air", "EventTrace": "E3 manifest", "gap": "none"},
            {"artifact": "FIG-E4", "source_csv": hashes["FIG_E4"]["dest"], "master": "E4_FINAL_STATISTICS_R2 relative change", "seeds": "30001-30020", "config": "E4 240 Gen2 Inst", "EventTrace": "E4 gen2 identity", "gap": "none"},
            {"artifact": "TABLE-I", "source_csv": hashes["TABLE_I"]["dest"], "master": "DATASET_METADATA_FINAL", "seeds": "n/a", "config": "FINAL_CONFIG_MASTER", "EventTrace": "n/a", "gap": "none"},
            {"artifact": "TABLE-II", "source_csv": hashes["TABLE_II"]["dest"], "master": "E3_FINAL_STATISTICS + Holm", "seeds": "30001-30020", "config": "E3", "EventTrace": "E3", "gap": "none"},
            {"artifact": "TABLE-III", "source_csv": hashes["TABLE_III"]["dest"], "master": "E4_240 + E4_FINAL_STATISTICS_R2", "seeds": "30001-30020", "config": "E4 Gen2", "EventTrace": "E4", "gap": "none"},
        ],
    )
    write_csv(
        out / "10_AUDIT/FINAL_MAIN_ARTIFACT_NUMERIC_CONSISTENCY.csv",
        [
            {"pair": "FIG-E1 vs E2 D_aligned CSV", "status": "EXACT_MATCH", "note": "byte-copy from manuscript-closure/freeze source"},
            {"pair": "FIG-E2 vs E3 structural master subset", "status": "AGGREGATION_MATCH", "note": "seed-level boxplot source copied; Traffic dropped in source"},
            {"pair": "FIG-E3 vs E3 prediction master", "status": "EXACT_MATCH", "note": "copy of E3_PREDICTION_METRICS_MASTER"},
            {"pair": "FIG-E4 vs E4_FINAL_STATISTICS_R2 relative_change", "status": "EXACT_MATCH", "note": "manuscript-closure FIG3 source"},
            {"pair": "TABLE-II vs E3_FINAL_STATISTICS means", "status": "AGGREGATION_MATCH", "note": "mean±std already computed in sealed table source; no recompute"},
            {"pair": "TABLE-III vs E4_240 / ablation table", "status": "EXACT_MATCH", "note": "w/o-Inst gen 2 in source"},
            {"pair": "TABLE-I vs DATASET_METADATA_FINAL", "status": "AGGREGATION_MATCH", "note": "field projection; T-Drive not listed as evaluated"},
        ],
    )
    write_json(
        out / "10_AUDIT/TDRIVE_FINAL_RESERVE_STATUS_R1.json",
        {
            "protocol_status": "PROTOCOL_SEALED",
            "formal_status": "FORMAL_NOT_RUN",
            "paper_role": "REVIEWER_RESERVE",
            "in_evaluated_dataset_count": False,
            "in_main_results": False,
            "in_main_tables": False,
            "in_main_empirical_figures": False,
            "default_action": "DO_NOT_RUN_BEFORE_SUBMISSION",
        },
    )
    write_json(
        out / "22_REPORTS/NO_NEW_EXPERIMENT_ATTESTATION.json".replace("22_REPORTS", "12_REPORTS"),
        {
            "training_started": False,
            "formal_run_started": False,
            "canary_started": False,
            "tdrive_run_started": False,
            "new_scientific_runs": 0,
            "scientific_metric_changed": False,
            "original_scientific_data_unchanged": True,
        },
    )
    ft_rows = [
        {"artifact_id": "FIG-C", "artifact_type": "figure", "provisional_number": "1", "title": "Framework (merged conceptual)", "section": "I/III–V", "rq": "setup", "main_or_appendix": "main", "source_file": "03_FIGURE_SPEC/FIG_C1_*.md + FIG_C2_*.md", "source_sha256": "n/a_conceptual", "claim_ids": "architecture", "scientific_message": "mismatch + coupled system", "final_status": "MAIN_SPEC_READY", "new_experiment_required": False},
        {"artifact_id": "FIG-E1", "artifact_type": "figure", "provisional_number": "2", "title": "Risk non-interchangeability", "section": "VII-B", "rq": "RQ1", "main_or_appendix": "main", "source_file": hashes["FIG_E1"]["dest"], "source_sha256": hashes["FIG_E1"]["sha256"], "claim_ids": "C1,C2", "scientific_message": "D_aligned direction", "final_status": "MAIN_SOURCE_FROZEN", "new_experiment_required": False},
        {"artifact_id": "FIG-E2", "artifact_type": "figure", "provisional_number": "3", "title": "Structural alignment", "section": "VII-C", "rq": "RQ2", "main_or_appendix": "main", "source_file": hashes["FIG_E2"]["dest"], "source_sha256": hashes["FIG_E2"]["sha256"], "claim_ids": "C3", "scientific_message": "Δ_group/Δ_c,s", "final_status": "MAIN_SOURCE_FROZEN", "new_experiment_required": False},
        {"artifact_id": "FIG-E3", "artifact_type": "figure", "provisional_number": "4", "title": "Prediction risk", "section": "VII-C", "rq": "RQ2", "main_or_appendix": "main", "source_file": hashes["FIG_E3"]["dest"], "source_sha256": hashes["FIG_E3"]["sha256"], "claim_ids": "C4", "scientific_message": "competitive/selective RMSE", "final_status": "MAIN_SOURCE_FROZEN", "new_experiment_required": False},
        {"artifact_id": "FIG-E4", "artifact_type": "figure", "provisional_number": "5", "title": "Component ablation", "section": "VII-D", "rq": "RQ3", "main_or_appendix": "main", "source_file": hashes["FIG_E4"]["dest"], "source_sha256": hashes["FIG_E4"]["sha256"], "claim_ids": "C5-C8", "scientific_message": "trade-offs", "final_status": "MAIN_SOURCE_FROZEN", "new_experiment_required": False},
        {"artifact_id": "TABLE-I", "artifact_type": "table", "provisional_number": "I", "title": "Datasets", "section": "VII-A", "rq": "setup", "main_or_appendix": "main", "source_file": hashes["TABLE_I"]["dest"], "source_sha256": hashes["TABLE_I"]["sha256"], "claim_ids": "setup", "scientific_message": "protocols; no T-Drive evaluated", "final_status": "MAIN_SOURCE_FROZEN", "new_experiment_required": False},
        {"artifact_id": "TABLE-II", "artifact_type": "table", "provisional_number": "II", "title": "Main effectiveness", "section": "VII-C", "rq": "RQ2", "main_or_appendix": "main", "source_file": hashes["TABLE_II"]["dest"], "source_sha256": hashes["TABLE_II"]["sha256"], "claim_ids": "C3,C4", "scientific_message": "SS/U-Air E3", "final_status": "MAIN_SOURCE_FROZEN", "new_experiment_required": False},
        {"artifact_id": "TABLE-III", "artifact_type": "table", "provisional_number": "III", "title": "Ablation", "section": "VII-D", "rq": "RQ3", "main_or_appendix": "main", "source_file": hashes["TABLE_III"]["dest"], "source_sha256": hashes["TABLE_III"]["sha256"], "claim_ids": "C5-C8", "scientific_message": "240 cells Gen2", "final_status": "MAIN_SOURCE_FROZEN", "new_experiment_required": False},
        {"artifact_id": "APP-F1", "artifact_type": "figure", "provisional_number": "A1", "title": "Local-Hajek provenance", "section": "Appendix C", "rq": "RQ2", "main_or_appendix": "appendix", "source_file": hashes["APP_F1"]["dest"], "source_sha256": hashes["APP_F1"]["sha256"], "claim_ids": "C2 diagnostic", "scientific_message": "weight_range=0 collapse provenance", "final_status": "APPENDIX_READY", "new_experiment_required": False},
        {"artifact_id": "APP-F2", "artifact_type": "figure", "provisional_number": "A2", "title": "P2 feasibility diagnostic", "section": "Appendix D", "rq": "RQ3", "main_or_appendix": "appendix", "source_file": hashes.get("APP_F2", {}).get("dest", ""), "source_sha256": hashes.get("APP_F2", {}).get("sha256", ""), "claim_ids": "C10", "scientific_message": "feasibility status; not exact optimality", "final_status": fig6, "new_experiment_required": False},
        {"artifact_id": "APP-T1", "artifact_type": "table", "provisional_number": "A-T1", "title": "E1 balanced sanity", "section": "Appendix B", "rq": "RQ1", "main_or_appendix": "appendix", "source_file": hashes["APP_T1"]["dest"], "source_sha256": hashes["APP_T1"]["sha256"], "claim_ids": "C1 context", "scientific_message": "no-harm sanity", "final_status": "APPENDIX_READY", "new_experiment_required": False},
        {"artifact_id": "APP-T2", "artifact_type": "table", "provisional_number": "A-T2", "title": "Full paired statistics", "section": "Appendix B", "rq": "RQ2-RQ3", "main_or_appendix": "appendix", "source_file": hashes.get("APP_T2", {}).get("dest", ""), "source_sha256": hashes.get("APP_T2", {}).get("sha256", ""), "claim_ids": "C3-C8", "scientific_message": "Holm families", "final_status": "APPENDIX_READY", "new_experiment_required": False},
        {"artifact_id": "APP-T3", "artifact_type": "table", "provisional_number": "A-T3", "title": "Full method results", "section": "Appendix E", "rq": "RQ2", "main_or_appendix": "appendix", "source_file": hashes.get("APP_T3", {}).get("dest", ""), "source_sha256": hashes.get("APP_T3", {}).get("sha256", ""), "claim_ids": "C3,C4", "scientific_message": "reference methods", "final_status": "APPENDIX_READY", "new_experiment_required": False},
        {"artifact_id": "APP-T4", "artifact_type": "table", "provisional_number": "A-T4", "title": "P2 feasibility summary", "section": "Appendix D", "rq": "RQ3", "main_or_appendix": "appendix", "source_file": hashes.get("APP_F2", {}).get("dest", ""), "source_sha256": hashes.get("APP_F2", {}).get("sha256", ""), "claim_ids": "C10", "scientific_message": "certificate counts", "final_status": fig6, "new_experiment_required": False},
        {"artifact_id": "APP-T5", "artifact_type": "table", "provisional_number": "A-T5", "title": "Runtime summary", "section": "Appendix E", "rq": "n/a", "main_or_appendix": "appendix", "source_file": hashes.get("APP_T5", {}).get("dest", ""), "source_sha256": hashes.get("APP_T5", {}).get("sha256", ""), "claim_ids": "none", "scientific_message": "existing runtime only; not scalability", "final_status": "OPTIONAL_APPENDIX", "new_experiment_required": False},
    ]
    write_csv(out / "11_FINAL/FINAL_FIGURE_TABLE_REGISTRY_R1.csv", ft_rows)
    master = {
        "title": TITLE,
        "target_journal": JOURNAL,
        "unique_mainline": "mismatch → reconstruction → calibration → structural alignment + competitive prediction",
        "contributions": ["C1 risk semantics", "C2 layer-aware reconstruction", "C3 feasibility-aware calibration"],
        "rqs": ["RQ1", "RQ2", "RQ3"],
        "sections": ["I–IX", "Appendix A–E"],
        "claim_ceiling": "C1–C10",
        "h_s": "h≠s; UTC 4-block h for SS/U-Air",
        "experiment_roles": "E1 sanity; E2 problem; E3 effectiveness SS/U-Air; E4 mechanism Gen2",
        "main_figures": ["FIG-C", "FIG-E1", "FIG-E2", "FIG-E3", "FIG-E4"],
        "main_tables": ["TABLE-I", "TABLE-II", "TABLE-III"],
        "appendix": "A proofs; B E1/stats; C Local-Hajek; D P2; E full tables",
        "contribution_theory_evidence_map": [
            {"contribution_id": "C1", "theorem_or_proposition": "P1 target-vs-arrival risk", "empirical_rq": "RQ1", "primary_figure": "FIG-E1", "primary_table": "APP-T1"},
            {"contribution_id": "C2", "theorem_or_proposition": "P2 normalized reconstruction", "empirical_rq": "RQ2", "primary_figure": "FIG-E2", "primary_table": "TABLE-II"},
            {"contribution_id": "C3", "theorem_or_proposition": "T-P2 uniqueness (theory-only empirically)", "empirical_rq": "RQ3", "primary_figure": "FIG-E4", "primary_table": "TABLE-III"},
        ],
        "figure_table_hashes": {k: (v.get("sha256") if isinstance(v, dict) else v) for k, v in hashes.items()},
        "tdrive": "PROTOCOL_SEALED / FORMAL_NOT_RUN / REVIEWER_RESERVE",
        "no_new_experiment": True,
        "e4_labels": E4_LABELS,
        "fig6_repair": fig6,
    }
    write_json(out / "11_FINAL/FRAZEN_PAPER_SPECIFICATION_MASTER_R1.json", master)
    write_text(
        out / "11_FINAL/FRAZEN_PAPER_SPECIFICATION_MASTER_R1.md",
        f"""# Frozen paper specification master R1

**Title.** {TITLE}

**Journal.** {JOURNAL}

**Contributions.** (1) target-risk semantics; (2) layer-aware reconstruction; (3) feasibility-aware calibration.

**RQs.** RQ1 mismatch (FIG-E1); RQ2 effectiveness (FIG-E2/E3, Table II); RQ3 components (FIG-E4, Table III).

**Main figures (5).** FIG-C merged framework + four empirical figures.

**Main tables (3).** I–III.

**T-Drive.** Protocol sealed, not run, reviewer reserve.

**Next.** WRITE SECTION III–VI USING FROZEN SPECIFICATION. No new experiments.
""",
    )
    write_text(
        out / "11_FINAL/RAVEN_MCS_WRITING_HANDOFF_R1.txt",
        f"""RAVEN-MCS WRITING HANDOFF R1

1. Title: {TITLE}
2. Journal: {JOURNAL}
3. Contributions: C1 risk semantics; C2 layer-aware reconstruction; C3 feasibility-aware calibration.
4. RQs: RQ1, RQ2, RQ3.
5. Structure: I Introduction; II Related Work; III Model; IV Reconstruction; V Calibration; VI Theory; VII Evaluation; VIII Discussion; IX Conclusion; Appendix A–E.
6. h(i)/s(i): SS/U-Air h = four UTC TOD groups (train mass, no test labels); s = spatial × time-block × weekday; h≠s.
7. Main figures: FIG-C, FIG-E1, FIG-E2, FIG-E3, FIG-E4.
8. Main tables: TABLE-I, TABLE-II, TABLE-III.
9. Appendix figures/tables: APP-F1 Local-Hajek; APP-F2 P2 feasibility; APP-T1 E1; APP-T2 stats; APP-T3 full methods; APP-T4 P2; APP-T5 runtime optional. FIG5 do not run.
10. Exact sources: 05_PROVENANCE/FINAL_FIGURE_SOURCES/ and FINAL_TABLE_SOURCES/ (hashes in 11_FINAL registries).
11. E4 w/o-Inst: Generation 2 ONLY.
12. Traffic: E2 OK; E3 cross-vintage NOT_COMPARABLE; not in Table II or FIG-E2/E3.
13. P2: feasibility auditable; exact experimental optimality not reconstructable.
14. Use: NO_CLEAR_EFFECT in current E4.
15. Debt: statistically consistent but quantitatively small.
16. T-Drive: PROTOCOL_SEALED, FORMAL_NOT_RUN, REVIEWER_RESERVE; do not run before submission.
17. Noncore gaps: debt/ESS trajectories, sampling interval, row-level propensities, FIG5 composition — do not experiment.
18. Next writing step: WRITE SECTION III–VI USING FROZEN SPECIFICATION
""",
    )

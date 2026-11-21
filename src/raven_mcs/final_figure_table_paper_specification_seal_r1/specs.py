"""Write specification markdown, registries, section specs, writing ceilings."""

from __future__ import annotations

from pathlib import Path

from raven_mcs.paper_data_r1.io_util import write_csv, write_json, write_text
from raven_mcs.final_figure_table_paper_specification_seal_r1.constants import E4_LABELS, JOURNAL, TITLE


def write_core_specs(out: Path, hashes: dict) -> None:
    write_json(
        out / "00_SPECIFICATION/FINAL_PAPER_POSITIONING_R1.json",
        {
            "title": TITLE,
            "journal": JOURNAL,
            "mainline": [
                "selection-induced deployment-target mismatch",
                "selection-layer-aware correction/reconstruction",
                "feasibility-aware target calibration",
                "reduced structural target mismatch",
                "competitive deployment-target prediction risk",
            ],
            "not_primarily": [
                "generic FL optimization",
                "generic imputation",
                "mobility prediction",
                "routing",
                "fairness",
                "system scalability",
            ],
        },
    )
    write_text(
        out / "00_SPECIFICATION/FINAL_PAPER_POSITIONING_R1.md",
        f"# Final paper positioning\n\n**Title.** {TITLE}\n\n**Journal.** {JOURNAL}\n\n**Mainline.** selection-induced deployment-target mismatch → selection-layer-aware correction/reconstruction → feasibility-aware target calibration → reduced structural mismatch with competitive prediction risk.\n\nNot a generic FL, imputation, mobility-prediction, routing, fairness, or scalability paper.\n",
    )
    contribs = [
        {
            "contribution_id": "C1",
            "title": "Deployment-target risk semantics under multi-layer non-random selection",
            "problem_gap": "Arrival/usable-update risk is treated as interchangeable with public deployment-target risk",
            "technical_core": "h(i) vs s(i); mu vs usable-update mass; D_aligned = ΔRMSE_μ − ΔRMSE_ρ",
            "main_theory": "Section III target-risk formulation",
            "main_evidence": "E2 FIG-E1; E1 no-harm context",
            "claim_ceiling": "C1–C2; not RAVEN superiority",
            "forbidden_overclaim": "RAVEN ranking on E2; fully real-world selection",
        },
        {
            "contribution_id": "C2",
            "title": "Selection-layer-aware target reconstruction across R/O/U with normalized correction",
            "problem_gap": "Single-layer IPW/window FL ignores staged opportunity–observation–usable structure",
            "technical_core": "layer-wise weights and Hajek normalization on reconstructed mass",
            "main_theory": "Section IV reconstruction; positivity/support",
            "main_evidence": "E3 FIG-E2/E3 TABLE-II; Local-Hajek appendix provenance",
            "claim_ceiling": "C3–C4 structural alignment + selective prediction",
            "forbidden_overclaim": "universal RMSE; three-dataset homogeneous E3; every layer independently necessary",
        },
        {
            "contribution_id": "C3",
            "title": "Feasibility-aware instantaneous and long-term target calibration",
            "problem_gap": "Unconstrained calibration can leave the feasible simplex; long-term mismatch accumulates",
            "technical_core": "instantaneous P2 adjustment + debt update; coupled with reconstruction",
            "main_theory": "Section V–VI P2 uniqueness under assumptions (theory); C10 empirical boundary",
            "main_evidence": "E4 FIG-E4 TABLE-III",
            "claim_ceiling": "C5–C8 endpoint trade-offs; Use NO_CLEAR_EFFECT; Debt small; Inst ENDPOINT_TRADEOFF",
            "forbidden_overclaim": "five independent innovations; Use indispensable; large Debt; all P2 experimentally exactly optimal",
        },
    ]
    write_csv(out / "00_SPECIFICATION/FINAL_CONTRIBUTION_REGISTRY_R1.csv", contribs)
    write_text(
        out / "00_SPECIFICATION/FINAL_CONTRIBUTION_REGISTRY_R1.md",
        "# Three contributions\n\nDo not promote Design/Obs/Use/Inst/Debt into five independent contributions.\n\n"
        + "\n".join(f"- **{r['contribution_id']}.** {r['title']}" for r in contribs)
        + "\n",
    )
    rqs = [
        {"rq_id": "RQ1", "question": "Does two-stage non-random selection create a meaningful deployment-target risk mismatch?", "evidence": "E1/E2", "primary_figure": "FIG-E1", "primary_table": "APP-T1 (E1)"},
        {"rq_id": "RQ2", "question": "Does RAVEN-MCS reduce structural deployment-target mismatch while maintaining competitive target prediction risk?", "evidence": "E3 SensorScope/U-Air", "primary_figure": "FIG-E2", "primary_table": "TABLE-II"},
        {"rq_id": "RQ3", "question": "How do the core correction and calibration components contribute to RAVEN's structural and predictive behavior?", "evidence": "E4 240-cell Gen2 Inst", "primary_figure": "FIG-E4", "primary_table": "TABLE-III"},
    ]
    write_csv(out / "00_SPECIFICATION/FINAL_RQ_REGISTRY_R1.csv", rqs)
    write_text(
        out / "00_SPECIFICATION/FINAL_RQ_REGISTRY_R1.md",
        "# Empirical RQs\n\nExactly three. No fourth main empirical RQ.\n\n"
        + "\n".join(f"- **{r['rq_id']}.** {r['question']}" for r in rqs)
        + "\n",
    )
    write_json(
        out / "00_SPECIFICATION/FINAL_CLAIM_CEILING_R1.json",
        {
            "allowed": {
                "C1": "Two-stage non-random selection can induce deployment-target mismatch.",
                "C2": "Arrival/usable-update risk is not generally interchangeable with deployment-target risk.",
                "C3": "On scientifically comparable SensorScope and U-Air E3 blocks, RAVEN-MCS consistently reduces structural target mismatch.",
                "C4": "RAVEN-MCS maintains competitive deployment-target prediction risk with selective significant gains.",
                "C5": "Core components have endpoint- and dataset-dependent roles.",
                "C6": "Use has NO_CLEAR_EFFECT in current E4.",
                "C7": "Debt has a statistically consistent but quantitatively small structural effect.",
                "C8": "Inst is ENDPOINT_TRADEOFF.",
                "C9": "Traffic E3 cross-vintage inference is NOT_COMPARABLE.",
                "C10": "P2 feasibility is auditable where reconstructable; exact experimental post-hoc optimality is not universally reconstructable.",
            },
            "forbidden": [
                "universal RMSE superiority",
                "all baselines significantly beaten",
                "every component is necessary",
                "Use is indispensable",
                "Debt has a large effect",
                "all P2 outputs are exactly optimal",
                "three-dataset homogeneous E3 superiority",
                "comprehensive robustness/scalability validation",
            ],
        },
    )
    write_text(
        out / "00_SPECIFICATION/FINAL_CLAIM_CEILING_R1.md",
        "# Claim ceiling C1–C10\n\nAllowed: mismatch; non-interchangeability; SensorScope/U-Air structural gains; competitive prediction with selective significance; endpoint-dependent components; Use NO_CLEAR_EFFECT; Debt quantitatively small; Inst ENDPOINT_TRADEOFF; Traffic E3 NOT_COMPARABLE; P2 feasibility not exact optimality.\n\nForbidden: universal RMSE; all components necessary; Use indispensable; large Debt; certified experimental P2 optimality; three-dataset homogeneous E3; robustness/scalability as a contribution.\n",
    )
    sections = [
        {"section": "I", "title": "Introduction", "core_question": "Why target-risk calibration under two-stage MCS selection?", "main_symbols": "μ, h(i), s(i), R,O,U", "main_theory": "positioning", "main_algorithm": "none", "main_evidence": "preview C1–C4", "planned_figures": "FIG-C (framework)", "planned_tables": "none", "appendix_dependency": "none", "page_priority": "high"},
        {"section": "II", "title": "Related Work", "core_question": "How is this distinct from FL/imputation/MCS?", "main_symbols": "n/a", "main_theory": "positioning", "main_algorithm": "none", "main_evidence": "none new", "planned_figures": "none", "planned_tables": "none", "appendix_dependency": "none", "page_priority": "compact"},
        {"section": "III", "title": "System Model and Target-Risk Formulation", "core_question": "What is deployment-target risk?", "main_symbols": "k, i, Y_i, h(i), s(i), R,O,U, μ", "main_theory": "target vs arrival risk", "main_algorithm": "none", "main_evidence": "E2 motivates", "planned_figures": "FIG-C panel A", "planned_tables": "none", "appendix_dependency": "A if defs expanded", "page_priority": "high"},
        {"section": "IV", "title": "Selection-Layer-Aware Target Reconstruction", "core_question": "How to reconstruct toward μ from R/O/U?", "main_symbols": "π, ν, q, Hajek weights", "main_theory": "positivity/support; normalized reconstruction", "main_algorithm": "layer-wise correction", "main_evidence": "E3", "planned_figures": "FIG-C panel B", "planned_tables": "none", "appendix_dependency": "C Local-Hajek", "page_priority": "high"},
        {"section": "V", "title": "Feasibility-Aware Target Calibration", "core_question": "How to stay feasible and accumulate long-term mismatch?", "main_symbols": "α, P2, debt e", "main_theory": "P2 uniqueness under assumptions", "main_algorithm": "inst + debt + aggregate", "main_evidence": "E4", "planned_figures": "FIG-C panel B", "planned_tables": "none", "appendix_dependency": "D P2", "page_priority": "high"},
        {"section": "VI", "title": "Theoretical Analysis", "core_question": "What is guaranteed vs empirically bounded?", "main_symbols": "P2, positivity", "main_theory": "selected propositions only", "main_algorithm": "none", "main_evidence": "not a substitute for E2–E4", "planned_figures": "none", "planned_tables": "none", "appendix_dependency": "A proofs", "page_priority": "moderate/high"},
        {"section": "VII", "title": "Evaluation", "core_question": "RQ1–RQ3", "main_symbols": "Δ_group, Δ_{c,s}, RMSE_μ, D_aligned", "main_theory": "none new", "main_algorithm": "none", "main_evidence": "E1–E4", "planned_figures": "FIG-E1–E4", "planned_tables": "I–III", "appendix_dependency": "B–E", "page_priority": "high"},
        {"section": "VIII", "title": "Discussion and Limitations", "core_question": "What must not be overclaimed?", "main_symbols": "n/a", "main_theory": "C10", "main_algorithm": "none", "main_evidence": "limitations", "planned_figures": "none", "planned_tables": "none", "appendix_dependency": "none", "page_priority": "compact"},
        {"section": "IX", "title": "Conclusion", "core_question": "Claim-safe close", "main_symbols": "n/a", "main_theory": "none", "main_algorithm": "none", "main_evidence": "C1–C8 only", "planned_figures": "none", "planned_tables": "none", "appendix_dependency": "none", "page_priority": "compact"},
        {"section": "Appendix", "title": "Proofs and supporting evidence", "core_question": "Complete proofs + diagnostics", "main_symbols": "as in VI", "main_theory": "proofs", "main_algorithm": "none", "main_evidence": "E1, Local-Hajek, P2, full tables", "planned_figures": "APP-F1, APP-F2", "planned_tables": "APP-T1–T4 optional T5", "appendix_dependency": "self", "page_priority": "supporting"},
    ]
    write_csv(out / "00_SPECIFICATION/FINAL_SECTION_STRUCTURE_R1.csv", sections)

    write_json(
        out / "01_SEMANTICS/FINAL_H_S_MANUSCRIPT_SEMANTICS_R1.json",
        {
            "h_equals_s": False,
            "SensorScope": {
                "h(i)": "four UTC time-of-day groups H1:00–06, H2:06–12, H3:12–18, H4:18–24; train-split UTC block mass; no test labels",
                "s(i)": "spatial_id × four time blocks × weekday/weekend",
            },
            "U-Air": {
                "h(i)": "four UTC time-of-day groups H1:00–06, H2:06–12, H3:12–18, H4:18–24; train-split UTC block mass; no test labels",
                "s(i)": "spatial_id × four time blocks × weekday/weekend",
            },
            "NSW-Traffic": {
                "h(i)": "repeatable UTC time-of-day 4-block; train-split mass only",
                "s(i)": "frozen real_region_id × time_block × weekday_flag (E2 public-target 4 regions)",
            },
            "forbidden": "do not write SensorScope/U-Air h(i) as spatial × time",
        },
    )
    write_text(
        out / "01_SEMANTICS/FINAL_H_S_MANUSCRIPT_SEMANTICS_R1.md",
        "# Final h(i)/s(i) manuscript semantics\n\n**h(i) ≠ s(i).** For SensorScope and U-Air, h(i) is four UTC TOD groups (train-split mass, no test labels). s(i) is spatial identity × four time blocks × weekday/weekend. Do not describe h(i) as spatial × time.\n",
    )
    write_csv(
        out / "01_SEMANTICS/FINAL_EXPERIMENT_ROLE_REGISTRY_R1.csv",
        [
            {"block": "E1", "role": "balanced/no-harm sanity", "paper_use": "appendix or compact VII-B", "not_use": "superiority ranking"},
            {"block": "E2", "role": "risk non-interchangeability / problem evidence", "paper_use": "FIG-E1 RQ1", "not_use": "RAVEN vs baselines ranking"},
            {"block": "E3", "role": "main effectiveness on SensorScope and U-Air", "paper_use": "FIG-E2/E3 TABLE-II RQ2", "not_use": "Traffic cross-vintage as homogeneous E3"},
            {"block": "E4", "role": "component/mechanism; 240 cells; w/o-Inst Gen2", "paper_use": "FIG-E4 TABLE-III RQ3", "not_use": "Gen0/Gen1 Inst; five independent innovations"},
            {"block": "Traffic", "role": "E2 valid; E3 NOT_COMPARABLE", "paper_use": "FIG-E1 only for E2", "not_use": "Table II; three-dataset E3"},
            {"block": "T-Drive", "role": "protocol-sealed reviewer reserve", "paper_use": "limitation sentence only", "not_use": "evaluated dataset count; main figures/tables/results"},
        ],
    )

    he1 = hashes["FIG_E1"]["sha256"]
    he2 = hashes["FIG_E2"]["sha256"]
    he3 = hashes["FIG_E3"]["sha256"]
    he4 = hashes["FIG_E4"]["sha256"]
    ht1 = hashes["TABLE_I"]["sha256"]
    ht2 = hashes["TABLE_II"]["sha256"]
    ht3 = hashes["TABLE_III"]["sha256"]
    p_e1 = hashes["FIG_E1"]["dest"]
    p_e2 = hashes["FIG_E2"]["dest"]
    p_e3 = hashes["FIG_E3"]["dest"]
    p_e4 = hashes["FIG_E4"]["dest"]
    p_t1 = hashes["TABLE_I"]["dest"]
    p_t2 = hashes["TABLE_II"]["dest"]
    p_t3 = hashes["TABLE_III"]["dest"]

    write_text(
        out / "03_FIGURE_SPEC/FIG_C1_PROBLEM_SELECTION_TARGET_MISMATCH_SPEC.md",
        """# FIG-C1 — Problem / selection / target-mismatch (conceptual)

**Type.** Non-experimental schematic. No quantitative experimental values.

**Panels.** (A) public target μ over groups h(i); (B) two-stage selection R→O→U producing usable-update mass; (C) mismatch between usable-update composition and μ.

**Symbols.** μ, h(i), s(i), R, O, U, Y_i, client k, atomic unit i.

**Visual flow.** deployment target μ  vs  opportunity R → observation O → usable update U → training/aggregation mass.

**Caption draft.** Two-stage non-random selection can make the distribution of usable federated updates differ from the intended deployment target μ, so arrival/usable-update risk is not generally interchangeable with deployment-target risk.

**Scientific message.** Motivate target-aware correction (C1–C2).

**Forbidden.** Do not imply measured D_aligned magnitudes; do not rank RAVEN; do not draw h(i)=s(i); do not depict fully real-world mobility as current evidence.
""",
    )
    write_text(
        out / "03_FIGURE_SPEC/FIG_C2_RAVEN_ARCHITECTURE_SPEC.md",
        """# FIG-C2 — RAVEN-MCS architecture (conceptual)

**Type.** Method schematic. Not five independent innovations.

**Flow.** opportunity/design correction → observation correction → usable-update correction → normalized target reconstruction → instantaneous calibration → P2 feasibility-aware adjustment → long-term debt update → aggregation.

**Caption draft.** RAVEN-MCS coordinates selection-layer-aware reconstruction with feasibility-aware instantaneous and long-term target calibration. Modules are coupled, not independently monotone boosters.

**Scientific message.** Contributions 2–3 as one architecture.

**Forbidden.** Do not box Design/Obs/Use/Inst/Debt as five contributions; do not claim each module is empirically necessary; do not show Use as indispensable; do not show Debt as a large lever.
""",
    )
    write_json(
        out / "03_FIGURE_SPEC/CONCEPTUAL_FIGURE_MERGE_DECISION.json",
        {
            "decision": "MERGE_INTO_SINGLE_FRAMEWORK_FIGURE",
            "reason": "TMC page budget: one two-panel framework (problem + architecture) avoids redundancy with four empirical figures.",
            "merged_id": "FIG-C",
            "main_figure_count": 5,
        },
    )
    write_text(
        out / "03_FIGURE_SPEC/FIG_E1_E2_RISK_NONINTERCHANGEABILITY_FINAL_SPEC.md",
        f"""# FIG-E1 — Risk non-interchangeability

**Source.** `{p_e1}`  
**SHA256.** `{he1}`

**Quantity.** D_aligned = ΔRMSE_μ − ΔRMSE_ρ on NSW Traffic complete-aligned (seeds 30001–30020; five formal methods).

**Message.** Arrival/usable-update risk is not generally interchangeable with deployment-target risk.

**Forbidden.** RAVEN superiority ranking; mixing E3 Traffic; T-Drive.

**Caption draft.** Seed-level D_aligned on complete-aligned Traffic traces. A stable nonzero direction supports risk non-interchangeability. This is not a method-ranking figure.
""",
    )
    write_text(
        out / "03_FIGURE_SPEC/FIG_E2_E3_STRUCTURAL_ALIGNMENT_FINAL_SPEC.md",
        f"""# FIG-E2 — Structural target alignment

**Source.** `{p_e2}`  
**SHA256.** `{he2}`

**Datasets.** SensorScope, U-Air. **Metrics.** Δ_group, Δ_{{c,s}}. Seeds 30001–30020.

**Message.** RAVEN's most stable empirical gain is structural target alignment (C3).

**Forbidden.** Traffic E3; Central as a competitive baseline; universal RMSE.

**Caption draft.** Seed-level structural mismatch. Lower is better. RAVEN reduces Δ_group and Δ_{{c,s}} relative to main window/Hajek baselines on comparable datasets.
""",
    )
    write_text(
        out / "03_FIGURE_SPEC/FIG_E3_E3_PREDICTION_RISK_FINAL_SPEC.md",
        f"""# FIG-E3 — Prediction risk

**Source.** `{p_e3}`  
**SHA256.** `{he3}`

**Datasets.** SensorScope, U-Air. **Metrics.** RMSE_μ, Tail RMSE.

**Message.** Structural alignment does not require catastrophic predictive degradation; gains are selective (C4).

**Forbidden.** Universal predictive superiority; Traffic E3 as a third homogeneous block.

**Caption draft.** Deployment-target prediction risk remains competitive. Holm-supported RMSE gains are selective, not universal.
""",
    )
    write_text(
        out / "03_FIGURE_SPEC/FIG_E4_E4_COMPONENT_ABLATION_FINAL_SPEC.md",
        f"""# FIG-E4 — Core component ablation

**Source.** `{p_e4}`  
**SHA256.** `{he4}`

**Configurations.** Full RAVEN; w/o Design, Obs, Use, Inst, Debt. **Inst generation: 2 only.**

**Quantity.** Relative change after removal. For lower-is-better metrics, positive = removal worsens.

**Labels.** Design/Obs/Inst={E4_LABELS['Inst']}; Use={E4_LABELS['Use']}; Debt={E4_LABELS['Debt']} (quantitatively small).

**Message.** Coupled architecture with endpoint-specific trade-offs (C5–C8).

**Forbidden.** All components necessary; Use indispensable; large Debt; Gen0/Gen1 Inst.
""",
    )

    main_figs = [
        {"figure_number_provisional": "1", "figure_id": "FIG-C", "title": "Problem and RAVEN-MCS architecture (merged C1/C2)", "type": "conceptual", "section": "I/III–V", "rq": "setup", "source_csv": "03_FIGURE_SPEC/ (schematic; no experimental CSV)", "source_sha256": "n/a_conceptual", "scientific_message": "mismatch then coupled reconstruction+calibration", "claim_ids": "C1-C3 architecture", "mandatory": True, "main_text": True, "caption_status": "drafted", "new_experiment_required": False, "final_status": "MAIN_SPEC_READY"},
        {"figure_number_provisional": "2", "figure_id": "FIG-E1", "title": "E2 risk non-interchangeability", "type": "empirical", "section": "VII-B", "rq": "RQ1", "source_csv": p_e1, "source_sha256": he1, "scientific_message": "usable-update vs target risk not interchangeable", "claim_ids": "C1,C2", "mandatory": True, "main_text": True, "caption_status": "drafted", "new_experiment_required": False, "final_status": "MAIN_SOURCE_FROZEN"},
        {"figure_number_provisional": "3", "figure_id": "FIG-E2", "title": "E3 structural target alignment", "type": "empirical", "section": "VII-C", "rq": "RQ2", "source_csv": p_e2, "source_sha256": he2, "scientific_message": "stable structural gains on SS/U-Air", "claim_ids": "C3", "mandatory": True, "main_text": True, "caption_status": "drafted", "new_experiment_required": False, "final_status": "MAIN_SOURCE_FROZEN"},
        {"figure_number_provisional": "4", "figure_id": "FIG-E3", "title": "E3 prediction risk", "type": "empirical", "section": "VII-C", "rq": "RQ2", "source_csv": p_e3, "source_sha256": he3, "scientific_message": "competitive prediction; selective gains", "claim_ids": "C4", "mandatory": True, "main_text": True, "caption_status": "drafted", "new_experiment_required": False, "final_status": "MAIN_SOURCE_FROZEN"},
        {"figure_number_provisional": "5", "figure_id": "FIG-E4", "title": "E4 component ablation", "type": "empirical", "section": "VII-D", "rq": "RQ3", "source_csv": p_e4, "source_sha256": he4, "scientific_message": "coupled trade-offs; Use null; Debt small; Inst tradeoff", "claim_ids": "C5-C8", "mandatory": True, "main_text": True, "caption_status": "drafted", "new_experiment_required": False, "final_status": "MAIN_SOURCE_FROZEN"},
    ]
    write_csv(out / "03_FIGURE_SPEC/FINAL_MAIN_FIGURE_REGISTRY_R1.csv", main_figs)
    app_f2 = hashes.get("APP_F2", {})
    write_csv(
        out / "03_FIGURE_SPEC/FINAL_APPENDIX_FIGURE_REGISTRY_R1.csv",
        [
            {"figure_id": "APP-F1", "title": "Local-Hajek degeneracy provenance", "final_status": "APPENDIX_READY", "source_csv": hashes["APP_F1"]["dest"], "source_sha256": hashes["APP_F1"]["sha256"], "new_experiment_required": False, "notes": "weight_range=0 certified collapse provenance"},
            {"figure_id": "APP-F2", "title": "P2 feasibility diagnostic", "final_status": "APPENDIX_READY", "source_csv": app_f2.get("dest", ""), "source_sha256": app_f2.get("sha256", ""), "new_experiment_required": False, "notes": "certificate summary; not exact optimality"},
            {"figure_id": "APP-F-runtime", "title": "Runtime diagnostic", "final_status": "OPTIONAL_APPENDIX", "source_csv": hashes.get("APP_T5", {}).get("dest", ""), "source_sha256": hashes.get("APP_T5", {}).get("sha256", ""), "new_experiment_required": False, "notes": "not a scalability claim"},
            {"figure_id": "FIG5_composition", "title": "Target composition trajectory", "final_status": "INSUFFICIENT_EXISTING_DATA_DO_NOT_RUN", "source_csv": "", "source_sha256": "", "new_experiment_required": False, "notes": "MISSING_NOT_RECORDED"},
            {"figure_id": "FIG9_dataset", "title": "Dataset support context", "final_status": "DROP_LOW_VALUE", "source_csv": "", "source_sha256": "", "new_experiment_required": False, "notes": "Table I already carries this"},
        ],
    )

    write_text(
        out / "04_TABLE_SPEC/TABLE_I_DATASET_PROTOCOL_SPEC.md",
        f"""# TABLE-I — Datasets and experimental protocols

**Source.** `{p_t1}`  
**SHA256.** `{ht1}`

Columns: dataset, domain, client/spatial identity, n clients/spatial units, atomic train/val/test, h(i), s(i), selection role, paper role.

**Datasets.** SensorScope, U-Air, NSW Traffic. **Do not list T-Drive as a completed formal evaluation dataset.**
""",
    )
    write_text(
        out / "04_TABLE_SPEC/TABLE_II_MAIN_EFFECTIVENESS_SPEC.md",
        f"""# TABLE-II — Main effectiveness

**Source.** `{p_t2}`  
**SHA256.** `{ht2}`

**Datasets.** SensorScope, U-Air only.  
**Core methods.** FedAvg-Window, FedAsync-Window, TimeAlign-Agg, Local-Hajek, TwoStage-Hajek, RAVEN-MCS.  
**Optional rows.** Inst-Cal, Debt-Cal (already in source). Reference-only (Central, SimOracle) may move to Appendix if width requires.

**Metrics.** RMSE_μ, Tail RMSE, Δ_group, Δ_{{c,s}} as mean±std; Holm tags are not numerical-best marks.

**Forbidden.** Traffic E3; T-Drive; universal RMSE wording.
""",
    )
    write_text(
        out / "04_TABLE_SPEC/TABLE_III_CORE_ABLATION_SPEC.md",
        f"""# TABLE-III — Core ablation

**Source.** `{p_t3}`  
**SHA256.** `{ht3}`

Rows: Full RAVEN; w/o Design, Obs, Use, Inst, Debt. Datasets SensorScope and U-Air. Metrics Δ_group, Δ_{{c,s}}, RMSE_μ, Tail RMSE. **w/o-Inst generation 2 only.**
""",
    )
    write_csv(
        out / "04_TABLE_SPEC/FINAL_MAIN_TABLE_REGISTRY_R1.csv",
        [
            {"table_id": "TABLE-I", "title": "Datasets and protocols", "section": "VII-A", "rq": "setup", "source_csv": p_t1, "source_sha256": ht1, "metrics": "setup", "datasets": "SensorScope,U-Air,NSW-Traffic", "methods": "n/a", "claim_ids": "setup", "mandatory": True, "main_text": True, "final_status": "MAIN_SOURCE_FROZEN"},
            {"table_id": "TABLE-II", "title": "Main effectiveness", "section": "VII-C", "rq": "RQ2", "source_csv": p_t2, "source_sha256": ht2, "metrics": "RMSE_mu,Tail_RMSE,Delta_group,Delta_c_s", "datasets": "SensorScope,U-Air", "methods": "core E3 + optional Inst/Debt-Cal", "claim_ids": "C3,C4", "mandatory": True, "main_text": True, "final_status": "MAIN_SOURCE_FROZEN"},
            {"table_id": "TABLE-III", "title": "Core ablation", "section": "VII-D", "rq": "RQ3", "source_csv": p_t3, "source_sha256": ht3, "metrics": "Delta_group,Delta_c_s,RMSE_mu,Tail_RMSE", "datasets": "SensorScope,U-Air", "methods": "RAVEN + five w/o-X", "claim_ids": "C5-C8", "mandatory": True, "main_text": True, "final_status": "MAIN_SOURCE_FROZEN"},
        ],
    )
    write_csv(
        out / "04_TABLE_SPEC/FINAL_APPENDIX_TABLE_REGISTRY_R1.csv",
        [
            {"table_id": "APP-T1", "title": "E1 balanced sanity", "final_status": "APPENDIX_READY", "source_csv": hashes["APP_T1"]["dest"], "source_sha256": hashes["APP_T1"]["sha256"], "new_experiment_required": False},
            {"table_id": "APP-T2", "title": "Full paired statistical results", "final_status": "APPENDIX_READY", "source_csv": hashes.get("APP_T2", {}).get("dest", "RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1/01_PAPER_CORE/STATISTICS/FINAL_STATISTICS_MASTER.csv"), "source_sha256": hashes.get("APP_T2", {}).get("sha256", ""), "new_experiment_required": False},
            {"table_id": "APP-T3", "title": "Full method results", "final_status": "APPENDIX_READY", "source_csv": hashes.get("APP_T3", {}).get("dest", ""), "source_sha256": hashes.get("APP_T3", {}).get("sha256", ""), "new_experiment_required": False},
            {"table_id": "APP-T4", "title": "P2 feasibility summary", "final_status": "APPENDIX_READY", "source_csv": app_f2.get("dest", ""), "source_sha256": app_f2.get("sha256", ""), "new_experiment_required": False},
            {"table_id": "APP-T5", "title": "Runtime/system summary", "final_status": "OPTIONAL_APPENDIX", "source_csv": hashes.get("APP_T5", {}).get("dest", ""), "source_sha256": hashes.get("APP_T5", {}).get("sha256", ""), "new_experiment_required": False},
        ],
    )

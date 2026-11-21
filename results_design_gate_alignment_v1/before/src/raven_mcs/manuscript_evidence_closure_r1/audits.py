"""Audits, T-Drive Go/No-Go, completeness, and claim registries."""

from __future__ import annotations

from pathlib import Path

from raven_mcs.paper_data_r1.io_util import sha256_file, write_csv, write_json, write_text
from raven_mcs.manuscript_evidence_closure_r1.constants import E4_LABELS


def write_audits(r2: Path, out: Path) -> None:
    write_json(
        out / "00_audit/FINAL_H_S_SEMANTICS_FOR_MANUSCRIPT.json",
        {
            "authority": "paper_ready_r2 TABLE_DATASET_SUMMARY_R2 + dataset metadata",
            "h_equals_s": False,
            "SensorScope": {
                "h(i)": "four UTC time-of-day groups H1:00–06, H2:06–12, H3:12–18, H4:18–24; train-split UTC block mass; no test labels",
                "s(i)": "spatial_id × four time blocks × weekday/weekend (processed opportunity_stratum)",
            },
            "U-Air": {
                "h(i)": "four UTC time-of-day groups H1:00–06, H2:06–12, H3:12–18, H4:18–24; train-split UTC block mass; no test labels",
                "s(i)": "spatial_id × four time blocks × weekday/weekend (processed opportunity_stratum)",
            },
            "NSW-Traffic": {
                "h(i)": "repeatable UTC time-of-day 4-block; train-split mass only",
                "s(i)": "frozen real_region_id × time_block × weekday_flag (E2 public-target 4 regions)",
                "e3_performance": "NOT_COMPARABLE cross-vintage; do not use as homogeneous E3 block",
            },
            "T-Drive": "protocol-only reserve; not current manuscript evidence",
            "forbidden": "do not describe SensorScope/U-Air h(i) as spatial × time",
        },
    )
    write_text(
        out / "00_audit/FINAL_H_S_SEMANTICS_FOR_MANUSCRIPT.md",
        "\n".join(
            [
                "# Final h(i) / s(i) manuscript semantics",
                "",
                "Authority: R2 `TABLE_DATASET_SUMMARY_R2.csv`.",
                "",
                "For SensorScope and U-Air, **h(i)** is four UTC time-of-day groups (H1–H4). **s(i)** is spatial identity × four time blocks × weekday/weekend. Therefore **h(i) ≠ s(i)**.",
                "",
                "Do not describe h(i) as spatial × time.",
                "",
                "NSW Traffic uses the sealed E2 public-target / region-stratum semantics. E3 Traffic performance inference remains NOT_COMPARABLE.",
                "",
            ]
        ),
    )
    write_json(
        out / "00_audit/FINAL_RQ_REGISTRY.json",
        {
            "n_main_empirical_rqs": 3,
            "RQ1": "Does two-stage non-random selection create a meaningful deployment-target risk mismatch?",
            "RQ2": "Does RAVEN-MCS reduce structural deployment-target mismatch while maintaining competitive target prediction risk?",
            "RQ3": "How do the core correction and calibration components contribute to RAVEN's structural and predictive behavior?",
            "not_main": "old RQ4–RQ6 appear only as theory, diagnostics, limitations, future work, or appendix",
        },
    )
    write_text(
        out / "00_audit/EXPERIMENT_ROLE_REGISTRY.md",
        "\n".join(
            [
                "# Experiment role registry",
                "",
                "- **E1:** Balanced/no-harm sanity evidence. Not a superiority claim.",
                "- **E2:** Risk-semantic non-interchangeability / problem evidence (Traffic PROFILE-S1). Not a RAVEN ranking figure.",
                "- **E3:** Main effectiveness on SensorScope and U-Air only. Traffic E3 is NOT_COMPARABLE.",
                "- **E4:** Core mechanism / ablation on the final 240-cell family. w/o-Inst Generation 2 only.",
                "- **Traffic:** E2 motivation/risk-semantic role; not homogeneous E3 performance evidence.",
                "- **T-Drive:** protocol-only reserve; NOT current manuscript evidence.",
                "",
            ]
        ),
    )
    write_json(
        out / "00_audit/NO_RUN_ATTESTATION.json",
        {
            "training_started": False,
            "formal_runs_started": False,
            "canary_started": False,
            "tdrive_formal_started": False,
            "e1_e2_e3_e4_reruns": 0,
            "r2_not_modified": True,
            "writes_only_under": "manuscript_evidence_closure_r1/",
        },
    )
    write_json(
        out / "00_audit/R2_AUTHORITY.json",
        {
            "sole_paper_data_authority": "paper_ready_r2 (R2 unpacked package; CORE/FULL zips are packaging of the same tree)",
            "r2_index_sha256": sha256_file(r2 / "00_index/CLAIM_TO_DATA_MAP_R2.csv")
            if (r2 / "00_index/CLAIM_TO_DATA_MAP_R2.csv").is_file()
            else "",
            "do_not_use_r1_when_r2_exists": True,
        },
    )


def write_claim_alignment(out: Path) -> None:
    write_text(
        out / "07_claim_alignment/INTRODUCTION_CONTRIBUTION_AUDIT.md",
        "\n".join(
            [
                "# Introduction contribution audit",
                "",
                "No standalone Introduction manuscript file exists in the workspace. This registry is the proposed final contribution architecture.",
                "",
                "Do not claim that each module is individually necessary.",
                "",
            ]
        ),
    )
    write_json(
        out / "07_claim_alignment/INTRODUCTION_CONTRIBUTION_REGISTRY.json",
        {
            "contribution_1": "Deployment-target risk semantics under multi-layer non-random selection (E2; C1–C2).",
            "contribution_2": "Selection-layer-aware coordinated correction / reconstruction (E3 architecture; C3–C4).",
            "contribution_3": "Feasibility-aware instantaneous + long-term target calibration, supported by structural-alignment evidence (E3/E4; C3, C5–C8). Not a claim that every module is individually necessary.",
            "forbidden": [
                "each module is individually necessary",
                "universal RMSE superiority",
                "Use is empirically necessary",
            ],
        },
    )
    theory_rows = [
        {
            "claim": "Two-stage/multi-layer selection can induce update vs deployment-target mismatch",
            "class": "DIRECTLY_EMPIRICALLY_SUPPORTED",
            "evidence": "E2 D_aligned / risk non-interchangeability",
            "intro_empirical": True,
        },
        {
            "claim": "Arrival/usable-update risk is not generally interchangeable with deployment-target risk",
            "class": "DIRECTLY_EMPIRICALLY_SUPPORTED",
            "evidence": "E2 D_aligned sign stability",
            "intro_empirical": True,
        },
        {
            "claim": "Hajek / two-stage IPW reconstruction of selection layers",
            "class": "INDIRECTLY_SUPPORTED",
            "evidence": "E3 TwoStage-Hajek and RAVEN vs window baselines on structural metrics",
            "intro_empirical": True,
        },
        {
            "claim": "Instantaneous target calibration (P2) existence/feasibility",
            "class": "INDIRECTLY_SUPPORTED",
            "evidence": "E4 Inst + P2 feasibility audit; exact experimental optimality NOT reconstructable",
            "intro_empirical": True,
        },
        {
            "claim": "Exact P2 uniqueness/optimality under theorem assumptions",
            "class": "THEORY_ONLY_VALID",
            "evidence": "mathematical optimizer claim; C10 forbids experimental exact-optimality language",
            "intro_empirical": False,
        },
        {
            "claim": "Long-term debt calibration has a structural role",
            "class": "DIRECTLY_EMPIRICALLY_SUPPORTED",
            "evidence": "E4 Debt STRUCTURAL_ONLY_SUPPORTED, quantitatively small",
            "intro_empirical": True,
        },
        {
            "claim": "Usable-update IPW (Use) is empirically necessary",
            "class": "NOT_EMPIRICALLY_TESTED",
            "note": "The component exists and was ablated; the sealed result is NO_CLEAR_EFFECT. Do not list as empirically demonstrated necessity.",
            "evidence": "E4 Use NO_CLEAR_EFFECT",
            "intro_empirical": False,
        },
        {
            "claim": "RAVEN reduces structural mismatch on comparable SensorScope/U-Air",
            "class": "DIRECTLY_EMPIRICALLY_SUPPORTED",
            "evidence": "E3 Holm on Delta_group and Delta_c_s vs main baselines",
            "intro_empirical": True,
        },
        {
            "claim": "Universal RMSE superiority / three-dataset homogeneous E3",
            "class": "OVERCLAIM_REQUIRES_WORDING_REPAIR",
            "evidence": "Forbidden by C4/C9; Traffic E3 NOT_COMPARABLE",
            "intro_empirical": False,
        },
        {
            "claim": "Real taxi-mobility opportunity as current formal evidence",
            "class": "NOT_EMPIRICALLY_TESTED",
            "evidence": "T-Drive protocol sealed but no formal performance block",
            "intro_empirical": False,
        },
    ]
    write_csv(out / "07_claim_alignment/SECTION_III_VI_THEORY_EVIDENCE_AUDIT.csv", theory_rows)
    write_text(
        out / "07_claim_alignment/SECTION_III_VI_THEORY_EVIDENCE_AUDIT.md",
        "\n".join(
            [
                "# Section III–VI theory/evidence audit",
                "",
                "No compiled Section III–VI manuscript exists. Claims are audited against the sealed method/experiment specification and R2 evidence.",
                "",
                "A proven theorem does not require an experiment for every term. An evidence gap is recorded only if Introduction and Conclusion treat the claim as experimentally demonstrated without E1–E4 support.",
                "",
                "| Claim | Class | Evidence |",
                "|---|---|---|",
            ]
            + [f"| {r['claim']} | {r['class']} | {r['evidence']} |" for r in theory_rows]
            + ["", "No new experiment is required solely because a theorem is theory-only.", ""]
        ),
    )
    write_text(
        out / "07_claim_alignment/CONCLUSION_CLAIM_AUDIT.md",
        "\n".join(
            [
                "# Conclusion claim audit",
                "",
                "No prior Conclusion manuscript was found. The R1 conclusion draft is claim-ceiling safe:",
                "- includes target-risk mismatch, coordinated architecture, structural alignment, selective prediction, component trade-offs;",
                "- excludes universal dominance, Use-necessity, large Debt, certified P2 optimality, homogeneous three-dataset E3.",
                "",
            ]
        ),
    )
    write_text(
        out / "07_claim_alignment/ABSTRACT_RESULT_CEILING.md",
        "\n".join(
            [
                "# Abstract result ceiling",
                "",
                "## Allowed quantitative claims",
                "- E2: D_aligned has a stable nonzero direction on Traffic complete-aligned (n=20 seeds × 5 methods).",
                "- E3: RAVEN reduces Δ_group and Δ_{c,s} vs main window/Hajek baselines on SensorScope and U-Air (Holm-supported in the sealed secondary families).",
                "- E3: RMSE_μ remains competitive; Holm-supported RMSE gains are selective (e.g., U-Air vs TwoStage-Hajek), not universal.",
                "- E4: component labels and small Debt magnitudes as in R2 (240 cells; w/o-Inst Gen 2).",
                "",
                "## Allowed qualitative claims",
                "- Two-stage selection can induce deployment-target mismatch.",
                "- Arrival risk is not generally interchangeable with deployment-target risk.",
                "- RAVEN is a coupled correction/calibration architecture with endpoint-dependent component roles.",
                "",
                "## Forbidden claims",
                "- universal RMSE superiority;",
                "- all baselines significantly beaten;",
                "- all five components indispensable;",
                "- Use is empirically necessary;",
                "- Debt has a large effect;",
                "- all P2 solutions experimentally certified exactly optimal;",
                "- three-dataset homogeneous E3 superiority;",
                "- T-Drive formal performance results.",
                "",
            ]
        ),
    )


def write_tdrive_decision(out: Path) -> dict:
    go_checks = {
        "1_positioning_depends_on_mobility_opportunity": {
            "true": False,
            "note": "Core positioning is two-stage/multi-layer non-random selection and target-risk calibration, not taxi-mobility-induced opportunity as a required empirical pillar.",
        },
        "2_e1e4_cannot_support_mobility_aspect": {
            "true": False,
            "note": "The mobility-specific aspect is not a core empirical contribution in C1–C10. E2–E4 close the selection/target-alignment story.",
        },
        "3_reviewer_can_ask_where_is_real_mobility": {
            "true": True,
            "note": "A TMC reviewer can still ask this as a presentation/external-validity question.",
        },
        "4_protocol_tests_same_core_claim": {
            "true": True,
            "note": "Sealed T-Drive protocol targets the same structural-alignment claim under real R.",
        },
        "5_clear_manuscript_placement": {
            "true": True,
            "note": "Would be a short external-validation note, not a new storyline.",
        },
        "6_high_value_vs_length": {
            "true": False,
            "note": "50 runs plus real-R/controlled-O/U disclosure add semantic burden larger than incremental evidence for C1–C10.",
        },
    }
    all_go = all(v["true"] for v in go_checks.values())
    nogo_hits = [
        "E1–E4 already close C1–C10",
        "T-Drive would not materially change the allowed Introduction/Conclusion if mobility is not a core empirical contribution",
        "controlled O/U weaken the claimed realism",
        "page budget is better spent explaining E2–E4",
        "new semantic burden (fleet split, h fallback, controlled layers) is large relative to evidence value",
        "running it mainly as one more dataset is forbidden by the round philosophy",
    ]
    decision = "C"
    name = "TDRIVE_RESERVE_FOR_REVIEWER_ONLY"
    payload = {
        "decision": name,
        "decision_code": decision,
        "go_all_true": all_go,
        "go_criteria": go_checks,
        "nogo_hits": nogo_hits,
        "do_not_run_in_this_round": True,
        "do_not_run_before_submission": True,
        "protocol_seal_is_not_authorization": True,
        "rationale": "A TMC reviewer may ask about real mobility, but that is an external-validity limitation—not a missing piece of the core claim chain. Keep the sealed 50-run protocol as reviewer-response reserve. Do not execute it to complete the present manuscript.",
    }
    write_json(out / "09_tdrive_decision/TDRIVE_MANUSCRIPT_LEVEL_GO_NO_GO.json", payload)
    write_text(
        out / "09_tdrive_decision/TDRIVE_MANUSCRIPT_LEVEL_GO_NO_GO.md",
        "\n".join(
            [
                "# T-Drive manuscript-level Go/No-Go",
                "",
                f"**Decision: {decision}. {name}**",
                "",
                "Evaluated only against manuscript-level criteria. Protocol Seal readiness is not a Go reason.",
                "",
                "## Go criteria (all required)",
                *[f"- {'YES' if v['true'] else 'NO'} — {k}: {v['note']}" for k, v in go_checks.items()],
                "",
                "All-true? **No.** Go is not recommended.",
                "",
                "## No-Go / reserve reasons",
                *[f"- {x}" for x in nogo_hits],
                "",
                "## Action",
                "Do not run T-Drive before submission. Keep the sealed protocol as reviewer-response reserve.",
                "",
            ]
        ),
    )
    return payload


def write_completeness_and_quality(out: Path, tdrive: dict) -> None:
    rows = [
        {
            "row": "Problem motivation",
            "importance_to_core": "high",
            "existing_evidence": "E2 Traffic D_aligned; C1–C2",
            "evidence_strength": "strong",
            "missing": "none for core claim",
            "requires_new_experiment": False,
            "paper_action": "Fig. 1 + RQ1",
        },
        {
            "row": "Risk-semantic distinction",
            "importance_to_core": "high",
            "existing_evidence": "E2 RMSE_mu vs RMSE_rho / D_aligned",
            "evidence_strength": "strong",
            "missing": "none",
            "requires_new_experiment": False,
            "paper_action": "Results VII-B",
        },
        {
            "row": "Method correctness",
            "importance_to_core": "high",
            "existing_evidence": "E0/E1 sanity + sealed runners",
            "evidence_strength": "adequate",
            "missing": "none requiring new science",
            "requires_new_experiment": False,
            "paper_action": "cite E1 appendix",
        },
        {
            "row": "Main structural effectiveness",
            "importance_to_core": "high",
            "existing_evidence": "E3 SensorScope/U-Air Holm on Delta_group/Delta_c_s",
            "evidence_strength": "strong",
            "missing": "Traffic E3 excluded by design",
            "requires_new_experiment": False,
            "paper_action": "Table II + Fig. 2",
        },
        {
            "row": "Prediction effectiveness",
            "importance_to_core": "medium-high",
            "existing_evidence": "E3 RMSE_mu/Tail competitive, selective Holm",
            "evidence_strength": "adequate_selective",
            "missing": "universal RMSE (forbidden to claim)",
            "requires_new_experiment": False,
            "paper_action": "Table II wording",
        },
        {
            "row": "Mechanism explanation",
            "importance_to_core": "high",
            "existing_evidence": "E4 240-cell ablation + labels",
            "evidence_strength": "strong_with_tradeoffs",
            "missing": "none",
            "requires_new_experiment": False,
            "paper_action": "Table III + Fig. 3",
        },
        {
            "row": "Theory support",
            "importance_to_core": "medium",
            "existing_evidence": "method specification + P2 theory vs C10 experimental boundary",
            "evidence_strength": "adequate",
            "missing": "experimental exact P2 optimality (not reconstructable)",
            "requires_new_experiment": False,
            "paper_action": "wording, not new runs",
        },
        {
            "row": "External mobility validity",
            "importance_to_core": "medium_for_TMC_presentation",
            "existing_evidence": "protocol seal only; no formal T-Drive block",
            "evidence_strength": "absent_as_performance_evidence",
            "missing": "formal real-mobility performance",
            "requires_new_experiment": False,
            "paper_action": "limitation + reviewer reserve (T-Drive C)",
        },
        {
            "row": "System cost",
            "importance_to_core": "low",
            "existing_evidence": "optional runtime diagnostics if present",
            "evidence_strength": "not_core",
            "missing": "full cost study",
            "requires_new_experiment": False,
            "paper_action": "do not trigger new experiments",
        },
        {
            "row": "Robustness",
            "importance_to_core": "low-medium",
            "existing_evidence": "paired seeds; E4 one-factor family",
            "evidence_strength": "limited_by_design",
            "missing": "broad robustness sweeps",
            "requires_new_experiment": False,
            "paper_action": "limitation; no new family",
        },
    ]
    write_csv(out / "10_report/MANUSCRIPT_EVIDENCE_COMPLETENESS_MATRIX.csv", rows)
    write_json(
        out / "10_report/EXPERIMENT_STOP_DECISION_R1.json",
        {
            "decision": "STOP_ALL_NEW_EXPERIMENTS_WRITE_MANUSCRIPT",
            "tdrive": tdrive["decision"],
            "other_experiment_families_recommended": [],
            "reason": "E1–E4 close the core claim chain. External mobility is a limitation/reserve, not a submission-blocking missing experiment.",
        },
    )
    write_text(
        out / "10_report/PAPER_QUALITY_AUDIT_R1.md",
        "\n".join(
            [
                "# Paper quality audit (internal heuristic, not an acceptance probability)",
                "",
                "| Dimension | Score (1–10) | Note |",
                "|---|---:|---|",
                "| Problem novelty | 8 | Target-risk vs arrival-risk under two-stage MCS selection is a sharp TMC-relevant problem. |",
                "| Methodological novelty | 8 | Coordinated correction + instantaneous/debt calibration is distinct from generic FL/imputation. |",
                "| Theoretical strength | 7 | Architecture is specified; exact experimental P2 optimality is bounded (C10). |",
                "| Evidence quality | 8 | Sealed E2–E4 with paired seeds, Holm families, and honest labels. |",
                "| Experimental completeness | 7 | Core claims closed; mobility external validity reserved. |",
                "| TMC fit | 8 | MCS selection/deployment mismatch is in-scope; do not oversell mobility traces. |",
                "| Overclaim risk | 6 | Residual risk if Abstract/Intro drift toward universal RMSE or component necessity. Ceiling files exist. |",
                "| Reproducibility | 8 | R2 hashes, configs, and EventTrace identity are sealed. |",
                "| Limitations | 8 | Explicit: Traffic vintage, P2, Use, small Debt, no T-Drive performance. |",
                "| Remaining acceptance risks | — | Reviewer may ask for real mobility, runtime, or broader robustness; answer with reserve/limitations rather than new families. |",
                "",
                f"T-Drive decision: `{tdrive['decision']}`.",
                "",
            ]
        ),
    )
    write_json(out / "10_report/E4_LABELS_USED.json", E4_LABELS)

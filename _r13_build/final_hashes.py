import hashlib
from pathlib import Path
W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\hashes.txt")
L=[]
def sha(p):
    p = Path(p)
    if not p.exists(): return "<absent>"
    h = hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda: f.read(1<<20), b""): h.update(c)
    return h.hexdigest()

ITEMS = [
 ("FIG_E3 bundle", "RAVEN_MCS_PUBLIC_REPRO_R1/figures/FIG_E3_E3_PREDICTION_RISK.csv"),
 ("FIG_E3 clean",  "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E3_E3_PREDICTION_RISK.csv"),
 ("FIG_E3 snapshot","snapshots/2026-09-29-pre-theta-resource/figure_data/FIG_E3_E3_PREDICTION_RISK.csv"),
 ("FIG_E3 extracted","TO_OVERLEAF_paper_tmc_r1_clean_extracted/figure_data/FIG_E3_E3_PREDICTION_RISK.csv"),
 ("FIG_E4 bundle", "RAVEN_MCS_PUBLIC_REPRO_R1/figures/FIG_E4_E4_COMPONENT_ABLATION.csv"),
 ("FIG_E4 clean",  "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv"),
 ("FIG_E4 snapshot","snapshots/2026-09-29-pre-theta-resource/figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv"),
 ("FIG_W1 bundle", "RAVEN_MCS_PUBLIC_REPRO_R1/figures/FIG_W1_DESIGN_GATE.csv"),
 ("FIG_W1 clean",  "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_W1_DESIGN_GATE.csv"),
 ("FIG_W1 snapshot","snapshots/2026-09-29-pre-theta-resource/figure_data/FIG_W1_DESIGN_GATE.csv"),
 ("TABLE_II bundle", "RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_MAIN_EFFECTIVENESS.csv"),
 ("TABLE_II P0", "post_review/P0_ni_artifact/tables/TABLE_II_MAIN_EFFECTIVENESS.csv"),
 ("TABLE_II_FREEZE bundle","RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_FREEZE.json"),
 ("TABLE_II_FREEZE P0","post_review/P0_ni_artifact/tables/TABLE_II_FREEZE.json"),
 ("TABLE_E3 bundle", "RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_E3_MAIN_EFFECTIVENESS.csv"),
 ("TABLE_E3 P0", "post_review/P0_ni_artifact/tables/TABLE_E3_MAIN_EFFECTIVENESS.csv"),
 ("TABLE_E3 r2", "paper_ready_r2/06_table_sources/TABLE_E3_MAIN_EFFECTIVENESS.csv"),
 ("TABLE_E3 freeze","RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1/16_TABLE_SOURCES/r2/TABLE_E3_MAIN_EFFECTIVENESS.csv"),
 ("TABLE_E4_COMPONENT_EFFECTS bundle","RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_E4_COMPONENT_EFFECTS.csv"),
 ("TABLE_E4_COMPONENT_EFFECTS r2","paper_ready_r2/06_table_sources/TABLE_E4_COMPONENT_EFFECTS.csv"),
 ("TABLE_E4_CORE_ABLATION bundle","RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_E4_CORE_ABLATION.csv"),
 ("TABLE_E4_CORE_ABLATION r2","paper_ready_r2/06_table_sources/TABLE_E4_CORE_ABLATION.csv"),
 ("E4_ABLATION_RELATIVE_CHANGE bundle","RAVEN_MCS_PUBLIC_REPRO_R1/tables/E4_ABLATION_RELATIVE_CHANGE.csv"),
 ("E4_ABLATION_RELATIVE_CHANGE r2","paper_ready_r2/01_core_data/e4/E4_ABLATION_RELATIVE_CHANGE.csv"),
 ("TABLE_E3_FULL_METHODS_SUPPLEMENT bundle","RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_E3_FULL_METHODS_SUPPLEMENT.csv"),
 ("TABLE_E3_FULL_METHODS_SUPPLEMENT r2","paper_ready_r2/06_table_sources/TABLE_E3_FULL_METHODS_SUPPLEMENT.csv"),
 ("PAPER_EVIDENCE_MASTER_LONG bundle","RAVEN_MCS_PUBLIC_REPRO_R1/tables/PAPER_EVIDENCE_MASTER_LONG.csv"),
 ("PAPER_EVIDENCE_MASTER_LONG r2","paper_ready_r2/01_core_data/master/PAPER_EVIDENCE_MASTER_LONG.csv"),
 ("TABLE_II_WORSTGROUP_PER_SEED bundle","RAVEN_MCS_PUBLIC_REPRO_R1/tables/TABLE_II_WORSTGROUP_PER_SEED.csv"),
 ("TABLE_II_WORSTGROUP_PER_SEED P0","post_review/P0_ni_artifact/tables/TABLE_II_WORSTGROUP_PER_SEED.csv"),
 ("MANIFEST bundle","RAVEN_MCS_PUBLIC_REPRO_R1/MANIFEST.csv"),
 ("MANIFEST_ADDITIONS bundle","RAVEN_MCS_PUBLIC_REPRO_R1/w1/MANIFEST_ADDITIONS.csv"),
 ("BUNDLE_SUMMARY bundle","RAVEN_MCS_PUBLIC_REPRO_R1/BUNDLE_SUMMARY.json"),
 ("build script bundle","RAVEN_MCS_PUBLIC_REPRO_R1/scripts/build_public_repro_bundle.py"),
 ("build script worktree","scripts/build_public_repro_bundle.py"),
 ("rebuild_table_ii_tolerance bundle","RAVEN_MCS_PUBLIC_REPRO_R1/scripts/rebuild_table_ii_tolerance.py"),
 ("rebuild_table_ii_tolerance P0","post_review/P0_ni_artifact/scripts/rebuild_table_ii_tolerance.py"),
 ("SCD_PHI_DECISION bundle","RAVEN_MCS_PUBLIC_REPRO_R1/tables/SCD_PHI_DECISION.json"),
 ("SCD_PHI_DECISION worktree","post_review/C2_scd_phi/SCD_PHI_DECISION.json"),
 ("ERRATA bundle","RAVEN_MCS_PUBLIC_REPRO_R1/w1/audit_v5/round_v5_1/ERRATA_FOR_PAPER.md"),
 ("A3P_RESOURCE_UPAIR bundle","RAVEN_MCS_PUBLIC_REPRO_R1/w1/audit_v5/round_v5_1/A3P_RESOURCE_UPAIR.csv"),
 ("C3_CELL_DIFF worktree","results_seed_path_audit_r1/C3_CELL_DIFF.csv"),
 ("c8_apply worktree","results_seed_path_audit_r1/c8_apply_figure_data.py"),
]
for label, rel in ITEMS:
    p = W/rel
    sz = p.stat().st_size if p.exists() else -1
    L.append(f"{label:<40} {sz:>10}  {sha(p)}  {rel}")
OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("\n".join(L))

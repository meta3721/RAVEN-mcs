import csv, hashlib, json, os
from pathlib import Path
from collections import defaultdict

B = Path(r"C:\Cursor\raven.mcs\RAVEN_MCS_PUBLIC_REPRO_R1")
W = Path(r"C:\Cursor\raven.mcs")

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

brec = {}
for dp, dn, fn in os.walk(B):
    for n in fn:
        p = Path(dp) / n
        brec[p.relative_to(B).as_posix()] = sha(p)

matches = json.loads(Path(r"C:\Cursor\raven.mcs\_r13_build\matches.json").read_text())

# ---- intended source mapping (from scripts/build_public_repro_bundle.py) ----
def intended(rel):
    """Return list of candidate intended worktree paths."""
    out = []
    if rel.startswith("configs/protocol_closure/"):
        out.append(W / "configs/frozen/e3_multidataset_protocol_closure" / rel[len("configs/protocol_closure/"):])
    if rel.startswith("eventtraces/e1_formal/"):
        out.append(W / "data/frozen/e1_r2/formal" / rel[len("eventtraces/e1_formal/"):])
    if rel.startswith("eventtraces/e2/"):
        out.append(W / "artifacts/e2_traffic_formal_runs_r1/eventtraces" / rel[len("eventtraces/e2/"):])
    if rel.startswith("eventtraces/e3/"):
        out.append(W / "artifacts/e3_formal_runs_r1/eventtraces" / rel[len("eventtraces/e3/"):])
    if rel.startswith("processed/"):
        out.append(W / "data/processed" / rel[len("processed/"):])
    exact = {
     "configs/e2_formal_run_config.json": "artifacts/e2_traffic_formal_runs_r1/FORMAL_RUN_CONFIG.json",
     "configs/e2_profile_registry.json": "configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json",
     "configs/e3_source_hashes.json": "configs/frozen/e3_target_pair_metric_final_r1/E3_FINAL_INTEGRATION_SOURCE_HASHES.json",
     "configs/e4_one_factor_spec.json": "artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json",
     "eventtraces/E2_EVENTTRACE_INDEX.csv": "paper_ready_r2/05_provenance/E2_EVENTTRACE_INDEX_120.csv",
     "eventtraces/E3_EVENTTRACE_MANIFEST.json": "artifacts/e3_formal_runs_r1/E3_FORMAL_EVENTTRACE_MANIFEST.json",
     "eventtraces/E2_EVENTTRACE_MANIFEST.csv": "artifacts/e2_traffic_formal_runs_r1/eventtrace_manifest.csv",
     "tables/TABLE_E1_BALANCED_SANITY.csv": "paper_ready_r2/06_table_sources/TABLE_E1_BALANCED_SANITY.csv",
     "tables/TABLE_E2_RISK_SEMANTICS.csv": "paper_ready_r2/06_table_sources/TABLE_E2_RISK_SEMANTICS.csv",
     "tables/TABLE_E3_FULL_METHODS_SUPPLEMENT.csv": "paper_ready_r2/06_table_sources/TABLE_E3_FULL_METHODS_SUPPLEMENT.csv",
     "tables/TABLE_E4_CORE_ABLATION.csv": "paper_ready_r2/06_table_sources/TABLE_E4_CORE_ABLATION.csv",
     "tables/TABLE_E4_COMPONENT_EFFECTS.csv": "paper_ready_r2/06_table_sources/TABLE_E4_COMPONENT_EFFECTS.csv",
     "tables/TABLE_DATASET_SUMMARY.csv": "paper_ready_r2/06_table_sources/TABLE_DATASET_SUMMARY.csv",
     "tables/PAPER_EVIDENCE_MASTER_LONG.csv": "paper_ready_r2/01_core_data/master/PAPER_EVIDENCE_MASTER_LONG.csv",
     "tables/E4_ABLATION_RELATIVE_CHANGE.csv": "paper_ready_r2/01_core_data/e4/E4_ABLATION_RELATIVE_CHANGE.csv",
     "tables/E3_FORMAL_HOLM_RESULTS.csv": "artifacts/e3_formal_runs_r1/E3_FORMAL_HOLM_RESULTS.csv",
     "tables/E4_ABLATION_HOLM_RESULTS.csv": "artifacts/e4_core_mechanism_ablation_r1/E4_ABLATION_HOLM_RESULTS.csv",
     "tables/CONFIG_REGISTRY.csv": "paper_ready_r2/05_provenance/FINAL_CONFIG_REGISTRY_R2.csv",
     "certificate/CERTIFICATE_STRESS.csv": "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_CERTIFICATE_STRESS.csv",
     "certificate/CERTIFICATE_WINDOWS.csv": "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_CERTIFICATE_WINDOWS.csv",
     "certificate/CERTIFICATE_TRACK_METRICS.csv": "results_sag_g1/round_r1m/eval/R1M_TRACK_METRICS.csv",
     "certificate/CERTIFICATE_BY_WINDOW.csv": "results_sag_g1/round_r1m/certificate/R1M_CERTIFICATE_BY_WINDOW.csv",
    }
    p0 = {"tables/TABLE_II_MAIN_EFFECTIVENESS.csv","tables/TABLE_II_FREEZE.json",
          "tables/TABLE_II_WORSTGROUP_PER_SEED.csv","tables/TABLE_E3_MAIN_EFFECTIVENESS.csv"}
    if rel in p0:
        out.append(W / "post_review/P0_ni_artifact/tables" / rel.split("/")[-1])
    if rel == "tdrive/TD_R_E3_PAIRED.csv":
        out.append(W / "post_review/P0_ni_artifact/tables/TD_R_E3_PAIRED.csv")
    if rel in exact:
        out.append(W / exact[rel])
    if rel.startswith("figures/") and rel.endswith(".csv"):
        out.append(W / "TO_OVERLEAF_paper_tmc_r1_clean/figure_data" / rel.split("/")[-1])
    if rel.startswith("cityscanner/"):
        n = rel.split("/")[-1]
        sub = {"CS_PHI_DECISION.json":"CS_PHI_DECISION.json","GO.json":"GO.json",
               "AUDIT.json":"C1_KILL_AUDIT.json","CS_E3.csv":"tables/CS_E3.csv",
               "CS_E3_PAIRED.csv":"tables/CS_E3_PAIRED.csv","CS_E3_SUMMARY.csv":"tables/CS_E3_SUMMARY.csv",
               "CS_PHI.csv":"tables/CS_PHI.csv"}.get(n)
        if sub: out.append(W / "results_c1_cityscanner/round_v1" / sub)
    if rel.startswith("cityscanner_p2/"):
        n = rel.split("/")[-1]
        sub = {"JO_PHI_DECISION.json":"JO_PHI_DECISION.json","GO.json":"GO.json",
               "AUDIT.json":"JO_KILL_AUDIT.json","JO_E3.csv":"tables/JO_E3.csv",
               "JO_E3_PAIRED.csv":"tables/JO_E3_PAIRED.csv","JO_E3_SUMMARY.csv":"tables/JO_E3_SUMMARY.csv"}.get(n)
        if sub: out.append(W / "results_joint_ou/round_v1" / sub)
    if rel.startswith("tdrive/") and rel != "tdrive/TD_R_E3_PAIRED.csv":
        n = rel.split("/")[-1]
        for sub in ("03_target","06_eventtrace","04_selection"):
            cand = W / "tdrive_protocol_seal_r1" / sub / n
            if cand.is_file(): out.append(cand)
    return out

print("=== A. intended-source comparison ===")
nodiff = []
for rel in sorted(brec):
    if rel.startswith("w1/"): continue
    cands = intended(rel)
    if not cands:
        continue
    for c in cands:
        if not c.is_file():
            print(f"MISSING_SOURCE  {rel}  <- {c.relative_to(W).as_posix()}")
            continue
        wh = sha(c)
        ok = wh == brec[rel]
        if not ok:
            print(f"DIFFERENT  {rel}  vs  {c.relative_to(W).as_posix()}")
            print(f"    bundle={brec[rel]}")
            print(f"    worktree={wh}")
            nodiff.append((rel, c.relative_to(W).as_posix()))
print("intended-source differences:", len(nodiff))

print()
print("=== B. files whose matches do NOT include the intended source ===")
for rel in sorted(brec):
    cs = intended(rel)
    if not cs: continue
    m = set(matches.get(rel, []))
    if any(str(c) in m for c in cs): continue
    print(f"NO_INTENDED_MATCH {rel}")
    for x in matches.get(rel, [])[:6]:
        print("     alt:", Path(x).relative_to(W).as_posix())

print()
print("=== C. all 19 no-match files: alt/near candidates ===")
nomatch = [r for r in sorted(brec) if not matches.get(r)]
print(len(nomatch))
for r in nomatch:
    print(" ", r, brec[r][:16], (B/r).stat().st_size)

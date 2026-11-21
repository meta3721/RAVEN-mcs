import hashlib, json, os
from pathlib import Path
from collections import defaultdict
W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
matches = json.loads((W/"_r13_build/matches.json").read_text())
OUT = W/"_r13_build/COMPARISON_TABLE.txt"

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

# declared source map (same as compare_intended.py)
def intended(rel):
    out = []
    if rel.startswith("configs/protocol_closure/"): out.append(W/"configs/frozen/e3_multidataset_protocol_closure"/rel[len("configs/protocol_closure/"):])
    if rel.startswith("eventtraces/e1_formal/"): out.append(W/"data/frozen/e1_r2/formal"/rel[len("eventtraces/e1_formal/"):])
    if rel.startswith("eventtraces/e2/"): out.append(W/"artifacts/e2_traffic_formal_runs_r1/eventtraces"/rel[len("eventtraces/e2/"):])
    if rel.startswith("eventtraces/e3/"): out.append(W/"artifacts/e3_formal_runs_r1/eventtraces"/rel[len("eventtraces/e3/"):])
    if rel.startswith("processed/"): out.append(W/"data/processed"/rel[len("processed/"):])
    exact = {
     "configs/e2_formal_run_config.json":"artifacts/e2_traffic_formal_runs_r1/FORMAL_RUN_CONFIG.json",
     "configs/e2_profile_registry.json":"configs/frozen/e2_traffic_profiles_s1/traffic_s1_s6_profile_registry.json",
     "configs/e3_source_hashes.json":"configs/frozen/e3_target_pair_metric_final_r1/E3_FINAL_INTEGRATION_SOURCE_HASHES.json",
     "configs/e4_one_factor_spec.json":"artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json",
     "eventtraces/E2_EVENTTRACE_INDEX.csv":"paper_ready_r2/05_provenance/E2_EVENTTRACE_INDEX_120.csv",
     "eventtraces/E3_EVENTTRACE_MANIFEST.json":"artifacts/e3_formal_runs_r1/E3_FORMAL_EVENTTRACE_MANIFEST.json",
     "eventtraces/E2_EVENTTRACE_MANIFEST.csv":"artifacts/e2_traffic_formal_runs_r1/eventtrace_manifest.csv",
     "tables/PAPER_EVIDENCE_MASTER_LONG.csv":"paper_ready_r2/01_core_data/master/PAPER_EVIDENCE_MASTER_LONG.csv",
     "tables/E4_ABLATION_RELATIVE_CHANGE.csv":"paper_ready_r2/01_core_data/e4/E4_ABLATION_RELATIVE_CHANGE.csv",
     "tables/E3_FORMAL_HOLM_RESULTS.csv":"artifacts/e3_formal_runs_r1/E3_FORMAL_HOLM_RESULTS.csv",
     "tables/E4_ABLATION_HOLM_RESULTS.csv":"artifacts/e4_core_mechanism_ablation_r1/E4_ABLATION_HOLM_RESULTS.csv",
     "tables/CONFIG_REGISTRY.csv":"paper_ready_r2/05_provenance/FINAL_CONFIG_REGISTRY_R2.csv",
     "certificate/CERTIFICATE_STRESS.csv":"TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_CERTIFICATE_STRESS.csv",
     "certificate/CERTIFICATE_WINDOWS.csv":"TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_CERTIFICATE_WINDOWS.csv",
     "certificate/CERTIFICATE_TRACK_METRICS.csv":"results_sag_g1/round_r1m/eval/R1M_TRACK_METRICS.csv",
     "certificate/CERTIFICATE_BY_WINDOW.csv":"results_sag_g1/round_r1m/certificate/R1M_CERTIFICATE_BY_WINDOW.csv",
    }
    if rel in exact: out.append(W/exact[rel])
    if rel in {"tables/TABLE_II_MAIN_EFFECTIVENESS.csv","tables/TABLE_II_FREEZE.json","tables/TABLE_II_WORSTGROUP_PER_SEED.csv","tables/TABLE_E3_MAIN_EFFECTIVENESS.csv"}:
        out.append(W/"post_review/P0_ni_artifact/tables"/rel.split("/")[-1])
    if rel == "tdrive/TD_R_E3_PAIRED.csv": out.append(W/"post_review/P0_ni_artifact/tables/TD_R_E3_PAIRED.csv")
    for n in ("TABLE_E1_BALANCED_SANITY.csv","TABLE_E2_RISK_SEMANTICS.csv","TABLE_E3_FULL_METHODS_SUPPLEMENT.csv","TABLE_E4_CORE_ABLATION.csv","TABLE_E4_COMPONENT_EFFECTS.csv","TABLE_DATASET_SUMMARY.csv"):
        if rel == "tables/"+n: out.append(W/"paper_ready_r2/06_table_sources"/n)
    if rel.startswith("figures/"): out.append(W/"TO_OVERLEAF_paper_tmc_r1_clean/figure_data"/rel.split("/")[-1])
    if rel.startswith("cityscanner/"):
        sub={"CS_PHI_DECISION.json":"CS_PHI_DECISION.json","GO.json":"GO.json","AUDIT.json":"C1_KILL_AUDIT.json","CS_E3.csv":"tables/CS_E3.csv","CS_E3_PAIRED.csv":"tables/CS_E3_PAIRED.csv","CS_E3_SUMMARY.csv":"tables/CS_E3_SUMMARY.csv","CS_PHI.csv":"tables/CS_PHI.csv"}.get(rel.split("/")[-1])
        if sub: out.append(W/"results_c1_cityscanner/round_v1"/sub)
    if rel.startswith("cityscanner_p2/"):
        sub={"JO_PHI_DECISION.json":"JO_PHI_DECISION.json","GO.json":"GO.json","AUDIT.json":"JO_KILL_AUDIT.json","JO_E3.csv":"tables/JO_E3.csv","JO_E3_PAIRED.csv":"tables/JO_E3_PAIRED.csv","JO_E3_SUMMARY.csv":"tables/JO_E3_SUMMARY.csv"}.get(rel.split("/")[-1])
        if sub: out.append(W/"results_joint_ou/round_v1"/sub)
    if rel.startswith("tdrive/") and rel != "tdrive/TD_R_E3_PAIRED.csv":
        n = rel.split("/")[-1]
        for s in ("03_target","06_eventtrace","04_selection"):
            c = W/"tdrive_protocol_seal_r1"/s/n
            if c.is_file(): out.append(c)
    return out

def grp(rel):
    return rel.split("/")[0] if "/" in rel else "(top-level)"

rows = defaultdict(list)
for rel in sorted(matches):
    g = grp(rel)
    bs = sha(B/rel)
    m = matches[rel]
    ins = intended(rel)
    wt = ""
    ws = ""
    verdict = ""
    note = ""
    if ins:
        c = ins[0]
        wt = c.relative_to(W).as_posix()
        if c.is_file():
            ws = sha(c)
            verdict = "SAME" if ws == bs else "DIFFERENT"
            note = "declared source (build script)"
        else:
            verdict = "SOURCE-MISSING"
    if not m:
        verdict = verdict or "NO-TWIN"
        note = (note + "; no byte-identical file anywhere in worktree").strip("; ")
    elif not ins:
        wt = Path(m[0]).relative_to(W).as_posix()
        ws = bs
        verdict = "SAME"
        note = f"no declared source; {len(m)} identical twin(s) in worktree (shown: first)"
    elif verdict == "SAME":
        note = f"declared source; identical elsewhere too ({len(m)})" if len(m) > 1 else "declared source"
    rows[g].append((rel, bs[:16], wt, ws[:16] if ws else "", verdict, note))

with OUT.open("w", encoding="ascii", errors="replace") as f:
    hdr = f"{'bundle path':<58}{'bundle sha256(16)':<18}{'worktree path':<72}{'wt sha256(16)':<18}{'verdict':<14}note"
    for g in ["(top-level)","certificate","cityscanner","cityscanner_p2","configs","eventtraces","figures","new_target","processed","scripts","tables","tdrive","w1"]:
        f.write(f"\n### {g}  ({len(rows[g])} files)\n")
        f.write(hdr+"\n")
        f.write("-"*len(hdr)+"\n")
        for r in rows[g]:
            f.write(f"{r[0]:<58}{r[1]:<18}{r[2]:<72}{r[3]:<18}{r[4]:<14}{r[5]}\n")
print("wrote", OUT)
for g in rows:
    print(g, len(rows[g]), "DIFFERENT/NO-TWIN:", sum(1 for r in rows[g] if r[4] not in ("SAME",)))

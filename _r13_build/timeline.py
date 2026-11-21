import csv, os, hashlib, datetime
from pathlib import Path
W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\timeline.txt")
L=[]
def w(s=""): L.append(s)

FILES = [
 "RAVEN_MCS_PUBLIC_REPRO_R1/figures/FIG_E3_E3_PREDICTION_RISK.csv",
 "RAVEN_MCS_PUBLIC_REPRO_R1/figures/FIG_E4_E4_COMPONENT_ABLATION.csv",
 "RAVEN_MCS_PUBLIC_REPRO_R1/figures/FIG_W1_DESIGN_GATE.csv",
 "RAVEN_MCS_PUBLIC_REPRO_R1/MANIFEST.csv",
 "RAVEN_MCS_PUBLIC_REPRO_R1/BUNDLE_SUMMARY.json",
 "RAVEN_MCS_PUBLIC_REPRO_R1/README.md",
 "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E3_E3_PREDICTION_RISK.csv",
 "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv",
 "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_W1_DESIGN_GATE.csv",
 "TO_OVERLEAF_paper_tmc_r1_clean/main.tex",
 "TO_OVERLEAF_paper_tmc_r1_clean_extracted/figure_data/FIG_E3_E3_PREDICTION_RISK.csv",
 "TO_OVERLEAF_paper_tmc_r1_final/figure_data/FIG_E3_E3_PREDICTION_RISK.csv",
 "paper_tmc_r1/figure_data/FIG_E3_E3_PREDICTION_RISK.csv",
 "snapshots/2026-09-29-pre-theta-resource/figure_data/FIG_E3_E3_PREDICTION_RISK.csv",
 "snapshots/2026-09-29-pre-theta-resource/figure_data/FIG_W1_DESIGN_GATE.csv",
 "deliverables/TO_SUBMIT_TMC_HANDBOOK_S15_R1/08_Final_Paper_Facing_Tables_Figures/figure_data/FIG_E3_E3_PREDICTION_RISK.csv",
 "RAVEN_MCS_FINAL_FIGURE_TABLE_PAPER_SPECIFICATION_SEAL_R1/05_PROVENANCE/FINAL_FIGURE_SOURCES/FIG_E3_E3_PREDICTION_RISK.csv",
 "_paper_work/figure_data/FIG_E3_E3_PREDICTION_RISK.csv",
 "post_review/P0_ni_artifact/tables/TABLE_E3_MAIN_EFFECTIVENESS.csv",
 "paper_ready_r2/06_table_sources/TABLE_E3_MAIN_EFFECTIVENESS.csv",
 "paper_ready_r2/01_core_data/e4/E4_ABLATION_RELATIVE_CHANGE.csv",
]
w("mtimes (local):")
for f in FILES:
    p = W / f
    if p.exists():
        st = p.stat()
        w(f"  {datetime.datetime.fromtimestamp(st.st_mtime).isoformat(sep=' ')}  {st.st_size:>9}  {f}")
    else:
        w(f"  MISSING  {f}")

# full E3 differing keys
brel = "RAVEN_MCS_PUBLIC_REPRO_R1/figures/FIG_E3_E3_PREDICTION_RISK.csv"
wrel = "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E3_E3_PREDICTION_RISK.csv"
br = list(csv.DictReader(open(W/brel, encoding="utf-8-sig", newline="")))
wr = list(csv.DictReader(open(W/wrel, encoding="utf-8-sig", newline="")))
K = ["dataset","method","seed"]
bd = {tuple(r[k] for k in K): r for r in br}
wd = {tuple(r[k] for k in K): r for r in wr}
diffs = sorted(k for k in bd if bd[k] != wd[k])
w("")
w(f"E3 differing keys ({len(diffs)}):")
for k in diffs:
    w(f"  {k}  RMSE_mu {bd[k]['RMSE_mu']} -> {wd[k]['RMSE_mu']}   Tail_RMSE {bd[k]['Tail_RMSE']} -> {wd[k]['Tail_RMSE']}")
methods = sorted(set(k[1] for k in diffs)); seeds = sorted(set(k[2] for k in diffs)); dss = sorted(set(k[0] for k in diffs))
w(f"  datasets={dss} methods={methods} seeds={seeds}")
w("")
w("E3 rows per dataset in bundle: " + str({d: sum(1 for r in br if r['dataset']==d) for d in sorted(set(r['dataset'] for r in br))}))
w("E3 methods in bundle: " + str(sorted(set(r['method'] for r in br))))
w("E4 datasets/components: " + str(sorted(set((r['dataset'], r['component']) for r in list(csv.DictReader(open(W/'RAVEN_MCS_PUBLIC_REPRO_R1/figures/FIG_E4_E4_COMPONENT_ABLATION.csv', encoding='utf-8-sig', newline='')))))))
OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("wrote", OUT)
print("\n".join(L[:30]))

import csv, os, json
from pathlib import Path
W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\stale_scan.txt")
L=[]
def w(s=""): L.append(s)

# documented repairs
rows = list(csv.DictReader(open(W/"results_seed_path_audit_r1/C3_CELL_DIFF.csv", encoding="utf-8-sig")))
pairs = []
for r in rows:
    old, new = r["printed_old"].strip(), r["theta_new"].strip()
    if old and new and old != new:
        pairs.append((r["table"], r["row"], r["column"], old, new))

# bundle files to scan
targets = []
for dp, dn, fn in os.walk(B):
    for n in fn:
        p = Path(dp)/n
        if p.suffix.lower() in (".csv",".json",".md",".txt",".tex"):
            targets.append(p)
targets.sort()

def has_cell(text, val):
    """val appears delimited (not glued to other digits)."""
    import re
    pat = re.compile(r"(?<![\d.])" + re.escape(val) + r"(?![\d])")
    return bool(pat.search(text))

texts = {}
for p in targets:
    try:
        if p.stat().st_size > 80*1024*1024: continue
        texts[p] = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        pass

w(f"documented repair cells (old != new): {len(pairs)}")
w("")
w("BUNDLE FILES that contain a superseded (old) value and NOT the corrected (new) value:")
w("")
flagged = {}
for tbl, row, col, old, new in pairs:
    for p, t in texts.items():
        rel = p.relative_to(B).as_posix()
        if has_cell(t, old) and not has_cell(t, new):
            flagged.setdefault(rel, []).append(f"{tbl}|{row}|{col}: {old} -> {new}")
for rel in sorted(flagged):
    w(f"  {rel}")
    for x in flagged[rel][:8]:
        w(f"      {x}")
    if len(flagged[rel]) > 8:
        w(f"      ... {len(flagged[rel])-8} more")

w("")
w("="*90)
w("Per-artifact old/new presence matrix (key artifacts)")
w("="*90)
KEY = [
 "tables/TABLE_II_MAIN_EFFECTIVENESS.csv",
 "tables/TABLE_E3_MAIN_EFFECTIVENESS.csv",
 "tables/TABLE_E4_CORE_ABLATION.csv",
 "tables/TABLE_E4_COMPONENT_EFFECTS.csv",
 "tables/TABLE_E4_COMPONENT_EFFECTS.csv",
 "tables/PAPER_EVIDENCE_MASTER_LONG.csv",
 "figures/FIG_E3_E3_PREDICTION_RISK.csv",
 "figures/FIG_E4_E4_COMPONENT_ABLATION.csv",
 "figures/FIG_W1_DESIGN_GATE.csv",
 "w1/audit_v5/round_v5_1/ERRATA_FOR_PAPER.md",
 "w1/audit_v5/round_v5_1/A3P_RESOURCE_UPAIR.csv",
]
TESTS = [("1.1911","1.1954","Table III UA RAVEN-Design/Inst-Cal RMSE_mu"),
         ("1.1882","1.1923","appendix Local-Hajek RMSE_mu"),
         ("1.216","1.2202","Table III UA TwoStage RMSE_mu"),
         ("1.1914","1.1958","appendix RAVEN-SimOracle RMSE_mu"),
         ("-6.553094","-6.885464","Table IV UA Design RMSE_mu"),
         ("-6.875243","-7.221249","Table IV UA Design Tail_RMSE"),
         ("0.023974","0.025271","Table IV UA Use RMSE_mu"),
         ("0.130684","0.142931","Table IV UA Inst RMSE_mu")]
header = "artifact".ljust(46) + "".join(f"[{i}]" for i in range(len(TESTS)))
w(header)
for i,(o,n,d) in enumerate(TESTS):
    w(f"  [{i}] {d}: old={o} new={n}")
w("")
for rel in KEY:
    p = B/rel
    if not p.exists():
        w(f"  {rel}  <absent>"); continue
    t = p.read_text(encoding="utf-8", errors="ignore")
    marks = []
    for o,n,d in TESTS:
        a = "O" if has_cell(t,o) else "."
        b = "N" if has_cell(t,n) else "."
        marks.append(a+b)
    w(f"  {rel:<52}" + "".join(f"{m:<4}" for m in marks))
w("  (O=old present, N=new present within each cell)")
OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("wrote", OUT, len(L))
print("\n".join(L[:40]))

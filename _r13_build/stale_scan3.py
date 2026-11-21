import csv, os, re
from pathlib import Path
W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\stale_scan3.txt")
L=[]
def w(s=""): L.append(s)

rows = list(csv.DictReader(open(W/"results_seed_path_audit_r1/C3_CELL_DIFF.csv", encoding="utf-8-sig")))
pairs = []
for r in rows:
    old, new = r["printed_old"].strip(), r["theta_new"].strip()
    if not old or not new: continue
    o2, n2 = old.lstrip("+"), new.lstrip("+")
    try:
        if round(float(o2), 12) == round(float(n2), 12): continue
    except ValueError:
        continue
    pairs.append((r["table"], r["row"], r["column"], o2, n2))

def dec(s):
    return len(s.split(".")[1]) if "." in s else 0

def matches(v, s):
    try:
        t = float(s.lstrip("+"))
    except ValueError:
        return False
    d = dec(s.lstrip("+"))
    return round(v, d) == round(t, d)

def csv_nums(p):
    out = []
    try:
        with open(p, encoding="utf-8-sig", newline="") as f:
            for row in csv.reader(f):
                for c in row:
                    c = c.strip()
                    try: out.append(float(c))
                    except ValueError: pass
    except Exception:
        return None
    return out

w(f"repair cells (numerically distinct): {len(pairs)}")
for i,(t,r_,c,o,n) in enumerate(pairs):
    w(f"  [{i:>2}] {t} | {r_} | {c} | {o} -> {n}")
w("")

files = []
for dp, dn, fn in os.walk(B):
    for n in fn:
        if Path(n).suffix.lower() == ".csv":
            files.append(Path(dp)/n)
files.sort()
flag = {}
for p in files:
    rel = p.relative_to(B).as_posix()
    vals = csv_nums(p)
    if not vals: continue
    for i,(t,r_,c,o,n) in enumerate(pairs):
        a = any(matches(v,o) for v in vals)
        b = any(matches(v,n) for v in vals)
        if a and not b:
            flag.setdefault(rel, []).append(i)
w("BUNDLE CSV FILES holding superseded value(s) with corrected value absent:")
for rel in sorted(flag):
    w(f"  {rel}: cells {flag[rel]}  ({len(flag[rel])})")
w("")
w("="*100)
w("Presence matrix for the 17 repair cells (o=old only, n=new only, B=both, .=neither)")
w("="*100)
KEY = ["tables/TABLE_II_MAIN_EFFECTIVENESS.csv","tables/TABLE_II_FREEZE.json",
 "tables/TABLE_II_WORSTGROUP_PER_SEED.csv",
 "tables/TABLE_E3_MAIN_EFFECTIVENESS.csv","tables/TABLE_E3_FULL_METHODS_SUPPLEMENT.csv",
 "tables/TABLE_E4_CORE_ABLATION.csv","tables/TABLE_E4_COMPONENT_EFFECTS.csv",
 "tables/E4_ABLATION_RELATIVE_CHANGE.csv","tables/E4_ABLATION_HOLM_RESULTS.csv",
 "tables/PAPER_EVIDENCE_MASTER_LONG.csv","tables/SCD_PHI.csv",
 "figures/FIG_E3_E3_PREDICTION_RISK.csv","figures/FIG_E4_E4_COMPONENT_ABLATION.csv",
 "figures/FIG_W1_DESIGN_GATE.csv"]
w("  " + "artifact".ljust(46) + "".join(f"{i:<3}" for i in range(len(pairs))))
for rel in KEY:
    p = B/rel
    if not p.exists(): w(f"  {rel} <absent>"); continue
    if p.suffix.lower() != ".csv":
        w(f"  {rel} <not csv>"); continue
    vals = csv_nums(p) or []
    marks = []
    for (t,r_,c,o,n) in pairs:
        a = any(matches(v,o) for v in vals); b = any(matches(v,n) for v in vals)
        marks.append("B" if (a and b) else ("o" if a else ("n" if b else ".")))
    w("  " + rel.ljust(46) + "".join(f"{m:<3}" for m in marks))
OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("\n".join(L))

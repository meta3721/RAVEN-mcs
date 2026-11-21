import csv, os, re, json
from pathlib import Path
W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\stale_scan2.txt")
L=[]
def w(s=""): L.append(s)

rows = list(csv.DictReader(open(W/"results_seed_path_audit_r1/C3_CELL_DIFF.csv", encoding="utf-8-sig")))
pairs = []
for r in rows:
    old, new = r["printed_old"].strip(), r["theta_new"].strip()
    if not old or not new: continue
    try:
        if abs(float(old) - float(new)) < 1e-12: continue   # formatting-only
    except ValueError:
        pass
    pairs.append((r["table"], r["row"], r["column"], old, new))
w(f"meaningful documented repair cells (old != new numerically): {len(pairs)}")
for p in pairs:
    w(f"   {p}")
w("")

def cells_of(p):
    out = []
    try:
        with open(p, encoding="utf-8-sig", newline="") as f:
            for row in csv.reader(f):
                for c in row:
                    out.append(c)
    except Exception:
        return None
    return out

def nums(cells):
    s = set()
    for c in cells:
        c = c.strip()
        try:
            s.add(float(c))
        except ValueError:
            pass
    return s

def approx_in(vals, target):
    try:
        t = float(target)
    except ValueError:
        return False
    for v in vals:
        if v == t: return True
        if abs(v) > 1e-12 and abs(v - t)/abs(v) < 1e-6: return True
        if abs(v) < 1e-12 and abs(v - t) < 1e-12: return True
    return False

def text_hit(t, val):
    return re.search(r"(?<![\d.])" + re.escape(val), t) is not None

files = []
for dp, dn, fn in os.walk(B):
    for n in fn:
        p = Path(dp)/n
        if p.suffix.lower() in (".csv",".json",".md",".txt"):
            files.append(p)
files.sort()

flagged = {}
for p in files:
    rel = p.relative_to(B).as_posix()
    if p.suffix.lower() == ".csv":
        c = cells_of(p)
        if c is None: continue
        vals = nums(c)
        for tbl,row,col,old,new in pairs:
            if approx_in(vals, old) and not approx_in(vals, new):
                flagged.setdefault(rel, []).append(f"{tbl} | {row} | {col}: {old} -> {new}")
    else:
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for tbl,row,col,old,new in pairs:
            if text_hit(t, old) and not text_hit(t, new):
                flagged.setdefault(rel, []).append(f"{tbl} | {row} | {col}: {old} -> {new}")

w("BUNDLE FILES holding a superseded value with the corrected value absent:")
tot = 0
for rel in sorted(flagged):
    tot += len(flagged[rel])
    w(f"  {rel}   ({len(flagged[rel])} cells)")
    for x in flagged[rel][:12]:
        w(f"      {x}")
    if len(flagged[rel]) > 12:
        w(f"      ... {len(flagged[rel])-12} more")
w(f"total flagged cell-instances: {tot}")

w("")
w("="*95)
w("Presence matrix, key artifacts (O=old only, N=new only, B=both, .=neither)")
w("="*95)
KEY = ["tables/TABLE_II_MAIN_EFFECTIVENESS.csv","tables/TABLE_II_FREEZE.json",
 "tables/TABLE_E3_MAIN_EFFECTIVENESS.csv","tables/TABLE_E3_FULL_METHODS_SUPPLEMENT.csv",
 "tables/TABLE_E4_CORE_ABLATION.csv","tables/TABLE_E4_COMPONENT_EFFECTS.csv",
 "tables/E4_ABLATION_RELATIVE_CHANGE.csv","tables/E4_ABLATION_HOLM_RESULTS.csv",
 "tables/PAPER_EVIDENCE_MASTER_LONG.csv","tables/TABLE_II_WORSTGROUP_PER_SEED.csv",
 "figures/FIG_E3_E3_PREDICTION_RISK.csv","figures/FIG_E4_E4_COMPONENT_ABLATION.csv",
 "figures/FIG_W1_DESIGN_GATE.csv",
 "w1/audit_v5/round_v5_1/ERRATA_FOR_PAPER.md","w1/audit_v5/round_v5_1/A3P_RESOURCE_UPAIR.csv"]
for i,(tbl,row,col,o,n) in enumerate(pairs):
    w(f"  [{i:>2}] {tbl} | {row} | {col} | {o} -> {n}")
w("")
hdr = "  " + "artifact".ljust(48) + "".join(f"{i:<3}" for i in range(len(pairs)))
w(hdr)
def status(vals, t, old, new):
    a = approx_in(vals,t and None or set()) if False else approx_in(vals, old)
    b = approx_in(vals, new)
    return "B" if (a and b) else ("O" if a else ("N" if b else "."))
for rel in KEY:
    p = B/rel
    if not p.exists():
        w(f"  {rel}  <absent>"); continue
    if p.suffix.lower() == ".csv":
        vals = nums(cells_of(p) or [])
        marks = [status(vals,None,o,n) for (_,_,_,o,n) in pairs]
    else:
        t = p.read_text(encoding="utf-8", errors="ignore")
        marks = []
        for (_,_,_,o,n) in pairs:
            a, b = text_hit(t,o), text_hit(t,n)
            marks.append("B" if (a and b) else ("O" if a else ("N" if b else ".")))
    w("  " + rel.ljust(48) + "".join(f"{m:<3}" for m in marks))
OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("wrote", OUT, len(L))

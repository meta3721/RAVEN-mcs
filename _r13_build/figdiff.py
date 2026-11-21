import csv, hashlib, io, json, math
from pathlib import Path

W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\figdiff.txt")
L = []
def w(s=""):
    L.append(s)

def sha(p):
    h = hashlib.sha256(); h.update(Path(p).read_bytes()); return h.hexdigest()

PAIRS = [
 ("figures/FIG_W1_DESIGN_GATE.csv", "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_W1_DESIGN_GATE.csv"),
 ("figures/FIG_E4_E4_COMPONENT_ABLATION.csv", "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv"),
 ("figures/FIG_E3_E3_PREDICTION_RISK.csv", "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E3_E3_PREDICTION_RISK.csv"),
]

def load(p):
    with open(p, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f)), None

for brel, wrel in PAIRS:
    bp, wp = B / brel, W / wrel
    w("="*100)
    w(f"PAIR {brel}")
    w(f"  bundle   {bp.stat().st_size:>8} B  {sha(bp)}")
    w(f"  worktree {wrel}  {wp.stat().st_size:>8} B  {sha(wp)}")
    br = list(csv.reader(open(bp, encoding="utf-8-sig", newline="")))
    wr = list(csv.reader(open(wp, encoding="utf-8-sig", newline="")))
    w(f"  bundle header: {br[0]}")
    w(f"  worktree header: {wr[0]}")
    w(f"  bundle data rows: {len(br)-1}   worktree data rows: {len(wr)-1}")
    if br[0] != wr[0]:
        w("  HEADER DIFFERS")
    hdr = br[0]
    # align by full row key (first N key columns)
    nk = 2 if len(hdr) > 2 else 1
    bd = {}
    for r in br[1:]:
        bd[tuple(r[:nk])] = r
    wd = {}
    for r in wr[1:]:
        wd[tuple(r[:nk])] = r
    w(f"  key columns: {hdr[:nk]}")
    w(f"  keys only in bundle: {sorted(set(bd)-set(wd))}")
    w(f"  keys only in worktree: {sorted(set(wd)-set(bd))}")
    common = sorted(set(bd) & set(wd))
    diffrows = [k for k in common if bd[k] != wd[k]]
    w(f"  common keys: {len(common)}   differing rows: {len(diffrows)}")
    colstats = {}
    for k in diffrows:
        b, ww = bd[k], wd[k]
        for i, c in enumerate(hdr):
            if i < len(b) and i < len(ww) and b[i] != ww[i]:
                colstats.setdefault(c, []).append((k, b[i], ww[i]))
    for c, lst in colstats.items():
        w(f"    column '{c}': {len(lst)} differing cells")
        mx = 0.0; mxr = None; mn = None
        anynum = True
        for k, bv, wv in lst:
            try:
                d = abs(float(bv) - float(wv))
            except ValueError:
                anynum = False; continue
            if d > mx: mx, mxr = d, (k, bv, wv)
            if mn is None or d < mn: mn = d
        if anynum:
            w(f"      min abs diff = {mn!r}   max abs diff = {mx!r}  at key {mxr}")
        w(f"      sample (first 6):")
        for k, bv, wv in lst[:6]:
            w(f"        key={k}  bundle={bv!r}  worktree={wv!r}")
    # full-row text comparison for small files
    if len(br) <= 12:
        w("  --- bundle rows ---")
        for r in br: w("   " + " | ".join(r))
        w("  --- worktree rows ---")
        for r in wr: w("   " + " | ".join(r))

OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("wrote", OUT, len(L), "lines")

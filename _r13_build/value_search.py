import csv, os, re, json
from pathlib import Path

W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\value_search.txt")
L=[]
def w(s=""): L.append(s)

# differing values, bundle vs clean-worktree
CASES = [
 ("FIG_W1_DESIGN_GATE RMSE_mu_pct U-Air Estimated", "7.072313349518344", "7.456497890808388"),
 ("FIG_W1_DESIGN_GATE RMSE_mu_pct U-Air Oracle",    "7.1079118838817745", "7.504511077483693"),
 ("FIG_E4 Design RMSE_mu relative_change_percent",  "-6.553093815666225", "-6.885463676716227"),
 ("FIG_E4 Design Tail_RMSE relative_change_percent","-6.875242584162889", "-7.221248907329521"),
 ("FIG_E4 Inst RMSE_mu relative_change_percent",    "0.1306837550913353", "0.14293076988935038"),
 ("FIG_E4 Obs RMSE_mu relative_change_percent",     "-0.0097196306106393", "-0.009782968291166629"),
 ("FIG_E3 U-Air Debt-Cal 30007 RMSE_mu",            "1.1443603420506454", "1.0965638173228216"),
 ("FIG_E3 U-Air Debt-Cal 30016 RMSE_mu",            "1.1644618391293844", "1.0565769811442463"),
 ("FIG_E3 U-Air TimeAlign-Agg 30016 RMSE_mu",       "1.1675261739713565", "1.050898929877568"),
]

def variants(s):
    f = float(s)
    out = set()
    out.add(s)
    for d in (1,2,3,4):
        out.add(f"{f:.{d}f}")
        out.add(f"{f:.{d}f}".lstrip("-") if f<0 else f"{f:.{d}f}")
    # also abs value rounded
    for d in (2,3,4):
        out.add(f"{abs(f):.{d}f}")
    return {x for x in out if len(x) >= 3}

def scan(root, exts, needles):
    hits = {}
    for dp, dn, fn in os.walk(root):
        for n in fn:
            if not any(n.lower().endswith(e) for e in exts): continue
            p = Path(dp)/n
            if p.stat().st_size > 40*1024*1024: continue
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except OSError: continue
            for nd in needles:
                if nd in txt:
                    idx = txt.find(nd)
                    line = txt.count("\n", 0, idx)+1
                    hits.setdefault(nd, []).append((str(p.relative_to(root)), line))
    return hits

for label, bval, wval in CASES:
    w("="*90)
    w(f"{label}")
    w(f"  bundle   value: {bval}")
    w(f"  worktree value: {wval}")
    for which, val in (("BUNDLE-VALUE", bval), ("WORKTREE-VALUE", wval)):
        w(f"  --- searching {which} ({val}) variants ---")
        for nd in sorted(variants(val)):
            hb = scan(B, (".csv",".json",".md",".txt",".py",".tex"), [nd]).get(nd, [])
            hw = scan(W / "TO_OVERLEAF_paper_tmc_r1_clean", (".tex",), [nd]).get(nd, [])
            if hb or hw:
                w(f"    token {nd!r}")
                for f, ln in hb[:6]: w(f"        BUNDLE   {f}:{ln}")
                for f, ln in hw[:6]: w(f"        MANUSCRIPT {f}:{ln}")

OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("wrote", OUT, len(L), "lines")

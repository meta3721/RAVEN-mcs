import os
from pathlib import Path
W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\exact_search.txt")
L=[]
def w(s=""): L.append(s)

CASES = [
 ("FIG_W1 RMSE_mu_pct U-Air Estimated", "7.072313349518344", "7.456497890808388"),
 ("FIG_W1 RMSE_mu_pct U-Air Oracle",    "7.1079118838817745", "7.504511077483693"),
 ("FIG_E4 U-Air Design RMSE_mu rel%",   "-6.553093815666225", "-6.885463676716227"),
 ("FIG_E4 U-Air Design Tail_RMSE rel%", "-6.875242584162889", "-7.221248907329521"),
 ("FIG_E4 U-Air Inst RMSE_mu rel%",     "0.1306837550913353", "0.14293076988935038"),
 ("FIG_E4 U-Air Obs RMSE_mu rel%",      "-0.0097196306106393", "-0.009782968291166629"),
 ("FIG_E4 U-Air Obs Tail_RMSE rel%",    "-0.0102288937108689", "-0.010295794089172574"),
 ("FIG_E4 U-Air Use RMSE_mu rel%",      "0.023973670577847", "0.02527079699465602"),
 ("FIG_E4 U-Air Debt RMSE_mu rel%",     "0.0007291917853553", "0.0006719663837970082"),
 ("FIG_E3 U-Air Debt-Cal 30007 RMSE_mu","1.1443603420506454", "1.0965638173228216"),
 ("FIG_E3 U-Air Debt-Cal 30016 RMSE_mu","1.1644618391293844", "1.0565769811442463"),
 ("FIG_E3 U-Air Debt-Cal 30018 RMSE_mu","1.1242410101389166", "1.1018097912391154"),
 ("FIG_E3 U-Air FedAvg-Window 30016 RMSE_mu","1.1675261739713565", "1.0512611630180884"),
 ("FIG_E3 U-Air TimeAlign-Agg 30016 RMSE_mu","1.1675261739713565", "1.050898929877568"),
]

def find_exact(root, exts, needle, cap=12):
    hits = []
    for dp, dn, fn in os.walk(root):
        for n in fn:
            if not any(n.lower().endswith(e) for e in exts): continue
            p = Path(dp)/n
            try:
                if p.stat().st_size > 60*1024*1024: continue
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except OSError: continue
            if needle in txt:
                idx = txt.find(needle)
                hits.append((str(p.relative_to(root)).replace("\\","/"), txt.count("\n",0,idx)+1, txt.count(needle)))
                if len(hits) >= cap: return hits
    return hits

for label, bval, wval in CASES:
    w("="*95)
    w(f"{label}   bundle={bval}   worktree/paper-dir={wval}")
    for tag, val in (("BUNDLE-VALUE", bval), ("PAPER-DIR-VALUE", wval)):
        hb = find_exact(B, (".csv",".json",".md",".txt",".py"), val)
        hm = find_exact(W/"TO_OVERLEAF_paper_tmc_r1_clean", (".tex",), val)
        w(f"  [{tag}] {val}")
        w(f"    in bundle files: {len(hb)}")
        for f, ln, c in hb[:8]: w(f"        {f}:{ln}  (x{c})")
        w(f"    in manuscript .tex (TO_OVERLEAF_paper_tmc_r1_clean): {len(hm)}")
        for f, ln, c in hm[:8]: w(f"        {f}:{ln}  (x{c})")
OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("wrote", OUT, len(L))

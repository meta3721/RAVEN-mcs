import os
from pathlib import Path
W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\exact_stale.txt")
L=[]
def w(s=""): L.append(s)

# full-precision (old -> new) pairs for the theta repair, taken from the bundle/worktree files themselves
PAIRS = [
 ("E4 UA Design RMSE_mu rel%",  "-6.553093815666225",  "-6.885463676716227"),
 ("E4 UA Design Tail rel%",     "-6.875242584162889",  "-7.221248907329521"),
 ("E4 UA Obs RMSE_mu rel%",     "-0.0097196306106393", "-0.009782968291166629"),
 ("E4 UA Obs Tail rel%",        "-0.0102288937108689", "-0.010295794089172574"),
 ("E4 UA Use RMSE_mu rel%",     "0.02397367057784707", "0.02527079699465602"),
 ("E4 UA Use Tail rel%",        "0.0252184289979606",  "0.026449615882742403"),
 ("E4 UA Inst RMSE_mu rel%",    "0.1306837550913353",  "0.14293076988935038"),
 ("E4 UA Inst Tail rel%",       "0.1363753990751629",  "0.14902918597946535"),
 ("E4 UA Debt RMSE_mu rel%",    "0.0007291917853553351","0.0006719663837970082"),
 ("E4 UA Debt Tail rel%",       "0.000775232954355",   "0.000715240505846325"),
 ("E4 parent UA RMSE_mu",       "1.191113924600986",   "1.195365574077496"),
 ("E3 UA RAVEN-SimOracle mean", "1.191447",            "1.195830"),
 ("E3 UA TwoStage-Hajek mean",  "1.215961",            "1.220198"),
]

files = []
for dp, dn, fn in os.walk(B):
    for n in fn:
        p = Path(dp)/n
        if p.suffix.lower() in (".csv",".json",".md",".txt",".py"):
            files.append(p)
files.sort()
texts = {}
for p in files:
    try:
        if p.stat().st_size > 80*1024*1024: continue
        texts[p] = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        pass
w(f"scanned {len(texts)} bundle text files")
w("")
res = {}
for label, old, new in PAIRS:
    fo = [p.relative_to(B).as_posix() for p,t in texts.items() if old in t]
    fn_ = [p.relative_to(B).as_posix() for p,t in texts.items() if new in t]
    w(f"### {label}")
    w(f"    OLD {old}")
    for x in sorted(fo): w(f"        old-in  {x}")
    w(f"    NEW {new}")
    for x in sorted(fn_): w(f"        new-in  {x}")
    for x in fo:
        if x not in fn_:
            res.setdefault(x, []).append(label)
    w("")
w("="*90)
w("BUNDLE FILES that hold the superseded value and NOT the corrected value (exact full precision):")
for x in sorted(res):
    w(f"  {x}   ({len(res[x])}: {', '.join(res[x])})")
OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("\n".join(L[-40:]))

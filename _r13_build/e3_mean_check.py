import csv, statistics
from pathlib import Path
W = Path(r"C:\Cursor\raven.mcs")
B = W / "RAVEN_MCS_PUBLIC_REPRO_R1"
OUT = Path(r"C:\Cursor\raven.mcs\_r13_build\e3_mean_check.txt")
L=[]
def w(s=""): L.append(s)

def load(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig", newline="")))

def means(rows, ds):
    d = {}
    for r in rows:
        if r["dataset"] != ds: continue
        d.setdefault(r["method"], []).append(float(r["RMSE_mu"]))
    return {k: (statistics.fmean(v), len(v)) for k, v in d.items()}

bfig = load(B/"figures/FIG_E3_E3_PREDICTION_RISK.csv")
wfig = load(W/"TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E3_E3_PREDICTION_RISK.csv")
t3   = load(B/"tables/TABLE_E3_MAIN_EFFECTIVENESS.csv")
t2   = load(B/"tables/TABLE_II_MAIN_EFFECTIVENESS.csv")

w("U-Air 20-seed mean RMSE_mu: bundle FIG_E3 vs worktree FIG_E3 vs bundle TABLE_E3 vs bundle TABLE_II")
w("")
w(f"{'method':<22}{'bundleFIG':>14}{'wtFIG':>14}{'TABLE_E3':>12}{'TABLE_II':>12}  verdict")
bm, wm = means(bfig, "U-Air"), means(wfig, "U-Air")
t3m = {r["method"]: r["RMSE_mu_mean"] for r in t3 if r["dataset"] == "U-Air"}
t2m = {r["method"]: r["RMSE_mu_mean"] for r in t2 if r["dataset"] == "U-Air"}
for meth in sorted(bm):
    b, n1 = bm[meth]; x, n2 = wm.get(meth, (float('nan'), 0))
    e3 = t3m.get(meth, ""); e2 = t2m.get(meth, "")
    verdicts = []
    if e3:
        fe = float(e3)
        vb = "MATCH" if abs(b-fe) < 5e-6 else ("close" if abs(b-fe) < 5e-4 else "NO")
        vx = "MATCH" if abs(x-fe) < 5e-6 else ("close" if abs(x-fe) < 5e-4 else "NO")
        verdicts.append(f"E3: bundleFIG={vb} wtFIG={vx}")
    w(f"{meth:<22}{b:>14.6f}{x:>14.6f}{str(e3):>12}{str(e2):>12}  {'; '.join(verdicts)}")

w("")
w("Also for comparison, printed Table II values in the manuscript (rounded to 5dp):")
w("  U-Air FedAvg-Window 1.18824, FedAU-Window 1.11281, ObsUse-Window 1.11203,")
w("  RAVEN-MCS-SCD 1.11306, TwoStage-Hajek 1.21596, RAVEN-MCS-Full-Design 1.19111")
w("---")
w("SensorScope means identical between the two FIG_E3 versions? " +
  str(means(bfig,"SensorScope") == means(wfig,"SensorScope")))
w("")
w("Difference in U-Air per-method means (bundleFIG - wtFIG):")
for meth in sorted(bm):
    b = bm[meth][0]; x = wm.get(meth, (float('nan'),))[0]
    w(f"  {meth:<22}{b-x:+.6f}")
OUT.write_text("\n".join(L), encoding="ascii", errors="replace")
print("\n".join(L))

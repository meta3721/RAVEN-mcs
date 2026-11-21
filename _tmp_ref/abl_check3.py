import csv, pathlib, statistics as st
rows = list(csv.DictReader(open("RAVEN_MCS_PUBLIC_REPRO_R1/tables/E4_ABLATION_RELATIVE_CHANGE.csv", newline="", encoding="utf-8")))
pub = {  # published tabe4e4e4lablation values, U-Air / SensorScope
 ("U-Air","Design"):(-6.943,4.990,-6.553), ("U-Air","Obs"):(0.123,0.022,-0.010),
 ("U-Air","Use"):(0.014,-0.014,0.024),      ("U-Air","Inst"):(-0.089,-0.143,0.131),
 ("U-Air","Debt"):(0.004,0.002,0.000),
 ("SensorScope","Design"):(1.237,0.597,0.005), ("SensorScope","Obs"):(0.096,-0.070,0.012),
 ("SensorScope","Use"):(0.026,0.026,0.012),    ("SensorScope","Inst"):(-0.260,0.310,-0.002),
 ("SensorScope","Debt"):(0.014,0.004,0.000),
}
print("component-wise mean relative_change_percent from the bundle CSV, vs the published table")
print(f"{'dataset':<12} {'comp':<7} {'metric':<12} {'CSV mean':>10} {'table':>9} {'agree?':>7}")
for ds in ("SensorScope","U-Air"):
    for comp in ("Design","Obs","Use","Inst","Debt"):
        for i, met in enumerate(("Delta_group","Delta_c_s","RMSE_mu")):
            v = [float(r["relative_change_percent"]) for r in rows
                 if r["dataset"]==ds and r["component"]==comp and r["metric"]==met]
            if not v: continue
            m = st.mean(v); t = pub[(ds,comp)][i]
            ok = "OK" if abs(m-t) < 0.01 else "*** DIFF ***"
            print(f"{ds:<12} {comp:<7} {met:<12} {m:>10.3f} {t:>9.3f} {ok:>7}")
    print()


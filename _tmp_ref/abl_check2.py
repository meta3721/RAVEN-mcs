import csv, pathlib, statistics as st
rows = list(csv.DictReader(open("RAVEN_MCS_PUBLIC_REPRO_R1/tables/E4_ABLATION_RELATIVE_CHANGE.csv", newline="", encoding="utf-8")))
pub = {  # published tabe4e4e4lablation values, U-Air / SensorScope
 ("uair","Design"):(-6.943,4.990,-6.553), ("uair","Obs"):(0.123,0.022,-0.010),
 ("uair","Use"):(0.014,-0.014,0.024),      ("uair","Inst"):(-0.089,-0.143,0.131),
 ("uair","Debt"):(0.004,0.002,0.000),
 ("sensorscope","Design"):(1.237,0.597,0.005), ("sensorscope","Obs"):(0.096,-0.070,0.012),
 ("sensorscope","Use"):(0.026,0.026,0.012),    ("sensorscope","Inst"):(-0.260,0.310,-0.002),
 ("sensorscope","Debt"):(0.014,0.004,0.000),
}
print("component-wise mean relative_change_percent from the bundle CSV, vs the published table")
print(f"{'dataset':<12} {'comp':<7} {'metric':<12} {'CSV mean':>10} {'table':>9} {'agree?':>7}")
for ds in ("sensorscope","uair"):
    for comp in ("Design","Obs","Use","Inst","Debt"):
        for i, met in enumerate(("Delta_group","Delta_c_s","RMSE_mu")):
            v = [float(r["relative_change_percent"]) for r in rows
                 if r["dataset"]==ds and r["component"]==comp and r["metric"]==met]
            if not v: continue
            m = st.mean(v); t = pub[(ds,comp)][i]
            ok = "OK" if abs(m-t) < 0.01 else "*** DIFF ***"
            print(f"{ds:<12} {comp:<7} {met:<12} {m:>10.3f} {t:>9.3f} {ok:>7}")
    print()

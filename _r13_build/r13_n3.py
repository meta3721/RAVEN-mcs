import json,pathlib,numpy as np
F=pathlib.Path(r"C:\Cursor\raven.mcs\artifacts\e3_formal_runs_r1\runs")
R=pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\runs")
S=[30001,30002,30003,30004,30005]
for b,arm in (("sensorscope","central_delivered"),("uair","central_delivered"),("traffic","central_delivered")):
    for n in (3,5):
        v=[json.loads((F/b/arm/("seed%d"%s)/"final_metrics.json").read_text())["RMSE_mu"] for s in S[:n]]
        print("%-11s %-18s n=%d mean=%.10f" % (b,arm,n,float(np.mean(v))))
# recompute ratio_to_c as the driver does (5 seeds)
for b,tag in (("sensorscope","A_eta0.01"),("uair","A_eta0.003"),("traffic","A_eta0.003")):
    new=[json.loads((R/tag/b/"fedavg_window"/("seed%d"%s)/"final_metrics.json").read_text())["RMSE_mu"] for s in S]
    c=[json.loads((F/b/"central_delivered"/("seed%d"%s)/"final_metrics.json").read_text())["RMSE_mu"] for s in S]
    print("%-11s new_mean=%.10f c_mean=%.10f ratio=%.10f  1.01c=%.10f PASS=%s" % (
        b,float(np.mean(new)),float(np.mean(c)),float(np.mean(new))/float(np.mean(c)),1.01*float(np.mean(c)),float(np.mean(new))<=1.01*float(np.mean(c))))

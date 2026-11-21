"""Confirm the published Table II RMSE_mu/Delta_group come from the E3 run
final_metrics.json (20-seed means), which fixes the metric definition lineage."""
import json
import statistics as st
from pathlib import Path

R = Path('artifacts/e3_formal_runs_r1/runs')
want = {
    ('sensorscope', 'raven'): ('RAVEN-Design', 7.9380, 0.0473, 1.0139),
    ('sensorscope', 'fedavg_window'): ('FedAvg-Window', 7.9389, 0.0459, 1.0558),
    ('uair', 'raven'): ('RAVEN-NoDesign', 1.1131, 0.0638, 1.0165),
    ('uair', 'fedavg_window'): ('FedAvg-Window', 1.1882, 0.0649, 1.1218),
}
for (ds, m), (label, pub_rmse, pub_sd, pub_dg) in want.items():
    vals_rmse, vals_dg = [], []
    for i in range(1, 21):
        p = R / ds / m / ('seed30%03d' % i) / 'final_metrics.json'
        if not p.is_file():
            continue
        j = json.loads(p.read_text(encoding='utf-8'))
        if j.get('RMSE_mu') is not None:
            vals_rmse.append(float(j['RMSE_mu']))
        if j.get('Delta_group') is not None:
            vals_dg.append(float(j['Delta_group']))
    print('%-12s %-16s n=%2d' % (ds, label, len(vals_rmse)))
    if vals_rmse:
        print('    RMSE_mu    computed mean+-sd = %.4f +- %.4f   |  Table II = %.4f +- %.4f  %s'
              % (st.mean(vals_rmse), st.stdev(vals_rmse), pub_rmse, pub_sd,
                 'MATCH' if abs(st.mean(vals_rmse) - pub_rmse) < 5e-4 else 'DIFF'))
    if vals_dg:
        print('    Delta_group computed mean    = %.4f                 |  Table II = %.4f        %s'
              % (st.mean(vals_dg), pub_dg,
                 'MATCH' if abs(st.mean(vals_dg) - pub_dg) < 5e-4 else 'DIFF'))

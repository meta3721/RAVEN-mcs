import json, pathlib, numpy as np
ROOT = pathlib.Path(".")
def means(tree, ds, m):
    d = ROOT/tree/ds/m
    out = {}
    for k in ("RMSE_mu", "Delta_group", "Delta_c_s"):
        v = [json.loads((d/f"seed{s}"/"final_metrics.json").read_text(encoding="utf-8")).get(k) for s in range(30001,30021)]
        v = [x for x in v if isinstance(x,(int,float))]
        out[k] = sum(v)/len(v) if v else None
    return out
print("=== U-Air: RAVEN one-factor ablation family (20-seed means, own trees) ===")
print(f"{'method':<24} {'tree':<5} {'RMSE_mu':>9} {'d_group':>9} {'d_c_s':>9}  gated-on components")
rows = [("raven","e3"),("raven_wo_design","e4"),("raven_wo_inst","e4"),("raven_wo_debt","e4"),
        ("raven_wo_obs","e4"),("raven_wo_use","e4"),("inst_cal","e3"),("debt_cal","e3"),
        ("twostage_hajek","e3"),("fedavg_window","e3"),("raven_wo_design","e4")]
seen=set()
for m, t in rows:
    if (m,t) in seen: continue
    seen.add((m,t))
    tree = {"e3":"artifacts/e3_formal_runs_r1/runs","e4":"artifacts/e4_core_mechanism_ablation_r1/runs"}[t]
    r = means(tree, "uair", m)
    print(f"{m:<24} {t:<5} {r['RMSE_mu']:>9.6f} {r['Delta_group']:>9.6f} {r['Delta_c_s']:>9.6f}")
print()
print("=== E4 arm policies: which components are OFF relative to _RAVEN_CORE ===")
import sys; sys.path.insert(0, str(ROOT/"src"))
from raven_mcs.aggregation.method_policy import POLICY_MAP
core = POLICY_MAP["raven"]
for m in ("raven","raven_wo_design","raven_wo_inst","raven_wo_debt","raven_wo_obs","raven_wo_use","inst_cal","debt_cal"):
    p = POLICY_MAP[m]
    off = [f for f in ("uses_design_ratio","uses_observation_ipw","uses_usable_ipw","uses_hajek_local_loss",
                       "uses_instant_calibration","uses_debt","uses_reference_penalty","uses_variance_penalty",
                       "uses_staleness_penalty") if getattr(core,f) and not getattr(p,f)]
    add = [f for f in ("uses_design_ratio","uses_observation_ipw","uses_usable_ipw","uses_hajek_local_loss",
                       "uses_instant_calibration","uses_debt","uses_reference_penalty","uses_variance_penalty",
                       "uses_staleness_penalty") if getattr(p,f) and not getattr(core,f)]
    print(f"  {m:<20} OFF={off if off else '-'}  ON-extra={add if add else '-'}")

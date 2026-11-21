import sys, pathlib, json
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
import run_h_headroom as h
h.OUT = pathlib.Path("results_active_set_repair/round_v1").resolve()
try:
    r = h.run_arm("C0_frozen", "uair", "raven_wo_inst", 30001, tag="c4probe")
    print("raven_wo_inst rerun RMSE_mu =", r["RMSE_mu"])
    fz = json.loads(pathlib.Path("artifacts/e4_core_mechanism_ablation_r1/runs/uair/raven_wo_inst/seed30001/final_metrics.json").read_text())
    print("frozen E4 raven_wo_inst    =", fz["RMSE_mu"], "| abs_diff =", abs(r["RMSE_mu"]-fz["RMSE_mu"]))
except Exception as e:
    print("RAISED:", type(e).__name__, str(e)[:200])

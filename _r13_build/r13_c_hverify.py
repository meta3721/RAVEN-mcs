"""R1.3 adversarial audit - objection (c): reproduce H, bootstrap, MDE80 exactly;
plus objection (b): how sensitive is eta_s* to the validation-weighting recipe.

ASCII only. Writes only under _r13_build.
"""
import json, csv, math, pathlib
import numpy as np
from scipy import stats

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_server_optimizer" / "round_v1"
BUILD = ROOT / "_r13_build"
SEEDS = [30001, 30002, 30003, 30004, 30005]
BOOT_DRAWS, BOOT_SEED = 10000, 20261007
H_BAR, LCB_BAR = 0.01, 0.005

cfg = json.loads((OUT / "S1P_FROZEN_CONFIG.json").read_text())
hjson = json.loads((OUT / "S1P_STAGE_C_H.json").read_text())
av = json.loads((OUT / "S1P_STAGE_A_VERDICT.json").read_text())
grid = list(csv.DictReader((OUT / "tables" / "STAGE_A_GRID.csv").open(encoding="utf-8")))

a = json.loads((BUILD / "r13_a_constants.json").read_text())

print("### C1  reproduce H / bootstrap / MDE80 from S1P_STAGE_C_H.json inputs")
for block, rec in hjson["H"].items():
    if "H_by_seed" not in rec:
        continue
    fed = np.array([rec["fedavg_test_RMSE_mu"][str(s)] for s in SEEDS])
    sim = np.array([rec["raven_simoracle_test_RMSE_mu"][str(s)] for s in SEEDS])
    Hs = (fed - sim) / fed
    rng = np.random.default_rng(BOOT_SEED)
    boot = np.array([np.mean(rng.choice(Hs, size=len(Hs), replace=True)) for _ in range(BOOT_DRAWS)])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    sd = float(np.std(Hs, ddof=1))
    n = len(Hs)
    mde5 = (stats.t.ppf(0.975, n - 1) + stats.t.ppf(0.80, n - 1)) * sd / math.sqrt(n)
    mde15 = (stats.t.ppf(0.975, 14) + stats.t.ppf(0.80, 14)) * sd / math.sqrt(15)
    print(" %-11s H_by_seed(rec)=%s" % (block, np.round(rec["H_by_seed"], 8).tolist()))
    print("             H_by_seed(recomp)=%s" % np.round(Hs, 8).tolist())
    print("             mean_H=%.10f (rec %.10f) boot=[%.8f, %.8f] (rec [%.8f, %.8f]) sd=%.8f MDE80_n5=%.8f (rec %.8f)"
          % (Hs.mean(), rec["mean_H"], lo, hi, rec["boot_lo"], rec["boot_hi"], sd, mde5, rec["MDE80_n5"]))
    print("             MDE80 at n=15 (instruction S6 wording) = %.8f ; 0.5*mean_H = %.8f ; cond_mde = %s"
          % (mde15, 0.5 * Hs.mean(), mde15 < 0.5 * Hs.mean()))
    print("             cond_mean_ge_1pct=%s  cond_lcb_gt_0.5pct=%s"
          % (Hs.mean() >= H_BAR, lo > LCB_BAR))

print()
print("### C2  every eta level: what selection would have been chosen under other recipes")
# per-level mean test RMSE and per-level mean validation RMSE (driver recipe) from the audit json
lev = {}
for r in grid:
    b, e, s = r["block"], float(r["eta_s"]), int(r["seed"])
    lev.setdefault((b, e), {"val": [], "test": []})
    if r.get("RMSE_mu_val_mu"):
        lev[(b, e)]["val"].append((s, float(r["RMSE_mu_val_mu"])))
    if r.get("test_RMSE_mu"):
        lev[(b, e)]["test"].append((s, float(r["test_RMSE_mu"])))
sel = {}
for b in ("sensorscope", "uair", "traffic"):
    print(" block", b, "frozen eta*=", cfg["per_block"][b]["eta_s_star"])
    rows = []
    for e in (0.001, 0.003, 0.01):
        v = [x[1] for x in lev[(b, e)]["val"]]
        t = [x[1] for x in lev[(b, e)]["test"]]
        rows.append((e, float(np.mean(v)), float(np.mean(t)), len(v), len(t)))
        print("   eta=%-7g mean_val=%.6f  mean_test=%.6f  n_val=%d n_test=%d"
              % (e, np.mean(v), np.mean(t), len(v), len(t)))
    bv = min(rows, key=lambda r: r[1])
    bt = min(rows, key=lambda r: r[2])
    print("   argmin validation -> eta=%.3g   argmin TEST (would be cheating; sensitivity only) -> eta=%.3g"
          % (bv[0], bt[0]))
    print("   test spread across eta levels: %.2f%% of the best level"
          % (100.0 * (max(r[2] for r in rows) / min(r[2] for r in rows) - 1.0)))
    # N3' verdicts at every eta level (same rule, 1.01*c)
    cpath = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs" / b / "central_delivered"
    if cpath.is_dir():
        cs = []
        for s in SEEDS:
            p = cpath / ("seed%d" % s) / "final_metrics.json"
            if p.is_file():
                cs.append(json.loads(p.read_text())["RMSE_mu"])
        c = float(np.mean(cs))
        fpath = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs" / b / "fedavg_window"
        fs = []
        if fpath.is_dir():
            for s in SEEDS:
                p = fpath / ("seed%d" % s) / "final_metrics.json"
                if p.is_file():
                    fs.append(json.loads(p.read_text())["RMSE_mu"])
        f = float(np.mean(fs)) if fs else None
        print("   c(central_delivered 5-seed mean)=%.6f  frozen fedavg=%s" % (c, f))
        for e, mv, mt, _, _ in rows:
            if mt <= 1.01 * c:
                v = "PASS"
            elif f is not None and mt <= f * 0.99:
                v = "PARTIAL"
            else:
                v = "FAIL"
            print("     eta=%-7g new_test=%.6f ratio_to_c=%.6f -> N3'=%s" % (e, mt, mt / c, v))

print()
print("### C3  is the constant predictor already better than every arm? (C_best vs arm test RMSE)")
for b in ("sensorscope", "uair", "traffic"):
    key = "A_eta%g/%s/30001" % (cfg["per_block"][b]["eta_s_star"], b)
    cbest = a["new"][key]["best_const_in_sample"]
    print(" %-11s best constant predictor (weighted train-free, in-sample-on-test mean) = %.6f" % (b, cbest))
    for k, v in sorted(a["new"].items()):
        if "/%s/" % b in k and k.startswith("A_eta"):
            print("     %-28s test=%.6f   vs const gain=%+.2f%%" % (k, v["test_mu"],
                  100.0 * (1.0 - v["test_mu"] / cbest)))
    for k, v in sorted(a["frozen"].items()):
        if "/%s/" % b in k:
            print("     %-28s test=%.6f   vs const gain=%+.2f%%" % (k, v["test_mu"],
                  100.0 * (1.0 - v["test_mu"] / cbest)))

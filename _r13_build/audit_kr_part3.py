"""READ-ONLY recomputation, part 3: stored RMSE_mu Design contrast + ladder pp margin."""
import hashlib
import json
import pathlib

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
SEEDS = list(range(30001, 30021))
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
E4 = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"


def sha(p):
    p = pathlib.Path(p)
    if not p.is_file():
        return "MISSING"
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


print("=" * 100)
print("4b) stored final_metrics.json RMSE_mu, E3 uair raven (Design on) vs E4 uair raven_wo_design (off)")
rows = []
for s in SEEDS:
    pa = E3 / "uair" / "raven" / ("seed%d" % s) / "final_metrics.json"
    pb = E4 / "uair" / "raven_wo_design" / ("seed%d" % s) / "final_metrics.json"
    if not (pa.is_file() and pb.is_file()):
        continue
    va = json.loads(pa.read_text(encoding="utf-8"))
    vb = json.loads(pb.read_text(encoding="utf-8"))
    rows.append({"seed": s, "design_on": float(va["RMSE_mu"]), "design_off": float(vb["RMSE_mu"]),
                 "Delta_group_on": float(va.get("Delta_group", float("nan"))),
                 "Delta_group_off": float(vb.get("Delta_group", float("nan")))})
st = pd.DataFrame(rows)
print("   n=%d  mean on=%.8f  mean off=%.8f" % (len(st), st.design_on.mean(), st.design_off.mean()))
print("   mean-of-paired-ratios = %+.6f %%" % (100 * ((st.design_off / st.design_on) - 1).mean()))
print("   ratio-of-means        = %+.6f %%" % (100 * (st.design_off.mean() / st.design_on.mean() - 1)))
print("   paired mean diff      = %+.8f" % (st.design_off - st.design_on).mean())
print("   FIG_E4 row: relative_change_percent=-6.885463676716227 paired_mean_difference=-0.08230646240707637")
print("   Delta_group means: on=%.6f off=%.6f  ratio-of-means %+.6f %% (FIG says -6.943368495586542)"
      % (st.Delta_group_on.mean(), st.Delta_group_off.mean(),
         100 * (st.Delta_group_off.mean() / st.Delta_group_on.mean() - 1)))
# same contrast on SensorScope, for the "several points is a U-Air fact" part
rows2 = []
for s in SEEDS:
    pa = E3 / "sensorscope" / "raven" / ("seed%d" % s) / "final_metrics.json"
    pb = E4 / "sensorscope" / "raven_wo_design" / ("seed%d" % s) / "final_metrics.json"
    if not (pa.is_file() and pb.is_file()):
        continue
    va = json.loads(pa.read_text(encoding="utf-8"))
    vb = json.loads(pb.read_text(encoding="utf-8"))
    rows2.append({"on": float(va["RMSE_mu"]), "off": float(vb["RMSE_mu"])})
s2 = pd.DataFrame(rows2)
print("   SensorScope same contrast: ratio-of-means RMSE_mu = %+.6f %% (FIG says +0.0052950537985118)"
      % (100 * (s2.off.mean() / s2.on.mean() - 1)))

print()
print("=" * 100)
print("5) claim 4: +0.768 / +0.286 pp projection-over-uniform margin")
for path in ["results_w1_ladder/round_v4/FULL_SEED_LADDER.csv",
             "results_w1_ladder/round_v5/FULL_SEED_LADDER.csv",
             "RAVEN_MCS_PUBLIC_REPRO_R1/w1/ladder_v3/FULL_SEED_LADDER.csv",
             "results_w1_ladder/round_v3/FULL_SEED_LADDER.csv",
             "results_w1_ladder/round_v4/TRAIN_SUMMARY.json",
             "RAVEN_MCS_PUBLIC_REPRO_R1/w1/frontier/G_F_BOTH.csv",
             "results_w1_ladder/round_v2/G_F_BOTH.csv",
             "results_endpoint_screen/round_v1/SCREEN_RUNS.csv"]:
    p = ROOT / path
    if not p.is_file():
        print("   %s : MISSING" % path)
        continue
    if p.suffix == ".json":
        d = json.loads(p.read_text(encoding="utf-8"))
        print("   %s (sha %s): %s" % (path, sha(p), json.dumps(d)[:600]))
        continue
    d = pd.read_csv(p)
    print("   %s (sha %s) columns=%s" % (path, sha(p), list(d.columns)[:14]))
    if "block" in d.columns and "rule" in d.columns and "pp_group" in d.columns:
        for ds, want in (("sensorscope", 0.768), ("uair", 0.286)):
            sub = d[(d.ds == ds) & (d.block == "all20")]
            unif = sub[sub.rule.str.contains("uniform", case=False)]
            proj = sub[sub.rule == "B1:raven"]
            if unif.empty or proj.empty:
                print("      %-12s rows not found" % ds)
                continue
            u = float(unif.pp_group.iloc[0]); r = float(proj.pp_group.iloc[0])
            du = float(unif.d_group.iloc[0]); dr = float(proj.d_group.iloc[0])
            ci = [float(x) for x in str(proj.paired_diff_vs_uniform_ci.iloc[0]).strip("()").split(",")]
            print("      %-12s pp_group uniform=%.8f proj(B1:raven)=%.8f  unif-proj=%+.6f pp "
                  "(manuscript +%.3f)  |  50*(d_unif-d_proj)=%+.6f  |  CI x50=[%.3f,%.3f]"
                  % (ds, u, r, u - r, want, 50 * (du - dr), -50 * ci[0], -50 * ci[1]))
        print("      pp_group == 50*d_group everywhere: %s"
              % bool(np.allclose(d.pp_group, 50 * d.d_group, atol=1e-6)))
    if "endpoint" in d.columns and "d_unif_minus_rule" in d.columns:
        for ds in ("sensorscope", "uair"):
            for arm in ("raven",):
                hit = d[(d.ds == ds) & (d.endpoint == "group") & (d.arm == arm)]
                if hit.empty:
                    continue
                r = hit.iloc[0]
                print("      G_F_BOTH %-12s arm=%-6s d_rule=%.8f d_unif=%.8f d_unif_minus_rule=%.8f "
                      "-> x50=%+.6f pp" % (ds, arm, r.d_rule, r.d_unif, r.d_unif_minus_rule,
                                           -50 * r.d_unif_minus_rule))
    if "Delta_group" in d.columns and "ds" in d.columns and "arm" in d.columns:
        piv = d.pivot_table(index="ds", columns="arm", values="Delta_group", aggfunc="mean")
        for ds in piv.index:
            if {"proj_beta", "uniform_window"} <= set(piv.columns):
                print("      SCREEN_RUNS %-12s mean Delta_group proj_beta=%.8f uniform_window=%.8f "
                      "-> x50=%+.6f pp"
                      % (ds, piv.loc[ds, "proj_beta"], piv.loc[ds, "uniform_window"],
                         50 * (piv.loc[ds, "uniform_window"] - piv.loc[ds, "proj_beta"])))

print()
print("=" * 100)
print("6) manuscript arm order 0.98464 / 1.01158 / 1.01394 / 1.01409 / 1.02693 / 1.05577 vs ladder")
p = ROOT / "results_w1_ladder/round_v4/FULL_SEED_LADDER.csv"
d = pd.read_csv(p)
for ds in ("sensorscope", "uair"):
    sub = d[(d.ds == ds) & (d.block == "all20")].sort_values("d_group")
    print("   %s: %s" % (ds, ", ".join("%s=%.5f" % (r.rule, r.d_group) for r in sub.itertuples())))
print("   looking for 0.98464 in the tree:")
import subprocess
for f in ["results_w1_ladder/round_v4/TRAIN_SUMMARY.json",
          "RAVEN_MCS_PUBLIC_REPRO_R1/w1/tradeoff_v4/TRAIN_SUMMARY.json",
          "results_w1_ladder/round_v4/A2A3_SUMMARY.json"]:
    fp = ROOT / f
    if fp.is_file():
        txt = fp.read_text(encoding="utf-8")
        print("     %s : contains 0.98464 -> %s ; sha %s" % (f, "0.98464" in txt, sha(fp)))

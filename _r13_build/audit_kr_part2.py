"""READ-ONLY recomputation, part 2: target-mass shares, the U-Air Design effect,
and the +0.768 / +0.286 pp projection margin.  Writes nothing.
"""
import hashlib
import importlib.util
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("gd", ROOT / "scripts/gate_dose.py")
gd = importlib.util.module_from_spec(spec)
sys.modules["gd"] = gd
spec.loader.exec_module(gd)

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
print("0) sha256 prefixes of candidate sources")
for p in [
    ROOT / ".rb_work/evidence_headroom/HEADROOM.csv",
    ROOT / ".rb_work/evidence_headroom/MASK_CONCENTRATION.csv",
    ROOT / ".rb_work/evidence_headroom/TARGET_CONCENTRATION.csv",
    ROOT / ".rb_work/evidence_headroom/CONCENTRATION_COUNTERFACTUAL.csv",
    ROOT / ".rb_work/evidence_headroom/REACHABILITY.csv",
    ROOT / ".rb_work/evidence_headroom/REACHABILITY_WINDOWS.parquet",
    ROOT / ".rb_work/evidence_reachability.py",
    ROOT / ".rb_work/evidence_concentration.py",
    ROOT / ".rb_work/audit_new_paragraphs.py",
    ROOT / "scripts/gate_dose.py",
    ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv",
    ROOT / "results_w1_ladder/round_v4/FULL_SEED_LADDER.csv",
    ROOT / "TA_placeholder",
]:
    print("   %-70s %s" % (str(p).replace(str(ROOT) + "\\", ""), sha(p)))

print()
print("=" * 100)
print("1) claims 5/6: largest target group share of mu (recomputed from the frozen artifact)")
for ds in ("sensorscope", "uair", "traffic"):
    try:
        mu, gids, meta = gd.production_mu(ds)
    except Exception as exc:  # noqa: BLE001
        print("   %-12s FAILED %s: %s" % (ds, type(exc).__name__, exc))
        continue
    mu = np.asarray(mu, float)
    share = mu / mu.sum()
    print("   %-12s n_groups=%-5d sum_mu=%.10f  top1=%.8f (%.4f %%)  top5=%.6f  "
          "n_groups_share>1%%=%d  all_equal=%.3e"
          % (ds, len(mu), mu.sum(), share.max(), 100 * share.max(), np.sort(share)[::-1][:5].sum(),
             int((share > 0.01).sum()), float(share.max() - share.min())))
    print("                artifact=%s sha256=%s  n_groups_frozen=%s n_groups_runtime=%s"
          % (meta["artifact_path"], str(meta["artifact_sha256"])[:16],
             meta["n_groups_frozen"], meta["n_groups_runtime"]))

print()
print("   TARGET_CONCENTRATION.csv (mu_group rows), as written:")
tc = pd.read_csv(ROOT / ".rb_work/evidence_headroom/TARGET_CONCENTRATION.csv")
print(tc[tc.label == "mu_group"].to_string(index=False))

print()
print("=" * 100)
print("2) claims 5/6 cross-check: HEADROOM.csv max_group_share per dataset")
hm = pd.read_csv(ROOT / ".rb_work/evidence_headroom/HEADROOM.csv")
print(hm.groupby("dataset")[["n_groups_present", "min_group_share", "max_group_share"]]
      .agg(["nunique", "min", "max"]).to_string())

print()
print("=" * 100)
print("3) claims 2/3 denominators per (dataset, arm) from HEADROOM.csv grouping keys")
for (ds, arm), g in hm.groupby(["dataset", "arm"]):
    print("   %-12s %-16s n_seeds=%d n_groups_present=%s RMSE_mu_tar_mean=%.6f"
          % (ds, arm, len(g), sorted(g.n_groups_present.unique()), g.RMSE_mu_tar.mean()))

print()
print("=" * 100)
print("4) claim 7: U-Air Design effect on RMSE_mu")
ua = hm[hm.dataset == "uair"]
a = ua[ua.arm == "raven"].set_index("seed").RMSE_mu_tar
b = ua[ua.arm == "raven_wo_design"].set_index("seed").RMSE_mu_tar
j = pd.concat([a.rename("design_on"), b.rename("design_off")], axis=1)
print("   HEADROOM.csv RMSE_mu_tar (checkpoint-recomputed, E3 raven vs E4 raven_wo_design)")
print("     mean design_on = %.8f ; mean design_off = %.8f" % (j.design_on.mean(), j.design_off.mean()))
print("     mean-of-ratios (off/on-1)*100 = %+.6f %%"
      % (100 * ((j.design_off / j.design_on) - 1).mean()))
print("     ratio-of-means (off/on-1)*100 = %+.6f %%"
      % (100 * (j.design_off.mean() / j.design_on.mean() - 1)))
print("     paired mean diff (off-on) = %+.8f" % (j.design_off - j.design_on).mean())
print("     per-seed rel %%: %s"
      % " ".join("%+.3f" % v for v in (100 * (j.design_off / j.design_on - 1))))

print()
print("   stored final_metrics.json RMSE_mu, same two arms")
rows = []
for s in SEEDS:
    pa = E3 / "uair/raven/seed%d/final_metrics.json" % s
    pb = E4 / "uair/raven_wo_design/seed%d/final_metrics.json" % s
    if not (pa.is_file() and pb.is_file()):
        continue
    va = json.loads(pa.read_text(encoding="utf-8"))
    vb = json.loads(pb.read_text(encoding="utf-8"))
    rows.append({"seed": s, "design_on": float(va["RMSE_mu"]), "design_off": float(vb["RMSE_mu"])})
st = pd.DataFrame(rows)
print("     n=%d  mean on=%.8f  mean off=%.8f" % (len(st), st.design_on.mean(), st.design_off.mean()))
print("     mean-of-ratios      = %+.6f %%" % (100 * ((st.design_off / st.design_on) - 1).mean()))
print("     ratio-of-means      = %+.6f %%" % (100 * (st.design_off.mean() / st.design_on.mean() - 1)))
print("     paired mean diff    = %+.8f" % (st.design_off - st.design_on).mean())
print("     FIG_E4 CSV states   = -6.885463676716227 %% (U-Air, Design, RMSE_mu)")
print("     FIG_E4 CSV paired_mean_difference = -0.08230646240707637")
print("     recomputed paired mean diff above = %+.8f" % (st.design_off - st.design_on).mean())

print()
print("   all U-Air E4 components on RMSE_mu (relative_change_percent):")
fig = pd.read_csv(ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/figure_data/FIG_E4_E4_COMPONENT_ABLATION.csv")
print(fig[(fig.dataset == "U-Air") & (fig.metric == "RMSE_mu")]
      [["component", "relative_change_percent", "paired_mean_difference", "Holm_p",
        "holm_significant", "direction", "qualitative_magnitude"]].to_string(index=False))

print()
print("=" * 100)
print("5) claim 4: the +0.768 / +0.286 pp projection-over-uniform margin")
for path in ["results_w1_ladder/round_v4/FULL_SEED_LADDER.csv",
             "results_w1_ladder/round_v5/FULL_SEED_LADDER.csv",
             "RAVEN_MCS_PUBLIC_REPRO_R1/w1/ladder_v3/FULL_SEED_LADDER.csv",
             "results_w1_ladder/round_v3/FULL_SEED_LADDER.csv"]:
    p = ROOT / path
    if not p.is_file():
        print("   %s : MISSING" % path)
        continue
    d = pd.read_csv(p)
    print("   %s (sha %s)" % (path, sha(p)))
    for ds, want in (("sensorscope", 0.768), ("uair", 0.286)):
        sub = d[(d.ds == ds) & (d.block == "all20")]
        unif = sub[sub.rule.str.contains("uniform", case=False)]
        # the projection rule is the ladder arm reported as B1:raven (see manuscript arm order)
        proj = sub[sub.rule == "B1:raven"]
        if unif.empty or proj.empty:
            print("      %-12s rows not found (rules: %s)" % (ds, sorted(sub.rule.unique())[:8]))
            continue
        u = float(unif.pp_group.iloc[0])
        r = float(proj.pp_group.iloc[0])
        du = float(unif.d_group.iloc[0])
        dr = float(proj.d_group.iloc[0])
        print("      %-12s pp_group uniform=%.8f proj(B1:raven)=%.8f  unif-proj=%+.6f pp "
              "(manuscript +%.3f)   d_group %.8f vs %.8f -> x50 = %+.6f"
              % (ds, u, r, u - r, want, du, dr, 50 * (du - dr)))
        ci = [float(x) for x in str(proj.paired_diff_vs_uniform_ci.iloc[0]).strip("()").split(",")]
        print("                   paired_diff_vs_uniform_group=%s ; x50 = [%.6f, %.6f]"
              % (proj.paired_diff_vs_uniform_group.iloc[0], -50 * ci[0], -50 * ci[1]))
    # is pp_group exactly 50 x d_group?
    print("      pp_group == 50*d_group on every row: %s (max abs dev %.3e)"
          % (bool(np.allclose(d.pp_group, 50 * d.d_group, atol=1e-6)),
             float(np.max(np.abs(d.pp_group - 50 * d.d_group)))))

print()
print("=" * 100)
print("6) where does 0.98464 (projection-with-debt) live, and the manuscript arm order")
print("   FULL_SEED_LADDER sensorscope/uair d_group for every rule at block=all20:")
p = ROOT / "results_w1_ladder/round_v4/FULL_SEED_LADDER.csv"
if p.is_file():
    d = pd.read_csv(p)
    for ds in ("sensorscope", "uair"):
        sub = d[(d.ds == ds) & (d.block == "all20")].sort_values("d_group")
        print("     %s: %s" % (ds, ", ".join("%s=%.5f" % (r.rule, r.d_group) for r in sub.itertuples())))

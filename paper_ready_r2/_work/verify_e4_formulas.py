"""Verify frozen E4 formulas (effect size, CI) against sealed stats; confirm 240-cell equality with raw index."""
import json
import numpy as np
import pandas as pd
from scipy import stats

ROOT = r"D:\Cursor\raven.mcs"
idx = pd.read_csv(ROOT + r"\artifacts\e4_wo_inst_reference_penalty_final_correction_r1\E4_FINAL_VALID_EVIDENCE_INDEX_R2.csv", dtype={"seed": str})
core = pd.read_csv(ROOT + r"\paper_ready_r1\01_core_data\e4\E4_FINAL_VALID_EVIDENCE_240.csv", dtype={"seed": str})
idx["ds_norm"] = idx["dataset"].str.lower()
core["ds_norm"] = core["dataset"].str.lower()
m = core.merge(idx, left_on=["ds_norm", "seed", "method_raw"], right_on=["ds_norm", "seed", "method"], suffixes=("_c", "_i"))
print("merged:", len(m))
for col in ["RMSE_mu", "Tail_RMSE", "Delta_group", "Delta_c_s"]:
    d = (m[col + "_c"].astype(float) - m[col + "_i"].astype(float)).abs().max()
    print(col, "max abs diff core vs index:", d)
print("EventTrace hash equal:", (m.EventTrace_hash_c == m.EventTrace_hash_i).all())

# Verify formulas against sealed paired tests (parent components) and Inst Gen2 stats
sealed = pd.read_csv(ROOT + r"\artifacts\e4_ablation_semantic_integrity_repair_r1\E4_ABLATION_PAIRED_TESTS_R2.csv")
inst_stats = json.load(open(ROOT + r"\artifacts\e4_wo_inst_reference_penalty_final_correction_r1\E4_INST_FINAL_STATS.json", encoding="utf-8"))

def check_cell(dataset_l, method, metric, sealed_row):
    full = core[(core.ds_norm == dataset_l) & (core.method_raw == "raven")][metric].astype(float).to_numpy()
    abl = core[(core.ds_norm == dataset_l) & (core.method_raw == method)][metric].astype(float).to_numpy()
    d = abl - full
    mean = d.mean()
    sd = d.std(ddof=1)
    med = np.median(d)
    es = mean / sd if sd > 0 else 0.0
    # CI: t-based parametric 95% on paired diffs?
    tq = stats.t.ppf(0.975, df=19)
    lo, hi = mean - tq * sd / np.sqrt(20), mean + tq * sd / np.sqrt(20)
    w = stats.wilcoxon(d, zero_method="wilcox", correction=False, alternative="two-sided")
    return dict(mean=mean, sd=sd, med=med, es=es, ci_lo=lo, ci_hi=hi, p=float(w.pvalue)), sealed_row

print("\n-- check parent sealed rows (E4_ABLATION_PAIRED_TESTS_R2.csv) --")
n_ok = n_bad = 0
for _, r in sealed.iterrows():
    got, _ = check_cell(r.dataset, r.method, r.metric, r)
    ok_es = np.isclose(got["es"], r.effect_size_paired, rtol=1e-6)
    ok_ci = np.isclose(got["ci_lo"], r.ci95_low, rtol=1e-6) and np.isclose(got["ci_hi"], r.ci95_high, rtol=1e-6)
    ok_p = np.isclose(got["p"], r.p_raw, rtol=1e-9)
    ok_mean = np.isclose(got["mean"], r.mean_paired_diff, rtol=1e-9)
    ok_med = np.isclose(got["med"], r.median_paired_diff, rtol=1e-9)
    if not (ok_es and ok_ci and ok_p and ok_mean and ok_med):
        n_bad += 1
        print("MISMATCH", r.dataset, r.component, r.metric,
              dict(es=(got["es"], r.effect_size_paired, ok_es),
                   ci_lo=(got["ci_lo"], r.ci95_low, ok_ci),
                   ci_hi=(got["ci_hi"], r.ci95_high, ok_ci),
                   p=(got["p"], r.p_raw, ok_p),
                   mean=(got["mean"], r.mean_paired_diff, ok_mean),
                   med=(got["med"], r.median_paired_diff, ok_med)))
    else:
        n_ok += 1
print("parent rows ok:", n_ok, "bad:", n_bad)

print("\n-- check Inst Gen2 sealed rows (E4_INST_FINAL_STATS.json) --")
n_ok = n_bad = 0
for r in inst_stats["rows"]:
    ds = {"sensorscope": "sensorscope", "uair": "uair"}[r["dataset"]]
    got, _ = check_cell(ds, "raven_wo_inst", r["metric"], r)
    ok_es = np.isclose(got["es"], r["effect_size_paired"], rtol=1e-6)
    ok_ci = np.isclose(got["ci_lo"], r["ci95_low"], rtol=1e-6) and np.isclose(got["ci_hi"], r["ci95_high"], rtol=1e-6)
    ok_p = np.isclose(got["p"], r["p_raw"], rtol=1e-9)
    ok_mean = np.isclose(got["mean"], r["mean_paired_diff"], rtol=1e-9)
    ok_med = np.isclose(got["med"], r["median_paired_diff"], rtol=1e-9)
    if not (ok_es and ok_ci and ok_p and ok_mean and ok_med):
        n_bad += 1
        print("MISMATCH", r["dataset"], r["metric"],
              dict(es=(got["es"], r["effect_size_paired"], ok_es),
                   ci_lo=(got["ci_lo"], r["ci95_low"], ok_ci),
                   ci_hi=(got["ci_hi"], r["ci95_high"], ok_ci),
                   p=(got["p"], r["p_raw"], ok_p),
                   mean=(got["mean"], r["mean_paired_diff"], ok_mean),
                   med=(got["med"], r["median_paired_diff"], ok_med)))
    else:
        n_ok += 1
print("inst rows ok:", n_ok, "bad:", n_bad)

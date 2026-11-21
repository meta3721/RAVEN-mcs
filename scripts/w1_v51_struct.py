"""W1 round v5.1 - A1' structural re-check (protocol 2.4).

Recomputes the Delta_group and Delta_c-s rows of round_v4/TRADEOFF_PAIRED.csv with the ORACLE
endpoints in place of the trained ones: same contrast list, same bootstrap (10 000, seed
20261002), same Wilcoxon, same Holm family (one dataset x endpoint).  Reports, side by side,
pp_v4 vs pp_oracle, the oracle CI, p_holm_v4 vs p_holm_oracle, and whether the verdict
(verdict = p_holm <= 0.05 on the v4 rule, plus the sign of pp_diff) changes.

Reads A1P_IMPL.csv (written by scripts/w1_v51_oracle.py); writes A1P_STRUCT_PAIRED.csv.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results_w1_ladder/round_v5_1"
V4 = ROOT / "results_w1_ladder/round_v4"
BOOT_N, BOOT_SEED = 10_000, 20261002
PAIRS = (("proj_beta", "uniform_window"), ("raven", "proj_beta"),
         ("proj_beta", "fedavg_window"), ("uniform_window", "fedavg_window"),
         ("proj_beta_debt", "proj_beta"))
ENDPOINTS = (("Delta_group", "d_group_oracle"), ("Delta_c_s", "d_cs_oracle"))


def holm(p):
    order = np.argsort(p)
    adj = np.empty_like(p)
    run = 0.0
    m = len(p)
    for rank, i in enumerate(order):
        val = min(1.0, (m - rank) * p[i])
        run = max(run, val)
        adj[i] = run
    return adj


def verdict(pp, p_holm):
    """v4 wording: a row is 'rule better' when the Holm-adjusted pp difference is
    positive and significant, 'reference better' when negative and significant, else n.s."""
    if p_holm <= 0.05 and pp > 0:
        return "rule_better"
    if p_holm <= 0.05 and pp < 0:
        return "reference_better"
    return "not_significant"


def main() -> None:
    imp = pd.read_csv(OUT / "A1P_IMPL.csv")
    imp = imp[imp.verdict.isin(["certified", "approximate", "comparator"])]
    v4 = pd.read_csv(V4 / "TRADEOFF_PAIRED.csv")
    v4 = v4[v4.endpoint.isin(["Delta_group", "Delta_c_s"])]
    out = []
    for ds in ("sensorscope", "uair"):
        sub = imp[imp.ds == ds]
        piv = {a: g.set_index("seed") for a, g in sub.groupby("arm")}
        for ep_name, col in ENDPOINTS:
            for a, b in PAIRS:
                if a not in piv or b not in piv:
                    out.append({"ds": ds, "endpoint": ep_name, "contrast": f"{a} - {b}",
                                "status": "missing_oracle_endpoints"})
                    continue
                pa, pb = piv[a], piv[b]
                common = pa.index.intersection(pb.index)
                d = (pa.loc[common, col] - pb.loc[common, col]).to_numpy(float)
                rng = np.random.default_rng(BOOT_SEED)
                boot = np.array([d[rng.choice(len(d), len(d), replace=True)].mean()
                                 for _ in range(BOOT_N)])
                try:
                    p = float(stats.wilcoxon(d).pvalue)
                except Exception:                                # noqa: BLE001
                    p = float("nan")
                out.append({"ds": ds, "endpoint": ep_name, "contrast": f"{a} - {b}",
                            "status": "ok", "n_seeds": int(len(d)),
                            "mean_diff_oracle": float(d.mean()),
                            "pp_oracle": float(-100 * d.mean() / 2),
                            "ci_lo_oracle": float(np.percentile(boot, 2.5)),
                            "ci_hi_oracle": float(np.percentile(boot, 97.5)),
                            "p_wilcoxon_oracle": p})
    oa = pd.DataFrame(out)
    ok = oa.status == "ok"
    for ds in ("sensorscope", "uair"):
        for ep in ("Delta_group", "Delta_c_s"):
            sel = ok & (oa.ds == ds) & (oa.endpoint == ep)
            if sel.any():
                oa.loc[sel, "p_holm_oracle"] = holm(oa.loc[sel, "p_wilcoxon_oracle"].to_numpy(float))
    merged = oa.merge(v4[["ds", "endpoint", "contrast", "pp_diff", "ci_lo", "ci_hi",
                          "p_wilcoxon", "p_holm", "n_seeds", "mean_diff"]]
                      .rename(columns={"pp_diff": "pp_v4", "ci_lo": "ci_lo_v4",
                                       "ci_hi": "ci_hi_v4", "p_wilcoxon": "p_wilcoxon_v4",
                                       "p_holm": "p_holm_v4", "n_seeds": "n_seeds_v4",
                                       "mean_diff": "mean_diff_v4"}),
                      on=["ds", "endpoint", "contrast"], how="outer", indicator=True)
    merged["verdict_v4"] = [verdict(r.pp_v4, r.p_holm_v4) if pd.notna(r.pp_v4)
                            and pd.notna(r.p_holm_v4) else "missing"
                            for r in merged.itertuples(index=False)]
    merged["verdict_oracle"] = [verdict(r.pp_oracle, r.p_holm_oracle)
                                if pd.notna(r.pp_oracle) and pd.notna(r.p_holm_oracle)
                                else "missing" for r in merged.itertuples(index=False)]
    merged["verdict_changed"] = merged.verdict_v4 != merged.verdict_oracle
    merged["d_pp"] = merged.pp_oracle - merged.pp_v4
    cols = ["ds", "endpoint", "contrast", "n_seeds", "pp_v4", "pp_oracle", "d_pp",
            "ci_lo_v4", "ci_hi_v4", "ci_lo_oracle", "ci_hi_oracle",
            "p_wilcoxon_v4", "p_wilcoxon_oracle", "p_holm_v4", "p_holm_oracle",
            "verdict_v4", "verdict_oracle", "verdict_changed"]
    merged[cols].to_csv(OUT / "A1P_STRUCT_PAIRED.csv", index=False)
    changed = merged[merged.verdict_changed.astype(bool)]
    summary = {
        "rows": int(len(merged)),
        "verdict_changes": int(len(changed)),
        "changed_rows": changed[["ds", "endpoint", "contrast", "pp_v4", "pp_oracle",
                                 "p_holm_v4", "p_holm_oracle", "verdict_v4",
                                 "verdict_oracle"]].to_dict("records"),
        "max_abs_d_pp": float(merged.d_pp.abs().max()),
        "max_abs_d_pp_by_endpoint": {ep: float(merged[merged.endpoint == ep].d_pp.abs().max())
                                     for ep in ("Delta_group", "Delta_c_s")},
        "note": ("Oracle endpoints replace the trained ones for the three Part B arms "
                 "(uniform_window is analytic and identical in both); the three frozen arms "
                 "retain the round-v4 endpoints, exactly as in the trained comparison."),
    }
    (OUT / "A1P_STRUCT_SUMMARY.json").write_text(json.dumps(summary, indent=2, default=str),
                                                encoding="utf-8")
    print(merged[cols].to_string(index=False))
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()

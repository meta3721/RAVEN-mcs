"""T3 post-processing: internal checks and registered contrasts from SOURCE_LADDER.csv.

No re-solve.  Internal check 1/2 are evaluated for both beta sources:
  * src = raven_wo_use : v2's L3/L5 actually used the R_on ruler arm's beta_hat, so this is the
    like-for-like comparison;
  * src = raven        : the literal wording of the v3 prompt (raven's own E3 beta_hat).
Contrast strings are "rule:src" (e.g. "B1:raven").
"""

from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "results_w1_ladder/round_v3"
R2 = ROOT / "results_w1_ladder/round_v2"
BOOT_N, BOOT_SEED = 10_000, 20261002
MIN_SEEDS = 8
CONTRASTS = (("B1:raven", "B0:raven"), ("B2:raven", "B1:raven"), ("B3:raven", "B2:raven"),
             ("B1:raven", "B1:raven_wo_design"), ("B1:raven", "B1:raven_wo_obs"),
             ("B1:raven", "B1:raven_wo_use"), ("B1:raven_simoracle", "B1:raven"),
             ("B1:raven", "B1:uniform"))


def split_rule_src(tag: str) -> tuple:
    rule, src = tag.split(":", 1)
    return rule, src


def main() -> None:
    df = pd.read_csv(OUT / "SOURCE_LADDER.csv")
    stage = pd.read_csv(R2 / "LADDER.csv")
    stage = stage[(stage["split"] == "report") & (stage["ruler"] == "R_on")]
    v2 = {r: stage[stage.rung == r].set_index(["ds", "seed"]) for r in ("L3", "L5")}

    checks = []
    for src in ("raven_wo_use", "raven"):
        for rule, v2rung, tol in (("B2", "L3", 1e-9), ("B3", "L5", 1e-7)):
            sub = df[(df.src == src) & (df.rule == rule) & (df["split"] == "report") & (df["status"].isna() | (df["status"] == "ok"))]
            errs = []
            for r in sub.itertuples():
                key = (r.ds, r.seed)
                if key in v2[v2rung].index:
                    errs.append(abs(r.d_group - float(v2[v2rung].loc[key, "d_group"])))
            checks.append({"src": src, "rule": rule, "vs_v2_rung": v2rung,
                           "n": len(errs), "max_err": (float(max(errs)) if errs else None),
                           "tol": tol,
                           "pass": bool(errs and max(errs) <= tol),
                           "role": "like-for-like (v2 used the R_on ruler arm's beta_hat)"
                           if src == "raven_wo_use" else "literal v3 prompt wording"})
    ck = pd.DataFrame(checks)

    # continuity: eps -> B1(raven)
    b1 = df[(df.src == "raven") & (df.rule == "B1")].set_index(["ds", "seed"])["d_group"]
    cont_rows = []
    try:
        cdf = pd.read_csv(OUT / "SOURCE_LADDER_CONTINUITY.csv")
        for r in cdf.itertuples():
            key = (r.ds, r.seed)
            if key in b1.index and np.isfinite(getattr(r, "d_group", np.nan)):
                cont_rows.append({"ds": r.ds, "eps": r.eps,
                                  "mean_abs_gap_to_B1_raven": float(np.mean(
                                      [abs(x - b1.loc[key]) for x in [r.d_group]]))})
    except Exception:
        pass

    rng = np.random.default_rng(BOOT_SEED)
    rep = df[df["split"] == "report"]
    out = []
    for ds in sorted(rep.ds.unique()):
        piv = {(s, rl): g.set_index("seed") for (s, rl), g in
               rep[rep.ds == ds].groupby(["src", "rule"])}
        for ep, col in (("group", "d_group"), ("cs", "d_cs")):
            for a, b in CONTRASTS:
                ra, sa = split_rule_src(a)
                rb, sb = split_rule_src(b)
                if (sa, ra) not in piv or (sb, rb) not in piv:
                    out.append({"ds": ds, "endpoint": ep, "contrast": f"{a} - {b}",
                                "status": "insufficient_alignment"})
                    continue
                va, vb = piv[(sa, ra)][col], piv[(sb, rb)][col]
                j = va.index.intersection(vb.index)
                d = (va.loc[j] - vb.loc[j]).dropna()
                if len(d) < MIN_SEEDS:
                    out.append({"ds": ds, "endpoint": ep, "contrast": f"{a} - {b}",
                                "status": "insufficient_alignment", "n_seeds": int(len(d))})
                    continue
                arr = d.to_numpy(dtype=float)
                boots = np.array([arr[rng.choice(len(arr), len(arr), replace=True)].mean()
                                  for _ in range(BOOT_N)])
                try:
                    p = float(stats.wilcoxon(arr).pvalue)
                except Exception:
                    p = float("nan")
                out.append({"ds": ds, "endpoint": ep, "contrast": f"{a} - {b}", "status": "ok",
                            "n_seeds": int(len(arr)), "mean_diff": float(arr.mean()),
                            "ci_lo": float(np.percentile(boots, 2.5)),
                            "ci_hi": float(np.percentile(boots, 97.5)), "p_wilcoxon": p,
                            "pp": float(-100 * arr.mean() / 2)})
    co = pd.DataFrame(out)
    co.to_csv(OUT / "SOURCE_LADDER_CONTRASTS.csv", index=False)
    ck.to_csv(OUT / "SOURCE_LADDER_CHECKS.csv", index=False)
    if cont_rows:
        pd.DataFrame(cont_rows).to_csv(OUT / "SOURCE_LADDER_CONTINUITY.csv", index=False)
    summ = {"checks": ck.to_dict("records"),
            "aligned_seeds_per_src": {f"{d}|{s}": int(df[(df.ds == d) & (df.src == s)]["seed"].nunique())
                                      for d in sorted(df.ds.unique()) for s in sorted(df.src.unique())},
            "rules_present": sorted(df.rule.unique()),
            "status_counts": df["status"].value_counts().to_dict() if "status" in df.columns else {}}
    (OUT / "SOURCE_LADDER.json").write_text(json.dumps(summ, indent=2, default=str), encoding="utf-8")
    print(json.dumps(summ, indent=2, default=str))
    print()
    print(co[co.status == "ok"][["ds", "endpoint", "contrast", "n_seeds", "mean_diff", "ci_lo",
                                 "ci_hi", "pp"]].round(6).to_string(index=False))


if __name__ == "__main__":
    main()

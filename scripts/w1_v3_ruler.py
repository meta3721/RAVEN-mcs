"""T2 (round v3): same-ruler audit of frozen baselines + FedAvg→RAVEN gap decomposition.

For every listed arm and (ds, seed): align to R_on by window_id with identical active_clients,
replay d_group (on the R_on composition) and d_c-s (with the arm's own pair_state.w_atomic),
and compare with the arm's frozen values.  <= 1e-9 => same ruler.

Read-only: writes only results_w1_ladder/round_v3/.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                       # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v3"
R2 = ROOT / "results_w1_ladder/round_v2"
E3 = ROOT / "artifacts/e3_formal_runs_r1/runs"
E4 = ROOT / "artifacts/e4_core_mechanism_ablation_r1/runs"
ARMS = {
    "fedavg_window": E3,
    "fedasync_window": E3,
    "flamf_timealign_adapted": E3,
    "debt_cal": E3,
    "twostage_hajek": E3,
    "local_hajek": E3,
    "raven_simoracle": E3,
    "raven": E3,
    # discovered locations (the v3 prompt assumed one E3 root; these two are separate):
    "fedau_window": ROOT / "artifacts/e3_fedau_window_r1/runs",
    "obsuse_window": ROOT / "artifacts/e3_obsuse_window_r1/runs",
    "raven_wo_design": E4,
}
DECOMP_ARMS = ("fedavg_window", "fedau_window", "obsuse_window")
TOL = 1e-9
BOOT_N, BOOT_SEED = 10_000, 20261002


def load_arm(ds: str, base: pathlib.Path, arm: str, seed: int):
    p = base / ds / arm / f"seed{seed}"
    if not (p / "final_metrics.json").is_file():
        return None
    act = W.active_windows(json.loads((p / "window_metrics.json").read_text(encoding="utf-8")))
    fm = json.loads((p / "final_metrics.json").read_text(encoding="utf-8"))
    ps = pd.read_parquet(p / "pair_state.parquet") if (p / "pair_state.parquet").is_file() else None
    return {"path": p, "act": act, "fm": fm, "ps": ps}


def audit(pi: dict) -> tuple:
    rows = []
    for ds in W.DS:
        pi_ds = pi[ds]
        star = pd.read_csv(R2 / "FRONTIER.csv")
        star = star[(star.ds == ds) & (star.ruler == "R_on")]
        star = star.groupby("seed")[["d_unif_group", "d_star_group"]].first()
        for seed in W.SEEDS:
            ruler = W.build_case(ds, "R_on", "raven_wo_use", seed, pi_ds)
            if ruler is None:
                continue
            for arm, base in ARMS.items():
                ac = load_arm(ds, base, arm, seed)
                if ac is None:
                    rows.append({"ds": ds, "arm": arm, "seed": seed, "aligned_frac": None,
                                 "err_group": None, "err_cs": None, "verdict": "missing_run"})
                    continue
                by_wid = {int(x["window_id"]): x for x in ac["act"]}
                pairs = []
                for j, wid in enumerate(ruler["wids"]):
                    x = by_wid.get(int(wid))
                    if x is None:
                        continue
                    if tuple(str(c) for c in x["active_clients"]) == tuple(ruler["clients"][j]):
                        pairs.append((j, x))
                frac_on = len(pairs) / max(ruler["n"], 1)
                frac_arm = len(pairs) / max(len(ac["act"]), 1)
                rec = {"ds": ds, "arm": arm, "seed": seed, "n_ruler": ruler["n"],
                       "n_arm": len(ac["act"]), "n_aligned": len(pairs),
                       "aligned_frac": frac_on, "aligned_frac_arm": frac_arm,
                       "frozen_d_group": ac["fm"].get("Delta_group"),
                       "frozen_d_cs": ac["fm"].get("Delta_c_s")}
                if not pairs or frac_on < 1.0 - 1e-12 or frac_arm < 1.0 - 1e-12:
                    rec.update({"err_group": None, "err_cs": None, "verdict": "ruler_misaligned",
                                "d_group_on_R_on": None, "d_cs_replay": None})
                    rows.append(rec)
                    continue
                dg = W.delta_group(ruler["M"],
                                   [np.asarray(x["alpha"], dtype=float) for _, x in pairs],
                                   ruler["mu"])
                amap = {int(x["window_id"]): {str(c): float(v) for c, v in
                                              zip(x["active_clients"], x["alpha"])}
                        for _, x in pairs}
                dcs = (W.delta_cs(ac["ps"], amap, len(pairs), pi_ds) if ac["ps"] is not None else None)
                eg = abs(dg - float(ac["fm"]["Delta_group"]))
                ec = (abs(dcs - float(ac["fm"]["Delta_c_s"]))
                      if dcs is not None and ac["fm"].get("Delta_c_s") is not None else None)
                same = bool(eg <= TOL and (ec is not None and ec <= TOL))
                rec.update({"err_group": eg, "err_cs": ec, "d_group_on_R_on": dg,
                            "d_cs_replay": dcs,
                            "verdict": "same_ruler" if same else "different_ruler"})
                if seed in star.index:
                    rec["d_unif_group"] = float(star.loc[seed, "d_unif_group"])
                    rec["d_star_group"] = float(star.loc[seed, "d_star_group"])
                rows.append(rec)
    df = pd.DataFrame(rows)
    return df


def decompose(df: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(BOOT_SEED)
    out = []
    for ds in W.DS:
        raven = load_frozen(ds, "raven")
        for arm in DECOMP_ARMS:
            sub = df[(df.ds == ds) & (df.arm == arm)]
            if not len(sub) or not (sub["verdict"] == "same_ruler").all():
                out.append({"ds": ds, "arm": arm, "status": "not_decomposable_different_ruler"
                            if len(sub) and (sub["verdict"] != "same_ruler").any()
                            else "missing_run",
                            "n_seeds": int(len(sub))})
                continue
            m = sub.merge(raven, on="seed", how="inner").dropna(
                subset=["Delta_group", "d_unif_group", "d_star_group"])
            if len(m) < 3:
                out.append({"ds": ds, "arm": arm, "status": "too_few_seeds", "n_seeds": int(len(m))})
                continue
            tot = m["frozen_d_group"] - m["Delta_group"]              # d_arm - d_RAVEN (protocol LHS)
            seg1 = m["frozen_d_group"] - m["d_unif_group"]            # arm - unif
            seg2 = m["d_unif_group"] - m["Delta_group"]               # unif - raven
            idx = np.arange(len(m))

            def boot(v):
                a = v.to_numpy(dtype=float)
                s = np.array([a[rng.choice(idx, size=len(a), replace=True)].mean()
                              for _ in range(BOOT_N)])
                return float(a.mean()), float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))

            t, tl, th = boot(tot)
            s1, s1l, s1h = boot(seg1)
            s2, s2l, s2h = boot(seg2)
            out.append({"ds": ds, "arm": arm, "status": "ok", "n_seeds": int(len(m)),
                        "delta_total": t, "delta_total_ci": [tl, th],
                        "seg1_arm_minus_unif": s1, "seg1_ci": [s1l, s1h],
                        "seg2_unif_minus_raven": s2, "seg2_ci": [s2l, s2h],
                        "seg1_share": s1 / t if t else None, "seg2_share": s2 / t if t else None,
                        "pp_total": 100 * t / 2, "pp_seg1": 100 * s1 / 2, "pp_seg2": 100 * s2 / 2})
    return pd.DataFrame(out)


def load_frozen(ds: str, arm: str) -> pd.DataFrame:
    rows = []
    for seed in W.SEEDS:
        p = E3 / ds / arm / f"seed{seed}" / "final_metrics.json"
        if p.is_file():
            rows.append({"seed": seed, "Delta_group": json.loads(p.read_text())["Delta_group"]})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", default="round_v3")
    args = ap.parse_args()
    global OUT
    OUT = ROOT / "results_w1_ladder" / args.round
    OUT.mkdir(parents=True, exist_ok=True)
    pi = {d: W.pi_tar_for(d) for d in W.DS}
    df = audit(pi)
    df.to_csv(OUT / "SAME_RULER_AUDIT.csv", index=False)
    dec = decompose(df)
    dec.to_csv(OUT / "GAP_DECOMPOSITION.csv", index=False)
    summ = df.groupby(["ds", "arm"])["verdict"].value_counts().unstack(fill_value=0).reset_index()
    print(summ.to_string(index=False))
    print()
    print(dec.to_string(index=False))


if __name__ == "__main__":
    main()

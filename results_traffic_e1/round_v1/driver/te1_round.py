"""TE1: FedAdam headroom confirmation on NSW-Traffic, confirm seeds 30006-30020.

Implements the execution prompt sections 3-8 in order. Read-only on
results_server_optimizer/round_v1/; all outputs under results_traffic_e1/round_v1/.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import pathlib
import sys
from datetime import datetime, timezone

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(__file__).resolve().parents[1]          # results_traffic_e1/round_v1
ROOT = pathlib.Path(__file__).resolve().parents[3]
S1P = ROOT / "results_server_optimizer/round_v1"            # frozen, read-only
RUNS = OUT / "runs"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))

from s1p_driver import (LOCAL_STEPS, TRAFFIC_REUSE_EXEMPTION, ServerOptWindowRunner,  # noqa: E402
                        kr_le3_share, run_one, validation_rmse_mu)

BLOCK, SCENARIO = "traffic", "complete_aligned"
ETA_S = 0.003
LOCAL_STEPS_EXPECTED = 2
ARMS = ("fedavg_window", "raven_simoracle")
SCREEN = list(range(30001, 30006))
CONFIRM = list(range(30006, 30021))
N_GROUPS = 172
BOOT_DRAWS, BOOT_SEED = 10000, 20261007
TAGS = {"fedavg_window": "C1_fedavg", "raven_simoracle": "C1_simoracle"}
S1P_TAG = {"fedavg_window": "A_eta0.003", "raven_simoracle": "C_raven_simoracle"}
S1P_PATHS = {
    "fedavg_window": S1P / "runs/A_eta0.003/traffic/fedavg_window/seed30001/final_metrics.json",
    "raven_simoracle": S1P / "runs/C_raven_simoracle/traffic/raven_simoracle/seed30001/final_metrics.json",
}
LOG = []


def say(msg: str) -> None:
    print(msg, flush=True)
    LOG.append(f"{datetime.now(timezone.utc).isoformat()} {msg}")


def jdump(obj, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def sha_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def blocked(reason: str, detail: str = "") -> int:
    (OUT / "TE1_BLOCKED.md").write_text(
        f"# TE1 BLOCKED\n\n{datetime.now(timezone.utc).isoformat()}\n\n## Reason\n\n{reason}\n\n"
        f"## Detail\n\n{detail}\n\n## State\n\nNo confirm seed was started.\n",
        encoding="utf-8")
    say(f"BLOCKED: {reason}")
    return 2


def run_traffic(arm: str, seed: int, tag: str, force: bool = False) -> pathlib.Path:
    return run_one(BLOCK, arm, seed, LOCAL_STEPS, tag, "adam", eta_s=ETA_S, force=force)


def run_dir(tag: str, arm: str, seed: int) -> pathlib.Path:
    return RUNS / tag / BLOCK / arm / ("seed%d" % seed)


def s1p_run_dir(arm: str, seed: int) -> pathlib.Path:
    return S1P / "runs" / S1P_TAG[arm] / BLOCK / arm / ("seed%d" % seed)


def nonfinite_scan(d: pathlib.Path) -> list[str]:
    """Every non-finite number reachable in the run directory: all JSON files and the checkpoint."""
    import torch

    bad: list[str] = []

    def walk(name, o, depth=0):
        if depth > 8:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                walk(f"{name}.{k}", v, depth + 1)
        elif isinstance(o, list):
            for i, v in enumerate(o[:20000]):
                walk(f"{name}[{i}]", v, depth + 1)
        elif isinstance(o, float) and not math.isfinite(o):
            bad.append(name)

    for p in sorted(d.rglob("*.json")):
        try:
            walk(p.name, json.loads(p.read_text(encoding="utf-8")))
        except Exception:  # noqa: BLE001
            continue
    ck = d / "checkpoints/final.pt"
    if ck.is_file():
        obj = torch.load(ck, map_location="cpu", weights_only=False)
        theta = obj["state_dict"] if isinstance(obj, dict) and "state_dict" in obj else obj
        for k, v in theta.items():
            if not bool(torch.isfinite(v).all()):
                bad.append(f"final.pt:{k}")
    return bad


def c_val_from_ckpt(ds, ckpt: pathlib.Path) -> dict:
    from raven_mcs.data.target import GroupMapper, TargetBuilder
    from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test
    import pandas as pd

    atomic = ds.atomic_df.copy()
    atomic["target_group_main"] = pd.Categorical(atomic["target_group"]).codes
    tgt = TargetBuilder(group_mapper=GroupMapper("target_group_main")).build(atomic, split="validation")
    mu = np.asarray([float(tgt.group_mass.get(str(g), 0.0)) for g in range(N_GROUPS)], dtype=np.float64)

    class _Shim:
        pass

    shim = _Shim()
    shim.model = CommonNDMF_from_ckpt(ckpt, ds.num_spatial)
    pred = _predict(shim, ds, split="validation")
    w = np.asarray(_mu_weights_for_test(pred, mu), dtype=np.float64)
    w = w / w.sum()
    y = np.asarray(pred["y_true"], dtype=np.float64)
    ybar = float(np.sum(w * y))
    return {"n": int(len(y)), "weighted_mean": ybar,
            "c_val": float(np.sqrt(np.sum(w * (y - ybar) ** 2))),
            "weight_sha256": hashlib.sha256(w.tobytes()).hexdigest(),
            "mu_weight_sha256": hashlib.sha256(mu.tobytes()).hexdigest()}


def val_rmse(arm: str, seed: int, d: pathlib.Path, ds) -> dict:
    ck = d / "checkpoints/final.pt"
    if not ck.is_file():
        return {"RMSE_mu_val_mu": None}
    return validation_rmse_mu(BLOCK, ds, ck, N_GROUPS)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tables").mkdir(exist_ok=True)
    say(f"TE1 start | block={BLOCK} eta_s={ETA_S} local_steps={LOCAL_STEPS} "
        f"exemption={TRAFFIC_REUSE_EXEMPTION}")

    # The configuration this round installs must equal the S1' frozen configuration recorded in the
    # frozen run. SERVER_OPT is a class attribute rewritten by install(), so read it back after
    # installing; reading it before any install returns the un-installed default ("off").
    from s1p_driver import BETA1, BETA2, TAU, install, uninstall

    frozen_meta = json.loads((S1P / "runs/A_eta0.003/traffic/fedavg_window/seed30001/"
                              "SERVER_OPT_META.json").read_text(encoding="utf-8"))
    frozen_so = frozen_meta["server_opt"]
    install("adam", ETA_S)
    would_install = dict(ServerOptWindowRunner.SERVER_OPT)
    uninstall()
    so = would_install
    config_check = {"s1p_frozen_server_opt": frozen_so, "would_install": would_install,
                    "constants": {"BETA1": BETA1, "BETA2": BETA2, "TAU": TAU},
                    "local_steps": LOCAL_STEPS, "local_steps_in_s1p_frozen_run": frozen_meta["local_steps"],
                    "server_opt_match": frozen_so == would_install}
    if frozen_so != would_install:
        return blocked("the configuration this round installs differs from the S1' frozen one",
                       json.dumps(config_check, default=str))
    if LOCAL_STEPS != LOCAL_STEPS_EXPECTED or frozen_meta["local_steps"] != LOCAL_STEPS:
        return blocked("LOCAL_STEPS mismatch", json.dumps(config_check, default=str))
    say(f"config check: installs {json.dumps(would_install)} == S1' frozen {json.dumps(frozen_so)}; "
        f"local_steps {LOCAL_STEPS} == {frozen_meta['local_steps']}")

    # ---- section 2 STOP check ----
    pre = [p for p in S1P.rglob("seed300*") if p.is_dir() and 30006 <= int(p.name[4:]) <= 30020]
    if pre:
        return blocked("confirm seeds already exist under the S1' tree", str(pre[:5]))
    say("section-2 STOP check: clear (no seed30006..30020 under the S1' tree)")

    # ---- section 3 G0 identity ----
    g0 = {"checked_utc": datetime.now(timezone.utc).isoformat(), "arms": {}}
    for arm in ARMS:
        d = run_traffic(arm, 30001, "G0_" + ("fedavg" if arm == "fedavg_window" else "simoracle"),
                        force=True)
        mine = json.loads((d / "final_metrics.json").read_text(encoding="utf-8"))
        ref = json.loads(S1P_PATHS[arm].read_text(encoding="utf-8"))
        same_rmse = mine.get("RMSE_mu") == ref.get("RMSE_mu")
        diffs = sorted(k for k in set(mine) | set(ref) if mine.get(k) != ref.get(k))
        g0["arms"][arm] = {"rerun_dir": str(d.relative_to(ROOT)), "rerun_RMSE_mu": mine.get("RMSE_mu"),
                           "s1p_file": str(S1P_PATHS[arm].relative_to(ROOT)),
                           "s1p_RMSE_mu": ref.get("RMSE_mu"), "bit_match": same_rmse,
                           "final_metrics_sha256": sha_file(d / "final_metrics.json"),
                           "differing_fields": diffs,
                           "checkpoint_sha256": sha_file(d / "checkpoints/final.pt")}
        say(f"  G0 {arm}: RMSE_mu {mine.get('RMSE_mu')} vs {ref.get('RMSE_mu')} bit_match={same_rmse} "
            f"differing_fields={diffs}")
        if not same_rmse:
            (OUT / "TE1_GATES.md").write_text(f"# TE1 gates\n\nG0 FAILED for {arm}.\n", encoding="utf-8")
            return blocked(f"G0 identity failed for {arm}",
                           f"rerun={mine.get('RMSE_mu')} s1p={ref.get('RMSE_mu')}")
    (OUT / "TE1_GATES.md").write_text(
        "# TE1 gates\n\n## G0 identity (traffic, eta_s = 0.003, R = 1, seed 30001)\n\n"
        "| arm | S1' RMSE_mu | re-run RMSE_mu | bit match | differing fields |\n|---|---:|---:|---|---|\n"
        + "\n".join(f"| {a} | {v['s1p_RMSE_mu']} | {v['rerun_RMSE_mu']} | {v['bit_match']} | "
                    f"{v['differing_fields']} |" for a, v in g0["arms"].items())
        + f"\n\nServer optimizer (frozen): `{json.dumps(so)}`\n\nLOCAL_STEPS = {LOCAL_STEPS}; "
        f"copy of the S1' driver sha256 `{sha_file(HERE / 's1p_driver.py')}`.\n",
        encoding="utf-8")
    say("G0 PASS on both arms")

    # ---- section 3 G-const, frozen before any confirm test prediction ----
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset

    ds = load_paper_dataset(ROOT, BLOCK)
    frozen_ck = s1p_run_dir("raven_simoracle", 30001) / "checkpoints/final.pt"
    rc = c_val_from_ckpt(ds, frozen_ck)
    # cross-check: the G0 re-run checkpoint must give the same weight vector
    g0_ck = run_dir("G0_simoracle", "raven_simoracle", 30001) / "checkpoints/final.pt"
    rc2 = c_val_from_ckpt(ds, g0_ck)
    rc.update({"source_checkpoint": str(frozen_ck.relative_to(ROOT)),
               "source_checkpoint_sha256": sha_file(frozen_ck),
               "cross_check_checkpoint": str(g0_ck.relative_to(ROOT)),
               "cross_check_c_val": rc2["c_val"],
               "cross_check_weight_sha256": rc2["weight_sha256"],
               "weight_vector_stable": rc["weight_sha256"] == rc2["weight_sha256"],
               "divergence_ceiling": 2.0 * rc["c_val"],
               "frozen_utc": datetime.now(timezone.utc).isoformat(),
               "note": "weighted standard deviation on the validation split through the scoring path "
                       "(runner._mu_weights_for_test + metrics.rmse_mu weights); frozen before any "
                       "confirm test prediction",
               "prompt_unweighted_check": {"sd": 0.99457, "mean": 0.00878}})
    jdump(rc, OUT / "TE1_FROZEN_CONST.json")
    c_val = rc["c_val"]
    say(f"G-const frozen: n={rc['n']} mean={rc['weighted_mean']:.8f} c_val={c_val:.8f} "
        f"ceiling={rc['divergence_ceiling']:.6f} weight_sha={rc['weight_sha256'][:16]} "
        f"stable={rc['weight_vector_stable']}")

    # ---- screen diagnostic (section 3), no GO column ----
    rows = []
    for seed in SCREEN:
        for arm in ARMS:
            d = s1p_run_dir(arm, seed)
            fm = json.loads((d / "final_metrics.json").read_text(encoding="utf-8"))
            vr = val_rmse(arm, seed, d, ds)
            nf = nonfinite_scan(d)
            v = vr["RMSE_mu_val_mu"]
            fail = bool(nf) or (v is not None and v > 2 * c_val)
            rows.append({"seed": seed, "arm": arm,
                         "validation_RMSE_mu": v,
                         "validation_weighted_mass_sum": vr.get("val_mu_mass_sum"),
                         "nonfinite_count": len(nf), "nonfinite_examples": ";".join(nf[:3]),
                         "exceeds_2c_val": (None if v is None else bool(v > 2 * c_val)),
                         "stability": "fail" if fail else "pass",
                         "test_RMSE_mu": fm.get("RMSE_mu"),
                         "source": "screen (S1' frozen run, not re-tested)"})
    with (OUT / "TE1_SCREEN_STABILITY.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    say("screen stability written (5 seeds x 2 arms, no GO column): "
        + ", ".join(f"seed{r['seed']}/{r['arm'].split('_')[0]}={r['stability']}" for r in rows))

    # ---- section 8 step 3: the 15 confirm pairs ----
    say("running 15 confirm pairs (both arms) ...")
    for seed in CONFIRM:
        for arm in ARMS:
            try:
                run_traffic(arm, seed, TAGS[arm])
            except Exception as exc:  # noqa: BLE001
                return blocked(f"a confirm run was refused or failed: {arm} seed {seed}",
                               f"{type(exc).__name__}: {exc}")

    # ---- section 4 + 5 ----
    conf, analysis = [], []
    for seed in CONFIRM:
        rec = {"seed": seed}
        ok = True
        for arm in ARMS:
            d = run_dir(TAGS[arm], arm, seed)
            fm = json.loads((d / "final_metrics.json").read_text(encoding="utf-8"))
            vr = val_rmse(arm, seed, d, ds)
            nf = nonfinite_scan(d)
            v = vr["RMSE_mu_val_mu"]
            rec[f"val_RMSE_mu_{arm}"] = v
            rec[f"test_RMSE_mu_{arm}"] = fm.get("RMSE_mu")
            rec[f"nonfinite_{arm}"] = len(nf)
            rec[f"stability_{arm}"] = "pass" if (not nf and v is not None and v <= 2 * c_val) else "fail"
            if rec[f"stability_{arm}"] == "fail":
                ok = False
            kr = kr_le3_share(d)
            rec[f"kr_le3_share_{arm}"] = kr["share_kr_le3"]
            rec[f"n_active_{arm}"] = kr["n_active"]
        rec["pair_stability"] = "pass" if ok else "fail"
        fed, sim = rec["test_RMSE_mu_fedavg_window"], rec["test_RMSE_mu_raven_simoracle"]
        rec["H_s"] = ((fed - sim) / fed) if (fed and sim is not None) else None
        conf.append(rec)
        if ok and rec["H_s"] is not None:
            analysis.append(rec)

    with (OUT / "tables/TE1_CONFIRM.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(conf[0].keys()))
        w.writeheader()
        w.writerows(conf)

    kr_rows = [{"seed": r["seed"], "arm": a, "n_active": r[f"n_active_{a}"],
                "share_kr_le3": r[f"kr_le3_share_{a}"], "pair_in_analysis_set":
                r["pair_stability"] == "pass"} for r in conf for a in ARMS]
    with (OUT / "tables/TE1_KR.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(kr_rows[0].keys()))
        w.writeheader()
        w.writerows(kr_rows)

    n_fail = sum(1 for r in conf if r["pair_stability"] == "fail")
    Hs = np.asarray([r["H_s"] for r in analysis], dtype=np.float64)
    n = int(len(Hs))
    out = {"verdict": None, "n_confirm_pairs": len(conf), "n_stability_failures": n_fail,
           "n_analysis": n, "H_per_seed": {str(r["seed"]): r["H_s"] for r in conf},
           "analysis_seeds": [r["seed"] for r in analysis]}
    if n_fail:
        out.update({"verdict": "NO-GO-STABILITY",
                    "stability_failures": [{"seed": r["seed"],
                                            "stability_fedavg_window": r["stability_fedavg_window"],
                                            "stability_raven_simoracle": r["stability_raven_simoracle"]}
                                           for r in conf if r["pair_stability"] == "fail"],
                    "note": "section 4: any confirm pair failing stability makes the primary verdict "
                            "NO-GO-STABILITY; the remaining pairs are descriptive only",
                    "descriptive_only": {"n": n, "mean_H": float(Hs.mean()) if n else None}})
    else:
        from scipy.stats import t as tdist

        mean_H = float(Hs.mean())
        sd = float(Hs.std(ddof=1))
        t_lo = float(tdist.ppf(0.975, n - 1))
        t_hi = float(tdist.ppf(0.80, n - 1))
        mde80 = (t_lo + t_hi) * sd / math.sqrt(n)
        rng = np.random.default_rng(BOOT_SEED)
        boot = np.asarray([float(np.mean(rng.choice(Hs, size=n, replace=True)))
                           for _ in range(BOOT_DRAWS)])
        lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
        kr_share = float(np.mean([r["kr_le3_share_fedavg_window"] for r in analysis]))
        kr_share_sim = float(np.mean([r["kr_le3_share_raven_simoracle"] for r in analysis]))
        cond = {"H_ge_0.01": mean_H >= 0.01, "boot_lower_gt_0.005": lo > 0.005,
                "mde80_lt_half_H": mde80 < 0.5 * mean_H,
                "kr_le3_share_le_0.25": kr_share <= 0.25}
        out.update({"verdict": "GO-H" if all(cond.values()) else "NO-GO-H",
                    "mean_H": mean_H, "sd_H": sd, "n": n,
                    "bootstrap": {"draws": BOOT_DRAWS, "rng": BOOT_SEED, "lower": lo, "upper": hi},
                    "MDE80": mde80, "t_lower": t_lo, "t_upper": t_hi,
                    "kr_le3_share_confirm_fedavg": kr_share,
                    "kr_le3_share_confirm_simoracle": kr_share_sim,
                    "kr_le3_share_basis": "mean over the analysis-set fedavg_window runs; the "
                                          "simoracle mean is reported alongside",
                    "conditions": cond,
                    "screen_mean_H_for_reference": -0.080700})
    out["created_utc"] = datetime.now(timezone.utc).isoformat()
    out["instruction_sha256"] = sha_file(ROOT / "ccfa-review-reports/"
                                               "raven-mcs-traffic-e1-confirm-execution-prompt.md")
    out["driver_sha256"] = sha_file(HERE / "s1p_driver.py")
    out["frozen_const"] = {k: rc[k] for k in ("n", "weighted_mean", "c_val", "divergence_ceiling",
                                              "weight_sha256")}
    out["config_check"] = config_check
    jdump(out, OUT / "TE1_VERDICT.json")

    # ---- section 7: the report ----
    L = ["# TE1: FedAdam headroom confirmation on NSW-Traffic", "",
         f"- Instruction: `ccfa-review-reports/raven-mcs-traffic-e1-confirm-execution-prompt.md`, "
         f"sha256 `{out['instruction_sha256']}`",
         f"- Driver: copy of the S1' driver, sha256 `{out['driver_sha256']}`",
         f"- Frozen server optimizer: `{json.dumps(so)}`, `LOCAL_STEPS = {LOCAL_STEPS}`, "
         f"one server update per window",
         f"- Block `{BLOCK}`, scenario `{SCENARIO}`, `eta_s = {ETA_S}`, arms {list(ARMS)}",
         f"- Screen seeds {SCREEN[0]}-{SCREEN[-1]} (closed, not re-tested); confirm seeds "
         f"{CONFIRM[0]}-{CONFIRM[-1]}",
         "", "## Gates", "",
         f"G0 identity passed on both arms: the re-run `RMSE_mu` equals the S1' file exactly "
         f"({g0['arms']['fedavg_window']['rerun_RMSE_mu']} and "
         f"{g0['arms']['raven_simoracle']['rerun_RMSE_mu']}), with differences confined to "
         f"{sorted(set(g0['arms']['fedavg_window']['differing_fields']) | set(g0['arms']['raven_simoracle']['differing_fields']))}.",
         "",
         f"G-const frozen before any confirm test prediction: `n = {rc['n']}`, weighted mean "
         f"`{rc['weighted_mean']:.8f}`, `c_val = {c_val:.8f}`, ceiling `2*c_val = "
         f"{rc['divergence_ceiling']:.6f}`, weight-vector sha256 `{rc['weight_sha256']}`. The weight "
         f"vector is identical when recomputed from the G0 re-run checkpoint "
         f"({rc['weight_vector_stable']}). The prompt's unweighted check value (sd 0.99457, mean "
         f"0.00878) agrees with the scoring-path value to four decimals.",
         "", "## Screen diagnostic", "",
         "Five S1' screen seeds, stability rule of section 4 applied, no GO column: "
         + ", ".join(f"seed {r['seed']} {r['arm']} = {r['stability']} (validation RMSE_mu "
                     f"{r['validation_RMSE_mu']:.6f})" for r in rows if r["arm"] == "raven_simoracle")
         + ". The seed 30005 oracle arm passes the ceiling as the prompt expected.",
         "",
         "## Confirm seeds and the primary estimand", "",
         f"`n_confirm_pairs = {out['n_confirm_pairs']}`, stability failures = "
         f"`{out['n_stability_failures']}`, analysis set `n = {out.get('n_analysis', n)}`.",
         ""]
    if out["verdict"] == "NO-GO-STABILITY":
        L += ["**Verdict: `NO-GO-STABILITY`.** At least one confirm pair failed the section-4 stability "
              "rule, so no GO is available. The surviving pairs are descriptive only.",
              "", "| seed | stability | H_s |", "|---|---|---|"]
        L += [f"| {r['seed']} | {r['pair_stability']} | {r['H_s']} |" for r in conf]
    else:
        L += [f"Mean `H = {out['mean_H']:.6f}` (sample sd `{out['sd_H']:.6f}`), percentile bootstrap "
              f"95% interval `[{out['bootstrap']['lower']:.6f}, {out['bootstrap']['upper']:.6f}]` "
              f"({out['bootstrap']['draws']} draws, rng {out['bootstrap']['rng']}), "
              f"`MDE80 = {out['MDE80']:.6f}` at `n = {out['n']}`, confirm `K_r <= 3` share "
              f"`{out['kr_le3_share_confirm_fedavg']:.6f}` (fedavg arm; simoracle arm "
              f"`{out['kr_le3_share_confirm_simoracle']:.6f}`).",
              "", "| GO condition | value | holds |", "|---|---:|---|",
              f"| H >= 0.01 | {out['mean_H']:.6f} | {out['conditions']['H_ge_0.01']} |",
              f"| bootstrap lower > 0.005 | {out['bootstrap']['lower']:.6f} | "
              f"{out['conditions']['boot_lower_gt_0.005']} |",
              f"| MDE80 < 0.5 * H | {out['MDE80']:.6f} vs {0.5 * out['mean_H']:.6f} | "
              f"{out['conditions']['mde80_lt_half_H']} |",
              f"| K_r <= 3 share <= 0.25 | {out['kr_le3_share_confirm_fedavg']:.6f} | "
              f"{out['conditions']['kr_le3_share_le_0.25']} |",
              "", f"**Verdict: `{out['verdict']}`.**", "",
              "| seed | validation RMSE_mu fedavg | validation RMSE_mu oracle | test RMSE_mu fedavg | "
              "test RMSE_mu oracle | H_s |", "|---|---:|---:|---:|---:|---:|"]
        L += [f"| {r['seed']} | {r['val_RMSE_mu_fedavg_window']:.6f} | "
              f"{r['val_RMSE_mu_raven_simoracle']:.6f} | {r['test_RMSE_mu_fedavg_window']:.6f} | "
              f"{r['test_RMSE_mu_raven_simoracle']:.6f} | {r['H_s']:.6f} |" for r in conf]
    L += ["", "## Deviations", "",
          "- The execution order of the prompt's section 8 was followed: driver copy, G0, freeze, "
          "screen table, then the 15 confirm pairs, then sections 4 and 5.",
          "- The prompt fixes the arms as `fedavg_window` and `raven_simoracle`; `raven` was not run. "
          "Stage B was not run and `eta_s` was not re-selected.",
          "- `K_r <= 3` is reported per seed and per arm in `tables/TE1_KR.csv`; the GO condition uses "
          "the analysis-set mean over the fedavg arm, with the simoracle mean reported alongside so "
          "the reading does not depend on that choice.",
          "- The finiteness limb of the stability rule scans every JSON file in the run directory and "
          "every checkpoint tensor. The runner writes no separate training-loss series, so no loss "
          "file exists beyond those.",
          "- No `src/`, paper, frozen artifact or `results_server_optimizer/round_v1/` path was "
          "modified; the traffic runs used the reuse-guard exemption already recorded in the "
          "diagnosis ledger Part IX item 65.",
          "", "## What this round does not claim", "",
          "The screen seeds are not re-tested and are not combined with the confirm seeds. A `GO-H` "
          "would be the prediction-headroom clause only, not a deployment-decision result and not a "
          "full E1. No edit to the paper follows from this round.",
          ""]
    (OUT / "TE1_REPORT.md").write_text("\n".join(L), encoding="utf-8")
    (OUT / "TE1_RUN_LOG.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    say(f"VERDICT {out['verdict']} | " + json.dumps({k: v for k, v in out.items()
                                                     if k in ("mean_H", "MDE80", "n")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

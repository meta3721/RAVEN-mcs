"""City Scanner forward scores under three region-weight vectors (inference only).

Protocol: the execution prompt "City Scanner forward scores under three target weights"
(attachment, 2026-10-02).  Evaluates the 50 frozen checkpoints (5 arms x 10 seeds) once
each on the 2,090 test units and scores the SAME predictions under three length-4
region-weight vectors:

    run : CS_PHI_DECISION.json['mu']            (the block's own test-region share)
    M1  : ACS 2021 B01003 population marginals  (MAP_MARGINALS.csv, map=M1)
    M2  : NYC 311 demand marginals              (MAP_MARGINALS.csv, map=M2)

Scoring uses the published path only: _predict, _mu_weights_for_test, rmse_mu.
No training, no src/ edits, no manuscript edits, no writes outside
results_exogenous_target/round_v1/ (and nothing already on disk there is overwritten).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import types

import numpy as np
import pandas as pd
import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from raven_mcs.e3.real_runner.runner import _mu_weights_for_test, _predict  # noqa: E402
from raven_mcs.metrics.accuracy import rmse_mu                               # noqa: E402
from raven_mcs.models.common_ndmf import deterministic_common_ndmf          # noqa: E402
import run_nodesign_supplement as nss                                       # noqa: E402

RUNS = ROOT / "results_c1_cityscanner/round_v1/runs/cityscanner_nyc_pm25"
ROUND = ROOT / "results_c1_cityscanner/round_v1"
OUT = ROOT / "results_exogenous_target/round_v1"
ARMS = ("fedavg_window", "twostage_hajek", "fedau_window", "obsuse_window", "raven")
SEEDS = list(range(32001, 32011))
N_TEST_EXPECTED = 2090
REPRO_TOL = 1e-6
WG_TOL = 1e-8
# expected vectors from the execution prompt: cross-check only, never a source
EXPECTED = {
    "run": (0.23732057416267943, 0.47464114832535886, 0.0708133971291866, 0.21722488038277513),
    "M1": (0.30607816093394624, 0.367698221016265, 0.06125064169088319, 0.2649729763589055),
    "M2": (0.21684976820757978, 0.3991468881250436, 0.04379795668554715, 0.34020538698182945),
}


def load_weights(ds) -> dict[str, np.ndarray]:
    decision = json.loads((ROUND / "CS_PHI_DECISION.json").read_text(encoding="utf-8"))
    setup = json.loads((ROUND / "CS_TRAIN_SETUP.json").read_text(encoding="utf-8"))
    enc = {str(k): int(v) for k, v in setup["h_encoding"].items()}
    ds_enc = {str(g): int(i) for g, i in ds._target_group_str_to_int.items()}
    if enc != ds_enc:
        raise SystemExit(f"STOP: h_encoding {enc} != dataset encoding {ds_enc}")
    order = [name for name, _ in sorted(enc.items(), key=lambda kv: kv[1])]

    mu_run_file = np.asarray([float(decision["mu"][r]) for r in order], dtype=np.float64)
    mu_run_setup = np.asarray([float(v) for v in setup["mu"]], dtype=np.float64)
    if np.max(np.abs(mu_run_file - mu_run_setup)) > 1e-12:
        raise SystemExit("STOP: CS_PHI_DECISION.mu != CS_TRAIN_SETUP.mu beyond 1e-12")

    marg = pd.read_csv(OUT / "MAP_MARGINALS.csv")
    out = {"run": mu_run_file}
    for name in ("M1", "M2"):
        sub = marg[(marg["map"] == name) & marg["region"].notna()]
        vals = {str(r["region"]): float(r["pi_sum"]) for _, r in sub.iterrows()}
        out[name] = np.asarray([vals[r] for r in order], dtype=np.float64)
    for name, vec in out.items():
        if abs(float(vec.sum()) - 1.0) > 1e-12:
            raise SystemExit(f"STOP: weight vector {name} sums to {vec.sum()}")
        exp = np.asarray(EXPECTED[name], dtype=np.float64)
        if np.max(np.abs(vec - exp)) > 1e-12:
            raise SystemExit(f"STOP: {name} {vec} != expected {exp}")
    return out


def region_rmse(pred: dict, gid: int) -> float:
    m = pred["groups"] == gid
    if not m.any():
        return float("nan")
    d = pred["y_pred"][m] - pred["y_true"][m]
    return float(np.sqrt(np.mean(d ** 2)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-only", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    ds, _, _ = nss._load_cityscanner()
    n_test = len(ds.get_atomic_units(split="test"))
    if n_test != N_TEST_EXPECTED:
        raise SystemExit(f"STOP: test units {n_test} != {N_TEST_EXPECTED}")
    weights = load_weights(ds)
    print("weights:", {k: [round(float(x), 12) for x in v] for k, v in weights.items()})
    print("test units:", n_test)

    rows, max_repro, state_keys, model_cls = [], 0.0, None, None
    for arm in ARMS:
        for seed in SEEDS:
            run_dir = RUNS / arm / f"seed{seed}"
            ckpt = run_dir / "checkpoints" / "final.pt"
            accepted = json.loads((run_dir / "CS_ACCEPTED.json").read_text(encoding="utf-8"))
            obj = torch.load(ckpt, map_location="cpu", weights_only=False)
            if not (isinstance(obj, dict) and obj and all(isinstance(v, torch.Tensor) for v in obj.values())):
                raise SystemExit(f"STOP: {ckpt} is not a bare state_dict (type {type(obj)})")
            model = deterministic_common_ndmf(ds.num_spatial, seed=seed)
            model.load_state_dict(obj)
            pred = _predict(types.SimpleNamespace(model=model), ds, split="test")
            if len(pred["y_true"]) != n_test:
                raise SystemExit(f"STOP: predicted {len(pred['y_true'])} != {n_test}")
            r_by_region = [region_rmse(pred, g) for g in range(4)]
            wg = float(np.nanmax(r_by_region))
            scores = {}
            for name, vec in weights.items():
                mu_w = _mu_weights_for_test(pred, vec)
                scores[name] = float(rmse_mu(pred["y_pred"], pred["y_true"], mu_w))
            repro = abs(scores["run"] - float(accepted["RMSE_mu"]))
            max_repro = max(max_repro, repro)
            state_keys = len(obj)
            model_cls = type(model).__name__
            wg_spread = max(abs(wg - (wg if name == "run" else wg)) for name in weights)
            wg_spread = max(abs(float(np.nanmax([region_rmse(pred, g) for g in range(4)])) - wg) for _ in [0])
            rows.append({"arm": arm, "seed": seed, "n_test": len(pred["y_true"]),
                         "RMSE_run": scores["run"], "RMSE_M1": scores["M1"], "RMSE_M2": scores["M2"],
                         "WG_run": wg, "WG_M1": wg, "WG_M2": wg,
                         "RMSE_R0": r_by_region[0], "RMSE_R1": r_by_region[1],
                         "RMSE_R2": r_by_region[2], "RMSE_R3": r_by_region[3],
                         "repro_abs_diff": repro})
            print(f"{arm:16s} seed{seed} RMSE_run={scores['run']:.9f} repro={repro:.3e} "
                  f"M1={scores['M1']:.9f} M2={scores['M2']:.9f} WG={wg:.9f}")
            if arm == "fedavg_window" and seed == 32001 and repro > REPRO_TOL:
                raise SystemExit(f"STOP: reproduction gate failed, |diff|={repro:.6e} > {REPRO_TOL}")
            if repro > REPRO_TOL:
                raise SystemExit(f"STOP: seed {arm}/{seed} reproduction failed, |diff|={repro:.6e}")
    if args.gate_only:
        print(f"gate-only: max repro diff {max_repro:.3e}")
        return

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "ENDPOINT_TABLE.csv", index=False)
    summary = {}
    for name in weights:
        means = df.groupby("arm")[f"RMSE_{name}"].mean().sort_values()
        fed = df[df["arm"] == "fedavg_window"].set_index("seed")[f"RMSE_{name}"]
        per_arm = {}
        for arm in ARMS:
            if arm == "fedavg_window":
                continue
            a = df[df["arm"] == arm].set_index("seed")[f"RMSE_{name}"]
            rel = ((a - fed) / fed).to_numpy()
            per_arm[arm] = {"paired_rel_mean": float(np.mean(rel)),
                            "seeds_smaller_than_fedavg": int((a < fed).sum())}
        summary[name] = {"ranking": list(means.index), "means": {k: float(v) for k, v in means.items()},
                         "vs_fedavg": per_arm}
    identical = len({tuple(summary[n]["ranking"]) for n in weights}) == 1
    wg_spread = float(np.max(np.abs(df[["WG_run", "WG_M1", "WG_M2"]].to_numpy()
                                     - df[["WG_run"]].to_numpy())))
    payload = {"weights": {k: [float(x) for x in v] for k, v in weights.items()},
               "weight_source": {"run": "CS_PHI_DECISION.json.mu (cross-checked against CS_TRAIN_SETUP.json.mu)",
                                 "M1": "MAP_MARGINALS.csv map=M1 region rows",
                                 "M2": "MAP_MARGINALS.csv map=M2 region rows"},
               "n_test": n_test, "max_repro_abs_diff": max_repro,
               "model_class": model_cls, "state_dict_keys": state_keys,
               "n_rows": int(len(df)), "wg_max_spread": wg_spread,
               "rankings_identical": bool(identical), "summary": summary}
    (OUT / "ENDPOINT_TABLE.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"max_repro_abs_diff": max_repro, "rankings_identical": identical,
                      "wg_max_spread": wg_spread,
                      "means": {n: summary[n]["means"] for n in summary}}, indent=2))


if __name__ == "__main__":
    main()

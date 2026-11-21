"""Path A: support-compatible Design. Diagnostic, then VAL training only."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TAB = OUT / "tables"
RUNS = OUT / "runs"
E3_ET = ROOT / "artifacts" / "e3_formal_runs_r1" / "eventtraces"
E3 = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs"
E4 = ROOT / "artifacts" / "e4_core_mechanism_ablation_r1" / "runs"

DATASETS = ("sensorscope", "uair")
VAL_SEEDS = list(range(30001, 30011))
TEST_SEEDS = list(range(30011, 30021))
ALL_SEEDS = VAL_SEEDS + TEST_SEEDS
PRIMARY = ("Delta_group", "RMSE_mu", "Tail_RMSE")
NONINF = -0.5


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sealed(dataset: str, method: str, seed: int) -> Path:
    if method == "raven_wo_design":
        return E4 / dataset / method / f"seed{seed}"
    return E3 / dataset / method / f"seed{seed}"


def _pct(new: float, ref: float) -> float:
    if ref is None or not np.isfinite(ref) or abs(float(ref)) < 1e-15:
        return float("nan")
    return 100.0 * (float(new) - float(ref)) / float(ref)


def _prepare(dataset: str):
    from raven_mcs.correction.pi_target import (
        build_pi_target,
        build_pi_target_support_compatible,
    )
    from raven_mcs.e3.canary.dataset_load import load_spatial_to_client
    from raven_mcs.e3.real_runner.generator_r3 import build_joint_pi_opp
    from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum

    atomic = pd.read_parquet(ROOT / "data" / "processed" / dataset / "atomic_units.parquet")
    atomic_sealed, _ = apply_sealed_opportunity_stratum(atomic, dataset=dataset, root=ROOT)
    mapping = load_spatial_to_client(ROOT, dataset)
    atomic_for_pi = atomic_sealed.copy()
    if "target_group_main" not in atomic_for_pi.columns:
        atomic_for_pi["target_group_main"] = atomic_for_pi["target_group"].astype(str)
    train = atomic_sealed.loc[atomic_sealed["split"].astype(str) == "train"]
    strata_by_client: dict[str, list[str]] = {}
    for r in train.itertuples(index=False):
        c = mapping.get(str(r.spatial_id))
        if c is None:
            continue
        strata_by_client.setdefault(c, []).append(str(r.opportunity_stratum))
    for c in strata_by_client:
        strata_by_client[c] = sorted(set(strata_by_client[c]))
    pi_opp = build_joint_pi_opp(sorted(strata_by_client), strata_by_client)
    test = build_pi_target(atomic_for_pi, mapping, split="test")
    sc = build_pi_target_support_compatible(
        atomic_for_pi, mapping, split="test", pi_opp_joint=pi_opp
    )
    test_map = {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in test.itertuples()
    }
    sc_map = {
        (str(r.client_id), str(r.opportunity_stratum)): float(r.pi_k_s_tar)
        for r in sc.itertuples()
    }
    return {
        "mapping": mapping,
        "unit_stratum": {
            str(r.unit_id): str(r.opportunity_stratum)
            for r in atomic_sealed.itertuples(index=False)
        },
        "pi_test": test_map,
        "pi_sc": sc_map,
        "pi_opp": pi_opp,
    }


def diagnose() -> pd.DataFrame:
    from raven_mcs.simulation.event_trace import load_event_trace

    rows = []
    for dataset in DATASETS:
        ctx = _prepare(dataset)
        n_zero_test = 0
        n_zero_sc = 0
        n_units = 0
        same_ar = []
        for seed in ALL_SEEDS:
            trace, _ = load_event_trace(
                E3_ET / dataset / f"seed{seed}" / "training_eventtrace"
            )
            events = trace.events
            for window_id, recs in events.groupby("window_id"):
                ar_test = []
                ar_sc = []
                for rec in recs.itertuples(index=False):
                    cid = str(rec.client_id)
                    risk = list(rec.risk_set_unit_ids or [])
                    obs = set(str(x) for x in (rec.observed_unit_ids or []))
                    o = np.asarray(
                        [1.0 if str(u) in obs else 0.0 for u in risk], dtype=np.float64
                    )
                    strata = [
                        ctx["unit_stratum"].get(str(u), "unknown") for u in risk
                    ]
                    z_test = np.asarray(
                        [ctx["pi_test"].get((cid, s), 0.0) for s in strata],
                        dtype=np.float64,
                    )
                    z_sc = np.asarray(
                        [ctx["pi_sc"].get((cid, s), 0.0) for s in strata],
                        dtype=np.float64,
                    )
                    n_units += len(risk)
                    n_zero_test += int(np.sum(z_test <= 0.0))
                    n_zero_sc += int(np.sum(z_sc <= 0.0))
                    if int(rec.U) == 1:
                        if float((o * np.maximum(z_test, 0.0)).sum()) > 0:
                            ar_test.append(cid)
                        if float((o * np.maximum(z_sc, 0.0)).sum()) > 0:
                            ar_sc.append(cid)
                same_ar.append(set(ar_test) == set(ar_sc))
        rows.append(
            {
                "dataset": dataset,
                "n_risk_units": n_units,
                "frac_pi_test_zero": n_zero_test / n_units if n_units else float("nan"),
                "frac_pi_sc_zero": n_zero_sc / n_units if n_units else float("nan"),
                "same_ar_test_vs_sc": float(np.mean(same_ar)) if same_ar else float("nan"),
            }
        )
    return pd.DataFrame(rows)


def _train_one(dataset: str, seed: int) -> dict:
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
    from raven_mcs.e3.real_runner.runner import run_e3_real

    run_dir = RUNS / dataset / "raven_sc_target" / f"seed{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    marker = run_dir / "final_metrics.json"
    if marker.is_file():
        return {"dataset": dataset, "seed": seed, "status": "REUSED", **_load_json(marker)}
    ds = load_paper_dataset(ROOT, dataset)
    mapping = load_spatial_to_client(ROOT, dataset)
    result = run_e3_real(
        root=ROOT,
        run_dir=run_dir,
        dataset=ds,
        method="raven",
        seed=int(seed),
        eventtrace_dir=E3_ET / dataset / f"seed{seed}" / "training_eventtrace",
        spatial_to_client=mapping,
        dataset_name=dataset,
        local_steps=2,
        pi_target_mode="support_compatible",
        source_identity={"note": "post_review_G1_path_A_scl"},
    )
    metrics = result.get("metrics") or _load_json(marker)
    row = {"dataset": dataset, "seed": seed, "status": result.get("status")}
    row.update({k: metrics.get(k) for k in PRIMARY + ("Delta_c_s", "ESS", "clip_rate_stage1")})
    return row


def collect_split(seeds: list[int]) -> pd.DataFrame:
    rows = []
    for dataset in DATASETS:
        for seed in seeds:
            sc_path = RUNS / dataset / "raven_sc_target" / f"seed{seed}" / "final_metrics.json"
            if not sc_path.is_file():
                continue
            sc = _load_json(sc_path)
            raven = _load_json(_sealed(dataset, "raven", seed) / "final_metrics.json")
            off = _load_json(_sealed(dataset, "raven_wo_design", seed) / "final_metrics.json")
            row = {"dataset": dataset, "seed": seed}
            for key in PRIMARY + ("Delta_c_s",):
                row[f"sc_{key}"] = sc.get(key)
                row[f"raven_{key}"] = raven.get(key)
                row[f"off_{key}"] = off.get(key)
                row[f"sc_vs_off_{key}_pct"] = _pct(sc.get(key), off.get(key))
                row[f"sc_vs_raven_{key}_pct"] = _pct(sc.get(key), raven.get(key))
            rows.append(row)
    return pd.DataFrame(rows)


def val_gate(val: pd.DataFrame) -> dict:
    checks = []
    u = val[val.dataset == "uair"]
    s = val[val.dataset == "sensorscope"]
    for key in PRIMARY:
        mean_pct = float(u[f"sc_vs_off_{key}_pct"].mean())
        checks.append(
            {
                "rule": f"uair_{key}_vs_nodesign",
                "value": mean_pct,
                "pass": mean_pct >= NONINF,
            }
        )
    dcs = float(u["sc_vs_off_Delta_c_s_pct"].mean())
    checks.append(
        {
            "rule": "uair_delta_cs_still_le_nodesign",
            "value": dcs,
            "pass": float(u["sc_Delta_c_s"].mean()) <= float(u["off_Delta_c_s"].mean()),
        }
    )
    for key in ("Delta_group", "Delta_c_s"):
        mean_pct = float(s[f"sc_vs_raven_{key}_pct"].mean())
        checks.append(
            {
                "rule": f"sensorscope_{key}_vs_raven",
                "value": mean_pct,
                "pass": mean_pct >= NONINF,
            }
        )
    ok = all(c["pass"] for c in checks)
    return {
        "verdict": "VALGATE_SOLVES" if ok else "PATH_A_FAILS",
        "n_uair": int(len(u)),
        "n_sensorscope": int(len(s)),
        "checks": checks,
    }


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    print("diagnose support")
    diag = diagnose()
    diag.to_csv(TAB / "support_diagnostic.csv", index=False)
    print(diag.to_string(index=False))

    print("train VAL seeds")
    train_rows = []
    for dataset in DATASETS:
        for seed in VAL_SEEDS:
            print(f"  {dataset} {seed}", flush=True)
            train_rows.append(_train_one(dataset, seed))
    pd.DataFrame(train_rows).to_csv(TAB / "val_train_status.csv", index=False)

    val = collect_split(VAL_SEEDS)
    val.to_csv(TAB / "val_contrast.csv", index=False)
    gate = val_gate(val)
    (OUT / "VAL_GATE.json").write_text(json.dumps(gate, indent=2), encoding="utf-8")
    print(json.dumps(gate, indent=2))
    if gate["verdict"] != "VALGATE_SOLVES":
        (OUT / "DECISION.md").write_text(
            "# Path A val decision\n\n**PATH_A_FAILS**. Do not open TEST. "
            "Recommend Path B (dataset-gated Design).\n",
            encoding="utf-8",
        )
        return
    (OUT / "DECISION.md").write_text(
        "# Path A val decision\n\n**VALGATE_SOLVES**. TEST look is now authorized "
        "as a single report, no retuning.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

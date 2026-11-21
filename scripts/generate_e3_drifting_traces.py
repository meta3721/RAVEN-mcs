#!/usr/bin/env python3
"""Generate E3-isomorphic drifting EventTraces (isolated from sealed complete_aligned).

No sealed drifting traces exist. Formal E3 traces are complete_aligned only.
This uses the same R3 generator, seeds 30001-30020, sealed strata, and window
horizon, with drifting.yaml opportunity drift (period=50, magnitude=0.1).
Writes artifacts/e3_drifting_r1/eventtraces/{dataset}/seed{seed}/.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from raven_mcs.e3.canary.constants import M_MC
from raven_mcs.e3.canary.dataset_load import (
    load_horizon,
    load_paper_dataset,
    load_spatial_to_client,
)
from raven_mcs.e3.formal.constants import FORMAL_SEEDS
from raven_mcs.e3.real_runner.generator_r3 import materialize_r3_trace
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
from raven_mcs.utils.serialization import dump_json, load_yaml

OUT_ART = _ROOT / "artifacts" / "e3_drifting_r1"
DATASETS = ("sensorscope", "uair")
SCENARIO_YAML = _ROOT / "configs" / "scenario" / "drifting.yaml"


def generate_one(dataset: str, seed: int, *, force: bool = False) -> dict:
    out = OUT_ART / "eventtraces" / dataset / f"seed{seed}"
    identity_path = out / "training_eventtrace" / "trace_identity.json"
    if identity_path.is_file() and not force:
        identity = json.loads(identity_path.read_text(encoding="utf-8"))
        return {"status": "REUSED", "dataset": dataset, "seed": seed, "hash": identity.get("trace_hash")}
    cfg = load_yaml(SCENARIO_YAML)
    ds = load_paper_dataset(_ROOT, dataset)
    mapping = load_spatial_to_client(_ROOT, dataset)
    atomic, stratum_meta = apply_sealed_opportunity_stratum(
        ds.atomic_df, dataset=dataset, root=_ROOT
    )
    horizon = load_horizon(_ROOT, dataset)
    n_windows = int(horizon["chosen_E3_formal_windows"])
    mat = materialize_r3_trace(
        dataset=dataset,
        atomic=atomic,
        spatial_to_client=mapping,
        out_dir=out,
        seed=int(seed),
        num_windows=n_windows,
        m_mc=M_MC,
        delivery_mode="nominal",
        drift_period=int(cfg.get("drift_period") or 0) or None,
        drift_magnitude=float(cfg.get("drift_magnitude") or 0.0),
    )
    dump_json(
        {
            "scenario": "drifting",
            "stratum_meta": stratum_meta,
            "num_windows": n_windows,
            "m_mc": M_MC,
            "drift_period": cfg.get("drift_period"),
            "drift_magnitude": cfg.get("drift_magnitude"),
            "note": "R3 complete_aligned protocol + opportunity drift; not a sealed formal trace",
        },
        out / "generation_meta.json",
    )
    identity = (mat.get("identity") or {})
    return {
        "status": "CREATED",
        "dataset": dataset,
        "seed": seed,
        "hash": identity.get("trace_hash"),
        "audit": mat.get("audit"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=["sensorscope", "uair", "all"], default="all")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--start-seed", type=int, default=None)
    parser.add_argument("--end-seed", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    datasets = DATASETS if args.dataset == "all" else (args.dataset,)
    if args.seed is not None:
        seeds = [args.seed]
    elif args.start_seed is not None or args.end_seed is not None:
        start = int(args.start_seed or FORMAL_SEEDS[0])
        end = int(args.end_seed or FORMAL_SEEDS[-1])
        seeds = [s for s in FORMAL_SEEDS if start <= s <= end]
    else:
        seeds = list(FORMAL_SEEDS)
    OUT_ART.mkdir(parents=True, exist_ok=True)
    rows = []
    for dataset in datasets:
        for seed in seeds:
            print(f"START trace {dataset} seed{seed}", flush=True)
            row = generate_one(dataset, seed, force=args.force)
            print(f"DONE {row['status']} {dataset} seed{seed} hash={row.get('hash')}", flush=True)
            rows.append(row)
    (OUT_ART / "trace_ledger.json").write_text(
        json.dumps({"scenario": "drifting", "rows": rows}, indent=2),
        encoding="utf-8",
    )
    print(f"OK {len(rows)} traces", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

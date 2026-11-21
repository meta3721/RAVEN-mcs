"""Central-All / Central-Delivered on real dataset + EventTrace records."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch import nn

from raven_mcs.data.processed_dataset import ProcessedDataset
from raven_mcs.models.common_ndmf import CommonNDMF
from raven_mcs.utils.hashing import sha256_json
from raven_mcs.utils.serialization import dump_json


def _train_ids_all(dataset: ProcessedDataset) -> list[str]:
    return (
        dataset.atomic_df.loc[dataset.atomic_df["split"].astype(str) == "train", "unit_id"]
        .astype(str)
        .tolist()
    )


def _train_ids_delivered(events: pd.DataFrame, dataset: ProcessedDataset) -> list[str]:
    """Exact delivered atomic unit IDs under EventTrace (U=1 observed units), train split only."""
    train = set(_train_ids_all(dataset))
    delivered: list[str] = []
    for _, row in events.iterrows():
        if int(row["U"]) != 1:
            continue
        obs = row["observed_unit_ids"]
        if isinstance(obs, str):
            import json

            obs = json.loads(obs)
        for uid in obs or []:
            uid = str(uid)
            if uid in train:
                delivered.append(uid)
    # Frozen dedup: unique preserve order
    seen = set()
    out = []
    for uid in delivered:
        if uid not in seen:
            seen.add(uid)
            out.append(uid)
    return out


def run_central_real(
    *,
    run_dir: Path,
    method: str,
    dataset: ProcessedDataset,
    events: pd.DataFrame,
    seed: int,
    local_steps: int = 30,
    lr: float = 1e-3,
) -> dict[str, Any]:
    if method not in {"central_all", "central_delivered"}:
        raise ValueError(method)
    run_dir = Path(run_dir)
    ckpt_dir = run_dir / "checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    if method == "central_all":
        unit_ids = _train_ids_all(dataset)
        protocol = "all legally available training atomic units"
    else:
        unit_ids = _train_ids_delivered(events, dataset)
        protocol = "exact EventTrace delivered (U=1) train atomic units; no Bernoulli resample"

    if not unit_ids:
        raise RuntimeError(f"{method}: empty training unit set")

    # Build tensors from real units using the SAME extract_features as federated
    # ClientTrainer / eval (_predict). Previously Central used raw time_index as
    # trend while federated training normalized it — PREPROCESSING_CONSISTENCY_FIX.
    from raven_mcs.models.features import extract_features

    spatial_ids: list[str] = []
    abs_times: list[float] = []
    time_idx: list[int] = []
    targets = []
    for uid in unit_ids:
        unit = dataset.get_atomic_by_id(uid)
        if unit is None or unit.split != "train":
            raise RuntimeError(f"illegal unit in central training: {uid}")
        spatial_ids.append(str(unit.spatial_id))
        abs_times.append(float(unit.absolute_time))
        time_idx.append(int(unit.time_index))
        targets.append(float(unit.target_value))

    spatial_to_idx = {str(sid): int(i) for sid, i in dataset._spatial_to_idx.items()}
    total_slots = int(dataset.atomic_df["time_index"].max()) + 1
    spatial_t, hour_t, weekday_t, trend_t = extract_features(
        spatial_ids, abs_times, time_idx, spatial_to_idx, total_slots
    )

    torch.manual_seed(int(seed))
    np.random.seed(int(seed))
    model = CommonNDMF(num_spatial=int(dataset.num_spatial))
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    y = torch.as_tensor(targets, dtype=torch.float32)
    n = len(unit_ids)
    losses = []
    model.train()
    for _ in range(int(local_steps)):
        idx = torch.randint(0, n, (min(32, n),))
        pred = model(spatial_t[idx], hour_t[idx], weekday_t[idx], trend_t[idx])
        loss = nn.functional.mse_loss(pred, y[idx])
        opt.zero_grad()
        loss.backward()
        opt.step()
        losses.append(float(loss.detach().cpu()))

    torch.save({"state_dict": model.state_dict(), "method": method, "seed": int(seed)}, ckpt_dir / "final.pt")
    summary = {
        "method": method,
        "protocol": protocol,
        "n_train_units": n,
        "train_unit_ids_hash": sha256_json(unit_ids),
        "train_unit_ids": unit_ids,
        "uses_test_targets": False,
        "bernoulli_resample": False,
        "final_train_loss": losses[-1] if losses else None,
        "steps": int(local_steps),
        "status": "CENTRAL_REALDATA_READY",
    }
    dump_json(summary, run_dir / "central_train_summary.json")
    return summary

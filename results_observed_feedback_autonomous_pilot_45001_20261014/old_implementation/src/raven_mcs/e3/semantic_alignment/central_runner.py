"""Central-All / Central-Delivered through the unified E3 runner framework."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch

from raven_mcs.e3.protocol_closure.central_reference import CentralTrainConfig, train_central_reference
from raven_mcs.utils.serialization import dump_json


def _delivered_mask_from_events(events: pd.DataFrame, n_rows: int) -> np.ndarray:
    """Build a delivered mask over synthetic train rows from EventTrace U=1 fractions."""
    u_rate = float(events["U"].astype(float).mean()) if len(events) else 0.5
    rng = np.random.default_rng(0)
    return rng.random(n_rows) < max(u_rate, 0.05)


def run_central_e3(
    *,
    run_dir: Path,
    method: str,
    events: pd.DataFrame,
    seed: int,
    n_train: int = 128,
    num_spatial: int = 8,
) -> dict[str, Any]:
    """Train Central reference on synthetic train-only tensors (no test labels)."""
    if method not in {"central_all", "central_delivered"}:
        raise ValueError(method)
    run_dir = Path(run_dir)
    ckpt_dir = run_dir / "checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(int(seed))
    spatial = rng.integers(0, num_spatial, size=n_train)
    hour = rng.integers(0, 24, size=n_train).astype(float)
    weekday = rng.integers(0, 7, size=n_train).astype(float)
    trend = np.linspace(0, 1, n_train)
    # Synthetic targets — not real dataset test labels
    targets = np.sin(hour / 24.0 * 2 * np.pi) + 0.1 * rng.normal(size=n_train)
    delivered = _delivered_mask_from_events(events, n_train) if method == "central_delivered" else None

    out = train_central_reference(
        spatial_index=spatial,
        hour=hour,
        weekday=weekday,
        trend=trend,
        targets=targets,
        delivered_mask=delivered,
        config=CentralTrainConfig(mode=method, seed=int(seed), local_steps=20, num_spatial=num_spatial),
    )
    # Persist a tiny checkpoint tensor for hashability (not a performance model claim)
    torch.save({"seed": int(seed), "method": method, "status": out["status"]}, ckpt_dir / "final.pt")
    dump_json(out, run_dir / "central_train_summary.json")
    out["train_mse_proxy"] = out.get("final_train_loss")
    out["train_mae_proxy"] = None
    out["uses_test_targets"] = False
    out["status"] = "CENTRAL_RUNNER_READY"
    return out

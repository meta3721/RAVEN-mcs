"""Minimal faithful Central-All / Central-Delivered reference training."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import torch
from torch import nn

from raven_mcs.models.common_ndmf import CommonNDMF

Mode = Literal["central_all", "central_delivered"]


@dataclass(frozen=True)
class CentralTrainConfig:
    mode: Mode
    seed: int
    local_steps: int = 50
    lr: float = 1e-3
    batch_size: int = 64
    num_spatial: int = 8


def _set_seed(seed: int) -> None:
    np.random.seed(int(seed))
    torch.manual_seed(int(seed))


def select_training_indices(
    *,
    mode: Mode,
    n: int,
    delivered_mask: np.ndarray | None,
) -> np.ndarray:
    idx = np.arange(int(n), dtype=np.int64)
    if mode == "central_all":
        return idx
    if delivered_mask is None:
        raise ValueError("central_delivered requires delivered_mask from EventTrace")
    mask = np.asarray(delivered_mask, dtype=bool)
    if len(mask) != n:
        raise ValueError("delivered_mask length mismatch")
    if not mask.any():
        raise ValueError("central_delivered has zero delivered rows")
    return idx[mask]


def train_central_reference(
    *,
    spatial_index: np.ndarray,
    hour: np.ndarray,
    weekday: np.ndarray,
    trend: np.ndarray,
    targets: np.ndarray,
    delivered_mask: np.ndarray | None,
    config: CentralTrainConfig,
) -> dict[str, Any]:
    """Train Common-NDMF centrally on train-only tensors. No test targets used."""
    _set_seed(config.seed)
    n = len(targets)
    keep = select_training_indices(mode=config.mode, n=n, delivered_mask=delivered_mask)
    spatial = torch.as_tensor(np.asarray(spatial_index)[keep], dtype=torch.long)
    hour_t = torch.as_tensor(np.asarray(hour)[keep], dtype=torch.float32)
    weekday_t = torch.as_tensor(np.asarray(weekday)[keep], dtype=torch.float32)
    trend_t = torch.as_tensor(np.asarray(trend)[keep], dtype=torch.float32)
    y = torch.as_tensor(np.asarray(targets)[keep], dtype=torch.float32)
    model = CommonNDMF(num_spatial=int(config.num_spatial))
    opt = torch.optim.Adam(model.parameters(), lr=config.lr)
    n_keep = int(spatial.shape[0])
    losses: list[float] = []
    model.train()
    for _ in range(int(config.local_steps)):
        batch = torch.randint(0, n_keep, (min(config.batch_size, n_keep),))
        pred = model(spatial[batch], hour_t[batch], weekday_t[batch], trend_t[batch])
        loss = nn.functional.mse_loss(pred, y[batch])
        opt.zero_grad()
        loss.backward()
        opt.step()
        losses.append(float(loss.detach().cpu()))
    return {
        "mode": config.mode,
        "seed": int(config.seed),
        "n_train_rows": n_keep,
        "steps": int(config.local_steps),
        "final_train_loss": float(losses[-1]) if losses else None,
        "uses_raven_only_state": False,
        "deterministic_seed": True,
        "backbone": "CommonNDMF",
        "status": "CENTRAL_REFERENCE_IMPLEMENTATION_READY",
    }


def central_protocol_spec() -> dict[str, Any]:
    return {
        "central_all": {
            "data_access": "all legally available training atomic units (split=train, no test targets)",
            "optimization_budget": "same backbone Common-NDMF; predeclared step budget per run",
            "same_model_backbone": True,
            "same_preprocessing": True,
            "same_train_test_split": True,
            "no_target_leakage": True,
            "table_role": "REFERENCE_ONLY",
            "checkpoint_policy": "write final.pt under run_dir/checkpoints",
            "runtime_accounting": "wall-clock of centralized SGD only",
        },
        "central_delivered": {
            "data_access": "only delivered/usable observations implied by frozen EventTrace (U=1 observed units)",
            "optimization_budget": "same backbone Common-NDMF; predeclared step budget per run",
            "same_model_backbone": True,
            "same_preprocessing": True,
            "same_train_test_split": True,
            "no_target_leakage": True,
            "table_role": "REFERENCE_ONLY",
            "checkpoint_policy": "write final.pt under run_dir/checkpoints",
            "runtime_accounting": "wall-clock of centralized SGD only",
        },
        "status": "CENTRAL_REFERENCE_READY",
        "implementation": "raven_mcs.e3.protocol_closure.central_reference.train_central_reference",
    }

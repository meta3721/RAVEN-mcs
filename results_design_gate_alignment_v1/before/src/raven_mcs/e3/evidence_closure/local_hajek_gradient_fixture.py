"""Deterministic gradient-level proof for the differentiable local Hájek loss."""

from __future__ import annotations

import hashlib
from typing import Any

import torch

from raven_mcs.training.local_objective import local_hajek_loss


def _hash(value: torch.Tensor) -> str:
    return hashlib.sha256(value.detach().cpu().numpy().tobytes()).hexdigest()


def run_fixture() -> dict[str, Any]:
    """Compare an equal-weight objective to unequal normalized Hájek weights."""
    torch.manual_seed(0)
    x = torch.tensor([[1.0], [3.0]], dtype=torch.float64)
    y = torch.tensor([0.0, 1.0], dtype=torch.float64)
    initial = torch.tensor([[0.25]], dtype=torch.float64)
    weights = torch.tensor([0.2, 0.8], dtype=torch.float64)
    uniform = torch.full_like(weights, 0.5)

    def evaluate(weight: torch.Tensor) -> tuple[float, torch.Tensor, torch.Tensor]:
        parameter = initial.clone().requires_grad_(True)
        prediction = (x @ parameter).reshape(-1)
        loss = local_hajek_loss(prediction, y, weight)
        loss.backward()
        gradient = parameter.grad.detach().clone()
        after = (parameter.detach() - 0.1 * gradient).clone()
        return float(loss.detach()), gradient, after

    fedavg_loss, fedavg_gradient, fedavg_after = evaluate(uniform)
    hajek_loss, hajek_gradient, hajek_after = evaluate(weights)
    distinct_gradient = not torch.allclose(fedavg_gradient, hajek_gradient, atol=1e-12, rtol=0.0)
    distinct_parameter = not torch.allclose(fedavg_after, hajek_after, atol=1e-12, rtol=0.0)
    return {
        "status": "PASS" if distinct_gradient and distinct_parameter else "FAIL",
        "input_batch": {"x": x.tolist(), "targets": y.tolist()},
        "weights": weights.tolist(),
        "denominator": float(weights.sum()),
        "fedavg_loss": fedavg_loss,
        "local_hajek_loss": hajek_loss,
        "gradient_hashes": {"fedavg": _hash(fedavg_gradient), "local_hajek": _hash(hajek_gradient)},
        "parameter_hashes": {"fedavg_one_step": _hash(fedavg_after), "local_hajek_one_step": _hash(hajek_after)},
        "gradient_values": {"fedavg": fedavg_gradient.tolist(), "local_hajek": hajek_gradient.tolist()},
        "analytical_expectation": "Unequal normalized sample weights change the weighted squared-error gradient and one-step parameter.",
        "distinct_gradient": distinct_gradient,
        "distinct_parameter": distinct_parameter,
    }

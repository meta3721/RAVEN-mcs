"""Server rules for the conditional reference-projection screen.

P projects the corrected reference. U is uniform on the same support.
Neither calls the full P2 solver.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from w1_v51a_oracle import project_Cr


def constraint_residual(alpha: np.ndarray, a_bar: float, e_bar: float) -> dict[str, float]:
    vector = np.asarray(alpha, dtype=np.float64)
    return {
        "simplex": abs(float(vector.sum()) - 1.0),
        "negative": float(np.maximum(-vector, 0.0).max()) if vector.size else 0.0,
        "cap": float(np.maximum(vector - float(a_bar), 0.0).max()) if vector.size else 0.0,
        "ess": float(max(0.0, float(vector @ vector) - 1.0 / float(e_bar))),
    }


def max_residual(parts: dict[str, float]) -> float:
    return float(max(parts.values()) if parts else 0.0)


class UniformAggregator:
    name = "matched_uniform"

    def __init__(self) -> None:
        self.records: list[dict] = []

    def compute_server_weights(self, payload) -> np.ndarray:
        count = len(payload.client_ids)
        if count <= 0:
            raise RuntimeError("uniform aggregator received an empty active set")
        alpha = np.full(count, 1.0 / count, dtype=np.float64)
        self.records.append({"K": count, "kind": "uniform"})
        return alpha


class ReferenceProjectionAggregator:
    name = "reference_projection"

    def __init__(self) -> None:
        self.records: list[dict] = []

    def compute_server_weights(self, payload) -> np.ndarray:
        beta = np.asarray(payload.beta_hat, dtype=np.float64)
        count = int(beta.size)
        if count <= 0 or count != len(payload.client_ids):
            raise RuntimeError("projection received an empty or misaligned reference")
        if abs(float(beta.sum()) - 1.0) > 1e-8 or np.any(beta < -1e-12):
            raise RuntimeError("projection reference is not a probability vector")
        a_bar = min(1.0, max(0.5, 1.0 / count))
        e_bar = min(3.0, float(count))
        alpha, kind, _multipliers = project_Cr(beta, a_bar, e_bar)
        alpha = np.asarray(alpha, dtype=np.float64)
        parts = constraint_residual(alpha, a_bar, e_bar)
        objective = 0.5 * float(np.sum((alpha - beta) ** 2))
        self.records.append(
            {
                "K": count,
                "kind": str(kind),
                "a_bar": a_bar,
                "e_bar": e_bar,
                "objective": objective,
                "residual": max_residual(parts),
                "parts": parts,
                "beta": beta,
                "alpha": alpha,
            }
        )
        if max_residual(parts) > 1e-8:
            raise RuntimeError(f"projection constraint residual {max_residual(parts)}")
        return alpha

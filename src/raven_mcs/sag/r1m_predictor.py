"""AGGREGATE_COVERAGE_RIDGE_V1. Closed-form ridge; intercept unpenalized. Alpha frozen at 1.0."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from raven_mcs.sag.r1m_features import design_matrix, feature_vector
from raven_mcs.sag.r1m_spec import FEATURE_NAMES, PREDICTOR_ID, RIDGE_ALPHA, feature_spec_hash
from raven_mcs.utils.hashing import sha256_json


@dataclass(frozen=True)
class RidgeSnapshot:
    coef: tuple[float, ...]
    ridge_alpha: float
    pretest_mean: float
    n_fit: int
    fit_end_window: str
    block_id: int
    feature_spec_hash: str
    snapshot_hash: str
    predictor_id: str = PREDICTOR_ID

    def predict_row(self, x: np.ndarray) -> float:
        return float(np.dot(np.asarray(self.coef, dtype=np.float64), np.asarray(x, dtype=np.float64)))

    def predict(
        self,
        *,
        availability_level: float,
        history_c: Sequence[float],
        hour: int,
        weekend: bool,
    ) -> float:
        x = feature_vector(
            availability_level=availability_level,
            history_c=history_c,
            hour=hour,
            weekend=weekend,
            pretest_mean=self.pretest_mean,
        )
        return self.predict_row(x)


def _ridge_coef(X: np.ndarray, y: np.ndarray, alpha: float) -> np.ndarray:
    n, p = X.shape
    if n == 0:
        raise ValueError("empty design matrix")
    xtx = X.T @ X
    penalty = np.eye(p, dtype=np.float64)
    penalty[0, 0] = 0.0
    try:
        return np.linalg.solve(xtx + float(alpha) * penalty, X.T @ y)
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(xtx + float(alpha) * penalty, X.T @ y, rcond=None)[0]


def fit_ridge_snapshot(
    *,
    availability_level: float,
    completed_c: Sequence[float],
    hours: Sequence[int],
    weekends: Sequence[bool],
    pretest_mean: float,
    fit_end_window: str,
    block_id: int,
    ridge_alpha: float = RIDGE_ALPHA,
) -> RidgeSnapshot:
    if abs(float(ridge_alpha) - RIDGE_ALPHA) > 0:
        raise ValueError("ridge_alpha is frozen at 1.0")
    c = [float(x) for x in completed_c]
    if len(c) != len(hours) or len(c) != len(weekends):
        raise ValueError("completed series length mismatch")
    if not c:
        raise ValueError("R1M_INSUFFICIENT_PRETEST_HISTORY")
    records = []
    for i in range(len(c)):
        records.append((float(availability_level), c[:i], int(hours[i]), bool(weekends[i])))
    X = design_matrix(records, pretest_mean=float(pretest_mean))
    y = np.asarray(c, dtype=np.float64)
    coef = _ridge_coef(X, y, RIDGE_ALPHA)
    payload = {
        "predictor_id": PREDICTOR_ID,
        "coef": [float(v) for v in coef],
        "ridge_alpha": RIDGE_ALPHA,
        "n_fit": int(len(c)),
        "fit_end_window": str(fit_end_window),
        "block_id": int(block_id),
        "feature_spec_hash": feature_spec_hash(),
        "feature_names": list(FEATURE_NAMES),
    }
    return RidgeSnapshot(
        coef=tuple(float(v) for v in coef),
        ridge_alpha=RIDGE_ALPHA,
        pretest_mean=float(pretest_mean),
        n_fit=int(len(c)),
        fit_end_window=str(fit_end_window),
        block_id=int(block_id),
        feature_spec_hash=feature_spec_hash(),
        snapshot_hash=sha256_json(payload),
    )

"""L2 logistic presence predictor. Expanding-window, no oracle labels in X."""

from __future__ import annotations

from typing import Any

import numpy as np

from raven_mcs.sag.r1j_spec import LOGISTIC_C, NUM_TOL, RANDOM_STATE, RIDGE_SOLVER, predictor_spec_hash
from raven_mcs.utils.hashing import sha256_json


def _fit_logistic(X: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    y = y.astype(int)
    if len(y) < 8 or int(y.min()) == int(y.max()):
        prev = float(y.mean()) if len(y) else 0.5
        return {
            "kind": "prevalence",
            "p": float(np.clip(prev, 1e-6, 1.0 - 1e-6)),
            "coef": None,
            "intercept": None,
        }
    from sklearn.linear_model import LogisticRegression

    clf = LogisticRegression(
        penalty="l2",
        C=float(LOGISTIC_C),
        solver=RIDGE_SOLVER,
        max_iter=400,
        random_state=int(RANDOM_STATE),
    )
    clf.fit(X, y)
    return {
        "kind": "logit",
        "p": None,
        "coef": clf.coef_.astype(float).ravel().tolist(),
        "intercept": float(clf.intercept_.ravel()[0]),
        "n_iter": int(np.max(clf.n_iter_)),
    }


def predict_p(model: dict[str, Any], X: np.ndarray) -> np.ndarray:
    if model["kind"] == "prevalence":
        return np.full(len(X), float(model["p"]), dtype=np.float64)
    coef = np.asarray(model["coef"], dtype=np.float64)
    intercept = float(model["intercept"])
    z = X @ coef + intercept
    z = np.clip(z, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-z))


def hat_from_p(p: float, *, pi_safe: float, mean_mass: float) -> float:
    scale = max(float(pi_safe), float(mean_mass) if np.isfinite(mean_mass) else 0.0)
    return float(np.clip(p, 0.0, 1.0) * scale)


def model_fit_hash(model: dict[str, Any], *, n_train_windows: int, n_train_pairs: int) -> str:
    return sha256_json(
        {
            "spec": predictor_spec_hash(),
            "kind": model.get("kind"),
            "coef": model.get("coef"),
            "intercept": model.get("intercept"),
            "p": model.get("p"),
            "n_train_windows": int(n_train_windows),
            "n_train_pairs": int(n_train_pairs),
        }
    )


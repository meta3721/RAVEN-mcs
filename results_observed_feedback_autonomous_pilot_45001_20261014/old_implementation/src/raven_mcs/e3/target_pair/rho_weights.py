"""Frozen RMSE_rho arrival/delivered weighting with correct group→unit mapping."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from raven_mcs.e3.target_pair.errors import RhoWeightError
from raven_mcs.metrics.accuracy import rmse_mu, rmse_rho


def build_rho_weights(
    *,
    test_groups: list[str],
    delivered_group_counts: Mapping[str, float],
) -> np.ndarray:
    """Map group delivered counts c_g onto test units without n_g inflation.

    Frozen rule:
        rho_g = c_g / sum_h c_h
        w_i = rho_g / n_g   for each test unit i in group g

    so that sum_{i in g} w_i = rho_g (not n_g * rho_g).
    """
    if not test_groups:
        raise RhoWeightError("RHO_WEIGHT_ERROR: empty test_groups")

    # Group sizes on the test list
    n_g: dict[str, int] = {}
    for g in test_groups:
        gs = str(g)
        n_g[gs] = n_g.get(gs, 0) + 1

    c_g = {str(k): float(v) for k, v in delivered_group_counts.items()}
    # Only count groups that appear in test support for the mass total,
    # but include delivered mass on test groups; groups with c=0 get 0 mass.
    c_on_test = {g: float(c_g.get(g, 0.0)) for g in n_g}
    total_c = float(sum(c_on_test.values()))
    if total_c <= 0:
        raise RhoWeightError("RHO_WEIGHT_ERROR: zero delivered mass for rho")

    w = np.zeros(len(test_groups), dtype=np.float64)
    for i, g in enumerate(test_groups):
        gs = str(g)
        cg = c_on_test[gs]
        ng = n_g[gs]
        if ng <= 0:
            raise RhoWeightError(f"RHO_WEIGHT_ERROR: n_g=0 for group {gs}")
        if cg <= 0:
            w[i] = 0.0
        else:
            rho_g = cg / total_c
            w[i] = rho_g / float(ng)

    s = float(w.sum())
    if abs(s - 1.0) > 1e-9:
        # If some test groups had all-zero c, mass may be < 1; renormalize only over
        # positive-mass units while preserving relative group totals among positive groups.
        if s <= 0:
            raise RhoWeightError("RHO_WEIGHT_ERROR: all-zero rho weights")
        w = w / s
    return w


def rho_group_diagnostics(
    *,
    test_groups: list[str],
    delivered_group_counts: Mapping[str, float],
) -> dict[str, Any]:
    """Diagnostics proving sum_{i in g} w_i == rho_g."""
    w = build_rho_weights(test_groups=test_groups, delivered_group_counts=delivered_group_counts)
    n_g: dict[str, int] = {}
    for g in test_groups:
        n_g[str(g)] = n_g.get(str(g), 0) + 1
    c_on_test = {g: float(delivered_group_counts.get(g, 0.0)) for g in n_g}
    total_c = float(sum(c_on_test.values()))
    rows = []
    max_err = 0.0
    for g, ng in sorted(n_g.items()):
        cg = c_on_test[g]
        rho_g = (cg / total_c) if total_c > 0 else 0.0
        mask = np.array([str(x) == g for x in test_groups])
        recovered = float(w[mask].sum())
        # After possible renormalize when some groups have c=0, compare among positive
        intended = rho_g
        if float(w.sum()) > 0 and abs(float(w.sum()) - 1.0) <= 1e-12 and total_c > 0:
            # If we renormalized because of zero-c groups only, positive groups keep
            # relative shares equal to c_g/sum_{h:c_h>0} c_h
            pos_total = sum(v for v in c_on_test.values() if v > 0)
            intended = (cg / pos_total) if (cg > 0 and pos_total > 0) else 0.0
        err = abs(recovered - intended)
        max_err = max(max_err, err)
        rows.append(
            {
                "group": g,
                "c_g": cg,
                "n_g": ng,
                "intended_rho_g": intended,
                "per_unit_weight": float(w[mask][0]) if mask.any() and ng > 0 else 0.0,
                "recovered_group_total_mass": recovered,
                "normalization_error": err,
            }
        )
    return {
        "rows": rows,
        "max_normalization_error": max_err,
        "status": "PASS" if max_err <= 1e-12 else "FAIL",
        "rule": "w_i = rho_g / n_g with rho_g = c_g / sum c_h",
    }


def delivered_group_counts_from_events(
    events: pd.DataFrame,
    unit_to_group: Mapping[str, str],
) -> dict[str, float]:
    counts: dict[str, float] = {}
    for _, row in events.iterrows():
        if int(row["U"]) != 1:
            continue
        obs = row["observed_unit_ids"]
        if isinstance(obs, str):
            import json

            obs = json.loads(obs)
        for uid in obs or []:
            g = unit_to_group.get(str(uid))
            if g is None:
                continue
            counts[str(g)] = counts.get(str(g), 0.0) + 1.0
    return counts


def compute_rmse_mu_rho(
    *,
    y_pred: np.ndarray,
    y_true: np.ndarray,
    mu_weights: np.ndarray,
    rho_weights: np.ndarray,
) -> dict[str, float]:
    if len(y_pred) != len(mu_weights) or len(y_pred) != len(rho_weights):
        raise RhoWeightError("RHO_WEIGHT_ERROR: weight length mismatch")
    return {
        "RMSE_mu": float(rmse_mu(y_pred, y_true, mu_weights)),
        "RMSE_rho": float(rmse_rho(y_pred, y_true, rho_weights)),
    }


def production_rho_analytical_test() -> dict[str, Any]:
    """Unequal n_g and c_g through the ACTUAL production builder."""
    # Groups: g0 has 3 test units, g1 has 1 test unit
    test_groups = ["g0", "g0", "g0", "g1"]
    c = {"g0": 2.0, "g1": 6.0}  # intended rho = [0.25, 0.75]
    # w: g0 units get 0.25/3 each; g1 gets 0.75/1
    hand_w = np.array([0.25 / 3, 0.25 / 3, 0.25 / 3, 0.75], dtype=np.float64)
    w = build_rho_weights(test_groups=test_groups, delivered_group_counts=c)
    diag = rho_group_diagnostics(test_groups=test_groups, delivered_group_counts=c)
    y_true = np.zeros(4)
    y_pred = np.array([1.0, 1.0, 1.0, 0.0])  # error on g0 only
    mu = np.array([0.25, 0.25, 0.25, 0.25])
    out = compute_rmse_mu_rho(y_pred=y_pred, y_true=y_true, mu_weights=mu, rho_weights=w)
    # RMSE_mu = sqrt(0.75) ; RMSE_rho = sqrt(0.25)  (all g0 mass)
    hand_mu = float(np.sqrt(0.75))
    hand_rho = float(np.sqrt(0.25))
    return {
        "hand_weights": hand_w.tolist(),
        "production_weights": w.tolist(),
        "weight_error": float(np.max(np.abs(w - hand_w))),
        "group_diagnostics": diag,
        "RMSE_mu": out["RMSE_mu"],
        "RMSE_rho": out["RMSE_rho"],
        "hand_mu": hand_mu,
        "hand_rho": hand_rho,
        "error_mu": abs(out["RMSE_mu"] - hand_mu),
        "error_rho": abs(out["RMSE_rho"] - hand_rho),
        "differ": abs(out["RMSE_mu"] - out["RMSE_rho"]) > 1e-12,
        "n_g_does_not_inflate_rho_g": diag["status"] == "PASS",
        "status": "PASS"
        if (
            float(np.max(np.abs(w - hand_w))) <= 1e-12
            and abs(out["RMSE_rho"] - hand_rho) <= 1e-12
            and diag["status"] == "PASS"
        )
        else "FAIL",
        "definition": {
            "RMSE_mu": "target-weighted risk under mu",
            "RMSE_rho": "delivered-observation group mass rho_g=c_g/sum c; w_i=rho_g/n_g",
            "sample_support": "frozen TEST atomic units",
        },
    }


def analytical_mu_rho_test() -> dict[str, Any]:
    """Backward-compatible alias pointing at production builder test. """
    return production_rho_analytical_test()

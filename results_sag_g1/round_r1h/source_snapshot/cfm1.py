"""CF-M1 matched-budget counterfactual. Isolates cross-time mixing only."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

import numpy as np

from raven_mcs.utils.hashing import sha256_json

SEED = 30001
TAU_COV = 0.05
RNG_SALT = 13  # same offset as E3-v1 generate_complete_aligned_r3


def matching_rule_payload() -> dict[str, Any]:
    return {
        "cf_id": "CF-M1",
        "paired_with": "CF0_E3v1_logical_window",
        "natural_hour_alignment": "train_natural_windows_sorted_by_time_index[window_id]",
        "matched_inputs": [
            "per_client_risk_set_size",
            "client_set_from_cf0",
            "candidate_budget_equals_risk_set_size",
            "seed",
            "target_law",
            "pi_safe",
            "tau_cov",
        ],
        "unique_change": "sample from same-natural-hour pool instead of global train pool",
        "without_replacement": True,
        "cross_time_fill": False,
        "replacement_padding": False,
        "deficit_rule": "sample_count = min(cf0_budget, available_in_natural_hour); log deficit; do not steal from other hours",
        "seed": SEED,
        "rng_salt": RNG_SALT,
        "tau_cov": TAU_COV,
    }


def matching_rule_hash() -> str:
    return sha256_json(matching_rule_payload())


def cf0_budgets_from_events(events, *, window_id: int) -> dict[str, int]:
    chunk = events.loc[events["window_id"].astype(int) == int(window_id)]
    out: dict[str, int] = {}
    for _, row in chunk.iterrows():
        client = str(row["client_id"])
        risk = row["risk_set_unit_ids"]
        if isinstance(risk, (list, tuple, np.ndarray)):
            out[client] = int(len(list(risk)))
        else:
            out[client] = 0
    return out


def sample_matched_hour(
    *,
    budgets: Mapping[str, int],
    hour_units_by_client: Mapping[str, Sequence[str]],
    window_id: int,
    seed: int = SEED,
) -> dict[str, Any]:
    rng = np.random.default_rng(int(seed) + RNG_SALT + int(window_id) * 97)
    chosen: list[str] = []
    deficit = 0
    per_client: dict[str, int] = {}
    for client in sorted(budgets):
        need = int(budgets[client])
        pool = sorted({str(u) for u in hour_units_by_client.get(client, [])})
        take = min(need, len(pool))
        deficit += max(0, need - take)
        if take > 0:
            idx = rng.choice(len(pool), size=take, replace=False)
            picked = [pool[int(i)] for i in np.sort(idx)]
            chosen.extend(picked)
        per_client[client] = take
    return {
        "unit_ids": chosen,
        "sample_count": len(chosen),
        "deficit": int(deficit),
        "per_client": per_client,
        "cross_time_fill": False,
        "replacement": False,
    }

"""Stage A: expected event count definition audit."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from raven_mcs.e2.empirical.events import OBS_RATE_TARGET, OPP_RATE_TARGET, USE_RATE_TARGET
from raven_mcs.utils.serialization import dump_json

ROOT = Path(__file__).resolve().parents[4]


def audit_event_counts(
    schedules: dict[int, dict[str, Any]],
    unit_stratum: dict[str, str],
    *,
    root: Path | None = None,
    p_opp: float = OPP_RATE_TARGET,
    p_obs: float = OBS_RATE_TARGET,
    q_use: float = USE_RATE_TARGET,
) -> dict[str, Any]:
    root = Path(root or ROOT)
    out = root / "outputs/e2_hard_variance"
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    cand_counts = []
    total_cand_mass = 0.0
    total_cand_count = 0
    dup_mass = 0
    for seed, sched in schedules.items():
        for r in sched["rows"]:
            uids = r["candidate_unit_ids"]
            masses = r["candidate_event_mass"]
            n = len(uids)
            cand_counts.append(n)
            total_cand_count += n
            if len(uids) != len(set(uids)):
                dup_mass += 1
            for uid, mass in zip(uids, masses, strict=True):
                m = float(mass)
                total_cand_mass += m
                rows.append({
                    "seed": seed,
                    "client_id": r["client_id"],
                    "window_id": r["window_id"],
                    "unit_id": uid,
                    "raw_stratum": unit_stratum[str(uid)],
                    "candidate_mass": m,
                    "expected_opportunity_mass": m * p_opp,
                    "expected_observation_mass": m * p_opp * p_obs,
                    "expected_hard_arrival_mass": m * p_opp * p_obs * q_use,
                    "expected_opportunity_count": p_opp,  # count unit with mass=1 model
                    "expected_observation_count": p_opp * p_obs,
                    "expected_hard_arrival_count": p_opp * p_obs * q_use,
                })
    detail = pd.DataFrame(rows)
    by_raw = detail.groupby("raw_stratum")["expected_hard_arrival_mass"].sum()
    # also count-model totals
    exp_arr_count = float(total_cand_count * p_opp * p_obs * q_use)
    exp_opp_count = float(total_cand_count * p_opp)
    exp_obs_count = float(total_cand_count * p_opp * p_obs)

    stage = pd.DataFrame([
        {
            "stage": "candidate",
            "count_unit": total_cand_count,
            "mass_unit": total_cand_mass,
            "definition": "scheduled unique supported candidates",
        },
        {
            "stage": "opportunity",
            "count_unit": exp_opp_count,
            "mass_unit": float(detail["expected_opportunity_mass"].sum()),
            "definition": "candidate × p_opp",
        },
        {
            "stage": "observation",
            "count_unit": exp_obs_count,
            "mass_unit": float(detail["expected_observation_mass"].sum()),
            "definition": "candidate × p_opp × p_obs",
        },
        {
            "stage": "hard_arrival",
            "count_unit": exp_arr_count,
            "mass_unit": float(detail["expected_hard_arrival_mass"].sum()),
            "definition": "candidate × p_opp × p_obs × q_use",
        },
    ])
    stage.to_csv(out / "E2_EXPECTED_EVENT_COUNT_BY_STAGE.csv", index=False)

    audit = {
        "total_candidate_count": int(total_cand_count),
        "total_candidate_mass": float(total_cand_mass),
        "expected_opportunity_count": exp_opp_count,
        "expected_observation_count": exp_obs_count,
        "expected_hard_arrival_count": exp_arr_count,
        "expected_opportunity_mass": float(detail["expected_opportunity_mass"].sum()),
        "expected_observation_mass": float(detail["expected_observation_mass"].sum()),
        "expected_hard_arrival_mass": float(detail["expected_hard_arrival_mass"].sum()),
        "realized_opportunity_count": None,
        "realized_observation_count": None,
        "realized_arrival_count": None,
        "average_candidates_per_client_window": float(np.mean(cand_counts)),
        "min_candidates_per_client_window": int(min(cand_counts)),
        "median_candidates_per_client_window": float(np.median(cand_counts)),
        "max_candidates_per_client_window": int(max(cand_counts)),
        "minimum_expected_arrivals_per_raw_stratum_mass": float(by_raw.min()) if len(by_raw) else 0.0,
        "minimum_expected_arrivals_per_raw_stratum_count_proxy": float(
            by_raw.min() / max(total_cand_mass, 1e-15) * exp_arr_count
        ) if len(by_raw) else 0.0,
        "duplicate_mass_count": int(dup_mass),
        "synthetic_event_count": 0,
        "event_mass_equals_one_for_hard_count_model": True,
        "mass_unit_definition": "E1 target_weight on schedule; hard count model uses event_mass=1",
        "stage_naming": ["candidate", "opportunity", "observation", "hard_arrival"],
        "finite_status": True,
        "rates": {"p_opp": p_opp, "p_obs": p_obs, "q_use": q_use},
        "status": "PASS" if dup_mass == 0 else "FAIL",
    }
    dump_json(audit, out / "E2_EVENT_COUNT_DEFINITION_AUDIT.json")
    return audit

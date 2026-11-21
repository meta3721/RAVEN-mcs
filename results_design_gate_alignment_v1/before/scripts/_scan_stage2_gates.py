#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical.schedule import build_continuous_schedule
from raven_mcs.e2.stage2.gates import (
    PROFILES,
    SCENARIOS,
    VALIDATION_SEEDS,
    evaluate_seed_profile_gates,
)
from raven_mcs.e2.stage2.sampler import generate_stage2_mother_trace
from raven_mcs.e2.stage2.stratum import build_opportunity_stratum_table

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    build_opportunity_stratum_table(ROOT)
    for prof in PROFILES:
        bad = []
        for seed in VALIDATION_SEEDS:
            streams = build_base_random_streams(
                seed, n_windows=300, n_clients=8, max_risk_set=20,
            )
            schedule = build_continuous_schedule(
                seed,
                schedule_uniforms=streams["base_client_window_schedule"],
                root=ROOT,
            )
            by = {}
            for scen in SCENARIOS:
                result = generate_stage2_mother_trace(
                    seed=seed,
                    profile_id=prof,
                    scenario_id=scen,
                    root=ROOT,
                    streams=streams,
                    schedule=schedule,
                )
                by[scen] = result["diagnostics"][300]
            evaluated = evaluate_seed_profile_gates(by)
            if not evaluated["profile_valid_seed"]:
                bad.append({
                    "seed": seed,
                    "failures": evaluated["failures"],
                    "bal_s": by["balanced"]["D_TV_stratum"],
                    "max_g_exp": max(by[s]["D_TV_group_exp_emp"] for s in SCENARIOS),
                })
        print(prof, "PASS" if not bad else bad)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

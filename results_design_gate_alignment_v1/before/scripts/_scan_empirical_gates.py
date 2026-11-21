#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical.gates import (
    PROFILES,
    SCENARIOS,
    VALIDATION_SEEDS,
    evaluate_seed_profile_gates,
)
from raven_mcs.e2.empirical.sampler import generate_empirical_mother_trace
from raven_mcs.e2.empirical.schedule import build_continuous_schedule

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
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
                result = generate_empirical_mother_trace(
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
                b = by["balanced"]
                bad.append({
                    "seed": seed,
                    "failures": evaluated["failures"],
                    "bal_g": b["D_TV_group"],
                    "bal_s": b["D_TV_stratum"],
                    "bal_head": b["head_mass_ratio"],
                    "bal_tail": b["tail_mass_ratio"],
                    "us_g": by["usable_only"]["D_TV_group"],
                    "us_tail": by["usable_only"]["tail_mass_ratio"],
                })
        print(prof, "PASS" if not bad else bad)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

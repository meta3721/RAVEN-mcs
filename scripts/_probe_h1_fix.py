#!/usr/bin/env python3
"""Probe small schedule/event knobs for H1 overshoot on 29103/29105."""
from __future__ import annotations

import argparse
from pathlib import Path

from raven_mcs.e2.distribution.base_streams import build_base_random_streams
from raven_mcs.e2.empirical import events as ev
from raven_mcs.e2.empirical.gates import evaluate_seed_profile_gates
from raven_mcs.e2.empirical.sampler import generate_empirical_mother_trace
from raven_mcs.e2.empirical.schedule import build_continuous_schedule
import raven_mcs.e2.empirical.schedule as sched

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = (
    "balanced",
    "opportunity_only",
    "observation_only",
    "usable_only",
    "complete_aligned",
    "complete_counteracting",
)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--cand", type=int, default=24)
    p.add_argument("--opp", type=float, default=0.55)
    p.add_argument("--profile", default="PROFILE-S3")
    p.add_argument("--seeds", default="29103,29105")
    args = p.parse_args()
    seeds = [int(x) for x in args.seeds.split(",")]
    old_cand = sched.CANDIDATE_SIZE
    old_opp = ev.OPP_RATE_TARGET
    sched.CANDIDATE_SIZE = int(args.cand)
    ev.OPP_RATE_TARGET = float(args.opp)
    try:
        for seed in seeds:
            streams = build_base_random_streams(
                seed, n_windows=300, n_clients=8, max_risk_set=int(args.cand),
            )
            schedule = build_continuous_schedule(
                seed,
                schedule_uniforms=streams["base_client_window_schedule"],
                root=ROOT,
                candidate_size=int(args.cand),
            )
            by = {}
            for scen in SCENARIOS:
                r = generate_empirical_mother_trace(
                    seed=seed,
                    profile_id=args.profile,
                    scenario_id=scen,
                    root=ROOT,
                    streams=streams,
                    schedule=schedule,
                )
                by[scen] = r["diagnostics"][300]
            ev_g = evaluate_seed_profile_gates(by)
            b = by["balanced"]
            print(
                f"cand={args.cand} opp={args.opp} {args.profile} seed={seed} "
                f"valid={ev_g['profile_valid_seed']} fail={ev_g['failures']} "
                f"bal_head={b['head_mass_ratio']:.5f} bal_tail={b['tail_mass_ratio']:.5f} "
                f"bal_g={b['D_TV_group']:.5f} us_g={by['usable_only']['D_TV_group']:.5f} "
                f"us_tail={by['usable_only']['tail_mass_ratio']:.5f}"
            )
    finally:
        sched.CANDIDATE_SIZE = old_cand
        ev.OPP_RATE_TARGET = old_opp
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

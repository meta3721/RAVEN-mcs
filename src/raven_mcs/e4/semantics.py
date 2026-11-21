"""Frozen one-factor-at-a-time E4 method semantics."""
from .constants import ABLATIONS, DATASETS, FORMAL_SEEDS, ROUND, SCENARIO, SMOKE_SEED

_DISABLED = {
    "raven_wo_design": "uses_design_ratio",
    "raven_wo_obs": "uses_observation_ipw",
    "raven_wo_use": "uses_usable_ipw",
    "raven_wo_inst": "uses_instant_calibration",
    "raven_wo_debt": "uses_debt",
}

def freeze() -> dict:
    return {
        "round": ROUND, "scenario": SCENARIO, "datasets": list(DATASETS),
        "formal_seeds": list(FORMAL_SEEDS), "smoke_seed": SMOKE_SEED,
        "reference_method": "raven", "reuse_only": True,
        "e3_eventtrace_root": "artifacts/e3_formal_runs_r1/eventtraces",
        "e3_reference_root": "artifacts/e3_formal_runs_r1/runs",
        "no_retuning": True, "local_steps": 2,
        "ablations": [
            {"method": method, "disabled_flag": _DISABLED[method],
             "all_other_raven_flags_unchanged": True}
            for method in ABLATIONS
        ],
    }

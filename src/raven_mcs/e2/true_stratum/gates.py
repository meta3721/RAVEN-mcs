"""Profile/window gates for true-stratum non-wrap repair (G1–G6)."""
from __future__ import annotations

from typing import Any, Mapping

# Reuse stage2 gate logic; diagnostics use D_TV_stratum for true stratum TV.
from raven_mcs.e2.stage2.gates import (  # noqa: F401
    PROFILES,
    SCENARIOS,
    SINGLE_STAGE,
    VALIDATION_SEEDS,
    evaluate_seed_profile_gates,
    select_strength_profile,
    select_window_length,
    window_prefix_stable,
)


def normalize_true_stratum_diagnostics(diag: Mapping[str, Any]) -> dict[str, Any]:
    """Alias D_TV_true_stratum* onto D_TV_stratum* for gate reuse."""
    out = dict(diag)
    if "D_TV_true_stratum" in out and "D_TV_stratum" not in out:
        out["D_TV_stratum"] = out["D_TV_true_stratum"]
    if "D_TV_true_stratum_exp_emp" in out and "D_TV_stratum_exp_emp" not in out:
        out["D_TV_stratum_exp_emp"] = out["D_TV_true_stratum_exp_emp"]
    if "D_TV_stratum" in out:
        out.setdefault("D_TV_true_stratum", out["D_TV_stratum"])
    if "D_TV_stratum_exp_emp" in out:
        out.setdefault("D_TV_true_stratum_exp_emp", out["D_TV_stratum_exp_emp"])
    return out

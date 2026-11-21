"""E3 production real-runner (pair/oracle correctness closure)."""

from raven_mcs.e3.real_runner.constants import CANARY_SEED, DEBUG_SEED, M_MC, ROUND
from raven_mcs.e3.real_runner.runner import run_e3_real

__all__ = ["ROUND", "CANARY_SEED", "DEBUG_SEED", "M_MC", "run_e3_real"]

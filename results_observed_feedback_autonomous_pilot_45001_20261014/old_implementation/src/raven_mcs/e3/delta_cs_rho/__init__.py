"""E3 final hotfix: true Delta_c_s (client×s) and atomic rho_i^arr."""

from raven_mcs.e3.delta_cs_rho.atomic_rho import build_atomic_arrival_rho
from raven_mcs.e3.delta_cs_rho.delta_cs_v6 import accumulate_delta_cs_v6
from raven_mcs.e3.delta_cs_rho.stratum import opportunity_stratum_definition

__all__ = [
    "accumulate_delta_cs_v6",
    "build_atomic_arrival_rho",
    "opportunity_stratum_definition",
]

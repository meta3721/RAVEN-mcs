"""Method policy definitions (P10-C).

Each method declares which components it uses, so the WindowRunner can
selectively apply correction, debt, variance, etc.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MethodPolicy:
    """Declarative policy for each method's correction/training pathway."""

    uses_central_training: bool = False
    uses_design_ratio: bool = False
    uses_observation_ipw: bool = False
    uses_usable_ipw: bool = False
    uses_hajek_local_loss: bool = False
    uses_instant_calibration: bool = False
    uses_debt: bool = False
    uses_reference_penalty: bool = False
    uses_variance_penalty: bool = False
    uses_staleness_penalty: bool = False
    uses_oracle_propensity: bool = False
    # F-1 diagnostic arms only. uses_oracle_propensity gates the q map and the atomic p map
    # together (window_runner.py:426-430 and :707-727); uses_oracle_p isolates the p map so the
    # two members of RAVEN-SimOracle can be separated. No paper method sets this.
    uses_oracle_p: bool = False
    is_external_baseline: bool = False
    # These three fields have separate responsibilities. gate_mode is only
    # retained to reproduce historical control policies, never the new method.
    design_control: str = "legacy"
    coverage_diagnostic: str = "aggregate_coverage"
    method_version: str = "legacy-v1"
    gate_mode: str = "policy"
    legacy_only: bool = False
    paper_method: bool = False


PAPER_METHOD_KEY = "raven_mcs"
FORMAL_DEFAULT_METHOD = "raven_mcs"
FORMAL_GATE_MODE = "aggregate_coverage"
CONFIGURED_METHOD_VERSION = "configured-design-v1"
LEGACY_COVERAGE_METHOD = "raven_coverage_legacy"

_RAVEN_CORE = dict(
    uses_design_ratio=True,
    uses_observation_ipw=True,
    uses_usable_ipw=True,
    uses_hajek_local_loss=True,
    uses_instant_calibration=True,
    uses_debt=True,
    uses_reference_penalty=True,
    uses_variance_penalty=True,
    uses_staleness_penalty=True,
)


# Method policy registry
POLICY_MAP: dict[str, MethodPolicy] = {
    "central_all": MethodPolicy(
        uses_central_training=True,
    ),
    "central_delivered": MethodPolicy(
        uses_central_training=True,
    ),
    "fedavg_window": MethodPolicy(),
    "fedau_window": MethodPolicy(
        uses_usable_ipw=True,
    ),
    "obsuse_window": MethodPolicy(
        uses_observation_ipw=True,
        uses_usable_ipw=True,
    ),
    "fedasync_window": MethodPolicy(
        uses_staleness_penalty=True,
    ),
    "timealign_agg": MethodPolicy(
        uses_staleness_penalty=True,
    ),
    "flamf_timealign_adapted": MethodPolicy(),
    "flamf_original": MethodPolicy(
        is_external_baseline=True,
    ),
    "local_hajek": MethodPolicy(
        uses_design_ratio=True,
        uses_observation_ipw=True,
        uses_hajek_local_loss=True,
    ),
    "twostage_hajek": MethodPolicy(
        uses_design_ratio=True,
        uses_observation_ipw=True,
        uses_usable_ipw=True,
        uses_hajek_local_loss=True,
    ),
    "inst_cal": MethodPolicy(
        uses_design_ratio=True,
        uses_observation_ipw=True,
        uses_usable_ipw=True,
        uses_instant_calibration=True,
        uses_reference_penalty=True,
        uses_variance_penalty=True,
        uses_staleness_penalty=True,
    ),
    "debt_cal": MethodPolicy(
        uses_debt=True,
        uses_instant_calibration=True,
        uses_reference_penalty=True,
    ),
    # LEGACY always-on (E1/E3/E4 historical). Not the paper default.
    "raven": MethodPolicy(
        **_RAVEN_CORE,
        gate_mode="always_on",
        legacy_only=True,
        paper_method=False,
    ),
    "raven_legacy_always_on": MethodPolicy(
        **_RAVEN_CORE,
        gate_mode="always_on",
        legacy_only=True,
        paper_method=False,
    ),
    # Unique paper method: explicit pre-window Design, independent coverage.
    "raven_mcs": MethodPolicy(
        **_RAVEN_CORE,
        design_control="configured",
        method_version=CONFIGURED_METHOD_VERSION,
        legacy_only=False,
        paper_method=True,
    ),
    "raven_coverage_legacy": MethodPolicy(
        **_RAVEN_CORE,
        gate_mode="aggregate_coverage",
        method_version="coverage-controlled-v1",
        legacy_only=True,
        paper_method=False,
    ),
    # E4 one-factor-at-a-time RAVEN ablations.  Keep every non-ablated RAVEN
    # component identical; do not substitute a historical partial method.
    "raven_wo_design": MethodPolicy(
        uses_observation_ipw=True, uses_usable_ipw=True, uses_hajek_local_loss=True,
        uses_instant_calibration=True, uses_debt=True, uses_reference_penalty=True,
        uses_variance_penalty=True, uses_staleness_penalty=True,
        gate_mode="always_off",
        legacy_only=True,
        paper_method=False,
    ),
    "raven_sag": MethodPolicy(
        **_RAVEN_CORE,
        gate_mode="sag",
        legacy_only=True,
        paper_method=False,
    ),
    "raven_wo_obs": MethodPolicy(
        uses_design_ratio=True, uses_usable_ipw=True, uses_hajek_local_loss=True,
        uses_instant_calibration=True, uses_debt=True, uses_reference_penalty=True,
        uses_variance_penalty=True, uses_staleness_penalty=True,
    ),
    "raven_wo_use": MethodPolicy(
        uses_design_ratio=True, uses_observation_ipw=True, uses_hajek_local_loss=True,
        uses_instant_calibration=True, uses_debt=True, uses_reference_penalty=True,
        uses_variance_penalty=True, uses_staleness_penalty=True,
    ),
    "raven_wo_inst": MethodPolicy(
        uses_design_ratio=True, uses_observation_ipw=True, uses_usable_ipw=True,
        uses_hajek_local_loss=True, uses_debt=True, uses_reference_penalty=True,
        uses_variance_penalty=True, uses_staleness_penalty=True,
    ),
    "raven_wo_debt": MethodPolicy(
        uses_design_ratio=True, uses_observation_ipw=True, uses_usable_ipw=True,
        uses_hajek_local_loss=True, uses_instant_calibration=True,
        uses_reference_penalty=True, uses_variance_penalty=True,
        uses_staleness_penalty=True,
    ),
    "raven_simoracle": MethodPolicy(
        uses_design_ratio=True,
        uses_observation_ipw=True,
        uses_usable_ipw=True,
        uses_hajek_local_loss=True,
        uses_instant_calibration=True,
        uses_debt=True,
        uses_reference_penalty=True,
        uses_variance_penalty=True,
        uses_staleness_penalty=True,
        uses_oracle_propensity=True,
    ),
    # F-1 diagnostic arm: identical to legacy "raven" except that the atomic observation
    # propensity is the true p_obs_true_by_unit while q stays estimated.
    "raven_oracle_p": MethodPolicy(
        **_RAVEN_CORE,
        gate_mode="always_on",
        legacy_only=True,
        paper_method=False,
        uses_oracle_p=True,
    ),
}


# Aliases never point raven_mcs at legacy always-on raven.
METHOD_ALIASES: dict[str, str] = {
    "centralall": "central_all",
    "centraldelivered": "central_delivered",
    "fedavg": "fedavg_window",
    "fedau": "fedau_window",
    "obsuse": "obsuse_window",
    "fedasync": "fedasync_window",
    "timealign": "timealign_agg",
    "time_align": "timealign_agg",
    "time_align_agg": "timealign_agg",
    "flamf": "flamf_original",
    "two_stage_hajek": "twostage_hajek",
    "instant_calibration": "inst_cal",
    "debt_calibration": "debt_cal",
    "simoracle": "raven_simoracle",
    "sag": "raven_sag",
    "sag_raven": "raven_sag",
    "raven_formal": "raven_mcs",
    "raven_mcs_formal": "raven_mcs",
    "raven_full_design_legacy": "raven_legacy_always_on",
    "raven_mcs_coverage_legacy": "raven_coverage_legacy",
}


def resolve_method(method: str) -> str:
    """Canonical POLICY_MAP key. raven_mcs is the unique paper method."""
    normalized = str(method).strip().lower().replace("-", "_")
    seen: set[str] = set()
    cur = normalized
    while True:
        if cur in seen:
            raise ValueError(f"method alias cycle involving {cur!r}")
        seen.add(cur)
        if cur in POLICY_MAP:
            return cur
        nxt = METHOD_ALIASES.get(cur)
        if nxt is None or nxt == cur:
            return cur
        cur = nxt


def get_method_policy(method: str) -> MethodPolicy:
    """Get the policy for a method by name."""
    canonical = resolve_method(method)
    if canonical in POLICY_MAP:
        return POLICY_MAP[canonical]
    return MethodPolicy()

"""Configured deployment method freeze. No experiment. Paper-facing name is RAVEN-MCS / raven_mcs."""

from __future__ import annotations

import argparse

from raven_mcs.aggregation.method_policy import (
    FORMAL_DEFAULT_METHOD,
    CONFIGURED_METHOD_VERSION,
    PAPER_METHOD_KEY,
    get_method_policy,
    resolve_method,
)

PAPER_METHOD = PAPER_METHOD_KEY
DEFAULT_METHOD = FORMAL_DEFAULT_METHOD
PAPER_DISPLAY_NAME = "RAVEN-MCS"
LEGACY_CONTROLS = ("raven_coverage_legacy", "raven_legacy_always_on", "raven_wo_design")
FORBIDDEN_PAPER_FACING = ("raven_mcs_formal",)
R1M_METHODS = (PAPER_METHOD,) + LEGACY_CONTROLS


def add_method_argument(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "--method",
        default=DEFAULT_METHOD,
        help="Formal paper method key (default: raven_mcs).",
    )
    parser.add_argument("--design", choices=("on", "off"), help="Required explicit setting for configured RAVEN-MCS")
    parser.add_argument("--design-source", default="explicit_cli")
    return parser


def formal_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="r1m_method_freeze")
    return add_method_argument(parser)


def assert_frozen() -> None:
    assert resolve_method(PAPER_METHOD) == "raven_mcs"
    assert get_method_policy(PAPER_METHOD).design_control == "configured"
    assert get_method_policy(PAPER_METHOD).method_version == CONFIGURED_METHOD_VERSION
    assert get_method_policy(PAPER_METHOD).paper_method is True
    assert get_method_policy("raven_mcs_formal") == get_method_policy("raven_mcs")
    assert get_method_policy("raven_legacy_always_on").legacy_only is True
    assert get_method_policy("raven").legacy_only is True
    assert PAPER_METHOD not in FORBIDDEN_PAPER_FACING

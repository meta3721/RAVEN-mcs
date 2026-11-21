"""R1m method freeze. No experiment. Paper-facing name is RAVEN-MCS / raven_mcs."""

from __future__ import annotations

import argparse

from raven_mcs.aggregation.method_policy import (
    FORMAL_DEFAULT_METHOD,
    FORMAL_GATE_MODE,
    PAPER_METHOD_KEY,
    get_method_policy,
    resolve_method,
)

PAPER_METHOD = PAPER_METHOD_KEY
DEFAULT_METHOD = FORMAL_DEFAULT_METHOD
PAPER_DISPLAY_NAME = "RAVEN-MCS"
LEGACY_CONTROLS = ("raven_legacy_always_on", "raven_wo_design")
FORBIDDEN_PAPER_FACING = ("raven_mcs_formal",)
R1M_METHODS = (PAPER_METHOD,) + LEGACY_CONTROLS


def add_method_argument(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "--method",
        default=DEFAULT_METHOD,
        help="Formal paper method key (default: raven_mcs).",
    )
    return parser


def formal_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="r1m_method_freeze")
    return add_method_argument(parser)


def assert_frozen() -> None:
    assert resolve_method(PAPER_METHOD) == "raven_mcs"
    assert get_method_policy(PAPER_METHOD).gate_mode == FORMAL_GATE_MODE
    assert get_method_policy(PAPER_METHOD).paper_method is True
    assert get_method_policy("raven_mcs_formal") == get_method_policy("raven_mcs")
    assert get_method_policy("raven_legacy_always_on").legacy_only is True
    assert get_method_policy("raven").legacy_only is True
    assert PAPER_METHOD not in FORBIDDEN_PAPER_FACING

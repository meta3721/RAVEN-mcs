"""Historical coverage-controlled audit identity; never the configured paper method."""
import argparse
from raven_mcs.aggregation.method_policy import LEGACY_COVERAGE_METHOD, get_method_policy

PAPER_METHOD = LEGACY_COVERAGE_METHOD  # Historical variable name in R1l/R1m programs.
DEFAULT_METHOD = LEGACY_COVERAGE_METHOD
LEGACY_CONTROLS = ("raven_legacy_always_on", "raven_wo_design")
R1M_METHODS = (DEFAULT_METHOD,) + LEGACY_CONTROLS


def formal_cli_parser():
    parser = argparse.ArgumentParser(description="Legacy coverage audit only")
    parser.add_argument("--method", choices=(DEFAULT_METHOD,), required=True)
    return parser


def assert_frozen():
    policy = get_method_policy(DEFAULT_METHOD)
    assert policy.gate_mode == "aggregate_coverage"
    assert policy.legacy_only and not policy.paper_method

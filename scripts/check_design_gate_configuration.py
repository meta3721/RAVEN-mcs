#!/usr/bin/env python3
"""Validate/serialize method identity without loading data or starting training."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from raven_mcs.experiments.r1m_method_freeze import formal_cli_parser
from raven_mcs.sag.r1l_design import configuration_for_method
from raven_mcs.aggregation.method_policy import get_method_policy, resolve_method


def main(argv=None):
    args=formal_cli_parser().parse_args(argv)
    configuration=configuration_for_method(args.method,args.design,source=args.design_source)
    policy=get_method_policy(args.method)
    print(json.dumps(dict(method=resolve_method(args.method),method_version=policy.method_version,
        design_control=policy.design_control,coverage_diagnostic=policy.coverage_diagnostic,
        coverage_role='diagnostic_only' if configuration else 'legacy_control',
        design_configuration=configuration.to_dict() if configuration else None,
        training_started=False),indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())

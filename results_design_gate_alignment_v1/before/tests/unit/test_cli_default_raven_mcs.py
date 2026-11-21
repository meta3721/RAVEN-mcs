from raven_mcs.experiments.r1m_method_freeze import DEFAULT_METHOD, formal_cli_parser


def test_cli_default_raven_mcs() -> None:
    parser = formal_cli_parser()
    args = parser.parse_args([])
    assert args.method == "raven_mcs"
    assert DEFAULT_METHOD == "raven_mcs"

from raven_mcs.aggregation.method_policy import (
    PAPER_METHOD_KEY,
    get_method_policy,
    resolve_method,
)


def test_paper_method_has_single_canonical_resolution() -> None:
    assert PAPER_METHOD_KEY == "raven_mcs"
    assert resolve_method("raven_mcs") == "raven_mcs"
    assert resolve_method("raven_mcs_formal") == "raven_mcs"
    assert resolve_method("raven_formal") == "raven_mcs"
    modes = {resolve_method(name) for name in ("raven_mcs", "raven_mcs_formal", "raven_formal")}
    assert modes == {"raven_mcs"}
    assert get_method_policy("raven_mcs").paper_method is True

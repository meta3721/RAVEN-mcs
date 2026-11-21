from raven_mcs.aggregation.method_policy import METHOD_ALIASES, POLICY_MAP, resolve_method


def test_no_alias_cycle() -> None:
    for key in list(METHOD_ALIASES) + list(POLICY_MAP):
        resolved = resolve_method(key)
        assert isinstance(resolved, str)
        assert resolved
    for src, dst in METHOD_ALIASES.items():
        assert src != dst or src in POLICY_MAP
        seen = {src}
        cur = dst
        while cur in METHOD_ALIASES and cur not in POLICY_MAP:
            assert cur not in seen, cur
            seen.add(cur)
            cur = METHOD_ALIASES[cur]

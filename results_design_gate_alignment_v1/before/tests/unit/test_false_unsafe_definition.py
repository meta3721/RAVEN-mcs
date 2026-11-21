from raven_mcs.sag.r1j_eval import classify

def test_false_unsafe_definition() -> None:
    assert classify(True, False) == "FALSE_UNSAFE"

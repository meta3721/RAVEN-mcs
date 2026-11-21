from raven_mcs.sag.r1j_eval import classify

def test_false_safe_definition() -> None:
    assert classify(False, True) == "FALSE_SAFE"

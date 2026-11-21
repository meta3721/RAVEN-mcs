from raven_mcs.sag.target_law import freeze_target_law_rule_v1

EXPECTED = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"


def test_e3v2_target_law_unchanged() -> None:
    assert freeze_target_law_rule_v1()["hash"] == EXPECTED

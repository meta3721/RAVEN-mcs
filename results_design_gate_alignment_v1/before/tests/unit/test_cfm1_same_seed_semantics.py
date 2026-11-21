from raven_mcs.sag.cfm1 import SEED, RNG_SALT

def test_cfm1_same_seed_semantics() -> None:
    assert SEED == 30001
    assert RNG_SALT == 13

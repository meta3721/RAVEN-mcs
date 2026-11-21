from raven_mcs.e3.formal.constants import CANARY_SEED, FORMAL_SEEDS
from raven_mcs.e3.formal.matrix import build_formal_matrix

def test_canary_seed_is_absent_from_formal_matrix() -> None:
    assert CANARY_SEED not in FORMAL_SEEDS
    assert all(row["seed"] != CANARY_SEED for row in build_formal_matrix()["rows"])

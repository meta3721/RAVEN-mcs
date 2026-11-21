from pathlib import Path
from e3_v2_protocol import population_rule_hash, population_rule_payload

ROOT = Path(__file__).resolve().parents[2]


def test_e3v2_population_rule_frozen() -> None:
    stored = (ROOT / "results_sag_g1/round_r1g/e3v2_spec/E3V2_POPULATION_RULE_HASH.txt").read_text(encoding="utf-8").strip()
    assert stored == population_rule_hash()
    assert population_rule_payload()["cross_time_resample"] is False
    assert "none" in str(population_rule_payload()["subsampling"])

from pathlib import Path
from raven_mcs.sag.r1l_conformal import finite_sample_conformal_quantile

def test_warmup8_not_nominal_95() -> None:
    _, n, warmup = finite_sample_conformal_quantile(list(range(8)))
    assert n == 8 and warmup is True
    spec = (Path(__file__).resolve().parents[2] / "src/raven_mcs/sag/r1l_spec.py").read_text(encoding="utf-8")
    assert "warmup_n_equals_8_forbidden_for_nominal_95" in spec

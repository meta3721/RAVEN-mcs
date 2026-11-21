from raven_mcs.sag.r1l_conformal import finite_sample_conformal_quantile
from raven_mcs.sag.r1l_spec import k_n
import math

def test_no_clip_conformal() -> None:
    q, n, warmup = finite_sample_conformal_quantile(list(range(18)))
    assert n == 18 and warmup is True
    assert math.isnan(q)
    assert k_n(18) == 19
    q2, n2, w2 = finite_sample_conformal_quantile(list(range(19)))
    assert n2 == 19 and w2 is False
    assert k_n(19) == 19
    src = __import__("pathlib").Path(__file__).resolve().parents[2] / "src/raven_mcs/sag/r1l_conformal.py"
    text = src.read_text(encoding="utf-8")
    assert "min(n" not in text and "min(k" not in text

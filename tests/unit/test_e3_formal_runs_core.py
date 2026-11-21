from raven_mcs.e3.formal.matrix import build_formal_matrix
from raven_mcs.e3.formal.metric_scale import convert_metrics, policy
from raven_mcs.e3.formal.stats import EPS_ZERO, signed_difference

def test_formal_matrix_counts_and_sealed_filter() -> None:
    matrix = build_formal_matrix()
    assert (matrix["n_new"], matrix["n_reused"], matrix["n_total"]) == (560, 100, 660)
    assert not any(r["dataset"] == "traffic" and r["method"] == "raven" for r in matrix["rows"] if r["kind"] == "new")

def test_metric_scale_physical_conversion() -> None:
    metrics = convert_metrics({"RMSE_mu": 2.0, "MAE_mu": 1.5}, policy("uair", sigma=4.0))
    assert metrics["RMSE_mu_std"] == 2.0 and metrics["RMSE_mu_phys"] == 8.0
    assert metrics["MAE_mu_phys"] == 6.0

def test_eps_zero_tie_logic() -> None:
    assert signed_difference(1.0, 1.0 + EPS_ZERO / 2) == 0.0
    assert signed_difference(1.0 + EPS_ZERO * 2, 1.0) > 0.0

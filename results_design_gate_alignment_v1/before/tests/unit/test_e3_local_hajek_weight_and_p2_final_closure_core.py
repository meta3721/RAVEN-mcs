from raven_mcs.e3.final_closure.core import certify_returned_alpha, summarize_weights

def test_p2_certificate_checks_ess_ball():
    assert certify_returned_alpha([0.5, 0.5])["classification"] == "CERTIFIED_WITHIN_NUMERICAL_TOLERANCE"
    assert certify_returned_alpha(None)["classification"] == "UNCERTIFIED_MISSING_STATE"

def test_weight_uniformity_epsilon():
    assert summarize_weights([0.5, 0.5])["is_uniform_eps"]
    assert not summarize_weights([0.4, 0.6])["is_uniform_eps"]

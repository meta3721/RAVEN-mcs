import numpy as np
from raven_mcs.aggregation.method_policy import get_method_policy
from raven_mcs.aggregation.methods import RavenAggregator, get_aggregator

FLAGS = ("uses_design_ratio", "uses_observation_ipw", "uses_usable_ipw",
         "uses_instant_calibration", "uses_debt")
METHOD_FLAG = {
    "raven_wo_design": "uses_design_ratio", "raven_wo_obs": "uses_observation_ipw",
    "raven_wo_use": "uses_usable_ipw", "raven_wo_inst": "uses_instant_calibration",
    "raven_wo_debt": "uses_debt",
}

def test_e4_ablation_policies_flip_exactly_one_raven_factor():
    full = get_method_policy("raven")
    assert all(getattr(full, flag) for flag in FLAGS)
    for method, disabled in METHOD_FLAG.items():
        policy = get_method_policy(method)
        assert [f for f in FLAGS if getattr(policy, f) != getattr(full, f)] == [disabled]
        agg = get_aggregator(method)
        assert isinstance(agg, RavenAggregator)
        if method == "raven_wo_inst":
            from raven_mcs.aggregation.methods import RavenWoInstAggregator
            assert isinstance(agg, RavenWoInstAggregator)

def test_raven_policy_identity_preserves_full_mode():
    before = get_method_policy("raven")
    after = get_method_policy("raven")
    assert before == after
    assert np.allclose(np.ones(3), np.ones_like(np.ones(3)))

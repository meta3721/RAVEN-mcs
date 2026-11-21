from raven_mcs.sag.r1k_barrier import coverage_upper_if_positive_lcb, strict_positive_lcb_possible

def test_positive_lcb_impossible_when_zero_prob_gt_delta() -> None:
    delta = 0.05
    assert coverage_upper_if_positive_lcb(0.20) < 1.0 - delta
    assert not strict_positive_lcb_possible(0.80, delta=delta)
    assert not strict_positive_lcb_possible(0.40, delta=delta)
    assert strict_positive_lcb_possible(1.00, delta=delta)

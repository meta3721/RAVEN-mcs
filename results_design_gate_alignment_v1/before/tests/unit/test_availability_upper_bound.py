from raven_mcs.sag.r1k_barrier import p_active_upper_from_a

def test_availability_upper_bound() -> None:
    for a in (1.0, 0.8, 0.6, 0.4, 0.2):
        assert p_active_upper_from_a(a) == a

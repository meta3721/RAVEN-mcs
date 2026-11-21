from raven_mcs.sag.r1l_conformal import finite_sample_conformal_quantile
from raven_mcs.sag.r1l_spec import N_MIN
from raven_mcs.sag.r1m_track import complete_window, decide_window, open_track


def test_n_lt_19_warmup_off() -> None:
    pretest_c = [0.08] * 12
    track = open_track(
        dataset="toy",
        availability_level=0.4,
        pretest_c=pretest_c,
        pretest_hours=[12] * 12,
        pretest_weekends=[False] * 12,
        pretest_labels=[f"pretest:{i}" for i in range(12)],
    )
    for t in range(N_MIN):
        rec = decide_window(track, window_id=t, hour=12, weekend=False)
        assert rec["state_before_decision"] == "WARMUP"
        assert rec["Gate"] == 0
        assert rec["Design"] == 0
        assert rec["C_LCB"] == 0.0
        complete_window(track, rec, c_t=0.08, hour=12, weekend=False, window_label=str(t))
    q, n, warmup = finite_sample_conformal_quantile(list(range(18)))
    assert warmup is True
    assert n == 18

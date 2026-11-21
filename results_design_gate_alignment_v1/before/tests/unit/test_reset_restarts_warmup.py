from raven_mcs.sag.r1m_track import complete_window, decide_window, open_track


def test_reset_restarts_warmup() -> None:
    track = open_track(
        dataset="toy",
        availability_level=0.4,
        pretest_c=[0.10] * 24,
        pretest_hours=[3] * 24,
        pretest_weekends=[False] * 24,
        pretest_labels=[f"p{i}" for i in range(24)],
    )
    for t in range(19):
        rec = decide_window(track, window_id=t, hour=3, weekend=False)
        complete_window(track, rec, c_t=0.10, hour=3, weekend=False, window_label=str(t))
    rec = decide_window(track, window_id=19, hour=3, weekend=False)
    rec = complete_window(track, rec, c_t=0.0, hour=3, weekend=False, window_label="19")
    if int(rec.get("reset_trigger_after_window") or 0) == 1:
        nxt = decide_window(track, window_id=20, hour=3, weekend=False)
        assert nxt["state_before_decision"] == "RESET"
        assert nxt["Gate"] == 0
        assert nxt["Design"] == 0
        complete_window(track, nxt, c_t=0.10, hour=3, weekend=False, window_label="20")
        after = decide_window(track, window_id=21, hour=3, weekend=False)
        assert after["state_before_decision"] == "WARMUP"
        assert after["Gate"] == 0

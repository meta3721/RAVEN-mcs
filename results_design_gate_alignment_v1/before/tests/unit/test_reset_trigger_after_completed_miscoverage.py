from raven_mcs.sag.r1m_reset import miscoverage_reset_trigger
from raven_mcs.sag.r1m_track import complete_window, decide_window, open_track


def _fill_warmup(track, n: int = 19, c: float = 0.10) -> None:
    for t in range(n):
        rec = decide_window(track, window_id=t, hour=3, weekend=False)
        complete_window(track, rec, c_t=c, hour=3, weekend=False, window_label=str(t))


def test_reset_trigger_after_completed_miscoverage() -> None:
    assert miscoverage_reset_trigger(state="CERTIFIED", c_lcb=0.2, c_t=0.01) is True
    assert miscoverage_reset_trigger(state="WARMUP", c_lcb=0.2, c_t=0.01) is False
    assert miscoverage_reset_trigger(state="CERTIFIED", c_lcb=0.01, c_t=0.2) is False
    track = open_track(
        dataset="toy",
        availability_level=0.4,
        pretest_c=[0.10] * 24,
        pretest_hours=[3] * 24,
        pretest_weekends=[False] * 24,
        pretest_labels=[f"p{i}" for i in range(24)],
    )
    _fill_warmup(track, 19, 0.10)
    rec = decide_window(track, window_id=19, hour=3, weekend=False)
    assert rec["state_before_decision"] == "CERTIFIED"
    rec = complete_window(track, rec, c_t=0.0, hour=3, weekend=False, window_label="19")
    if float(rec["C_LCB"]) > 0.0:
        assert int(rec["reset_trigger_after_window"]) == 1
        nxt = decide_window(track, window_id=20, hour=3, weekend=False)
        assert nxt["state_before_decision"] == "RESET"
        assert nxt["Gate"] == 0

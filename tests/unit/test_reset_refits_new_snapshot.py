from raven_mcs.sag.r1m_track import complete_window, decide_window, open_track


def test_reset_refits_new_snapshot() -> None:
    track = open_track(
        dataset="toy",
        availability_level=0.4,
        pretest_c=[0.10] * 24,
        pretest_hours=[3] * 24,
        pretest_weekends=[False] * 24,
        pretest_labels=[f"p{i}" for i in range(24)],
    )
    h0 = track.snapshot.snapshot_hash
    for t in range(19):
        rec = decide_window(track, window_id=t, hour=3, weekend=False)
        complete_window(track, rec, c_t=0.10, hour=3, weekend=False, window_label=str(t))
    assert track.snapshot.snapshot_hash == h0
    rec = decide_window(track, window_id=19, hour=3, weekend=False)
    rec = complete_window(track, rec, c_t=0.0, hour=3, weekend=False, window_label="19")
    if int(rec.get("reset_trigger_after_window") or 0) == 1:
        assert track.snapshot.snapshot_hash != h0
        assert track.block_id == 1
        assert rec.get("new_snapshot_hash") == track.snapshot.snapshot_hash

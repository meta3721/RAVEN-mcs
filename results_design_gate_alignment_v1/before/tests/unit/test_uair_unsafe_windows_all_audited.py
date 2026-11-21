from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_uair_unsafe_windows_all_audited() -> None:
    text = (ROOT / "results_sag_g1/round_r1h/boundary_audit/UAIR_UNSAFE_WINDOW_AUDIT.md").read_text(encoding="utf-8")
    for wid in (0, 1, 2, 51, 52):
        assert f"window {wid}" in text

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BANNED = (
    "Design is kept on SensorScope",
    "it is kept on SensorScope and dropped",
    "Design is dropped on U-Air",
)


def test_intro_has_no_old_dataset_gate_claim() -> None:
    main = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
    i = main.index(r"\section{Introduction}")
    j = main.index(r"\section{Related Work}")
    chunk = main[i:j]
    flat = " ".join(chunk.split())
    for phrase in BANNED:
        assert phrase not in chunk
    assert 'the coverage Gate is a separate diagnostic.' in flat
    assert "fixed before the window opens and held throughout it" in flat

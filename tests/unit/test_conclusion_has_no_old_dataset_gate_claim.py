from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BANNED = (
    "Design is kept on SensorScope",
    "Design remains part of the default",
    "the gated default drops Design",
)


def test_conclusion_has_no_old_dataset_gate_claim() -> None:
    main = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
    i = main.index(r"\section{Conclusion}")
    j = main.index(r"\section*{Data and Code Availability}")
    chunk = main[i:j]
    flat = " ".join(chunk.split())
    for phrase in BANNED:
        assert phrase not in chunk
        assert phrase not in flat
    assert 'With Design configured on' in flat

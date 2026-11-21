from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BANNED = (
    "Design is kept on SensorScope",
    "Design is dropped on U-Air",
    "gated default drops Design",
    "kept on SensorScope and dropped",
)


def _abstract(tex: str) -> str:
    i = tex.index(r"\begin{abstract}")
    j = tex.index(r"\end{abstract}")
    return tex[i:j]


def test_abstract_has_no_old_dataset_gate_claim() -> None:
    main = (ROOT / "TO_OVERLEAF_paper_tmc_r1_clean/main.tex").read_text(encoding="utf-8")
    chunk = _abstract(main)
    flat = " ".join(chunk.split())
    for phrase in BANNED:
        assert phrase not in chunk
    assert 'preconfigured opportunity Design factor' in flat

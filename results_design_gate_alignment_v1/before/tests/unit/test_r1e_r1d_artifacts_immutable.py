"""R1e must not rewrite sealed R1d artifacts."""

from __future__ import annotations

from pathlib import Path

from raven_mcs.utils.hashing import sha256_file

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "raven_mcs" / "experiments" / "run_sag_g1_r1e.py"
R1D_FILES = (
    "outputs/sag_g1_r1d/dynamic_cov/DYNAMIC_COV_PREDICTION.csv",
    "outputs/sag_g1_r1d/dynamic_cov/CURRENT_WINDOW_OPP_REALIZED.csv",
    "outputs/sag_g1_r1d/R1D_VERDICT.json",
    "outputs/sag_g1_r1d/target/TARGET_LAW_RULE_FROZEN.json",
)


def test_r1e_r1d_artifacts_immutable() -> None:
    text = SRC.read_text(encoding="utf-8")
    assert "outputs/sag_g1_r1d" in text
    assert "refusing to write into outputs/sag_g1_r1d" in text
    first = {rel: sha256_file(ROOT / rel) for rel in R1D_FILES}
    second = {rel: sha256_file(ROOT / rel) for rel in R1D_FILES}
    assert first == second
    prov = ROOT / "outputs" / "sag_g1_r1e" / "provenance" / "R1D_INPUT_SHA256SUMS.txt"
    if prov.is_file():
        listed = {}
        for line in prov.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            digest, rel = line.split("  ", 1)
            listed[rel.replace("\\", "/")] = digest
        for rel, digest in first.items():
            key = rel.replace("\\", "/")
            if key in listed:
                assert listed[key] == digest

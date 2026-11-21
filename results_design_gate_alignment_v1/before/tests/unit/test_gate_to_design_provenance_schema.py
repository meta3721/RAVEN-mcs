from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = (
    "dataset",
    "window_id",
    "block_id",
    "predictor_snapshot_id",
    "certificate_state",
    "n_cal",
    "C_hat",
    "q",
    "C_LCB",
    "tau_cov",
    "Gate_t",
    "Design_t",
    "design_branch",
)


def test_gate_to_design_provenance_schema() -> None:
    schema = (
        ROOT / "results_sag_g1/round_r1l_v12/interface/R1L_V12_GATE_TO_DESIGN_PROVENANCE_SCHEMA.md"
    ).read_text(encoding="utf-8")
    for field in REQUIRED:
        assert field in schema
    assert "DESIGN_ON" in schema
    assert "DESIGN_OFF" in schema
    from raven_mcs.sag.r1l_design import PROVENANCE_FIELDS

    assert tuple(REQUIRED) == PROVENANCE_FIELDS

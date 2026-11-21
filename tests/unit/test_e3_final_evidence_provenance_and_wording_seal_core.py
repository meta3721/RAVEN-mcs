from raven_mcs.e3.final_seal.core import all_identity_fields_match, reclassify_p2_record


def test_reclassification_separates_feasibility_from_optimality():
    result = reclassify_p2_record({"max_residual": 0.0})
    assert result["feasibility_status"] == "CERTIFIED_FEASIBLE"
    assert result["optimality_status"] == "NOT_RECONSTRUCTABLE"
    assert result["native_solver_status_available"] is False


def test_identity_requires_all_comparable_pairs_to_match():
    row = {
        "formal_eventtrace_hash": "a", "replay_eventtrace_hash": "a",
        "formal_config_hash": "b", "replay_config_hash": "b",
        "formal_target_artifact_sha256": "c", "replay_target_artifact_sha256": "c",
        "formal_stratum_identity_sha256": "d", "replay_stratum_identity_sha256": "d",
    }
    assert all_identity_fields_match(row)
    row["replay_config_hash"] = "different"
    assert not all_identity_fields_match(row)

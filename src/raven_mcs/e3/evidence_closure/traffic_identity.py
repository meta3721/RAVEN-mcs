"""Conservative, explicit Traffic E2/E3 source-vintage comparability policy."""

from __future__ import annotations

from typing import Any

RMSE_DECISION = "TRAFFIC_RMSE_MU_NOT_COMPARABLE_ACROSS_SOURCE_VINTAGES"


def build_identity_audit(e2_hash: str | None, e3_hash: str | None) -> dict[str, Any]:
    """Record known identities and source-level differences without overclaiming."""
    same_data = bool(e2_hash and e2_hash == e3_hash)
    checks: dict[str, Any] = {
        "processed_dataset_hash": {"e2": e2_hash, "e3": e3_hash, "equivalent": same_data},
        "split_hash": {"equivalent": None, "note": "Not jointly recoverable from saved artifacts."},
        "train_scaler": {"equivalent": False, "note": "E2 standardized reporting; E3 dual-domain measurement sync."},
        "feature_extraction": {"equivalent": False, "note": "E3 fixes evaluation extract_features wiring."},
        "target_preprocessing": {"equivalent": None}, "model_architecture": {"equivalent": None},
        "initialization_semantics": {"equivalent": None}, "optimizer_type": {"equivalent": None},
        "learning_rate": {"equivalent": None}, "local_steps": {"equivalent": None},
        "batch_size": {"equivalent": None}, "weight_decay": {"equivalent": None},
        "local_loss_code": {"equivalent": None}, "aggregation_code": {"equivalent": None},
        "evaluation_feature_extraction": {"equivalent": False, "note": "E3 source revision includes a feature-evaluation fix."},
        "inverse_transform_logic": {"equivalent": False, "note": "E3 provides synchronized physical and standardized domains."},
        "RMSE_mu_formula": {"equivalent": None}, "RMSE_mu_reporting_domain": {"equivalent": False},
        "EventTrace_identity": {"equivalent": True, "note": "E2 EventTraces reused by E3."},
        "target_h_i": {"equivalent": True}, "opportunity_stratum_s_i": {"equivalent": True},
        "method_source_revision": {"equivalent": False}, "runtime_config": {"equivalent": None},
    }
    return {
        "decision": RMSE_DECISION,
        "load_bearing_non_equivalences": ["feature_extraction", "evaluation_feature_extraction", "inverse_transform_logic", "method_source_revision"],
        "checks": checks,
        "interpretation": "A deterministic unit conversion cannot establish paired inferential identity after source/evaluation revision differences.",
    }


def comparison_policy() -> dict[str, Any]:
    return {
        "RMSE_mu": "N_A_NOT_COMPARABLE", "MAE_mu": "N_A_NOT_COMPARABLE",
        "Head_RMSE": "N_A_NOT_COMPARABLE", "Tail_RMSE": "N_A_NOT_COMPARABLE",
        "Delta_group": "DESCRIPTIVE_ONLY",
        "Delta_c_s": "N_A_NOT_COMPARABLE",
        "RMSE_rho": "N_A_NOT_COMPARABLE",
        "rationale": "No old-vs-new Traffic paired significance; reuse remains descriptive evidence. New-only Traffic methods may be compared within vintage.",
    }

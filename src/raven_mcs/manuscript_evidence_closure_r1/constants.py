"""Manuscript evidence closure R1 constants."""

from __future__ import annotations

ROUND = "RAVEN-MCS-MANUSCRIPT-EVIDENCE-CLOSURE-R1"
R2_ROOT = "paper_ready_r2"

METHOD_DISPLAY = {
    "fedavg_window": "FedAvg-Window",
    "fedasync_window": "FedAsync-Window",
    "flamf_timealign_adapted": "TimeAlign-Agg",
    "local_hajek": "Local-Hajek",
    "twostage_hajek": "TwoStage-Hajek",
    "inst_cal": "Inst-Cal",
    "debt_cal": "Debt-Cal",
    "raven": "RAVEN-MCS",
    "raven_simoracle": "RAVEN-SimOracle",
    "central_all": "Central-All",
    "central_delivered": "Central-Delivered",
}

METHOD_CANONICAL = {v: k for k, v in METHOD_DISPLAY.items()}

E3_MAIN_METHODS = [
    "FedAvg-Window",
    "FedAsync-Window",
    "TimeAlign-Agg",
    "Local-Hajek",
    "TwoStage-Hajek",
    "Inst-Cal",
    "Debt-Cal",
    "RAVEN-MCS",
]
E3_REFERENCE_METHODS = ["Central-All", "Central-Delivered", "RAVEN-SimOracle"]
E3_FIG_METHODS = [
    "FedAvg-Window",
    "FedAsync-Window",
    "TimeAlign-Agg",
    "Local-Hajek",
    "TwoStage-Hajek",
    "RAVEN-MCS",
]
E2_FIG_METHODS = [
    "FedAvg-Window",
    "FedAsync-Window",
    "TimeAlign-Agg",
    "TwoStage-Hajek",
    "RAVEN-MCS",
]
E4_CONFIGS = [
    "RAVEN-MCS",
    "RAVEN-w/o-Design",
    "RAVEN-w/o-Obs",
    "RAVEN-w/o-Use",
    "RAVEN-w/o-Inst",
    "RAVEN-w/o-Debt",
]
E4_COMPONENTS = ["Design", "Obs", "Use", "Inst", "Debt"]
E4_LABELS = {
    "Design": "ENDPOINT_TRADEOFF",
    "Obs": "ENDPOINT_TRADEOFF",
    "Use": "NO_CLEAR_EFFECT",
    "Inst": "ENDPOINT_TRADEOFF",
    "Debt": "STRUCTURAL_ONLY_SUPPORTED",
}

STATUSES = {
    "A": "MANUSCRIPT_EVIDENCE_R1_CLOSED_STOP_EXPERIMENTS_WRITE_PAPER",
    "B": "MANUSCRIPT_EVIDENCE_R1_CLOSED_TDRIVE_HIGH_VALUE_PENDING_APPROVAL",
    "C": "MANUSCRIPT_EVIDENCE_R1_BLOCKED_BY_CORE_DATA_CONFLICT",
    "D": "MANUSCRIPT_EVIDENCE_R1_BLOCKED_BY_CLAIM_EVIDENCE_MISMATCH",
}

FORBIDDEN_PHRASES = (
    "universally outperforms",
    "universal RMSE superiority",
    "all baselines significantly beaten",
    "all five components are indispensable",
    "Use is empirically necessary",
    "Debt has a large effect",
    "all P2 solutions are experimentally certified exactly optimal",
    "three-dataset homogeneous E3 superiority",
)

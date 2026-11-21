"""Table II unit/scale consistency repair R1 constants."""

from __future__ import annotations

ROUND = "RAVEN-MCS-FINAL-TABLE-II-UNIT-SCALE-CONSISTENCY-REPAIR-R1"
OUT_DIR = "RAVEN_MCS_FINAL_TABLE_II_REPAIR_R1"
SPEC = "RAVEN_MCS_FINAL_FIGURE_TABLE_PAPER_SPECIFICATION_SEAL_R1"
FREEZE = "RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1"
ZIP_NAME = "TO_SUBMIT_RAVEN_MCS_FINAL_TABLE_II_UNIT_SCALE_REPAIR_R1.zip"
STATUS_A = "RAVEN_MCS_TABLEII_REPAIR_R1_PASS_PAPER_SPEC_FINAL_SEALED"
STATUS_B = "RAVEN_MCS_TABLEII_REPAIR_R1_BLOCKED_BY_AUTHORITATIVE_SOURCE_CONFLICT"
STATUS_C = "RAVEN_MCS_TABLEII_REPAIR_R1_BLOCKED_BY_REMAINING_SCALE_MISMATCH"
STATUS_D = "RAVEN_MCS_TABLEII_REPAIR_R1_BLOCKED_BY_CROSS_ARTIFACT_CONFLICT"
STALE_UAIR_RATIO = 17.36325122
MATCH_ABS = 1e-10
ROUNDING_ABS = 5e-4
STALE_RATIO_TOL = 0.05
UAIR_STALE_FLOOR = 10.0
SUBDIRS = [
    "00_AUDIT",
    "01_REBUILT_TABLE_II",
    "02_STATISTICS_LINKAGE",
    "03_CROSS_ARTIFACT_CHECKS",
    "04_REGISTRY_UPDATES",
    "05_SYMBOL_NAMING_REPAIR",
    "06_PROVENANCE",
    "06_PROVENANCE/SUPERSEDED_TABLE_II",
    "07_REPORT",
]
METHOD_CANONICAL = {
    "FedAvg-Window": "fedavg_window",
    "FedAsync-Window": "fedasync_window",
    "TimeAlign-Agg": "flamf_timealign_adapted",
    "Local-Hajek": "local_hajek",
    "TwoStage-Hajek": "twostage_hajek",
    "Inst-Cal": "inst_cal",
    "Debt-Cal": "debt_cal",
    "RAVEN-MCS": "raven",
    "Central-All": "central_all",
    "Central-Delivered": "central_delivered",
    "RAVEN-SimOracle": "raven_simoracle",
}
PRIMARY_METHODS = {
    "FedAvg-Window",
    "FedAsync-Window",
    "TimeAlign-Agg",
    "Local-Hajek",
    "TwoStage-Hajek",
    "Inst-Cal",
    "Debt-Cal",
    "RAVEN-MCS",
}

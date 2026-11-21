"""Final paper data asset freeze R1 constants."""

from __future__ import annotations

ROUND = "RAVEN-MCS-FINAL-PAPER-DATA-ASSET-FREEZE-R1"
OUT_DIR = "RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1"

STATUSES = {
    "A": "RAVEN_MCS_FINAL_DATA_R1_FROZEN_ALL_MANUSCRIPT_CORE_DATA_READY",
    "B": "RAVEN_MCS_FINAL_DATA_R1_FROZEN_CORE_READY_SUPPORTING_GAPS_REMAIN",
    "C": "RAVEN_MCS_FINAL_DATA_R1_BLOCKED_BY_CORE_DATA_CONFLICT",
    "D": "RAVEN_MCS_FINAL_DATA_R1_BLOCKED_BY_PROVENANCE_GAP",
    "E": "RAVEN_MCS_FINAL_DATA_R1_BLOCKED_BY_MISSING_CORE_EVIDENCE",
}

E4_LABELS = {
    "Design": "ENDPOINT_TRADEOFF",
    "Obs": "ENDPOINT_TRADEOFF",
    "Use": "NO_CLEAR_EFFECT",
    "Inst": "ENDPOINT_TRADEOFF",
    "Debt": "STRUCTURAL_ONLY_SUPPORTED",
}

SUBDIRS = [
    "00_MASTER_CATALOG",
    "01_PAPER_CORE",
    "01_PAPER_CORE/E1",
    "01_PAPER_CORE/E2",
    "01_PAPER_CORE/E3",
    "01_PAPER_CORE/E4",
    "01_PAPER_CORE/DATASET_METADATA",
    "01_PAPER_CORE/STATISTICS",
    "01_PAPER_CORE/CLAIM_MAPS",
    "02_PAPER_SUPPORTING",
    "03_APPENDIX_CANDIDATES",
    "04_ALL_RUN_METRICS",
    "05_WINDOW_LEVEL",
    "06_SELECTION_PROCESS",
    "06_SELECTION_PROCESS/propensity",
    "07_WEIGHTS",
    "07_WEIGHTS/local_hajek_provenance",
    "08_CALIBRATION_DEBT",
    "08_CALIBRATION_DEBT/calibration",
    "08_CALIBRATION_DEBT/debt",
    "09_P2_SOLVER",
    "10_ESS_VARIANCE",
    "11_RUNTIME_SYSTEM",
    "12_EVENTTRACES",
    "12_EVENTTRACES/E2",
    "12_EVENTTRACES/E3",
    "12_EVENTTRACES/E4",
    "12_EVENTTRACES/TDRIVE_PROTOCOL_ONLY",
    "13_CONFIGS",
    "14_SOURCE_PROVENANCE",
    "15_FIGURE_SOURCES",
    "16_TABLE_SOURCES",
    "17_SUPERSEDED",
    "18_INVALID_CANARY",
    "19_NOT_COMPARABLE",
    "20_TDRIVE_RESERVE",
    "21_MANIFESTS",
    "22_REPORTS",
]

CATALOG_FIELDS = [
    "asset_id",
    "relative_asset_path",
    "original_path",
    "filename",
    "file_type",
    "size_bytes",
    "sha256",
    "created_or_modified_time",
    "round",
    "dataset",
    "scenario",
    "method",
    "configuration",
    "seed",
    "seed_range",
    "generation",
    "granularity",
    "metric_family",
    "scientific_object",
    "evidence_status",
    "paper_role",
    "paper_eligible",
    "appendix_eligible",
    "rebuttal_useful",
    "source_authority",
    "supersedes",
    "superseded_by",
    "comparability_status",
    "claim_ids",
    "rq_ids",
    "figure_candidate",
    "table_candidate",
    "provenance_status",
    "notes",
]

NA = "MISSING_NOT_RECORDED"
N_A = "N_A_NOT_APPLICABLE"

CORE_ZIP = "RAVEN_MCS_FINAL_PAPER_DATA_CORE_R1.zip"
FULL_ZIP = "RAVEN_MCS_FINAL_PAPER_DATA_FULL_R1.zip"

CORE_PREFIXES = (
    "00_MASTER_CATALOG/",
    "01_PAPER_CORE/",
    "04_ALL_RUN_METRICS/",
    "13_CONFIGS/",
    "14_SOURCE_PROVENANCE/",
    "15_FIGURE_SOURCES/",
    "16_TABLE_SOURCES/",
    "21_MANIFESTS/",
    "22_REPORTS/",
)

CORE_ROOT_FILES = (
    "RAVEN_MCS_FINAL_PAPER_DATA_HANDOFF_R1.txt",
    "RAVEN_MCS_FINAL_PAPER_DATA_ASSET_FREEZE_R1_REPORT.md",
    "FDAF_GATES_R1.json",
)

REFERENCE_METHODS = {"Central-All", "Central-Delivered", "RAVEN-SimOracle", "central_all", "central_delivered", "raven_simoracle"}

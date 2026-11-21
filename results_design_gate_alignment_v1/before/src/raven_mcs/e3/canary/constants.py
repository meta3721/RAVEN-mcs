"""Constants for E3-MULTIDATASET-REAL-RUNNER-CANARY-R1."""

from __future__ import annotations

ROUND = "E3-MULTIDATASET-REAL-RUNNER-CANARY-R1"
CANARY_SEED = 31001
FORMAL_SEEDS = list(range(30001, 30021))
SCENARIO = "complete_aligned"
M_MC = 2000
REGISTRY_SHA256 = "7d9b8292522b6fbcc15d83ebb065fc8a73b79787ed643aea49c48f30596acbc7"

# Frozen processed atomic_units.parquet hashes (protocol closure)
FROZEN_DATASET_HASHES = {
    "sensorscope": "47581d5b04d3795b3fe663198ba32a53e83f35707718a82bd1ec0662daff88ce",
    "uair": "0d57445890f7e1a21038c17106a8e7f332e95fe13fe81713f24b8fd0ab254eed",
    "traffic": "db45a2ecc66c27abeaf58b0c03ce66de7bfaf6727f4523ea06ef226a9ce3de50",
}

E2_TRAFFIC_REUSED_METHODS = [
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "twostage_hajek",
    "raven",
]

ALL_CANONICAL_METHODS = [
    "fedavg_window",
    "fedasync_window",
    "flamf_timealign_adapted",
    "local_hajek",
    "twostage_hajek",
    "inst_cal",
    "debt_cal",
    "raven",
    "raven_simoracle",
    "central_all",
    "central_delivered",
]

PHASE1 = [
    ("sensorscope", "fedavg_window"),
    ("sensorscope", "raven"),
    ("sensorscope", "raven_simoracle"),
    ("sensorscope", "central_delivered"),
    ("uair", "fedavg_window"),
    ("uair", "raven"),
    ("uair", "raven_simoracle"),
    ("uair", "central_delivered"),
    ("traffic", "local_hajek"),
    ("traffic", "raven_simoracle"),
    ("traffic", "central_delivered"),
]

PHASE2 = [
    ("sensorscope", "fedasync_window"),
    ("sensorscope", "flamf_timealign_adapted"),
    ("sensorscope", "local_hajek"),
    ("sensorscope", "twostage_hajek"),
    ("sensorscope", "inst_cal"),
    ("sensorscope", "debt_cal"),
    ("sensorscope", "central_all"),
    ("uair", "fedasync_window"),
    ("uair", "flamf_timealign_adapted"),
    ("uair", "local_hajek"),
    ("uair", "twostage_hajek"),
    ("uair", "inst_cal"),
    ("uair", "debt_cal"),
    ("uair", "central_all"),
    ("traffic", "inst_cal"),
    ("traffic", "debt_cal"),
    ("traffic", "central_all"),
]

TRAFFIC_CANARY_METHODS = [
    "local_hajek",
    "inst_cal",
    "debt_cal",
    "raven_simoracle",
    "central_all",
    "central_delivered",
]

HORIZON_JSON = {
    "sensorscope": "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json",
    "uair": "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json",
    "traffic": "configs/frozen/e3_multidataset_protocol_closure/traffic/horizon.json",
}

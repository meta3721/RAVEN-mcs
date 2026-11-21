"""T-Drive real-mobility protocol seal R1 constants. Not an experiment round."""

from __future__ import annotations

ROUND = "RAVEN-MCS-TDRIVE-REAL-MOBILITY-PROTOCOL-SEAL-R1"
PROTOCOL_ID = "TDRIVE_REAL_MOBILITY_PROTOCOL_R1"
DATASET_CANONICAL = "tdrive_speed"
DATASET_PAPER = "T-Drive-Speed"
SCENARIO = "complete_aligned"
SPLIT_ID = "processed_temporal_60_20_20_slot"
MU_TOLERANCE = 1e-12
EPS_ZERO = 1e-12
ALPHA = 0.05
FORMAL_SEEDS = list(range(30001, 30011))
CANARY_SEED = 30001
MICRO_FIXTURE_SEED = 31999
MEAN_OBSERVATION_RATE = 0.35
S_MAX = 5
WINDOW_DURATION = 1.0
M_MC = 2000
LOCAL_STEPS = 2
ALPHA_MAX = 0.5
E_MIN = 3.0
LAMBDA_GROUP = 1.0
LAMBDA_BETA = 1.0
LAMBDA_V = 0.1
LAMBDA_S = 0.1

# Paper display name → E3 canonical implementation ID.
METHODS = (
    {
        "slot": "M1",
        "display": "FedAvg-Window",
        "canonical": "fedavg_window",
        "role": "baseline",
    },
    {
        "slot": "M2",
        "display": "FedAsync-Window",
        "canonical": "fedasync_window",
        "role": "baseline",
    },
    {
        "slot": "M3",
        "display": "TimeAlign-Agg",
        "canonical": "flamf_timealign_adapted",
        "role": "baseline",
        "alias_note": "E3 canonical ID flamf_timealign_adapted; do not substitute timealign_agg or flamf_original",
    },
    {
        "slot": "M4",
        "display": "TwoStage-Hajek",
        "canonical": "twostage_hajek",
        "role": "baseline",
    },
    {
        "slot": "M5",
        "display": "RAVEN-MCS",
        "canonical": "raven",
        "role": "focal",
    },
)

FORBIDDEN_METHODS = (
    "local_hajek",
    "inst_cal",
    "debt_cal",
    "raven_simoracle",
    "central_all",
    "central_delivered",
    "raven_wo_design",
    "raven_wo_obs",
    "raven_wo_use",
    "raven_wo_inst",
    "raven_wo_debt",
    "timealign_agg",
    "flamf_original",
)

PRIMARY_METRICS = ("Delta_group", "Delta_c_s", "RMSE_mu")
STRUCTURAL_PRIMARY = ("Delta_group", "Delta_c_s")
PREDICTIVE_PRIMARY = ("RMSE_mu",)

H_FALLBACK_LABEL = "PRE_REGISTERED_PROTOCOL_FALLBACK"
H_GROUPS = (
    {"h_id": "H1", "hour_start": 0, "hour_end": 6, "block": 0},
    {"h_id": "H2", "hour_start": 6, "hour_end": 12, "block": 1},
    {"h_id": "H3", "hour_start": 12, "hour_end": 18, "block": 2},
    {"h_id": "H4", "hour_start": 18, "hour_end": 24, "block": 3},
)

STATUSES = {
    "A": "TDRIVE_PROTOCOL_R1_SEALED_READY_FOR_1SEED_CANARY",
    "B": "TDRIVE_PROTOCOL_R1_BLOCKED_BY_DATA_SEMANTICS",
    "C": "TDRIVE_PROTOCOL_R1_BLOCKED_BY_SPLIT_OR_LEAKAGE",
    "D": "TDRIVE_PROTOCOL_R1_BLOCKED_BY_EVENTTRACE_SEMANTICS",
    "E": "TDRIVE_PROTOCOL_R1_BLOCKED_BY_METHOD_OR_CONFIG_IDENTITY",
    "F": "TDRIVE_PROTOCOL_R1_BLOCKED_BY_PROVENANCE_CONFLICT",
}

METHOD_SOURCE_FILES = {
    "fedavg_window": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
    ],
    "fedasync_window": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
    ],
    "flamf_timealign_adapted": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
    ],
    "twostage_hajek": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
        "src/raven_mcs/correction/hajek.py",
    ],
    "raven": [
        "src/raven_mcs/aggregation/method_policy.py",
        "src/raven_mcs/aggregation/methods.py",
        "src/raven_mcs/training/window_runner.py",
        "src/raven_mcs/aggregation/p2_cvxpy.py",
        "src/raven_mcs/correction/hajek.py",
        "src/raven_mcs/metrics/debt.py",
    ],
}

INVENTORY_CANDIDATES = (
    "data/raw/tdrive_speed",
    "data/processed/tdrive_speed",
    "data/interim/tdrive_speed",
    "data/manifests/tdrive_speed_manifest.json",
    "configs/dataset/tdrive_speed.yaml",
    "configs/experiment/E9_tdrive.yaml",
    "src/raven_mcs/data/tdrive.py",
    "src/raven_mcs/data/split.py",
    "src/raven_mcs/data/controlled.py",
    "src/raven_mcs/data/fleet.py",
    "src/raven_mcs/data/schema.py",
    "src/raven_mcs/data/pipeline.py",
    "src/raven_mcs/data/base.py",
    "src/raven_mcs/e3/real_runner/generator_r3.py",
    "src/raven_mcs/e3/real_runner/stage2_r3.py",
    "src/raven_mcs/e3/real_runner/constants.py",
    "src/raven_mcs/e3/real_runner/simoracle_q.py",
    "src/raven_mcs/simulation/event_trace.py",
    "src/raven_mcs/metrics/distribution.py",
    "src/raven_mcs/metrics/accuracy.py",
    "src/raven_mcs/e3/delta_cs_rho/delta_cs_v6.py",
    "src/raven_mcs/e3/formal/stats.py",
    "src/raven_mcs/aggregation/method_policy.py",
    "paper_ready_r2/08_tdrive_readiness",
    "paper_ready_r1/08_tdrive_readiness",
    "src/raven_mcs/paper_data_r2/tdrive.py",
    "src/raven_mcs/paper_data_r1/tdrive_readiness.py",
    "artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json",
    "configs/frozen/e3_target_pair_metric_final_r1/E3_FINAL_INTEGRATION_SOURCE_HASHES.json",
    "configs/frozen/e3_multidataset_protocol_closure/sensorscope/stage2_eligibility.json",
)

"""Frozen support-consumption protocol constants.

These values are the predeclared gates. They are not search parameters.
"""

from __future__ import annotations

PROTOCOL_NAME = "support-consumption-v1"
MAIN_BLOCK = "measured-O"
REVIEW_BLOCK = "visit"
S_MAX = 5
RESIDENCE_H = 2
POOL_CAP = 64
COMPLEMENT_MARGIN = 0.01
ALPHA_MAX = 0.5
E_MIN = 3.0
A_MAX = 20.0
P_MIN = 0.05
PI_MIN = 1e-6
LOCAL_STEPS = 2
SERVER_LR = 0.01
NUM_WINDOWS = 100
NUM_GROUPS = 4
BACKBONE = "CommonNDMF"
SERVER_OPTIMIZER = "one_weighted_sgd_step"
PROPENSITY_PRIOR = 0.2
PROPENSITY_MIN_SAMPLES = 5
PROPENSITY_L2 = 1e-2
COMPOSITION_TOLERANCE = 1e-6
DEVELOPMENT_SEEDS = {
    "measured-O": (33001, 33002, 33003),
    "visit": (32001, 32002, 32003),
}
CACHE_ARMS = ("I-Proj", "F1-Proj", "F2-Proj", "S-Proj")
EXTERNAL_ARMS = ("TwoStage-Hájek", "FedAvg-Window")
PER_SEED_COMPLEMENT_MIN = 0.05
POOLED_COMPLEMENT_MIN = 0.10
CROSS_CLOSE_COMMIT_MIN = 0.10
MEAN_D_IMPROVEMENT_MIN = 0.005
RESIDENCE_QUANTILE = 0.95
CPU_BUDGET = {"P0": 300.0, "P1": 600.0, "P2": 300.0}
WALL_BUDGET = {"P0": 600.0, "P1": 1200.0, "P2": 900.0}
REGION_ORDER = ("region0", "region1", "region2", "region3")

# Age at a close is close_index - arrival_close. The arrival close has age 0.
# Age 2 triggers deadline release. Age greater than 2 expires.
# Complementary-release denominator is every close, including empty closes.
# Pooled denominator is the three development seeds times 100 closes.
# Cross-close commit denominator is every positive-mass delivered message.
# Time-average D starts at 1 and carries the last release distance forward.
# Ordinary-cache domination requires strictly lower mean D, mean residence,
# and the 0.95 linear quantile of residence, against F1-Proj or F2-Proj.

"""Unit tests for E3 stratum identity and Traffic reuse seal."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from raven_mcs.e3.delta_cs_rho.atomic_rho import (
    analytical_atomic_rmse_rho_test,
    within_group_heterogeneity_test,
)
from raven_mcs.e3.delta_cs_rho.delta_cs_v6 import nonsymmetric_delta_cs_analytical_test
from raven_mcs.e3.delta_cs_rho.stratum import opportunity_stratum_definition
from raven_mcs.e3.protocol_closure.reuse_guard import (
    DuplicateReusedTrafficRunBlocked,
    assert_schedulable_e3_run,
)
from raven_mcs.e3.stratum_seal.constants import TRAFFIC_PUBLIC_TARGET_MAPPING_HASH
from raven_mcs.e3.stratum_seal.remap import apply_sealed_opportunity_stratum
from raven_mcs.e3.stratum_seal.traffic_regions import (
    TrafficStratumIdentityError,
    load_frozen_traffic_station_regions,
)

ROOT = Path(__file__).resolve().parents[2]


def test_traffic_four_region_mapping():
    mapping, meta = load_frozen_traffic_station_regions(ROOT)
    assert len(mapping) == 43
    assert len(set(mapping.values())) == 4
    assert meta["mapping_hash"] == TRAFFIC_PUBLIC_TARGET_MAPPING_HASH
    assert meta["status"] == "FROZEN_IDENTITY_RECOVERED"


def test_traffic_stratum_not_344():
    atomic = pd.read_parquet(ROOT / "data/processed/traffic/atomic_units.parquet")
    assert atomic["opportunity_stratum"].nunique() == 344  # raw processed
    remapped, meta = apply_sealed_opportunity_stratum(atomic, dataset="traffic", root=ROOT)
    assert meta["n_unique_strata"] <= 32
    assert remapped["opportunity_stratum"].nunique() == 32
    assert all(str(s).startswith("region") for s in remapped["opportunity_stratum"].unique())


def test_sensorscope_uair_identity_confirmed():
    d = opportunity_stratum_definition(ROOT)
    assert d["datasets"]["sensorscope"]["n_legal_opportunity_strata"] == 440
    assert d["datasets"]["uair"]["n_legal_opportunity_strata"] == 288
    ss = pd.read_parquet(ROOT / "data/processed/sensorscope/atomic_units.parquet")
    ua = pd.read_parquet(ROOT / "data/processed/uair/atomic_units.parquet")
    _, mss = apply_sealed_opportunity_stratum(ss, dataset="sensorscope", root=ROOT)
    _, mua = apply_sealed_opportunity_stratum(ua, dataset="uair", root=ROOT)
    assert mss["remapped"] is False
    assert mua["remapped"] is False
    assert ss["opportunity_stratum"].nunique() == 440
    assert ua["opportunity_stratum"].nunique() == 288


def test_delta_cs_and_rho_still_pass():
    toy = nonsymmetric_delta_cs_analytical_test()
    assert toy["status"] == "PASS"
    assert toy["h_independence"]
    assert within_group_heterogeneity_test()["status"] == "PASS"
    assert analytical_atomic_rmse_rho_test()["status"] == "PASS"


def test_traffic_sealed_runs_not_schedulable():
    with pytest.raises(DuplicateReusedTrafficRunBlocked):
        assert_schedulable_e3_run(
            dataset="traffic", scenario="complete_aligned", seed=30001, method="raven"
        )

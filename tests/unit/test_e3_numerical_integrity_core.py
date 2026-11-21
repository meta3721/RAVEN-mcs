"""Core audit helpers for the numerical-integrity clean canary."""

from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from raven_mcs.e3.canary.dataset_load import apply_train_zscore_standardization
from raven_mcs.e3.canary.schedule import build_canary_matrix
from raven_mcs.e3.numerical.source_freeze import build_source_freeze_payload, hash_source_files


def test_canary_matrix_remains_28() -> None:
    assert build_canary_matrix()["n_logical_runs"] == 28


def test_source_freeze_hashes_requested_files(tmp_path) -> None:
    (tmp_path / "sample.py").write_text("x = 1\n", encoding="utf-8")
    assert hash_source_files(tmp_path, ["sample.py"])["sample.py"]
    payload = build_source_freeze_payload(tmp_path)
    assert payload["status"] == "FROZEN"
    assert payload["code_must_not_change_after_freeze"] is True


def test_zscore_rebuilds_measurement_index() -> None:
    dataset = SimpleNamespace(
        target_mean=10.0,
        target_std=2.0,
        _client_df=pd.DataFrame(
            [{"client_id": "c1", "unit_id": "u1", "potential_measurement": 12.0}]
        ),
        _atomic_df=pd.DataFrame([{"target_value": 8.0}]),
    )
    result = apply_train_zscore_standardization(dataset)
    assert result["status"] == "APPLIED"
    assert dataset._client_df.loc[0, "potential_measurement"] == 1.0
    assert dataset._atomic_df.loc[0, "target_value"] == -1.0
    assert dataset._measurement_index[("c1", "u1")] == 1.0

"""Tiny controlled fixture for non-performance correctness smoke."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.data.base import DatasetMetadata
from raven_mcs.data.processed_dataset import ProcessedDataset
from raven_mcs.utils.serialization import dump_json


def build_correctness_fixture(out_dir: Path) -> dict[str, Any]:
    """Create a tiny real-format processed dataset + client map (2 clients).

    Critical: every train opportunity stratum also appears in test support so
    pi_tar(k,s) > 0 for strata used during EventTrace training (zeta non-zero).
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    client_rows = []
    # 4 blocks × 2 spatial × (1 train + 1 test) = 16 units
    for block in range(4):
        for spatial_i, spatial in enumerate(["n0", "n1"]):
            client = f"client-{spatial_i:03d}"
            tg = f"{spatial}::block{block}"
            os_ = f"{spatial}::block{block}::weekday"
            for split, t_off in (("train", 0), ("test", 1)):
                t = block * 2 + t_off
                unit_id = f"{spatial}_t{t:05d}"
                rows.append(
                    {
                        "unit_id": unit_id,
                        "spatial_id": spatial,
                        "absolute_time": pd.Timestamp("2020-01-01", tz="UTC")
                        + pd.Timedelta(hours=t * 6),
                        "time_index": t,
                        "target_value": float(1.0 + spatial_i + 0.1 * t),
                        "split": split,
                        "target_group": tg,
                        "opportunity_stratum": os_,
                        "public_features": {
                            "hour_sin": 0.0,
                            "hour_cos": 1.0,
                            "time_block": float(block),
                            "weekday": 1.0,
                        },
                        "support_flag": True,
                        "is_warmup": False,
                    }
                )
                client_rows.append(
                    {
                        "client_id": client,
                        "unit_id": unit_id,
                        "potential_measurement": float(1.0 + spatial_i + 0.1 * t),
                        "controlled_generator_parameters": {"fixture": 1.0},
                        "split": split,
                        "source_trace_id": "fixture",
                    }
                )
    # small validation holdout (block0 twins) — not used by pi_tar
    for spatial_i, spatial in enumerate(["n0", "n1"]):
        t = 100 + spatial_i
        unit_id = f"{spatial}_t{t:05d}"
        rows.append(
            {
                "unit_id": unit_id,
                "spatial_id": spatial,
                "absolute_time": pd.Timestamp("2020-01-01", tz="UTC")
                + pd.Timedelta(hours=t * 6),
                "time_index": t,
                "target_value": float(2.0 + spatial_i),
                "split": "validation",
                "target_group": f"{spatial}::block0",
                "opportunity_stratum": f"{spatial}::block0::weekday",
                "public_features": {
                    "hour_sin": 0.0,
                    "hour_cos": 1.0,
                    "time_block": 0.0,
                    "weekday": 1.0,
                },
                "support_flag": True,
                "is_warmup": False,
            }
        )
        client_rows.append(
            {
                "client_id": f"client-{spatial_i:03d}",
                "unit_id": unit_id,
                "potential_measurement": float(2.0 + spatial_i),
                "controlled_generator_parameters": {"fixture": 1.0},
                "split": "validation",
                "source_trace_id": "fixture",
            }
        )

    atomic = pd.DataFrame(rows)
    clients = pd.DataFrame(client_rows)
    atomic.to_parquet(out_dir / "atomic_units.parquet", index=False)
    clients.to_parquet(out_dir / "client_measurements.parquet", index=False)
    mapping = {"n0": "client-000", "n1": "client-001"}
    dump_json(mapping, out_dir / "spatial_to_client.json")
    return {
        "data_dir": str(out_dir),
        "spatial_to_client": mapping,
        "n_train_units": int((atomic["split"] == "train").sum()),
        "n_test_units": int((atomic["split"] == "test").sum()),
    }


def load_fixture_dataset(data_dir: Path) -> ProcessedDataset:
    meta = DatasetMetadata(
        dataset="e3_correctness_fixture",
        target_name="synthetic",
        target_unit="unitless",
        spatial_unit="station",
        time_unit="hour",
        source_name="e3-correctness-fixture",
        source_url="local://fixture",
        raw_license="internal-test",
        filtering_rules=("finite synthetic values only",),
    )
    return ProcessedDataset(data_dir, meta)

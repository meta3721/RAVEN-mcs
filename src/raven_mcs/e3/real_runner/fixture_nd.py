"""Non-degenerate correctness fixture (3 clients, multi-window, multi-delivery)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from raven_mcs.data.base import DatasetMetadata
from raven_mcs.data.processed_dataset import ProcessedDataset
from raven_mcs.utils.serialization import dump_json


def build_nondegenerate_fixture(out_dir: Path) -> dict[str, Any]:
    """3 clients × 4 blocks × (train+test) with non-uniform targets."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    client_rows = []
    spatials = ["n0", "n1", "n2"]
    for block in range(4):
        for spatial_i, spatial in enumerate(spatials):
            client = f"client-{spatial_i:03d}"
            tg = f"{spatial}::block{block}"
            os_ = f"{spatial}::block{block}::weekday"
            for split, t_off in (("train", 0), ("test", 1)):
                t = block * 2 + t_off + spatial_i * 20
                unit_id = f"{spatial}_t{t:05d}"
                # Non-uniform potential values
                y = float(1.0 + 0.5 * spatial_i + 0.2 * block + (0.3 if split == "test" else 0.0))
                rows.append(
                    {
                        "unit_id": unit_id,
                        "spatial_id": spatial,
                        "absolute_time": pd.Timestamp("2020-01-01", tz="UTC")
                        + pd.Timedelta(hours=t * 6),
                        "time_index": t,
                        "target_value": y,
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
                        "potential_measurement": y,
                        "controlled_generator_parameters": {"fixture": 1.0},
                        "split": split,
                        "source_trace_id": "fixture_nd",
                    }
                )
    atomic = pd.DataFrame(rows)
    clients = pd.DataFrame(client_rows)
    atomic.to_parquet(out_dir / "atomic_units.parquet", index=False)
    clients.to_parquet(out_dir / "client_measurements.parquet", index=False)
    mapping = {s: f"client-{i:03d}" for i, s in enumerate(spatials)}
    dump_json(mapping, out_dir / "spatial_to_client.json")
    return {
        "data_dir": str(out_dir),
        "spatial_to_client": mapping,
        "n_train_units": int((atomic["split"] == "train").sum()),
        "n_test_units": int((atomic["split"] == "test").sum()),
        "n_clients": 3,
        "n_spatial_time_groups": int(atomic["target_group"].nunique()),
    }


def load_nd_fixture(data_dir: Path) -> ProcessedDataset:
    meta = DatasetMetadata(
        dataset="e3_nondegenerate_fixture",
        target_name="synthetic",
        target_unit="unitless",
        spatial_unit="station",
        time_unit="hour",
        source_name="e3-nd-fixture",
        source_url="local://fixture_nd",
        raw_license="internal-test",
        filtering_rules=("finite synthetic values only",),
    )
    return ProcessedDataset(data_dir, meta)

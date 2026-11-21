from pathlib import Path
import pandas as pd

from raven_mcs.e3.canary.dataset_load import load_paper_dataset

ROOT = Path(__file__).resolve().parents[2]


def test_raw_timestamp_retention() -> None:
    ds = load_paper_dataset(ROOT, "sensorscope")
    assert "absolute_time" in ds.atomic_df.columns
    ts = pd.to_datetime(ds.atomic_df["absolute_time"], utc=True)
    assert ts.notna().all()

"""Training label boundary for the frozen P0 panel.

The training entry can read D_fit and D_tune labels only.
V, A, and T label requests are refused before any label file is opened.
This module does not fit a model and does not compute error metrics.
"""
import csv
from pathlib import Path


class DataAccess:
    def __init__(self, root):
        self.root = Path(root)

    def training_labels(self, split):
        if split not in ("D_fit", "D_tune", "D"):
            raise PermissionError("training entry refuses labels for split " + str(split))
        parts = ("D_fit", "D_tune") if split == "D" else (split,)
        rows = []
        for part in parts:
            path = self.root / "data" / f"labels_{part}.csv"
            with path.open(encoding="utf-8", newline="") as handle:
                rows.extend(list(csv.DictReader(handle)))
        return rows

    def training_frame(self, split):
        labels = self.training_labels(split)
        parts = {"D_fit", "D_tune"} if split == "D" else {split}
        features = {}
        with (self.root / "data" / "features.csv").open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row["split"] not in parts:
                    continue
                if row["row_id"] in features:
                    raise RuntimeError("duplicate feature row_id " + row["row_id"])
                features[row["row_id"]] = row
        merged = []
        for label in labels:
            feature = features.get(label["row_id"])
            if feature is None:
                raise RuntimeError("label without D feature " + label["row_id"])
            item = dict(feature)
            item["reference"] = label["reference"]
            merged.append(item)
        return merged

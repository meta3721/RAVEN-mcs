"""Interface check only. No model is trained, so prediction invariance is not claimed."""
import csv
from pathlib import Path

from data_access import DataAccess


def _header(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return handle.readline()


def check(root, require_labels):
    root = Path(root)
    access = DataAccess(root)
    checks = []

    def add(name, ok, **extra):
        item = {"check": name, "ok": bool(ok)}
        item.update(extra)
        checks.append(item)

    for split in ("V", "A", "T"):
        try:
            access.training_labels(split)
            add("training_refuses_" + split, False, detail="call returned rows")
        except PermissionError as exc:
            add("training_refuses_" + split, True, detail=str(exc))

    data = root / "data"
    for name in ("labels_A.csv", "labels_T.csv"):
        add("file_absent_" + name, not (data / name).exists())

    meta_path = root / "reference_events_metadata.csv"
    if meta_path.exists():
        bad = 0
        with meta_path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("split") in ("A", "T") and row.get("reference_value", "") != "":
                    bad += 1
        add("A_T_reference_values_withheld", bad == 0, leaked_rows=bad)
    else:
        add("A_T_reference_values_withheld", False, detail="metadata missing")

    panel_path = root / "evaluation_panel.csv"
    if panel_path.exists():
        header = _header(panel_path).lower()
        add(
            "panel_has_no_concentration_column",
            "pm25" not in header and "reference" not in header,
        )
    else:
        add("panel_has_no_concentration_column", False, detail="panel missing")

    excluded_path = root / "excluded_device_days.csv"
    if excluded_path.exists():
        header = _header(excluded_path).lower()
        add("excluded_table_has_no_concentration_column", "pm25" not in header and "reference_value" not in header)
    else:
        add("excluded_table_has_no_concentration_column", False, detail="excluded table missing")

    if require_labels:
        counts = {}
        for split in ("D_fit", "D_tune"):
            try:
                rows = access.training_labels(split)
                counts[split] = len(rows)
                add("training_reads_" + split, True, n=len(rows))
            except Exception as exc:
                counts[split] = None
                add("training_reads_" + split, False, detail=type(exc).__name__ + ": " + str(exc))
        try:
            union = access.training_labels("D")
            expected = (counts.get("D_fit") or 0) + (counts.get("D_tune") or 0)
            add("training_D_is_only_D_fit_plus_D_tune", len(union) == expected, n=len(union), expected=expected)
        except Exception as exc:
            add("training_D_is_only_D_fit_plus_D_tune", False, detail=str(exc))
        try:
            frame = access.training_frame("D_fit")
            add("training_frame_D_fit", len(frame) == (counts.get("D_fit") or -1), n=len(frame))
        except Exception as exc:
            add("training_frame_D_fit", False, detail=str(exc))
        try:
            access.training_frame("A")
            add("training_frame_refuses_A", False, detail="call returned rows")
        except PermissionError:
            add("training_frame_refuses_A", True)
        feature_header = _header(data / "features.csv").lower() if (data / "features.csv").exists() else ""
        add("features_have_no_reference_column", "pm25fm" not in feature_header and "reference" not in feature_header)

    passed = all(item["ok"] for item in checks)
    return {
        "passed": passed,
        "require_labels": require_labels,
        "checks": checks,
        "model_trained": False,
        "prediction_invariance": "NOT_RUN",
    }

"""I/O helpers for paper-data packaging (read sealed sources, write only under paper_ready_r1/)."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


MISSING = "MISSING_NOT_RECORDED"
N_A = "N_A_NOT_APPLICABLE"
NOT_COMPARABLE = "NOT_COMPARABLE"
INVALID = "INVALID"
SUPERSEDED = "SUPERSEDED"
VALID = "VALID"


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ensure_dir(path: Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, obj: Any) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    return path


def write_text(path: Path, text: str) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")
    return path


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fieldnames: Sequence[str] | None = None) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    if fieldnames is None:
        keys: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for k in row.keys():
                if k not in seen:
                    seen.add(k)
                    keys.append(k)
        fieldnames = keys
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fieldnames), extrasaction="ignore")
        w.writeheader()
        for row in rows:
            out = {}
            for k in fieldnames:
                v = row.get(k, "")
                out[k] = "" if v is None else v
            w.writerow(out)
    return path


def read_csv(path: Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def copy_file(src: Path, dst: Path) -> Path:
    src = Path(src)
    dst = Path(dst)
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)
    return dst


def safe_float(v: Any) -> float | None:
    if v is None:
        return None
    s = str(v).strip()
    if s == "" or s.upper() in {MISSING, N_A, NOT_COMPARABLE, "NAN", "NONE", "NULL"}:
        return None
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def empty_or_value(v: Any) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    return s


METHOD_CANONICAL = {
    "fedavg_window": "FedAvg-Window",
    "fedasync_window": "FedAsync-Window",
    "flamf_timealign_adapted": "TimeAlign-Agg",
    "timealign_agg": "TimeAlign-Agg",
    "local_hajek": "Local-Hajek",
    "twostage_hajek": "TwoStage-Hajek",
    "inst_cal": "Inst-Cal",
    "debt_cal": "Debt-Cal",
    "raven": "RAVEN-MCS",
    "raven_mcs": "RAVEN-MCS",
    "central_all": "Central-All",
    "central_delivered": "Central-Delivered",
    "raven_simoracle": "RAVEN-SimOracle",
    "raven_wo_design": "RAVEN-w/o-Design",
    "raven_wo_obs": "RAVEN-w/o-Obs",
    "raven_wo_use": "RAVEN-w/o-Use",
    "raven_wo_inst": "RAVEN-w/o-Inst",
    "raven_wo_debt": "RAVEN-w/o-Debt",
}

DATASET_CANONICAL = {
    "sensorscope": "SensorScope",
    "uair": "U-Air",
    "u-air": "U-Air",
    "traffic": "NSW-Traffic",
    "nsw-traffic": "NSW-Traffic",
    "nsw_traffic": "NSW-Traffic",
    "tdrive": "T-Drive-Speed",
    "tdrive_speed": "T-Drive-Speed",
    "t-drive": "T-Drive-Speed",
    "balanced": "Balanced",
}


def canon_method(name: str) -> str:
    key = str(name).strip()
    return METHOD_CANONICAL.get(key, METHOD_CANONICAL.get(key.lower(), key))


def canon_dataset(name: str) -> str:
    key = str(name).strip()
    return DATASET_CANONICAL.get(key, DATASET_CANONICAL.get(key.lower(), key))


def write_meta_json(
    csv_path: Path,
    *,
    source_files: Iterable[str],
    filters: str,
    transformations: str,
    metric_definitions: Mapping[str, str] | None = None,
    included_seeds: Iterable[Any] | None = None,
    excluded_rows: str = "",
    statistical_method: str = "",
    version: str = "R1",
) -> Path:
    meta = {
        "source_files": list(source_files),
        "filters": filters,
        "transformations": transformations,
        "metric_definitions": dict(metric_definitions or {}),
        "included_seeds": list(included_seeds or []),
        "excluded_rows": excluded_rows,
        "statistical_method": statistical_method,
        "version": version,
        "csv_sha256": sha256_file(csv_path) if csv_path.is_file() else "",
        "csv_relative": str(csv_path).replace("\\", "/"),
    }
    return write_json(csv_path.with_suffix(csv_path.suffix + ".meta.json"), meta)

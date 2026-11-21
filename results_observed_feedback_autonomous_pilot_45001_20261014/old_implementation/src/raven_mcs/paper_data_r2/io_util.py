"""I/O helpers for R2. Writes only under paper_ready_r2/ and deliverables/."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from raven_mcs.paper_data_r1.io_util import (  # noqa: F401
    DATASET_CANONICAL,
    INVALID,
    METHOD_CANONICAL,
    MISSING,
    NOT_COMPARABLE,
    N_A,
    SUPERSEDED,
    VALID,
    canon_dataset,
    canon_method,
    copy_file,
    empty_or_value,
    ensure_dir,
    read_csv,
    read_json,
    safe_float,
    sha256_bytes,
    sha256_file,
    write_csv,
    write_json,
    write_text,
)


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
    version: str = "R2",
    extra: Mapping[str, Any] | None = None,
) -> Path:
    from raven_mcs.paper_data_r1.io_util import write_json as _wj, sha256_file as _sha

    meta: dict[str, Any] = {
        "source_files": list(source_files),
        "filters": filters,
        "transformations": transformations,
        "metric_definitions": dict(metric_definitions or {}),
        "included_seeds": list(included_seeds or []),
        "excluded_rows": excluded_rows,
        "statistical_method": statistical_method,
        "version": version,
        "csv_sha256": _sha(csv_path) if csv_path.is_file() else "",
        "csv_relative": str(csv_path).replace("\\", "/"),
    }
    if extra:
        meta.update(dict(extra))
    return _wj(csv_path.with_suffix(csv_path.suffix + ".meta.json"), meta)

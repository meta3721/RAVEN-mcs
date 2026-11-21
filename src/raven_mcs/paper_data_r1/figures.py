"""Figure-source builders (delegates to tables.build_tables_and_figures)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .tables import build_tables_and_figures


def build_figures(paper: Path) -> dict[str, Any]:
    """Build figure sources; table sources are built in the same pass."""
    return build_tables_and_figures(paper)

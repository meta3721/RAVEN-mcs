"""Seed-major formal scheduling."""
from __future__ import annotations
import json
from pathlib import Path
from .matrix import build_formal_matrix
from raven_mcs.utils.serialization import dump_json

def stage_rows(stage: str, seed: int | None = None) -> list[dict]:
    stages = ("A", "B", "C") if stage == "all" else (stage,)
    return [r for r in build_formal_matrix()["rows"] if r["kind"] == "new" and r["stage"] in stages and (seed is None or r["seed"] == seed)]
def update_progress(art: Path, row: dict) -> None:
    path = art / "progress.json"
    data = json.loads(path.read_text()) if path.is_file() else {"completed": {}}
    data["completed"][row["logical_run_id"]] = bool(row.get("accepted"))
    dump_json(data, path)

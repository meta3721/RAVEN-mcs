"""Formal EventTrace provisioning, preserving sealed E2 Traffic traces."""
from __future__ import annotations
import json
import shutil
from pathlib import Path
from typing import Any
from raven_mcs.e3.canary.execute import ensure_eventtrace as _ensure_canary_eventtrace
from .constants import E2_ART_RELATIVE_PATH

def eventtrace_dir(art: Path, dataset: str, seed: int) -> Path:
    return art / "eventtraces" / dataset / f"seed{seed}" / "training_eventtrace"

def ensure_eventtrace(root: Path, art: Path, dataset: str, seed: int) -> dict[str, Any]:
    if dataset == "traffic":
        return link_traffic_e2_trace(root, art, seed)
    return _ensure_canary_eventtrace(root, art, dataset, seed)

def link_traffic_e2_trace(root: Path, art: Path, seed: int) -> dict[str, Any]:
    source = root / E2_ART_RELATIVE_PATH / "eventtraces" / str(seed) / "complete_aligned" / "training_eventtrace"
    destination = eventtrace_dir(art, "traffic", seed)
    if not source.is_dir():
        raise FileNotFoundError(f"sealed E2 Traffic EventTrace missing: {source}")
    if destination.exists():
        return {"status": "REUSED", "path": str(destination), "source": str(source)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    (destination.parent / "e2_reuse_provenance.json").write_text(json.dumps({"source": str(source), "mode": "COPY_NO_REGENERATION"}), encoding="utf-8")
    return {"status": "COPIED", "path": str(destination), "source": str(source)}

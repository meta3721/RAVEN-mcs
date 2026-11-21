"""Phase 0 attestation: no training / rerun / new scientific work yet."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from raven_mcs.utils.serialization import dump_json

from .constants import ART_NAME, PARENT_ART, ROUND, art_path


def write_phase0(root: Path) -> dict[str, Any]:
    art = art_path(root)
    art.mkdir(parents=True, exist_ok=True)
    payload = {
        "round": ROUND,
        "artifact": ART_NAME,
        "parent": PARENT_ART,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "attestation": {
            "training_started": False,
            "rerun_started": False,
            "new_eventtraces": False,
            "new_formal_runs": False,
            "new_smoke_runs": False,
            "parent_raw_runs_deleted": False,
            "parent_raw_runs_overwritten": False,
            "e5_launched": False,
        },
        "status": "PHASE0_ATTESTED",
    }
    dump_json(payload, art / "E4_SEMANTIC_REPAIR_PHASE0_ATTESTATION.json")
    return payload

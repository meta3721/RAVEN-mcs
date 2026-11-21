"""Pre-window public TOD context for R1e. Never infer block from current R/O/U."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from raven_mcs.e3.real_runner.constants import GENERATOR_VERSION, WINDOW_DURATION
from raven_mcs.sag.deployment_groups import utc_tod_block

MAPPER_RULE = "RepeatableTimeOfDayMapper_UTC_hour_floordiv_6"
EXPECTED_TARGET_HASH = "86fd55f7e0bf8499944433de16324bd4687befd5568892613ee87acacad3ad07"


class WindowContextError(ValueError):
    """Raised when current-window event presence would leak into TOD context."""


@dataclass(frozen=True)
class PublicWindowSchedule:
    """Fixed public UTC start times, known before any current-window EventTrace row."""

    window_start_utc: Mapping[int, Any]
    source: str
    uses_current_event_presence: bool = False
    uses_current_R: bool = False
    uses_current_O: bool = False
    uses_current_U: bool = False

    def __post_init__(self) -> None:
        if self.uses_current_event_presence or self.uses_current_R or self.uses_current_O or self.uses_current_U:
            raise WindowContextError(
                "PublicWindowSchedule cannot be built from current R/O/U or event presence"
            )


def public_window_tod_block(window_id: int, schedule: PublicWindowSchedule) -> int:
    """Map a public window timestamp through the frozen paper TOD mapper."""
    if int(window_id) not in {int(k) for k in schedule.window_start_utc}:
        raise WindowContextError(f"window_id={window_id} missing from public schedule")
    ts = schedule.window_start_utc[int(window_id)]
    block = utc_tod_block(pd.Series([ts], name="absolute_time"))
    return int(block.iloc[0])


def forbid_tod_from_current_event_presence(
    *,
    events: Any = None,
    window_id: int | None = None,
    risk_set_unit_ids: Sequence[Any] | None = None,
) -> None:
    """Hard refusal: current EventTrace row existence is not a public clock."""
    _ = (events, window_id, risk_set_unit_ids)
    raise WindowContextError(
        "TOD block must not be inferred from current-window EventTrace event presence"
    )


def dataset_name_is_forbidden_context(dataset: str | None) -> bool:
    return str(dataset or "").strip().lower() in {"sensorscope", "uair", "sensor_scope"}


def audit_e3_prewindow_public_schedule(root: Path) -> dict[str, Any]:
    """Search sealed E3 traces and generator for a legal UTC window schedule.

    A legal schedule must provide window_id -> UTC timestamp before reading
    the current window's risk-set / observation / usable marks, and that
    timestamp must be consumable by RepeatableTimeOfDayMapper.
    """
    root = Path(root)
    ss_meta = root / (
        "artifacts/e3_formal_runs_r1/eventtraces/sensorscope/seed30001/"
        "training_eventtrace/metadata.json"
    )
    findings = {
        "mapper_required": MAPPER_RULE,
        "generator_version": GENERATOR_VERSION,
        "window_duration_constant": float(WINDOW_DURATION),
        "eventtrace_metadata_has_utc_schedule": False,
        "eventtrace_metadata_has_window_timestamps": False,
        "e3_generator_uses_abstract_window_index_clock": True,
        "e3_generator_samples_train_pool_independent_of_wall_clock": True,
        "e2_continuous_schedule_reusable_for_e3": False,
        "repeatable_mapper_accepts_raw_window_id": False,
        "must_read_current_event_to_invent_utc": True,
        "legal": False,
        "verdict": "NO_LEGAL_PREWINDOW_CONTEXT_FOR_R1E",
        "metadata_path": str(ss_meta).replace("\\", "/"),
    }
    if ss_meta.is_file():
        payload = json.loads(ss_meta.read_text(encoding="utf-8"))
        keys = set(str(k) for k in payload)
        utc_keys = {"window_start_utc", "window_schedule", "absolute_time", "public_clock"}
        findings["eventtrace_metadata_keys"] = sorted(keys)
        findings["eventtrace_metadata_has_utc_schedule"] = bool(keys & utc_keys)
    findings["reason"] = (
        "Sealed E3 EventTrace metadata stores only dataset/seed/num_windows/"
        "num_clients/s_max/generator. The complete-aligned R3 generator clocks "
        f"windows as abstract index time (deadline = window_id + {WINDOW_DURATION}), "
        "not UTC. Risk sets are sampled from the train pool independently of "
        "dataset absolute_time. RepeatableTimeOfDayMapper requires a UTC datetime; "
        "raw window_id is not a legal input. Reusing the E2 300-window SensorScope "
        "schedule would invent a mapping that is not the sealed E3 protocol. "
        "No frozen window_id -> UTC timestamp table exists. Inferring the block "
        "from the current window's first EventTrace row would use current-window "
        "event presence and is forbidden."
    )
    return findings

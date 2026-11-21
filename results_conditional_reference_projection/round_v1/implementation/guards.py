"""Resource tracking and frozen feasibility checks for the remaining seeds.

These checks do not train a model. The low-memory clock is injected so the
30 second rule can be tested without waiting.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

import numpy as np

FEASIBILITY_LIMIT = 1e-8
LOW_FREE_BYTES = 2 * 1024**3
LOW_FREE_SECONDS = 30.0


class RealConstraintViolation(RuntimeError):
    def __init__(self, payload: dict) -> None:
        super().__init__(json.dumps(payload, ensure_ascii=False))
        self.payload = payload


def frozen_bars(count: int) -> tuple[float, float]:
    size = int(count)
    if size <= 0:
        raise ValueError("empty server weight vector")
    return min(1.0, max(0.5, 1.0 / size)), min(3.0, float(size))


def constraint_parts(alpha: np.ndarray, a_bar: float, e_bar: float) -> dict[str, float]:
    vector = np.asarray(alpha, dtype=np.float64)
    negative = float(np.maximum(-vector, 0.0).max()) if vector.size else 0.0
    cap = float(np.maximum(vector - float(a_bar), 0.0).max()) if vector.size else 0.0
    ess = float(max(0.0, float(vector @ vector) - 1.0 / float(e_bar)))
    return {
        "simplex": abs(float(vector.sum()) - 1.0),
        "negative": negative,
        "cap": cap,
        "ess": ess,
    }


def clean_server_weights(weights: np.ndarray) -> tuple[np.ndarray, dict]:
    """Clip only a negative that is already inside the frozen tolerance.

    Cap, ESS, and simplex violations beyond 1e-8 are not repaired. The vector
    returned here is the one the server is allowed to apply.
    """
    raw = np.asarray(weights, dtype=np.float64).copy()
    a_bar, e_bar = frozen_bars(raw.size)
    before = constraint_parts(raw, a_bar, e_bar)
    structural = max(before["simplex"], before["cap"], before["ess"])
    if structural > FEASIBILITY_LIMIT or before["negative"] > FEASIBILITY_LIMIT:
        raise RealConstraintViolation(
            {
                "stage": "before_cleanup",
                "a_bar": a_bar,
                "e_bar": e_bar,
                "before": before,
                "limit": FEASIBILITY_LIMIT,
            }
        )
    cleaned = raw
    if before["negative"] > 0.0:
        cleaned = np.clip(raw, 0.0, None)
        total = float(cleaned.sum())
        if total <= 0.0:
            raise RealConstraintViolation({"stage": "cleanup", "reason": "nonpositive sum"})
        cleaned = cleaned / total
    after = constraint_parts(cleaned, a_bar, e_bar)
    correction = float(np.max(np.abs(cleaned - raw))) if raw.size else 0.0
    if max(after.values()) > FEASIBILITY_LIMIT:
        raise RealConstraintViolation(
            {
                "stage": "after_cleanup",
                "a_bar": a_bar,
                "e_bar": e_bar,
                "before": before,
                "after": after,
                "correction_max_abs": correction,
                "limit": FEASIBILITY_LIMIT,
            }
        )
    return cleaned, {
        "a_bar": a_bar,
        "e_bar": e_bar,
        "before": before,
        "after": after,
        "correction_max_abs": correction,
        "clipped_negative": bool(before["negative"] > 0.0),
    }


class LowMemoryTracker:
    def __init__(self, limit_seconds: float = LOW_FREE_SECONDS) -> None:
        self.limit_seconds = float(limit_seconds)
        self.low_since: float | None = None
        self.breached = False
        self.max_continuous = 0.0
        self._lock = threading.Lock()

    def observe(self, free: int, now: float) -> None:
        with self._lock:
            if int(free) < LOW_FREE_BYTES:
                if self.low_since is None:
                    self.low_since = float(now)
                elapsed = float(now) - self.low_since
                self.max_continuous = max(self.max_continuous, elapsed)
                if elapsed >= self.limit_seconds:
                    self.breached = True
                return
            self.low_since = None


class BudgetLedger:
    def __init__(self, path: Path, cpu_limit: float, wall_limit: float) -> None:
        self.path = Path(path)
        self.cpu_limit = float(cpu_limit)
        self.wall_limit = float(wall_limit)
        self.cpu_closed = 0.0
        self.wall_closed = 0.0
        self.open_cpu = 0.0
        self.open_wall = 0.0
        self.history: list[dict] = []

    def load(self) -> None:
        if not self.path.is_file():
            return
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.cpu_closed = float(payload.get("cpu_closed", 0.0))
        self.wall_closed = float(payload.get("wall_closed", 0.0))
        self.history = list(payload.get("history", []))
        open_process = payload.get("open_process")
        if open_process:
            self.cpu_closed += float(open_process.get("cpu", 0.0))
            self.wall_closed += float(open_process.get("wall", 0.0))
            self.history.append(
                {
                    "event": "closed_crashed_process",
                    "cpu": open_process.get("cpu"),
                    "wall": open_process.get("wall"),
                    "included_in_closed_total": True,
                }
            )

    def spent(self, process_cpu: float, process_wall: float) -> tuple[float, float]:
        return self.cpu_closed + float(process_cpu), self.wall_closed + float(process_wall)

    def snapshot(self, process_cpu: float, process_wall: float, note: str) -> None:
        self.open_cpu = float(process_cpu)
        self.open_wall = float(process_wall)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {
                    "cpu_limit": self.cpu_limit,
                    "wall_limit": self.wall_limit,
                    "cpu_closed": self.cpu_closed,
                    "wall_closed": self.wall_closed,
                    "open_process": {"cpu": self.open_cpu, "wall": self.open_wall, "note": note},
                    "spent_cpu": self.cpu_closed + self.open_cpu,
                    "spent_wall": self.wall_closed + self.open_wall,
                    "history": self.history,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def close_process(self, process_cpu: float, process_wall: float, note: str) -> None:
        self.history.append(
            {
                "event": "closed_process",
                "cpu": float(process_cpu),
                "wall": float(process_wall),
                "note": note,
                "included_in_closed_total": True,
            }
        )
        self.cpu_closed += float(process_cpu)
        self.wall_closed += float(process_wall)
        self.open_cpu = 0.0
        self.open_wall = 0.0
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {
                    "cpu_limit": self.cpu_limit,
                    "wall_limit": self.wall_limit,
                    "cpu_closed": self.cpu_closed,
                    "wall_closed": self.wall_closed,
                    "open_process": None,
                    "spent_cpu": self.cpu_closed,
                    "spent_wall": self.wall_closed,
                    "history": self.history,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def exceeds(self, process_cpu: float, process_wall: float) -> bool:
        cpu, wall = self.spent(process_cpu, process_wall)
        return cpu > self.cpu_limit or wall > self.wall_limit

    def remaining(self, process_cpu: float, process_wall: float) -> tuple[float, float]:
        cpu, wall = self.spent(process_cpu, process_wall)
        return self.cpu_limit - cpu, self.wall_limit - wall

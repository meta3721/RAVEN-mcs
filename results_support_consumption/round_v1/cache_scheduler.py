"""Independent HOLD/CONSUME scheduler. It does not train a model."""

from __future__ import annotations

import copy
from dataclasses import dataclass

import numpy as np

from protocol import (
    ALPHA_MAX,
    CACHE_ARMS,
    COMPLEMENT_MARGIN,
    E_MIN,
    EXTERNAL_ARMS,
    NUM_GROUPS,
    POOL_CAP,
    RESIDENCE_H,
    S_MAX,
    SERVER_LR,
)
from support_distance import DistanceFailure, DistanceSolver


class SchedulerFault(RuntimeError):
    pass


class NotAuthorized(RuntimeError):
    pass


@dataclass
class PoolMessage:
    attempt_id: str
    client_id: str
    registration_window: int
    registration_time: float
    arrival_time: float
    arrival_close: int
    retry: int
    download_version: int
    m: float
    composition: tuple[float, ...]
    group_mass: tuple[float, ...]
    raw_workload: float | None
    state: str = "in_flight"
    commit_close: int | None = None
    release_reason: str | None = None
    residence: int | None = None

    @property
    def sort_key(self) -> tuple[str, int, int]:
        return (self.client_id, int(self.registration_window), int(self.retry))


def _column(message: PoolMessage) -> np.ndarray:
    return np.asarray(message.composition, dtype=np.float64)


class Scheduler:
    def __init__(
        self,
        policy: str,
        mu: np.ndarray,
        *,
        s_max: int = S_MAX,
        residence_h: int = RESIDENCE_H,
        pool_cap: int = POOL_CAP,
        margin: float = COMPLEMENT_MARGIN,
        alpha_max: float = ALPHA_MAX,
        e_min: float = E_MIN,
        rng_seed: int = 0,
    ):
        if policy not in CACHE_ARMS:
            raise KeyError(policy)
        self.policy = policy
        self.s_max = int(s_max)
        self.residence_h = int(residence_h)
        self.pool_cap = int(pool_cap)
        self.margin = float(margin)
        self.mu = np.asarray(mu, dtype=np.float64).reshape(-1)
        self.solver = DistanceSolver(self.mu, alpha_max=alpha_max, e_min=e_min)
        self.version = 0
        self.pending: dict[str, PoolMessage] = {}
        self.in_flight: dict[str, PoolMessage] = {}
        self.terminal: dict[str, PoolMessage] = {}
        self.committed_ids: set[str] = set()
        self.rng = np.random.default_rng(int(rng_seed))
        self.optimizer = {
            "name": "weighted_sgd",
            "eta": float(SERVER_LR),
            "step_count": 0,
            "version": 0,
        }
        self.ledger: list[dict] = []
        self.budget = {"decision_solves": 0, "metric_solves": 0, "releases": 0, "holds": 0}
        self.carried_d = 1.0
        self.current_close: int | None = None
        self.finished = False
        self.faults: list[str] = []
        self.release_log: list[tuple[int, tuple[str, ...]]] = []
        self.overflow_count = 0
        self.overflow_workload = 0.0
        self.overflow_group_mass = np.zeros(self.mu.shape[0], dtype=np.float64)
        self.known_ids: set[str] = set()

    def begin_close(self, close_id: int) -> None:
        self._alive()
        if self.current_close is not None and int(close_id) != self.current_close + 1:
            self._fault(f"close grid skipped at {close_id}")
        self.current_close = int(close_id)

    def register(self, attempt) -> PoolMessage:
        self._alive()
        if self.current_close is None:
            self._fault("register before a close")
        if int(attempt.registration_window) != int(self.current_close):
            self._fault(f"registration {attempt.attempt_id} is outside close {self.current_close}")
        if int(attempt.arrival_close) < int(attempt.registration_window):
            self._fault(f"arrival precedes registration for {attempt.attempt_id}")
        if attempt.attempt_id in self.known_ids or attempt.attempt_id in self.committed_ids:
            self._fault(f"attempt {attempt.attempt_id} re-entered")
        message = PoolMessage(
            attempt_id=str(attempt.attempt_id),
            client_id=str(attempt.client_id),
            registration_window=int(attempt.registration_window),
            registration_time=float(attempt.registration_time),
            arrival_time=float(attempt.arrival_time),
            arrival_close=int(attempt.arrival_close),
            retry=int(attempt.retry),
            download_version=int(self.version),
            m=float(attempt.m),
            composition=tuple(float(x) for x in attempt.composition),
            group_mass=tuple(float(x) for x in attempt.group_mass),
            raw_workload=None if attempt.raw_workload is None else float(attempt.raw_workload),
            state="in_flight",
        )
        if len(message.composition) != self.mu.shape[0]:
            self._fault(f"composition width mismatch for {message.attempt_id}")
        self.known_ids.add(message.attempt_id)
        self.in_flight[message.attempt_id] = message
        return message

    def deliver(self, attempt_id: str) -> None:
        self._alive()
        message = self.in_flight.get(str(attempt_id))
        if message is None:
            self._fault(f"delivery of unknown in-flight attempt {attempt_id}")
            return
        if int(message.arrival_close) != int(self.current_close):
            self._fault(f"delivery of {attempt_id} outside its arrival close")
        version_age = int(self.version) - int(message.download_version)
        if version_age < 0:
            self._fault(f"negative version age for {attempt_id}")
        if version_age > self.s_max:
            self._move_terminal(message, "version_rejected")
            return
        existing = self.pending.get(message.client_id)
        if existing is not None:
            if _newer(message, existing):
                self._move_terminal(existing, "superseded")
                del self.pending[existing.client_id]
            else:
                self._move_terminal(message, "superseded")
                return
        message.state = "pending"
        del self.in_flight[message.attempt_id]
        self.pending[message.client_id] = message
        self._enforce_cap()

    def close(self, close_id: int) -> dict:
        self._alive()
        if int(close_id) != int(self.current_close):
            self._fault(f"close {close_id} does not match the open close")
        for message in list(self.pending.values()):
            age = int(close_id) - int(message.arrival_close)
            if age < 0:
                self._fault(f"future message {message.attempt_id} is pending")
            elif age > self.residence_h or (message.m <= 0.0 and age >= self.residence_h):
                self._move_terminal(message, "expired")
                del self.pending[message.client_id]
        positive = [message for message in self.pending.values() if message.m > 0.0]
        held = [message for message in positive if message.arrival_close < close_id]
        arrived = [message for message in positive if message.arrival_close == close_id]
        action, reason, distances = self._decide(close_id, held, arrived)
        committed: list[str] = []
        distance = None
        if action == "RELEASE":
            if positive:
                distance = distances.get("P")
                if distance is None:
                    distance = self._distance(positive, decision=False)
                self.carried_d = float(distance)
                self.version += 1
                self.optimizer["step_count"] += 1
                self.optimizer["version"] = int(self.version)
                self.budget["releases"] += 1
            clients = [message.client_id for message in self.pending.values()]
            if len(clients) != len(set(clients)):
                self._fault("release contains a duplicated client")
            for message in list(self.pending.values()):
                self._commit(message, close_id, reason)
                committed.append(message.attempt_id)
                del self.pending[message.client_id]
            committed.sort()
            self.release_log.append((int(close_id), tuple(committed)))
        else:
            self.budget["holds"] += 1
        record = {
            "window_id": int(close_id),
            "action": action,
            "reason": reason,
            "n_H": len(held),
            "n_A": len(arrived),
            "n_P": len(positive),
            "n_pending": len(committed) if action == "RELEASE" else len(self.pending),
            "d_h": distances.get("H"),
            "d_a": distances.get("A"),
            "d_p": distances.get("P", distance),
            "d_carried": float(self.carried_d),
            "committed_attempt_ids": committed,
            "version_after": int(self.version),
            "optimizer_steps": int(self.optimizer["step_count"]),
        }
        self.ledger.append(record)
        return record

    def finish(self) -> None:
        self._alive()
        for message in list(self.pending.values()):
            self._move_terminal(message, "endpoint_unconsumed")
            del self.pending[message.client_id]
        for message in list(self.in_flight.values()):
            self._move_terminal(message, "not_delivered")
            del self.in_flight[message.attempt_id]
        self.finished = True

    def insert_pending_for_test(self, message: PoolMessage) -> None:
        """Place an already-pending message. Production replay does not call this."""
        self._alive()
        if message.attempt_id in self.known_ids:
            self._fault(f"test insert reused {message.attempt_id}")
        self.known_ids.add(message.attempt_id)
        message.state = "pending"
        self.pending[message.client_id] = message

    def snapshot(self) -> dict:
        return {
            "version": int(self.version),
            "pending": copy.deepcopy(self.pending),
            "in_flight": copy.deepcopy(self.in_flight),
            "terminal": copy.deepcopy(self.terminal),
            "committed_ids": set(self.committed_ids),
            "rng": copy.deepcopy(self.rng.bit_generator.state),
            "optimizer": copy.deepcopy(self.optimizer),
            "ledger": copy.deepcopy(self.ledger),
            "budget": copy.deepcopy(self.budget),
            "carried_d": float(self.carried_d),
            "finished": bool(self.finished),
            "current_close": self.current_close,
            "faults": list(self.faults),
            "release_log": copy.deepcopy(self.release_log),
            "known_ids": set(self.known_ids),
            "overflow_count": int(self.overflow_count),
            "overflow_workload": float(self.overflow_workload),
            "overflow_group_mass": self.overflow_group_mass.copy(),
        }

    def restore(self, snap: dict) -> None:
        required = {
            "version",
            "pending",
            "in_flight",
            "terminal",
            "committed_ids",
            "rng",
            "optimizer",
            "ledger",
            "budget",
        }
        missing = sorted(required - set(snap))
        if missing:
            raise SchedulerFault(f"incomplete snapshot, missing {missing}")
        restored = copy.deepcopy(snap)
        self.version = int(restored["version"])
        self.pending = restored["pending"]
        self.in_flight = restored["in_flight"]
        self.terminal = restored["terminal"]
        self.committed_ids = set(restored["committed_ids"])
        self.rng.bit_generator.state = restored["rng"]
        self.optimizer = restored["optimizer"]
        self.ledger = restored["ledger"]
        self.budget = restored["budget"]
        self.carried_d = float(restored.get("carried_d", self.carried_d))
        self.finished = bool(restored.get("finished", False))
        self.current_close = restored.get("current_close")
        self.faults = list(restored.get("faults", []))
        self.release_log = list(restored.get("release_log", []))
        self.known_ids = set(restored.get("known_ids", []))
        self.overflow_count = int(restored.get("overflow_count", 0))
        self.overflow_workload = float(restored.get("overflow_workload", 0.0))
        mass = restored.get("overflow_group_mass")
        if mass is not None:
            self.overflow_group_mass = np.asarray(mass, dtype=np.float64).copy()

    def _decide(self, close_id: int, held: list[PoolMessage], arrived: list[PoolMessage]):
        distances: dict[str, float] = {}
        pool = held + arrived
        if not pool:
            return "HOLD", "HOLD_EMPTY", distances
        max_age = max(int(close_id) - int(message.arrival_close) for message in pool)
        if self.policy == "I-Proj":
            distances["P"] = self._distance(pool, decision=False)
            return "RELEASE", "IMMEDIATE_RELEASE", distances
        if self.policy == "F1-Proj":
            if max_age >= 1:
                distances["P"] = self._distance(pool, decision=False)
                return "RELEASE", "AGE_RELEASE", distances
            return "HOLD", "HOLD_NO_COMPLEMENT", distances
        if self.policy == "F2-Proj":
            if max_age >= self.residence_h:
                distances["P"] = self._distance(pool, decision=False)
                return "RELEASE", "DEADLINE_RELEASE", distances
            return "HOLD", "HOLD_NO_COMPLEMENT", distances
        if max_age >= self.residence_h:
            distances["P"] = self._distance(pool, decision=False)
            return "RELEASE", "DEADLINE_RELEASE", distances
        if held and arrived:
            distances["H"] = self._distance(held, decision=True)
            distances["A"] = self._distance(arrived, decision=True)
            distances["P"] = self._distance(pool, decision=True)
            if distances["P"] <= min(distances["H"], distances["A"]) - self.margin:
                return "RELEASE", "COMPLEMENTARY_RELEASE", distances
        return "HOLD", "HOLD_NO_COMPLEMENT", distances

    def _distance(self, messages: list[PoolMessage], *, decision: bool) -> float:
        ordered = sorted(messages, key=lambda message: message.sort_key)
        matrix = np.column_stack([_column(message) for message in ordered])
        try:
            distance, _alpha = self.solver.solve(matrix)
        except DistanceFailure:
            raise
        bucket = "decision_solves" if decision else "metric_solves"
        self.budget[bucket] += 1
        return float(distance)

    def _enforce_cap(self) -> None:
        while len(self.pending) > self.pool_cap:
            victim = min(
                self.pending.values(),
                key=lambda message: (message.arrival_time, message.attempt_id),
            )
            self.overflow_count += 1
            if victim.raw_workload is not None:
                self.overflow_workload += float(victim.raw_workload)
            self.overflow_group_mass += np.asarray(victim.group_mass, dtype=np.float64)
            self._move_terminal(victim, "overflow_dropped")
            del self.pending[victim.client_id]

    def _commit(self, message: PoolMessage, close_id: int, reason: str) -> None:
        if message.attempt_id in self.committed_ids or message.attempt_id in self.terminal:
            self._fault(f"committed message re-entered: {message.attempt_id}")
            return
        message.state = "committed"
        message.commit_close = int(close_id)
        message.release_reason = reason
        message.residence = int(close_id) - int(message.arrival_close)
        self.committed_ids.add(message.attempt_id)
        self.terminal[message.attempt_id] = message

    def _move_terminal(self, message: PoolMessage, state: str) -> None:
        if message.attempt_id in self.terminal or message.attempt_id in self.committed_ids:
            self._fault(f"message {message.attempt_id} changed state twice")
            return
        message.state = state
        self.in_flight.pop(message.attempt_id, None)
        self.terminal[message.attempt_id] = message

    def _fault(self, text: str) -> None:
        self.faults.append(text)
        raise SchedulerFault(text)

    def _alive(self) -> None:
        if self.finished:
            raise SchedulerFault("scheduler was used after the endpoint")
        if self.faults:
            raise SchedulerFault(self.faults[-1])


def _newer(candidate: PoolMessage, current: PoolMessage) -> bool:
    if candidate.download_version != current.download_version:
        return candidate.download_version > current.download_version
    if candidate.registration_time != current.registration_time:
        return candidate.registration_time > current.registration_time
    return candidate.sort_key > current.sort_key


@dataclass
class AttemptView:
    attempt_id: str
    client_id: str
    registration_window: int
    registration_time: float
    arrival_time: float
    arrival_close: int
    retry: int
    m: float
    composition: tuple[float, ...]
    group_mass: tuple[float, ...]
    raw_workload: float | None = None


def run_cache(policy: str, attempts: list[AttemptView], mu: np.ndarray, n_windows: int) -> Scheduler:
    if policy not in CACHE_ARMS:
        raise KeyError(policy)
    scheduler = Scheduler(policy, mu)
    by_registration: dict[int, list[AttemptView]] = {window: [] for window in range(n_windows)}
    by_arrival: dict[int, list[AttemptView]] = {window: [] for window in range(n_windows)}
    for attempt in attempts:
        if 0 <= int(attempt.registration_window) < n_windows:
            by_registration[int(attempt.registration_window)].append(attempt)
        if 0 <= int(attempt.arrival_close) < n_windows:
            by_arrival[int(attempt.arrival_close)].append(attempt)
    for window in range(n_windows):
        scheduler.begin_close(window)
        for attempt in sorted(
            by_registration[window],
            key=lambda item: (item.client_id, item.registration_window, item.retry),
        ):
            scheduler.register(attempt)
        for attempt in sorted(by_arrival[window], key=lambda item: (item.client_id, item.registration_window, item.retry)):
            scheduler.deliver(attempt.attempt_id)
        scheduler.close(window)
    scheduler.finish()
    return scheduler


class ProtocolRunner:
    """Six named arm entries. Only the four cache arms can run without training."""

    def run_cache(self, policy: str, attempts: list[AttemptView], mu: np.ndarray, n_windows: int) -> Scheduler:
        return run_cache(policy, attempts, mu, n_windows)

    def run_external(self, policy: str) -> None:
        if policy not in EXTERNAL_ARMS:
            raise KeyError(policy)
        raise NotAuthorized(
            f"{policy} remains specified for a later approved training batch and is not executed"
        )

    def measure(self, checkpoint: str | None = None) -> None:
        del checkpoint
        raise NotAuthorized("P0-P2 has no prediction checkpoint and does not compute task gain")


def synthetic_attempt(
    client: str,
    window: int,
    composition: tuple[float, ...],
    *,
    retry: int = 0,
    mass: float = 1.0,
) -> AttemptView:
    composition = tuple(float(x) for x in composition)
    group_mass = tuple(mass * value for value in composition)
    return AttemptView(
        attempt_id=f"{client}|{window}|{retry}",
        client_id=client,
        registration_window=window,
        registration_time=float(window) + 0.1,
        arrival_time=float(window) + 0.2,
        arrival_close=window,
        retry=retry,
        m=float(mass),
        composition=composition,
        group_mass=group_mass,
        raw_workload=1.0,
    )

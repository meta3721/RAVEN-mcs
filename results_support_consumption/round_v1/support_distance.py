"""Minimum L1 support distance on the frozen cap and ESS set."""

from __future__ import annotations

import numpy as np

from protocol import ALPHA_MAX, COMPOSITION_TOLERANCE, E_MIN


class DistanceFailure(RuntimeError):
    """A failed solve. It does not carry a reusable distance."""


def cap_of(n_active: int, alpha_max: float = ALPHA_MAX) -> float:
    if n_active <= 0:
        raise ValueError("n_active must be positive")
    if alpha_max <= 0:
        raise ValueError("alpha_max must be positive")
    return float(min(1.0, max(float(alpha_max), 1.0 / float(n_active))))


def ess_of(n_active: int, e_min: float = E_MIN) -> float:
    if n_active <= 0:
        raise ValueError("n_active must be positive")
    if e_min <= 0:
        raise ValueError("e_min must be positive")
    return float(min(float(e_min), float(n_active)))


def _violations(alpha: np.ndarray, cap: float, ess_bound: float) -> tuple[float, float, float, float]:
    value = np.asarray(alpha, dtype=np.float64).reshape(-1)
    return (
        abs(float(value.sum()) - 1.0),
        max(0.0, -float(value.min())),
        max(0.0, float(value.max()) - float(cap)),
        max(0.0, float(np.square(value).sum()) - (1.0 / float(ess_bound))),
    )


class DistanceSolver:
    """Solve D(S) = min 0.5 ||M alpha - mu||_1 over the cap/ESS simplex.

    K <= E_min makes the ESS ball the uniform vector, so that case is closed
    form. Larger sets use one parameterized convex program per K.
    """

    def __init__(self, mu: np.ndarray, alpha_max: float = ALPHA_MAX, e_min: float = E_MIN):
        self.mu = np.asarray(mu, dtype=np.float64).reshape(-1)
        if self.mu.ndim != 1 or self.mu.size == 0:
            raise ValueError("mu must be a nonempty vector")
        if not np.all(np.isfinite(self.mu)) or np.any(self.mu < 0):
            raise ValueError("mu must be finite and nonnegative")
        self.alpha_max = float(alpha_max)
        self.e_min = float(e_min)
        self.calls = 0
        self._problems: dict[int, tuple[object, object, object]] = {}

    def solve(
        self,
        coverage: np.ndarray,
        *,
        cap_override: float | None = None,
        ess_override: float | None = None,
    ) -> tuple[float, np.ndarray]:
        matrix = np.asarray(coverage, dtype=np.float64)
        if matrix.ndim != 2 or matrix.shape[0] != self.mu.shape[0] or matrix.shape[1] == 0:
            raise DistanceFailure("coverage matrix must be groups by a nonempty client set")
        if not np.all(np.isfinite(matrix)):
            raise DistanceFailure("coverage matrix must be finite")
        if np.any(matrix < -1e-8):
            raise DistanceFailure("coverage matrix has a negative entry")
        if np.any(np.abs(matrix.sum(axis=0) - 1.0) > COMPOSITION_TOLERANCE):
            raise DistanceFailure("a composition column does not sum to one")
        k = int(matrix.shape[1])
        cap = cap_of(k, self.alpha_max) if cap_override is None else float(cap_override)
        ess_bound = ess_of(k, self.e_min) if ess_override is None else float(ess_override)
        self.calls += 1
        if cap * k < 1.0 - 1e-12:
            raise DistanceFailure("INFEASIBLE_CONFIGURATION: cap cannot cover the simplex")
        if ess_bound <= 0:
            raise DistanceFailure("INFEASIBLE_CONFIGURATION: ESS bound is not positive")
        if cap_override is None and ess_override is None and k <= int(self.e_min):
            alpha = np.full(k, 1.0 / k, dtype=np.float64)
            distance = 0.5 * float(np.abs(matrix @ alpha - self.mu).sum())
            self._accept(alpha, cap, ess_bound)
            return distance, alpha
        alpha = self._convex(
            matrix,
            cap,
            ess_bound,
            cache=cap_override is None and ess_override is None,
        )
        self._accept(alpha, cap, ess_bound)
        distance = 0.5 * float(np.abs(matrix @ alpha - self.mu).sum())
        return distance, alpha

    def _accept(self, alpha: np.ndarray, cap: float, ess_bound: float) -> None:
        violations = _violations(alpha, cap, ess_bound)
        if not np.all(np.isfinite(violations)) or max(violations) > COMPOSITION_TOLERANCE:
            raise DistanceFailure(
                "solver result exceeds the feasibility tolerance and cannot drive an action"
            )

    def _convex(
        self,
        matrix: np.ndarray,
        cap: float,
        ess_bound: float,
        *,
        cache: bool,
    ) -> np.ndarray:
        import cvxpy as cp

        groups, clients = matrix.shape
        problem = parameter = alpha = None
        if cache:
            problem, parameter, alpha = self._problems.get(clients, (None, None, None))
        if problem is None:
            parameter = cp.Parameter((groups, clients))
            alpha = cp.Variable(clients)
            slack = cp.Variable(groups)
            constraints = [
                cp.sum(alpha) == 1.0,
                alpha >= 0.0,
                alpha <= cap,
                cp.sum_squares(alpha) <= 1.0 / ess_bound,
                parameter @ alpha - self.mu <= slack,
                self.mu - parameter @ alpha <= slack,
            ]
            problem = cp.Problem(cp.Minimize(0.5 * cp.sum(slack)), constraints)
            if cache:
                self._problems[clients] = (problem, parameter, alpha)
        parameter.value = matrix
        status = self._solve_problem(problem)
        value = None if alpha.value is None else np.asarray(alpha.value, dtype=np.float64).reshape(-1)
        if status != "optimal" or value is None or not np.all(np.isfinite(value)):
            fresh, fresh_alpha = self._build_fresh(matrix, cap, ess_bound)
            status = self._solve_problem(fresh, solver="SCS")
            value = None if fresh_alpha.value is None else np.asarray(fresh_alpha.value, dtype=np.float64).reshape(-1)
            if status not in {"optimal", "optimal_inaccurate"} or value is None:
                raise DistanceFailure(f"support solver failed: {status}")
        return value

    def _build_fresh(self, matrix: np.ndarray, cap: float, ess_bound: float):
        import cvxpy as cp

        groups, clients = matrix.shape
        alpha = cp.Variable(clients)
        slack = cp.Variable(groups)
        constraints = [
            cp.sum(alpha) == 1.0,
            alpha >= 0.0,
            alpha <= cap,
            cp.sum_squares(alpha) <= 1.0 / ess_bound,
            matrix @ alpha - self.mu <= slack,
            self.mu - matrix @ alpha <= slack,
        ]
        return cp.Problem(cp.Minimize(0.5 * cp.sum(slack)), constraints), alpha

    @staticmethod
    def _solve_problem(problem, solver: str = "CLARABEL") -> str:
        import cvxpy as cp

        chosen = cp.CLARABEL if solver == "CLARABEL" else cp.SCS
        try:
            if solver == "SCS":
                problem.solve(solver=chosen, verbose=False, eps=1e-7, max_iters=20_000)
            else:
                problem.solve(solver=chosen, verbose=False, warm_start=True)
        except Exception as exc:  # noqa: BLE001
            raise DistanceFailure(f"support solver exception: {exc}") from exc
        return str(problem.status)

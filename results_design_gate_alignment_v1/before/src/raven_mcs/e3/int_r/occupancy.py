"""INT-R protocol occupancy: client-window A_{k,t}, independent of labels and methods."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

DATASET_ID = {"sensorscope": 0, "uair": 1}
RHO_STAR = 0.425
B_STAR = 0.38
RHO_WINDOW = (0.40, 0.45)
B_WINDOW = (0.30, 0.45)
CALIBRATION_SEED = 29999
STABILITY_SEEDS = tuple(range(28001, 28021))
OCC1_WINDOW = (0.35, 0.50)
L_MEAN_STD_MAX = 0.06
CALIBRATOR_VERSION_V2 = "v2_stability_screen"
STABILITY_LADDER = ("L40", "L36", "L32", "L_mean")
GRID_N_PRIMARY = 22
GRID_N_EXPAND = 44
GRID_LO = 0.55
GRID_HI = 0.98


@dataclass(frozen=True)
class OccupancySpec:
    family: str
    alpha: float
    beta: float
    rho0: float
    burstiness_miss: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def occupancy_rng(dataset: str, seed: int) -> np.random.Generator:
    ds = DATASET_ID[str(dataset).lower()]
    return np.random.default_rng(int(seed) + 10007 * ds + 17)


def burstiness(gaps: np.ndarray) -> float:
    gaps = np.asarray(gaps, dtype=np.float64)
    if gaps.size < 2:
        return float("nan")
    mu = float(np.mean(gaps))
    sd = float(np.std(gaps, ddof=1))
    if mu + sd <= 0:
        return float("nan")
    return float((sd - mu) / (sd + mu))


def simulate_occupancy(
    *,
    n_clients: int,
    n_windows: int,
    spec: OccupancySpec,
    rng: np.random.Generator,
) -> np.ndarray:
    """Return A with shape (n_windows, n_clients) in {0,1}."""
    n_clients = int(n_clients)
    n_windows = int(n_windows)
    A = np.zeros((n_windows, n_clients), dtype=np.int8)
    if spec.family == "bernoulli_iid":
        A[0] = (rng.random(n_clients) < float(spec.rho0)).astype(np.int8)
        for t in range(1, n_windows):
            A[t] = (rng.random(n_clients) < float(spec.rho0)).astype(np.int8)
        return A
    if spec.family != "two_state_markov":
        raise ValueError(f"unknown occupancy family {spec.family!r}")
    alpha = float(spec.alpha)
    beta = float(spec.beta)
    state = (rng.random(n_clients) < float(spec.rho0)).astype(np.int8)
    A[0] = state
    for t in range(1, n_windows):
        u = rng.random(n_clients)
        stay_on = (state == 1) & (u < alpha)
        turn_on = (state == 0) & (u >= beta)
        state = np.where(stay_on | turn_on, 1, 0).astype(np.int8)
        A[t] = state
    return A


def occupancy_metrics(A: np.ndarray) -> dict[str, float]:
    A = np.asarray(A, dtype=np.int8)
    n_windows, n_clients = A.shape
    mean_active = float(A.mean())
    gaps: list[float] = []
    per_client_b: list[float] = []
    for k in range(n_clients):
        slots = np.flatnonzero(A[:, k])
        if slots.size >= 3:
            g = np.diff(slots.astype(np.float64))
            gaps.extend(g.tolist())
            per_client_b.append(burstiness(g))
        elif slots.size >= 2:
            gaps.extend(np.diff(slots.astype(np.float64)).tolist())
    pooled = np.asarray(gaps, dtype=np.float64)
    b_pooled = burstiness(pooled)
    all_off = float(np.mean(A.sum(axis=1) == 0))
    mean_active_clients = float(A.sum(axis=1).mean())
    return {
        "mean_active_frac": mean_active,
        "burstiness_pooled": float(b_pooled),
        "burstiness_per_client_mean": float(np.nanmean(per_client_b)) if per_client_b else float("nan"),
        "fraction_windows_all_clients_off": all_off,
        "mean_active_clients_per_window": mean_active_clients,
        "n_clients": float(n_clients),
        "n_windows": float(n_windows),
        "n_pooled_gaps": float(pooled.size),
    }


def v1_cell_seed(alpha: float, beta: float) -> int:
    """v1 per-cell RNG seed for the T-Drive scalar match. Do not change."""
    return (
        CALIBRATION_SEED
        + (int(round(float(alpha) * 1e6)) % 10007)
        + 97 * (int(round(float(beta) * 1e6)) % 10007)
    )


def calibrate_markov(
    *,
    n_clients: int,
    n_windows: int,
    rng: np.random.Generator | None = None,
) -> OccupancySpec:
    """Grid-search sticky Markov on occupancy draws only (no labels)."""
    del rng  # each grid cell uses an independent seed; do not consume a shared stream
    alphas = np.linspace(GRID_LO, GRID_HI, GRID_N_PRIMARY)
    betas = np.linspace(GRID_LO, GRID_HI, GRID_N_PRIMARY)
    best_rho: OccupancySpec | None = None
    best_rho_score = float("inf")
    best_both: OccupancySpec | None = None
    best_both_score = float("inf")
    for alpha in alphas:
        for beta in betas:
            spec = OccupancySpec(
                family="two_state_markov",
                alpha=float(alpha),
                beta=float(beta),
                rho0=RHO_STAR,
            )
            cell_rng = np.random.default_rng(v1_cell_seed(float(alpha), float(beta)))
            A = simulate_occupancy(
                n_clients=n_clients, n_windows=n_windows, spec=spec, rng=cell_rng
            )
            met = occupancy_metrics(A)
            rho = met["mean_active_frac"]
            b = met["burstiness_pooled"]
            if not (RHO_WINDOW[0] <= rho <= RHO_WINDOW[1]):
                continue
            rho_pen = (rho - RHO_STAR) ** 2
            b_pen = 0.0 if np.isnan(b) else 0.25 * (b - B_STAR) ** 2
            score = rho_pen + b_pen
            if score < best_rho_score:
                best_rho_score = score
                best_rho = spec
            if not np.isnan(b) and B_WINDOW[0] <= b <= B_WINDOW[1] and score < best_both_score:
                best_both_score = score
                best_both = spec
    if best_both is not None:
        return best_both
    if best_rho is not None:
        return OccupancySpec(
            family=best_rho.family,
            alpha=best_rho.alpha,
            beta=best_rho.beta,
            rho0=best_rho.rho0,
            burstiness_miss=True,
        )
    raise RuntimeError(
        "INT-R occupancy calibrator could not hit mean active fraction "
        f"in {RHO_WINDOW} for n_clients={n_clients} n_windows={n_windows}"
    )


def stability_screen(
    *,
    spec: OccupancySpec,
    n_clients: int,
    n_windows_by_dataset: dict[str, int],
    seeds: tuple[int, ...] = STABILITY_SEEDS,
) -> dict[str, float]:
    """Occupancy-only dummy-seed screen. Seeds must be the frozen stability family."""
    if tuple(seeds) != STABILITY_SEEDS:
        raise ValueError("stability_screen seeds must be the frozen STABILITY_SEEDS tuple")
    rhos: list[float] = []
    hits = 0
    for seed in seeds:
        for dataset, n_windows in n_windows_by_dataset.items():
            A = simulate_occupancy(
                n_clients=n_clients,
                n_windows=int(n_windows),
                spec=spec,
                rng=occupancy_rng(str(dataset), int(seed)),
            )
            rho = float(A.mean())
            rhos.append(rho)
            if OCC1_WINDOW[0] <= rho <= OCC1_WINDOW[1]:
                hits += 1
    arr = np.asarray(rhos, dtype=np.float64)
    return {
        "hits": float(hits),
        "n_checks": float(arr.size),
        "mean_rho": float(arr.mean()) if arr.size else float("nan"),
        "std_rho": float(np.std(arr, ddof=1)) if arr.size >= 2 else float("nan"),
    }


def _level_ok(row: dict[str, Any], level: str) -> bool:
    hits = int(row["hits"])
    if level == "L40":
        return hits == 40
    if level == "L36":
        return hits >= 36
    if level == "L32":
        return hits >= 32
    if level == "L_mean":
        mean_rho = float(row["mean_rho"])
        std_rho = float(row["std_rho"])
        return (
            RHO_WINDOW[0] <= mean_rho <= RHO_WINDOW[1]
            and np.isfinite(std_rho)
            and std_rho <= L_MEAN_STD_MAX
        )
    raise ValueError(f"unknown stability level {level!r}")


def _pick_ladder(rows: list[dict[str, Any]]) -> tuple[str | None, list[dict[str, Any]]]:
    for level in STABILITY_LADDER:
        both = [r for r in rows if r["both"] and _level_ok(r, level)]
        if both:
            return level, both
        any_rho = [r for r in rows if _level_ok(r, level)]
        if any_rho:
            return level, any_rho
    return None, []


def _eval_grid_rows(
    *,
    n_clients: int,
    n_windows_cal: int,
    n_windows_by_dataset: dict[str, int],
    grid_n: int,
) -> list[dict[str, Any]]:
    alphas = np.linspace(GRID_LO, GRID_HI, int(grid_n))
    betas = np.linspace(GRID_LO, GRID_HI, int(grid_n))
    rows: list[dict[str, Any]] = []
    for alpha in alphas:
        for beta in betas:
            spec = OccupancySpec(
                family="two_state_markov",
                alpha=float(alpha),
                beta=float(beta),
                rho0=RHO_STAR,
            )
            cell_rng = np.random.default_rng(v1_cell_seed(float(alpha), float(beta)))
            A = simulate_occupancy(
                n_clients=n_clients,
                n_windows=n_windows_cal,
                spec=spec,
                rng=cell_rng,
            )
            met = occupancy_metrics(A)
            rho = float(met["mean_active_frac"])
            b = float(met["burstiness_pooled"])
            if not (RHO_WINDOW[0] <= rho <= RHO_WINDOW[1]):
                continue
            rho_pen = (rho - RHO_STAR) ** 2
            b_pen = 0.0 if np.isnan(b) else 0.25 * (b - B_STAR) ** 2
            both = (not np.isnan(b)) and (B_WINDOW[0] <= b <= B_WINDOW[1])
            stab = stability_screen(
                spec=spec,
                n_clients=n_clients,
                n_windows_by_dataset=n_windows_by_dataset,
            )
            rows.append(
                {
                    "alpha": float(alpha),
                    "beta": float(beta),
                    "rho_cal": rho,
                    "B_cal": b,
                    "score": float(rho_pen + b_pen),
                    "both": bool(both),
                    "hits": int(stab["hits"]),
                    "n_checks": int(stab["n_checks"]),
                    "mean_rho": float(stab["mean_rho"]),
                    "std_rho": float(stab["std_rho"]),
                }
            )
    return rows


def _select_row(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    def key(r: dict[str, Any]) -> tuple[float, float, float, float]:
        return (
            float(r["score"]),
            float(r["std_rho"]),
            float(r["alpha"]),
            float(r["beta"]),
        )

    return min(candidates, key=key)


@dataclass(frozen=True)
class CalibrationV2Result:
    spec: OccupancySpec
    stability_level: str
    stability_hits: int
    stability_n_checks: int
    stability_mean_rho: float
    stability_std_rho: float
    grid_expanded: bool
    grid_rows: tuple[dict[str, Any], ...]


def calibrate_markov_v2(
    *,
    n_clients: int,
    n_windows_cal: int,
    n_windows_by_dataset: dict[str, int],
) -> CalibrationV2Result:
    """T-Drive scalar match plus dummy-seed stability screen. Occupancy draws only."""
    required = {"sensorscope", "uair"}
    if set(n_windows_by_dataset) != required:
        raise ValueError(f"n_windows_by_dataset keys must be {required}")
    rows = _eval_grid_rows(
        n_clients=n_clients,
        n_windows_cal=n_windows_cal,
        n_windows_by_dataset=n_windows_by_dataset,
        grid_n=GRID_N_PRIMARY,
    )
    if not rows:
        raise RuntimeError(
            "INT-R occupancy calibrator v2 could not hit mean active fraction "
            f"in {RHO_WINDOW} on the scalar-match grid"
        )
    level, cand = _pick_ladder(rows)
    grid_expanded = False
    if not cand:
        rows = _eval_grid_rows(
            n_clients=n_clients,
            n_windows_cal=n_windows_cal,
            n_windows_by_dataset=n_windows_by_dataset,
            grid_n=GRID_N_EXPAND,
        )
        grid_expanded = True
        level, cand = _pick_ladder(rows)
    if not cand or level is None:
        raise RuntimeError(
            "INT-R occupancy calibrator v2 exhausted the stability ladder "
            f"{STABILITY_LADDER}; no feasible pair"
        )
    chosen = _select_row(cand)
    burstiness_miss = not bool(chosen["both"])
    spec = OccupancySpec(
        family="two_state_markov",
        alpha=float(chosen["alpha"]),
        beta=float(chosen["beta"]),
        rho0=RHO_STAR,
        burstiness_miss=burstiness_miss,
    )
    return CalibrationV2Result(
        spec=spec,
        stability_level=str(level),
        stability_hits=int(chosen["hits"]),
        stability_n_checks=int(chosen["n_checks"]),
        stability_mean_rho=float(chosen["mean_rho"]),
        stability_std_rho=float(chosen["std_rho"]),
        grid_expanded=bool(grid_expanded),
        grid_rows=tuple(rows),
    )


def a_map_from_matrix(
    client_ids: list[str],
    A: np.ndarray,
) -> dict[tuple[str, int], int]:
    out: dict[tuple[str, int], int] = {}
    for t in range(A.shape[0]):
        for j, cid in enumerate(client_ids):
            out[(cid, t)] = int(A[t, j])
    return out

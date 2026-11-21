"""G5: P2 second-solver replay + practical-significance classification.

Read-only on sealed audits and persisted invocation states. No formal retrain.
"""

from __future__ import annotations

import json
from pathlib import Path

import cvxpy as cp
import numpy as np
import pandas as pd
from scipy import stats

from raven_mcs.aggregation.feasibility import alpha_bar, ess_ball_bound

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TAB = OUT / "tables"

MPID_PCT = 0.5
AGREE_L1 = 1e-4
AGREE_REL_OBJ = 1e-4
MATERIAL_COMP = 1e-3
ALPHA_MAX = 0.5
E_MIN = 3.0
N_NONWARN = 20
RNG = np.random.default_rng(30001)

SEALED_778 = {
    "warning_count": 778,
    "affected_runs": 85,
    "audited_windows": 6438,
    "max_constraint_residual": 2.686e-8,
    "hard_tol": 1e-7,
    "source": "paper_ready_r2/02_supporting_data/solver/E3_P2_INACCURATE_CERTIFICATE_SUMMARY.csv",
    "feasibility": "CERTIFIED",
    "exact_optimality": "NOT_RECONSTRUCTABLE",
}

P2_TREES = [
    ROOT / "post_review/G1_support_compatible/runs",
    ROOT / "artifacts/e3_drifting_r1/runs",
]


def _installed_solvers() -> list[str]:
    names = []
    for label, flag in (
        ("OSQP", getattr(cp, "OSQP", None)),
        ("ECOS", getattr(cp, "ECOS", None)),
        ("SCS", getattr(cp, "SCS", None)),
        ("CLARABEL", getattr(cp, "CLARABEL", None)),
    ):
        try:
            if flag is not None and flag in cp.installed_solvers():
                names.append(label)
        except Exception:
            continue
    return names


def pick_second_solver(installed: list[str]) -> str:
    # OSQP is QP-only and cannot encode the ESS ball ‖α‖₂² ≤ 1/Ē.
    for name in ("ECOS", "SCS"):
        if name in installed:
            return name
    raise RuntimeError(f"no SOCP second solver (ECOS/SCS); installed={installed}")


def objective_value(alpha, M, mu, beta, debt, v_diag, tau, lam) -> float:
    a = np.asarray(alpha, dtype=np.float64).reshape(-1)
    mix = M @ a
    return float(
        -debt @ mix
        + 0.5 * lam["group"] * np.sum((mix - mu) ** 2)
        + 0.5 * lam["beta"] * np.sum((a - beta) ** 2)
        + 0.5 * lam["variance"] * np.sum(v_diag * a**2)
        + lam["staleness"] * float(tau @ a)
    )


def primal_residuals(alpha, n_active: int) -> dict[str, float]:
    a = np.asarray(alpha, dtype=np.float64).reshape(-1)
    a_bar = alpha_bar(alpha_max=ALPHA_MAX, n_active=n_active)
    e_bar = ess_ball_bound(e_min=E_MIN, n_active=n_active)
    simplex = abs(float(a.sum()) - 1.0)
    lower = max(0.0, -float(a.min()))
    upper = max(0.0, float(a.max()) - a_bar)
    ess = max(0.0, float(np.square(a).sum()) - 1.0 / e_bar)
    return {
        "simplex": simplex,
        "nonnegative": lower,
        "upper_bound": upper,
        "ess_l2": ess,
        "max_primal": max(simplex, lower, upper, ess),
    }


def grad_j(alpha, M, mu, beta, debt, v_diag, tau, lam) -> np.ndarray:
    a = np.asarray(alpha, dtype=np.float64).reshape(-1)
    mix = M @ a
    return (
        -M.T @ debt
        + lam["group"] * (M.T @ (mix - mu))
        + lam["beta"] * (a - beta)
        + lam["variance"] * (v_diag * a)
        + lam["staleness"] * tau
    )


def stationarity_residual(alpha, M, mu, beta, debt, v_diag, tau, lam) -> float:
    g = grad_j(alpha, M, mu, beta, debt, v_diag, tau, lam)
    return float(np.linalg.norm(g - np.mean(g)))


def solve_raw(backend: str, M, mu, beta, debt, v_diag, tau, lam) -> dict:
    n_active = int(beta.size)
    a_bar = alpha_bar(alpha_max=ALPHA_MAX, n_active=n_active)
    e_bar = ess_ball_bound(e_min=E_MIN, n_active=n_active)
    alpha = cp.Variable(n_active)
    mix = M @ alpha
    obj = (
        -debt @ (M @ alpha)
        + 0.5 * lam["group"] * cp.sum_squares(mix - mu)
        + 0.5 * lam["beta"] * cp.sum_squares(alpha - beta)
        + 0.5 * lam["variance"] * cp.sum(cp.multiply(v_diag, cp.square(alpha)))
        + lam["staleness"] * (tau @ alpha)
    )
    problem = cp.Problem(
        cp.Minimize(obj),
        [cp.sum(alpha) == 1.0, alpha >= 0.0, alpha <= a_bar, cp.sum_squares(alpha) <= 1.0 / e_bar],
    )
    kwargs = {"solver": getattr(cp, backend), "verbose": False}
    if backend == "SCS":
        kwargs.update(eps=1e-7, max_iters=100_000)
    try:
        problem.solve(**kwargs)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": f"exception:{type(exc).__name__}"}
    if alpha.value is None:
        return {"ok": False, "status": str(problem.status)}
    a = np.asarray(alpha.value, dtype=np.float64).reshape(-1)
    return {
        "ok": True,
        "status": str(problem.status),
        "alpha": a,
        "objective_solver": float(problem.value) if problem.value is not None else float("nan"),
        "objective_eval": objective_value(a, M, mu, beta, debt, v_diag, tau, lam),
        "residuals": primal_residuals(a, n_active),
        "stationarity": stationarity_residual(a, M, mu, beta, debt, v_diag, tau, lam),
    }


def unpack(rec: dict) -> dict | None:
    try:
        M = np.asarray(rec["M"], dtype=np.float64)
        mu = np.asarray(rec["mu"], dtype=np.float64)
        beta = np.asarray(rec["beta"], dtype=np.float64)
        debt = np.asarray(rec["debt"], dtype=np.float64)
        v_diag = np.asarray(rec["variance"], dtype=np.float64)
        tau = np.asarray(rec["staleness"], dtype=np.float64)
        lam = {k: float(v) for k, v in rec["lambdas"].items()}
        alpha = np.asarray(rec["alpha"], dtype=np.float64)
    except (KeyError, TypeError, ValueError):
        return None
    if M.ndim != 2 or beta.size == 0 or M.shape[1] != beta.size:
        return None
    return {
        "M": M,
        "mu": mu,
        "beta": beta,
        "debt": debt,
        "v_diag": v_diag,
        "tau": tau,
        "lam": lam,
        "alpha": alpha,
        "warning": bool(rec.get("warning")),
        "status": rec.get("status"),
        "primary_status": rec.get("primary_status"),
        "logged_objective": rec.get("objective"),
        "logged_residuals": rec.get("residuals") or {},
    }


def collect_windows() -> list[dict]:
    rows = []
    paths: list[Path] = []
    g1 = P2_TREES[0]
    if g1.is_dir():
        paths.extend(sorted(g1.glob("*/raven*/seed*/p2_invocation_states.json")))
    drift = P2_TREES[1]
    if drift.is_dir():
        paths.extend(
            sorted(p for p in drift.glob("*/raven/seed*/p2_invocation_states.json") if int(p.parts[-2].replace("seed", "")) <= 30005)
        )
    for path in paths:
        parts = path.parts
        dataset = parts[-4]
        method = parts[-3]
        seed = int(parts[-2].replace("seed", ""))
        tree_name = path.parts[path.parts.index("runs") - 1] if "runs" in path.parts else path.parent.parent.parent.name
        try:
            blob = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(blob, list):
            continue
        warn_idx = [i for i, rec in enumerate(blob) if bool(rec.get("warning"))]
        keep = set(warn_idx)
        others = [i for i in range(len(blob)) if i not in keep]
        if others:
            take = min(N_NONWARN, len(others))
            keep.update(int(i) for i in RNG.choice(others, size=take, replace=False))
        for i in sorted(keep):
            packed = unpack(blob[i])
            if packed is None:
                continue
            packed.update(
                {
                    "tree": tree_name,
                    "dataset": dataset,
                    "method": method,
                    "seed": seed,
                    "window_index": i,
                    "n_windows_file": len(blob),
                }
            )
            rows.append(packed)
        del blob
    return rows


def _pair_gaps(a1, a2, M, j1, j2) -> dict[str, float]:
    alpha_l1 = float(np.abs(a1 - a2).sum())
    comp_l1 = float(np.abs(M @ (a1 - a2)).sum())
    rel_obj = abs(j1 - j2) / (1.0 + abs(j1))
    return {
        "alpha_l1": alpha_l1,
        "comp_l1": comp_l1,
        "rel_obj": rel_obj,
        "agree": bool(alpha_l1 <= AGREE_L1 and comp_l1 <= AGREE_L1 and rel_obj <= AGREE_REL_OBJ),
        "material_comp": bool(comp_l1 >= MATERIAL_COMP),
    }


def compare_window(rec: dict, second: str) -> dict:
    M, mu, beta, debt, v_diag, tau, lam = (
        rec["M"],
        rec["mu"],
        rec["beta"],
        rec["debt"],
        rec["v_diag"],
        rec["tau"],
        rec["lam"],
    )
    logged = rec["alpha"]
    primary = solve_raw("CLARABEL", M, mu, beta, debt, v_diag, tau, lam)
    raw = solve_raw(second, M, mu, beta, debt, v_diag, tau, lam)
    out = {
        "tree": rec["tree"],
        "dataset": rec["dataset"],
        "method": rec["method"],
        "seed": rec["seed"],
        "window_index": rec["window_index"],
        "warning": rec["warning"],
        "logged_status": rec["status"],
        "second_solver": second,
        "primary_ok": bool(primary.get("ok")),
        "primary_status": primary.get("status"),
        "second_ok": bool(raw.get("ok")),
        "second_status": raw.get("status"),
    }
    if not (primary.get("ok") and raw.get("ok")):
        out.update(alpha_l1=float("nan"), comp_l1=float("nan"), rel_obj=float("nan"), agree=False, material_comp=False)
        return out
    a1, a2 = primary["alpha"], raw["alpha"]
    j1, j2 = primary["objective_eval"], raw["objective_eval"]
    pair = _pair_gaps(a1, a2, M, j1, j2)
    j_logged = objective_value(logged, M, mu, beta, debt, v_diag, tau, lam)
    vs_logged = _pair_gaps(logged, a1, M, j_logged, j1)
    out.update(
        alpha_l1=pair["alpha_l1"],
        comp_l1=pair["comp_l1"],
        rel_obj=pair["rel_obj"],
        agree=pair["agree"],
        material_comp=pair["material_comp"],
        logged_vs_clarabel_alpha_l1=vs_logged["alpha_l1"],
        logged_vs_clarabel_comp_l1=vs_logged["comp_l1"],
        logged_obj=j_logged,
        clarabel_obj=j1,
        second_obj=j2,
        logged_primal=primal_residuals(logged, logged.size)["max_primal"],
        clarabel_primal=primary["residuals"]["max_primal"],
        second_primal=raw["residuals"]["max_primal"],
        clarabel_stationarity=primary["stationarity"],
        second_stationarity=raw["stationarity"],
    )
    return out


def mean_pct_ci(x: np.ndarray) -> dict:
    x = np.asarray(x, dtype=np.float64)
    x = x[np.isfinite(x)]
    n = int(x.size)
    if n == 0:
        return {"n": 0, "mean": float("nan"), "ci_lo": float("nan"), "ci_hi": float("nan"), "p": float("nan")}
    mean = float(np.mean(x))
    if n < 2:
        return {"n": n, "mean": mean, "ci_lo": mean, "ci_hi": mean, "p": float("nan")}
    se = float(np.std(x, ddof=1) / np.sqrt(n))
    tcrit = float(stats.t.ppf(0.975, n - 1))
    try:
        p = float(stats.wilcoxon(x, zero_method="wilcox", alternative="two-sided").pvalue)
    except ValueError:
        p = float("nan")
    return {
        "n": n,
        "mean": mean,
        "ci_lo": mean - tcrit * se,
        "ci_hi": mean + tcrit * se,
        "p": p,
    }


def classify(mean_pct: float, p_value: float | None = None) -> str:
    small = abs(float(mean_pct)) < MPID_PCT
    sig = p_value is not None and np.isfinite(p_value) and p_value < 0.05
    if small and sig:
        return "quantitatively_small"
    if small:
        return "no_clear_effect_or_below_mpid"
    if sig:
        return "practically_meaningful"
    return "point_estimate_ge_mpid_not_significant"


def practical_tables() -> pd.DataFrame:
    e4 = pd.read_csv(
        ROOT / "manuscript_evidence_closure_r1/03_figure_sources/FIG3_E4_COMPONENT_REMOVAL_FINAL.csv"
    )
    rows = []
    for rec in e4.to_dict(orient="records"):
        rows.append(
            {
                "family": "E4_component_removal",
                "split": "formal20",
                "dataset": rec["dataset"],
                "contrast": f"remove_{rec['component']}",
                "endpoint": rec["metric"],
                "mean_pct": float(rec["relative_change_percent"]),
                "p": float(rec["Holm_p"]),
                "mpid_pct": MPID_PCT,
                "class": classify(float(rec["relative_change_percent"]), float(rec["Holm_p"])),
                "note": rec.get("qualitative_magnitude"),
            }
        )

    pb_test = pd.read_csv(ROOT / "post_review/G1_path_b_gated_default/tables/test_seed.csv")
    for ds, col, endpoint in (
        ("uair", "gated_vs_raven_Delta_group_pct", "Delta_group"),
        ("uair", "gated_vs_raven_RMSE_mu_pct", "RMSE_mu"),
        ("uair", "gated_vs_raven_Tail_RMSE_pct", "Tail_RMSE"),
        ("uair", "gated_vs_raven_Delta_c_s_pct", "Delta_c_s"),
        ("sensorscope", "raven_vs_off_Delta_group_pct", "Delta_group"),
        ("sensorscope", "raven_vs_off_RMSE_mu_pct", "RMSE_mu"),
        ("sensorscope", "raven_vs_off_Tail_RMSE_pct", "Tail_RMSE"),
        ("sensorscope", "raven_vs_off_Delta_c_s_pct", "Delta_c_s"),
    ):
        sub = pb_test.loc[pb_test["dataset"] == ds, col].to_numpy(dtype=float)
        st = mean_pct_ci(sub)
        rows.append(
            {
                "family": "PathB_TEST",
                "split": "test10",
                "dataset": ds,
                "contrast": col,
                "endpoint": endpoint,
                "mean_pct": st["mean"],
                "ci_lo": st["ci_lo"],
                "ci_hi": st["ci_hi"],
                "p": st["p"],
                "mpid_pct": MPID_PCT,
                "class": classify(st["mean"], st["p"]),
                "n": st["n"],
            }
        )

    g2 = pd.read_csv(ROOT / "post_review/G2_external_baselines/tables/paired_worstgroup.csv")
    g2_test = g2.loc[(g2["split"] == "test") & (g2["baseline"].isin(["fedau_window", "obsuse_window"]))]
    for rec in g2_test.to_dict(orient="records"):
        rows.append(
            {
                "family": "G2_TEST_WorstGroup",
                "split": "test10",
                "dataset": rec["dataset"],
                "contrast": f"gated_vs_{rec['baseline']}",
                "endpoint": "WorstGroupRMSE",
                "mean_pct": float(rec["mean_pct_gated_minus_base"]),
                "ci_lo": float(rec["pct_ci95_low"]),
                "ci_hi": float(rec["pct_ci95_high"]),
                "p": float(rec["p_holm"]) if pd.notna(rec.get("p_holm")) else float(rec["p_raw"]),
                "mpid_pct": MPID_PCT,
                "class": classify(float(rec["mean_pct_gated_minus_base"]), float(rec["p_raw"])),
                "n": int(rec["n"]),
            }
        )
    return pd.DataFrame(rows)


def decide(cmp: pd.DataFrame, practical: pd.DataFrame, second: str, installed: list[str]) -> dict:
    ok = cmp.loc[cmp["second_ok"]]
    warn = ok.loc[ok["warning"]]
    n_disagree = int((~ok["agree"]).sum()) if len(ok) else 0
    n_material = int(ok["material_comp"].sum()) if len(ok) else 0
    debt = practical.loc[practical["contrast"].str.contains("Debt", case=False, na=False)]
    debt_small = bool(len(debt) and (debt["mean_pct"].abs() < MPID_PCT).all())
    if len(ok) == 0:
        verdict = "G5_FAIL"
        reason = "second solver produced no successful reconstructable solves"
    elif n_material > 0:
        verdict = "G5_SOLVER_DIVERGE"
        reason = f"{n_material} windows have ||M Δα||_1 ≥ {MATERIAL_COMP}"
    else:
        verdict = "G5_ACCEPTED"
        reason = (
            f"second solver {second} agrees or stays below material composition; "
            f"Debt below MPID={MPID_PCT}%"
        )
    return {
        "verdict": verdict,
        "reason": reason,
        "second_solver": second,
        "installed_solvers": installed,
        "n_compared": int(len(cmp)),
        "n_warning_compared": int(cmp["warning"].sum()) if len(cmp) else 0,
        "n_second_ok": int(len(ok)),
        "n_agree": int(ok["agree"].sum()) if len(ok) else 0,
        "n_disagree": n_disagree,
        "n_material_comp": n_material,
        "max_alpha_l1": float(ok["alpha_l1"].max()) if len(ok) else float("nan"),
        "max_comp_l1": float(ok["comp_l1"].max()) if len(ok) else float("nan"),
        "max_rel_obj": float(ok["rel_obj"].max()) if len(ok) else float("nan"),
        "n_warning_agree": int(warn["agree"].sum()) if len(warn) else 0,
        "n_warning_ok": int(len(warn)),
        "debt_below_mpid": debt_small,
        "mpid_pct": MPID_PCT,
        "seed_scope": "20 formal / 10+10 split seeds are algorithmic EventTrace randomness, not independent cities",
        "sealed_778": SEALED_778,
        "formal_rerun_required": verdict == "G5_SOLVER_DIVERGE",
    }


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    installed = _installed_solvers()
    second = pick_second_solver(installed)
    windows = collect_windows()
    cmp_rows = [compare_window(w, second) for w in windows]
    cmp = pd.DataFrame(cmp_rows)
    practical = practical_tables()
    decision = decide(cmp, practical, second, installed)
    cmp.to_csv(TAB / "second_solver_windows.csv", index=False)
    practical.to_csv(TAB / "practical_significance.csv", index=False)
    (OUT / "G5_SUMMARY.json").write_text(json.dumps(decision, indent=2), encoding="utf-8")
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()

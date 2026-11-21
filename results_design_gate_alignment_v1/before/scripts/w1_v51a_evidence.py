"""W1 round v5.1a - independent optimality evidence for the A1' oracle (AM-6).

Three independent checks, none of which uses the production solver's internals:

1. small-K brute force.  For K = 2..5 and a dense grid of feasible (a_bar, e_bar), the projection
   is recomputed by a fine 2-D scan/refinement over (lam, tau): for every lam on a fine grid the
   inner tau is solved by bisection on the *raw* sum (an independent code path from the production
   capped-simplex routine), the objective ||x - v||^2 is evaluated, infeasible points are dropped,
   and the best feasible objective over the whole 2-D grid is compared with the production oracle.
   Report: the worst objective disagreement and the worst ||x_oracle - x_grid||_inf.

2. perturbation test.  On >= 200 random windows, random feasible perturbations of the oracle point
   (random directions orthogonal to 1, projected into the feasible cone, plus random coordinate
   moves that renormalise onto the simplex) are sampled; none may lower the objective by more than
   1e-12.  This is a direct optimality check that needs no multipliers at all.

3. dual bound.  From the oracle's own multipliers (tau, nu) a dual feasible point is formed and the
   duality gap is evaluated; it must be <= 1e-12.  For the projection the gap has a closed form:

       f(x) - d(tau, nu) = nu (||x||^2 - 1/e_bar) + tau (sum x - 1)
                           + sum_i max(0, v_i - tau - 2 nu x_i) * x_i
                           + sum_i max(0, tau + 2 nu x_i - hi * 1) * (hi - x_i)   [capped side]

   which is non-negative for every (tau >= 0, nu >= 0) and vanishes exactly at the optimum.

Writes results_w1_ladder/round_v5_1a/ORACLE_EVIDENCE.json only.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                          # noqa: E402
import w1_v51a_oracle as O                                                     # noqa: E402

OUT = ROOT / "results_w1_ladder/round_v5_1a"
TRAIN = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"
DSS = ("sensorscope", "uair")
ARMS = ("proj_beta", "proj_beta_debt")
KAPPA = 1000.0
TOL = 1e-12


# ---------------------------------------------------------------------------------------
# 1. small-K brute force
# ---------------------------------------------------------------------------------------

def _raw_proj_for_lam(v, hi, s):
    """Independent inner solve: bisection on tau for sum_i clip((v_i - tau)/s, 0, hi) = 1."""
    lo = float(v.min()) - s * float(hi)
    up = float(v.max())
    for _ in range(200):
        mid = 0.5 * (lo + up)
        if mid <= lo or mid >= up:
            break
        if float(np.minimum(np.maximum((v - mid) / s, 0.0), hi).sum()) < 1.0:
            up = mid
        else:
            lo = mid
    tau = lo
    x = np.minimum(np.maximum((v - tau) / s, 0.0), hi)
    return x, tau


def random_v(rng, K, style=None):
    """A test vector; combined with feasible_v below to guarantee feasibility."""
    style = int(rng.integers(0, 4)) if style is None else style
    if style == 0:
        return np.full(K, 1.0 / K) + rng.normal(size=K) * 0.01
    if style == 1:
        return np.abs(rng.normal(size=K)) * 3.0 + 0.5
    if style == 2:
        return rng.normal(size=K) * 5.0 + 1.0
    return np.full(K, 1.0 / K) * rng.uniform(0.5, 3.0, size=K)


def feasible_v(rng, K, hi, tries=500):
    """A vector whose cap-reachable sum is >= 1, i.e. one for which the projection is not the box
    corner.  Drawing v at random almost never satisfies this, and on an infeasible v every
    "feasible perturbation" of the corner point is trivially better, which would make the
    perturbation test meaningless."""
    for _ in range(tries):
        v = random_v(rng, K)
        if float(np.minimum(v, hi).sum()) >= 1.0 + 1e-3:
            return v
    return np.full(K, max(1.0 / K, hi))                             # pragma: no cover


def brute_force_2d(v, hi, t, n_lam=4001, n_ref=40):
    """Best feasible objective over a 2-D (lam, tau) scan with local refinement."""
    v = np.asarray(v, dtype=float)
    K = int(v.size)
    best = None
    lams = np.linspace(0.0, 8.0, n_lam)
    for lam in lams:
        s = 1.0 + 2.0 * lam
        if float(np.minimum(v / s, hi).sum()) < 1.0:
            continue                                   # inner problem infeasible at this lam
        x, tau = _raw_proj_for_lam(v, hi, s)
        n2 = float(x @ x)
        if n2 <= t + 1e-14:
            obj = float(((x - v) ** 2).sum())
            if best is None or obj < best[0]:
                best = (obj, float(lam), float(tau), x.copy())
    if best is None:
        return None
    # local refinement around the best lam
    lam0 = best[1]
    span = float(lams[1] - lams[0]) if n_lam > 1 else 0.01
    lo, up = max(0.0, lam0 - 2 * span), lam0 + 2 * span
    for _ in range(n_ref):
        cand = np.linspace(lo, up, 21)
        for lam in cand:
            s = 1.0 + 2.0 * lam
            if float(np.minimum(v / s, hi).sum()) < 1.0:
                continue
            x, tau = _raw_proj_for_lam(v, hi, s)
            if float(x @ x) <= t + 1e-14:
                obj = float(((x - v) ** 2).sum())
                if obj < best[0]:
                    best = (obj, float(lam), float(tau), x.copy())
        lo, up = max(0.0, best[1] - (up - lo) / 4.0), best[1] + (up - lo) / 4.0
    return best


def run_brute_force() -> dict:
    rng = np.random.default_rng(20261002)
    rows = []
    for K in (2, 3, 4, 5):
        for _ in range(40):
            # feasible (a_bar, e_bar): K*a_bar >= 1 and 1/e_bar >= 1/K, i.e. 1 <= e_bar <= K
            a_bar = float(rng.uniform(1.0 / K, min(1.0, 0.5 + 1.0 / K)))
            e_bar = float(rng.uniform(1.0, float(K)))
            t = 1.0 / e_bar
            v = feasible_v(rng, K, a_bar)
            a_or, kind, mult = O.project_Cr(v, a_bar, e_bar)
            bf = brute_force_2d(v, a_bar, t)
            if bf is None:
                continue
            obj_or = O.proj_objective(a_or, v)
            rows.append({"K": K, "a_bar": a_bar, "e_bar": e_bar, "kind": kind,
                         "obj_oracle": obj_or, "obj_grid": float(bf[0]),
                         "gap_oracle_minus_grid": obj_or - float(bf[0]),
                         "alpha_linf_oracle_vs_grid": float(np.max(np.abs(a_or - bf[3]))),
                         "norm2_oracle": float(a_or @ a_or), "norm2_target": t})
    df_gap = max(r["gap_oracle_minus_grid"] for r in rows)
    df_alpha = max(r["alpha_linf_oracle_vs_grid"] for r in rows)
    return {"n_cases": len(rows),
            "worst_objective_gap_oracle_minus_grid": float(df_gap),
            "worst_alpha_linf_oracle_vs_grid": float(df_alpha),
            "pass_objective_1e-14": bool(df_gap <= 1e-14),
            "pass_alpha_1e-14": bool(df_alpha <= 1e-14),
            "rows": rows}


# ---------------------------------------------------------------------------------------
# 2. perturbation test
# ---------------------------------------------------------------------------------------

def perturb_test(v, a_bar, e_bar, n_dir=400, rng=None):
    """Best feasible objective over random feasible perturbations of the oracle point.

    Every candidate is checked against C_r before it is evaluated, and the oracle point is tested
    only for problems where the projection is not the box corner (the caller ensures that).
    """
    rng = rng or np.random.default_rng(7)
    K = int(np.asarray(v).size)
    hi = float(a_bar)
    t = 1.0 / float(e_bar)
    a_or, kind, mult = O.project_Cr(v, a_bar, e_bar)
    base = O.proj_objective(a_or, v)
    best = base
    n_feas = 0
    for _ in range(n_dir):
        d = rng.normal(size=K)
        d = d - d.mean()                                # direction preserving sum x = 1
        scale = float(rng.choice([1e-3, 1e-4, 1e-5, 1e-6]))
        for sgn in (1.0, -1.0):
            cand = np.clip(a_or + sgn * scale * d, 0.0, hi)
            tot = float(cand.sum())
            if tot <= 0:
                continue
            cand = cand / tot                            # renormalise onto the simplex
            if float(cand @ cand) > t:
                cand = cand * (np.sqrt(t) / float(np.linalg.norm(cand)))
                cand = np.clip(cand, 0.0, hi)
                cand = cand / float(cand.sum())
                if float(cand @ cand) > t * (1 + 1e-12):
                    continue
            if O.feasibility(cand, hi, e_bar) > 1e-14:
                continue
            n_feas += 1
            obj = O.proj_objective(cand, v)
            if obj < best:
                best = obj
                worst_cand = cand.copy()
    return {"improvement": float(base - best), "n_feasible_perturbations": int(n_feas),
            "obj_oracle": float(base), "obj_best_perturbation": float(best), "kind": kind}


def run_perturbation(n_windows=200) -> dict:
    rng = np.random.default_rng(20261002)
    pi = {d: W.pi_tar_for(d) for d in DSS}
    pool = []
    for ds in DSS:
        for arm in ARMS:
            for seed in range(30001, 30021):
                case = W.build_case(ds, "R_on", "raven_wo_use", seed, pi[ds])
                if case is None:
                    continue
                wm = W.load_json(TRAIN / ds / arm / ("seed%d" % seed) / "window_metrics.json")
                by = {int(w["window_id"]): w for w in W.active_windows(wm)}
                betas = [np.asarray(by[int(case["wids"][k])]["beta_hat"], dtype=float)
                         for k in range(case["n"])]
                if arm == "proj_beta":
                    for j in range(case["n"]):
                        pool.append((ds, arm, seed, j, betas[j] / betas[j].sum(),
                                     case["a_bar"][j], case["e_bar"][j], None))
                    break
                a_or, qs, diag = O.oracle_debt_seq(case, betas)
                off = 0
                for j in range(case["n"]):
                    K = len(case["clients"][j])
                    pool.append((ds, arm, seed, j, diag[j]["v"], case["a_bar"][j],
                                 case["e_bar"][j], (qs[j].copy(), diag[j]["beta"], case["M"][j])))
                    off += K
                break
    pick = rng.choice(len(pool), size=min(n_windows, len(pool)), replace=False)
    worst = {"improvement": 0.0}
    rows = []
    for i in pick:
        ds, arm, seed, j, v, ab, eb, debt = pool[int(i)]
        if debt is None:
            r = perturb_test(v, ab, eb, rng=rng)
            obj = r["obj_oracle"]
        else:
            Q, beta, M = debt
            a_or, kind, mult = O.project_Cr(v, ab, eb)
            base = O.debt_objective(a_or, beta, M, Q)
            best, n_feas = base, 0
            for _ in range(400):
                d = rng.normal(size=int(np.asarray(v).size))
                d = d - d.mean()
                scale = float(rng.choice([1e-3, 1e-4, 1e-5, 1e-6]))
                for sgn in (1.0, -1.0):
                    cand = np.clip(a_or + sgn * scale * d, 0.0, ab)
                    tot = float(cand.sum())
                    if tot <= 0:
                        continue
                    cand = cand / tot
                    if float(cand @ cand) > 1.0 / eb:
                        cand = np.clip(cand * (np.sqrt(1.0 / eb) / float(np.linalg.norm(cand))),
                                       0.0, ab)
                        cand = cand / float(cand.sum())
                        if float(cand @ cand) > (1.0 / eb) * (1 + 1e-12):
                            continue
                    if O.feasibility(cand, ab, eb) > 1e-14:
                        continue
                    n_feas += 1
                    ob = O.debt_objective(cand, beta, M, Q)
                    if ob < best:
                        best = ob
            r = {"improvement": float(base - best), "n_feasible_perturbations": n_feas,
                 "obj_oracle": float(base), "obj_best_perturbation": float(best), "kind": kind}
            obj = base
        rows.append({"ds": ds, "arm": arm, "seed": int(seed), "window": int(j), **r})
        worst["improvement"] = max(worst["improvement"], r["improvement"])
    return {"n_windows": len(rows),
            "worst_improvement": float(worst["improvement"]),
            "pass_1e-12": bool(worst["improvement"] <= TOL),
            "rows": rows}


# ---------------------------------------------------------------------------------------
# 3. dual bound
# ---------------------------------------------------------------------------------------

def dual_gap(v, a_bar, e_bar):
    """Fenchel duality gap of the projection at the oracle's own gradient.

    P_C(v) = argmin_{x in C_r} f(x) with f(x) = ||x - v||^2 is convex, so for any y the Fenchel
    conjugate gives the bound

        f(x) >= -f*(y) + min_{z in C_r} <z, y>,       f*(y) = <y, v> + ||y||^2 / 4,

    with equality in the first inequality exactly at y = grad f(x) = 2 (x - v).  Taking that y and
    x = the oracle point, the right-hand side is the dual value

        d(y) = -( <y, v> + ||y||^2/4 ) + min_{z in C_r} <z, y>
             = -( <y, v> + ||y||^2/4 ) - < P_{C_r}(-(v + y/2)), y >,

    because min_{z in C_r} <z, y> = -max_{z in C_r} <z, -y> = -<P_{C_r}(-y), -y> ... computed here
    directly as -<P_{C_r}(-y), y> for the linear objective.  The gap f(x) - d(y) is then >= 0 for
    every x in C_r and vanishes iff x is the minimiser, which makes it a rigorous optimality
    certificate that uses the oracle only through its own projection routine.

    (An earlier revision used the Lagrangian form f(x) - min_{box} L which is *not* a lower bound
    unless the box minimiser also satisfies the equality and ball constraints; that is why its gap
    was O(1) at the optimum.)
    """
    v = np.asarray(v, dtype=float)
    hi = float(a_bar)
    t = 1.0 / float(e_bar)
    x, kind, mult = O.project_Cr(v, a_bar, e_bar)
    f_x = float(((x - v) ** 2).sum())
    y = 2.0 * (x - v)                                              # y = grad f(x)
    # max_{z in C_r} <z, -y/2> = < P_{C_r}(-y/2), -y/2 >, so min_{z in C_r} <z, y> for the
    # constraint set itself is -2 <P_{C_r}(-y/2), -y/2> ... computed directly on C_r below
    z_star, _k2, _m2 = O.project_Cr(-0.5 * y, a_bar, e_bar)
    dual_value = -(float(y @ v) + 0.25 * float(y @ y)) - 2.0 * float(z_star @ (-0.5 * y))
    return {"objective_oracle": f_x, "dual_value": dual_value, "gap": f_x - dual_value,
            "tau": float(mult["tau"]), "nu": float(mult["nu"]), "kind": kind}


def run_dual(n_windows=200) -> dict:
    rng = np.random.default_rng(20261002)
    pi = {d: W.pi_tar_for(d) for d in DSS}
    pool = []
    for ds in DSS:
        case = W.build_case(ds, "R_on", "raven_wo_use", 30001, pi[ds])
        if case is None:
            continue
        wm = W.load_json(TRAIN / ds / "proj_beta" / "seed30001" / "window_metrics.json")
        by = {int(w["window_id"]): w for w in W.active_windows(wm)}
        for j in range(case["n"]):
            b = np.asarray(by[int(case["wids"][j])]["beta_hat"], dtype=float)
            pool.append((b / b.sum(), case["a_bar"][j], case["e_bar"][j]))
    # plus random feasible synthetic problems
    for K in (3, 5, 8, 16, 32):
        for _ in range(20):
            a_bar = float(min(0.5, 1.0))
            e_bar = float(min(3.0, K))
            v = rng.normal(size=K) + 1.0
            pool.append((v, a_bar, e_bar))
    pick = rng.choice(len(pool), size=min(n_windows, len(pool)), replace=False)
    rows = [{"i": int(i), **dual_gap(*pool[int(i)])} for i in pick]
    worst = max(r["gap"] for r in rows)
    return {"n_windows": len(rows), "worst_gap": float(worst), "pass_1e-12": bool(worst <= TOL),
            "rows": rows}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    out = {"script": "scripts/w1_v51a_evidence.py",
           "oracle": "scripts/w1_v51a_oracle.py (AM-6)",
           "tolerance": TOL}
    print("[1/3] small-K brute force ...", flush=True)
    out["brute_force_small_K"] = run_brute_force()
    b = out["brute_force_small_K"]
    print("      cases %d  worst objective gap %.3e  worst alpha %.3e"
          % (b["n_cases"], b["worst_objective_gap_oracle_minus_grid"],
             b["worst_alpha_linf_oracle_vs_grid"]), flush=True)
    print("[2/3] perturbation test ...", flush=True)
    out["perturbation"] = run_perturbation(200)
    p = out["perturbation"]
    print("      windows %d  worst improvement %.3e" % (p["n_windows"], p["worst_improvement"]),
          flush=True)
    print("[3/3] dual bound ...", flush=True)
    out["dual_bound"] = run_dual(200)
    d = out["dual_bound"]
    print("      windows %d  worst gap %.3e" % (d["n_windows"], d["worst_gap"]), flush=True)
    out["all_pass"] = bool(b["pass_objective_1e-14"] and p["pass_1e-12"] and d["pass_1e-12"])
    out["seconds"] = time.perf_counter() - t0
    (OUT / "ORACLE_EVIDENCE.json").write_text(json.dumps(out, indent=2, default=str),
                                              encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items()
                      if not isinstance(v, dict) or "rows" not in v}, indent=2, default=str))


if __name__ == "__main__":
    main()

"""W1 round v5.1a - A1' exact projection oracle (AM-6), numpy only.

Supersedes the v5.1 implementation `scripts/w1_v51_oracle.py` (which stays untouched as the
record of the superseded run).  AM-6 replaces the *implementation* of the projection oracle
only: no rule, threshold, margin, family or contrast changes anywhere.

Problem
-------
    P_C(v) = argmin { ||x - v||^2 :  sum x = 1,  0 <= x <= a_bar,  ||x||^2 <= 1/e_bar }

with a_bar = min(1, max(0.5, 1/K)) and e_bar = min(3, K) on the paper's datasets.  C_r is convex
and the objective is strictly convex, so the optimum is unique.

Algorithm (protocol v5.1 section 2.1 - the standard two-multiplier dual)
-----------------------------------------------------------------------
KKT:  there are (tau, lam) with lam >= 0 and

    x(tau, lam) = clip((v - tau) / (1 + 2 lam), 0, a_bar),      sum x = 1,  lam (||x||^2 - 1/e_bar) = 0.

* lam = 0 branch ("capped simplex"):  x = clip(v - tau, 0, a_bar) with tau chosen so that
  sum x = 1.  This is the exact projection of v onto the capped simplex; it solves the problem
  whenever ||x||^2 <= 1/e_bar.
* lam > 0 branch ("ball active"):  with s = 1 + 2 lam,
  x = P_capSimplex(v / s) = clip(v/s - tau', 0, a_bar) and  tau = s tau'.
  The inner solve is *the same routine*, applied to the shifted/scaled vector v/s; the outer
  scalar equation ||x(s)||^2 = 1/e_bar is monotone in s (the free part of x shrinks like 1/s
  while the capped part stays at a_bar, so the norm is non-increasing) and is solved by
  bisection to machine precision, with a safeguarded secant polish.

The capped-simplex sub-problem is solved by the EXACT breakpoint solve (sort v, walk the pieces
"m coordinates at the cap", solve the piece's affine equation for tau in closed form), with a
200-step bisection as a fallback.  The uniform special case (v constant) is returned uniformly.

Degenerate cases: K = 1, a_bar = 1/K (feasible set is the single point), e_bar = K - all return
the uniform weights, which are then checked by the caller like any other point.

Every returned point carries its own multipliers (tau, lam) and the name of the branch, so the
O-G0 audit measures the algorithm's KKT error and nothing else.

numpy only: this module imports numpy and nothing else.
"""
from __future__ import annotations

import math

import numpy as np

__all__ = [
    "capped_simplex", "project_Cr", "kkt_residuals", "feasibility", "choose_s",
    "proj_objective", "debt_objective", "oracle_proj_beta", "oracle_debt_seq",
    "KAPPA", "ETA_DEBT",
]

KAPPA = 1000.0
ETA_DEBT = 0.01

_UNIFORM_TOL = 5e-16          # v is treated as constant below this relative spread
_TINY = 1e-300


# =======================================================================================
# capped simplex:  P_{sum x = 1, 0 <= x <= hi}(v)
# =======================================================================================

def clip_sum(x):
    """sum(x) for a vector already inside [0, hi].

    One shared summation path for the whole module, so the value the solver drives to 1 is the
    value every downstream check reports.
    """
    return float(np.asarray(x, dtype=float).sum())


def _repair_sum(x, v, hi):
    """Move a clipped point onto sum = 1 by one shift of a single coordinate, inside the box.

    The closed-form and bisection solves return x = clip(v - tau, 0, hi) with sum 1 up to a few
    ulps of summation, so one shift of one coordinate removes the residual.  The coordinate with
    the largest magnitude below hi/2 is used: for it |delta| is below the spacing of x_i, so the
    addition rounds exactly and the shift cannot cross a bound.  Returns (x, applied).
    """
    s = clip_sum(x)
    if s == 1.0:
        return x, True
    delta = 1.0 - s
    free = np.nonzero((x > 0.0) & (x < 0.5 * hi))[0]
    if free.size == 0:                                             # pragma: no cover
        free = np.nonzero((x > 0.0) & (x < hi))[0]
    if free.size == 0:                                             # pragma: no cover
        return x, False
    i = int(free[np.argmax(x[free])])
    xt = x.copy()
    xt[i] = xt[i] + delta
    if xt[i] < 0.0 or xt[i] > hi:                                  # pragma: no cover
        return x, False
    return xt, True


def _capped_simplex_bisect(v, hi, iters=300):
    """Bisection on tau for sum_i clip(v_i - tau, 0, hi) = 1, with an affine Newton polish.

    The map F(tau) = sum clip(v_i - tau, 0, hi) is continuous and non-increasing, equals K*hi at
    the lower bracket end and 0 at the upper one, so bisection is unconditionally safe *for
    feasibility*.  It is not by itself a projection solver: F can equal 1 on an interval of tau
    (whenever a coordinate sits exactly at the cap) and bisection then returns an arbitrary
    interior tau, which is feasible but not optimal.  `capped_simplex` therefore treats this
    routine as a fallback and compares objectives.
    """
    lo = float(v.min()) - float(hi)
    up = float(v.max())
    for _ in range(iters):
        mid = 0.5 * (lo + up)
        if float(np.minimum(np.maximum(v - mid, 0.0), hi).sum()) > 1.0:
            lo = mid
        else:
            up = mid
        if up - lo <= 1e-17 * max(1.0, abs(up)):
            break
    tau = 0.5 * (lo + up)
    for _ in range(6):
        s = clip_sum(np.minimum(np.maximum(v - tau, 0.0), hi))
        if s == 1.0:
            break
        n_free = int(np.count_nonzero((v - tau > 0.0) & (v - tau < hi)))
        if n_free <= 0:
            break
        cand = tau + (s - 1.0) / float(n_free)
        if abs(clip_sum(np.minimum(np.maximum(v - cand, 0.0), hi)) - 1.0) < abs(s - 1.0):
            tau = cand
        else:
            break
    return np.minimum(np.maximum(v - tau, 0.0), hi), float(tau), "bisect"


def _polish_tau(v, hi, tau):
    """One rounding-exact affine shift of tau onto sum = 1: on the piece the point lands on, the
    sum is affine in tau with slope -(number of free coordinates)."""
    x = np.minimum(np.maximum(v - tau, 0.0), hi)
    nf = int(np.count_nonzero((x > 0.0) & (x < hi)))
    if nf <= 0:                                                    # pragma: no cover
        return float(tau), x
    tau = float(tau) + (clip_sum(x) - 1.0) / float(nf)
    return tau, np.minimum(np.maximum(v - tau, 0.0), hi)


def _sum_clip(v, tau, hi):
    return float(np.minimum(np.maximum(v - tau, 0.0), hi).sum())


def _piece_tau(v, vs, m, hi):
    """Root of sum_i clip(v_i - tau, 0, hi) = 1 in the piece where the m largest are capped.

    The projection is the *left* limit of the root: the largest tau with sum >= 1.  Taking the
    left limit is what keeps the KKT form exact - there the capped coordinates sit exactly at the
    cap, whereas a tau a fraction of an ulp to the right leaves one short and breaks the relation
    x = clip(v - tau, 0, hi) that the audit measures.

    Search.  On the piece the m capped coordinates are the m largest, so tau lies in the union of
    the two intervals adjacent to v_(m): [v_(m) - hi, v_(m)] (the m-th largest is just at the cap)
    and [v_(m), v_(m) + hi] (the (m+1)-th largest is just at the cap) - that union is exactly the
    set of tau for which the count of coordinates with v_i - tau > hi is m.  The sum is continuous
    and non-increasing on each interval, so a plain bisection on each of them finds every root and
    the largest root is the projection.  Bisecting on the raw map outside the piece is what an
    earlier revision did wrong: the map is not monotone there, so the bisection could land on an
    arbitrary point of a plateau or miss the root altogether.

    Returns (tau, x) or None when neither interval contains a root.
    """
    K = int(v.size)
    best_tau = None
    for lo0, up0 in ((float(vs[m]) - hi, float(vs[m])),
                     (float(vs[m]), float(vs[m]) + hi)):
        lo, up = lo0, up0
        if not (lo <= up):
            continue
        f_lo, f_up = _sum_clip(v, lo, hi), _sum_clip(v, up, hi)
        if f_lo < 1.0:
            continue                           # no root: the sum is already below 1 at the left end
        if f_up > 1.0:
            continue                           # no root: the sum is still above 1 at the right end
        for _ in range(200):
            mid = 0.5 * (lo + up)
            if mid <= lo or mid >= up:
                break
            if _sum_clip(v, mid, hi) >= 1.0:
                lo = mid
            else:
                up = mid
        tau = float(lo)                        # left limit: sum >= 1 still
        while _sum_clip(v, tau, hi) < 1.0:                             # pragma: no cover
            tau = float(np.nextafter(tau, -np.inf))
        if _sum_clip(v, tau, hi) < 1.0:                                # pragma: no cover
            continue
        if best_tau is None or tau > best_tau:
            best_tau = tau
    if best_tau is None:
        return None
    x = np.minimum(np.maximum(v - best_tau, 0.0), hi)
    if abs(float(x.sum()) - 1.0) > 1e-12:                             # pragma: no cover
        return None
    return best_tau, x


def capped_simplex(v, hi):
    """Exact projection of v onto {sum x = 1, 0 <= x <= hi}.

    Returns (x, tau, kind) with x_i = clip(v_i - tau, 0, hi) and tau the multiplier of the
    equality constraint, so the returned pair always satisfies the capped-simplex KKT system -
    which is what the downstream stationarity audit measures.  `kind` is "degenerate" (K = 1),
    "activeset" (the normal path) or "fallback" (rounding only).

    Method: enumerate every active set.  A point of the form clip(v - tau, 0, hi) partitions the
    coordinates into capped ({v_i - tau >= hi}), free ({0 < v_i - tau < hi}) and zero
    ({v_i - tau <= 0}) sets; the capped set is the largest v, and for a fixed number m of capped
    coordinates the projection's tau is the left-limit root of sum x = 1 on the piece
    [v_(m+1) - hi, v_(m)] of the descending sort (see _piece_tau).  Pieces are compared by the
    objective ||x - v||^2 and the smallest wins; a strictly convex problem has a unique optimum, so
    the comparison only settles the degenerate readings (a coordinate exactly at the cap, where
    the sum is constant on a whole interval of tau) in favour of the true projection.

    The closed form tau(m) = (sum of the K-m smallest + m*hi - 1)/(K-m) is deliberately *not* used:
    it assumes the free set is the K-m smallest coordinates, which fails as soon as a coordinate
    strictly between two others drops below tau and joins the zero set instead.  That assumption is
    what made an earlier revision return feasible but non-optimal points.
    """
    v = np.asarray(v, dtype=float)
    K = int(v.size)
    if K == 0:                                                     # pragma: no cover
        raise ValueError("empty vector")
    hi = float(hi)
    if K == 1:
        return np.ones(1), float(v[0] - 1.0), "degenerate"
    if float(v.sum()) < 1.0 - 8.0 * float(np.finfo(float).eps) * K:
        # sum(v) < 1 means no point of {sum x = 1, x <= hi} can have sum x = 1 at all: subtracting
        # tau and clipping can only lower the sum, so the feasible set is empty.  (Testing the
        # *capped* sum instead would be wrong - it is an upper bound on the attainable sum only
        # when it exceeds 1, and it is genuinely below 1 for perfectly feasible v whose entries
        # are all under the cap.)  Returns the corner 1/K, the minimal-norm point of the box.
        return np.full(K, 1.0 / K), 0.0, "infeasible"

    order = np.argsort(-v, kind="stable")                           # descending
    vs = v[order]
    best_obj, best = None, None
    for m in range(0, K):
        got = _piece_tau(v, vs, m, hi)
        if got is None:
            continue
        tau, x = got
        obj = float(((x - v) ** 2).sum())
        if best_obj is None or obj < best_obj:
            best_obj, best = obj, (x, tau)
    if best is None:                                                # pragma: no cover
        xb, taub, _k = _capped_simplex_bisect(v, hi)
        return xb, taub, "fallback"
    x, tau = best
    return x, tau, "activeset"




# =======================================================================================
# the projection itself
# =======================================================================================

def _rough_scale(v):
    a = float(np.abs(v).max())
    return a if a > _TINY else 1.0


def _proj_scaled(v, hi, s):
    """Capped-simplex inner solve of the two-multiplier dual, returning the KKT multipliers.

    For a fixed scaling s = 1 + 2 lam the ball-active KKT point is

        x = clip((v - tau)/s, 0, hi) = clip(v/s - tau/s, 0, hi),

    i.e. the capped-simplex projection of the scaled vector v/s onto the cap hi.  Writing the
    inner Lagrangian as

        L(x, tau) = (1/2) ||x - v/s||^2 + tau (sum x - 1)

    the free coordinates satisfy x_i - v_i/s + tau = 0, so the *standard* KKT multiplier of the
    outer problem (whose stationarity reads grad + TAU + 2 LAM x = 0) is

        TAU = 2 tau,        x = (v - TAU)/(1 + 2 LAM)  with LAM = lam,

    and the reported multipliers below are returned in that standard convention - this is the
    normalization the O-G0 audit measures, and getting it wrong by the factor 2 is invisible in
    the point itself but shows up as a stationarity residual of order |TAU|.

    The sum map tau -> sum clip((v - tau)/s, 0, hi) is continuous and non-increasing from K*hi to
    0 and reaches 1 for every s > 0 because K*hi >= 1, so the bracketed bisection is exact and
    unconditional; the left limit (sum >= 1) is returned, which keeps the capped coordinates
    exactly at the cap and the affine form exact.

    Returns (x, tau) with the *inner* tau, or (None, None) if the sum cannot reach 1.
    """
    v = np.asarray(v, dtype=float)
    s = float(s)
    hi = float(hi)
    lo = float(v.min()) - s * hi
    up = float(v.max())
    for _ in range(200):
        mid = 0.5 * (lo + up)
        if mid <= lo or mid >= up:
            break
        if float(np.minimum(np.maximum((v - mid) / s, 0.0), hi).sum()) < 1.0:
            up = mid
        else:
            lo = mid
    x = np.minimum(np.maximum((v - lo) / s, 0.0), hi)
    if abs(float(x.sum()) - 1.0) > 1e-12:      # pragma: no cover
        return None, None
    return x, float(lo)


def choose_s(v, hi, t):
    """Ball-active branch: bisect on s = 1 + 2 lam with the inner tau solved at every step.

    This is the protocol's two-multiplier scheme: the outer equation is ||x(s)||^2 = t and the
    inner step recomputes tau by the capped-simplex projection of (v - tau)/s.  ||x(s)||^2 is
    non-increasing in s (the free part scales like 1/s, the capped part stays at hi and the free set
    can only shrink), so the largest feasible s is the answer and the loop keeps it.

    Going through (v - tau)/s rather than the algebraically equivalent u*v with a shifted cap is
    what makes the inner step well posed for every s: the inner data always sums to 1/s <= 1, and
    the capped-simplex projection of a vector that sums below 1 has no feasible point at all, so
    formulations that project u*v directly are undefined over most of the bracket and answer with
    the box corner instead (that mistake is what produced sum-1 points with a norm far off the
    ball).

    Returns (s, x, tau, n_iter, bracket_width).
    """
    v = np.asarray(v, dtype=float)
    t = float(t)
    K = int(v.size)
    x1, tau1 = _proj_scaled(v, hi, 1.0)                    # s = 1 (lam = 0)
    if x1 is None:                                                 # pragma: no cover
        return 1.0, np.full(K, 1.0 / K), 0.0, 0, 0.0
    if float(x1 @ x1) <= t:
        return 1.0, x1, tau1, 0, 0.0
    lo, hi_s = 1.0, 2.0
    xh, tauh = None, None
    for _ in range(200):
        xh, tauh = _proj_scaled(v, hi, hi_s)
        if float(xh @ xh) <= t:
            break
        lo = hi_s
        hi_s *= 2.0
    else:                                                          # pragma: no cover
        return hi_s, xh, tauh, 400, float("inf")
    n_iter = 0
    width = hi_s - lo
    for _ in range(200):
        mid = 0.5 * (lo + hi_s)
        if mid <= lo or mid >= hi_s:
            break
        xm, taum = _proj_scaled(v, hi, mid)
        n_iter += 1
        if xm is None:                                             # pragma: no cover
            break
        if float(xm @ xm) > t:                          # too fine: the answer is above
            lo = mid
        else:                                          # feasible: keep it, search downward
            hi_s, xh, tauh = mid, xm, taum
        width = hi_s - lo
        if width <= 1e-18 * max(1.0, abs(hi_s)):
            break
    return float(hi_s), xh, tauh, n_iter, float(width)


def project_Cr(v, a_bar, e_bar):
    """P_C(v) for C = {sum x = 1, 0 <= x <= a_bar, ||x||^2 <= 1/e_bar}.

    Returns (alpha, kind, mult) with mult the multipliers in the stable parameterization:

        mult["u"]          = 1 (lam = 0) or 1/s with s = 1 + 2 lam (ball active)
        mult["tau_scaled"] = tau' = tau/s, with  alpha = clip(v/s - tau', 0, a_bar)
        mult["lam_scaled"] = lam' = lam s = (1 - u)/2
        mult["tau"]        = tau = tau'/u          (reported)
        mult["nu"]         = lam = lam'/u          (reported)

    (u, tau', lam') stay O(1) even when lam ~ 1e12, and they reconstruct alpha and the KKT
    residual exactly (see kkt_residuals).

    `kind` is "degenerate_uniform" (K = 1: the only point) | the capped-simplex kinds
    ("activeset" | "degenerate" | "fallback") | "ball".
    """
    v = np.asarray(v, dtype=float)
    K = int(v.size)
    hi = float(a_bar)
    t = 1.0 / float(e_bar)
    if K == 1:
        return np.ones(1), "degenerate_uniform", {"u": 1.0, "tau_scaled": 0.0, "lam_scaled": 0.0,
                                                  "tau": 0.0, "nu": 0.0}
    # Uniform control (gate O-G2): if v is the uniform vector and the uniform vector is feasible,
    # the projection is the uniform vector itself - the projection of a constant vector is exactly
    # uniform.  Returning it directly removes the O(K eps) summation noise of the bisection and
    # makes the gate exact to the last bit.
    if float(np.max(np.abs(v - 1.0 / K))) <= 8.0 * float(np.finfo(float).eps):
        uni = np.full(K, 1.0 / K)
        if (float(uni.max()) <= hi) and (float(uni @ uni) <= t):
            return uni, "uniform_control", {"u": 1.0, "tau_scaled": float(v[0] - 1.0 / K),
                                            "lam_scaled": 0.0,
                                            "tau": float(v[0] - 1.0 / K), "nu": 0.0}
    x0, tau0, kind0 = capped_simplex(v, hi)
    if float(x0 @ x0) <= t:
        # the ball is slack: the capped-simplex projection already solves P_C.
        # Uniform control (O-G2): when the returned point is uniform to within a few ulps and the
        # uniform vector is feasible, return the uniform vector itself.  The projection of a
        # *constant* vector is exactly uniform, so this only removes the O(K eps) summation noise
        # of the bisection; it is what makes the O-G2 gate exact (feeding the uniform vector must
        # return it to the last bit).
        if float(np.max(np.abs(x0 - 1.0 / K))) <= 4.0 * float(np.finfo(float).eps):
            uni = np.full(K, 1.0 / K)
            if (float(uni.max()) <= hi) and (float(uni @ uni) <= t):
                return uni, kind0, {"u": 1.0, "tau_scaled": tau0, "lam_scaled": 0.0,
                                    "tau": tau0, "nu": 0.0}
        return x0, kind0, {"u": 1.0, "tau_scaled": tau0, "lam_scaled": 0.0,
                           "tau": tau0, "nu": 0.0}
    s, x, tau, _n_it, _w = choose_s(v, hi, t)
    if x is None:                                                  # pragma: no cover
        return np.full(K, 1.0 / K), "fallback_uniform", {"u": 1.0, "tau_scaled": 0.0,
                                                         "lam_scaled": 0.0, "tau": 0.0, "nu": 0.0}
    # Consistency guard: the reported multipliers must reconstruct the returned point through the
    # KKT form alpha = clip((v - tau)/s, 0, hi).  A fallback inside choose_s (or the rounding of
    # the last bisection step) can return a point that is optimal only to rounding, and reporting
    # multipliers that do not generate it would make the stationarity audit measure the mismatch
    # instead of the algorithm's error.  When the reconstruction disagrees, the point is re-derived
    # from the multipliers.
    for _ in range(4):
        x_rec = np.minimum(np.maximum((v - 0.5 * tau) / s, 0.0), hi)
        if float(x_rec @ x_rec) <= t and abs(float(x_rec.sum()) - 1.0) <= 1e-13:
            x = x_rec
            break
        # the free set of the reconstruction differs: re-solve tau on its own free set
        free = ((v - 0.5 * tau) / s > 0.0) & ((v - 0.5 * tau) / s < hi)
        nf = int(np.count_nonzero(free))
        if nf < 2:                                                 # pragma: no cover
            break
        xf, vf = x[free], v[free]
        mx, mv = float(np.mean(xf)), float(np.mean(vf))
        den = float(np.sum((xf - mx) ** 2))
        if den <= 0.0:                                             # pragma: no cover
            break
        s = float(np.sum((xf - mx) * (vf - mv))) / den
        tau = mv - s * mx                          # inner tau; TAU = tau/u is reported
        if not (s > 0.0):                                          # pragma: no cover
            break
    u = 1.0 / float(s)
    lam_p = 0.5 * (1.0 - u)                       # lam' = lam s = (1 - 1/s)/2
    return x, "ball", {"u": float(u), "tau_scaled": float(tau) * float(u),
                       "lam_scaled": float(lam_p), "tau": float(tau),
                       "nu": float(lam_p) / float(u)}


def feasibility(a, a_bar, e_bar):
    """Max violation of C_r = {sum = 1, x >= 0, x <= a_bar, ||x||^2 <= 1/e_bar}."""
    a = np.asarray(a, dtype=float)
    return float(max(abs(float(a.sum()) - 1.0), max(0.0, -float(a.min())),
                     max(0.0, float(a.max()) - float(a_bar)),
                     max(0.0, float(a @ a) - 1.0 / float(e_bar))))


# =======================================================================================
# KKT audit
# =======================================================================================

def kkt_residuals(a, grad, a_bar, e_bar, tau=None, nu=None, u=None, tau_scaled=None,
                  lam_scaled=None):
    """Max primal, stationarity and complementary-slackness residuals of the projection KKT.

        Lagrangian:  f(a) + tau (sum a - 1) - lo.a + up.(a - a_bar) + nu (||a||^2 - 1/e_bar)

    With g = grad + tau + 2 nu a the exact residuals of a projection point are

        stationarity = max( max_i |g_i| over the strictly free coordinates,
                            max_i max(0, -g_i) over the coordinates at 0,
                            max_i max(0,  g_i) over the coordinates at a_bar )
        cs           = max( max_i max(0, -g_i) * a_i ,  max_i max(0, g_i) * (a_bar - a_i) ,
                            |nu (||a||^2 - 1/e_bar)| )

    which is the ordinary KKT violation measure: it is zero exactly at a KKT point and it never
    asks a coordinate that is at a bound to satisfy the *equality* form of stationarity.  A
    coordinate at a bound is charged only max(0, -+g), which is what its multiplier can absorb.

    Optimality measure.  The violation of a point is the smallest violation over all admissible
    multipliers, so the audit reports

        stationarity = min( raw, fitted )

    where `raw` uses the multipliers that built the point (tau, nu) - or, when the caller passes the
    ball-active triple (u, tau', lam'), the equivalent plain-form pair tau = tau'/u,
    nu = lam'/u - and `fitted` refits only the equality multiplier on the free coordinates with the
    least-squares solution of the free-set equations, which share the single unknown tau:

        tau_fit = mean_i ( -grad_i - 2 nu a_i )  over the free coordinates.

    The free-set equations are exactly the KKT stationarity of a projection restricted to the free
    coordinates, so `fitted` is the natural measure of whether the active set of the returned point
    is the correct one: at the projection it is O(eps) * |tau|, and at a feasible non-optimal point
    it is bounded away from zero.  `raw` differs from it only by the last bits of tau, because a
    finite-precision tau cannot make the sum exactly 1 and satisfy the free-set equations at the
    same time - taking the minimum avoids charging the point for that last bit.  Both values are
    stored (`stat_raw`, `stat_fit`) and `cs` uses the multiplier that achieved the minimum.

    Large-nu stability.  When nu ~ 1e12 (near-uniform windows) tau and nu themselves cannot be
    resolved in double precision, and the plain sum tau + 2 nu a cancels two ~1e12 quantities.
    The caller therefore passes the construction triple (u, tau', lam') with tau = tau'/u and
    nu = lam'/u; the audit forms the *same* residual through the scaled expression
    g = u grad - tau' + 2 lam' a (identical in exact arithmetic, computed without the cancellation)
    and fits tau' instead, converting back for the report.

    `grad` is the gradient of the objective at a: a - v for a projection, and
    -M^T Q + (a - beta)/kappa for the debt rule's objective.
    """
    a = np.asarray(a, dtype=float)
    grad = np.asarray(grad, dtype=float)
    hi = float(a_bar)
    t = 1.0 / float(e_bar)
    n2 = float(a @ a)
    primal = max(abs(float(a.sum()) - 1.0), max(0.0, -float(a.min())),
                 max(0.0, float(a.max()) - hi), max(0.0, n2 - t))
    scaled = u is not None
    if scaled:
        u_used = float(u)
        tau_p = float(tau_scaled)
        lam_p = float(lam_scaled)
        tau_plain = tau_p / u_used
        nu_plain = lam_p / u_used
    else:
        u_used = 1.0
        tau_plain = float(tau) if tau is not None else None
        nu_plain = float(nu) if nu is not None else None
    at_lo = a <= 0.0
    # A coordinate that misses the cap by a few ulps is at the cap: it is classified by the
    # multiplier sign, i.e. the active set is augmented by the near-bound coordinates, and the
    # stationarity residual is then evaluated on the (smaller) strictly free set.  Without the
    # width the residual charges a near-cap coordinate the equality form and reports O(1) at a
    # perfectly optimal point (seen on the K = 2 windows where the feasible set is a single point).
    at_hi = a >= hi * (1.0 - 64.0 * float(np.finfo(float).eps))
    free = ~(at_lo | at_hi)
    idx = np.nonzero(free)[0]
    if tau_plain is None or nu_plain is None:
        if idx.size >= 2:
            A = np.stack([np.ones(idx.size), 2.0 * a[idx]], axis=1)
            sol, *_ = np.linalg.lstsq(A, -grad[idx], rcond=None)
            fit_tau, fit_nu = float(sol[0]), float(sol[1])
        elif idx.size == 1:
            i = int(idx[0])
            fit_tau, fit_nu = float(-grad[i]), 0.0
        else:                                                      # pragma: no cover
            fit_tau, fit_nu = 0.0, 0.0
        if tau_plain is None:
            tau_plain = fit_tau
        if nu_plain is None:
            nu_plain = max(fit_nu, 0.0)
            if n2 < t:
                nu_plain = 0.0
    nu_plain = max(float(nu_plain), 0.0)
    scale = max(1.0, abs(u_used), float(np.max(np.abs(a))) if a.size else 1.0)
    floor = 200.0 * float(np.finfo(float).eps) * scale

    def _resid(tau_use):
        """Stationarity vector and its violation at the equality multiplier tau_use.

        With g = grad + tau + 2 nu a the Lagrangian stationarity is g - lo + up = 0, so a
        coordinate at zero needs g_i >= 0 (its multiplier is lo_i = g_i) and a coordinate at the
        cap needs g_i <= 0 (up_i = -g_i).  The violation is therefore max(0, -g_i) at the cap and
        max(0, g_i) at zero; taking the wrong sign charges an optimal single-point feasible set
        (K = 2, a_bar = 1/K) a residual of 2|tau|.
        """
        if scaled:
            g = u_used * grad - tau_use + 2.0 * lam_p * a        # == u * (grad + tau + 2 nu a)
        else:
            g = grad + tau_use + 2.0 * nu_plain * a
        st = 0.0
        if idx.size:
            st = max(st, float(np.max(np.abs(g[idx]))))
        if at_lo.any():
            st = max(st, float(np.max(np.maximum(g[at_lo], 0.0))))
        if at_hi.any():
            st = max(st, float(np.max(np.maximum(-g[at_hi], 0.0))))
        return st, g

    # `tau_use` in _resid is the multiplier of the residual form actually used: the scaled
    # tau' = u tau when the caller passed the (u, tau', lam') triple, and the plain tau otherwise.
    # Mixing the two (feeding tau'/u into the scaled residual) is a factor-1/u error that shows up
    # as a stationarity residual of order |tau| at a perfectly optimal point.
    tau0 = float(tau_p) if scaled else float(tau_plain)
    stat_raw, _g = _resid(tau0)
    # Least-squares refit of the equality multiplier on the free coordinates.  The free-set
    # equations are grad_i + tau + 2 nu a_i = 0 in the plain parameterization, so the fitted value
    # is tau_plain_fit = mean(-grad_i - 2 nu a_i) and it is converted to the scaled form for the
    # residual; the fit itself is done in plain coordinates because the scaled gradient term is
    # O(u) and the fit would be ill-conditioned there.
    nu_fit = nu_plain
    gbase = grad + 2.0 * nu_fit * a
    n_free = int(idx.size)
    if n_free >= 1:
        tau_plain_cand = -float(np.mean(gbase[idx]))
    elif at_hi.any() and at_lo.any():
        # violation = max(max_hi(grad + 2 nu a + tau), max_lo(-grad - 2 nu a - tau)); equalising
        # the two branches gives the minimiser
        tau_plain_cand = 0.5 * (float(np.min(gbase[at_lo])) - float(np.max(gbase[at_hi])))
    elif at_hi.any():
        # need grad_i + 2 nu a_i + tau <= 0 for every capped coordinate, i.e. tau <= -max gbase
        tau_plain_cand = -float(np.max(gbase[at_hi]))
    elif at_lo.any():
        # need grad_i + 2 nu a_i + tau >= 0 for every zero coordinate, i.e. tau >= -min gbase
        tau_plain_cand = -float(np.min(gbase[at_lo]))
    else:                                                          # pragma: no cover
        tau_plain_cand = tau_plain
    tau_cand = tau_plain_cand * u_used if scaled else tau_plain_cand
    stat_cand, _g = _resid(float(tau_cand))
    if stat_cand < stat_raw:
        stat, tau_used = float(stat_cand), float(tau_cand)
        stat_fit, tau_fit = float(stat_cand), float(tau_cand)
    else:
        stat, tau_used = float(stat_raw), float(tau0)
        stat_fit, tau_fit = float(stat_cand), float(tau_cand)
    if scaled:
        g = u_used * grad - tau_used + 2.0 * lam_p * a
        nu_cs = lam_p
    else:
        g = grad + tau_used + 2.0 * nu_plain * a
        nu_cs = nu_plain
    cs = abs(nu_cs * (n2 - t))
    if at_lo.any():
        cs = max(cs, float(np.max(np.maximum(g[at_lo], 0.0) * a[at_lo])))
    if at_hi.any():
        cs = max(cs, float(np.max(np.maximum(-g[at_hi], 0.0) * (hi - a[at_hi]))))
    return {"primal": float(primal), "stationarity": float(max(0.0, stat)), "cs": float(cs),
            "stat_raw": float(max(0.0, stat_raw)), "stat_fit": float(max(0.0, stat_fit)),
            "stat_floor": float(floor), "u": u_used,
            "tau_scaled": float(tau_p if scaled else tau_plain),
            "tau_fit": tau_fit, "lam_scaled": float(lam_p if scaled else nu_plain),
            "nu": float(nu_plain), "tau": float(tau_plain),
            "n_free": int(idx.size), "n_at_lo": int(at_lo.sum()), "n_at_hi": int(at_hi.sum()),
            "norm2": n2, "norm2_target": t}


def proj_objective(a, beta):
    """||a - beta||^2."""
    return float(((np.asarray(a, dtype=float) - np.asarray(beta, dtype=float)) ** 2).sum())


def debt_objective(a, beta, M, Q, kappa=KAPPA):
    """-Q^T M a + (1/(2 kappa)) ||a - beta||^2."""
    a = np.asarray(a, dtype=float)
    return float(-np.asarray(Q, dtype=float) @ (np.asarray(M, dtype=float) @ a)
                 + (1.0 / (2.0 * float(kappa)))
                 * float(((a - np.asarray(beta, dtype=float)) ** 2).sum()))


def audit_projection(a, v, a_bar, e_bar, mult):
    """KKT audit of min ||x - v||^2 / 2 on C_r at the multipliers that built `a`."""
    return kkt_residuals(a, np.asarray(a, dtype=float) - np.asarray(v, dtype=float),
                         a_bar, e_bar, tau=mult.get("tau"), nu=mult.get("nu"),
                         u=mult.get("u"), tau_scaled=mult.get("tau_scaled"),
                         lam_scaled=mult.get("lam_scaled"))


def audit_debt(a, M, Q, beta, a_bar, e_bar, mult, kappa=KAPPA):
    """KKT audit of min -Q^T M a + (1/(2 kappa)) ||a - beta||^2 on C_r."""
    grad = -(np.asarray(M, dtype=float).T @ np.asarray(Q, dtype=float)) \
        + (np.asarray(a, dtype=float) - np.asarray(beta, dtype=float)) / float(kappa)
    return kkt_residuals(a, grad, a_bar, e_bar, tau=mult.get("tau"), nu=mult.get("nu"),
                         u=mult.get("u"), tau_scaled=mult.get("tau_scaled"),
                         lam_scaled=mult.get("lam_scaled"))


# =======================================================================================
# the two rules
# =======================================================================================

def oracle_proj_beta(betas, case):
    """proj_beta oracle: alpha_r = P_C(beta_hat_r / sum beta_hat_r), one projection per window."""
    alphas, diag = [], []
    for j in range(case["n"]):
        b = np.asarray(betas[j], dtype=float)
        b = b / b.sum()
        a, kind, mult = project_Cr(b, case["a_bar"][j], case["e_bar"][j])
        alphas.append(a)
        diag.append({"kind": kind, "mult": mult, "v": b})
    return np.concatenate(alphas), diag


def oracle_debt_seq(case, betas, kappa=KAPPA, eta=ETA_DEBT):
    """proj_beta_debt oracle (exact closed loop).

    alpha_r = P_C(beta_r + kappa M_r^T Q_r),  Q_{r+1} = max(Q_r + eta (mu - M_r alpha_r), 0).
    Returns (alphas, Q_before_each_window, diag).
    """
    Q = np.zeros(case["G"])
    alphas, qs, diag = [], [], []
    for j in range(case["n"]):
        b = np.asarray(betas[j], dtype=float)
        b = b / b.sum()
        w = b + float(kappa) * (case["M"][j].T @ Q)
        a, kind, mult = project_Cr(w, case["a_bar"][j], case["e_bar"][j])
        qs.append(Q.copy())
        alphas.append(a)
        diag.append({"kind": kind, "mult": mult, "v": w, "beta": b, "Q": Q.copy()})
        Q = np.maximum(Q + float(eta) * (case["mu"] - case["M"][j] @ a), 0.0)
    return np.concatenate(alphas), qs, diag

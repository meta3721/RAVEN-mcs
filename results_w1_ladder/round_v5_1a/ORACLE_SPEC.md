# ORACLE_SPEC — W1 round v5.1a, the A1′ projection oracle (AM-6)

```text
File:   scripts/w1_v51a_oracle.py      (numpy only - no CVXPY, no scipy)
Round:  results_w1_ladder/round_v5_1a/
Status: supersedes scripts/w1_v51_oracle.py, which is kept untouched as the record of the
        superseded run.
```

## 1 The problem

```text
    P_C(v) = argmin { ||x - v||^2 :  sum x = 1,  0 <= x <= a_bar,  ||x||^2 <= 1/e_bar }
```

with `a_bar = min(1, max(0.5, 1/K))` and `e_bar = min(3, K)` on the paper's datasets.  `C_r` is
convex (the ball is a sublevel set of a convex quadratic) and the objective is strictly convex, so
the minimiser is unique.  The oracle must return the minimiser, not merely a feasible point: the
v5.1 implementation returned points whose objective was up to **+1.11e-06 worse** than a feasible
comparator, which is impossible for an exact projection and proved that implementation suboptimal.

## 2 The algorithm

### 2.1 Two-multiplier dual

KKT for `P_C` with multipliers `(TAU, LAM)`, `LAM >= 0`:

```text
    x = clip((v - TAU) / (1 + 2 LAM), 0, a_bar),      sum x = 1,   LAM (||x||^2 - 1/e_bar) = 0.
```

* **`LAM = 0` branch.** `x = clip(v - TAU, 0, a_bar)` with `TAU` chosen so that `sum x = 1`: the
  capped-simplex projection of `v`.  It solves `P_C` whenever `||x||^2 <= 1/e_bar`.
* **`LAM > 0` branch.** With `s = 1 + 2 LAM > 1`,

  ```text
      x = clip((v - TAU)/s, 0, a_bar) = clip(v/s - TAU/s, 0, a_bar),
  ```

  the capped-simplex projection of the *scaled* vector `v/s` onto the cap `a_bar`.  The inner
  multiplier is `tau = TAU/s`; the reported pair is `TAU = s tau`, `LAM = (s-1)/2`.  The outer
  scalar equation `||x(s)||^2 = 1/e_bar` is solved by bisection on `s`, the inner one by bisection
  on `tau` at every step.

Both scalar maps are continuous and monotone in the direction used, so bisection is exact and
unconditional:

| map | direction | bracket | why it is well posed everywhere |
|---|---|---|---|
| `tau -> sum clip((v - TAU)/s, 0, a_bar)` | non-increasing | `[min(v) - s*a_bar, max(v)]` | reaches `K*a_bar >= 1` at the left end and `0` at the right end |
| `s -> ||clip((v - TAU)/s, 0, a_bar)||^2` | non-increasing | `[1, s_max]` found by doubling | the free part scales like `1/s`, the capped part stays at `a_bar`, and the free set only shrinks |

The inner solve returns the **left limit** of the root: the largest `tau` with `sum >= 1`.  That is
what keeps the coordinates that are at the cap exactly at the cap, so the affine form
`x = clip((v - TAU)/s, 0, a_bar)` holds bit-exactly and the KKT residual is machine zero rather
than a fraction of `|TAU|`.

### 2.2 Capped-simplex sub-problem

`capped_simplex(v, hi)` enumerates the active sets.  A point of the form `clip(v - tau, 0, hi)`
partitions the coordinates into capped (`v_i - tau >= hi`), free (`0 < v_i - tau < hi`) and zero
(`v_i - tau <= 0`); the capped set is the largest `v`, and for a fixed number `m` of capped
coordinates the root of `sum x = 1` is bracketed and bisected, since the sum is continuous and
non-increasing on that piece.  The pieces are compared by the objective and the smallest wins.

The closed form `tau(m) = (sum of the K-m smallest + m*hi - 1)/(K-m)` is deliberately **not** used:
it assumes the free set is the `K-m` smallest coordinates, which fails as soon as a coordinate
strictly between two others drops below the root and belongs to the zero set.  That assumption is
what made an earlier revision of this file return feasible but non-optimal points; the current
routine reproduces the exact optimum on an exhaustive active-set enumeration and on a dense 2-D
`(lam, tau)` scan (`ORACLE_EVIDENCE.json`).

### 2.3 Degenerate cases

* `K = 1`: the only point is `x = 1`.
* `sum(v) < 1`: no point of `{sum x = 1, x <= hi}` exists at all (subtracting `tau` and clipping
  can only lower the sum), so the projection is undefined; the routine returns the minimal-norm
  point of the box, `1/K`, and labels it `infeasible`.  This case does not arise for the paper's
  `beta_hat` vectors, which are normalised to sum 1.
* `a_bar = 1/K`: the cap alone forces `x = 1/K`; the routine returns it with the label
  `degenerate`.
* near-uniform windows (`LAM ~ 1e12`): the multipliers themselves are not representable to better
  than ~`1e-4`, so the oracle reports the scale-stable triple
  `(u, tau' , lam') = (1/s, tau/s, LAM/s)`; the point is unchanged and is exact to machine
  precision, and the KKT residual is evaluated in the scaled form
  `g = u*grad - tau' + 2*lam'*a`, which is free of the `TAU + 2 LAM a` cancellation that loses 16
  digits in that regime.

## 3 The two rules

```text
    proj_beta       alpha_r = P_C(beta_hat_r / sum beta_hat_r)
    proj_beta_debt  alpha_r = P_C(beta_hat_r / sum beta_hat_r + kappa M_r^T Q_r),
                    Q_{r+1} = max(Q_r + eta (mu - M_r alpha_r), 0),  Q_0 = 0,
                    kappa = 1000,  eta = 0.01
```

The debt rule is algebraically the same projection: with `w = beta + kappa M^T Q`,

```text
    -Q^T M a + (1/(2 kappa)) ||a - beta||^2  =  (1/(2 kappa)) ||a - w||^2  +  const(a-independent)
```

so its minimiser on `C_r` is exactly `P_C(w)`.  The identity is verified numerically in
`O_GATES_RERUN.json["self_check_debt_algebra"]` (identity residual ~1e-17) together with a
perturbation check that no feasible point beats the oracle point.

## 4 The audit

`kkt_residuals(a, grad, a_bar, e_bar, ...)` measures, at the multipliers that built the point,

```text
    g_i            = grad_i + TAU + 2 LAM a_i
    primal         = max(|sum a - 1|, max(0, -min a), max(0, max a - a_bar),
                         max(0, ||a||^2 - 1/e_bar))
    stationarity   = max( max_free |g_i|,  max_zero max(0, g_i),  max_cap max(0, -g_i) )
    cs             = max( |LAM (||a||^2 - 1/e_bar)|,
                          max_zero max(0, g_i) a_i,   max_cap max(0, -g_i) (a_bar - a_i) )
```

with the sign conventions of the Lagrangian
`L = f(a) + TAU (sum a - 1) - lo.a + up.(a - a_bar) + LAM (||a||^2 - 1/e_bar)`: a coordinate at
zero needs `g_i >= 0`, one at the cap needs `g_i <= 0`, and a free one needs `g_i = 0`.  A
coordinate that misses the cap by a few ulps is classified as at the cap (the width is
`64 eps a_bar`).

The audit also refits the equality multiplier on the free coordinates
(`TAU_fit = mean(-grad_i - 2 LAM a_i)`) and reports `stationarity = min(raw, fitted)` together with
both components (`stat_raw`, `stat_fit`).  The fit is formed strictly inside the parameterization
that the residual uses; mixing them (feeding `tau'/u` into the scaled residual) is a factor `1/u`
error that shows up as a residual of order `|TAU|` at a perfectly optimal point.  For the paper's
windows the two agree to within a few times `1e-9`, i.e. the returned points satisfy the KKT
system on their own free sets.

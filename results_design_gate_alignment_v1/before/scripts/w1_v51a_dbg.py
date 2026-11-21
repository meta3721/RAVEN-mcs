"""Dump the failing v5.1a oracle windows (development diagnostic; writes nothing)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import w1_replay as W                                                          # noqa: E402
import w1_v51a_oracle as O                                                     # noqa: E402

np.set_printoptions(precision=18, suppress=False, linewidth=250)
TRAIN = ROOT / "results_w1_ladder/round_v4/train/v4/C0_frozen"


def dump_capped(v, hi):
    K = v.size
    order = np.argsort(-v, kind="stable")
    vs = v[order]
    tail = np.concatenate([np.cumsum(np.minimum(vs[::-1], hi))[::-1], np.zeros(1)])
    S = np.arange(K, dtype=float) * hi + tail[:K]
    print("  sorted:", vs)
    print("  S     :", S)
    for m in range(K):
        n = K - m
        tau_m = (float(S[m]) - 1.0) / float(n)
        xm = np.minimum(np.maximum(v - tau_m, 0.0), hi)
        ncap = int(np.count_nonzero(v - tau_m >= hi))
        print("    m=%d tau=%.17g sum=%.17g ncap=%d nfree=%d S=%.17g"
              % (m, tau_m, float(xm.sum()), ncap,
                 int(np.count_nonzero((v - tau_m > 0) & (v - tau_m < hi))), float(S[m])))


def show(ds, arm, seed, wanted):
    case = W.build_case(ds, "R_on", "raven_wo_use", seed, W.pi_tar_for(ds))
    wm = W.load_json(TRAIN / ds / arm / ("seed%d" % seed) / "window_metrics.json")
    by = {int(w["window_id"]): w for w in W.active_windows(wm)}
    betas = [np.asarray(by[int(case["wids"][j])]["beta_hat"], dtype=float)
             for j in range(case["n"])]
    if arm == "proj_beta":
        a_or, diag = O.oracle_proj_beta(betas, case)
        qs = [None] * case["n"]
    else:
        a_or, qs, diag = O.oracle_debt_seq(case, betas)
    off = 0
    for j in range(case["n"]):
        K = len(case["clients"][j])
        a = a_or[off:off + K]
        off += K
        if j != wanted:
            continue
        d = diag[j]
        ab, eb = case["a_bar"][j], case["e_bar"][j]
        print("=== %s %s seed%d window %d K=%d a_bar=%r e_bar=%r" % (ds, arm, seed, j, K, ab, eb))
        print("v      :", d["v"])
        print("alpha  :", a)
        print("sum    : %.20g   norm2 %.20g  target %.20g" % (float(a.sum()), float(a @ a), 1.0 / eb))
        print("kind   :", d["kind"], "mult", d["mult"])
        if d["kind"] == "ball":
            s, x, taus, nit, w = O.choose_s(d["v"], ab, 1.0 / eb)
            print("choose_s: s=%.20g  tau_scaled=%.20g  lam=%.20g  iters=%d width=%.3g"
                  % (s, taus, 0.5 * (s - 1.0), nit, w))
            print("  x from choose_s == alpha:", bool(np.array_equal(x, a)))
        res = O.audit_projection(a, d["v"], ab, eb, d["mult"])
        print("kkt    : primal %.3e stat %.3e (raw %.3e fit %.3e) cs %.3e free %d lo %d hi %d"
              % (res["primal"], res["stationarity"], res["stat_raw"], res["stat_fit"], res["cs"],
                 res["n_free"], res["n_at_lo"], res["n_at_hi"]))
        print("         tau_scaled %.17g  tau_fit %.17g  u %.3g  lam_s %.3g"
              % (res["tau_scaled"], res["tau_fit"], res["u"], res["lam_scaled"]))
        if d["kind"] == "ball":
            print("         ball: norm2 %.17g target %.17g" % (res["norm2"], res["norm2_target"]))


if __name__ == "__main__":
    import numpy as _np
    v = _np.array([0.8122577371658936, 0.13387075773696588, 0.053871505097140594])
    for u in (1.0, 0.8, 2.0 / 3.0, 0.5, 0.3, 0.1):
        x, tp, k = O.capped_simplex(u * v, u * 0.5)
        print("u=%.6f sum=%.6f norm2=%.6f tau'=%.6f kind=%s x=%s"
              % (u, float(x.sum()), float(x @ x), tp, k, _np.array2string(x, precision=6)))
    a, kind, mult = O.project_Cr(v, 0.5, 3.0)
    print("proj", kind, mult, a, "sum", float(a.sum()), "norm2", float(a @ a))
    res = O.audit_projection(a, v, 0.5, 3.0, mult)
    print({k: res[k] for k in ("primal", "stationarity", "stat_raw", "stat_fit", "cs")})

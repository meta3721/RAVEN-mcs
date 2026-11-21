"""F-1 final readout.

Arms
  N  artifacts/e3_f1_score_dependent_r1   published traces (theta_O = 0)
  S  artifacts/e3_f1_theta1_r1            F-1-O traces (theta_O = 1.0)
Published reference: artifacts/e3_formal_runs_r1

Pre-registered rules (design doc section 5):
  E1 (primary)  Delta_oracle = RMSE_mu(raven) - RMSE_mu(raven_oracle_p) on the S trace, paired.
                |Delta| <= 0.5%  -> H-A refuted (an exact propensity buys nothing even when the
                                    selection law is within-stratum and label-correlated)
                Delta  >  0.5%  -> H-A supported (the harder regime created recoverable error)
  E2 (secondary) change in RAVEN's lead over uncorrected baselines between the N and S traces.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(".")
PUB = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs"
ARMS = {
    "N": ROOT / "artifacts" / "e3_f1_score_dependent_r1" / "runs",
    "S": ROOT / "artifacts" / "e3_f1_theta1_r1" / "runs",
}
DATASETS = ["sensorscope", "uair"]
BASELINES = ["twostage_hajek", "fedavg_window"]
ENDPOINTS = ["RMSE_mu", "Delta_group", "Tail_RMSE"]
Z = 1.959964 + 0.841621


def load(base: Path, ds: str, method: str) -> dict[str, dict]:
    out = {}
    d = base / ds / method
    if not d.is_dir():
        return out
    for seed in sorted(d.glob("seed*")):
        f = seed / "final_metrics.json"
        if f.is_file():
            out[seed.name] = json.loads(f.read_text(encoding="utf-8"))
    return out


def pair(a: dict, b: dict, ep: str):
    seeds = sorted(set(a) & set(b))
    rows = [(a[s][ep], b[s][ep]) for s in seeds
            if a[s].get(ep) is not None and b[s].get(ep) is not None]
    if len(rows) < 2:
        return None
    return (np.array([r[0] for r in rows], float), np.array([r[1] for r in rows], float))


def stats(x: np.ndarray, y: np.ndarray):
    d = x - y
    n = len(d)
    sd = float(d.std(ddof=1))
    se = sd / np.sqrt(n)
    return dict(n=n, a=float(x.mean()), b=float(y.mean()), mean=float(d.mean()),
                pct=100.0 * float(d.mean()) / float(x.mean()),
                sd=sd, mde=Z * se, mde_pct=100.0 * Z * se / float(x.mean()),
                sig=abs(float(d.mean())) / se if se > 0 else float("inf"))


def show(tag: str, s: dict) -> None:
    print(f"{tag:<44}{s['n']:>3}{s['a']:>11.4f}{s['b']:>11.4f}"
          f"{s['pct']:>9.3f}{s['sd']:>9.4f}{s['mde_pct']:>8.3f}{s['sig']:>7.2f}")


def main() -> int:
    print("=" * 96)
    print("GATE 1 - harness reproduction: arm N 'raven' vs the published 'raven'")
    print("=" * 96)
    print(f"{'comparison':<44}{'n':>3}{'arm N':>11}{'published':>11}{'delta%':>9}")
    for ds in DATASETS:
        r = pair(load(ARMS["N"], ds, "raven"), load(PUB, ds, "raven"), "RMSE_mu")
        if r is None:
            print(f"{ds + ' raven vs published':<44}  no data")
            continue
        x, y = r
        print(f"{ds + ' raven vs published':<44}{len(x):>3}{x.mean():>11.6f}{y.mean():>11.6f}"
              f"{100*(x.mean()-y.mean())/y.mean():>9.4f}")

    for arm in ("N", "S"):
        base = ARMS[arm]
        have = {}
        for ds in DATASETS:
            for m in ["raven", "raven_oracle_p"] + BASELINES:
                have[(ds, m)] = len(load(base, ds, m))
        print(f"\narm {arm}: cells available "
              + ", ".join(f"{ds}/{m}={have[(ds, m)]}" for ds, m in have if have[(ds, m)]))
        if not any(have.values()):
            continue

        print("\n" + "=" * 96)
        print(f"E1 [{arm}] - exact observation propensity vs the plug-in model (paired, same trace)")
        print("=" * 96)
        print(f"{'contrast':<44}{'n':>3}{'plugin':>11}{'oracle p':>11}"
              f"{'delta%':>9}{'sd':>9}{'MDE%':>8}{'sig':>7}")
        for ds in DATASETS:
            plugin = load(base, ds, "raven")
            oracle = load(base, ds, "raven_oracle_p")
            for ep in ENDPOINTS:
                r = pair(plugin, oracle, ep)
                if r is None:
                    continue
                show(f"{ds} {ep}  raven - oracle_p", stats(*r))

        if arm == "S":
            print("\n" + "=" * 96)
            print("E2 - did RAVEN's lead over uncorrected baselines move between N and S?")
            print("=" * 96)
            print(f"{'contrast':<44}{'n':>3}{'arm N':>11}{'arm S':>11}"
                  f"{'change':>9}{'sd':>9}{'MDE%':>8}{'sig':>7}")
            for ds in DATASETS:
                for bl in BASELINES:
                    rn = pair(load(ARMS["N"], ds, "raven"), load(ARMS["N"], ds, bl), "RMSE_mu")
                    rs = pair(load(ARMS["S"], ds, "raven"), load(ARMS["S"], ds, bl), "RMSE_mu")
                    if rn is None or rs is None:
                        continue
                    gn = rn[0] - rn[1]
                    gs = rs[0] - rs[1]
                    n = min(len(gn), len(gs))
                    gn, gs = gn[:n], gs[:n]
                    d = gs - gn
                    sd = float(d.std(ddof=1))
                    se = sd / np.sqrt(n)
                    print(f"{ds + ' raven - ' + bl:<44}{n:>3}{100*gn.mean()/rn[1].mean():>11.3f}"
                          f"{100*gs.mean()/rs[1].mean():>11.3f}"
                          f"{100*d.mean()/rs[1].mean():>9.3f}{sd:>9.4f}"
                          f"{100*Z*se/rs[1].mean():>8.3f}"
                          f"{abs(float(d.mean()))/se if se > 0 else float('inf'):>7.2f}")

    print("\n" + "=" * 96)
    print("MANIPULATION GATE (arm S): realized observation counts and clip rate")
    print("=" * 96)
    for ds in DATASETS:
        a = load(ARMS["N"], ds, "raven")
        b = load(ARMS["S"], ds, "raven")
        seeds = sorted(set(a) & set(b))
        if not seeds:
            continue
        for key in ("clip_rate_stage1", "ESS"):
            va = [a[s][key] for s in seeds if a[s].get(key) is not None]
            vb = [b[s][key] for s in seeds if b[s].get(key) is not None]
            if va and vb:
                print(f"{ds:<12}{key:<18}N mean={np.mean(va):.6f}   S mean={np.mean(vb):.6f}"
                      f"   change={100*(np.mean(vb)-np.mean(va))/abs(np.mean(va)):+.3f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

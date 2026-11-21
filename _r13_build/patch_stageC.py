import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\driver\s1p_driver.py")
txt = p.read_text(encoding="utf-8")

ANCHOR = "def cmd_gates(args) -> int:"
STAGE_C = '''# --------------------------------------------------------------------- Stage C
#
# GO-H per section 6, with amendment A3 (MDE80 evaluated at n = 5):
#   H = (RMSE_mu(fedavg) - RMSE_mu(raven_simoracle)) / RMSE_mu(fedavg), paired by seed
#   GO-H  iff  mean(H) >= 1 %  AND  bootstrap 95 % lower bound > 0.5 %  AND  MDE80 < 0.5 * mean(H)
#   AND the block is not excluded by the section-6 K_r clause: "do not upgrade SS/UA to GO if more
#   than 25 % of active windows have K_r <= 3".
STAGE_C_BOOT_DRAWS = 10000
STAGE_C_BOOT_SEED = 20261007
STAGE_C_H_BAR = 0.01
STAGE_C_H_LCB_BAR = 0.005
STAGE_C_KR_EXCLUDE = 0.25
STAGE_C_KR_GUARD_BLOCKS = ("sensorscope", "uair")


def kr_le3_share(run_dir: pathlib.Path) -> dict:
    rows = json.loads((run_dir / "window_metrics.json").read_text(encoding="utf-8"))
    act = [r for r in rows if r.get("active")]
    if not act:
        return {"n_active": 0, "share_kr_le3": None, "share_ar_le2": None}
    return {
        "n_active": len(act),
        "share_kr_le3": sum(1 for r in act if (r.get("a_r_size") or 0) <= 3) / len(act),
        "share_ar_le2": sum(1 for r in act if (r.get("a_r_size") or 0) <= 2) / len(act),
    }


def mde80_paired(sd: float, n: int) -> float:
    from scipy import stats
    return float((stats.t.ppf(0.975, n - 1) + stats.t.ppf(0.80, n - 1)) * sd / math.sqrt(n))


def stage_c(args) -> int:
    cfg = json.loads((OUT / "S1P_FROZEN_CONFIG.json").read_text(encoding="utf-8"))
    av = json.loads((OUT / "S1P_STAGE_A_VERDICT.json").read_text(encoding="utf-8"))
    grid = list(csv.DictReader((OUT / "tables" / "STAGE_A_GRID.csv").open(encoding="utf-8")))

    rows, hres = [], {}
    for block in BLOCKS:
        star = cfg["per_block"][block].get("eta_s_star")
        n3 = av["N3_prime"].get(block, {}).get("verdict")
        if star is None or n3 != "PASS":
            hres[block] = {"verdict": "not_run", "reason": f"N3'={n3}"}
            continue
        for arm in ("raven_simoracle", "raven"):
            for seed in SCREEN_SEEDS:
                try:
                    run_one(block, arm, seed, LOCAL_STEPS, "C_%s" % arm, "adam", eta_s=star)
                except Exception as exc:  # noqa: BLE001
                    rows.append({"block": block, "arm": arm, "seed": seed, "blocked": True,
                                 "error": f"{type(exc).__name__}: {exc}"[:300]})
        fed, sim, rav, kr = {}, {}, {}, None
        for r in grid:
            if r["block"] != block or float(r["eta_s"]) != float(star):
                continue
            seed = int(r["seed"])
            fed[seed] = float(r["test_RMSE_mu"])
            if kr is None and r.get("run_dir"):
                kr = kr_le3_share(ROOT / r["run_dir"])
        for arm, store in (("raven_simoracle", sim), ("raven", rav)):
            for seed in SCREEN_SEEDS:
                pth = RUNS / ("C_%s" % arm) / block / arm / ("seed%d" % seed) / "final_metrics.json"
                if pth.is_file():
                    store[seed] = json.loads(pth.read_text(encoding="utf-8")).get("RMSE_mu")
        seeds = sorted(set(fed) & set(sim))
        if len(seeds) < 3:
            hres[block] = {"verdict": "not_run", "reason": f"only {len(seeds)} paired seeds"}
            continue
        Hs = np.asarray([(fed[s] - sim[s]) / fed[s] for s in seeds], dtype=np.float64)
        rng = np.random.default_rng(STAGE_C_BOOT_SEED)
        boot = np.asarray([np.mean(rng.choice(Hs, size=len(Hs), replace=True))
                           for _ in range(STAGE_C_BOOT_DRAWS)])
        lo, hi = np.percentile(boot, [2.5, 97.5])
        sd = float(np.std(Hs, ddof=1))
        mde = mde80_paired(sd, len(Hs))
        mean_h = float(np.mean(Hs))
        cond_h = mean_h >= STAGE_C_H_BAR
        cond_lcb = float(lo) > STAGE_C_H_LCB_BAR
        cond_mde = mde < 0.5 * mean_h if mean_h > 0 else False
        guard = kr is not None and kr.get("share_kr_le3") is not None and \\
            block in STAGE_C_KR_GUARD_BLOCKS and kr["share_kr_le3"] > STAGE_C_KR_EXCLUDE
        verdict = "GO-H" if (cond_h and cond_lcb and cond_mde and not guard) else "NO-GO-H"
        hres[block] = {
            "verdict": verdict, "eta_s_star": star, "n_paired_seeds": len(seeds),
            "paired_seeds": seeds, "H_by_seed": [float(x) for x in Hs], "mean_H": mean_h,
            "boot_lo": float(lo), "boot_hi": float(hi), "paired_sd": sd, "MDE80_n5": mde,
            "cond_mean_ge_1pct": bool(cond_h), "cond_lcb_gt_0.5pct": bool(cond_lcb),
            "cond_mde_lt_half_H": bool(cond_mde),
            "kr_clause": {"applies": block in STAGE_C_KR_GUARD_BLOCKS,
                          "share_kr_le3": (kr or {}).get("share_kr_le3"),
                          "threshold": STAGE_C_KR_EXCLUDE, "excluded_from_GO": bool(guard)},
            "fedavg_test_RMSE_mu": {str(s): fed[s] for s in seeds},
            "raven_simoracle_test_RMSE_mu": {str(s): sim[s] for s in seeds},
            "raven_descriptive_test_RMSE_mu": {str(s): rav[s] for s in seeds if s in rav},
            "kr_le3_under_new_config": kr,
            "bootstrap": {"draws": STAGE_C_BOOT_DRAWS, "rng_seed": STAGE_C_BOOT_SEED,
                          "type": "percentile 95%"},
        }
        print(f"  C {block:<12} mean_H={mean_h:.6f} "
              f"CI=[{float(lo):.6f},{float(hi):.6f}] MDE80={mde:.6e} "
              f"kr_le3={(kr or {}).get('share_kr_le3')} -> {verdict}", flush=True)

    with (OUT / "tables" / "STAGE_C_H.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["block", "arm", "seed", "blocked", "error"])
        w.writeheader()
        w.writerows(rows)
    dump_json({"H": hres, "created_utc": now(),
               "amendment_A3": "MDE80 evaluated at n = 5 per section 2; n = 15 reserved for the "
                               "separately authorized confirmatory run"},
              OUT / "S1P_STAGE_C_H.json")
    return 0


'''
assert txt.count(ANCHOR) == 1, "anchor"
txt = txt.replace(ANCHOR, STAGE_C + ANCHOR)

OLD = '''    ap.add_argument("--stage", choices=("gates", "g2", "A"), default="gates")'''
NEW = '''    ap.add_argument("--stage", choices=("gates", "g2", "A", "C"), default="gates")'''
assert txt.count(OLD) == 1, "cli"
txt = txt.replace(OLD, NEW)

OLD2 = '''    if args.stage == "A":
        return stage_a(args)'''
NEW2 = '''    if args.stage == "A":
        return stage_a(args)
    if args.stage == "C":
        return stage_c(args)'''
assert txt.count(OLD2) == 1, "cli2"
txt = txt.replace(OLD2, NEW2)

p.write_text(txt, encoding="utf-8")
print("patched;", len(txt.splitlines()), "lines")

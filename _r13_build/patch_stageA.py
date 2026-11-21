import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\driver\s1p_driver.py")
txt = p.read_text(encoding="utf-8")

# ---- imports ----
OLD = "import numpy as np\n\nROOT = pathlib.Path(__file__).resolve().parents[3]"
NEW = "import numpy as np\nimport pandas as pd\n\nROOT = pathlib.Path(__file__).resolve().parents[3]"
assert txt.count(OLD) == 1, "imp"
txt = txt.replace(OLD, NEW)

# ---- Stage A machinery, inserted before cmd_gates ----
ANCHOR = "def cmd_gates(args) -> int:"
STAGE_A = '''# --------------------------------------------------------------------- Stage A
#
# PRE-REGISTERED before any grid run (recorded here and echoed into S1P_FROZEN_CONFIG.json):
#
#   1. The runner does not emit a validation metric: `run_e3_real` calls `_predict(..., split="test")`
#      only, and `window_metrics.json` rows carry just {window_id, active, active_clients, a_r_size,
#      alpha, beta_hat}.  A validation RMSE_mu is therefore computed here as READ-ONLY post-processing
#      from the saved checkpoint, reusing the repo's own `_predict` with `split="validation"`.
#   2. Validation RMSE_mu weights each validation unit by `mu_g / count_g` with `mu_g` taken from a
#      `TargetBuilder(..., split="validation")` build on the same `target_group_main` mapping that
#      `build_full_runner` uses.  The test-mu-weighted variant is recorded as a sensitivity only.
#   3. Selection uses ONLY validation means.  Nothing derived from the test split is written to any
#      file until `S1P_FROZEN_CONFIG.json` exists.  The seal is procedural, not physical: the runner
#      itself writes test metrics into each run directory as part of its own output contract, which
#      cannot be changed without editing `src/`.
#   4. Ties within 0.1 % of the best validation mean go to the smaller eta_s.
#   5. A run counts as FAILED for its eta_s if any non-finite value appears in final_metrics or the
#      checkpoint fails to load.
STAGE_A_TIE_REL = 1e-3


def _validation_mu(dataset, n_groups: int) -> np.ndarray:
    from raven_mcs.data.target import GroupMapper, RepeatableTimeOfDayMapper, TargetBuilder

    atomic = dataset.atomic_df.copy()
    if n_groups == 4:
        atomic["target_group_main"] = RepeatableTimeOfDayMapper().map(atomic)
    else:
        atomic["target_group_main"] = pd.Categorical(atomic["target_group"]).codes
    tgt = TargetBuilder(group_mapper=GroupMapper("target_group_main")).build(atomic, split="validation")
    return np.asarray([float(tgt.group_mass.get(str(g), 0.0)) for g in range(n_groups)], dtype=np.float64)


def validation_rmse_mu(block: str, dataset, ckpt: pathlib.Path, n_groups: int) -> dict:
    """Read-only validation RMSE_mu from a saved checkpoint."""
    from raven_mcs.e3.real_runner.runner import CommonNDMF_from_ckpt, _predict, _mu_weights_for_test
    from raven_mcs.metrics.accuracy import rmse_mu

    class _Shim:
        pass

    shim = _Shim()
    shim.model = CommonNDMF_from_ckpt(Path(ckpt), dataset.num_spatial)
    pred = _predict(shim, dataset, split="validation")
    out = {"n_val_units": int(len(pred["y_true"]))}
    for tag, mu in (("val_mu", _validation_mu(dataset, n_groups)), ("test_mu", None)):
        if tag == "test_mu":
            continue
        w = _mu_weights_for_test(pred, mu)
        out[f"{tag}_mass_sum"] = float(np.sum(mu))
        out[f"RMSE_mu_{tag}"] = float(rmse_mu(pred["y_pred"], pred["y_true"], w)) if len(w) else None
    return out


def movement_per_tensor(ckpt: pathlib.Path, seed: int) -> dict:
    """Relative parameter movement of the saved checkpoint against the seed-reconstructed init."""
    import torch
    from raven_mcs.models.common_ndmf import deterministic_common_ndmf

    obj = torch.load(ckpt, map_location="cpu", weights_only=False)
    theta = obj["state_dict"] if isinstance(obj, dict) and "state_dict" in obj else obj
    init = deterministic_common_ndmf(int(theta["spatial.weight"].shape[0]), seed=seed).state_dict()
    tot_d2 = tot_i2 = 0.0
    per = {}
    for k in sorted(theta):
        a = init[k].detach().cpu().double()
        b = theta[k].detach().cpu().double()
        d2 = float(((b - a) ** 2).sum())
        i2 = float((a ** 2).sum())
        per[k] = (math.sqrt(d2) / math.sqrt(i2)) if i2 > 0 else float("nan")
        tot_d2 += d2
        tot_i2 += i2
    return {
        "overall_rel_movement": math.sqrt(tot_d2) / math.sqrt(tot_i2),
        "head_0_weight_rel": per.get("head.0.weight"),
        "head_8_bias_rel": per.get("head.8.bias"),
        "spatial_weight_rel": per.get("spatial.weight"),
    }


def stage_a(args) -> int:
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset

    grid_dir = OUT / "tables"
    grid_dir.mkdir(parents=True, exist_ok=True)
    val_rows = []
    for block in BLOCKS:
        dataset = load_paper_dataset(ROOT, block)
        n_groups = int(dataset.num_groups)
        for eta_s in STAGE_A_ETA_S:
            for seed in SCREEN_SEEDS:
                tag = "A_eta%g" % eta_s
                d = run_one(block, "fedavg_window", seed, LOCAL_STEPS, tag, "adam", eta_s=eta_s)
                ck = d / "checkpoints" / "final.pt"
                row = {"block": block, "arm": "fedavg_window", "seed": seed, "eta_s": eta_s,
                       "run_dir": str(d.relative_to(ROOT)).replace("\\\\", "/")}
                try:
                    row.update(validation_rmse_mu(block, dataset, ck, n_groups))
                    row.update(movement_per_tensor(ck, seed))
                    row["ckpt_ok"] = True
                except Exception as exc:  # noqa: BLE001
                    row["ckpt_ok"] = False
                    row["error"] = repr(exc)
                hajek = json.loads((d / "final_metrics.json").read_text(encoding="utf-8"))
                row["hajek_target_risk_objective"] = hajek.get("target_risk_objective")
                row["no_h_mass_loss"] = hajek.get("Gap_mis")
                row["finite"] = all(
                    not isinstance(v, float) or math.isfinite(v) for v in hajek.values()
                )
                row["diverged"] = not (row["ckpt_ok"] and row["finite"]
                                       and row.get("RMSE_mu_val_mu") is not None
                                       and math.isfinite(row.get("RMSE_mu_val_mu") or float("nan")))
                val_rows.append(row)
                print(f"  A {block:<12} eta={eta_s:<7g} seed{seed}  "
                      f"val={row.get('RMSE_mu_val_mu')!r}  diverged={row['diverged']}")

    with (grid_dir / "STAGE_A_VALIDATION.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in val_rows for k in r}))
        w.writeheader()
        w.writerows(val_rows)

    # ---- selection on validation ONLY ----
    frozen = {"schema": "S1P_STAGE_A_SELECTION_V1", "created_utc": now(),
              "selection_rule": "per block: argmin of the mean validation RMSE_mu over the 5 screen "
                                "seeds among non-diverged levels; ties within 0.1 % go to the smaller "
                                "eta_s", "tie_rel": STAGE_A_TIE_REL,
              "validation_metric": "RMSE_mu on the validation split, weights mu_g / count_g with mu_g "
                                   "from TargetBuilder(split='validation') on target_group_main",
              "screen_seeds": SCREEN_SEEDS, "grid_eta_s": list(STAGE_A_ETA_S),
              "test_split_read": False}
    per_block = {}
    for block in BLOCKS:
        levels = {}
        for eta_s in STAGE_A_ETA_S:
            rs = [r for r in val_rows if r["block"] == block and r["eta_s"] == eta_s and not r["diverged"]]
            levels[eta_s] = {
                "n_non_diverged": len(rs),
                "mean_val_RMSE_mu": (float(np.mean([r["RMSE_mu_val_mu"] for r in rs])) if rs else None),
            }
        ok = {k: v for k, v in levels.items() if v["mean_val_RMSE_mu"] is not None}
        if not ok:
            per_block[block] = {"eta_s_star": None, "reason": "every level diverged", "levels": levels}
            continue
        best = min(ok.values(), key=lambda v: v["mean_val_RMSE_mu"])["mean_val_RMSE_mu"]
        cands = sorted(k for k, v in ok.items()
                       if v["mean_val_RMSE_mu"] <= best * (1.0 + STAGE_A_TIE_REL))
        per_block[block] = {"eta_s_star": float(cands[0]), "tie_candidates": [float(c) for c in cands],
                            "levels": levels}
    frozen["per_block"] = per_block
    cfg_path = OUT / "S1P_FROZEN_CONFIG.json"
    dump_json(frozen, cfg_path)
    digest = sha256_file(cfg_path)
    print(f"  froze S1P_FROZEN_CONFIG.json sha256={digest}")

    # ---- only now open the test split ----
    test_rows = []
    for block in BLOCKS:
        star = per_block[block]["eta_s_star"]
        if star is None:
            continue
        for r in val_rows:
            if r["block"] != block or r["eta_s"] != star:
                continue
            fm = json.loads((ROOT / r["run_dir"] / "final_metrics.json").read_text(encoding="utf-8"))
            test_rows.append({"block": block, "seed": r["seed"], "eta_s": star,
                              "test_RMSE_mu": fm.get("RMSE_mu"), "test_Delta_group": fm.get("Delta_group"),
                              "test_Delta_c_s": fm.get("Delta_c_S"), "test_Tail_RMSE": fm.get("Tail_RMSE")})
    with (grid_dir / "STAGE_A_GRID.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in val_rows + test_rows for k in r}))
        w.writeheader()
        for r in val_rows:
            rr = dict(r)
            m = [t for t in test_rows if t["block"] == r["block"] and t["seed"] == r["seed"]]
            if m:
                rr.update({k: v for k, v in m[0].items() if k.startswith("test_")})
            w.writerow(rr)

    # ---- N3' per block on test ----
    n3 = {}
    for block in BLOCKS:
        star = per_block[block]["eta_s_star"]
        if star is None:
            n3[block] = {"verdict": "FAIL", "reason": "no non-diverged level"}
            continue
        c_vals, f_vals, new_vals = [], [], []
        for r in test_rows:
            if r["block"] != block:
                continue
            sd = ROOT / "artifacts/e3_formal_runs_r1/runs" / block / "central_delivered" / ("seed%d" % r["seed"]) / "final_metrics.json"
            fd = ROOT / "artifacts/e3_formal_runs_r1/runs" / block / "fedavg_window" / ("seed%d" % r["seed"]) / "final_metrics.json"
            if sd.is_file():
                c_vals.append(json.loads(sd.read_text(encoding="utf-8")).get("RMSE_mu"))
            if fd.is_file():
                f_vals.append(json.loads(fd.read_text(encoding="utf-8")).get("RMSE_mu"))
            new_vals.append(r["test_RMSE_mu"])
        c = float(np.mean(c_vals)) if c_vals else None
        frozen_fed = float(np.mean(f_vals)) if f_vals else None
        new = float(np.mean(new_vals)) if new_vals else None
        if c is None or new is None:
            n3[block] = {"verdict": "FAIL", "reason": "missing central_delivered or new mean"}
            continue
        if new <= 1.01 * c:
            verdict = "PASS"
        elif frozen_fed is not None and new <= frozen_fed * 0.99:
            verdict = "PARTIAL"
        else:
            verdict = "FAIL"
        n3[block] = {"verdict": verdict, "eta_s_star": star, "c_central_delivered": c,
                     "frozen_fedavg_window": frozen_fed, "new_fedavg": new,
                     "ratio_to_c": new / c if c else None,
                     "vs_frozen_fedavg_rel": (new / frozen_fed - 1.0) if frozen_fed else None,
                     "threshold_1p01c": 1.01 * c}
    dump_json({"frozen_config_sha256": digest, "N3_prime": n3, "created_utc": now()},
              OUT / "S1P_STAGE_A_VERDICT.json")
    for block, v in n3.items():
        print(f"  N3' {block:<12} {v['verdict']}  ratio_to_c={v.get('ratio_to_c')}")
    return 0


'''
assert txt.count(ANCHOR) == 1, "stageA anchor"
txt = txt.replace(ANCHOR, STAGE_A + ANCHOR)

# ---- CLI ----
OLD2 = '''    ap.add_argument("--stage", choices=("gates", "g2"), default="gates")'''
NEW2 = '''    ap.add_argument("--stage", choices=("gates", "g2", "A"), default="gates")
    ap.add_argument("--force", action="store_true", help="re-run existing cells")'''
assert txt.count(OLD2) == 1, "cli"
txt = txt.replace(OLD2, NEW2)

OLD3 = '''    args = ap.parse_args()
    if args.stage == "g2":'''
NEW3 = '''    args = ap.parse_args()
    if args.stage == "A":
        return stage_a(args)
    if args.stage == "g2":'''
assert txt.count(OLD3) == 1, "cli2"
txt = txt.replace(OLD3, NEW3)

p.write_text(txt, encoding="utf-8")
print("patched;", len(txt.splitlines()), "lines")

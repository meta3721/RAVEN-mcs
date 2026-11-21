import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\driver\s1p_driver.py")
t = p.read_text(encoding="utf-8")

# ---- A. completeness-aware skip + failure marker ----
OLD = '''def run_one(block: str, arm: str, seed: int, local_steps: int, tag: str, mode: str,
            eta_s=None, force: bool = False) -> pathlib.Path:
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
    from raven_mcs.e3.real_runner.runner import run_e3_real

    d = RUNS / tag / block / arm / ("seed%d" % seed)
    if d.exists():
        if not force:
            print(f"  [skip] {d.relative_to(ROOT)} exists")
            return d
        shutil.rmtree(d)
    d.mkdir(parents=True)'''
NEW = '''def run_complete(d: pathlib.Path) -> bool:
    """A cell counts as done only when both of its terminal artifacts exist.

    `run_e3_real` can refuse before writing anything (the reuse guard raises before its own mkdir), and
    a directory left behind by such a refusal must never be mistaken for a completed run.
    """
    return (d / "final_metrics.json").is_file() and (d / "checkpoints" / "final.pt").is_file()


def run_one(block: str, arm: str, seed: int, local_steps: int, tag: str, mode: str,
            eta_s=None, force: bool = False) -> pathlib.Path:
    from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
    from raven_mcs.e3.real_runner.runner import run_e3_real

    d = RUNS / tag / block / arm / ("seed%d" % seed)
    if d.exists():
        if run_complete(d) and not force:
            print(f"  [skip] {d.relative_to(ROOT)} (complete)")
            return d
        print(f"  [redo] {d.relative_to(ROOT)} "
              f"({'forced' if force else 'incomplete cell'})", flush=True)
        shutil.rmtree(d)
    d.mkdir(parents=True)'''
assert t.count(OLD) == 1, "A"
t = t.replace(OLD, NEW)

OLD2 = '''        print(f"  [run ] {d.relative_to(ROOT)}  {dt:.1f}s  optimizer_steps={n_applied}")
    finally:
        uninstall()
    return d'''
NEW2 = '''        print(f"  [run ] {d.relative_to(ROOT)}  {dt:.1f}s  optimizer_steps={n_applied}")
    except Exception as exc:  # noqa: BLE001
        dump_json({"failed": True, "error": f"{type(exc).__name__}: {exc}"[:500],
                   "block": block, "arm": arm, "seed": int(seed), "tag": tag,
                   "server_opt": dict(ServerOptWindowRunner.SERVER_OPT), "created_utc": now()},
                  d / "RUN_FAILED.json")
        raise
    finally:
        uninstall()
    return d'''
assert t.count(OLD2) == 1, "B"
t = t.replace(OLD2, NEW2)

# ---- C. a level is eligible only if ALL screen seeds are non-diverged ----
OLD3 = '''            n_blocked = sum(1 for r in val_rows
                            if r["block"] == block and r["eta_s"] == eta_s and r["blocked"])
            levels[eta_s] = {
                "n_non_diverged": len(rs),
                "n_blocked": n_blocked,
                "mean_val_RMSE_mu": (float(np.mean([r["RMSE_mu_val_mu"] for r in rs])) if rs else None),
            }
        ok = {k: v for k, v in levels.items() if v["mean_val_RMSE_mu"] is not None}
        if not ok:
            blk = [r for r in val_rows if r["block"] == block and r["blocked"]]
            reason = ("BLOCKED: " + TRAFFIC_REUSE_GUARD_NOTE) if blk else "every level diverged"'''
NEW3 = '''            n_blocked = sum(1 for r in val_rows
                            if r["block"] == block and r["eta_s"] == eta_s and r["blocked"])
            levels[eta_s] = {
                "n_non_diverged": len(rs),
                "n_screen_seeds": len(SCREEN_SEEDS),
                # Section 4 selects on "the mean validation RMSE_mu over the 5 seeds", so a level is
                # eligible only when all five screen seeds produced a usable run.  A level averaged
                # over a surviving subset is recorded but not selectable.
                "all_screen_seeds_usable": len(rs) == len(SCREEN_SEEDS),
                "n_blocked": n_blocked,
                "mean_val_RMSE_mu": (float(np.mean([r["RMSE_mu_val_mu"] for r in rs])) if rs else None),
            }
        ok = {k: v for k, v in levels.items() if v.get("all_screen_seeds_usable")}
        if not ok:
            blk = [r for r in val_rows if r["block"] == block and r["blocked"]]
            if blk:
                reason = "BLOCKED: " + TRAFFIC_REUSE_GUARD_NOTE
            elif any(v["n_non_diverged"] for v in levels.values()):
                reason = ("NO_ELIGIBLE_LEVEL: every level lost at least one screen seed to divergence, "
                          "so none can be averaged over the 5 seeds section 4 specifies")
            else:
                reason = "every level diverged"'''
assert t.count(OLD3) == 1, "C"
t = t.replace(OLD3, NEW3)

# ---- C2. blocked/incomplete reason must survive into N3' ----
OLD4 = '''            why = per_block[block].get("reason", "no non-diverged level")
            n3[block] = {"verdict": ("BLOCKED" if why.startswith("BLOCKED") else "FAIL"),
                         "reason": why,
                         "example_error": per_block[block].get("example_error", "")}'''
NEW4 = '''            why = per_block[block].get("reason", "no non-diverged level")
            if why.startswith("BLOCKED"):
                v = "BLOCKED"
            elif why.startswith("NO_ELIGIBLE_LEVEL"):
                v = "NO_ELIGIBLE_LEVEL"
            else:
                v = "FAIL"
            n3[block] = {"verdict": v, "reason": why,
                         "example_error": per_block[block].get("example_error", "")}'''
assert t.count(OLD4) == 1, "C2"
t = t.replace(OLD4, NEW4)

# ---- D. the test-row pass must tolerate a cell with no final_metrics.json ----
OLD5 = '''            fm = json.loads((ROOT / r["run_dir"] / "final_metrics.json").read_text(encoding="utf-8"))'''
NEW5 = '''            fm_path = (ROOT / r["run_dir"] / "final_metrics.json") if r.get("run_dir") else None
            if fm_path is None or not fm_path.is_file():
                continue
            fm = json.loads(fm_path.read_text(encoding="utf-8"))'''
assert t.count(OLD5) == 1, "D"
t = t.replace(OLD5, NEW5)

p.write_text(t, encoding="utf-8")
print("patched: run_complete gate, failure marker, all-5-seed eligibility, defensive test-row read")

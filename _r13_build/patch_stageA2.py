import pathlib

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\driver\s1p_driver.py")
txt = p.read_text(encoding="utf-8")

# 1. STAGE_A header: record the traffic scheduling block as a known, pre-registered possibility.
OLD = '''STAGE_A_TIE_REL = 1e-3
'''
NEW = '''STAGE_A_TIE_REL = 1e-3

# The E3 protocol closure's reuse guard refuses `traffic` + `complete_aligned` + formal seed +
# {fedavg_window, fedasync_window, flamf_timealign_adapted, twostage_hajek, raven} with
# DUPLICATE_REUSED_TRAFFIC_RUN_BLOCKED (src/raven_mcs/e3/protocol_closure/reuse_guard.py, untracked,
# mtime 2026-10-07 17:00:29 -- added after the earlier traffic round finished at 16:27).  Stage A
# trains `fedavg_window` on traffic, so those cells are refused.  Per section 1 that condition cannot
# be met without editing src/, so it is recorded as a BLOCKED block rather than worked around; the
# refusal is caught per cell so the SensorScope and U-Air cells are unaffected and the exact error
# text is preserved.  See S1P_BLOCKED.md.
TRAFFIC_REUSE_GUARD_NOTE = (
    "traffic + complete_aligned + seed in 30001..30020 + fedavg_window/raven is REUSE_ONLY_NO_RERUN"
)
'''
assert txt.count(OLD) == 1, "a1"
txt = txt.replace(OLD, NEW)

# 2. per-cell try/except + incremental CSV write
OLD2 = '''                tag = "A_eta%g" % eta_s
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
                      f"val={row.get('RMSE_mu_val_mu')!r}  diverged={row['diverged']}")'''

NEW2 = '''                tag = "A_eta%g" % eta_s
                row = {"block": block, "arm": "fedavg_window", "seed": seed, "eta_s": eta_s,
                       "run_dir": "", "blocked": False, "blocked_reason": "", "error": "",
                       "ckpt_ok": False, "finite": False, "diverged": True}
                try:
                    d = run_one(block, "fedavg_window", seed, LOCAL_STEPS, tag, "adam", eta_s=eta_s)
                    row["run_dir"] = str(d.relative_to(ROOT)).replace("\\\\", "/")
                    ck = d / "checkpoints" / "final.pt"
                    row.update(validation_rmse_mu(block, dataset, ck, n_groups))
                    row.update(movement_per_tensor(ck, seed))
                    row["ckpt_ok"] = True
                    hajek = json.loads((d / "final_metrics.json").read_text(encoding="utf-8"))
                    row["hajek_target_risk_objective"] = hajek.get("target_risk_objective")
                    row["no_h_mass_loss"] = hajek.get("Gap_mis")
                    row["finite"] = all(
                        not isinstance(v, float) or math.isfinite(v) for v in hajek.values()
                    )
                    row["diverged"] = not (row["ckpt_ok"] and row["finite"]
                                           and row.get("RMSE_mu_val_mu") is not None
                                           and math.isfinite(row.get("RMSE_mu_val_mu") or float("nan")))
                except Exception as exc:  # noqa: BLE001
                    row["blocked"] = "DuplicateReusedTrafficRunBlocked" in type(exc).__name__
                    row["blocked_reason"] = TRAFFIC_REUSE_GUARD_NOTE if row["blocked"] else ""
                    row["error"] = f"{type(exc).__name__}: {exc}"[:400]
                    row["diverged"] = True
                val_rows.append(row)
                # incremental write so a later refusal cannot lose completed cells
                with (grid_dir / "STAGE_A_VALIDATION.csv").open("w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=sorted({k for r in val_rows for k in r}))
                    w.writeheader()
                    w.writerows(val_rows)
                print(f"  A {block:<12} eta={eta_s:<7g} seed{seed}  "
                      f"val={row.get('RMSE_mu_val_mu')!r}  "
                      f"{'BLOCKED' if row['blocked'] else 'diverged=' + str(row['diverged'])}",
                      flush=True)'''
assert txt.count(OLD2) == 1, "a2"
txt = txt.replace(OLD2, NEW2)

# 3. selection must skip blocked cells and report blocked blocks
OLD3 = '''            rs = [r for r in val_rows if r["block"] == block and r["eta_s"] == eta_s and not r["diverged"]]
            levels[eta_s] = {
                "n_non_diverged": len(rs),
                "mean_val_RMSE_mu": (float(np.mean([r["RMSE_mu_val_mu"] for r in rs])) if rs else None),
            }
        ok = {k: v for k, v in levels.items() if v["mean_val_RMSE_mu"] is not None}
        if not ok:
            per_block[block] = {"eta_s_star": None, "reason": "every level diverged", "levels": levels}
            continue'''
NEW3 = '''            rs = [r for r in val_rows if r["block"] == block and r["eta_s"] == eta_s
                  and not r["diverged"] and not r["blocked"]]
            n_blocked = sum(1 for r in val_rows
                            if r["block"] == block and r["eta_s"] == eta_s and r["blocked"])
            levels[eta_s] = {
                "n_non_diverged": len(rs),
                "n_blocked": n_blocked,
                "mean_val_RMSE_mu": (float(np.mean([r["RMSE_mu_val_mu"] for r in rs])) if rs else None),
            }
        ok = {k: v for k, v in levels.items() if v["mean_val_RMSE_mu"] is not None}
        if not ok:
            blk = [r for r in val_rows if r["block"] == block and r["blocked"]]
            reason = ("BLOCKED: " + TRAFFIC_REUSE_GUARD_NOTE) if blk else "every level diverged"
            per_block[block] = {"eta_s_star": None, "reason": reason, "levels": levels,
                                "n_blocked_cells": len(blk),
                                "example_error": (blk[0]["error"] if blk else "")}
            continue'''
assert txt.count(OLD3) == 1, "a3"
txt = txt.replace(OLD3, NEW3)

# 4. N3' must report blocked blocks
OLD4 = '''    for block in BLOCKS:
        star = per_block[block]["eta_s_star"]
        if star is None:
            n3[block] = {"verdict": "FAIL", "reason": "no non-diverged level"}
            continue'''
NEW4 = '''    for block in BLOCKS:
        star = per_block[block]["eta_s_star"]
        if star is None:
            why = per_block[block].get("reason", "no non-diverged level")
            n3[block] = {"verdict": ("BLOCKED" if why.startswith("BLOCKED") else "FAIL"),
                         "reason": why,
                         "example_error": per_block[block].get("example_error", "")}
            continue'''
assert txt.count(OLD4) == 1, "a4"
txt = txt.replace(OLD4, NEW4)

# 5. Stage A summary print must tolerate BLOCKED
OLD5 = '''    for block, v in n3.items():
        print(f"  N3' {block:<12} {v['verdict']}  ratio_to_c={v.get('ratio_to_c')}")
    return 0'''
NEW5 = '''    for block, v in n3.items():
        print(f"  N3' {block:<12} {v['verdict']}  ratio_to_c={v.get('ratio_to_c')}"
              + (f"  ({v.get('reason', '')[:80]})" if v["verdict"] == "BLOCKED" else ""), flush=True)
    return 0'''
assert txt.count(OLD5) == 1, "a5"
txt = txt.replace(OLD5, NEW5)

p.write_text(txt, encoding="utf-8")
print("patched;", len(txt.splitlines()), "lines")

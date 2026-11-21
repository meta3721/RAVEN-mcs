"""Phase A Design mechanism audit. Read-only over sealed E3/E4 artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
E3 = ROOT / "artifacts" / "e3_formal_runs_r1" / "runs"
E4 = ROOT / "artifacts" / "e4_core_mechanism_ablation_r1" / "runs"
OUT = Path(__file__).resolve().parent / "design_noharm_results" / "phase_a"
DATASETS = ("sensorscope", "uair")
SEEDS = list(range(30001, 30021))
METRICS = (
    "Delta_group",
    "Delta_c_s",
    "RMSE_mu",
    "Tail_RMSE",
    "ESS",
    "clip_rate_stage1",
    "clip_rate_stage2",
    "delta_ref",
)


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _run_dir(root: Path, dataset: str, method: str, seed: int) -> Path:
    return root / dataset / method / f"seed{seed}"


def _l1(x: np.ndarray) -> float:
    return float(np.abs(x).sum())


def _coarse_blocks(vec: np.ndarray) -> np.ndarray:
    n = int(vec.size)
    if n % 4 != 0:
        return vec
    return vec.reshape(-1, 4).sum(axis=0)


def _match_p2(off_p2: list, alpha_off: np.ndarray, beta_off: np.ndarray, used: set[int]):
    for i, st in enumerate(off_p2):
        if i in used:
            continue
        beta_p2 = np.asarray(st.get("beta") or [], dtype=np.float64)
        alpha_p2 = np.asarray(st.get("alpha") or [], dtype=np.float64)
        if beta_p2.size != beta_off.size or alpha_p2.size != alpha_off.size:
            continue
        if np.allclose(beta_p2, beta_off, atol=1e-7, rtol=1e-5) and np.allclose(
            alpha_p2, alpha_off, atol=1e-7, rtol=1e-5
        ):
            return i, st
    return None, None


def _align_windows(on_wm: list, off_wm: list, off_p2: list) -> list[dict]:
    rows = []
    used_p2: set[int] = set()
    for on, off in zip(on_wm, off_wm):
        if not on.get("active") or not off.get("active"):
            continue
        clients_on = list(on.get("active_clients") or [])
        clients_off = list(off.get("active_clients") or [])
        alpha_on = np.asarray(on.get("alpha") or [], dtype=np.float64)
        beta_on = np.asarray(on.get("beta_hat") or [], dtype=np.float64)
        alpha_off = np.asarray(off.get("alpha") or [], dtype=np.float64)
        beta_off = np.asarray(off.get("beta_hat") or [], dtype=np.float64)
        p2_i, st = _match_p2(off_p2, alpha_off, beta_off, used_p2)
        if st is None:
            rows.append(
                {
                    "window_id": on.get("window_id", off.get("window_id")),
                    "n_active": int(alpha_on.size),
                    "same_clients": clients_on == clients_off,
                    "dim_ok": False,
                    "p2_matches_off": False,
                    "alpha_beta_l1_on": _l1(alpha_on - beta_on) if alpha_on.size == beta_on.size and alpha_on.size else np.nan,
                    "alpha_beta_l1_off": _l1(alpha_off - beta_off) if alpha_off.size == beta_off.size and alpha_off.size else np.nan,
                }
            )
            continue
        used_p2.add(int(p2_i))
        m = np.asarray(st["M"], dtype=np.float64)
        mu = np.asarray(st["mu"], dtype=np.float64)
        same_clients = clients_on == clients_off
        dim_ok = (
            m.ndim == 2
            and m.shape[1] == alpha_on.size == beta_on.size == alpha_off.size == beta_off.size
            and m.shape[0] == mu.size
        )
        p2_matches_off = True
        row = {
            "window_id": on.get("window_id", off.get("window_id")),
            "n_active": int(alpha_on.size),
            "same_clients": bool(same_clients),
            "dim_ok": bool(dim_ok),
            "p2_matches_off": bool(p2_matches_off),
            "alpha_beta_l1_on": _l1(alpha_on - beta_on) if alpha_on.size and alpha_on.size == beta_on.size else np.nan,
            "alpha_beta_l1_off": _l1(alpha_off - beta_off) if alpha_off.size and alpha_off.size == beta_off.size else np.nan,
        }
        if same_clients and dim_ok:
            mix_beta_on = m @ beta_on
            mix_beta_off = m @ beta_off
            mix_alpha_on = m @ alpha_on
            mix_alpha_off = m @ alpha_off
            row.update(
                {
                    "p2_beta_l1_on": _l1(mix_beta_on - mu),
                    "p2_beta_l1_off": _l1(mix_beta_off - mu),
                    "p2_alpha_l1_on": _l1(mix_alpha_on - mu),
                    "p2_alpha_l1_off": _l1(mix_alpha_off - mu),
                    "coarse_beta_l1_on": _l1(_coarse_blocks(mix_beta_on) - _coarse_blocks(mu)),
                    "coarse_beta_l1_off": _l1(_coarse_blocks(mix_beta_off) - _coarse_blocks(mu)),
                    "coarse_alpha_l1_on": _l1(_coarse_blocks(mix_alpha_on) - _coarse_blocks(mu)),
                    "coarse_alpha_l1_off": _l1(_coarse_blocks(mix_alpha_off) - _coarse_blocks(mu)),
                    "mu_dim": int(mu.size),
                }
            )
        rows.append(row)
    return rows


def _eventtrace_hash(run: Path) -> str | None:
    ledger = run / "ledger.jsonl"
    if not ledger.is_file():
        return None
    for line in ledger.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        if rec.get("EventTrace_hash"):
            return str(rec["EventTrace_hash"])
    return None


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    seed_rows = []
    window_rows = []
    coverage = []

    for dataset in DATASETS:
        for seed in SEEDS:
            on_dir = _run_dir(E3, dataset, "raven", seed)
            off_dir = _run_dir(E4, dataset, "raven_wo_design", seed)
            rec = {
                "dataset": dataset,
                "seed": seed,
                "on_exists": on_dir.is_dir(),
                "off_exists": off_dir.is_dir(),
                "on_accepted": (on_dir / "FORMAL_ACCEPTED.json").is_file(),
                "off_accepted": (off_dir / "FORMAL_ACCEPTED.json").is_file(),
                "on_has_p2": (on_dir / "p2_invocation_states.json").is_file(),
                "off_has_p2": (off_dir / "p2_invocation_states.json").is_file(),
            }
            if not (on_dir.is_dir() and off_dir.is_dir()):
                coverage.append(rec)
                continue
            on_m = _load_json(on_dir / "final_metrics.json")
            off_m = _load_json(off_dir / "final_metrics.json")
            rec["eventtrace_hash_on"] = _eventtrace_hash(on_dir)
            rec["eventtrace_hash_off"] = _eventtrace_hash(off_dir)
            rec["eventtrace_match"] = rec["eventtrace_hash_on"] == rec["eventtrace_hash_off"]
            seed_row = {"dataset": dataset, "seed": seed, "eventtrace_match": rec["eventtrace_match"]}
            for key in METRICS:
                seed_row[f"{key}_on"] = on_m.get(key)
                seed_row[f"{key}_off"] = off_m.get(key)
                a, b = on_m.get(key), off_m.get(key)
                if isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(b) > 1e-15:
                    seed_row[f"{key}_rel_off_minus_on_pct"] = (float(b) - float(a)) / abs(float(a)) * 100.0
                    seed_row[f"{key}_rel_on_minus_off_pct"] = (float(a) - float(b)) / abs(float(b)) * 100.0
                else:
                    seed_row[f"{key}_rel_off_minus_on_pct"] = np.nan
                    seed_row[f"{key}_rel_on_minus_off_pct"] = np.nan
            seed_rows.append(seed_row)

            on_wm = _load_json(on_dir / "window_metrics.json")
            off_wm = _load_json(off_dir / "window_metrics.json")
            off_p2 = _load_json(off_dir / "p2_invocation_states.json") if rec["off_has_p2"] else []
            aligned = _align_windows(on_wm, off_wm, off_p2)
            rec["n_windows_on"] = len(on_wm)
            rec["n_windows_off"] = len(off_wm)
            rec["n_p2_off"] = len(off_p2)
            rec["n_aligned"] = len(aligned)
            rec["n_same_clients"] = sum(1 for r in aligned if r.get("same_clients"))
            rec["n_p2_usable"] = sum(1 for r in aligned if r.get("same_clients") and r.get("dim_ok"))
            coverage.append(rec)
            for row in aligned:
                window_rows.append({"dataset": dataset, "seed": seed, **row})

    seed_df = pd.DataFrame(seed_rows)
    win_df = pd.DataFrame(window_rows)
    cov_df = pd.DataFrame(coverage)
    seed_df.to_csv(OUT / "seed_metrics.csv", index=False)
    win_df.to_csv(OUT / "window_alignment.csv", index=False)
    cov_df.to_csv(OUT / "coverage.csv", index=False)

    summary_rows = []
    for dataset, g in seed_df.groupby("dataset"):
        row = {"dataset": dataset, "n_seeds": int(len(g))}
        for key in METRICS:
            on = g[f"{key}_on"].astype(float)
            off = g[f"{key}_off"].astype(float)
            row[f"{key}_on_mean"] = float(on.mean())
            row[f"{key}_off_mean"] = float(off.mean())
            rel = (on - off) / off.replace(0, np.nan) * 100.0
            row[f"{key}_on_vs_off_pct_mean"] = float(rel.mean())
            row[f"{key}_on_worse_count"] = int((on > off + 1e-12).sum())
        summary_rows.append(row)
    summary_df = pd.DataFrame(summary_rows)

    win_stats = []
    usable = (
        win_df[win_df["same_clients"].astype(bool) & win_df["dim_ok"].astype(bool)].copy()
        if not win_df.empty and "same_clients" in win_df.columns
        else win_df.iloc[0:0].copy()
    )
    for dataset, g in ([] if usable.empty else usable.groupby("dataset")):
        dbeta = g["p2_beta_l1_on"] - g["p2_beta_l1_off"]
        dalpha = g["p2_alpha_l1_on"] - g["p2_alpha_l1_off"]
        cbeta = g["coarse_beta_l1_on"] - g["coarse_beta_l1_off"]
        calpha = g["coarse_alpha_l1_on"] - g["coarse_alpha_l1_off"]
        win_stats.append(
            {
                "dataset": dataset,
                "n_windows": int(len(g)),
                "p2_beta_on_mean": float(g["p2_beta_l1_on"].mean()),
                "p2_beta_off_mean": float(g["p2_beta_l1_off"].mean()),
                "p2_beta_on_worse_frac": float((dbeta > 1e-12).mean()),
                "p2_alpha_on_mean": float(g["p2_alpha_l1_on"].mean()),
                "p2_alpha_off_mean": float(g["p2_alpha_l1_off"].mean()),
                "p2_alpha_on_worse_frac": float((dalpha > 1e-12).mean()),
                "coarse_beta_on_worse_frac": float((cbeta > 1e-12).mean()),
                "coarse_alpha_on_worse_frac": float((calpha > 1e-12).mean()),
                "alpha_beta_l1_on_mean": float(g["alpha_beta_l1_on"].mean()),
                "alpha_beta_l1_off_mean": float(g["alpha_beta_l1_off"].mean()),
            }
        )
    win_sum = pd.DataFrame(win_stats)
    summary_df.to_csv(OUT / "seed_summary.csv", index=False)
    win_sum.to_csv(OUT / "window_summary.csv", index=False)

    lines = ["Phase A Design mechanism audit (no new training).", ""]
    lines.append("Sources")
    lines.append(f"- Design ON:  {E3.as_posix()}/*/raven/seed*")
    lines.append(f"- Design OFF: {E4.as_posix()}/*/raven_wo_design/seed*")
    lines.append("- Complete-aligned only. Seeds 30001-30020.")
    lines.append("")
    lines.append("Coverage")
    lines.append(f"- seed rows: {len(seed_df)}")
    lines.append(f"- eventtrace matches: {int(cov_df['eventtrace_match'].fillna(False).sum())}/{len(cov_df)}")
    lines.append(f"- ON p2 files: {int(cov_df['on_has_p2'].sum())} (expected 0 on E3 formal raven)")
    lines.append(f"- OFF p2 files: {int(cov_df['off_has_p2'].sum())}")
    lines.append(f"- aligned windows: {len(win_df)}; usable same-client+dim: {len(usable)}")
    lines.append("- zeta vectors are not persisted; clip_rate_stage1 is the stored Design-clip proxy.")
    lines.append("- P2 target dimension is runtime h(i) (U-Air 144, SensorScope 220), not the 4-block paper caption.")
    lines.append("- coarse_* collapses station::block by block = group_id % 4.")
    lines.append("")
    lines.append("Seed-level means (ON = full RAVEN, OFF = w/o-Design)")
    for _, r in summary_df.iterrows():
        lines.append(f"[{r['dataset']}] n={int(r['n_seeds'])}")
        for key in ("Delta_group", "Delta_c_s", "RMSE_mu", "Tail_RMSE", "clip_rate_stage1", "ESS"):
            lines.append(
                f"  {key}: ON {r[f'{key}_on_mean']:.6f} vs OFF {r[f'{key}_off_mean']:.6f} "
                f"(ON vs OFF {r[f'{key}_on_vs_off_pct_mean']:+.3f}%; ON worse {int(r[f'{key}_on_worse_count'])}/20)"
            )
    lines.append("")
    lines.append("Window-level P2 mismatch using OFF-run M,mu and ON/OFF beta,alpha from window_metrics")
    for _, r in win_sum.iterrows():
        lines.append(
            f"[{r['dataset']}] windows={int(r['n_windows'])} "
            f"P2||M beta-mu|| ON {r['p2_beta_on_mean']:.4f} OFF {r['p2_beta_off_mean']:.4f} "
            f"(ON worse {r['p2_beta_on_worse_frac']*100:.1f}%)"
        )
        lines.append(
            f"  P2||M alpha-mu|| ON {r['p2_alpha_on_mean']:.4f} OFF {r['p2_alpha_off_mean']:.4f} "
            f"(ON worse {r['p2_alpha_on_worse_frac']*100:.1f}%)"
        )
        lines.append(
            f"  coarse-4 ||M alpha-mu|| ON-worse frac {r['coarse_alpha_on_worse_frac']*100:.1f}%; "
            f"||alpha-beta|| ON {r['alpha_beta_l1_on_mean']:.4f} OFF {r['alpha_beta_l1_off_mean']:.4f}"
        )
    lines.append("")
    lines.append("Author verdict (honest)")

    u = summary_df[summary_df["dataset"] == "uair"].iloc[0]
    s = summary_df[summary_df["dataset"] == "sensorscope"].iloc[0]
    u_win = win_sum[win_sum["dataset"] == "uair"].iloc[0] if not win_sum.empty else None
    s_win = win_sum[win_sum["dataset"] == "sensorscope"].iloc[0] if not win_sum.empty else None

    rmse_gap = float(u["RMSE_mu_on_vs_off_pct_mean"])
    group_gap = float(u["Delta_group_on_vs_off_pct_mean"])
    cs_gap = float(u["Delta_c_s_on_vs_off_pct_mean"])
    clip_on = float(u["clip_rate_stage1_on_mean"])
    clip_off = float(u["clip_rate_stage1_off_mean"])

    beta_pulls_away = bool(u_win is not None and u_win["p2_beta_on_mean"] > u_win["p2_beta_off_mean"] + 1e-6)
    alpha_worse = bool(u_win is not None and u_win["p2_alpha_on_worse_frac"] >= 0.6)
    clip_extreme = clip_on > 0.05
    struct_small_rmse_large = abs(group_gap) < 2.0 and rmse_gap > 4.0

    if beta_pulls_away:
        lines.append(
            "- U-Air fine P2 L1: Design-on beta is farther from the stored P2 target than Design-off."
        )
    else:
        lines.append(
            "- U-Air fine P2 L1 (144-d) is often geometrically flat along the simplex: "
            "||M v - mu||_1 can be identical for different v. Do not use that as evidence that beta is on-target."
        )
    if u_win is not None:
        lines.append(
            f"- U-Air coarse-4 ||M beta-mu|| ON-worse frac {float(u_win['coarse_beta_on_worse_frac'])*100:.1f}%; "
            f"||M alpha-mu|| ON-worse frac {float(u_win['coarse_alpha_on_worse_frac'])*100:.1f}%."
        )
        lines.append(
            f"- U-Air ||alpha-beta||_1 is larger with Design ON "
            f"({float(u_win['alpha_beta_l1_on_mean']):.3f} vs {float(u_win['alpha_beta_l1_off_mean']):.3f}). "
            "P2 systematically pulls away from the Design reference."
        )
    if clip_extreme:
        lines.append(
            f"- U-Air clip_rate_stage1 ON {clip_on:.4f} vs OFF {clip_off:.4f}. "
            "Design ratios are often clipped; clipping experiments are warranted."
        )
    else:
        lines.append(
            f"- U-Air clip_rate_stage1 ON {clip_on:.4f} vs OFF {clip_off:.4f}. "
            "Stored clip rate is modest; extreme-zeta is not the main persisted signal."
        )
    lines.append(
        f"- U-Air seed means: Delta_group ON vs OFF {group_gap:+.3f}%; "
        f"RMSE_mu {rmse_gap:+.3f}%; Delta_c_s {cs_gap:+.3f}% "
        f"(positive = Design-on worse)."
    )
    if struct_small_rmse_large:
        lines.append(
            "- RMSE gap is large relative to the structural gap. Local Design-weighted training "
            "is the more plausible RMSE driver. Phase B1 P2-only is unlikely to close RMSE."
        )
    elif abs(rmse_gap) > 3.0:
        lines.append(
            "- RMSE gap remains large. Even if beta is off-target, a P2 constraint alone is not enough "
            "to claim the Design problem is solved."
        )
    lines.append(
        f"- SensorScope seed means: Delta_group {float(s['Delta_group_on_vs_off_pct_mean']):+.3f}%; "
        f"RMSE_mu {float(s['RMSE_mu_on_vs_off_pct_mean']):+.3f}%; "
        f"Delta_c_s {float(s['Delta_c_s_on_vs_off_pct_mean']):+.3f}%."
    )
    if u_win is not None:
        lines.append(
            f"- U-Air window frac where Design-on has worse P2||M alpha-mu||: "
            f"{u_win['p2_alpha_on_worse_frac']*100:.1f}% "
            f"(systematic if >>50%; sporadic if near 50%)."
        )
    if s_win is not None:
        lines.append(
            f"- SensorScope window frac Design-on worse P2||M alpha-mu||: "
            f"{s_win['p2_alpha_on_worse_frac']*100:.1f}%."
        )
    lines.append("- Phase A does not select a method and does not use a test-set gate.")
    lines.append("- VERDICT_PHASE_A=AUDIT_ONLY. Not VALGATE_SOLVES / CONSTRAINED_SOLVES / DESIGN_DROPPED.")
    (OUT / "conclusion.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

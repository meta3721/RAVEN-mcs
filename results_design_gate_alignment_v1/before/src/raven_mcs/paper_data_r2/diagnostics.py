"""Optional offline extraction of diagnostics from sealed run states (no training)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .io_util import MISSING, ensure_dir, sha256_file, write_csv, write_json, write_text

DIAG_ITEMS = [
    "debt_trajectory",
    "debt_norm",
    "per_group_debt",
    "ESS_trajectory",
    "n_eff_trajectory",
    "P2_runtime",
    "solver_runtime",
    "P2_objective_components",
    "calibration_residual",
    "target_composition_trajectory",
    "weight_distribution",
    "clipping_frequency",
    "q_distribution",
    "p_obs_distribution",
    "active_client_counts",
    "delivered_counts",
    "opportunity_counts",
    "observed_counts",
    "usable_counts",
    "P2_candidate_counts",
    "aggregation_participant_counts",
    "staleness",
    "per_group_error",
    "per_stratum_error",
]


def extract_diagnostics(root: Path, paper: Path) -> dict[str, Any]:
    root = Path(root)
    out = ensure_dir(paper / "02_supporting_data" / "diagnostics_r2")
    sample = root / "artifacts/e3_formal_runs_r1/runs/sensorscope/raven/seed30001"
    fm = json.loads((sample / "final_metrics.json").read_text(encoding="utf-8"))
    wm = json.loads((sample / "window_metrics.json").read_text(encoding="utf-8"))
    wm_keys = sorted({k for w in wm for k in w.keys()}) if wm else []

    # Extract run-level scalars from sealed final_metrics for E3 SS/UA raven + E4 240 cells' paths
    run_rows = []
    window_rows = []
    extracted_from = []

    def consider(run_dir: Path, round_id: str, dataset: str, method: str, seed: str) -> None:
        fmp = run_dir / "final_metrics.json"
        wmp = run_dir / "window_metrics.json"
        if not fmp.is_file():
            return
        metrics = json.loads(fmp.read_text(encoding="utf-8"))
        run_rows.append(
            {
                "round": round_id,
                "dataset": dataset,
                "method": method,
                "seed": seed,
                "source_file": str(fmp).replace("\\", "/"),
                "source_sha256": sha256_file(fmp),
                "ESS": metrics.get("ESS", MISSING),
                "MAE_mu": metrics.get("MAE_mu", MISSING),
                "RMSE_rho": metrics.get("RMSE_rho", MISSING),
                "clip_rate_stage1": metrics.get("clip_rate_stage1", MISSING),
                "clip_rate_stage2": metrics.get("clip_rate_stage2", MISSING),
                "Q_norm1_over_S": metrics.get("Q_norm1_over_S", MISSING),
                "Q_norm2_over_S": metrics.get("Q_norm2_over_S", MISSING),
                "runtime_seconds": metrics.get("runtime_seconds", MISSING),
                "solver_status": metrics.get("solver_status", MISSING),
                "delta_ref": metrics.get("delta_ref", MISSING),
                "no_training_attestation": True,
            }
        )
        extracted_from.append(str(fmp).replace("\\", "/"))
        if wmp.is_file():
            windows = json.loads(wmp.read_text(encoding="utf-8"))
            n_active = []
            a_r = []
            for w in windows:
                n = len(w.get("active_clients") or [])
                n_active.append(n)
                a_r.append(w.get("a_r_size"))
                window_rows.append(
                    {
                        "round": round_id,
                        "dataset": dataset,
                        "method": method,
                        "seed": seed,
                        "window_id": w.get("window_id"),
                        "active": w.get("active"),
                        "n_active_clients": n,
                        "a_r_size": w.get("a_r_size"),
                        "has_alpha": int("alpha" in w),
                        "has_beta_hat": int("beta_hat" in w),
                        "has_debt": int("debt" in w or "debt_norm" in w),
                        "source_file": str(wmp).replace("\\", "/"),
                    }
                )

    # E3 SensorScope/U-Air raven (reference) — 20 seeds each
    for ds in ("sensorscope", "uair"):
        for seed in range(30001, 30021):
            consider(
                root / "artifacts/e3_formal_runs_r1/runs" / ds / "raven" / f"seed{seed}",
                "E3",
                ds,
                "raven",
                str(seed),
            )

    # E4 parent ablations + Gen2 inst (paths from 240-cell CSV)
    import csv

    cells = list(
        csv.DictReader((paper / "01_core_data/e4/E4_FINAL_VALID_EVIDENCE_240.csv").open(encoding="utf-8", newline=""))
    )
    seen = set()
    for r in cells:
        p = r.get("path") or ""
        if not p or p in seen:
            continue
        seen.add(p)
        consider(root / p, "E4", r["dataset_raw"], r["method_raw"], str(r["seed"]))

    write_csv(out / "RUNLEVEL_SEALED_SCALARS_R2.csv", run_rows)
    write_csv(out / "WINDOW_ACTIVE_CLIENTS_R2.csv", window_rows)

    availability = []
    present_map = {
        "clipping_frequency": "final_metrics.json clip_rate_stage1/stage2",
        "weight_distribution": "window_metrics.json alpha (per window, supporting)",
        "active_client_counts": "window_metrics.json active_clients",
        "P2_candidate_counts": "window_metrics.json a_r_size (interpreted as candidate/active-set size; supporting only)",
        "aggregation_participant_counts": "window_metrics.json n_active_clients",
        "solver_runtime": "final_metrics.json runtime_seconds (total run, not P2-only)",
    }
    for item in DIAG_ITEMS:
        if item in present_map:
            availability.append(
                {
                    "item": item,
                    "status": "EXTRACTED_SUPPORTING",
                    "source": present_map[item],
                    "paper_use": "SUPPORTING_ONLY",
                    "no_training": True,
                }
            )
        elif item in {"ESS_trajectory"}:
            availability.append(
                {
                    "item": item,
                    "status": "PARTIAL_SCALAR_ONLY",
                    "source": "final_metrics.json ESS (run-level scalar, not a trajectory)",
                    "paper_use": "SUPPORTING_ONLY",
                    "no_training": True,
                }
            )
        else:
            availability.append(
                {
                    "item": item,
                    "status": MISSING,
                    "source": "searched window_metrics.json keys=" + ",".join(wm_keys) + "; final_metrics.json keys=" + ",".join(sorted(fm.keys())),
                    "paper_use": "do not invent",
                    "no_training": True,
                }
            )
    write_csv(out / "DIAGNOSTIC_EXTRACTION_STATUS_R2.csv", availability)
    write_json(
        out / "DIAGNOSTIC_EXTRACTION_ATTESTATION.json",
        {
            "no_training": True,
            "no_new_stochastic_process": True,
            "formula": "copy sealed JSON fields; n_active_clients = len(active_clients)",
            "n_runlevel_rows": len(run_rows),
            "n_window_rows": len(window_rows),
            "sample_window_keys": wm_keys,
            "note": "Debt/ESS/P2-runtime trajectories remain MISSING_NOT_RECORDED as time series. Do not promote to paper claims.",
        },
    )
    extra_md = [
        "# Extra valid data collected in R2",
        "",
        "Supporting diagnostics only. Not new RQ answers.",
        "",
        f"- Run-level sealed scalars: `{len(run_rows)}` rows in `02_supporting_data/diagnostics_r2/RUNLEVEL_SEALED_SCALARS_R2.csv` (ESS, MAE_mu, RMSE_rho, clip rates, Q norms, runtime_seconds, solver_status).",
        f"- Per-window active-client / a_r_size: `{len(window_rows)}` rows in `WINDOW_ACTIVE_CLIENTS_R2.csv`.",
        "- MAE_mu and RMSE_rho exist in sealed `final_metrics.json` even though the 240-cell CSV marked them MISSING_NOT_RECORDED; they are packaged here as supporting extraction, not as new core E4 metrics.",
        "- Debt trajectory, ESS trajectory, and P2-only runtime remain MISSING_NOT_RECORDED (not present as series in sealed window_metrics.json).",
        "",
    ]
    write_text(paper / "10_reports" / "EXTRA_VALID_DATA_COLLECTED_R2.md", "\n".join(extra_md))
    return {
        "n_runlevel": len(run_rows),
        "n_window": len(window_rows),
        "window_keys": wm_keys,
        "missing_items": [a["item"] for a in availability if a["status"] == MISSING],
    }

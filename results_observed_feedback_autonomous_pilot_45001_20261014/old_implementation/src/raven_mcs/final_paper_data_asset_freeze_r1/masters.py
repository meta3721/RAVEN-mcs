"""Run-level, long-metric, statistics, dataset, and config masters."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from raven_mcs.paper_data_r1.io_util import copy_file, sha256_file, write_csv, write_json
from raven_mcs.final_paper_data_asset_freeze_r1.constants import N_A, NA, REFERENCE_METHODS


def _na(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return NA
    s = str(v).strip()
    if s == "" or s.lower() in {"nan", "none", "null"}:
        return NA
    return s


def _write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def _row_run(
    *,
    round_id: str,
    dataset: str,
    scenario: str,
    method: str,
    configuration: str,
    seed: str,
    generation: str,
    run_id: str,
    attempt_id: str,
    validity: str,
    evidence_status: str,
    paper_role: str,
    source_vintage: str,
    EventTrace_hash: str,
    RMSE_mu: str,
    MAE_mu: str,
    Tail_RMSE: str,
    Delta_group: str,
    Delta_c_s: str,
    RMSE_rho: str,
    runtime: str,
    warning_count: str = NA,
    P2_warning_count: str = NA,
    notes: str = "",
    config_hash: str = NA,
    source_hash: str = NA,
    dataset_hash: str = NA,
    split_hash: str = NA,
    checkpoint_hash: str = NA,
) -> dict:
    return {
        "round": round_id,
        "dataset": dataset,
        "scenario": scenario,
        "method": method,
        "configuration": configuration,
        "seed": seed,
        "generation": generation,
        "run_id": run_id,
        "attempt_id": _na(attempt_id),
        "validity": validity,
        "evidence_status": evidence_status,
        "paper_role": paper_role,
        "source_vintage": source_vintage,
        "EventTrace_hash": _na(EventTrace_hash),
        "config_hash": config_hash,
        "source_hash": source_hash,
        "dataset_hash": dataset_hash,
        "split_hash": split_hash,
        "checkpoint_hash": _na(checkpoint_hash),
        "RMSE_mu": _na(RMSE_mu),
        "MAE_mu": _na(MAE_mu),
        "Tail_RMSE": _na(Tail_RMSE),
        "Delta_group": _na(Delta_group),
        "Delta_c_s": _na(Delta_c_s),
        "RMSE_rho": _na(RMSE_rho),
        "runtime": _na(runtime),
        "warning_count": _na(warning_count),
        "P2_warning_count": _na(P2_warning_count),
        "notes": notes,
    }


def build_run_masters(r2: Path, out: Path) -> dict:
    rows: list[dict] = []
    e1 = pd.read_csv(r2 / "01_core_data/e1/E1_FINAL_VALID_RUNS.csv")
    for _, r in e1.iterrows():
        rows.append(
            _row_run(
                round_id="E1",
                dataset=_na(r.get("dataset")),
                scenario=_na(r.get("scenario")),
                method=_na(r.get("method")),
                configuration=_na(r.get("method")),
                seed=str(r.get("seed")),
                generation=N_A,
                run_id=_na(r.get("logical_run_id")),
                attempt_id="1",
                validity=_na(r.get("validity_label")) or "VALID",
                evidence_status="PAPER_CORE",
                paper_role="RQ1_PROBLEM_EVIDENCE",
                source_vintage="E1_R2_FINAL_SEALED",
                EventTrace_hash=_na(r.get("EventTrace_hash")),
                RMSE_mu=r.get("RMSE_mu"),
                MAE_mu=r.get("MAE_mu"),
                Tail_RMSE=r.get("Tail_RMSE"),
                Delta_group=r.get("Delta_group"),
                Delta_c_s=r.get("Delta_c_s"),
                RMSE_rho=r.get("RMSE_rho"),
                runtime=r.get("runtime"),
                notes=_na(r.get("notes")),
            )
        )
    e2 = pd.read_csv(r2 / "01_core_data/e2/E2_FINAL_VALID_RUNS_600.csv")
    for _, r in e2.iterrows():
        rows.append(
            _row_run(
                round_id="E2",
                dataset=_na(r.get("dataset")),
                scenario=_na(r.get("scenario")),
                method=_na(r.get("method")),
                configuration=_na(r.get("method")),
                seed=str(r.get("seed")),
                generation=N_A,
                run_id=_na(r.get("logical_run_id")),
                attempt_id=_na(r.get("attempt_id")),
                validity=_na(r.get("validity_label")) or "VALID",
                evidence_status="PAPER_CORE",
                paper_role="RQ1_PROBLEM_EVIDENCE",
                source_vintage="E2_TRAFFIC_FORMAL_RUNS_R1",
                EventTrace_hash=_na(r.get("EventTrace_hash")),
                RMSE_mu=r.get("RMSE_mu"),
                MAE_mu=r.get("MAE_mu"),
                Tail_RMSE=r.get("Tail_RMSE"),
                Delta_group=r.get("Delta_group"),
                Delta_c_s=NA,
                RMSE_rho=r.get("RMSE_rho"),
                runtime=r.get("runtime_seconds"),
                notes="E2 formal accepted; not a RAVEN superiority benchmark",
            )
        )
    e3 = pd.read_csv(r2 / "01_core_data/e3/E3_FINAL_VALID_EVIDENCE_INDEX.csv")
    for _, r in e3.iterrows():
        ds = str(r.get("dataset"))
        method = str(r.get("method"))
        traffic = ds.lower() in {"nsw-traffic", "traffic", "nsw_traffic"}
        ref = method in REFERENCE_METHODS
        if traffic:
            status, role = "NOT_COMPARABLE", "NOT_FOR_PAPER"
        elif ref:
            status, role = "REFERENCE_ONLY", "APPENDIX_ONLY"
        else:
            status, role = "PAPER_CORE", "RQ2_MAIN_EFFECTIVENESS"
        rows.append(
            _row_run(
                round_id="E3",
                dataset=ds,
                scenario=_na(r.get("scenario")),
                method=method,
                configuration=method,
                seed=str(r.get("seed")),
                generation=N_A,
                run_id=_na(r.get("logical_run_id")),
                attempt_id=_na(r.get("attempt_id")),
                validity="VALID" if str(r.get("accepted")).lower() in {"true", "1"} else str(r.get("accepted")),
                evidence_status=status,
                paper_role=role,
                source_vintage=_na(r.get("source_vintage")),
                EventTrace_hash=_na(r.get("EventTrace_hash")),
                RMSE_mu=r.get("RMSE_mu") if str(r.get("RMSE_mu_status")).upper() == "VALID" else NA,
                MAE_mu=r.get("MAE_mu") if str(r.get("MAE_mu_status")).upper() == "VALID" else NA,
                Tail_RMSE=r.get("Tail_RMSE") if str(r.get("Tail_RMSE_status")).upper() == "VALID" else NA,
                Delta_group=r.get("Delta_group") if str(r.get("Delta_group_status")).upper() == "VALID" else NA,
                Delta_c_s=r.get("Delta_c_s") if str(r.get("Delta_c_s_status")).upper() == "VALID" else NA,
                RMSE_rho=r.get("RMSE_rho") if str(r.get("RMSE_rho_status")).upper() == "VALID" else NA,
                runtime=r.get("runtime"),
                P2_warning_count=_na(r.get("P2_warning_count")),
                checkpoint_hash=_na(r.get("checkpoint_hash")),
                notes=_na(r.get("notes")),
            )
        )
    e4 = pd.read_csv(r2 / "01_core_data/e4/E4_FINAL_VALID_EVIDENCE_240.csv")
    for _, r in e4.iterrows():
        gen = str(r.get("generation"))
        cfg = str(r.get("configuration"))
        paper_core = not (cfg == "RAVEN-w/o-Inst" and gen not in {"2", "2.0"})
        rows.append(
            _row_run(
                round_id="E4",
                dataset=_na(r.get("dataset")),
                scenario="complete_aligned",
                method=_na(r.get("configuration")),
                configuration=cfg,
                seed=str(r.get("seed")),
                generation=gen,
                run_id=_na(r.get("logical_run_id")),
                attempt_id=_na(r.get("attempt_id")),
                validity=_na(r.get("validity")),
                evidence_status="PAPER_CORE" if paper_core else "SUPERSEDED",
                paper_role="RQ3_MECHANISM",
                source_vintage="E4_240_R2",
                EventTrace_hash=_na(r.get("EventTrace_hash")),
                RMSE_mu=r.get("RMSE_mu"),
                MAE_mu=r.get("MAE_mu") if str(r.get("MAE_mu_status")).upper() == "VALID" else NA,
                Tail_RMSE=r.get("Tail_RMSE"),
                Delta_group=r.get("Delta_group"),
                Delta_c_s=r.get("Delta_c_s"),
                RMSE_rho=r.get("RMSE_rho") if str(r.get("RMSE_rho_status")).upper() == "VALID" else NA,
                runtime=r.get("runtime"),
                warning_count=_na(r.get("solver_warnings")),
                checkpoint_hash=_na(r.get("checkpoint_hash")),
                notes=_na(r.get("superseded_reason")),
            )
        )
    df = pd.DataFrame(rows)
    csv_path = out / "04_ALL_RUN_METRICS/ALL_VALID_RUNS_MASTER.csv"
    write_csv(csv_path, df.to_dict(orient="records"))
    _write_parquet(df, out / "04_ALL_RUN_METRICS/ALL_VALID_RUNS_MASTER.parquet")

    long_src = r2 / "01_core_data/master/PAPER_EVIDENCE_MASTER_LONG_R2.csv"
    long_df = pd.read_csv(long_src)
    long_rows = []
    src_sha = sha256_file(long_src)
    for _, r in long_df.iterrows():
        long_rows.append(
            {
                "round": r.get("round"),
                "dataset": r.get("dataset"),
                "scenario": r.get("scenario"),
                "method": r.get("method_or_configuration"),
                "configuration": r.get("method_or_configuration"),
                "seed": r.get("seed"),
                "generation": N_A,
                "metric": r.get("metric"),
                "value": _na(r.get("value")),
                "unit": N_A,
                "granularity": "run",
                "evidence_status": r.get("scientific_status") or r.get("status"),
                "paper_role": r.get("paper_role"),
                "source_file": r.get("source_file"),
                "source_sha256": src_sha,
            }
        )
    ldf = pd.DataFrame(long_rows)
    write_csv(out / "04_ALL_RUN_METRICS/ALL_VALID_METRICS_LONG.csv", ldf.to_dict(orient="records"))
    _write_parquet(ldf, out / "04_ALL_RUN_METRICS/ALL_VALID_METRICS_LONG.parquet")

    n_e1 = int((df["round"] == "E1").sum())
    n_e2 = int((df["round"] == "E2").sum())
    n_e3 = int((df["round"] == "E3").sum())
    n_e3_comp = int(((df["round"] == "E3") & (df["evidence_status"] == "PAPER_CORE")).sum())
    n_e4 = int((df["round"] == "E4").sum())
    n_wo2 = int(((df["round"] == "E4") & (df["configuration"] == "RAVEN-w/o-Inst") & (df["generation"].astype(str).isin(["2", "2.0"]))).sum())
    return {
        "n_runs": len(df),
        "n_long": len(ldf),
        "n_e1": n_e1,
        "n_e2": n_e2,
        "n_e3": n_e3,
        "n_e3_comparable_nonref": n_e3_comp,
        "n_e4": n_e4,
        "n_wo_inst_gen2": n_wo2,
    }


def build_statistics_and_metadata(r2: Path, mec: Path, out: Path) -> None:
    copy_file(r2 / "01_core_data/master/DATASET_METADATA_MASTER_R2.csv", out / "01_PAPER_CORE/DATASET_METADATA/DATASET_METADATA_FINAL.csv")
    stats_files = [
        ("E1", r2 / "04_statistics/E1_FINAL_STATISTICS.csv", True, "E1_R2_FINAL_SEALED"),
        ("E2", r2 / "04_statistics/E2_FINAL_STATISTICS.csv", True, "E2_TRAFFIC_FORMAL"),
        ("E3", r2 / "04_statistics/E3_FINAL_STATISTICS.csv", True, "E3_FORMAL"),
        ("E3_HOLM", r2 / "04_statistics/E3_FORMAL_HOLM_RESULTS.csv", True, "E3_primary_RMSE_Holm"),
        ("E4", r2 / "04_statistics/E4_FINAL_STATISTICS_R2.csv", True, "E4_R2_rebuilt_Holm"),
        ("E4_OLD", r2 / "04_statistics/E4_FINAL_STATISTICS.csv", False, "pre-R2 superseded"),
    ]
    rows = []
    for key, path, eligible, version in stats_files:
        if not path.is_file():
            continue
        df = pd.read_csv(path)
        for _, r in df.iterrows():
            rec = {k: r.get(k, "") for k in df.columns}
            rec["stat_key"] = key
            rec["version"] = version
            rec["generation"] = rec.get("evidence_generation", rec.get("generation", N_A))
            rec["paper_eligible"] = eligible
            rec["superseded_by"] = "E4_FINAL_STATISTICS_R2.csv" if key == "E4_OLD" else ""
            rec["source_file"] = str(path.as_posix())
            rec["test"] = rec.get("test", rec.get("family", "sealed"))
            rec["Holm_family"] = rec.get("holm_family", rec.get("family", rec.get("family_id", "")))
            rec["metric"] = rec.get("metric", rec.get("primary_metric", ""))
            rec["dataset"] = rec.get("dataset", rec.get("Dataset", ""))
            rec["comparison"] = rec.get("comparison", rec.get("component", rec.get("method", "")))
            rows.append(rec)
    write_csv(out / "01_PAPER_CORE/STATISTICS/FINAL_STATISTICS_MASTER.csv", rows)
    cfg = pd.read_csv(r2 / "05_provenance/FINAL_CONFIG_REGISTRY_R2.csv")
    cfg_rows = []
    for _, r in cfg.iterrows():
        cfg_rows.append(
            {
                "round": r.get("round"),
                "dataset": r.get("dataset"),
                "method": r.get("method_or_configuration"),
                "scenario": r.get("scenario"),
                "seed_policy": r.get("seed_set"),
                "source_revision": r.get("source_revision"),
                "config_hash": r.get("config_hash"),
                "resolved_config_hash": r.get("resolved_config_hash"),
                "preprocessing_hash": r.get("preprocessing_hash"),
                "h(i)": r.get("target_h_definition"),
                "s(i)": r.get("opportunity_stratum_s_definition"),
                "EventTrace_policy": r.get("EventTrace_policy"),
                "lambda_group": r.get("lambda_group"),
                "lambda_beta": r.get("lambda_beta"),
                "lambda_v": r.get("lambda_v"),
                "lambda_s": r.get("lambda_s"),
                "P2_policy": r.get("P2_solver_policy"),
                "q_policy": r.get("q_policy"),
                "debt_policy": r.get("debt_policy"),
                "paper_eligibility": r.get("paper_role"),
            }
        )
    write_csv(out / "13_CONFIGS/FINAL_CONFIG_MASTER.csv", cfg_rows)
    write_json(
        out / "14_SOURCE_PROVENANCE/FINAL_H_S_SEMANTICS.json",
        {
            "h_equals_s": False,
            "SensorScope_UAir_h": "four UTC time-of-day groups H1–H4; train-split mass; no test labels",
            "SensorScope_UAir_s": "spatial_id × four time blocks × weekday/weekend",
            "authority": "paper_ready_r2 + manuscript_evidence_closure_r1",
        },
    )
    hs_md = (mec / "00_audit/FINAL_H_S_SEMANTICS_FOR_MANUSCRIPT.md")
    if hs_md.is_file():
        copy_file(hs_md, out / "14_SOURCE_PROVENANCE/FINAL_H_S_SEMANTICS.md")
    else:
        (out / "14_SOURCE_PROVENANCE/FINAL_H_S_SEMANTICS.md").write_text(
            "# Final h(i)/s(i)\n\nh ≠ s. SensorScope/U-Air h(i) is four UTC TOD groups; s(i) is spatial × time-block × weekday.\n",
            encoding="utf-8",
        )

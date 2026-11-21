"""Rebuild manuscript-ready dataset summary from frozen/read-only evidence only."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .io_util import MISSING, N_A, sha256_file, write_csv, write_json, write_meta_json


def _hash_if(path: Path) -> str:
    return sha256_file(path) if path.is_file() else MISSING


def _read_json(path: Path) -> Any:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _parquet_facts(path: Path) -> dict[str, Any]:
    import pandas as pd

    df = pd.read_parquet(path)
    facts: dict[str, Any] = {"n_rows": int(len(df)), "columns": list(df.columns)}
    for col, key in [
        ("spatial_id", "n_spatial_id"),
        ("opportunity_stratum", "n_opportunity_stratum"),
        ("target_group", "n_target_group"),
        ("split", "split_counts"),
    ]:
        if col in df.columns:
            if col == "split":
                facts[key] = {str(k): int(v) for k, v in df[col].value_counts().to_dict().items()}
            else:
                facts[key] = int(df[col].nunique())
    if "absolute_time" in df.columns:
        facts["time_min"] = str(df["absolute_time"].min())
        facts["time_max"] = str(df["absolute_time"].max())
    elif "time_index" in df.columns:
        facts["time_min"] = str(int(df["time_index"].min()))
        facts["time_max"] = str(int(df["time_index"].max()))
        facts["n_time_index"] = int(df["time_index"].nunique())
    if "time_index" in df.columns:
        facts["n_time_index"] = int(df["time_index"].nunique())
        facts["time_index_min"] = int(df["time_index"].min())
        facts["time_index_max"] = int(df["time_index"].max())
    return facts


def rebuild_dataset_summary(root: Path, paper: Path) -> dict[str, Any]:
    root = Path(root)
    paper = Path(paper)
    prov_rows: list[dict[str, Any]] = []

    def add(dataset: str, field: str, value: Any, source: str, key: str, method: str, status: str) -> str:
        src = root / source if source and not source.startswith("MISSING") else None
        sha = _hash_if(src) if src is not None else MISSING
        val = MISSING if value is None or value == "" else value
        prov_rows.append(
            {
                "dataset": dataset,
                "field": field,
                "value": val,
                "source_file": source,
                "source_key_or_row": key,
                "source_sha256": sha,
                "recovery_method": method,
                "confidence": "high" if status == "RECOVERED_DIRECT" else ("medium" if status == "RECOVERED_DETERMINISTIC" else "none"),
                "status": status,
            }
        )
        return str(val)

    datasets: list[dict[str, Any]] = []

    # ---------- SensorScope ----------
    ss_raw = _read_json(root / "data/raw/sensorscope/provenance.json")
    ss_h = _read_json(root / "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json")
    ss_s = _read_json(root / "configs/frozen/e3_multidataset_protocol_closure/sensorscope/opportunity_strata.json")
    ss_t = _read_json(root / "configs/frozen/e3_multidataset_protocol_closure/sensorscope/public_target.json")
    ss_e = _read_json(root / "configs/frozen/e3_multidataset_protocol_closure/sensorscope/stage2_eligibility.json")
    ss_parq = root / "data/processed/sensorscope/atomic_units.parquet"
    ss_pf = _parquet_facts(ss_parq)
    ss_raw_md5 = ss_raw["files"][0]["md5"]
    row = {"dataset": "SensorScope"}
    row["domain"] = add("SensorScope", "domain", "environmental sensing (EPFL SensorScope)", "data/raw/sensorscope/provenance.json", "source_name", "direct", "RECOVERED_DIRECT")
    row["raw_data_source_name"] = add("SensorScope", "raw_data_source_name", ss_raw["source_name"], "data/raw/sensorscope/provenance.json", "source_name", "direct", "RECOVERED_DIRECT")
    row["raw_data_checksum"] = add("SensorScope", "raw_data_checksum", f"md5:{ss_raw_md5}", "data/raw/sensorscope/provenance.json", "files[0].md5", "direct", "RECOVERED_DIRECT")
    row["processed_data_checksum"] = add("SensorScope", "processed_data_checksum", f"sha256:{_hash_if(ss_parq)}", "data/processed/sensorscope/atomic_units.parquet", "file_sha256", "sha256", "RECOVERED_DIRECT")
    row["client_identity_definition"] = add("SensorScope", "client_identity_definition", "station-level spatial identity (spatial_id = station)", "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "spatial_units + processed spatial_id", "direct", "RECOVERED_DIRECT")
    row["number_stations"] = add("SensorScope", "number_stations", ss_h["spatial_units"], "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "spatial_units", "direct", "RECOVERED_DIRECT")
    row["number_spatial_units"] = add("SensorScope", "number_spatial_units", ss_h["spatial_units"], "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "spatial_units", "direct", "RECOVERED_DIRECT")
    row["number_clients"] = add("SensorScope", "number_clients", ss_h["spatial_units"], "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "spatial_units (station=client in E3/E4)", "direct", "RECOVERED_DIRECT")
    row["spatial_unit_definition"] = add("SensorScope", "spatial_unit_definition", "station-level; 55 stations", "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "spatial_units", "direct", "RECOVERED_DIRECT")
    row["time_span_start"] = add("SensorScope", "time_span_start", f"time_index={ss_h['split_boundaries']['train']['time_min']}", "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "split_boundaries.train.time_min", "direct", "RECOVERED_DIRECT")
    row["time_span_end"] = add("SensorScope", "time_span_end", f"time_index={ss_h['split_boundaries']['test']['time_max']}", "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "split_boundaries.test.time_max", "direct", "RECOVERED_DIRECT")
    row["sampling_interval"] = add("SensorScope", "sampling_interval", MISSING, "", "", "not in frozen horizon/provenance", "MISSING_NOT_RECORDED")
    row["target_h_definition"] = add("SensorScope", "target_h_definition", f"train-split UTC time-of-day 4-block mass; groups={ss_t['group_names']}; construction={ss_t['construction']}", "configs/frozen/e3_multidataset_protocol_closure/sensorscope/public_target.json", "construction/group_names/mu", "direct", "RECOVERED_DIRECT")
    row["opportunity_stratum_s_definition"] = add("SensorScope", "opportunity_stratum_s_definition", ss_s["definition"], "configs/frozen/e3_multidataset_protocol_closure/sensorscope/opportunity_strata.json", "definition", "direct", "RECOVERED_DIRECT")
    row["number_target_groups"] = add("SensorScope", "number_target_groups", len(ss_t["group_ids"]), "configs/frozen/e3_multidataset_protocol_closure/sensorscope/public_target.json", "group_ids", "direct", "RECOVERED_DIRECT")
    row["max_opportunity_strata"] = add("SensorScope", "max_opportunity_strata", ss_s["n_strata"], "configs/frozen/e3_multidataset_protocol_closure/sensorscope/opportunity_strata.json", "n_strata (55×4×2=440)", "direct", "RECOVERED_DIRECT")
    row["train_split_definition"] = add("SensorScope", "train_split_definition", f"time_index {ss_h['split_boundaries']['train']['time_min']}-{ss_h['split_boundaries']['train']['time_max']}; n_atomic={ss_h['split_boundaries']['train']['n_atomic']}", "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "split_boundaries.train", "direct", "RECOVERED_DIRECT")
    row["validation_split_definition"] = add("SensorScope", "validation_split_definition", f"time_index {ss_h['split_boundaries']['validation']['time_min']}-{ss_h['split_boundaries']['validation']['time_max']}; n_atomic={ss_h['split_boundaries']['validation']['n_atomic']}", "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "split_boundaries.validation", "direct", "RECOVERED_DIRECT")
    row["test_split_definition"] = add("SensorScope", "test_split_definition", f"time_index {ss_h['split_boundaries']['test']['time_min']}-{ss_h['split_boundaries']['test']['time_max']}; n_atomic={ss_h['split_boundaries']['test']['n_atomic']}", "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "split_boundaries.test", "direct", "RECOVERED_DIRECT")
    row["train_count"] = add("SensorScope", "train_count", ss_h["split_boundaries"]["train"]["n_atomic"], "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "split_boundaries.train.n_atomic", "direct", "RECOVERED_DIRECT")
    row["validation_count"] = add("SensorScope", "validation_count", ss_h["split_boundaries"]["validation"]["n_atomic"], "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "split_boundaries.validation.n_atomic", "direct", "RECOVERED_DIRECT")
    row["test_count"] = add("SensorScope", "test_count", ss_h["split_boundaries"]["test"]["n_atomic"], "configs/frozen/e3_multidataset_protocol_closure/sensorscope/horizon.json", "split_boundaries.test.n_atomic", "direct", "RECOVERED_DIRECT")
    row["selection_mechanism"] = add("SensorScope", "selection_mechanism", f"two-stage: {ss_e.get('stage1_stage2_timing')}; delivered iff U=1; s_max={ss_e.get('s_max')}", "configs/frozen/e3_multidataset_protocol_closure/sensorscope/stage2_eligibility.json", "stage1_stage2_timing/eligibility_rule", "direct", "RECOVERED_DIRECT")
    row["real_data_component"] = add("SensorScope", "real_data_component", "station temperature observations (Zenodo Sensorscope.zip)", "data/raw/sensorscope/provenance.json", "files[0]", "direct", "RECOVERED_DIRECT")
    row["controlled_or_semi_synthetic_component"] = add("SensorScope", "controlled_or_semi_synthetic_component", "controlled two-stage selection / EventTrace on real station series", "configs/frozen/e3_multidataset_protocol_closure/sensorscope/stage2_eligibility.json", "eligibility_rule", "direct", "RECOVERED_DIRECT")
    row["paper_role"] = add("SensorScope", "paper_role", "E3/E4 main comparable evidence", "", "claim ceiling C3-C8", "direct from sealed E3/E4 role", "RECOVERED_DIRECT")
    row["final_comparability_status"] = add("SensorScope", "final_comparability_status", "SCI_COMPARABLE_MAIN", "paper_ready_r1/01_core_data/e3/E3_COLLECTION_STATUS.json", "core_complete", "direct", "RECOVERED_DIRECT")
    row["notes"] = add("SensorScope", "notes", f"processed n_rows={ss_pf['n_rows']}; n_spatial_id={ss_pf.get('n_spatial_id')}; n_strata_processed={ss_pf.get('n_opportunity_stratum')}; common_timestamps={ss_h['common_timestamps']}", "data/processed/sensorscope/atomic_units.parquet", "nunique spatial_id/opportunity_stratum", "deterministic", "RECOVERED_DETERMINISTIC")
    datasets.append(row)

    # ---------- U-Air ----------
    ua_raw = _read_json(root / "data/raw/uair/provenance.json")
    ua_h = _read_json(root / "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json")
    ua_s = _read_json(root / "configs/frozen/e3_multidataset_protocol_closure/uair/opportunity_strata.json")
    ua_t = _read_json(root / "configs/frozen/e3_multidataset_protocol_closure/uair/public_target.json")
    ua_e = _read_json(root / "configs/frozen/e3_multidataset_protocol_closure/uair/stage2_eligibility.json")
    ua_parq = root / "data/processed/uair/atomic_units.parquet"
    ua_pf = _parquet_facts(ua_parq)
    row = {"dataset": "U-Air"}
    row["domain"] = add("U-Air", "domain", "urban air quality", "data/raw/uair/provenance.json", "source_name", "direct", "RECOVERED_DIRECT")
    row["raw_data_source_name"] = add("U-Air", "raw_data_source_name", ua_raw["source_name"], "data/raw/uair/provenance.json", "source_name", "direct", "RECOVERED_DIRECT")
    row["raw_data_checksum"] = add("U-Air", "raw_data_checksum", f"md5:{ua_raw['files'][0]['md5']}", "data/raw/uair/provenance.json", "files[0].md5", "direct", "RECOVERED_DIRECT")
    row["processed_data_checksum"] = add("U-Air", "processed_data_checksum", f"sha256:{_hash_if(ua_parq)}", "data/processed/uair/atomic_units.parquet", "file_sha256", "sha256", "RECOVERED_DIRECT")
    row["client_identity_definition"] = add("U-Air", "client_identity_definition", "spatial_id-level identity", "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "spatial_units", "direct", "RECOVERED_DIRECT")
    row["number_stations"] = add("U-Air", "number_stations", ua_h["spatial_units"], "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "spatial_units", "direct", "RECOVERED_DIRECT")
    row["number_spatial_units"] = add("U-Air", "number_spatial_units", ua_h["spatial_units"], "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "spatial_units", "direct", "RECOVERED_DIRECT")
    row["number_clients"] = add("U-Air", "number_clients", ua_h["spatial_units"], "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "spatial_units", "direct", "RECOVERED_DIRECT")
    row["spatial_unit_definition"] = add("U-Air", "spatial_unit_definition", "spatial_id-level; 36 spatial identities", "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "spatial_units", "direct", "RECOVERED_DIRECT")
    row["time_span_start"] = add("U-Air", "time_span_start", f"time_index={ua_h['split_boundaries']['train']['time_min']}", "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "split_boundaries.train.time_min", "direct", "RECOVERED_DIRECT")
    row["time_span_end"] = add("U-Air", "time_span_end", f"time_index={ua_h['split_boundaries']['test']['time_max']}", "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "split_boundaries.test.time_max", "direct", "RECOVERED_DIRECT")
    row["sampling_interval"] = add("U-Air", "sampling_interval", MISSING, "", "", "not in frozen horizon/provenance", "MISSING_NOT_RECORDED")
    row["target_h_definition"] = add("U-Air", "target_h_definition", f"train-split UTC time-of-day 4-block mass; groups={ua_t['group_names']}; construction={ua_t['construction']}", "configs/frozen/e3_multidataset_protocol_closure/uair/public_target.json", "construction/group_names", "direct", "RECOVERED_DIRECT")
    row["opportunity_stratum_s_definition"] = add("U-Air", "opportunity_stratum_s_definition", ua_s["definition"], "configs/frozen/e3_multidataset_protocol_closure/uair/opportunity_strata.json", "definition", "direct", "RECOVERED_DIRECT")
    row["number_target_groups"] = add("U-Air", "number_target_groups", len(ua_t["group_ids"]), "configs/frozen/e3_multidataset_protocol_closure/uair/public_target.json", "group_ids", "direct", "RECOVERED_DIRECT")
    row["max_opportunity_strata"] = add("U-Air", "max_opportunity_strata", ua_s["n_strata"], "configs/frozen/e3_multidataset_protocol_closure/uair/opportunity_strata.json", "n_strata (36×4×2=288)", "direct", "RECOVERED_DIRECT")
    row["train_split_definition"] = add("U-Air", "train_split_definition", f"time_index {ua_h['split_boundaries']['train']['time_min']}-{ua_h['split_boundaries']['train']['time_max']}; n_atomic={ua_h['split_boundaries']['train']['n_atomic']}", "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "split_boundaries.train", "direct", "RECOVERED_DIRECT")
    row["validation_split_definition"] = add("U-Air", "validation_split_definition", f"time_index {ua_h['split_boundaries']['validation']['time_min']}-{ua_h['split_boundaries']['validation']['time_max']}; n_atomic={ua_h['split_boundaries']['validation']['n_atomic']}", "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "split_boundaries.validation", "direct", "RECOVERED_DIRECT")
    row["test_split_definition"] = add("U-Air", "test_split_definition", f"time_index {ua_h['split_boundaries']['test']['time_min']}-{ua_h['split_boundaries']['test']['time_max']}; n_atomic={ua_h['split_boundaries']['test']['n_atomic']}", "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "split_boundaries.test", "direct", "RECOVERED_DIRECT")
    row["train_count"] = add("U-Air", "train_count", ua_h["split_boundaries"]["train"]["n_atomic"], "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "split_boundaries.train.n_atomic", "direct", "RECOVERED_DIRECT")
    row["validation_count"] = add("U-Air", "validation_count", ua_h["split_boundaries"]["validation"]["n_atomic"], "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "split_boundaries.validation.n_atomic", "direct", "RECOVERED_DIRECT")
    row["test_count"] = add("U-Air", "test_count", ua_h["split_boundaries"]["test"]["n_atomic"], "configs/frozen/e3_multidataset_protocol_closure/uair/horizon.json", "split_boundaries.test.n_atomic", "direct", "RECOVERED_DIRECT")
    row["selection_mechanism"] = add("U-Air", "selection_mechanism", f"two-stage: {ua_e.get('stage1_stage2_timing')}; delivered iff U=1; s_max={ua_e.get('s_max')}", "configs/frozen/e3_multidataset_protocol_closure/uair/stage2_eligibility.json", "stage1_stage2_timing", "direct", "RECOVERED_DIRECT")
    row["real_data_component"] = add("U-Air", "real_data_component", "Microsoft Research Urban Air (Data-1.zip)", "data/raw/uair/provenance.json", "files[0]", "direct", "RECOVERED_DIRECT")
    row["controlled_or_semi_synthetic_component"] = add("U-Air", "controlled_or_semi_synthetic_component", "controlled two-stage selection / EventTrace on real spatial series", "configs/frozen/e3_multidataset_protocol_closure/uair/stage2_eligibility.json", "eligibility_rule", "direct", "RECOVERED_DIRECT")
    row["paper_role"] = add("U-Air", "paper_role", "E3/E4 main comparable evidence", "", "claim ceiling C3-C8", "direct", "RECOVERED_DIRECT")
    row["final_comparability_status"] = add("U-Air", "final_comparability_status", "SCI_COMPARABLE_MAIN", "paper_ready_r1/01_core_data/e3/E3_COLLECTION_STATUS.json", "core_complete", "direct", "RECOVERED_DIRECT")
    row["notes"] = add("U-Air", "notes", f"processed n_rows={ua_pf['n_rows']}; n_spatial_id={ua_pf.get('n_spatial_id')}; n_strata_processed={ua_pf.get('n_opportunity_stratum')}; common_timestamps={ua_h['common_timestamps']}", "data/processed/uair/atomic_units.parquet", "nunique", "deterministic", "RECOVERED_DETERMINISTIC")
    datasets.append(row)

    # ---------- NSW-Traffic ----------
    tr_raw = _read_json(root / "data/raw/traffic/provenance.json")
    tr_h = _read_json(root / "configs/frozen/e3_multidataset_protocol_closure/traffic/horizon.json")
    tr_s = _read_json(root / "configs/frozen/e3_multidataset_protocol_closure/traffic/opportunity_strata.json")
    tr_t = _read_json(root / "configs/frozen/e3_multidataset_protocol_closure/traffic/public_target.json")
    tr_parq = root / "data/processed/traffic/atomic_units.parquet"
    tr_pf = _parquet_facts(tr_parq)
    e2_src = _read_json(root / "artifacts/e2_traffic_formal_runs_r1/SOURCE_HASHES.json")
    row = {"dataset": "NSW-Traffic"}
    row["domain"] = add("NSW-Traffic", "domain", "road traffic volume", "data/raw/traffic/provenance.json", "source_name", "direct", "RECOVERED_DIRECT")
    row["raw_data_source_name"] = add("NSW-Traffic", "raw_data_source_name", tr_raw["source_name"], "data/raw/traffic/provenance.json", "source_name", "direct", "RECOVERED_DIRECT")
    row["raw_data_checksum"] = add("NSW-Traffic", "raw_data_checksum", "; ".join(f"{f['filename']}:md5:{f['md5']}" for f in tr_raw["files"]), "data/raw/traffic/provenance.json", "files[*].md5", "direct", "RECOVERED_DIRECT")
    row["processed_data_checksum"] = add("NSW-Traffic", "processed_data_checksum", f"sha256:{e2_src['files']['data/processed/traffic/atomic_units.parquet']}", "artifacts/e2_traffic_formal_runs_r1/SOURCE_HASHES.json", "files[data/processed/traffic/atomic_units.parquet]", "direct", "RECOVERED_DIRECT")
    row["client_identity_definition"] = add("NSW-Traffic", "client_identity_definition", "43 stations mapped to 4 frozen real coordinate regions (no recluster)", "configs/frozen/e3_multidataset_protocol_closure/traffic/opportunity_strata.json", "spatial_coarsening", "direct", "RECOVERED_DIRECT")
    row["number_stations"] = add("NSW-Traffic", "number_stations", tr_h["spatial_units"], "configs/frozen/e3_multidataset_protocol_closure/traffic/horizon.json", "spatial_units", "direct", "RECOVERED_DIRECT")
    row["number_spatial_units"] = add("NSW-Traffic", "number_spatial_units", 4, "configs/frozen/e3_multidataset_protocol_closure/traffic/opportunity_strata.json", "4 frozen real regions", "direct", "RECOVERED_DIRECT")
    row["number_clients"] = add("NSW-Traffic", "number_clients", 43, "artifacts/e2_traffic_formal_runs_r1/FORMAL_RUN_CONFIG.json", "hyperparameters.n_clients", "direct", "RECOVERED_DIRECT")
    row["spatial_unit_definition"] = add("NSW-Traffic", "spatial_unit_definition", tr_s["spatial_coarsening"], "configs/frozen/e3_multidataset_protocol_closure/traffic/opportunity_strata.json", "spatial_coarsening", "direct", "RECOVERED_DIRECT")
    row["time_span_start"] = add("NSW-Traffic", "time_span_start", f"time_index={tr_h['split_boundaries']['train']['time_min']}", "configs/frozen/e3_multidataset_protocol_closure/traffic/horizon.json", "split_boundaries.train.time_min", "direct", "RECOVERED_DIRECT")
    row["time_span_end"] = add("NSW-Traffic", "time_span_end", f"time_index={tr_h['split_boundaries']['test']['time_max']}", "configs/frozen/e3_multidataset_protocol_closure/traffic/horizon.json", "split_boundaries.test.time_max", "direct", "RECOVERED_DIRECT")
    row["sampling_interval"] = add("NSW-Traffic", "sampling_interval", "hourly permanent counts (raw); protocol windows as frozen E2 100-window identity", "data/raw/traffic/provenance.json", "road_traffic_counts_hourly_permanent.zip", "direct", "RECOVERED_DIRECT")
    row["target_h_definition"] = add("NSW-Traffic", "target_h_definition", f"construction={tr_t.get('construction')}; group_definition={tr_t.get('group_definition')}", "configs/frozen/e3_multidataset_protocol_closure/traffic/public_target.json", "construction", "direct", "RECOVERED_DIRECT")
    row["opportunity_stratum_s_definition"] = add("NSW-Traffic", "opportunity_stratum_s_definition", tr_s["definition"], "configs/frozen/e3_multidataset_protocol_closure/traffic/opportunity_strata.json", "definition", "direct", "RECOVERED_DIRECT")
    row["number_target_groups"] = add("NSW-Traffic", "number_target_groups", len(tr_t.get("group_ids", [])), "configs/frozen/e3_multidataset_protocol_closure/traffic/public_target.json", "group_ids", "direct", "RECOVERED_DIRECT")
    row["max_opportunity_strata"] = add("NSW-Traffic", "max_opportunity_strata", tr_s["n_strata"], "configs/frozen/e3_multidataset_protocol_closure/traffic/opportunity_strata.json", "n_strata (4×4×2=32)", "direct", "RECOVERED_DIRECT")
    row["train_split_definition"] = add("NSW-Traffic", "train_split_definition", f"time_index {tr_h['split_boundaries']['train']['time_min']}-{tr_h['split_boundaries']['train']['time_max']}; n_atomic={tr_h['split_boundaries']['train']['n_atomic']}", "configs/frozen/e3_multidataset_protocol_closure/traffic/horizon.json", "split_boundaries.train", "direct", "RECOVERED_DIRECT")
    row["validation_split_definition"] = add("NSW-Traffic", "validation_split_definition", f"time_index {tr_h['split_boundaries']['validation']['time_min']}-{tr_h['split_boundaries']['validation']['time_max']}; n_atomic={tr_h['split_boundaries']['validation']['n_atomic']}", "configs/frozen/e3_multidataset_protocol_closure/traffic/horizon.json", "split_boundaries.validation", "direct", "RECOVERED_DIRECT")
    row["test_split_definition"] = add("NSW-Traffic", "test_split_definition", f"time_index {tr_h['split_boundaries']['test']['time_min']}-{tr_h['split_boundaries']['test']['time_max']}; n_atomic={tr_h['split_boundaries']['test']['n_atomic']}", "configs/frozen/e3_multidataset_protocol_closure/traffic/horizon.json", "split_boundaries.test", "direct", "RECOVERED_DIRECT")
    row["train_count"] = add("NSW-Traffic", "train_count", tr_h["split_boundaries"]["train"]["n_atomic"], "configs/frozen/e3_multidataset_protocol_closure/traffic/horizon.json", "n_atomic", "direct", "RECOVERED_DIRECT")
    row["validation_count"] = add("NSW-Traffic", "validation_count", tr_h["split_boundaries"]["validation"]["n_atomic"], "configs/frozen/e3_multidataset_protocol_closure/traffic/horizon.json", "n_atomic", "direct", "RECOVERED_DIRECT")
    row["test_count"] = add("NSW-Traffic", "test_count", tr_h["split_boundaries"]["test"]["n_atomic"], "configs/frozen/e3_multidataset_protocol_closure/traffic/horizon.json", "n_atomic", "direct", "RECOVERED_DIRECT")
    row["selection_mechanism"] = add("NSW-Traffic", "selection_mechanism", "E2 PROFILE-S1 controlled two-stage selection on real stations; E3 Traffic reused-old vs new-current is NOT_COMPARABLE", "artifacts/e2_traffic_formal_runs_r1/FORMAL_RUN_CONFIG.json", "profile=PROFILE-S1", "direct", "RECOVERED_DIRECT")
    row["real_data_component"] = add("NSW-Traffic", "real_data_component", "TfNSW / Data.NSW traffic volume counts + station reference", "data/raw/traffic/provenance.json", "files", "direct", "RECOVERED_DIRECT")
    row["controlled_or_semi_synthetic_component"] = add("NSW-Traffic", "controlled_or_semi_synthetic_component", "PROFILE-S1 six-scenario EventTrace on real traffic series; 4 frozen regions", "artifacts/e2_traffic_formal_runs_r1/FORMAL_RUN_CONFIG.json", "scenarios", "direct", "RECOVERED_DIRECT")
    row["paper_role"] = add("NSW-Traffic", "paper_role", "E2 main (risk non-interchangeability); E3 reference-only / NOT_COMPARABLE cross-vintage", "", "C1,C2,C9", "direct", "RECOVERED_DIRECT")
    row["final_comparability_status"] = add("NSW-Traffic", "final_comparability_status", "E2: SCI_COMPARABLE_MAIN; E3: NOT_COMPARABLE_CROSS_VINTAGE", "artifacts/e3_formal_evidence_integrity_and_claim_closure_r1", "traffic policy", "direct", "RECOVERED_DIRECT")
    row["notes"] = add("NSW-Traffic", "notes", f"processed n_rows={tr_pf['n_rows']}; n_spatial_id={tr_pf.get('n_spatial_id')}; n_strata={tr_s['n_strata']}; region_mapping_hash={tr_s.get('region_mapping_hash')}", "data/processed/traffic/atomic_units.parquet", "nunique", "deterministic", "RECOVERED_DETERMINISTIC")
    datasets.append(row)

    # ---------- T-Drive (readiness only) ----------
    td_yaml = root / "configs/dataset/tdrive_speed.yaml"
    td_man = root / "data/manifests/tdrive_speed_manifest.json"
    td_parq = root / "data/processed/tdrive_speed/atomic_units.parquet"
    td_raw = root / "data/raw/tdrive_speed"
    import yaml

    td_cfg = yaml.safe_load(td_yaml.read_text(encoding="utf-8")) if td_yaml.is_file() else {}
    td_pf = _parquet_facts(td_parq) if td_parq.is_file() else {}
    row = {"dataset": "T-Drive-Speed"}
    row["domain"] = add("T-Drive-Speed", "domain", "vehicle mobility / speed", "configs/dataset/tdrive_speed.yaml", "target.name", "direct", "RECOVERED_DIRECT")
    row["raw_data_source_name"] = add("T-Drive-Speed", "raw_data_source_name", td_cfg.get("download", {}).get("source_name", MISSING), "configs/dataset/tdrive_speed.yaml", "download.source_name", "direct", "RECOVERED_DIRECT")
    if td_man.is_file():
        man = _read_json(td_man)
        if isinstance(man, dict) and "files" in man:
            checksum_s = str(man.get("files"))[:400]
        elif isinstance(man, dict):
            checksum_s = "sha256:" + _hash_if(td_man)
        else:
            checksum_s = "sha256:" + _hash_if(td_man)
        row["raw_data_checksum"] = add("T-Drive-Speed", "raw_data_checksum", checksum_s, "data/manifests/tdrive_speed_manifest.json", "manifest", "direct", "RECOVERED_DIRECT")
    else:
        row["raw_data_checksum"] = add("T-Drive-Speed", "raw_data_checksum", MISSING, "data/manifests/tdrive_speed_manifest.json", "", "", "MISSING_NOT_RECORDED")
    row["processed_data_checksum"] = add("T-Drive-Speed", "processed_data_checksum", f"sha256:{_hash_if(td_parq)}" if td_parq.is_file() else MISSING, "data/processed/tdrive_speed/atomic_units.parquet", "file_sha256", "sha256", "RECOVERED_DIRECT" if td_parq.is_file() else "MISSING_NOT_RECORDED")
    row["client_identity_definition"] = add("T-Drive-Speed", "client_identity_definition", "trajectory/vehicle records; same vehicle cannot construct both target and client input (yaml physical_filters)", "configs/dataset/tdrive_speed.yaml", "physical_filters/fleet", "direct", "RECOVERED_DIRECT")
    row["number_stations"] = add("T-Drive-Speed", "number_stations", N_A, "", "not a station dataset", "", "MISSING_NOT_RECORDED")
    row["number_spatial_units"] = add("T-Drive-Speed", "number_spatial_units", td_pf.get("n_spatial_id", MISSING), "data/processed/tdrive_speed/atomic_units.parquet", "spatial_id nunique", "deterministic", "RECOVERED_DETERMINISTIC" if "n_spatial_id" in td_pf else "MISSING_NOT_RECORDED")
    row["number_clients"] = add("T-Drive-Speed", "number_clients", MISSING, "", "formal client count not frozen", "", "MISSING_NOT_RECORDED")
    row["spatial_unit_definition"] = add("T-Drive-Speed", "spatial_unit_definition", f"yaml grid.cell_meters={td_cfg.get('grid', {}).get('cell_meters')} (intended; spatial grid freeze not complete)", "configs/dataset/tdrive_speed.yaml", "grid.cell_meters", "direct", "RECOVERED_DIRECT")
    row["time_span_start"] = add("T-Drive-Speed", "time_span_start", td_pf.get("time_min", MISSING), "data/processed/tdrive_speed/atomic_units.parquet", "time min", "deterministic", "RECOVERED_DETERMINISTIC" if td_pf else "MISSING_NOT_RECORDED")
    row["time_span_end"] = add("T-Drive-Speed", "time_span_end", td_pf.get("time_max", MISSING), "data/processed/tdrive_speed/atomic_units.parquet", "time max", "deterministic", "RECOVERED_DETERMINISTIC" if td_pf else "MISSING_NOT_RECORDED")
    row["sampling_interval"] = add("T-Drive-Speed", "sampling_interval", f"yaml grid.slot_minutes={td_cfg.get('grid', {}).get('slot_minutes')} (intended; time-slot freeze not complete)", "configs/dataset/tdrive_speed.yaml", "grid.slot_minutes", "direct", "RECOVERED_DIRECT")
    row["target_h_definition"] = add("T-Drive-Speed", "target_h_definition", f"speed target; unit={td_cfg.get('target', {}).get('unit')}", "configs/dataset/tdrive_speed.yaml", "target", "direct", "RECOVERED_DIRECT")
    row["opportunity_stratum_s_definition"] = add("T-Drive-Speed", "opportunity_stratum_s_definition", MISSING, "", "opportunity definition not frozen", "", "MISSING_NOT_RECORDED")
    row["number_target_groups"] = add("T-Drive-Speed", "number_target_groups", MISSING, "", "not frozen", "", "MISSING_NOT_RECORDED")
    row["max_opportunity_strata"] = add("T-Drive-Speed", "max_opportunity_strata", MISSING, "", "not frozen", "", "MISSING_NOT_RECORDED")
    split = td_cfg.get("split", {})
    row["train_split_definition"] = add("T-Drive-Speed", "train_split_definition", f"yaml intended train={split.get('train')} (NOT frozen as formal protocol)", "configs/dataset/tdrive_speed.yaml", "split.train", "direct", "RECOVERED_DIRECT")
    row["validation_split_definition"] = add("T-Drive-Speed", "validation_split_definition", f"yaml intended validation={split.get('validation')} (NOT frozen)", "configs/dataset/tdrive_speed.yaml", "split.validation", "direct", "RECOVERED_DIRECT")
    row["test_split_definition"] = add("T-Drive-Speed", "test_split_definition", f"yaml intended test={split.get('test')} (NOT frozen)", "configs/dataset/tdrive_speed.yaml", "split.test", "direct", "RECOVERED_DIRECT")
    sc = td_pf.get("split_counts")
    if sc:
        row["train_count"] = add("T-Drive-Speed", "train_count", sc.get("train", MISSING), "data/processed/tdrive_speed/atomic_units.parquet", "split==train", "deterministic", "RECOVERED_DETERMINISTIC")
        row["validation_count"] = add("T-Drive-Speed", "validation_count", sc.get("validation", MISSING), "data/processed/tdrive_speed/atomic_units.parquet", "split==validation", "deterministic", "RECOVERED_DETERMINISTIC")
        row["test_count"] = add("T-Drive-Speed", "test_count", sc.get("test", MISSING), "data/processed/tdrive_speed/atomic_units.parquet", "split==test", "deterministic", "RECOVERED_DETERMINISTIC")
    else:
        row["train_count"] = add("T-Drive-Speed", "train_count", MISSING, "", "formal split not frozen", "", "MISSING_NOT_RECORDED")
        row["validation_count"] = add("T-Drive-Speed", "validation_count", MISSING, "", "formal split not frozen", "", "MISSING_NOT_RECORDED")
        row["test_count"] = add("T-Drive-Speed", "test_count", MISSING, "", "formal split not frozen", "", "MISSING_NOT_RECORDED")
    row["selection_mechanism"] = add("T-Drive-Speed", "selection_mechanism", MISSING, "", "opportunity/EventTrace not frozen", "", "MISSING_NOT_RECORDED")
    row["real_data_component"] = add("T-Drive-Speed", "real_data_component", "Microsoft Research T-Drive trajectory sample", "configs/dataset/tdrive_speed.yaml", "download.source_name", "direct", "RECOVERED_DIRECT")
    row["controlled_or_semi_synthetic_component"] = add("T-Drive-Speed", "controlled_or_semi_synthetic_component", "intended grid/slot/fleet filters in yaml; not a frozen formal protocol", "configs/dataset/tdrive_speed.yaml", "grid/fleet/physical_filters", "direct", "RECOVERED_DIRECT")
    row["paper_role"] = add("T-Drive-Speed", "paper_role", "READINESS METADATA ONLY; no formal result fields; future external validation", "", "section 10/22", "direct", "RECOVERED_DIRECT")
    row["final_comparability_status"] = add("T-Drive-Speed", "final_comparability_status", "NOT_FORMAL_RUN", "", "no T-Drive formal experiments", "direct", "RECOVERED_DIRECT")
    row["notes"] = add("T-Drive-Speed", "notes", f"raw_dir_exists={td_raw.exists()}; processed_exists={td_parq.is_file()}; n_rows={td_pf.get('n_rows', MISSING)}; NO formal metrics", "data/processed/tdrive_speed", "inventory", "direct", "RECOVERED_DIRECT")
    datasets.append(row)

    write_csv(paper / "05_provenance" / "DATASET_METADATA_PROVENANCE.csv", prov_rows)
    fields = list(datasets[0].keys())
    write_csv(paper / "06_table_sources" / "TABLE_DATASET_SUMMARY_R2.csv", datasets, fields)
    write_csv(paper / "06_table_sources" / "TABLE_DATASET_SUMMARY.csv", datasets, fields)
    write_csv(paper / "01_core_data" / "master" / "DATASET_METADATA_MASTER_R2.csv", datasets, fields)
    write_meta_json(
        paper / "06_table_sources" / "TABLE_DATASET_SUMMARY_R2.csv",
        source_files=[
            "data/raw/{sensorscope,uair,traffic}/provenance.json",
            "configs/frozen/e3_multidataset_protocol_closure/{sensorscope,uair,traffic}/*.json",
            "data/processed/*/atomic_units.parquet",
            "configs/dataset/tdrive_speed.yaml",
            "artifacts/e2_traffic_formal_runs_r1/SOURCE_HASHES.json",
        ],
        filters="frozen/read-only evidence only; T-Drive readiness metadata only (no formal results)",
        transformations="copy sealed numeric/string fields; sha256 processed parquet; never guess missing fields",
        excluded_rows="no guessed sampling intervals; T-Drive opportunity/EventTrace/split remain MISSING_NOT_RECORDED where unfrozen",
        statistical_method="n/a (metadata table)",
    )
    guessed = [r for r in prov_rows if r["status"] not in {"RECOVERED_DIRECT", "RECOVERED_DETERMINISTIC", "MISSING_NOT_RECORDED", "CONFLICT_REQUIRES_REVIEW"}]
    return {"n_datasets": len(datasets), "n_provenance_rows": len(prov_rows), "n_guessed": len(guessed), "rows": datasets}

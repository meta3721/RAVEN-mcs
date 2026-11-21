"""Execute an E4 ablation using a pre-existing E3 EventTrace."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .constants import ABLATIONS, DATASETS, FORMAL_SEEDS, SCENARIO
from .matrix import logical_run_id
from raven_mcs.e3.canary.dataset_load import load_paper_dataset, load_spatial_to_client
from raven_mcs.e3.real_runner.runner import run_e3_real
from raven_mcs.utils.serialization import dump_json

def run_logical(*, root: Path, art: Path, dataset: str, method: str, seed: int,
                freeze: dict[str, Any] | None = None, force: bool = False,
                eventtrace_dir: Path | None = None,
                accepted_marker_name: str = "FORMAL_ACCEPTED.json",
                allow_nonformal_seed: bool = False) -> dict[str, Any]:
    if dataset not in DATASETS or method not in ABLATIONS:
        raise ValueError("E4 permits only sensorscope/uair and canonical ablations")
    if not allow_nonformal_seed and int(seed) not in FORMAL_SEEDS:
        raise ValueError(f"Formal E4 seed must be in {FORMAL_SEEDS[0]}..{FORMAL_SEEDS[-1]}")
    run_dir = Path(art) / "runs" / dataset / method / f"seed{seed}"
    marker = run_dir / accepted_marker_name
    if marker.is_file() and not force:
        return {"status": "ALREADY_ACCEPTED", **json.loads(marker.read_text(encoding="utf-8"))}
    if eventtrace_dir is None:
        eventtrace = Path(root) / "artifacts/e3_formal_runs_r1/eventtraces" / dataset / f"seed{seed}" / "training_eventtrace"
    else:
        eventtrace = Path(eventtrace_dir)
    if not (eventtrace / "trace_identity.json").is_file():
        raise FileNotFoundError(f"EventTrace unavailable: {eventtrace}")
    result = run_e3_real(
        root=Path(root), run_dir=run_dir, dataset=load_paper_dataset(Path(root), dataset),
        method=method, seed=int(seed), eventtrace_dir=eventtrace,
        spatial_to_client=load_spatial_to_client(Path(root), dataset), dataset_name=dataset,
        scenario=SCENARIO, local_steps=2, ledger_path=run_dir / "ledger.jsonl",
        source_identity={"source_manifest_hash": (freeze or {}).get("source_manifest_hash"),
                         "git_commit": (freeze or {}).get("git_commit")},
    )
    accepted = result.get("status") == "REAL_PATH_EXECUTED"
    row = {"logical_run_id": logical_run_id(dataset, method, seed), "dataset": dataset,
           "method": method, "seed": int(seed), "scenario": SCENARIO,
           "accepted": accepted, "execution_status": result.get("status"),
           "completed_windows": result.get("completed_windows"),
           "finished_utc": datetime.now(timezone.utc).isoformat()}
    dump_json(row, run_dir / "e4_attempt_result.json")
    if accepted:
        dump_json({**row, "paper_evidence": not allow_nonformal_seed}, marker)
    return row

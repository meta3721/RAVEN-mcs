from pathlib import Path
import json

from raven_mcs.experiments.sag_runtime import eventtrace_dir

ROOT = Path(__file__).resolve().parents[2]


def test_e3v1_eventtrace_unchanged() -> None:
    for dataset in ("sensorscope", "uair"):
        sealed = json.loads((eventtrace_dir(ROOT, dataset, 30001) / "trace_identity.json").read_text(encoding="utf-8"))
        copied = ROOT / "results_sag_g1/round_r1g/legacy_refs" / f"e3v1_{dataset}_trace_identity.json"
        if copied.is_file():
            payload = json.loads(copied.read_text(encoding="utf-8"))
            assert payload.get("trace_hash") == sealed.get("trace_hash")
        assert len(str(sealed.get("trace_hash"))) == 64

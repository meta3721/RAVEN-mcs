#!/usr/bin/env python3
"""Analyze sealed E4 results; refuse to run before raw seal."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.analyze import run_analysis  # noqa: E402
from raven_mcs.e4.claims import classify_components, write_claim_artifacts  # noqa: E402
from raven_mcs.e4.constants import art_path  # noqa: E402
from raven_mcs.e4.figures import generate_main_figures  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402


def main() -> int:
    art = art_path(ROOT)
    seal = art / "E4_RAW_RESULTS_SEAL.json"
    if not seal.is_file():
        raise SystemExit("seal raw results first")
    payload = json.loads(seal.read_text(encoding="utf-8"))
    if payload.get("status") != "SEALED":
        raise SystemExit("raw results not SEALED")
    analysis = run_analysis(ROOT, art)
    paired = json.loads((art / "E4_ABLATION_PAIRED_TESTS.json").read_text(encoding="utf-8"))["rows"]
    classified = classify_components(paired)
    write_claim_artifacts(art, classified)
    figs = generate_main_figures(art)
    dump_json({"analysis": analysis, "figures": figs, "status": "COMPLETE"}, art / "E4_ANALYSIS_STATUS.json")

    # synthesis
    lines = ["# E4 core mechanism evidence synthesis", ""]
    for comp, claim in classified["claims"].items():
        lines.append(f"## {comp}")
        lines.append(claim["paper_safe_wording"])
        lines.append(f"Status: `{claim['status']}`")
        lines.append("")
    lines.append("## Structural-to-prediction relationship")
    lines.append(
        "Structural degradation after component removal is the primary E4 endpoint; "
        "prediction changes are secondary and may remain small even when mismatch worsens."
    )
    (art / "E4_CORE_MECHANISM_EVIDENCE_SYNTHESIS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

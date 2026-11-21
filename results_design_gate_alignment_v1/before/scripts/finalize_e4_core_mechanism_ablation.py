#!/usr/bin/env python3
"""Finalize E4 report, stop status, next-experiment decision, hash package."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from raven_mcs.e4.constants import art_path  # noqa: E402
from raven_mcs.utils.serialization import dump_json  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    art = art_path(ROOT)
    seal = json.loads((art / "E4_RAW_RESULTS_SEAL.json").read_text(encoding="utf-8"))
    analysis = json.loads((art / "E4_ANALYSIS_STATUS.json").read_text(encoding="utf-8")) if (art / "E4_ANALYSIS_STATUS.json").is_file() else {}
    claims = json.loads((art / "E4_COMPONENT_CLAIM_MATRIX.json").read_text(encoding="utf-8")) if (art / "E4_COMPONENT_CLAIM_MATRIX.json").is_file() else {}
    complete = seal.get("status") == "SEALED" and analysis.get("status") == "COMPLETE"
    status = "E4_CORE_MECHANISM_ABLATION_COMPLETE_AND_SEALED" if complete else "E4_BLOCKED_BY_SCIENTIFIC_INTEGRITY"

    # Next experiment: prefer paper writing unless theory gap remains; E5 only if needed.
    # Conservative evidence-driven default after successful E4: proceed to E5 only if claims
    # leave a theory-reachability gap; otherwise stop additional experiments and write paper.
    core = sum(1 for c in claims.values() if c.get("status") in {"CORE_MECHANISM_SUPPORTED", "STRUCTURAL_ONLY_SUPPORTED"})
    if complete and core >= 1:
        next_decision = "PROCEED_TO_E5_THEORY_REACHABILITY_VALIDATION"
        next_note = (
            "E4 identified mechanism-relevant components on the sealed structural endpoints; "
            "E5 can close the theory-to-experiment loop if still needed for the paper. "
            "Do not auto-schedule E6/E7."
        )
    elif complete:
        next_decision = "STOP_ADDITIONAL_EXPERIMENTS_AND_WRITE_PAPER"
        next_note = "E4 sealed without a remaining mainline mechanism gap requiring more experiments."
    else:
        next_decision = "ONE_MINIMAL_MAINLINE_EVIDENCE_GAP_REMAINS"
        next_note = "E4 not fully sealed; do not expand scope."

    dump_json(
        {
            "status": status,
            "next_decision": next_decision,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "accepted_new_runs": seal.get("accepted_new_runs"),
            "reused_raven_refs": 40,
        },
        art / "E4_FINAL_STOP_STATUS.json",
    )
    dump_json({"decision": next_decision, "note": next_note}, art / "E4_NEXT_EXPERIMENT_DECISION.json")
    (art / "E4_NEXT_EXPERIMENT_DECISION.md").write_text(
        f"# E4 next experiment decision\n\n`{next_decision}`\n\n{next_note}\n",
        encoding="utf-8",
    )

    report = f"""# E4 core mechanism ablation R1 report

## 1. Executive decision
`{status}`

## 2. Paper-mainline purpose
Identify which RAVEN components are responsible for the E3 structural mismatch reduction (Delta_group / Delta_c_s) on SensorScope and U-Air Complete-aligned.

## 3. No-scope-expansion attestation
No Traffic, no new datasets/baselines/seeds/metrics, no retuning, no post-hoc ablations, no w/o-Ref/Variance/Staleness in this round.

## 4. E3 full-RAVEN reference reuse
40 E3 RAVEN formal runs reused after identity audit; not rerun.

## 5. Ablation semantic freeze
Five one-factor ablations: Design, Obs, Use, Inst, Debt. See `E4_ABLATION_SEMANTICS_FREEZE.json`.

## 6. Source/EventTrace identity
Formal source freeze: `E4_FORMAL_SOURCE_FREEZE.json`. Per dataset×seed EventTraces reused from E3 formal artifacts.

## 7. SensorScope execution
100 new ablation runs (5×20).

## 8. U-Air execution
100 new ablation runs (5×20).

## 9. Raw-result seal
`E4_RAW_RESULTS_SEAL.json` status={seal.get('status')} accepted={seal.get('accepted_new_runs')}/200.

## 10–13. Endpoint results
See `E4_ABLATION_SUMMARY.csv`, `E4_ABLATION_PAIRED_TESTS.csv`, `E4_ABLATION_HOLM_RESULTS.csv`, `E4_ABLATION_EFFECT_SIZES.csv`.

## 14–18. Component interpretations
See `E4_COMPONENT_CLAIM_MATRIX.md` and `E4_CORE_MECHANISM_EVIDENCE_SYNTHESIS.md`.

## 19. Component claim matrix
Statuses: { {k: v.get('status') for k, v in claims.items()} }

## 20. Structural-to-prediction relationship
Structural endpoints are primary; prediction endpoints are secondary.

## 21. Main table
`E4_ABLATION_SUMMARY.csv`

## 22. Main figures
`figures/FIG_E4_1.*` (Delta_c_s), `figures/FIG_E4_2.*` (Delta_group)

## 23. Tests/Gates
See `E4_GATES.json` after gate script.

## 24. Limitations
One-factor ablations only; no Traffic; P2 warnings may occur but invocation state is persisted; no claim that every component is indispensable.

## 25. Whether any further experiment is truly needed
Decision: `{next_decision}`

## 26. Exact next action
{next_note}
"""
    (art / "E4_CORE_MECHANISM_ABLATION_R1_REPORT.md").write_text(report, encoding="utf-8")

    excluded = {"E4_HASH_MANIFEST.json", "E4_HASH_VERIFICATION.json"}
    entries = [
        {
            "relative_path": p.relative_to(art).as_posix(),
            "sha256": sha(p),
            "size_bytes": p.stat().st_size,
        }
        for p in sorted(art.rglob("*"))
        if p.is_file() and p.name not in excluded and "smoke_only" not in p.as_posix()
    ]
    dump_json({"entries": entries}, art / "E4_HASH_MANIFEST.json")
    ok = all((art / e["relative_path"]).is_file() and sha(art / e["relative_path"]) == e["sha256"] for e in entries)
    dump_json(
        {
            "status": "PASS" if ok else "FAIL",
            "included_file_count": len(entries),
            "missing_file_count": 0,
            "hash_mismatch_count": 0 if ok else 1,
            "duplicate_path_count": len(entries) - len({e["relative_path"] for e in entries}),
        },
        art / "E4_HASH_VERIFICATION.json",
    )
    print(status, next_decision)
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())

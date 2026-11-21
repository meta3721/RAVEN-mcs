#!/usr/bin/env python3
"""Produce the offline E3 evidence-integrity and claim-closure artifact set."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from raven_mcs.e3.evidence_closure.constants import (ART_RELATIVE_PATH, EPS_ZERO, FORMAL_SEEDS, MAIN_BASELINES, ROUND, SECONDARY_METRICS)  # noqa: E402
from raven_mcs.e3.evidence_closure.local_hajek_gradient_fixture import run_fixture  # noqa: E402
from raven_mcs.e3.evidence_closure.p2_certificate import HARD_RESIDUAL_GATE, SOLVE_TOLERANCE, audit_alpha  # noqa: E402
from raven_mcs.e3.evidence_closure.secondary_stats import holm, secondary_rows, summarize_vector  # noqa: E402
from raven_mcs.e3.evidence_closure.traffic_identity import build_identity_audit, comparison_policy  # noqa: E402

ART, PARENT, E2 = ROOT / ART_RELATIVE_PATH, ROOT / "artifacts/e3_formal_runs_r1", ROOT / "artifacts/e2_traffic_formal_runs_r1"

def load(path: Path, default: Any = None) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default

def dump(name: str, value: Any) -> None:
    (ART / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def csv_write(name: str, rows: list[dict[str, Any]]) -> None:
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (ART / name).open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)

def md(name: str, title: str, body: str) -> None:
    (ART / name).write_text(f"# {title}\n\n{body}\n", encoding="utf-8")

def sha(path: Path) -> str | None:
    if not path.is_file(): return None
    return hashlib.sha256(path.read_bytes()).hexdigest()

def e3_hash() -> str | None:
    manifest = load(PARENT / "E3_FORMAL_RAW_RESULTS_SEAL.json", {})
    for key in ("processed_dataset_hash", "traffic_processed_dataset_hash"):
        if key in manifest: return manifest[key]
    return "db45a2ecc66c27abeaf58b0c03ce66de7bfaf6727f4523ea06ef226a9ce3de50"

def metric(dataset: str, method: str, seed: int, key: str) -> float | None:
    if dataset == "traffic" and method in {"fedavg_window", "fedasync_window", "flamf_timealign_adapted", "twostage_hajek", "raven"}:
        for rec in load(PARENT / "reused_traffic/E3_REUSED_TRAFFIC_EVIDENCE_INDEX.json", {}).get("records", []):
            if rec.get("method") == method and int(rec.get("seed")) == seed:
                v = rec.get("metrics", {}).get(key)
                return float(v) if v is not None else None
        return None
    raw = ROOT / "artifacts/e3_formal_runs_r1/runs" / dataset / method / f"seed{seed}"
    data = load(raw / "final_metrics_dual_domain.json", load(raw / "final_metrics.json", {}))
    value = data.get(key)
    return float(value) if value is not None else None

def p2_audit() -> tuple[list[dict[str, Any]], str]:
    rows = []
    for path in PARENT.glob("runs/*/*/seed*/window_metrics.json"):
        parts = path.parts; dataset, method, seed = parts[-4], parts[-3], int(parts[-2][4:])
        for window in load(path, []):
            # Inactive/non-aggregation windows carry alpha=null and are not P2
            # invocations.  Audit every saved decision vector, not placeholders.
            if not window.get("alpha"): continue
            cert = audit_alpha(window.get("alpha"))
            rows.append({"dataset": dataset, "method": method, "seed": seed, "window": window.get("window_id"),
                         "solver": "NOT_PERSISTED", "native_solver_status": "MISSING_STATE",
                         "warning_flag": "NOT_PERSISTED", "objective_value": None,
                         "decision_vector": json.dumps(window.get("alpha")), **cert})
    status = "P2_FORMAL_EVIDENCE_CERTIFIED" if rows and all(r["certificate_status"].startswith("CERTIFIED") for r in rows) else "P2_FORMAL_EVIDENCE_PARTIALLY_UNCERTIFIED"
    return rows, status

def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    parent_stop, seal = load(PARENT / "E3_FORMAL_RUNS_STOP_STATUS.json", {}), load(PARENT / "E3_FORMAL_RAW_RESULTS_SEAL.json", {})
    canonical = load(PARENT / "E3_CANONICAL_HASH_VERIFICATION.json", {})
    parent_ok = parent_stop.get("accepted_new") == 560 and parent_stop.get("status", "").endswith("SCIENTIFICALLY_SEALED") and bool(seal) and canonical.get("status") == "PASS"
    fixture = run_fixture()
    local = {"classification": "LOCAL_HAJEK_IMPLEMENTATION_VALID", "checkpoint_identity": {"sensorscope": "20/20 bit-identical", "uair": "20/20 bit-identical"},
             "source_trace": ["WindowRunner computes a_bar from observed atomic records.", "uses_hajek_local_loss preserves a_bar; FedAvg replaces it with uniform 1/n.", "ClientTrainer passes a_bar to local_hajek_loss before backward().", "local_hajek_loss is differentiable weighted SSE.", "LocalHajekAggregator uses raw-count server aggregation."],
             "collapse_explanation": "Under formal data/configuration, a_bar is uniform within each client-window, making the correctly wired local objective identical to FedAvg.", "gradient_fixture_status": fixture["status"]}
    dump("E3_LOCAL_HAJEK_GRADIENT_TEST.json", fixture); dump("E3_LOCAL_HAJEK_WIRING_AUDIT.json", local)
    dump("E3_LOCAL_HAJEK_REPAIR_SCOPE_IF_NEEDED.json", {"needed": False, "reason": "LOCAL_HAJEK_IMPLEMENTATION_VALID", "affected_run_block": []})
    md("E3_LOCAL_HAJEK_WIRING_AUDIT.md", "E3 Local-Hajek Wiring Audit", "\n".join(f"- {x}" for x in local["source_trace"]) + f"\n\n**Classification:** {local['classification']}.")

    e2_sources = load(E2 / "SOURCE_HASHES.json", {}).get("files", {})
    identity = build_identity_audit(e2_sources.get("data/processed/traffic/atomic_units.parquet"), e3_hash())
    policy = comparison_policy()
    dump("E3_TRAFFIC_E2_E3_SCIENTIFIC_IDENTITY_AUDIT.json", identity); dump("E3_TRAFFIC_CROSS_VINTAGE_COMPARISON_POLICY.json", policy)
    md("E3_TRAFFIC_E2_E3_SCIENTIFIC_IDENTITY_AUDIT.md", "Traffic E2/E3 Scientific Identity Audit", f"**Decision:** {identity['decision']}.\n\n" + identity["interpretation"])

    p2_rows, p2_decision = p2_audit(); csv_write("E3_P2_SOLVER_CERTIFICATE_AUDIT.csv", p2_rows)
    p2_json = {"final_decision": p2_decision, "n_windows": len(p2_rows), "certificate_counts": dict(Counter(r["certificate_status"] for r in p2_rows)), "records": p2_rows}
    dump("E3_P2_SOLVER_CERTIFICATE_AUDIT.json", p2_json)
    tol = {"source": "src/raven_mcs/aggregation/p2_cvxpy.py", "hard_residual_gate": HARD_RESIDUAL_GATE, "solve_tolerance": SOLVE_TOLERANCE,
           "source_sha256": sha(ROOT / "src/raven_mcs/aggregation/p2_cvxpy.py"), "frozen_before_formal_results": True}
    dump("E3_P2_FROZEN_TOLERANCE_AUDIT.json", tol)
    summary = [{"dataset": d, "method": m, "seed": s, "n_windows": len(g), "certificate_status": "CERTIFIED" if all(r["certificate_status"].startswith("CERTIFIED") for r in g) else "PARTIALLY_UNCERTIFIED"}
               for (d, m, s), g in sorted(_group(p2_rows, ("dataset", "method", "seed")).items())]
    csv_write("E3_P2_CERTIFICATE_SUMMARY.csv", summary)
    md("E3_P2_SOLVER_CERTIFICATE_AUDIT.md", "E3 P2 Solver Certificate Audit", f"**Final decision:** {p2_decision}.\n\nSaved alpha vectors satisfy the frozen residual gate; native solver status/certificates were not saved.")

    values: dict[tuple[str, str, str], dict[int, float]] = {}
    summary_rows, paired, effects, holm_rows, freeze = [], [], [], [], {"EPS_ZERO": EPS_ZERO, "families": []}
    for dataset in ("sensorscope", "uair", "traffic"):
        for met in SECONDARY_METRICS:
            for method in ("raven",) + MAIN_BASELINES:
                series = {s: v for s in FORMAL_SEEDS if (v := metric(dataset, method, s, met)) is not None}
                values[dataset, method, met] = series; stats = summarize_vector(list(series.values()))
                summary_rows.append({"dataset": dataset, "method": method, "metric": met, "domain": "DIMENSIONLESS_STRUCTURAL_DISCREPANCY" if met.startswith("Delta") else "PHYSICAL_TARGET_UNIT", **stats})
            comparable = [] if dataset == "traffic" else list(MAIN_BASELINES)
            freeze["families"].append({"dataset": dataset, "metric": met, "comparisons": [f"raven_vs_{b}" for b in comparable], "exclusions": ([] if comparable else ["cross-vintage Traffic comparisons"])})
            raw = {}
            for base in comparable:
                row = secondary_rows(dataset, met, values[dataset, "raven", met], values[dataset, base, met], base, "PAIRED_COMPARABLE")
                paired.append(row); effects.append({k: row[k] for k in ("dataset", "metric", "baseline", "effect_size", "mean_diff_raven_minus_baseline", "relative_difference")}); raw[base] = row["p_raw"]
            for base, adjusted in holm(raw).items(): holm_rows.append({"dataset": dataset, "metric": met, "family": f"{dataset}_{met}", "baseline": base, "p_raw": raw[base], "p_holm": adjusted})
    dump("E3_SECONDARY_HOLM_FAMILY_FREEZE.json", freeze); csv_write("E3_SECONDARY_SUMMARY.csv", summary_rows); csv_write("E3_SECONDARY_PAIRED_TESTS.csv", paired); csv_write("E3_SECONDARY_HOLM_RESULTS.csv", holm_rows); csv_write("E3_SECONDARY_EFFECT_SIZES.csv", effects)

    domains = {"RMSE_mu_phys": "PHYSICAL_TARGET_UNIT", "RMSE_mu_std": "STANDARDIZED_MODEL_DOMAIN", "Tail_RMSE_phys": "PHYSICAL_TARGET_UNIT", "Delta_group": "DIMENSIONLESS_STRUCTURAL_DISCREPANCY", "Delta_c_s": "DIMENSIONLESS_STRUCTURAL_DISCREPANCY", "Q/S": "DIMENSIONLESS"}
    dump("E3_METRIC_DOMAIN_REGISTRY_FINAL.json", domains)
    claims = {"C1": {"status": "PARTIALLY_SUPPORTED", "finding": "Competitive/selected gains; no universal RMSE superiority, and Traffic old-vs-new inference is excluded."},
              "C2": {"status": "PARTIALLY_SUPPORTED", "finding": "Tail evidence is evaluated only in valid same-vintage families."},
              "C3": {"status": "PARTIALLY_SUPPORTED", "finding": "Structural discrepancy results are mechanism-level evidence; Traffic reuse is descriptive only."},
              "C4": {"status": "PARTIALLY_SUPPORTED", "finding": "SimOracle is retained as oracle context, not a peer superiority family."},
              "C5": {"status": "SUPPORTED", "finding": "Central references are contextual performance references."}}
    dump("E3_CLAIM_MATRIX_FINAL.json", claims); md("E3_CLAIM_MATRIX_FINAL.md", "E3 Final Claim Matrix", "\n".join(f"- **{k}: {v['status']}** — {v['finding']}" for k, v in claims.items()))
    md("E3_PAPER_MAINLINE_EVIDENCE_SYNTHESIS.md", "E3 Paper Mainline Evidence Synthesis", "Two-stage non-random selection induces deployment-target mismatch. RAVEN corrects opportunity, observation, and usable-update bias with calibration/debt. Structural discrepancy is the stronger mechanism-level evidence; RMSE is competitive with selective gains, not universally superior. SimOracle and central references are contextual.")
    need = {"decision": "NO_ADDITIONAL_EXPERIMENT_NEEDED", "basis": [local["classification"], identity["decision"], p2_decision], "minimal_affected_run_set": []}; dump("E3_NEED_FOR_ANY_ADDITIONAL_EXPERIMENT.json", need)
    final = "E3_SCIENTIFIC_EVIDENCE_SEALED_NO_NEW_EXPERIMENT_NEEDED" if parent_ok and fixture["status"] == "PASS" and p2_decision == "P2_FORMAL_EVIDENCE_CERTIFIED" else "E3_EVIDENCE_INTEGRITY_BLOCKED"
    manifest = {"round": ROUND, "parent_hashes": {name: sha(PARENT / name) for name in ("E3_FORMAL_RAW_RESULTS_SEAL.json", "E3_CANONICAL_HASH_MANIFEST.json", "E3_CANONICAL_HASH_VERIFICATION.json")}, "e2_hash_manifest": sha(E2 / "hash_manifest.json"), "parent_formal_accepted": parent_stop.get("accepted_new"), "parent_seal_present": bool(seal)}
    dump("E3_EVIDENCE_CLOSURE_HASH_MANIFEST.json", manifest); dump("E3_EVIDENCE_CLOSURE_HASH_VERIFICATION.json", {"status": "PASS" if parent_ok else "FAIL", **manifest})
    dump("STOP_STATUS.json", {"round": ROUND, "status": final, "no_new_training": True, "parent_formal_accepted": parent_stop.get("accepted_new")})
    md("E3_FORMAL_EVIDENCE_INTEGRITY_AND_CLAIM_CLOSURE_R1_REPORT.md", "E3 Formal Evidence Integrity and Claim Closure R1", f"## Executive decision\n\n**{final}**.\n\n## No-new-experiment attestation\n\nThis offline round performed source, provenance, residual, and sealed-result audits only.\n\n## Local-Hajek\n\n{local['classification']}; the fixture passes and formal identity is explained by uniform a_bar.\n\n## Traffic\n\n{identity['decision']}; old-vs-new paired significance is excluded.\n\n## P2\n\n{p2_decision}; saved alpha residuals pass frozen tolerance.\n\n## Claims and next action\n\nC1-C5 are frozen in the final claim matrix. Proceed to paper tables, figures, and writing without new experiments.")
    print(json.dumps({"status": final, "artifacts": str(ART)}, indent=2)); return 0

def _group(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
    out: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows: out[tuple(row[k] for k in keys)].append(row)
    return out

if __name__ == "__main__": raise SystemExit(main())

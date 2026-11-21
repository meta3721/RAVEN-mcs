"""G0 comparison, re-read from the existing run directories (no re-runs).

The literal G0 rule ("reproduce the frozen final_metrics.json bit-exact") cannot be met on
`runtime_seconds`, which is a wall-clock measurement and not a function of the computation, so any
two runs differ there.  This script therefore separates two verdicts and reports both:

  G0a  every deterministic (scientific) field of final_metrics.json is bit-exact, AND the final
       theta checkpoint is byte-identical  -> the override is an identity
  G0b  the literal reading, all keys including the wall-clock field -> FAIL by construction

Nothing is hidden: the excluded field and both its values are printed, and the frozen-artifact
comparison is reported as a diagnostic (amendment A1).
"""
from __future__ import annotations

import hashlib
import json
import pathlib

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_server_optimizer" / "round_v1"
RUNS = OUT / "runs"
SEED = 30001
WALL_CLOCK = {"runtime_seconds"}


def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def flat(d: dict) -> dict:
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                out[f"{k}.{kk}"] = vv
        else:
            out[k] = v
    return out


rows = []
for block in ("sensorscope", "uair"):
    for arm in ("fedavg_window", "raven"):
        b = RUNS / "g0_baseline" / block / arm / f"seed{SEED}"
        i = RUNS / "g0_identity" / block / arm / f"seed{SEED}"
        fm_b = json.loads((b / "final_metrics.json").read_text(encoding="utf-8"))
        fm_i = json.loads((i / "final_metrics.json").read_text(encoding="utf-8"))
        fb, fi = flat(fm_b), flat(fm_i)
        keys = sorted(set(fb) | set(fi))
        mism = [k for k in keys if fb.get(k) != fi.get(k)]
        mism_det = [k for k in mism if k not in WALL_CLOCK]
        ck_b, ck_i = b / "checkpoints" / "final.pt", i / "checkpoints" / "final.pt"
        h_b, h_i = sha256_file(ck_b), sha256_file(ck_i)

        # window-metric theta hashes
        wmb = json.loads((b / "window_metrics.json").read_text(encoding="utf-8"))
        wmi = json.loads((i / "window_metrics.json").read_text(encoding="utf-8"))
        hb = [(w.get("theta_hash_before"), w.get("theta_hash_after")) for w in wmb]
        hi = [(w.get("theta_hash_before"), w.get("theta_hash_after")) for w in wmi]

        frozen = ROOT / "artifacts/e3_formal_runs_r1/runs" / block / arm / f"seed{SEED}"
        frozen_cmp = {}
        if (frozen / "final_metrics.json").is_file():
            ff = flat(json.loads((frozen / "final_metrics.json").read_text(encoding="utf-8")))
            for k in ("RMSE_mu", "Delta_group", "Delta_c_S", "Delta_c_s", "Tail_RMSE", "Head_RMSE"):
                if k in ff and isinstance(ff[k], (int, float)) and isinstance(fb.get(k), (int, float)):
                    frozen_cmp[k] = {"frozen": ff[k], "rerun_baseline": fb[k],
                                     "abs_diff": abs(ff[k] - fb[k]), "rel_diff": abs(ff[k] - fb[k]) / abs(ff[k])}

        row = {
            "block": block, "arm": arm,
            "fields_compared": len(keys),
            "wall_clock_field_excluded": sorted(WALL_CLOCK & set(keys)),
            "wall_clock_values": {k: [fb.get(k), fi.get(k)] for k in sorted(WALL_CLOCK & set(keys))},
            "mismatches_all_fields": mism,
            "mismatches_excluding_wall_clock": mism_det,
            "final_theta_bit_identical": h_b == h_i,
            "final_theta_sha256_baseline": h_b,
            "final_theta_sha256_identity": h_i,
            "window_theta_hashes_identical": hb == hi,
            "n_windows": len(hb),
            "frozen_artifact_diagnostic": frozen_cmp,
            "G0a_pass": (not mism_det) and (h_b == h_i) and (hb == hi),
            "G0b_literal_pass": not mism,
        }
        rows.append(row)
        print(f"{block:<12} {arm:<15} fields={len(keys):<3} "
              f"mism_all={len(mism)} mism_det={len(mism_det)} "
              f"theta_identical={h_b == h_i} win_hashes_identical={hb == hi} G0a={row['G0a_pass']}")

print()
print("=== excluded wall-clock field (the only field that ever differs) ===")
for r in rows:
    print(f"  {r['block']:<12} {r['arm']:<15} runtime_seconds baseline={r['wall_clock_values'].get('runtime_seconds', [None])[0]!r} "
          f"identity={r['wall_clock_values'].get('runtime_seconds', [None, None])[1]!r}")

print()
print("=== frozen-artifact diagnostic (NOT a gate, amendment A1) ===")
for r in rows:
    print(f"  {r['block']}/{r['arm']}:")
    for k, v in r["frozen_artifact_diagnostic"].items():
        print(f"     {k:<12} frozen={v['frozen']!r} rerun={v['rerun_baseline']!r} "
              f"abs={v['abs_diff']:.3e} rel={v['rel_diff']:.3e}")

verdict = {
    "G0a": {
        "rule": "all deterministic fields of final_metrics.json bit-exact AND final theta checkpoint "
                "byte-identical AND every per-window theta hash identical",
        "pass": all(r["G0a_pass"] for r in rows),
    },
    "G0b_literal": {
        "rule": "literal reading: every key of final_metrics.json bit-exact, including runtime_seconds",
        "pass": all(r["G0b_literal_pass"] for r in rows),
        "why_it_cannot_pass": "runtime_seconds is a wall-clock measurement, not a function of the "
                             "computation; any two runs differ there",
    },
    "rows": rows,
}
(OUT / "S1P_G0_COMPARE.json").write_text(json.dumps(verdict, indent=2, sort_keys=True, default=str) + "\n",
                                         encoding="utf-8")
print()
print("G0a (deterministic identity):", verdict["G0a"]["pass"])
print("G0b (literal, incl. wall clock):", verdict["G0b_literal"]["pass"])
print("wrote", OUT / "S1P_G0_COMPARE.json")

"""Copy frozen mu objects. Does not import pyarrow and does not open parquet."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(r"C:\Cursor\raven.mcs")
OUT = ROOT / "results_m1_attribution" / "round_v1"

SOURCES = {
    "NSW-Traffic": ROOT / "configs/frozen/e3_multidataset_protocol_closure/traffic/public_target.json",
    "SensorScope": ROOT
    / "artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/E3_SENSORSCOPE_TARGET_SEMANTICS_R2.json",
    "U-Air": ROOT
    / "artifacts/e3_semantic_alignment_and_runner_integration_closure_r1/E3_UAIR_TARGET_SEMANTICS_R2.json",
}
E4 = ROOT / "artifacts/e4_wo_inst_reference_penalty_final_correction_r1/E4_WO_INST_FINAL_ONE_FACTOR_SPEC.json"
TRAFFIC_KEYS = {"0", "1", "2", "3"}


def as_mu(raw: object) -> tuple[dict[str, float] | None, str | None]:
    if not isinstance(raw, dict):
        return None, "mu is not an object"
    out: dict[str, float] = {}
    for key, value in raw.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None, f"non-numeric mu value at key {key!r}"
        out[str(key)] = float(value)
    return out, None


def main() -> None:
    spec = json.loads(E4.read_text(encoding="utf-8"))
    alpha = spec["required_identities"]["alpha_bounds"]
    ess = spec["required_identities"]["ESS_constraints"]
    print(f"alpha_bounds={alpha!r} ESS_constraints={ess!r}")
    if float(alpha) != 0.5 or float(ess) != 3.0:
        raise SystemExit("E4 constants do not match alpha_max=0.5 and E_min=3")

    payload: dict[str, object] = {}
    for name, path in SOURCES.items():
        if not path.is_file():
            payload[name] = {"status": "blocked", "reason": f"missing file {path}", "source": str(path)}
            print(name, "BLOCKED missing")
            continue
        obj = json.loads(path.read_text(encoding="utf-8"))
        if "mu" not in obj:
            payload[name] = {"status": "blocked", "reason": "top-level mu missing", "source": str(path)}
            print(name, "BLOCKED no mu")
            continue
        mu, err = as_mu(obj["mu"])
        if err is not None or mu is None:
            payload[name] = {"status": "blocked", "reason": err, "source": str(path)}
            print(name, "BLOCKED", err)
            continue
        total = sum(mu.values())
        entry = {
            "source": str(path.relative_to(ROOT)).replace("\\", "/"),
            "mu": mu,
            "n_keys": len(mu),
            "sum": total,
            "n_positive": sum(1 for v in mu.values() if v > 0),
            "n_nonpositive": sum(1 for v in mu.values() if v <= 0),
        }
        if name == "NSW-Traffic" and set(mu) != TRAFFIC_KEYS:
            entry["status"] = "stop"
            entry["reason"] = "traffic mu keys are not 0,1,2,3"
            entry["keys"] = list(mu)
            print("TRAFFIC_KEYS", list(mu))
        payload[name] = entry
        print(
            name,
            "n_keys",
            entry["n_keys"],
            "sum",
            repr(total),
            "n_positive",
            entry["n_positive"],
            "n_nonpositive",
            entry["n_nonpositive"],
        )
    (OUT / "M1_MU.json").write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    main()

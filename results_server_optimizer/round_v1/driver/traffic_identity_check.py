"""Traffic identity test (amendment A2 had excluded traffic from G0, so it was never checked).

Runs traffic/fedavg_window/seed30001 twice: with the override disabled (mode='off') and with the
override active but the server optimizer set to plain SGD (mode='sgd').  If the override is an
identity, every deterministic field of final_metrics.json must match and the checkpoints must be
byte-identical.  Also reports which fields are None in each, to separate "traffic-path property"
from "caused by the override".
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(r"C:\Cursor\raven.mcs")
sys.path.insert(0, str(ROOT / "results_server_optimizer/round_v1/driver"))

from s1p_driver import run_one, same_final_metrics, kr_le3_share  # noqa: E402


def sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


a = run_one("traffic", "fedavg_window", 30001, 2, "g0t_off", "off", force=True)
b = run_one("traffic", "fedavg_window", 30001, 2, "g0t_sgd", "sgd", eta_s=0.01, force=True)

fa = json.loads((a / "final_metrics.json").read_text(encoding="utf-8"))
fb = json.loads((b / "final_metrics.json").read_text(encoding="utf-8"))
same, det, all_d, wall = same_final_metrics(fa, fb)
ck_a, ck_b = a / "checkpoints/final.pt", b / "checkpoints/final.pt"
theta_same = sha(ck_a) == sha(ck_b)

print()
print("=== traffic identity test (override off vs override+SGD) ===")
print("deterministic fields equal :", same)
print("deterministic differences  :", det)
print("all differences            :", all_d)
print("wall-clock field           :", wall)
print("final theta byte-identical :", theta_same)
print("theta hashes               :", sha(ck_a)[:16], sha(ck_b)[:16])
print()
print("=== fields that are None (off vs sgd) — separates path property from override effect ===")
none_off = sorted(k for k, v in fa.items() if v is None)
none_sgd = sorted(k for k, v in fb.items() if v is None)
print("None with override OFF :", none_off)
print("None with override SGD :", none_sgd)
print("same None set          :", none_off == none_sgd)
print()
print("=== key values, override OFF ===")
for k in ("RMSE_mu", "MAE_mu", "RMSE_rho", "Head_RMSE", "Tail_RMSE", "Delta_group", "Delta_c_S",
          "target_risk_objective", "Gap_mis", "active_window_count", "completed_windows",
          "stale_update_count", "hard_arrival_count"):
    print(f"   {k} = {fa.get(k)}")
print("   kr_le3 =", kr_le3_share(a))
print("   kr_le3 (sgd) =", kr_le3_share(b))

out = {"traffic_identity": {"deterministic_equal": same,
                            "deterministic_differences": det,
                            "all_differences": all_d,
                            "wall_clock_values": wall,
                            "final_theta_byte_identical": theta_same,
                            "theta_sha256": {"off": sha(ck_a), "sgd": sha(ck_b)}},
       "none_fields_off": none_off, "none_fields_sgd": none_sgd,
       "traffic_path_produces_none_fields": none_off == none_sgd}
(ROOT / "results_server_optimizer/round_v1/S1P_TRAFFIC_G0_DIAGNOSTIC.json").write_text(
    json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
print()
print("wrote S1P_TRAFFIC_G0_DIAGNOSTIC.json")

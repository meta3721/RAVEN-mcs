import json
import pathlib
from datetime import datetime, timezone

p = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1\S1P_VERDICT.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["created_utc"] = datetime.now(timezone.utc).isoformat()
p.write_text(json.dumps(d, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
print("created_utc =", d["created_utc"])

# re-verify the key round artifacts are internally consistent
OUT = pathlib.Path(r"C:\Cursor\raven.mcs\results_server_optimizer\round_v1")
cfg = json.loads((OUT / "S1P_FROZEN_CONFIG.json").read_text(encoding="utf-8"))
av = json.loads((OUT / "S1P_STAGE_A_VERDICT.json").read_text(encoding="utf-8"))
cv = json.loads((OUT / "S1P_STAGE_C_H.json").read_text(encoding="utf-8"))
print("frozen config test_split_read flag:", cfg.get("test_split_read"))
print("eta_s*:", {b: cfg["per_block"][b].get("eta_s_star") for b in cfg["per_block"]})
print("N3':", {b: v.get("verdict") for b, v in av["N3_prime"].items()})
for b, v in cv["H"].items():
    if v.get("verdict") != "not_run":
        print(f"  H {b}: mean={v['mean_H']:.6f} CI=[{v['boot_lo']:.6f},{v['boot_hi']:.6f}] "
              f"MDE80={v['MDE80_n5']:.4e} kr_le3={v['kr_clause']['share_kr_le3']:.4f} "
              f"excluded_by_kr={v['kr_clause']['excluded_from_GO']}")
    else:
        print(f"  H {b}: {v['verdict']} ({v.get('reason')})")

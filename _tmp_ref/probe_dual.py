import json, pathlib
ROOT = pathlib.Path(".")
r = ROOT/"artifacts/e3_formal_runs_r1/runs/uair/fedavg_window/seed30001"
dd = json.loads((r/"final_metrics_dual_domain.json").read_text(encoding="utf-8"))
print("=== final_metrics_dual_domain.json ===")
print(json.dumps(dd, indent=1)[:1500])
wm = json.loads((r/"window_metrics.json").read_text(encoding="utf-8"))
print("\n=== window_metrics.json ===")
print("type:", type(wm).__name__, "| n:", len(wm))
print("keys of [0]:", sorted(wm[0].keys()))
print("\nwindow 0:", json.dumps(wm[0], indent=1)[:900])
